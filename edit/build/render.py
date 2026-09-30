"""Render the EDL to video, frame by frame.

Timing: every shot boundary is a song beat; its frame is computed from absolute
time, round((beat - B0) * period * FPS), never by adding shot lengths.

Inside a shot the source clock is driven by a speed curve (keyframes on song
beats) and pinned by an anchor: `at=(source_seconds, beat)` puts that exact
source moment on that beat -- the strike on the kick, the net on the downbeat.

    python3 build/render.py              # full render -> out/edit.mp4
    python3 build/render.py --from 12 --to 20   # shots 12..19 only (preview)
    python3 build/render.py --half       # 960x540 preview
"""
import argparse
import os
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import edl

ROOT = Path(__file__).resolve().parent.parent
BUILD, MEDIA, OUT = ROOT / "build", ROOT / "media", ROOT / "out"
FONTS = ROOT / "assets" / "fonts"
FPS = 50
SRC = Path(os.environ.get("EDIT_SRC", MEDIA / "src"))

GRID = json.loads((BUILD / "grid.json").read_text())
PER, OFF = GRID["period"], GRID["offset"]


def tb(b):
    """Song time of beat b."""
    return OFF + b * PER


def fb(b):
    """Output frame of beat b, from absolute time."""
    return round((b - edl.B0) * PER * FPS)


# ---------------------------------------------------------------- sources

_probe = {}


def probe(key):
    if key not in _probe:
        path = next(p for p in SRC.glob(key + ".*") if p.suffix in (".mp4", ".webm", ".mkv", ".mov"))
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,r_frame_rate,field_order", "-show_entries", "format=duration",
             "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
        j = json.loads(out)
        s = j["streams"][0]
        num, den = map(int, s["r_frame_rate"].split("/"))
        _probe[key] = dict(path=path, w=s["width"], h=s["height"], fps=num / den,
                           dur=float(j["format"]["duration"]),
                           interlaced=s.get("field_order", "progressive") not in ("progressive", "unknown"))
    return _probe[key]


_DIS = None


def interpolate(A, B, a, cache, key):
    """In-between frame at fraction a from A to B via dense optical flow.
    Across a camera cut (large difference) it falls back to the nearer frame."""
    global _DIS
    if key not in cache:
        cache.clear()
        h, w = A.shape[:2]
        sw, sh = w // 4, h // 4
        ga = cv2.cvtColor(cv2.resize(A, (sw, sh), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        gb = cv2.cvtColor(cv2.resize(B, (sw, sh), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        if np.abs(ga.astype(np.int16) - gb).mean() > 38:
            cache[key] = None
        else:
            if _DIS is None:
                _DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
            fab = cv2.resize(_DIS.calc(ga, gb, None), (w, h)) * 4
            fba = cv2.resize(_DIS.calc(gb, ga, None), (w, h)) * 4
            gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
            cache[key] = (fab, fba, gx, gy)
    f = cache[key]
    if f is None:
        return A if a < 0.5 else B
    fab, fba, gx, gy = f
    a = float(a)  # a numpy float64 would promote the maps out of float32
    wa = cv2.remap(A, gx - a * fab[..., 0], gy - a * fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.remap(B, gx - (1 - a) * fba[..., 0], gy - (1 - a) * fba[..., 1], cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(wa, 1 - a, wb, a, 0)


class Reader:
    """Sequential decoder for one source window, cover-scaled to (w, h).

    Frames come out at a forced constant rate, so frame n sits at t0 + n / rate
    and the nearest source frame for any time is a plain rounding.
    """

    def __init__(self, key, t0, t1, w, h, focus=(0.5, 0.5), fit="fill", crop=None):
        p = probe(key)
        self.rate = p["fps"] * (2 if p["interlaced"] else 1)
        # snap to a source frame and seek half a frame early, so decoded
        # frame 0 is exactly the frame at self.t0
        k = max(0, math.floor(t0 * self.rate))
        self.t0, self.w, self.h = k / self.rate, w, h
        seek = max(0.0, (k - 0.5) / self.rate)
        vf = []
        if p["interlaced"]:
            vf.append("bwdif=mode=send_field")
        if crop:  # (x0, y0, x1, y1) normalised: cut away burned-in graphics first
            x0, y0, x1, y1 = crop
            vf.append(f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f}")
        fx, fy = focus
        if fit == "fill":
            vf += [f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos",
                   f"crop={w}:{h}:(iw-{w})*{fx}:(ih-{h})*{fy}"]
            chain = ",".join(vf)
        else:  # "blur": fit inside, blurred cover behind (for 4:3 material)
            pre = ",".join(vf) + "," if vf else ""
            chain = (f"{pre}split[a][b];"
                     f"[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
                     f"boxblur=24:2,eq=brightness=-0.12[bg];"
                     f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
                     f"[bg][fg]overlay=(W-w)/2:(H-h)/2")
        chain += f",setpts=PTS-STARTPTS,fps={self.rate:.6f},format=rgb24"
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", f"{seek:.4f}", "-i", str(p["path"]),
             "-t", f"{t1 - self.t0 + 0.5:.4f}", "-filter_complex", chain,
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=w * h * 3 * 4)
        self.n, self.frames = -1, {}
        self.size = w * h * 3
        self.flow_cache = {}

    def _frame(self, i):
        """Source frame i of the window; past the end the last one is held."""
        while self.n < i:
            buf = self.proc.stdout.read(self.size)
            if len(buf) < self.size:
                break
            self.n += 1
            self.frames[self.n] = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.frames.pop(self.n - 3, None)
        if not self.frames:
            raise RuntimeError(f"no frames decoded at index {i}")
        if i in self.frames:
            return self.frames[i]
        return self.frames[min(self.frames, key=lambda k: abs(k - i))]

    def get(self, t):
        """Frame at source time t; between two source frames, a motion-compensated
        in-between (the sources run at 24-30 fps, the edit at 50 and in slow motion)."""
        x = max(0.0, (t - self.t0) * self.rate)
        i = int(math.floor(x))
        a = x - i
        A = self._frame(i)
        if a < 0.12:
            return A
        B = self._frame(i + 1)
        if B is A:
            return A
        if a > 0.88:
            return B
        return interpolate(A, B, a, self.flow_cache, i)

    def close(self):
        self.proc.stdout.close()
        self.proc.kill()
        self.proc.wait()


# ---------------------------------------------------------------- clocks

def source_times(clip, b0, b1):
    """Source time for every output frame of a shot (or panel)."""
    f0, f1 = fb(b0), fb(b1)
    n = f1 - f0
    beats = edl.B0 + (np.arange(f0, f1) / FPS) / PER  # song beat of each frame
    sp = clip.get("speed", 1.0)
    if isinstance(sp, (int, float)):
        v = np.full(n, float(sp))
    else:  # keyframes [(beat, speed), ...], linear in between, held outside
        kb, kv = zip(*sp)
        v = np.interp(beats, kb, kv)
    ts = np.concatenate([[0.0], np.cumsum((v[1:] + v[:-1]) / 2)]) / FPS
    src, beat = clip.get("at", (clip.get("tin", 0.0), b0))
    ia = (fb(beat) - f0)
    ts_at = np.interp(ia, np.arange(n), ts) if 0 <= ia < n else (
        ts[0] + (ia) * v[0] / FPS if ia < 0 else ts[-1] + (ia - n + 1) * v[-1] / FPS)
    return ts - ts_at + src


# ---------------------------------------------------------------- look

def curve_lut(contrast=1.0, lift=0.0, gamma=1.0):
    x = np.arange(256) / 255.0
    y = np.clip(x, 0, 1) ** gamma
    y = 0.5 + (y - 0.5) * contrast            # linear contrast around mid grey
    y = y + 0.06 * (contrast - 1) * np.sin(2 * np.pi * y) * -1  # soft S
    y = lift + y * (1 - lift)
    return np.clip(y * 255, 0, 255).astype(np.uint8)


GRADES = {
    #        contrast lift  gamma  sat   r     g     b     vignette
    "base": (1.10, 0.00, 1.00, 1.12, 1.02, 1.00, 0.98, 0.22),
    "cold": (1.06, 0.03, 1.04, 0.58, 0.93, 1.00, 1.08, 0.38),
    "warm": (1.12, 0.00, 0.97, 1.20, 1.07, 1.00, 0.90, 0.25),
    "mono": (1.25, 0.02, 1.00, 0.00, 1.00, 1.00, 1.00, 0.35),
}


class Look:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.luts = {k: curve_lut(c, l, g) for k, (c, l, g, *_rest) in GRADES.items()}
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
        self.vig_r = np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6
        rng = np.random.default_rng(7)
        self.grain = [rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32) for _ in range(12)]

    def apply(self, img, grade, grain, fi):
        c, l, g, sat, rm, gm, bm, vig = GRADES[grade]
        img = cv2.LUT(img, self.luts[grade]).astype(np.float32)
        luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
        img = luma[..., None] + sat * (img - luma[..., None])
        img *= np.array([rm, gm, bm], np.float32)
        img *= (1 - vig * self.vig_r)[..., None]
        if grain:
            n = cv2.resize(self.grain[fi % len(self.grain)], (self.w, self.h),
                           interpolation=cv2.INTER_LINEAR)
            img += (grain * n)[..., None]
        return np.clip(img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- text

class Text:
    def __init__(self, w, h):
        self.w, self.h, self.cache = w, h, {}
        self.s = w / 1920

    def font(self, name, size):
        return ImageFont.truetype(str(FONTS / name), max(8, int(size * self.s)))

    def layer(self, kind, text):
        key = (kind, text)
        if key in self.cache:
            return self.cache[key]
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        s = self.s
        if kind == "label":   # small, lower left: which goal this is
            f = self.font("BebasNeue-Regular.ttf", 46)
            x, y = int(70 * s), int(self.h - 118 * s)
            d.rectangle([x, y + int(6 * s), x + int(6 * s), y + int(44 * s)], fill=(218, 32, 28, 255))
            d.text((x + int(20 * s) + 2, y + 2), text, font=f, fill=(0, 0, 0, 150))
            d.text((x + int(20 * s), y), text, font=f, fill=(255, 255, 255, 240))
        elif kind == "title":  # big name card, centred low
            name, _, num = text.partition("|")
            f = self.font("Anton-Regular.ttf", 150)
            fn = self.font("Anton-Regular.ttf", 150)
            bw = d.textlength(name, font=f)
            nw = d.textlength(num, font=fn) if num else 0
            gap = int(34 * s) if num else 0
            x = (self.w - bw - nw - gap) / 2
            y = self.h * 0.60
            d.text((x + 4, y + 4), name, font=f, fill=(0, 0, 0, 120))
            d.text((x, y), name, font=f, fill=(255, 255, 255, 250))
            if num:
                d.text((x + bw + gap, y), num, font=fn, fill=(218, 32, 28, 255))
        elif kind == "end":
            f = self.font("Anton-Regular.ttf", 120)
            f2 = self.font("BebasNeue-Regular.ttf", 54)
            a, _, b = text.partition("|")
            aw = d.textlength(a, font=f)
            d.text(((self.w - aw) / 2, self.h * 0.40), a, font=f, fill=(255, 255, 255, 250))
            bw = d.textlength(b, font=f2)
            d.text(((self.w - bw) / 2, self.h * 0.40 + 170 * s), b, font=f2, fill=(218, 32, 28, 255))
        arr = np.asarray(im, np.float32) / 255.0
        self.cache[key] = arr
        return arr

    def over(self, img, kind, text, alpha, dx=0):
        lay = self.layer(kind, text)
        if dx:
            lay = np.roll(lay, int(dx), axis=1)
        a = lay[..., 3:4] * alpha
        return (img.astype(np.float32) * (1 - a) + lay[..., :3] * 255 * a).astype(np.uint8)


# ---------------------------------------------------------------- compositing

def zoom_warp(img, z, cx, cy, dx=0.0, dy=0.0, rot=0.0):
    """Scale by z around (cx, cy) in pixels, then shift; one resample."""
    h, w = img.shape[:2]
    if abs(z - 1) < 1e-4 and not dx and not dy and not rot:
        return img
    M = cv2.getRotationMatrix2D((cx, cy), rot, z)  # (cx, cy) stays put
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def fx_state(shot, i, n, bpos, rng):
    """Zoom multiplier, shake offset, overlays for frame i of n."""
    fx = shot.get("fx", ())
    z, dx, dy, rot = 1.0, 0.0, 0.0, 0.0
    white = black = 0.0
    split = 0.0
    tsec = i / FPS
    if "punch" in fx:
        k = max(0.0, 1 - tsec / 0.24)
        z *= 1 + 0.085 * k * k
    if "thump" in fx or "thump_soft" in fx:
        amp = 0.028 if "thump" in fx else 0.014
        ph = bpos - math.floor(bpos + 1e-6)
        first = math.floor(bpos + 1e-6) == math.floor(shot["b0"] + 1e-6)
        if not (first and "punch" in fx):
            down = (math.floor(bpos + 1e-6) % 4 == 0)
            z *= 1 + amp * (1.6 if down else 1.0) * max(0.0, 1 - ph / 0.4) ** 2
    if "push" in shot:
        p0, p1 = shot["push"]
        z *= p0 + (p1 - p0) * (i / max(1, n - 1))
    for sb in shot.get("shake", ()):
        dt = (bpos - sb) * PER
        if 0 <= dt < 0.45:
            a = 22 * math.exp(-dt / 0.12)
            dx += a * rng.uniform(-1, 1)
            dy += a * rng.uniform(-1, 1)
            rot += 0.35 * a / 22 * rng.uniform(-1, 1)
            z *= 1 + 0.05 * math.exp(-dt / 0.12)  # margin so edges never show
    if "flash" in fx:
        white = max(white, 0.9 * max(0.0, 1 - tsec / 0.16))
    for fb_ in shot.get("flash_at", ()):
        dt = (bpos - fb_) * PER
        if 0 <= dt < 0.16:
            white = max(white, 0.75 * (1 - dt / 0.16))
    if "rgbhit" in fx:
        split = 26 * max(0.0, 1 - tsec / 0.2)
    if "dip" in fx:
        black = max(black, max(0.0, 1 - tsec / 0.14))
    if "open" in fx:
        black = max(black, max(0.0, 1 - tsec / (PER * shot.get("open_beats", 2))))
    if "close" in fx:
        cb = shot.get("close_beats", 2)
        left = (shot["b1"] - bpos) * PER
        black = max(black, max(0.0, 1 - left / (PER * cb)))
    return z, dx, dy, rot, white, black, split


def render_panel(reader, t, rect, focus, W, H):
    """Cut a panel of rect (x0,y0,x1,y1 in px) out of a full-frame source."""
    x0, y0, x1, y1 = rect
    pw, ph = x1 - x0, y1 - y0
    frame = reader.get(t)
    fh, fw = frame.shape[:2]
    # crop the largest box of panel aspect around focus, then resize
    ar = pw / ph
    cw, ch = (fw, fw / ar) if fw / fh < ar else (fh * ar, fh)
    cx = min(max(focus[0] * fw, cw / 2), fw - cw / 2)
    cy = min(max(focus[1] * fh, ch / 2), fh - ch / 2)
    crop = frame[int(cy - ch / 2):int(cy + ch / 2), int(cx - cw / 2):int(cx + cw / 2)]
    return cv2.resize(crop, (pw, ph), interpolation=cv2.INTER_AREA if cw > pw else cv2.INTER_LINEAR)


def layout_at(shot, bpos, W, H):
    keys = shot["layouts"]
    cur = keys[0][1]
    prev = cur
    tstart = keys[0][0]
    for b, rects in keys:
        if bpos + 1e-6 >= b:
            prev, cur, tstart = cur, rects, b
    k = ease((bpos - tstart) * PER / 0.11)
    out = []
    for r0, r1 in zip(prev, cur):
        r = [a + (b_ - a) * k for a, b_ in zip(r0, r1)]
        out.append((int(r[0] * W), int(r[1] * H), int(r[2] * W), int(r[3] * H)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="s0", type=int, default=0)
    ap.add_argument("--to", dest="s1", type=int, default=None)
    ap.add_argument("--half", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    W, H = (960, 540) if a.half else (1920, 1080)
    shots = edl.shots()
    sel = shots[a.s0:a.s1]
    OUT.mkdir(exist_ok=True)
    name = a.out or ("edit_video.mp4" if (a.s0 == 0 and a.s1 is None) else f"preview_{a.s0}_{a.s1}.mp4")
    dst = OUT / name
    look, text = Look(W, H), Text(W, H)
    rng = np.random.default_rng(3)

    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12",
         "-pix_fmt", "yuv420p", str(dst)], stdin=subprocess.PIPE)

    for si, shot in enumerate(sel, start=a.s0):
        f0, f1 = fb(shot["b0"]), fb(shot["b1"])
        n = f1 - f0
        grade = shot.get("grade", "base")
        grain = {"grain": 6.0, "grain_heavy": 12.0}.get(
            next((x for x in shot.get("fx", ()) if x.startswith("grain")), ""), 0.0)
        if shot.get("black"):
            blk = np.zeros((H, W, 3), np.uint8).tobytes()
            for _ in range(n):
                enc.stdin.write(blk)
            print(f"shot {si:3d}  beats {shot['b0']:>6}-{shot['b1']:<6} frames {f0:5d}-{f1:5d}  black", flush=True)
            continue
        panels = shot.get("panels") or [shot]
        readers, clocks = [], []
        for p in panels:
            ts = source_times(p, shot["b0"], shot["b1"])
            clocks.append(ts)
            readers.append(Reader(p["src"], float(ts.min()) - 0.05, float(ts.max()) + 0.05, W, H,
                                  p.get("focus", (0.5, 0.5)), p.get("fit", "fill"), p.get("crop")))
        for i in range(n):
            bpos = edl.B0 + (f0 + i) / FPS / PER
            z, dx, dy, rot, white, black, split = fx_state(shot, i, n, bpos, rng)
            if "layouts" in shot:
                img = np.zeros((H, W, 3), np.uint8)
                for r, rect, ts, p in zip(readers, layout_at(shot, bpos, W, H), clocks, panels):
                    x0, y0, x1, y1 = rect
                    if x1 - x0 < 4 or y1 - y0 < 4:
                        continue
                    img[y0:y1, x0:x1] = render_panel(r, ts[i], rect, p.get("focus", (0.5, 0.5)), W, H)
                    # hairline gutter
                    cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (0, 0, 0), max(2, W // 320))
            else:
                img = readers[0].get(clocks[0][i])
            zc = shot.get("zoom", 1.0) * z
            cx, cy = shot.get("zc", (0.5, 0.5))
            img = zoom_warp(img, zc, cx * W, cy * H, dx * W / 1920, dy * W / 1920, rot)
            if split > 0.5:
                s = int(split * W / 1920)
                img = img.copy()
                img[:, s:, 0] = img[:, :-s, 0]
                img[:, :-s, 2] = img[:, s:, 2]
            img = look.apply(img, grade, grain, f0 + i)
            if white > 0:
                img = (img.astype(np.float32) * (1 - white) + 255 * white).astype(np.uint8)
            for kind in ("label", "title", "end"):
                if kind in shot:
                    tsec, dur = i / FPS, n / FPS
                    delay = shot.get(kind + "_delay", 0.0) * PER  # in beats
                    fade_out = min(1.0, (dur - tsec) / 0.18) if kind != "end" else 1.0
                    al = min(1.0, max(0.0, (tsec - delay) / 0.18)) * fade_out
                    slide = (1 - ease((tsec - delay) / 0.35)) * 40 * W / 1920 if kind == "label" else 0
                    if al > 0:
                        img = text.over(img, kind, shot[kind], al, -slide)
            if black > 0:
                img = (img.astype(np.float32) * (1 - black)).astype(np.uint8)
            enc.stdin.write(np.ascontiguousarray(img).tobytes())
        for r in readers:
            r.close()
        print(f"shot {si:3d}  beats {shot['b0']:>6}-{shot['b1']:<6} frames {f0:5d}-{f1:5d}  {shot.get('src', 'split')}", flush=True)

    enc.stdin.close()
    enc.wait()
    print("wrote", dst)


if __name__ == "__main__":
    main()
