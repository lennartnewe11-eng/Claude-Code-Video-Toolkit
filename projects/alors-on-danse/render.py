"""Render the "Alors on danse" travel edit.

usage: python3 render.py --media DIR --song SONG.wav --out OUT.mp4 [--scale 0.5] [--jobs 4]
                         [--frames A:B]  (render only a frame range, for previews)
"""
import argparse
import bisect
import math
import os
import subprocess
import sys
import time
import multiprocessing as mp

import cv2
import numpy as np

import engine as E
import timeline as TL

FPS = E.FPS


class Edit:
    def __init__(self, cfg):
        self.cfg = cfg
        self.BT = np.array(TL.load_beats(), float)
        self.T0 = self.BT[3]
        self.shots = TL.shots()
        self.texts = TL.texts()
        self.blinks = TL.blinks()
        # --- place shots on the beat grid
        cur = TL.at(0)
        starts = []
        for s in self.shots:
            s["sb"], s["eb"] = cur, cur + s["b"]
            starts.append(cur)
            cur += s["b"]
        for bar in TL.CHECKPOINTS:
            if TL.at(bar) not in starts and TL.at(bar) != cur:
                near = min(starts, key=lambda x: abs(x - TL.at(bar)))
                raise SystemExit(f"timeline out of sync at bar {bar}: nearest shot start "
                                 f"beat {near} vs {TL.at(bar)}")
        self.shots[-1]["eb"] = max(self.shots[-1]["eb"], TL.END_BEAT)
        self.N = self.frame_of(TL.END_BEAT)
        for s in self.shots:
            s["F0"], s["F1"] = self.frame_of(s["sb"]), self.frame_of(s["eb"])
            s["D"] = (s["F1"] - s["F0"]) / FPS
        self.shots[-1]["F1"] = self.N
        self.starts = [s["F0"] for s in self.shots]
        # precomputed per-frame helpers
        W, H = cfg.W, cfg.H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        vig = np.clip(1.0 - 0.28 * np.clip(r - 0.55, 0, None) ** 1.6, 0, 1)
        self.vig = cv2.merge([(vig * 255).astype(np.uint8)] * 3)
        rng = np.random.default_rng(7)
        self.grain = []
        for _ in range(6):
            g = cv2.GaussianBlur(rng.normal(0, 5.5, (H, W)).astype(np.float32), (0, 0), 0.7)
            g3 = cv2.merge([g, g, g])
            self.grain.append((np.clip(g3, 0, 255).astype(np.uint8),
                               np.clip(-g3, 0, 255).astype(np.uint8)))
        self.typo = E.Typo(cfg)
        self.photo_cache = {}
        self.readers = {}

    # --- time helpers ---------------------------------------------------------
    def bt(self, x):
        """song time of fractional beat index x"""
        BT = self.BT
        i = int(math.floor(x))
        if i < 0:
            return BT[0] + x * (BT[1] - BT[0])
        if i >= len(BT) - 1:
            return BT[-1] + (x - (len(BT) - 1)) * (BT[-1] - BT[-2])
        return BT[i] + (x - i) * (BT[i + 1] - BT[i])

    def beat_pos(self, t_song):
        BT = self.BT
        i = bisect.bisect_right(BT, t_song) - 1
        if i < 0:
            return (t_song - BT[0]) / (BT[1] - BT[0])
        if i >= len(BT) - 1:
            return len(BT) - 1 + (t_song - BT[-1]) / (BT[-1] - BT[-2])
        return i + (t_song - BT[i]) / (BT[i + 1] - BT[i])

    def frame_of(self, beat):
        return int(round((self.bt(beat) - self.T0) * FPS))

    def out_t(self, beat):
        return self.bt(beat) - self.T0

    # --- source frames --------------------------------------------------------
    def src_time(self, s, tl):
        sp = s.get("sp", 1.0)
        if "tmap" in s:
            return E.pw_linear(s["tmap"], tl)
        if s.get("vel"):
            k = 0
            b0 = self.out_t(s["sb"])
            while k < s["b"] and self.out_t(s["sb"] + k + 1) - b0 <= tl:
                k += 1
            lb0 = self.out_t(s["sb"] + k) - b0
            lb1 = self.out_t(s["sb"] + k + 1) - b0
            u = (tl - lb0) / max(1e-6, lb1 - lb0)
            return sp * (lb0 + (lb1 - lb0) * E.ease_out(u, 2.2))
        return sp * tl

    def get_reader(self, idx):
        s = self.shots[idx]
        if idx not in self.readers:
            for k in [k for k in self.readers if k < idx]:
                self.readers.pop(k).close()
            ts = [self.src_time(s, f / FPS) for f in range(s["F1"] - s["F0"] + 1)]
            nfr = int(max(ts) * FPS) + 4
            self.readers[idx] = E.VReader(self.cfg, s["src"], s["t"], nfr, s.get("mode", "land"))
        return self.readers[idx]

    def photo(self, s):
        key = (s["kind"], str(s["src"]))
        if key not in self.photo_cache:
            cfg = self.cfg
            if s["kind"] == "p":
                img = E.load_photo(cfg, s["src"])
                self.photo_cache[key] = (E.cover_crop(img, cfg.SW, cfg.SH, s.get("fx", 0.5),
                                                      s.get("fy", 0.5)), None)
            else:
                imgs = [E.load_photo(cfg, n) for n in s["src"]]
                self.photo_cache[key] = E.build_panels(cfg, imgs, s.get("focus"))
        return self.photo_cache[key]

    def source_frame(self, idx, tl):
        s = self.shots[idx]
        ranges = None
        if s["kind"] in ("p", "split"):
            img, ranges = self.photo(s)
        else:
            rd = self.get_reader(idx)
            fi = self.src_time(s, tl) * FPS
            a = int(math.floor(fi))
            frac = fi - a
            img = rd.get(a)
            if s.get("blend") and frac > 0.08:
                img = cv2.addWeighted(img, 1 - frac, rd.get(a + 1), frac, 0)
            ranges = getattr(rd, "ranges", None)
        if s.get("reveal") and ranges:
            beats_in = self.beat_pos(tl + self.bt(s["sb"])) - s["sb"]
            k = int(beats_in / s["reveal"]) + 1
            if k < len(ranges):
                img = img.copy()
                img[:, ranges[k][0] - int(10 * self.cfg.sc):] = 0
        return img

    # --- effects --------------------------------------------------------------
    def bounce_amp(self, bp):
        bar = (bp - 3) / 4
        for b0, b1, a in TL.BOUNCE:
            if b0 <= bar < b1:
                return a
        return 0.0

    def flash_amount(self, t_out, idx):
        f = 0.0
        # shot flashes (current and previous shots, the decay may cross a cut)
        for j in (idx - 1, idx):
            if j < 0:
                continue
            s = self.shots[j]
            if s.get("flash"):
                dt = t_out - s["F0"] / FPS
                if dt >= 0:
                    f += s["flash"] * math.exp(-dt / s.get("flash_tau", 0.12))
            if s.get("reveal"):
                n_panels = 3 if isinstance(s["src"], list) and len(s["src"]) == 3 else (
                    3 if s.get("mode") == "tri" else 2)
                for k in range(1, n_panels):
                    dt = t_out - self.out_t(s["sb"] + k * s["reveal"])
                    if 0 <= dt < 0.6:
                        f += 0.4 * math.exp(-dt / 0.06)
        for b, amp, tau in self.blinks:
            dt = t_out - self.out_t(b)
            if 0 <= dt < 1.0:
                f += amp * math.exp(-dt / tau)
        return min(1.0, f)

    def rgb_split_amount(self, t_out, idx, tl):
        s = self.shots[idx]
        a = 0.0
        if s.get("punch", 0) >= 0.12 or s.get("flash", 0) >= 0.8:
            a = max(a, 14 * math.exp(-tl / 0.09))
        return a * self.cfg.sc

    # --- typography -----------------------------------------------------------
    # Every lyric is one calligraphic script in white. Each word is written on
    # (left-to-right wipe) exactly while it is sung: `t` = sung onset and `d` =
    # sung duration, both in song seconds, measured from the isolated vocals.

    def anchor_xy(self, w, h, anchor, bleed=(0.0, 0.0), lb=0, margin=None, y=0.5, x=0.5):
        """Centre of a w x h box placed against a frame edge/corner.

        bleed = fraction of the box pushed outside the picture on the anchored
        side(s), so words are deliberately cut by the frame edge."""
        W, H = self.cfg.W, self.cfg.H
        m = 60 * self.cfg.sc if margin is None else margin
        bx, by = bleed
        if anchor in ("tl", "bl", "l"):
            cx = (-bx * w if bx > 0 else m) + w / 2
        elif anchor in ("tr", "br", "r"):
            cx = (W + bx * w if bx > 0 else W - m) - w / 2
        else:
            cx = x * W
        # vertical bleed is measured from the picture edge (inside any letterbox)
        if anchor in ("tl", "tr", "t"):
            cy = (lb - by * h if by > 0 else m + lb) + h / 2
        elif anchor in ("bl", "br", "b"):
            cy = (H - lb + by * h if by > 0 else H - m - lb) - h / 2
        else:
            cy = y * H
        return cx, cy

    def draw_script_word(self, out, wd, t_song, t1, lb):
        sc = self.cfg.sc
        dt = t_song - wd["t"]
        if dt < 0:
            return
        m = self.typo.mask(wd["text"], wd.get("size", 260) * sc)
        h, w = m.shape
        cx, cy = self.anchor_xy(w, h, wd.get("anchor", "c"), wd.get("bleed", (0, 0)), lb,
                                y=wd.get("y", 0.5), x=wd.get("x", 0.5))
        d = max(0.12, wd.get("d", 0.3))
        p = E.clamp(dt / d)
        wipe = E.ease_out(p, 2.0)
        settle = 1 + 0.05 * (1 - E.ease_out(dt / 0.45))
        drift = 10 * sc * (1 - E.ease_out(dt / 0.45))
        fade = E.clamp((t1 - t_song) / 0.15) * wd.get("alpha", 1.0)
        rot = wd.get("rot", 0.0)
        n = wd.get("layers", 0)
        lx, ly = wd.get("step", (0.05, -0.16))
        for i in range(n, 0, -1):      # ghost repeats behind the word, like overwritten ink
            dti = dt - 0.05 * i
            if dti <= 0:
                continue
            E.blit(out, m, cx + i * lx * w, cy + i * ly * h, settle, fade * (0.5 / (i + 0.6)),
                   rot=rot + i * wd.get("rot_step", -2.5), wipe=E.ease_out(E.clamp(dti / d), 2.0))
        E.blit(out, m, cx, cy + drift, settle, fade, shadow=0.45, rot=rot, wipe=wipe)

    def draw_texts(self, out, t_out, bp):
        cfg, sc = self.cfg, self.cfg.sc
        W, H = cfg.W, cfg.H
        t_song = t_out + self.T0
        lb_amt = E.pw_linear(TL.LETTERBOX, bp)
        lb = int(round(lb_amt * (H - W / 2.39) / 2))
        for ev in self.texts:
            if not (ev["t0"] <= t_song < ev["t1"]):
                continue
            if ev["style"] == "script":
                for wd in ev["words"]:
                    self.draw_script_word(out, wd, t_song, ev["t1"], lb)
            elif ev["style"] == "scatter":
                rng = np.random.default_rng(ev.get("seed", 0))
                for it in ev["items"]:
                    fx = rng.choice([rng.uniform(0.08, 0.28), rng.uniform(0.72, 0.92)])
                    fy = rng.choice([rng.uniform(0.16, 0.34), rng.uniform(0.66, 0.84)])
                    size, rot = rng.uniform(170, 280), rng.uniform(-14, 14)
                    lt = t_song - it["t"]
                    if lt < 0:
                        continue
                    life = it.get("life", 0.9)
                    a = E.clamp((life - lt) / 0.25) * E.clamp((ev["t1"] - t_song) / 0.15)
                    if a <= 0:
                        continue
                    m = self.typo.mask(it["text"], size * sc)
                    E.blit(out, m, fx * W, fy * H, 1 + 0.06 * (1 - E.ease_out(lt / 0.3)), a,
                           shadow=0.45, rot=rot, wipe=E.ease_out(E.clamp(lt / max(0.1, it.get("d", 0.2))), 2.0))

    # --- one output frame -----------------------------------------------------
    def render(self, n):
        cfg = self.cfg
        W, H, sc = cfg.W, cfg.H, cfg.sc
        idx = bisect.bisect_right(self.starts, n) - 1
        s = self.shots[idx]
        tl = (n - s["F0"]) / FPS
        t_out = n / FPS
        t_song = t_out + self.T0
        bp = self.beat_pos(t_song)

        img = self.source_frame(idx, tl)

        # camera move
        u = tl / max(1e-6, s["D"])
        z = E.lerp(s.get("z0", 1.0), s.get("z1", s.get("z0", 1.0)), E.ease_io(u))
        z *= 1 + s.get("punch", 0.0) * math.exp(-tl / 0.16)
        amp = self.bounce_amp(bp)
        if amp and not s.get("strobe"):
            i = bisect.bisect_right(self.BT, t_song) - 1
            if i >= 0:
                z *= 1 + amp * math.exp(-(t_song - self.BT[i]) / 0.10)
        rot = E.lerp(s.get("rot0", 0.0), s.get("rot1", s.get("rot0", 0.0)), u)
        A = s.get("shake", 0.0) * sc * math.exp(-tl / 0.28)
        dx = A * E.hash_noise(n, 1)
        dy = A * E.hash_noise(n, 2)
        rot += A * 0.04 * E.hash_noise(n, 3)
        z *= 1 + 0.02 * abs(rot) + 2.2 * A / W
        px = E.lerp(s.get("px0", 0.0), s.get("px1", s.get("px0", 0.0)), E.ease_io(u))
        py = E.lerp(s.get("py0", 0.0), s.get("py1", s.get("py0", 0.0)), E.ease_io(u))
        scale = (W / cfg.SW) * z
        cxs, cys = cfg.SW / 2 + px * cfg.SW, cfg.SH / 2 + py * cfg.SH
        M = cv2.getRotationMatrix2D((cxs, cys), rot, scale)
        M[0, 2] += W / 2 + dx - cxs
        M[1, 2] += H / 2 + dy - cys
        out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REFLECT101)

        # grade
        desat = E.pw_linear(s["desat"], tl) if "desat" in s else 0.0
        out = E.grade(out, s.get("look", "cine"), s.get("ev", 1.0), desat)

        # typography
        self.draw_texts(out, t_out, bp)

        # chromatic split
        d = int(round(self.rgb_split_amount(t_out, idx, tl)))
        if d >= 1:
            b, g, r = cv2.split(out)
            b = np.roll(b, -d, axis=1)
            r = np.roll(r, d, axis=1)
            out = cv2.merge([b, g, r])

        # white flash / blink
        f = self.flash_amount(t_out, idx)
        if f > 0.004:
            out = cv2.convertScaleAbs(out, alpha=1 - f, beta=255 * f)

        # vignette + grain
        out = cv2.multiply(out, self.vig, scale=1 / 255)
        gp, gn = self.grain[n % len(self.grain)]
        out = cv2.subtract(cv2.add(out, gp), gn)

        # letterbox
        lb = E.pw_linear(TL.LETTERBOX, bp)
        if lb > 0.002:
            hb = int(round(lb * (H - W / 2.39) / 2))
            if hb > 0:
                out[:hb] = 0
                out[H - hb:] = 0

        # global fade
        fade = E.pw_linear(TL.FADE, bp)
        if fade < 0.999:
            out = cv2.convertScaleAbs(out, alpha=fade)
        return out


def worker(args, cfg, f0, f1, path):
    cv2.setNumThreads(1)
    ed = Edit(cfg)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{cfg.W}x{cfg.H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
         "-pix_fmt", "yuv420p", "-g", "60", "-bf", "2", "-threads", "2", path],
        stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(f0, f1):
        enc.stdin.write(ed.render(n).tobytes())
        if (n - f0) % 150 == 0:
            el = time.time() - t0
            print(f"[{os.path.basename(path)}] {n - f0}/{f1 - f0} frames "
                  f"({(n - f0) / max(el, 1e-6):.1f} fps)", flush=True)
    enc.stdin.close()
    enc.wait()
    for r in ed.readers.values():
        r.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", required=True)
    ap.add_argument("--fonts", default=os.path.join(os.path.dirname(__file__), "fonts"))
    ap.add_argument("--song", required=True, help="wav/m4a/mov with the song's audio")
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--frames", default=None)
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()

    cfg = E.Cfg(args.scale, args.media, args.fonts)
    ed = Edit(cfg)
    print(f"{len(ed.shots)} shots, {len(ed.texts)} text events, {ed.N} frames "
          f"({ed.N / FPS:.2f}s), song offset {ed.T0:.3f}s", flush=True)
    f0, f1 = 0, ed.N
    if args.frames:
        a, b = args.frames.split(":")
        f0, f1 = int(a or 0), int(b or ed.N)
    work = args.workdir or os.path.splitext(args.out)[0] + "_parts"
    os.makedirs(work, exist_ok=True)

    # split into chunks at shot boundaries
    jobs = max(1, args.jobs)
    bounds = [f0]
    for k in range(1, jobs):
        target = f0 + (f1 - f0) * k // jobs
        cand = min((s["F0"] for s in ed.shots if f0 < s["F0"] < f1),
                   key=lambda x: abs(x - target), default=target)
        if cand > bounds[-1]:
            bounds.append(cand)
    bounds.append(f1)
    parts = []
    procs = []
    for k in range(len(bounds) - 1):
        p = os.path.join(work, f"part_{k:02d}.mp4")
        parts.append(p)
        # spawn (not fork): OpenCV's thread pool can deadlock in forked children
        pr = mp.get_context("spawn").Process(target=worker,
                                             args=(args, cfg, bounds[k], bounds[k + 1], p))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
        if pr.exitcode != 0:
            sys.exit(f"worker failed ({pr.exitcode})")

    lst = os.path.join(work, "parts.txt")
    with open(lst, "w") as fh:
        for p in parts:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    dur = (f1 - f0) / FPS
    start = ed.T0 + f0 / FPS
    fade_out = max(0.0, dur - 2.0)
    af = (f"volume=5dB,alimiter=limit=0.84:attack=5:release=60:level=0,"
          f"afade=t=in:st=0:d=0.25,afade=t=out:st={fade_out:.3f}:d=2.0")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-ss", f"{start:.4f}", "-t", f"{dur:.4f}", "-i", args.song,
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af,
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart",
         "-shortest", args.out], check=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
