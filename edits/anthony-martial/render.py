#!/usr/bin/env python3
"""Anthony Martial (Man Utd) – 16:9 TikTok edit, 14.2 s seamless loop.

Song window: the second pass of the song's opening hook ("Bin auf Cartier, nicht auf Ray-Ban …"),
from the downbeat after the first kick roll (14.70 s) to the downbeat after the second kick roll
(28.92 s). Same lyric, same roll on both ends, so the loop is musically invisible.

  bar 1  debut vs Liverpool 2015 – run, strike on the kick, ball in, celebration   (+ hook caption)
  bar 2  Stoke 2016 – solo, strike on the kick, ball in, arms-wide celebration
  bar 3  drums drop out ("Ich bin Selfmade, 100%") – Fulham 2019 solo in slow-mo,
         strike exactly when the kick returns, keeper beaten, net
  bar 4  Cardiff 2018 – solo, strike, net – then 3 one-beat flashes on the kick roll -> loop
"""
import subprocess, sys, math, os, json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("AM9_MEDIA", os.path.join(HERE, "media"))
SONG = f"{ROOT}/audio/song.wav"
FONT = os.environ.get("AM9_FONT", os.path.join(ROOT, "fonts", "Montserrat-BlackItalic.ttf"))
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else f"{ROOT}/out/martial_edit.mp4"
PREVIEW = "--preview" in sys.argv

OW, OH, FPS = 1920, 1080, 30
SW, SH = 1920, 1080

BEAT = 0.44440                      # 135 BPM, grid snapped to the kick drum
def B(k):
    return 32.030 + BEAT * k

K0, K1 = -39, -7                    # 32 beats = 4 bars
PRE = 0.010                         # start 10 ms early so the downbeat transient stays intact
T0, T_END = B(K0) - PRE, B(K1) - PRE

SRC = f"{ROOT}/src/plcomp.mp4"      # Premier League "Martial – every PL goal" compilation, 1080p30
# burned-in overlays of the source that must never enter the crop window
FORBIDDEN = [(1735, 30, 1880, 200),   # Premier League lion, top right
             (1560, 975, 1905, 1052)] # "英超联赛 bilibili" watermark, bottom right

# EDL: (k_in, k_out, src_in, src_out, crop, extras)  crop = dict(cx=x | [(t, x), …], cy=y, h=height)
EDL = [
    # bar 1 – debut vs Liverpool, 12 Sep 2015
    (-39, -36, 17.59, 18.92, dict(cx=[(17.59, 860), (18.92, 900)], cy=495, h=960), {}),
    (-36, -34, 19.48, 20.37, dict(cx=[(19.48, 1080), (20.37, 900)], cy=540, h=900), {}),
    (-34, -31,  9.40, 10.73, dict(cx=[(9.4, 1120), (10.0, 1150), (10.73, 1000)], cy=470, h=960), {}),
    # bar 2 – Stoke, Feb 2016
    (-31, -28, 202.59, 203.92, dict(cx=[(202.59, 640), (203.92, 760)], cy=560, h=880), {}),
    (-28, -26, 204.62, 205.51, dict(cx=900, cy=480, h=920), {}),
    (-26, -23, 206.05, 207.38, dict(cx=960, cy=540, h=1080), {}),
    # bar 3 – drop-out: Fulham, Jan 2019
    (-23, -22, 51.00, 51.44, dict(cx=820, cy=560, h=880), {}),
    (-22, -18, 51.44, 52.30, dict(cx=[(51.44, 760), (52.30, 800)], cy=560, h=820), {"interp": True}),
    (-18, -16, 52.30, 52.98, dict(cx=[(52.30, 900), (52.98, 1150)], cy=560, h=960), {"interp": True}),
    (-16, -15, 53.02, 53.46, dict(cx=1300, cy=560, h=960), {}),
    # bar 4 – Cardiff, Dec 2018 + kick roll
    (-15, -12, 28.09, 29.42, dict(cx=[(28.09, 900), (29.42, 980)], cy=560, h=900), {}),
    (-12, -10, 30.15, 31.04, dict(cx=1150, cy=480, h=950), {}),
    (-10,  -9, 136.00, 136.44, dict(cx=1150, cy=520, h=960), {}),   # Norwich 2019, ball in
    ( -9,  -8, 40.05, 40.49, dict(cx=760, cy=560, h=860), {}),      # Southampton 2020, strike
    ( -8,  -7, 32.25, 32.69, dict(cx=980, cy=460, h=900), {}),      # Cardiff, the look -> loop
]

CAPTION = (B(-39) - PRE, B(-34), "DEBÜT MIT 19. GEGEN LIVERPOOL.")

IMPACT = {-36: dict(flash=0.25, shake=10, punch=0.10),
          -28: dict(flash=0.50, shake=0, punch=0.10),
          -18: dict(flash=0.85, shake=22, punch=0.12),
          -12: dict(flash=0.50, shake=0, punch=0.10)}
ROLL = [-10, -9, -8]
SNARES = [-37, -33, -29, -25, -17, -13]


def fidx(t):
    return int(round((t - T0) * FPS))


def interp_kf(kf, t):
    if not isinstance(kf, list):
        return float(kf)
    return float(np.interp(t, [p[0] for p in kf], [p[1] for p in kf]))


def safe_window(cx, cy, h):
    """16:9 window around (cx, cy), clamped to the frame and pushed out of the FORBIDDEN rects."""
    while True:
        w = h * 16 / 9
        x0 = min(max(cx - w / 2, 0), SW - w)
        y0 = min(max(cy - h / 2, 0), SH - h)
        ok = True
        for fx0, fy0, fx1, fy1 in FORBIDDEN:
            if x0 < fx1 and x0 + w > fx0 and y0 < fy1 and y0 + h > fy0:
                ok = False
                # cheapest escape: move left so the right edge clears it, or up/down
                cand = []
                if fx0 - w >= 0:
                    cand.append((abs((fx0 - w) - x0), fx0 - w, y0))
                if fy0 - h >= 0:
                    cand.append((abs((fy0 - h) - y0), x0, fy0 - h))
                if fy1 + h <= SH:
                    cand.append((abs(fy1 - y0), x0, fy1))
                if cand:
                    _, x0, y0 = min(cand)
                    ok = all(not (x0 < a1 and x0 + w > a0 and y0 < b1 and y0 + h > b0)
                             for a0, b0, a1, b1 in FORBIDDEN)
                break
        if ok:
            return x0, y0, w, h
        h -= 8
        if h < 400:
            raise RuntimeError("no safe window")


def decode(a, b, n, speed, interp):
    vf = [f"setpts=(PTS-STARTPTS)/{speed:.6f}"]
    if interp and speed < 0.95:
        vf.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    else:
        vf.append(f"fps={FPS}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{(b - a) + 0.5:.3f}",
           "-i", SRC, "-an", "-vf", ",".join(vf), "-frames:v", str(n),
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    got = len(raw) // (SW * SH * 3)
    if got == 0:
        raise RuntimeError(f"no frames {a}-{b}")
    frames = list(np.frombuffer(raw[: got * SW * SH * 3], np.uint8).reshape(got, SH, SW, 3))
    while len(frames) < n:
        frames.append(frames[-1])
    return frames[:n]


def crop(img, c, t_src):
    x0, y0, w, h = safe_window(interp_kf(c["cx"], t_src), c.get("cy", SH / 2), c.get("h", SH))
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


def caption_sprite(text, size=78):
    font = ImageFont.truetype(FONT, size)
    pad, sw = 40, 8
    bbox = font.getbbox(text, stroke_width=sw)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    im = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((pad - bbox[0] + 5, pad - bbox[1] + 7), text, font=font, fill=(0, 0, 0, 150),
           stroke_width=sw, stroke_fill=(0, 0, 0, 150))
    im = Image.fromarray(cv2.GaussianBlur(np.array(im), (0, 0), 6))
    d = ImageDraw.Draw(im)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=(255, 255, 255, 255),
           stroke_width=sw, stroke_fill=(0, 0, 0, 255))
    return np.array(im)


def overlay(img, sp, cx, cy, scale):
    if abs(scale - 1) > 1e-3:
        sp = cv2.resize(sp, (int(sp.shape[1] * scale), int(sp.shape[0] * scale)), interpolation=cv2.INTER_LINEAR)
    h, w = sp.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, OW), min(y0 + h, OH)
    part = sp[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = part[..., 3:4] / 255.0
    roi = img[ya:yb, xa:xb].astype(np.float32)
    img[ya:yb, xa:xb] = (roi * (1 - a) + part[..., [2, 1, 0]] * a).astype(np.uint8)
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
    rng = np.random.default_rng(9)
    cuts = [s[0] for s in EDL]
    punch = [(fidx(B(k)), d["punch"]) for k, d in IMPACT.items()] + \
            [(fidx(B(k)), 0.06) for k in ROLL] + \
            [(fidx(B(k)), 0.045) for k in cuts if k not in IMPACT and k not in ROLL] + \
            [(fidx(B(k)), 0.02) for k in SNARES]
    flash_ev = [(fidx(B(k)), d["flash"]) for k, d in IMPACT.items()]
    shake_ev = [(fidx(B(k)), d["shake"]) for k, d in IMPACT.items() if d["shake"]]
    rgb_ev = [(fidx(B(k)), 14) for k in IMPACT] + [(fidx(B(k)), 7) for k in cuts if k not in IMPACT]
    cap = (fidx(CAPTION[0]), fidx(CAPTION[1]), caption_sprite(CAPTION[2]))

    enc = None
    if not PREVIEW:
        os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
        dur = n_total / FPS
        enc = subprocess.Popen([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
            "-ss", f"{T0:.3f}", "-t", f"{dur:.3f}", "-i", SONG,
            "-filter_complex",
            "[0:v]eq=contrast=1.08:saturation=1.15:gamma=0.98,unsharp=5:5:0.6:5:5:0.0,"
            "vignette=angle=PI/5.5,format=yuv420p[v];"
            f"[1:a]{loudnorm_filter(dur)},aresample=44100,"
            f"afade=t=in:st=0:d=0.005,afade=t=out:st={dur - 0.005:.3f}:d=0.005[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level", "4.2",
            "-g", "30", "-bf", "2", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "320k", "-ar", "44100",
            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    else:
        os.makedirs(f"{ROOT}/out", exist_ok=True)

    f_global = 0
    for i, (k0, k1, a, b, c, ex) in enumerate(EDL):
        s0, s1 = B(k0) - PRE, B(k1) - PRE
        n = fidx(s1) - fidx(s0)
        speed = (b - a) / (s1 - s0)
        frames = decode(a, b, n, speed, ex.get("interp", False))
        print((i, k0, k1, round(s0, 3), a, b, round(speed, 3), n), flush=True)
        for k, fr in enumerate(frames):
            f = f_global + k
            img = crop(fr, c, a + (k / FPS) * speed)
            z = 1.0 + env(f, punch, 3.0)
            sh = env(f, shake_ev, 4.0)
            dx = dy = 0.0
            if sh > 0.8:
                dx, dy = rng.uniform(-sh, sh), rng.uniform(-sh, sh)
                z += sh / 900.0
            img = zoom_shift(img, z, dx, dy)
            cv_ = env(f, rgb_ev, 2.5)
            if cv_ > 0.8:
                s = int(round(cv_))
                b_, g_, r_ = cv2.split(img)
                img = cv2.merge([np.roll(b_, -s, axis=1), g_, np.roll(r_, s, axis=1)])
            fl = min(1.0, env(f, flash_ev, 2.2))
            if fl > 0.01:
                img = cv2.addWeighted(img, 1 - fl, np.full_like(img, 255), fl, 0)
            if cap[0] <= f < cap[1]:
                scale = 1.0 + 0.12 * math.exp(-(f - cap[0]) / 1.6)
                img = overlay(img.copy(), cap[2], OW / 2, OH * 0.085, scale)
            if PREVIEW:
                if k in (0, n // 2, n - 1):
                    cv2.imwrite(f"{ROOT}/out/prev_{i:02d}_{k:03d}.jpg", cv2.resize(img, (384, 216)))
            else:
                enc.stdin.write(img.tobytes())
        f_global += n
    if enc:
        enc.stdin.close()
        enc.wait()
    print("total frames", f_global, "expected", n_total, "duration", round(f_global / FPS, 3))


if __name__ == "__main__":
    main()
