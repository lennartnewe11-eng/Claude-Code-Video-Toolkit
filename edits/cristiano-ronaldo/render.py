#!/usr/bin/env python3
"""Cristiano Ronaldo – vertical (9:16) TikTok edit, built for watch time.

Structure (20.6 s, loops seamlessly):
  0.0 s  hook   – 21-year-old Ronaldo (WM 2006) + on-screen lyric, no drums yet
  2.7 s  DROP   – bicycle kick vs Juventus: contact exactly on the 808
  ~8 s   haters – "calma" at Camp Nou on "Hater am Platzen vor Neid"
  ~11 s  heart  – "Ich erfülle Mamas Wunschzettel": Dolores in tears, Ballon d'Or tears
  ~14 s  break  – drums drop out, SIU run + jump in slow-mo …
  15.6 s DROP 2 – … SIU landing on the bass return
  ~17 s  outro  – screams, trophies, smile → loops back to young Ronaldo smiling
"""
import subprocess, sys, math, os, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CR7_MEDIA", os.path.join(HERE, "media"))
SONG = f"{ROOT}/audio/song.wav"
FONT = os.environ.get("CR7_FONT", os.path.join(ROOT, "fonts", "Montserrat-BlackItalic.ttf"))
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else f"{ROOT}/out/cr7_edit.mp4"
PREVIEW = "--preview" in sys.argv

OW, OH, FPS = 1080, 1920, 30          # output: 9:16
SW, SH = 1920, 1080                   # every source is normalised to 1920x1080 first

# 135 BPM, grid snapped to the kick drum; k=1 is the drop after the a-cappella intro
BEAT = 0.44440
def B(k):
    return 32.030 + BEAT * k

T0, T_END = B(-5), 50.400             # "Viele, die mir heut…" -> "…in mein Kreis rein"

# EDL: (beat_in, beat_out, src, src_in, src_out, crop, extras)
#   crop = dict(cx=[(src_t, x), …] or x, cy=y, h=crop height) in 1920x1080 coords; width = h*9/16
EDL = [
    # HOOK (a-cappella) – young Ronaldo, Man Utd 2003
    (-5, -3, "young",   53.10, 53.99, dict(cx=[(53.1, 1030), (53.99, 1080)], cy=565, h=880), {"pushin": 0.06}),   # WM 2006, the look
    (-3, -1, "young",   11.20, 12.09, dict(cx=1300, cy=600, h=960), {}),                                        # WM 2006, the scream
    # bicycle kick: rise in slow-mo, contact ON the drop
    (-1,  1, "bicycle", 74.44, 74.88, dict(cx=[(74.44, 1040), (74.88, 1160)], cy=520, h=1080), {"interp": True}),
    ( 1,  3, "bicycle", 74.88, 75.40, dict(cx=[(74.88, 1160), (75.40, 1190)], cy=540, h=1080), {"interp": True}),
    ( 3,  5, "bicycle", 63.17, 64.06, dict(cx=[(63.17, 1500), (63.45, 1420), (63.70, 1270), (64.06, 1220)], cy=470, h=960), {}),
    ( 5,  7, "bicycle", 24.85, 25.74, dict(cx=[(24.85, 820), (25.15, 860), (25.45, 660), (25.74, 720)], cy=560, h=1080), {}),
    ( 7,  9, "bicycle", 84.15, 85.04, dict(cx=[(84.15, 1130), (85.04, 1060)], cy=540, h=1080), {}),         # Zidane
    ( 9, 11, "bicycle", 87.05, 87.94, dict(cx=[(87.05, 1090), (87.94, 1160)], cy=540, h=1080), {}),         # hand on heart
    # "Ich lass heute meine Kunst sprechen, kleine Hater am Platzen vor Neid"
    (11, 13, "iconic",  30.55, 31.44, dict(cx=[(30.55, 780), (31.05, 760), (31.44, 770)], cy=540, h=1080), {}),  # beard (vs Spain)
    (13, 14, "portugal", 25.30, 25.74, dict(cx=840, cy=540, h=1080), {}),                                 # the stare
    (14, 17, "calma",   16.55, 17.88, dict(cx=[(16.55, 1000), (17.30, 820), (17.88, 900)], cy=560, h=1080), {}),
    # "Ich erfülle Mamas Wunschzettel, bevor Mama geht mit der Zeit"
    (17, 19, "mom",     13.20, 14.09, dict(cx=[(13.2, 640), (14.09, 960)], cy=600, h=960), {}),             # points to the stands
    (19, 21, "mom",     15.55, 16.44, dict(cx=880, cy=600, h=960), {"pushin": 0.05}),                       # Dolores in tears
    (21, 23, "mom2013", 199.95, 200.84, dict(cx=850, cy=560, h=1000), {"pushin": 0.05}),                    # Ballon d'Or 2013
    (23, 25, "mom",     35.40, 36.29, dict(cx=720, cy=480, h=960), {"pushin": 0.05}),
    # break: drums out -> SIU run + jump (slow-mo) -> landing on the bass return
    (25, 27, "siu",     72.40, 73.29, dict(cx=1060, cy=540, h=1080), {}),
    (27, 30, "siu",     73.85, 74.97, dict(cx=[(73.85, 1080), (74.25, 1020), (74.65, 970), (74.85, 870), (74.97, 830)], cy=540, h=1080), {"pushin": 0.06}),
    (30, 32, "siu",     20.00, 20.89, dict(cx=[(20.0, 720), (20.6, 960), (20.89, 960)], cy=560, h=1080), {}),
    # "…begrüßt uns mit Gangzeit – lass kein Pisser in mein Kreis rein"
    (32, 34, "siu",     44.72, 45.61, dict(cx=[(44.72, 940), (45.1, 800), (45.5, 1000), (45.61, 1000)], cy=500, h=1080), {}),
    (34, 36, "portugal", 39.15, 40.04, dict(cx=900, cy=540, h=1080), {}),
    (36, 37, "siu",     10.29, 10.57, dict(cx=880, cy=540, h=1080), {"interp": True}),
    (37, 38, "siu",     13.00, 13.44, dict(cx=960, cy=540, h=1080), {}),
    (38, None, "bicycle", 99.70, 100.45, dict(cx=[(99.7, 1180), (100.45, 1120)], cy=450, h=900), {"interp": True, "pushin": 0.05}),
]

CAPTIONS = [  # (t_in, t_out, text) in song time
    (T0,     30.52, "VIELE, DIE MIR HEUT"),
    (30.52,  31.18, "DIE HAND SCHÜTTELN,"),
    (40.38,  40.86, "ICH ERFÜLLE"),
    (40.86,  41.76, "MAMAS WUNSCHZETTEL,"),
    (41.76,  42.56, "BEVOR MAMA GEHT"),
    (42.56,  43.45, "MIT DER ZEIT"),
]

KICKS = [1, 4, 6, 9, 12, 14, 17, 20, 22, 25, 30, 33, 36, 38, 41]
DROPS = {1: dict(flash=0.85, shake=22, punch=0.12), 30: dict(flash=0.9, shake=26, punch=0.12)}


def fidx(t):
    return int(round((t - T0) * FPS))


def seg_times(seg):
    s0 = B(seg[0])
    s1 = B(seg[1]) if seg[1] is not None else T_END
    return s0, s1


def interp_kf(kf, t):
    if not isinstance(kf, list):
        return float(kf)
    ts = [p[0] for p in kf]
    xs = [p[1] for p in kf]
    return float(np.interp(t, ts, xs))


def decode(src, a, b, n, speed, interp):
    vf = [f"scale={SW}:{SH}:flags=lanczos,setsar=1", f"setpts=(PTS-STARTPTS)/{speed:.6f}"]
    if interp and speed < 0.95:
        vf.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    else:
        vf.append(f"fps={FPS}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{(b - a) + 0.5:.3f}",
           "-i", f"{ROOT}/src/{src}.mp4", "-an", "-vf", ",".join(vf), "-frames:v", str(n),
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    got = len(raw) // (SW * SH * 3)
    if got == 0:
        raise RuntimeError(f"no frames for {src} {a}-{b}")
    frames = list(np.frombuffer(raw[: got * SW * SH * 3], np.uint8).reshape(got, SH, SW, 3))
    while len(frames) < n:
        frames.append(frames[-1])
    return frames[:n]


def crop_vertical(img, crop, t_src, push):
    h = crop.get("h", SH) / push
    w = h * 9 / 16
    cx = interp_kf(crop.get("cx", SW / 2), t_src)
    cy = crop.get("cy", SH / 2)
    x0 = min(max(cx - w / 2, 0), SW - w)
    y0 = min(max(cy - h / 2, 0), SH - h)
    # sub-pixel crop + resize in one affine warp (smooth pans, no jitter)
    sx, sy = OW / w, OH / h
    M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)


def env(f, events, tau):
    v = 0.0
    for fe, amp in events:
        if f >= fe:
            v += amp * math.exp(-(f - fe) / tau)
    return v


def zoom_shift(img, z, dx, dy):
    if z <= 1.0001 and abs(dx) < 0.5 and abs(dy) < 0.5:
        return img
    M = np.float32([[z, 0, (1 - z) * OW / 2 + dx], [0, z, (1 - z) * OH / 2 + dy]])
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def caption_sprite(text, size=86):
    font = ImageFont.truetype(FONT, size)
    pad = 40
    bbox = font.getbbox(text, stroke_width=9)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    while tw > OW - 140:                      # keep inside TikTok's safe width
        size -= 4
        font = ImageFont.truetype(FONT, size)
        bbox = font.getbbox(text, stroke_width=9)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    im = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # soft drop shadow
    d.text((pad - bbox[0] + 6, pad - bbox[1] + 8), text, font=font, fill=(0, 0, 0, 150),
           stroke_width=9, stroke_fill=(0, 0, 0, 150))
    im = Image.fromarray(cv2.GaussianBlur(np.array(im), (0, 0), 6))
    d = ImageDraw.Draw(im)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=(255, 255, 255, 255),
           stroke_width=9, stroke_fill=(0, 0, 0, 255))
    return np.array(im)  # RGBA


def overlay(img, sprite_rgba, cx, cy, scale):
    sp = sprite_rgba
    if abs(scale - 1) > 1e-3:
        sp = cv2.resize(sp, (int(sp.shape[1] * scale), int(sp.shape[0] * scale)), interpolation=cv2.INTER_LINEAR)
    h, w = sp.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, OW), min(y0 + h, OH)
    if xa >= xb or ya >= yb:
        return img
    part = sp[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = part[..., 3:4] / 255.0
    bgr = part[..., [2, 1, 0]]
    roi = img[ya:yb, xa:xb].astype(np.float32)
    img[ya:yb, xa:xb] = (roi * (1 - a) + bgr * a).astype(np.uint8)
    return img


def loudnorm_filter(dur, target=-14.0, tp=-1.0):
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{T0:.3f}", "-t", f"{dur:.3f}", "-i", SONG,
                            "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    return (f"loudnorm=I={target}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}")


def main():
    n_total = fidx(T_END)
    rng = np.random.default_rng(7)
    cut_beats = sorted({s[0] for s in EDL} - set(DROPS) - {-5, -3, -1})
    punch = [(fidx(B(k)), d["punch"]) for k, d in DROPS.items()] + \
            [(fidx(B(k)), 0.045) for k in cut_beats] + \
            [(fidx(B(k)), 0.025) for k in KICKS if k not in DROPS and k not in cut_beats]
    flash_ev = [(fidx(B(k)), d["flash"]) for k, d in DROPS.items()]
    shake_ev = [(fidx(B(k)), d["shake"]) for k, d in DROPS.items()]
    rgb_ev = [(fidx(B(k)), 14) for k in DROPS] + [(fidx(B(k)), 6) for k in cut_beats]
    sprites = [(fidx(a), fidx(b), caption_sprite(txt)) for a, b, txt in CAPTIONS]

    enc = None
    if not PREVIEW:
        os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
        dur = n_total / FPS
        enc = subprocess.Popen([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
            "-ss", f"{T0:.3f}", "-t", f"{dur:.3f}", "-i", SONG,
            "-filter_complex",
            "[0:v]eq=contrast=1.08:saturation=1.15:gamma=0.98,unsharp=5:5:0.7:5:5:0.0,"
            "vignette=angle=PI/5,format=yuv420p[v];"
            f"[1:a]{loudnorm_filter(dur)},aresample=44100,"
            f"afade=t=in:st=0:d=0.01,afade=t=out:st={dur - 0.03:.3f}:d=0.03[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-level", "4.2",
            "-g", "30", "-bf", "2", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "320k", "-ar", "44100",
            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    else:
        os.makedirs(f"{ROOT}/out", exist_ok=True)

    f_global = 0
    for i, seg in enumerate(EDL):
        k0, k1, src, a, b, crop, ex = seg
        s0, s1 = seg_times(seg)
        n = fidx(s1) - fidx(s0)
        speed = (b - a) / (s1 - s0)
        frames = decode(src, a, b, n, speed, ex.get("interp", False))
        print((i, k0, k1, round(s0, 3), src, a, b, round(speed, 3), n), flush=True)
        for k, fr in enumerate(frames):
            f = f_global + k
            t_src = a + (k / FPS) * speed
            push = 1.0 + ex.get("pushin", 0.0) * (k / max(1, n - 1))
            img = crop_vertical(fr, crop, t_src, push)
            z = 1.0 + env(f, punch, 3.0)
            sh = env(f, shake_ev, 4.0)
            dx = dy = 0.0
            if sh > 0.8:
                dx, dy = rng.uniform(-sh, sh), rng.uniform(-sh, sh)
                z += sh / 900.0
            img = zoom_shift(img, z, dx, dy)
            c = env(f, rgb_ev, 2.5)
            if c > 0.8:
                s = int(round(c))
                b_, g_, r_ = cv2.split(img)
                img = cv2.merge([np.roll(b_, -s, axis=1), g_, np.roll(r_, s, axis=1)])
            fl = min(1.0, env(f, flash_ev, 2.2))
            if fl > 0.01:
                img = cv2.addWeighted(img, 1 - fl, np.full_like(img, 255), fl, 0)
            for fa, fb, spr in sprites:
                if fa <= f < fb:
                    age = f - fa
                    scale = 1.0 + 0.12 * math.exp(-age / 1.6)   # pop-in
                    img = overlay(img.copy(), spr, OW / 2, OH * 0.60, scale)
            if PREVIEW:
                if k in (0, n // 2, n - 1):
                    cv2.imwrite(f"{ROOT}/out/prev_{i:02d}_{k:03d}.jpg", cv2.resize(img, (216, 384)))
            else:
                enc.stdin.write(img.tobytes())
        f_global += n
    if enc:
        enc.stdin.close()
        enc.wait()
    print("total frames", f_global, "expected", n_total, "duration", round(f_global / FPS, 3))


if __name__ == "__main__":
    main()
