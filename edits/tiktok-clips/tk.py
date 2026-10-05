"""TikTok clip toolkit: 9:16 layout, text overlays, self-made (royalty-free) audio, encoding.

Layout (1080x1920) with TikTok's UI in mind:
  y 0–150      status bar / "Following | For You"      -> nothing important
  y 160–390    TITLE area (hook text)
  y 400–1660   main video window (1080x1260, 6:7) over a blurred, darkened full-bleed copy
  y ≥ 1560     caption / username / music ticker          -> labels stay above 1540
  x ≥ 950      like/comment/share column (y 700–1500)     -> text max width 840, centred
"""
import math, os, subprocess, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
WIN_Y, WIN_W, WIN_H = 400, 1080, 1260
FONT = os.environ.get("CLIPS_FONT", os.path.join(os.environ.get("CLIPS_MEDIA", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "media")), "Montserrat-BlackItalic.ttf"))
YELLOW = (255, 214, 0)
WHITE = (255, 255, 255)


# ----------------------------------------------------------------------------- video in
def read_clip(path, t0, t1, n, pre="scale=1920:1080:flags=lanczos,setsar=1", interp=False, sw=1920, sh=1080):
    """Decode src[t0:t1] retimed to exactly n output frames (slow-mo when t1-t0 < n/FPS)."""
    speed = (t1 - t0) / (n / FPS)
    vf = [pre, f"setpts=(PTS-STARTPTS)/{speed:.6f}"]
    vf.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
              if interp and speed < 0.95 else f"fps={FPS}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{(t1 - t0) + 0.6:.3f}",
           "-i", path, "-an", "-vf", ",".join(vf), "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    got = len(raw) // (sw * sh * 3)
    if got == 0:
        raise RuntimeError(f"no frames: {path} {t0}-{t1}")
    fr = list(np.frombuffer(raw[: got * sw * sh * 3], np.uint8).reshape(got, sh, sw, 3))
    while len(fr) < n:
        fr.append(fr[-1])
    return fr[:n]


def warp_crop(img, rect, out_w, out_h, zoom=1.0):
    """Sub-pixel crop of rect=(x, y, w, h) (zoomed around its centre) scaled to out_w x out_h."""
    x, y, w, h = rect
    cx, cy = x + w / 2, y + h / 2
    w2, h2 = w / zoom, h / zoom
    sx, sy = out_w / w2, out_h / h2
    M = np.float32([[sx, 0, -(cx - w2 / 2) * sx], [0, sy, -(cy - h2 / 2) * sy]])
    return cv2.warpAffine(img, M, (out_w, out_h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)


def compose(src, rect, zoom=1.0, blur_main=0.0, dark_main=0.0, bg_dark=0.55, shake=(0, 0)):
    """Full 9:16 frame: blurred full-bleed background + 6:7 main window at WIN_Y."""
    sh, sw = src.shape[:2]
    bw = sh * W / H
    bg = warp_crop(src, ((sw - bw) / 2, 0, bw, sh), W // 4, H // 4)
    bg = cv2.GaussianBlur(bg, (0, 0), 9)
    bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_LINEAR)
    out = (bg.astype(np.float32) * (1 - bg_dark)).astype(np.uint8)
    win = warp_crop(src, rect, WIN_W, WIN_H, zoom)
    if blur_main > 0.5:
        win = cv2.GaussianBlur(win, (0, 0), blur_main)
    if dark_main > 0:
        win = (win.astype(np.float32) * (1 - dark_main)).astype(np.uint8)
    dx, dy = shake
    y0 = WIN_Y + int(dy)
    out[max(0, y0):y0 + WIN_H] = win[max(0, -y0):H - y0] if dx == 0 else np.roll(win, int(dx), axis=1)[max(0, -y0):H - y0]
    return out


def grade(img, contrast=1.07, sat=1.15):
    f = img.astype(np.float32) / 255.0
    f = (f - 0.5) * contrast + 0.5
    hsv = cv2.cvtColor(np.clip(f, 0, 1), cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * sat, 0, 1)
    return (cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) * 255).astype(np.uint8)


# ----------------------------------------------------------------------------- text
_font_cache = {}


def font(size):
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FONT, size)
    return _font_cache[size]


def text_sprite(lines, size=84, fill=WHITE, stroke=8, box=None, max_w=840, line_gap=0.12, pad=28):
    """RGBA sprite of centred multi-line text. box=(r,g,b) draws a solid highlight box behind it."""
    if isinstance(lines, str):
        lines = [lines]
    while True:
        f = font(size)
        bbs = [f.getbbox(l, stroke_width=stroke) for l in lines]
        widths = [b[2] - b[0] for b in bbs]
        if max(widths) <= max_w - (2 * pad if box else 0) or size <= 30:
            break
        size -= 3
    lh = int(size * (1 + line_gap))
    tw = max(widths) + 2 * pad
    th = lh * len(lines) + 2 * pad
    im = Image.new("RGBA", (tw + 24, th + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle([12, 12, 12 + tw, 12 + th], radius=18, fill=box + (255,))
    for i, l in enumerate(lines):
        b = bbs[i]
        x = 12 + (tw - (b[2] - b[0])) / 2 - b[0]
        y = 12 + pad + i * lh - f.getbbox("Ag")[1] * 0.2
        if box:
            d.text((x, y), l, font=f, fill=fill)
        else:
            d.text((x, y), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    arr = np.array(im)
    if not box:   # soft drop shadow
        sh = np.zeros_like(arr)
        sh[..., 3] = cv2.GaussianBlur(arr[..., 3], (0, 0), 7)
        sh = np.roll(np.roll(sh, 6, 0), 5, 1)
        a = arr[..., 3:4].astype(np.float32) / 255
        out = sh.astype(np.float32)
        out[..., 3] = out[..., 3] * 0.6
        out[..., :3] = arr[..., :3] * a + out[..., :3] * (1 - a)
        out[..., 3] = np.maximum(out[..., 3], arr[..., 3])
        arr = out.astype(np.uint8)
    return arr


def paste(img, sprite, cx, cy, scale=1.0, alpha=1.0):
    sp = sprite
    if abs(scale - 1) > 1e-3:
        sp = cv2.resize(sp, (max(1, int(sp.shape[1] * scale)), max(1, int(sp.shape[0] * scale))),
                        interpolation=cv2.INTER_LINEAR)
    h, w = sp.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return img
    part = sp[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = part[..., 3:4] / 255.0 * alpha
    roi = img[ya:yb, xa:xb].astype(np.float32)
    img[ya:yb, xa:xb] = (roi * (1 - a) + part[..., 2::-1] * a).astype(np.uint8)
    return img


def pop(age_frames, dur=5, amount=0.18):
    """scale for a pop-in: starts big, settles to 1.0"""
    if age_frames < 0:
        return 0.0
    return 1.0 + amount * math.exp(-age_frames / (dur / 2.2))


def flash(img, a):
    if a <= 0.01:
        return img
    return cv2.addWeighted(img, 1 - a, np.full_like(img, 255), a, 0)


def progress_bar(img, frac, y=WIN_Y - 10, h=10, color=YELLOW):
    cv2.rectangle(img, (0, y), (W, y + h), (40, 40, 40), -1)
    cv2.rectangle(img, (0, y), (int(W * max(0, min(1, frac))), y + h), color[::-1], -1)
    return img


# ----------------------------------------------------------------------------- audio
def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(d, a=0.003, decay=0.2):
    t = _t(d)
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / decay)


def _noise(d, seed=0):
    return np.random.default_rng(seed).normal(0, 1, int(d * SR))


def _band(x, lo, hi):
    from scipy.signal import butter, sosfilt
    sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x)


def _hp(x, f):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)


def kick(g=1.0):
    t = _t(0.45)
    f = 45 + 95 * np.exp(-t / 0.045)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return g * (np.sin(ph) * np.exp(-t / 0.16) + 0.25 * _hp(_noise(0.45, 1), 2000) * np.exp(-t / 0.004))


def clap(g=0.6):
    d = 0.22
    x = _band(_noise(d, 2), 900, 3500)
    e = np.exp(-_t(d) / 0.06)
    for k in (0.0, 0.011, 0.022):
        e += 0.6 * (np.abs(_t(d) - k) < 0.004)
    return g * x * e / 2


def hat(g=0.25, d=0.045):
    return g * _hp(_noise(d, 3), 7000) * np.exp(-_t(d) / 0.012)


def bass(freq=55, d=0.4, g=0.55):
    t = _t(d)
    return g * np.tanh(1.5 * np.sin(2 * np.pi * freq * t)) * np.minimum(1, t / 0.005) * np.exp(-t / 0.25)


def tick(g=0.55):
    t = _t(0.06)
    return g * (np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.008) + 0.4 * _hp(_noise(0.06, 4), 3000) * np.exp(-t / 0.003))


def ding(g=0.5, f0=1318.5):
    t = _t(1.4)
    x = sum(a * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t / (0.9 / k)) for k, a in ((1, 1), (2, 0.45), (3, 0.25), (4.2, 0.12)))
    return g * x * np.minimum(1, t / 0.002)


def whoosh(d=0.45, g=0.5, up=True):
    t = _t(d)
    x = _noise(d, 5)
    from scipy.signal import butter, sosfilt
    out = np.zeros_like(x)
    n = 12
    for i in range(n):
        s, e = i * len(x) // n, (i + 1) * len(x) // n
        fc = (400 * (12 ** (i / n))) if up else (5000 / (12 ** (i / n)))
        sos = butter(2, [fc * 0.7, min(fc * 1.6, 18000)], btype="band", fs=SR, output="sos")
        out[s:e] = sosfilt(sos, x[s:e])
    return g * out * np.sin(np.pi * t / d) ** 2


def impact(g=1.0):
    t = _t(1.3)
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t / 0.08)) * t) * np.exp(-t / 0.45)
    crack = _band(_noise(1.3, 6), 200, 6000) * np.exp(-t / 0.05)
    return g * (boom + 0.5 * crack)


def riser(d=1.5, g=0.35):
    t = _t(d)
    f = 200 * (8 ** (t / d))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    nz = _hp(_noise(d, 7), 1500)
    return g * (0.5 * tone + 0.5 * nz) * (t / d) ** 2


def heartbeat(g=0.8):
    return g * (kick(0.9)[: int(0.25 * SR)] * 0.8)


class Mix:
    def __init__(self, dur):
        self.buf = np.zeros(int(dur * SR) + SR)
        self.dur = dur

    def add(self, x, t, g=1.0):
        i = int(round(t * SR))
        if i >= len(self.buf):
            return
        j = min(len(self.buf), i + len(x))
        self.buf[i:j] += g * x[: j - i]

    def beat(self, t0, t1, bpm, pattern="hiphop", g=1.0, bass_notes=(55, 55, 65.4, 49)):
        b = 60 / bpm
        n = 0
        t = t0
        while t < t1 - 1e-6:
            pos = n % 8                     # 8 eighth-notes per bar
            bar = (n // 8) % len(bass_notes)
            if pattern == "hiphop":
                if pos in (0, 5):
                    self.add(kick(), t, g)
                if pos in (2, 6):
                    self.add(clap(), t, g)
                self.add(hat(0.18 if pos % 2 else 0.26), t, g)
                if pos == 0:
                    self.add(bass(bass_notes[bar], d=b * 3.5), t, g)
            elif pattern == "trap":
                if pos in (0, 3, 6) or (pos == 7 and bar % 2):
                    self.add(kick(), t, g)
                if pos in (4,):
                    self.add(clap(0.7), t, g)
                self.add(hat(0.2), t, g)
                self.add(hat(0.12), t + b / 4, g)
                if pos in (0, 3):
                    self.add(bass(bass_notes[bar], d=b * 2.5, g=0.6), t, g)
            n += 1
            t = t0 + n * b / 2

    def write(self, path):
        x = self.buf[: int(self.dur * SR)]
        x = np.tanh(x * 0.9) / 0.9 if np.abs(x).max() > 0.9 else x
        st = np.stack([x, x], 1)
        import wave
        pcm = (np.clip(st / max(1.0, np.abs(st).max() * 1.05), -1, 1) * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def loudnorm(path_in, target=-14.0, tp=-1.0):
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", path_in, "-af",
                            f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    return (f"loudnorm=I={target}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}")


def encoder(out, audio_wav, dur, crf=19):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    return subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", audio_wav, "-filter_complex",
        f"[0:v]format=yuv420p[v];[1:a]{loudnorm(audio_wav)},aresample={SR},atrim=0:{dur:.3f}[a]",
        "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-profile:v", "high", "-level", "4.2",
        "-g", "30", "-bf", "2", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
        "-movflags", "+faststart", out], stdin=subprocess.PIPE)
