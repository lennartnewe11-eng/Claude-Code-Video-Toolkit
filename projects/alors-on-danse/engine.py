"""Frame compositor for the beat-synced edit.

Everything here is stateless per output frame (given the timeline), so the
render can be split into independent chunks and run in parallel.
"""
import math
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

FPS = 30


class Cfg:
    def __init__(self, scale=1.0, media=".", fonts="."):
        self.sc = scale
        self.W = int(round(1920 * scale / 2) * 2)
        self.H = int(round(1080 * scale / 2) * 2)
        # decode resolution: 1.2x the output so zooms stay sharp
        self.SW = int(round(2304 * scale / 2) * 2)
        self.SH = int(round(1296 * scale / 2) * 2)
        self.media = media
        self.fonts = fonts


# ----------------------------------------------------------------------------
# small math helpers
# ----------------------------------------------------------------------------

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(u, p=3.0):
    u = clamp(u)
    return 1 - (1 - u) ** p


def ease_io(u):
    u = clamp(u)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def lerp(a, b, u):
    return a + (b - a) * u


def pw_linear(points, x):
    """Piecewise linear interpolation over [(x, y), ...]."""
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / max(1e-9, x1 - x0)
    return points[-1][1]


def hash_noise(n, k):
    """Deterministic pseudo random in [-1, 1] for frame n, channel k."""
    x = math.sin(n * 12.9898 + k * 78.233) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


# ----------------------------------------------------------------------------
# source preparation
# ----------------------------------------------------------------------------

def media_path(cfg, name):
    for ext in (".mov", ".jpeg", ".jpg", ""):
        p = os.path.join(cfg.media, name + ext)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(name)


def load_photo(cfg, name):
    im = ImageOps.exif_transpose(Image.open(media_path(cfg, name))).convert("RGB")
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)


def cover_crop(img, w, h, fx=0.5, fy=0.5):
    """Resize+crop img to exactly w x h, keeping the focus point in view."""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    nw, nh = int(math.ceil(iw * s)), int(math.ceil(ih * s))
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    x0 = int(clamp(fx * nw - w / 2, 0, nw - w))
    y0 = int(clamp(fy * nh - h / 2, 0, nh - h))
    return np.ascontiguousarray(r[y0:y0 + h, x0:x0 + w])


def build_panels(cfg, imgs, focus=None, gap=None):
    """Side-by-side panels filling SWxSH; returns (frame, list of x-ranges)."""
    n = len(imgs)
    gap = int(10 * cfg.sc) if gap is None else gap
    focus = focus or [(0.5, 0.5)] * n
    pw = (cfg.SW - gap * (n - 1)) // n
    out = np.zeros((cfg.SH, cfg.SW, 3), np.uint8)
    ranges = []
    x = 0
    for i, im in enumerate(imgs):
        w = pw if i < n - 1 else cfg.SW - x
        out[:, x:x + w] = cover_crop(im, w, cfg.SH, *focus[i])
        ranges.append((x, x + w))
        x += w + gap
    return out, ranges


class VReader:
    """Streams decoded frames of one shot from ffmpeg (sequential access)."""

    def __init__(self, cfg, name, t_in, nframes, mode="land"):
        self.cfg = cfg
        SW, SH = cfg.SW, cfg.SH
        if mode == "land":
            vf = f"fps={FPS},scale={SW}:{SH}:flags=bicubic,setsar=1"
        elif mode == "blur":  # portrait clip on a blurred copy of itself
            fh = SH
            vf = (f"fps={FPS},split[a][b];[a]scale={SW}:-2,crop={SW}:{SH},"
                  f"boxblur=40:3,eq=brightness=-0.06:saturation=0.9[bg];"
                  f"[b]scale=-2:{fh}[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1")
        elif mode == "tri":  # the same portrait clip three times side by side
            gap = int(10 * cfg.sc)
            pw = (SW - 2 * gap) // 3
            last = SW - 2 * (pw + gap)
            vf = (f"fps={FPS},scale={pw}:-2,crop={pw}:{SH},split=3[a][b][c];"
                  f"[c]pad={last}:{SH}:0:0[c2];"
                  f"[a]pad={pw + gap}:{SH}:0:0[a2];[b]pad={pw + gap}:{SH}:0:0[b2];"
                  f"[a2][b2][c2]hstack=3,setsar=1")
            self.ranges = [(0, pw), (pw + gap, 2 * pw + gap), (2 * (pw + gap), SW)]
        else:
            raise ValueError(mode)
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t_in):.3f}",
               "-i", media_path(cfg, name), "-frames:v", str(nframes),
               "-filter_complex" if ";" in vf else "-vf", vf,
               "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, bufsize=SW * SH * 3 * 2)
        self.fsize = SW * SH * 3
        self.cache = {}
        self.idx = -1

    def get(self, k):
        k = max(0, k)
        while self.idx < k:
            buf = self.p.stdout.read(self.fsize)
            if len(buf) < self.fsize:
                break
            self.idx += 1
            self.cache[self.idx] = np.frombuffer(buf, np.uint8).reshape(
                self.cfg.SH, self.cfg.SW, 3)
            for old in [i for i in self.cache if i < self.idx - 2]:
                del self.cache[old]
        if not self.cache:
            return np.zeros((self.cfg.SH, self.cfg.SW, 3), np.uint8)
        k = min(k, self.idx)
        while k not in self.cache and k < self.idx:
            k += 1
        return self.cache[k]

    def close(self):
        try:
            self.p.stdout.close()
            self.p.kill()
            self.p.wait()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# colour looks
# ----------------------------------------------------------------------------

def _curve(x, contrast, black=0.0, white=1.0, gamma=1.0):
    x = np.clip((x - black) / (white - black), 0, 1) ** gamma
    # smooth S-curve blended by `contrast`
    s = x * x * (3 - 2 * x)
    return np.clip(x + contrast * (s - x), 0, 1)


def make_look(name):
    x = np.arange(256) / 255.0
    sat, bloom, lift = 1.0, 0.0, 0.0
    if name == "bw":
        c = _curve(x, 0.85, black=0.05, white=0.95, gamma=1.08)
        luts = [c, c, c]
        sat = 0.0
    elif name == "dream":
        c = _curve(x, 0.15, gamma=0.95)
        luts = [c * 0.93 + 0.07, c * 0.92 + 0.06, c * 0.88 + 0.05]  # lifted, warm
        luts = [np.clip(l * 1.0 + 0.02, 0, 1) for l in luts]
        sat, bloom = 0.9, 0.45
    elif name == "warm":
        c = _curve(x, 0.40, black=0.02, gamma=1.02)
        luts = [np.clip(c * 1.03 + 0.01, 0, 1), c, np.clip(c * 0.94, 0, 1)]
        sat, bloom = 1.18, 0.22
    elif name == "night":
        c = _curve(x, 0.45, black=0.03, gamma=0.88)
        luts = [np.clip(c * 1.02, 0, 1), c, np.clip(c * 1.02 + 0.015 * (1 - x), 0, 1)]
        sat, bloom = 1.12, 0.25
    elif name == "vivid":
        c = _curve(x, 0.45, black=0.03, gamma=1.02)
        luts = [np.clip(c + 0.02 * (x - 0.3), 0, 1), c, np.clip(c + 0.03 * (0.5 - x), 0, 1)]
        sat = 1.2
    else:  # "cine": gentle teal/orange split with crushed blacks
        c = _curve(x, 0.42, black=0.035, gamma=1.03)
        luts = [np.clip(c + 0.025 * (x - 0.45), 0, 1), c,
                np.clip(c + 0.035 * (0.45 - x), 0, 1)]
        sat = 1.06
    lut = np.stack([np.clip(l * 255, 0, 255).astype(np.uint8) for l in luts[::-1]], -1)  # BGR
    return {"lut": lut.reshape(256, 1, 3), "sat": sat, "bloom": bloom, "lift": lift}


LOOKS = {k: make_look(k) for k in ("bw", "dream", "warm", "night", "vivid", "cine")}


def grade(img, look, ev=1.0, desat=0.0):
    L = LOOKS[look]
    if ev != 1.0:
        img = cv2.convertScaleAbs(img, alpha=ev)
    out = cv2.LUT(img, L["lut"])
    sat = L["sat"] * (1 - desat)
    if abs(sat - 1.0) > 1e-3:
        g = cv2.cvtColor(cv2.cvtColor(out, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        out = cv2.addWeighted(out, sat, g, 1 - sat, 0)
    if L["bloom"] > 0:
        h, w = out.shape[:2]
        small = cv2.resize(out, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        hi = cv2.subtract(small, (150, 150, 150, 0))
        hi = cv2.GaussianBlur(hi, (0, 0), 6 * w / 1920 * 4 / 4 + 3)
        hi = cv2.resize(hi, (w, h), interpolation=cv2.INTER_LINEAR)
        out = cv2.addWeighted(out, 1.0, hi, L["bloom"] * 1.6, 0)
    return out


# ----------------------------------------------------------------------------
# typography
# ----------------------------------------------------------------------------

class Typo:
    """One calligraphic script (Ballet, OFL) for every lyric, with a crayon texture."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.path = os.path.join(cfg.fonts, "Ballet.ttf")
        self.cache = {}

    def font(self, size):
        key = ("font", size)
        if key not in self.cache:
            self.cache[key] = ImageFont.truetype(self.path, size)
        return self.cache[key]

    def mask(self, text, size, texture=True):
        """Tight alpha mask (float32 0..1) of `text`, swashes included."""
        size = max(8, int(round(size)))
        key = ("mask", text, size, texture)
        if key in self.cache:
            return self.cache[key]
        fnt = self.font(size)
        W = int(fnt.getlength(text)) + 3 * size
        H = int(size * 3.2)
        img = Image.new("L", (W, H), 0)
        ImageDraw.Draw(img).text((size * 1.2, size * 0.9), text, font=fnt, fill=255)
        m = np.asarray(img, np.float32) / 255.0
        ys, xs = np.nonzero(m > 0.01)
        if len(xs):
            m = m[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
        if size >= 60:  # a slightly heavier nib so hairlines survive on moving footage
            k = max(2, int(round(size / 110)))
            m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        if texture:
            m = crayon(m, seed=sum(map(ord, text)) + size, sc=size / 300.0)
        self.cache[key] = np.ascontiguousarray(m)
        return self.cache[key]


def crayon(m, seed=1, sc=1.0):
    """Wobbly edge + grainy fill, like a wax crayon / pencil stroke."""
    rng = np.random.default_rng(seed)
    h, w = m.shape
    sig = max(1.0, 2.0 * sc)
    amp = max(0.8, 2.2 * sc)
    dx = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sig) * amp * 2.5
    dy = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sig) * amp * 2.5
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    mm = cv2.remap(m, gx + dx, gy + dy, cv2.INTER_LINEAR)
    g = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 0.7)
    g = (g - g.min()) / max(1e-6, g.max() - g.min())
    return np.clip(mm * (0.55 + 0.45 * g) * 1.18, 0, 1)


def blit(out, m, cx, cy, scale=1.0, alpha=1.0, color=(255, 255, 255), mode="normal",
         shadow=0.0, rot=0.0, wipe=1.0):
    """Composite alpha mask `m` centred at (cx, cy) onto `out` in place.

    wipe < 1 reveals the mask from the left (a soft pen-stroke write-on)."""
    if alpha <= 0.003 or m is None or m.size == 0 or wipe <= 0:
        return
    if wipe < 1.0:
        w_ = m.shape[1]
        soft = 0.18 * w_
        x = np.arange(w_, dtype=np.float32)
        ramp = np.clip((wipe * (w_ + soft) - x) / soft, 0, 1)
        m = m * ramp[None, :]
    if abs(scale - 1.0) > 1e-3 or abs(rot) > 1e-3:
        h, w = m.shape
        s = max(scale, 0.01)
        nw, nh = int(w * s * 1.3) + 4, int(h * s * 1.3) + 4
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, s)
        M[0, 2] += nw / 2 - w / 2
        M[1, 2] += nh / 2 - h / 2
        m = cv2.warpAffine(m, M, (nw, nh), flags=cv2.INTER_LINEAR)
    H, W = out.shape[:2]
    h, w = m.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0] * alpha
    roi = out[ya:yb, xa:xb].astype(np.float32)
    if shadow > 0:
        sh = cv2.GaussianBlur(mm, (0, 0), max(1.0, h * 0.04))
        roi *= (1 - sh * shadow)[..., None]
    a = mm[..., None]
    if mode == "diff":
        roi = roi * (1 - a) + (255.0 - roi) * a
    else:
        col = np.array(color, np.float32)[::-1]
        roi = roi * (1 - a) + col * a
    out[ya:yb, xa:xb] = np.clip(roi, 0, 255).astype(np.uint8)
