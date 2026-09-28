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
from multiprocessing import Process

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
        for ev in self.texts:  # slams hit with a small flash
            if ev["style"] == "slam" and ev.get("mode") == "diff":
                dt = t_out - self.out_t(ev["b0"])
                if 0 <= dt < 0.5:
                    f += 0.35 * math.exp(-dt / 0.05)
        return min(1.0, f)

    def rgb_split_amount(self, t_out, idx, tl):
        s = self.shots[idx]
        a = 0.0
        if s.get("punch", 0) >= 0.12 or s.get("flash", 0) >= 0.8:
            a = max(a, 14 * math.exp(-tl / 0.09))
        for ev in self.texts:
            if ev["style"] in ("slam", "stack", "pulse"):
                dt = t_out - self.out_t(ev["b0"])
                if 0 <= dt < 0.5:
                    a = max(a, 10 * math.exp(-dt / 0.07))
        return a * self.cfg.sc

    # --- typography -----------------------------------------------------------
    def draw_texts(self, out, t_out, bp):
        cfg, ty, sc = self.cfg, self.typo, self.cfg.sc
        W, H = cfg.W, cfg.H
        for ev in self.texts:
            if not (ev["b0"] <= bp < ev["b1"]):
                continue
            te = t_out - self.out_t(ev["b0"])
            tleft = self.out_t(ev["b1"]) - t_out
            st = ev["style"]
            if st == "slam":
                m = ty.mask(ev["text"], "anton", ev.get("size", 380) * sc)
                fit = min(1.0, 0.9 * W / m.shape[1])
                s = fit * (1 + 0.45 * math.exp(-te / 0.055))
                sh = 0
                if ev.get("shake"):
                    sh = 12 * sc * math.exp(-te / 0.3)
                E.blit(out, m, W / 2 + sh * E.hash_noise(int(te * 300), 1),
                       H / 2 + sh * E.hash_noise(int(te * 300), 2), s, 1.0,
                       mode=ev.get("mode", "normal"), shadow=0.35 if ev.get("mode") != "diff" else 0)
            elif st == "serif":
                size = ev.get("size", 150) * sc
                words = ev["words"]
                masks = [ty.mask(w, "serif_i", size) for w in words]
                space = size * 0.28
                total = sum(m.shape[1] for m in masks) + space * (len(words) - 1)
                fit = min(1.0, 0.9 * W / total)
                x = W / 2 - total * fit / 2
                y = ev.get("y", 0.5) * H
                fade_out = E.clamp(tleft / 0.15)
                for w, m, b in zip(words, masks, ev["beats"]):
                    wt = t_out - self.out_t(ev["b0"] + b)
                    wm = m.shape[1] * fit
                    if wt >= 0:
                        a = E.ease_out(wt / 0.16) * fade_out
                        dy = 22 * sc * (1 - E.ease_out(wt / 0.3))
                        E.blit(out, m, x + wm / 2, y + dy, fit, a, shadow=0.55)
                    x += wm + space * fit
            elif st == "stack":
                lines = ev["lines"]
                n = len(lines)
                total_h = (0.98 if ev.get("big") else 0.78) * H
                lh = total_h / n
                y0 = H / 2 - total_h / 2 + lh / 2
                mode = ev.get("mode", "solid")
                for i, (ln, b) in enumerate(zip(lines, ev["beats"])):
                    lt = t_out - self.out_t(ev["b0"] + b)
                    if lt < 0:
                        continue
                    outline = mode == "outline" or (mode == "mixed" and i != 1)
                    size = lh * 1.18
                    m = ty.mask(ln, "anton", size, tracking=4 * sc,
                                outline=int(5 * sc) if outline else 0)
                    fit = min(lh * 0.98 / m.shape[0], 0.94 * W / m.shape[1])
                    s = fit * (1 + 0.3 * math.exp(-lt / 0.06))
                    E.blit(out, m, W / 2, y0 + i * lh, s, 1.0,
                           mode="diff" if mode == "diff" else "normal",
                           shadow=0 if mode == "diff" else 0.3)
            elif st == "kw":
                word_m = ty.mask(ev["word"], "anton", 260 * sc)
                fit = min(1.0, 0.62 * W / word_m.shape[1])
                side = ev.get("side", 0)
                cx = W * (0.36 if side == 0 else 0.64)
                cy = H * (0.52 if side == 0 else 0.56)
                s = fit * (1 + 0.35 * math.exp(-te / 0.06))
                fade = E.clamp(tleft / 0.08)
                E.blit(out, word_m, cx, cy, s, fade, shadow=0.45)
                pre = ty.mask(ev["pre"], "serif_i", 84 * sc)
                pa = E.ease_out(te / 0.12) * fade
                E.blit(out, pre, cx - word_m.shape[1] * fit / 2 + pre.shape[1] / 2,
                       cy - word_m.shape[0] * fit / 2 - pre.shape[0] * 0.55, 1.0, pa, shadow=0.5)
            elif st == "label":
                n_chars = int(te * 26)
                a = E.clamp(tleft / 0.25)
                x0 = 96 * sc
                if ev["text"]:
                    txt = ev["text"][:n_chars]
                    if txt:
                        m = ty.mask(txt, "mono_b", 46 * sc, tracking=14 * sc)
                        E.blit(out, m, x0 + m.shape[1] / 2, H * 0.80, 1.0, a, shadow=0.6)
                sub = ev["sub"][:max(0, n_chars - (len(ev["text"]) // 2))]
                if sub:
                    m2 = ty.mask("— " + sub, "mono", 26 * sc, tracking=6 * sc)
                    E.blit(out, m2, x0 + m2.shape[1] / 2, H * 0.80 + (46 if ev["text"] else 0) * sc,
                           1.0, a * 0.9, shadow=0.6)
            elif st == "track":
                dur = self.out_t(ev["b1"]) - self.out_t(ev["b0"])
                u = E.ease_out(te / dur, 2)
                m = ty.mask(ev["text"], "serif_i", 118 * sc, tracking=(4 + 34 * u) * sc)
                a = E.ease_io(te / 1.6) * E.clamp(tleft / 0.3)
                E.blit(out, m, W / 2, H * 0.47, 1.0, a, shadow=0.5)
                if ev.get("sub"):
                    m2 = ty.mask(ev["sub"], "mono", 24 * sc, tracking=(18 + 10 * u) * sc)
                    a2 = E.ease_io((te - 1.0) / 1.2) * E.clamp(tleft / 0.3)
                    E.blit(out, m2, W / 2, H * 0.47 + 95 * sc, 1.0, a2 * 0.85, shadow=0.5)
            elif st == "pulse":
                k = int(bp - ev["b0"])
                bt_ = t_out - self.out_t(ev["b0"] + k)
                outline = k % 2 == 1
                m = ty.mask(ev["text"], "anton", 520 * sc, outline=int(7 * sc) if outline else 0)
                fit = min(1.0, 0.96 * W / m.shape[1], 0.95 * H / m.shape[0])
                E.blit(out, m, W / 2, H / 2, fit * (1 + 0.14 * math.exp(-bt_ / 0.08)), 1.0,
                       mode="normal" if outline else "diff")
            elif st == "scatter":
                rng = np.random.default_rng(ev.get("seed", 0))
                nb = int(round(ev["b1"] - ev["b0"]))
                spots = [(rng.uniform(0.14, 0.86), rng.uniform(0.2, 0.8), rng.uniform(120, 230),
                          rng.uniform(-12, 12)) for _ in range(nb)]
                for k, (fx, fy, size, rot) in enumerate(spots):
                    lt = t_out - self.out_t(ev["b0"] + k)
                    if lt < 0:
                        continue
                    life = self.out_t(ev["b0"] + k + 1.6) - self.out_t(ev["b0"] + k)
                    a = E.ease_out(lt / 0.08) * E.clamp((life - lt) / 0.25) * E.clamp(tleft / 0.15)
                    if a <= 0:
                        continue
                    m = ty.mask(ev["text"], "serif_i", size * sc)
                    E.blit(out, m, fx * W, fy * H, 1 + 0.25 * math.exp(-lt / 0.07), a,
                           shadow=0.5, rot=rot)
            elif st == "echo":
                k = int(bp - ev["b0"])
                bt_ = t_out - self.out_t(ev["b0"] + k)
                m = ty.mask(ev["text"], "anton", 300 * sc)
                mo = ty.mask(ev["text"], "anton", 300 * sc, outline=int(4 * sc))
                fit = min(1.0, 0.72 * W / m.shape[1])
                h = m.shape[0] * fit
                fade = E.clamp(tleft / 0.2) * E.ease_out(te / 0.1)
                for i in range(1, 4):
                    if k >= i:
                        a = (0.75 - 0.2 * i) * fade
                        for sgn in (-1, 1):
                            E.blit(out, mo, W / 2, H / 2 + sgn * i * h * 0.92, fit, a)
                E.blit(out, m, W / 2, H / 2, fit * (1 + 0.08 * math.exp(-bt_ / 0.08)), fade,
                       shadow=0.4)
            elif st == "type":
                n_chars = int(te * 16) + 1
                txt = ev["text"][:n_chars]
                cursor = "_" if int(te * 4) % 2 == 0 else " "
                m = ty.mask(txt + cursor, "mono", 44 * sc, tracking=6 * sc)
                full = ty.mask(ev["text"] + "_", "mono", 44 * sc, tracking=6 * sc)
                E.blit(out, m, W / 2 - full.shape[1] / 2 + m.shape[1] / 2, H * 0.5, 1.0,
                       E.clamp(tleft / 0.1), shadow=0.6)

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
        pr = Process(target=worker, args=(args, cfg, bounds[k], bounds[k + 1], p))
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
    af = (f"volume=5dB,alimiter=limit=0.89:attack=5:release=60,"
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
