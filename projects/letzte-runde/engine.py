"""Frame-accurate compositing engine for vertical short-form edits.

Everything is driven by plain data (see edl.py): shots with time-remap curves,
impact events, text cards and a HUD. Frames are rendered in numpy/OpenCV and
piped straight into ffmpeg, so there is no intermediate image sequence on disk.
"""
from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.interpolate import PchipInterpolator

W, H, FPS = 1080, 1920, 30
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


# ---------------------------------------------------------------------------
# easing helpers
# ---------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------------------
# source footage
# ---------------------------------------------------------------------------
def probe(path: Path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
        "-of", "csv=p=0", str(path)]).decode().strip().split(",")
    w, h = int(out[0]), int(out[1])
    num, den = out[2].split("/")
    return w, h, float(num) / float(den)


@dataclass
class Shot:
    """One cut of the edit.

    clip      Mixkit clip id (assets/video/<clip>.mp4)
    t0, t1    position in the timeline (seconds)
    remap     [(timeline_t, source_t), ...] – monotone curve, PCHIP-interpolated,
              so speed ramps accelerate/decelerate smoothly.
    crop      (cx, cy, ch): 9:16 window centred at cx/cy (0..1 of source),
              height = ch * source height.
    zoom      [(t, z)] keyframes, z=1 → crop fills the frame.
    focus     (fx, fy) zoom anchor inside the crop (0..1).
    look      colour pipeline name (see LOOKS).
    hold      if set, source time is frozen at this value (freeze frame).
    """
    clip: str
    t0: float
    t1: float
    remap: list
    crop: tuple = (0.5, 0.5, 1.0)
    zoom: list = field(default_factory=lambda: [(0, 1.0)])
    focus: tuple = (0.5, 0.5)
    look: str = "fight"
    pan: list = field(default_factory=list)  # [(t, dx, dy)] in output px
    sharpen: float = 0.0
    dehaze: float = 0.0  # black-point pull for hazy, backlit footage
    wide: float = 1.0    # decode wider than 9:16 so focus_keys can pan across
    focus_keys: list = field(default_factory=list)  # [(t, fx, fy)] animated zoom anchor

    # filled in by load()
    frames: np.ndarray | None = None
    first: int = 0
    fps: float = 24.0

    def src_time(self, t):
        ts = [p[0] for p in self.remap]
        ss = [p[1] for p in self.remap]
        if len(ts) == 1:
            return ss[0]
        if len(ts) == 2:
            return float(np.interp(t, ts, ss))
        return float(PchipInterpolator(ts, ss)(clamp(t, ts[0], ts[-1])))

    def speed(self, t, dt=1 / FPS):
        return (self.src_time(t + dt / 2) - self.src_time(t - dt / 2)) / dt

    def zoom_at(self, t):
        ts = [k[0] for k in self.zoom]
        zs = [k[1] for k in self.zoom]
        if len(ts) == 1:
            return zs[0]
        # eased between keyframes
        if t <= ts[0]:
            return zs[0]
        for i in range(len(ts) - 1):
            if ts[i] <= t <= ts[i + 1]:
                u = (t - ts[i]) / max(1e-6, ts[i + 1] - ts[i])
                return zs[i] + (zs[i + 1] - zs[i]) * ease_in_out(u)
        return zs[-1]

    def focus_at(self, t):
        if not self.focus_keys:
            return self.focus
        ts = [k[0] for k in self.focus_keys]
        return (float(np.interp(t, ts, [k[1] for k in self.focus_keys])),
                float(np.interp(t, ts, [k[2] for k in self.focus_keys])))

    def pan_at(self, t):
        if not self.pan:
            return 0.0, 0.0
        ts = [k[0] for k in self.pan]
        return (float(np.interp(t, ts, [k[1] for k in self.pan])),
                float(np.interp(t, ts, [k[2] for k in self.pan])))


def load_shot(shot: Shot, max_zoom: float):
    """Decode exactly the source frames this shot touches, cropped to 9:16 and
    pre-scaled so the largest zoom in the shot never upsamples twice."""
    path = ASSETS / "video" / f"{shot.clip}.mp4"
    sw, sh, fps = probe(path)
    shot.fps = fps
    samples = np.linspace(shot.t0, shot.t1, int((shot.t1 - shot.t0) * FPS * 4) + 2)
    srcs = [shot.src_time(t) for t in samples]
    lo = max(0, int(math.floor(min(srcs) * fps)) - 2)
    hi = int(math.ceil(max(srcs) * fps)) + 2
    cx, cy, ch = shot.crop
    ch_px = min(sh, ch * sh)
    cw_px = ch_px * 9 / 16 * shot.wide
    if cw_px > sw:
        cw_px = sw
        ch_px = cw_px * 16 / 9 / shot.wide
    x = clamp(cx * sw - cw_px / 2, 0, sw - cw_px)
    y = clamp(cy * sh - ch_px / 2, 0, sh - ch_px)
    cw, chh = int(cw_px) // 2 * 2, int(ch_px) // 2 * 2
    x, y = int(x) // 2 * 2, int(y) // 2 * 2
    pz = max(1.0, max_zoom)
    pw, ph = int(round(W * pz * shot.wide / 2) * 2), int(round(H * pz / 2) * 2)
    # never upscale in ffmpeg beyond the native crop – the warp does the rest
    if pw > cw:
        pw, ph = cw, chh
    vf = (f"crop={cw}:{chh}:{x}:{y},"
          f"scale={pw}:{ph}:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709,"
          f"format=rgb24")
    n = hi - lo + 1
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0, (lo - 0.5) / fps):.6f}", "-i", str(path),
           "-frames:v", str(n), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.check_output(cmd)
    frames = np.frombuffer(raw, np.uint8).reshape(-1, ph, pw, 3)
    shot.frames = frames
    shot.first = lo
    return shot


# ---------------------------------------------------------------------------
# temporal sampling: optical-flow in-betweens for slow motion,
# shutter-style frame accumulation for speed-ups
# ---------------------------------------------------------------------------
_dis = None


def _flow(a, b):
    global _dis
    if _dis is None:
        _dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    s = 0.5
    ga = cv2.cvtColor(cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    f = _dis.calc(ga, gb, None)
    f = cv2.resize(f, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR) / s
    return f


@lru_cache(maxsize=64)
def _grid(h, w):
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return gx, gy


_flow_cache: dict = {}


def flow_interp(shot: Shot, i: int, a: float):
    A = shot.frames[i]
    B = shot.frames[min(i + 1, len(shot.frames) - 1)]
    key = (id(shot), i)
    if key not in _flow_cache:
        _flow_cache.clear() if len(_flow_cache) > 6 else None
        _flow_cache[key] = (_flow(A, B), _flow(B, A))
    fab, fba = _flow_cache[key]
    gx, gy = _grid(A.shape[0], A.shape[1])
    ia = cv2.remap(A, gx - a * fab[..., 0], gy - a * fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    ib = cv2.remap(B, gx - (1 - a) * fba[..., 0], gy - (1 - a) * fba[..., 1], cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(ia, 1 - a, ib, a, 0)


def sample_source(shot: Shot, t: float):
    """Return the source image (uint8, prescaled crop) for timeline time t."""
    fi = shot.src_time(t) * shot.fps - shot.first
    n = len(shot.frames)
    speed = abs(shot.speed(t))
    # source frames covered by a 180° shutter at the output frame rate
    span = speed * shot.fps / FPS * 0.5
    if span > 0.9:
        k = int(min(6, math.ceil(span * 1.5)))
        idx = np.clip(np.round(np.linspace(fi - span / 2, fi + span / 2, k)).astype(int), 0, n - 1)
        acc = np.zeros(shot.frames[0].shape, np.float32)
        for j in idx:
            acc += shot.frames[j]
        return (acc / len(idx)).astype(np.uint8)
    i = int(math.floor(fi))
    a = fi - i
    i = int(clamp(i, 0, n - 1))
    if a < 0.08 or i >= n - 1:
        return shot.frames[i]
    if a > 0.92:
        return shot.frames[min(i + 1, n - 1)]
    if speed < 0.85:
        return flow_interp(shot, i, a)
    return shot.frames[int(round(fi)) if round(fi) < n else n - 1]


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def place(img: np.ndarray, zoom: float, focus, shake=(0.0, 0.0), rot=0.0, pan=(0.0, 0.0)):
    ph, pw = img.shape[:2]
    p = ph / H  # prescale factor (height is always the 9:16 reference)
    z = zoom
    # keep the view inside the crop
    hx, hy = (W / 2) * p / z, (H / 2) * p / z
    fx = clamp(focus[0] * pw, hx, pw - hx) if hx < pw / 2 else pw / 2
    fy = clamp(focus[1] * ph, hy, ph - hy) if hy < ph / 2 else ph / 2
    s = z / p
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    ox, oy = W / 2 + shake[0] + pan[0], H / 2 + shake[1] + pan[1]
    M = np.array([[s * c, -s * si, ox - s * (c * fx - si * fy)],
                  [s * si, s * c, oy - s * (si * fx + c * fy)]], np.float32)
    interp = cv2.INTER_CUBIC if s > 0.95 else cv2.INTER_LINEAR
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=cv2.BORDER_REFLECT101)


# ---------------------------------------------------------------------------
# colour
# ---------------------------------------------------------------------------
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def _scurve(x, amount):
    sm = x * x * (3 - 2 * x)
    return x + amount * (sm - x)


def grade(img: np.ndarray, look: str, k: float = 1.0) -> np.ndarray:
    """img float32 0..1 RGB → graded float32."""
    x = img
    if look in ("fight", "ko", "outro", "freeze"):
        x = np.clip((x - 0.025) / 0.975, 0, 1)            # set black point
        x = _scurve(x, 0.55)                               # filmic contrast
        l = (x @ LUMA)[..., None]
        sh = (1 - l) ** 2
        hi = l ** 2
        x = x + sh * np.array([-0.020, 0.012, 0.030], np.float32)   # teal shadows
        x = x + hi * np.array([0.045, 0.012, -0.030], np.float32)    # warm highlights
        sat = {"fight": 1.12, "ko": 1.22, "outro": 1.08, "freeze": 0.35}[look]
        l = (x @ LUMA)[..., None]
        x = l + (x - l) * sat
        if look == "freeze":
            x = x * np.array([0.92, 0.98, 1.06], np.float32)
    elif look == "memory":
        l = (x @ LUMA)[..., None]
        l = np.clip((l - 0.03) / 0.78, 0, 1)
        l = _scurve(l, 0.85)
        x = np.repeat(l, 3, axis=2) * np.array([1.02, 1.0, 0.96], np.float32)  # faint warm silver
    return np.clip(x, 0, 1)


def bloom(x: np.ndarray, strength=0.22, threshold=0.72, tint=(1.0, 0.82, 0.70)):
    small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    l = small @ LUMA
    m = np.clip((l - threshold) / (1 - threshold), 0, 1)[..., None]
    glow = small * m
    glow = cv2.GaussianBlur(glow, (0, 0), 9) * 0.6 + cv2.GaussianBlur(glow, (0, 0), 28) * 0.4
    glow = cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR) * np.array(tint, np.float32)
    return 1 - (1 - x) * (1 - glow * strength)  # screen


@lru_cache(maxsize=4)
def vignette_mask(strength: float):
    gx, gy = np.meshgrid(np.linspace(-1, 1, W, dtype=np.float32), np.linspace(-1, 1, H, dtype=np.float32))
    r = np.sqrt((gx * 0.95) ** 2 + (gy * 0.62) ** 2)
    return (1 - strength * np.clip(r - 0.35, 0, None) ** 1.6)[..., None].astype(np.float32)


def chroma_split(x: np.ndarray, amt: float):
    if amt <= 0.0005:
        return x
    out = x.copy()
    for ch, s in ((0, 1 + amt), (2, 1 - amt)):
        M = np.array([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]], np.float32)
        out[..., ch] = cv2.warpAffine(x[..., ch], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out


class Grain:
    def __init__(self, n=10, seed=7):
        rng = np.random.default_rng(seed)
        self.tex = []
        for _ in range(n):
            g = rng.normal(0, 1, (H, W)).astype(np.float32)
            g = cv2.GaussianBlur(g, (0, 0), 0.65)
            self.tex.append(g / (g.std() + 1e-6))
        self.rng = np.random.default_rng(seed + 1)

    def apply(self, x, amount, frame):
        g = self.tex[(frame * 7) % len(self.tex)][..., None]
        l = (x @ LUMA)[..., None]
        w = 4 * l * (1 - l) + 0.15          # strongest in the mid-tones, like film
        return np.clip(x + g * amount * w, 0, 1)


# ---------------------------------------------------------------------------
# typography
# ---------------------------------------------------------------------------
FONTS = {
    "anton": ASSETS / "fonts" / "Anton-Regular.ttf",
    "barlow": ASSETS / "fonts" / "BarlowCondensed-ExtraBold.ttf",
    "barlow_black": ASSETS / "fonts" / "BarlowCondensed-Black.ttf",
    "barlow_semi": ASSETS / "fonts" / "BarlowCondensed-SemiBold.ttf",
}
WHITE = (255, 255, 255)
RED = (255, 44, 44)


@lru_cache(maxsize=256)
def render_line(text: str, font: str, size: int, color=WHITE, accent=RED, tracking=0.0,
                shadow=True, stroke=0):
    """Render one line to a premultiplied RGBA float array. {braces} are drawn
    in the accent colour, [brackets] in white on an accent-coloured box."""
    f = ImageFont.truetype(str(FONTS[font]), size)
    parts = []  # (text, style) with style "" | "accent" | "box"
    buf, style = "", ""
    for ch in text:
        if ch in "{}[]":
            if buf:
                parts.append((buf, style))
            buf, style = "", {"{": "accent", "[": "box"}.get(ch, "")
        else:
            buf += ch
    if buf:
        parts.append((buf, style))
    # measure with tracking
    track = tracking * size
    glyphs = []
    x = 0.0
    for seg, a in parts:
        for c in seg:
            adv = f.getlength(c)
            glyphs.append((c, x, a))
            x += adv + track
    width = int(math.ceil(x - track + size * 0.16)) + 2 * stroke + 40
    asc, desc = f.getmetrics()
    height = asc + desc + 2 * stroke + 40
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # red boxes behind [boxed] runs
    cap_top, cap_bot = f.getbbox("H")[1], f.getbbox("H")[3]
    runs, cur = [], None
    for c, gx, a in glyphs:
        if a == "box":
            if cur is None:
                cur = [gx, gx + f.getlength(c)]
            else:
                cur[1] = gx + f.getlength(c)
        elif cur is not None:
            runs.append(cur)
            cur = None
    if cur is not None:
        runs.append(cur)
    px, py = size * 0.07, size * 0.07
    for x0, x1 in runs:
        d.rounded_rectangle([20 + x0 - px, 20 + cap_top - py, 20 + x1 + px, 20 + cap_bot + py],
                            radius=int(size * 0.06), fill=(*accent, 255))
    for c, gx, a in glyphs:
        fill = accent if a == "accent" else color
        d.text((20 + stroke + gx, 20 + stroke), c, font=f, fill=(*fill, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 255) if stroke else None)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        alpha = img.split()[3].filter(ImageFilter.GaussianBlur(size * 0.10))
        sh.putalpha(alpha.point(lambda v: int(v * 0.55)))
        base = Image.new("RGBA", (width, height + int(size * 0.06)), (0, 0, 0, 0))
        base.alpha_composite(sh, (0, int(size * 0.05)))
        base.alpha_composite(img, (0, 0))
        img = base
    arr = np.asarray(img).astype(np.float32) / 255.0
    arr[..., :3] *= arr[..., 3:4]
    return arr


def composite(dst: np.ndarray, layer: np.ndarray, cx: float, cy: float, scale=1.0, opacity=1.0,
              blur_y=0.0):
    """Alpha-over a premultiplied RGBA layer centred at (cx, cy)."""
    if opacity <= 0.003:
        return dst
    lay = layer
    if abs(scale - 1) > 1e-3:
        lay = cv2.resize(layer, None, fx=scale, fy=scale,
                         interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    if blur_y > 0.5:
        k = int(blur_y) * 2 + 1
        lay = cv2.blur(lay, (1, k))
    lh, lw = lay.shape[:2]
    x0, y0 = int(round(cx - lw / 2)), int(round(cy - lh / 2))
    x1, y1 = x0 + lw, y0 + lh
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x1), min(H, y1)
    if dx1 <= dx0 or dy1 <= dy0:
        return dst
    part = lay[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)] * opacity
    region = dst[dy0:dy1, dx0:dx1]
    region[:] = part[..., :3] + region * (1 - part[..., 3:4])
    return dst


@lru_cache(maxsize=64)
def pill(w: int, h: int, color=(10, 12, 16), alpha=0.62, radius=None):
    radius = radius or h // 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                                          fill=(*color, int(255 * alpha)))
    arr = np.asarray(img).astype(np.float32) / 255.0
    arr[..., :3] *= arr[..., 3:4]
    return arr


# ---------------------------------------------------------------------------
# encoder
# ---------------------------------------------------------------------------
def open_encoder(path: Path, crf=16):
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", str(crf),
           "-maxrate", "15M", "-bufsize", "30M", "-profile:v", "high", "-level", "4.2",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv", "-g", str(FPS * 2), "-movflags", "+faststart", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
