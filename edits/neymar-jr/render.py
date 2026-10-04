#!/usr/bin/env python3
"""Neymar Jr – 16:9 black-and-white edit modelled on a reference TikTok, 13.64 s seamless loop.

Reference features reproduced:
  * 16:9, full black & white, crushed blacks, hard contrast, vignette
  * vocal intro (no drums): slow, cinematic – warm-up juggling wide -> feet close-up -> face close-up
  * drop: white flash, then ONE CUT PER BEAT alternating Champions-League dribbles and face close-ups
  * "NEYMAR JR 10" from behind -> free kick vs Red Star (Gazprom boards) -> ball in -> celebration
  * celebration fades to black, the black tail loops back into the warm-up
Audio is the reference's own song segment (first sample -> start of the next loop).
"""
import subprocess, sys, math, os, json
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NJR_MEDIA", os.path.join(HERE, "media"))
SONG = f"{ROOT}/audio/ref_audio.wav"          # audio track of the reference screen recording
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else f"{ROOT}/out/neymar_edit.mp4"
PREVIEW = "--preview" in sys.argv

OW, OH, FPS = 1920, 1080, 30
SW, SH = 1920, 1080

A_IN = 0.9753                  # first audio sample of the loop in the reference recording
A_LEN = 13.638                 # loop length (next loop starts at 14.613)
BEAT = 0.46850                 # 128.07 BPM, grid snapped to the kick drum
def G(n):                      # output time of beat n (n = 13 is the drop)
    return 0.0022 + BEAT * n

N_FRAMES = int(round(A_LEN * FPS))
FADE_IN, FADE_OUT = G(27.0), G(27.8)  # celebration fades to black like the reference

# EDL: (n_in, n_out, src, src_in, src_out, crop(x, y, w, h), extras)
EDL = [
    # vocal intro – slow and cinematic
    (0, 5,   "rare",       38.90, 40.66, (220, 110, 1600, 900), {"interp": True, "push": 0.05}),   # UCL warm-up juggling
    (5, 8,   "skills1819", 242.35, 243.76, (240, 135, 1440, 810), {"push": 0.04}),                 # feet + ball close-up
    (8, 12,  "skills1819", 444.82, 446.00, (480, 135, 1440, 810), {"interp": True, "push": 0.07}), # the face
    (12, 13, "skills1819", 679.80, 680.27, (240, 135, 1440, 810), {}),                             # ball at the feet
    # DROP – white flash, one cut per beat
    (13, 14, "skills1819", 603.85, 604.32, (480, 135, 1440, 810), {}),
    (14, 15, "scene8k",    11.25, 11.72, (200, 90, 1600, 900), {}),        # vs Real Madrid, Bernabéu 2018
    (15, 16, "scene8k",    11.72, 12.19, (200, 90, 1600, 900), {}),
    (16, 17, "scene8k",    12.19, 12.66, (460, 120, 1280, 720), {}),
    (17, 18, "faces",      79.08, 79.55, (0, 105, 1529, 860), {}),         # hands on face
    (18, 19, "scene8k",    13.15, 13.62, (320, 60, 1600, 900), {}),        # vs Bayern, CHAMPIONS LEAGUE board
    (19, 20, "scene8k",    22.55, 23.02, (0, 80, 1600, 900), {}),          # profile, Bernabéu crowd
    (20, 21, "skills1819", 342.42, 342.89, (300, 135, 1440, 810), {}),     # close dribble
    (21, 22, "skills1819", 456.00, 456.47, (400, 135, 1440, 810), {}),     # feet on the ball
    (22, 23.333, "faces",  77.92, 78.54, (170, 110, 1493, 840), {}),       # NEYMAR JR 10
    (23.333, 25, "uclpsg", 31.08, 31.86, (0, 20, 1660, 934), {}),          # free kick vs Red Star, strike on the cut
    (25, 26, "uclpsg",     32.45, 32.92, (320, 130, 1600, 900), {}),       # ball in
    (26, None, "uclpsg",   105.20, 106.40, (40, 120, 1600, 900), {"interp": True, "push": 0.06}),  # crossed arms
]

FLASH = {13: 1.0, 25: 0.35}
PUNCH_DROP = 0.10
PUNCH_CUT = 0.05


def fidx(t):
    return int(round(t * FPS))


def decode(src, a, b, n, speed, interp):
    vf = [f"setpts=(PTS-STARTPTS)/{speed:.6f}"]
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
        raise RuntimeError(f"no frames {src} {a}-{b}")
    frames = list(np.frombuffer(raw[: got * SW * SH * 3], np.uint8).reshape(got, SH, SW, 3))
    while len(frames) < n:
        frames.append(frames[-1])
    return frames[:n]


def crop_scale(img, c, push):
    x, y, w, h = c
    cx, cy = x + w / 2, y + h / 2
    w2, h2 = w / push, h / push
    x0, y0 = cx - w2 / 2, cy - h2 / 2
    sx, sy = OW / w2, OH / h2
    M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)


def env(f, events, tau):
    v = 0.0
    for fe, amp in events:
        if f >= fe:
            v += amp * math.exp(-(f - fe) / tau)
    return v


def zoom(img, z):
    if z <= 1.0005:
        return img
    M = np.float32([[z, 0, (1 - z) * OW / 2], [0, z, (1 - z) * OH / 2]])
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# black & white look: luma with a hard S-curve (crushed blacks, bright highlights)
_x = np.arange(256) / 255.0
_s = np.clip((_x - 0.06) / 0.88, 0, 1)
LUT = np.clip(255 * (_s ** 1.12 * (3 - 2 * _s) * _s * 0.5 + _s ** 1.12 * 0.5), 0, 255).astype(np.uint8)
YY, XX = np.mgrid[0:OH, 0:OW]
VIG = (1.0 - 0.42 * (((XX - OW / 2) / (OW / 2)) ** 2 + ((YY - OH / 2) / (OH / 2)) ** 2) ** 1.4).clip(0.45, 1)
VIG = VIG.astype(np.float32)
# 4 pre-baked, slightly soft grain plates: keeps the filmic texture but stays compressible
_gr = np.random.default_rng(3)
GRAIN = [cv2.GaussianBlur(_gr.normal(0, 2.4, (OH, OW)).astype(np.float32), (0, 0), 0.7) for _ in range(4)]


def grade(img, rng):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.LUT(g, LUT).astype(np.float32) * VIG
    g += GRAIN[rng.integers(len(GRAIN))]                         # fine film grain (pre-baked tiles)
    return np.clip(g, 0, 255).astype(np.uint8)


def loudnorm_filter(target=-14.0, tp=-1.0):
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{A_IN:.4f}", "-t", f"{A_LEN:.3f}", "-i", SONG,
                            "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    return (f"loudnorm=I={target}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}")


def main():
    rng = np.random.default_rng(10)
    cuts = [s[0] for s in EDL if s[0] >= 14]
    punch = [(fidx(G(13)), PUNCH_DROP)] + [(fidx(G(n)), PUNCH_CUT) for n in cuts]
    flash = [(fidx(G(n)), a) for n, a in FLASH.items()]

    enc = None
    if not PREVIEW:
        os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
        dur = N_FRAMES / FPS
        enc = subprocess.Popen([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
            "-ss", f"{A_IN:.4f}", "-t", f"{dur:.3f}", "-i", SONG,
            "-filter_complex",
            "[0:v]format=yuv420p[v];"
            f"[1:a]{loudnorm_filter()},aresample=44100,afade=t=out:st={dur - 0.01:.3f}:d=0.01[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-level", "4.2",
            "-g", "30", "-bf", "2", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    else:
        os.makedirs(f"{ROOT}/out", exist_ok=True)

    f_global = 0
    for i, (n0, n1, src, a, b, c, ex) in enumerate(EDL):
        f0 = fidx(G(n0)) if n0 > 0 else 0
        f1 = fidx(G(n1)) if n1 is not None else N_FRAMES
        n = f1 - f0
        speed = (b - a) / (n / FPS)
        frames = decode(src, a, b, n, speed, ex.get("interp", False))
        print((i, n0, n1, round(f0 / FPS, 3), src, a, b, round(speed, 3), n), flush=True)
        for k, fr in enumerate(frames):
            f = f0 + k
            push = 1.0 + ex.get("push", 0.0) * (k / max(1, n - 1))
            img = crop_scale(fr, c, push)
            img = zoom(img, 1.0 + env(f, punch, 3.2))
            g = grade(img, rng)
            fl = min(1.0, env(f, flash, 2.0))
            if fl > 0.01:
                g = (g.astype(np.float32) * (1 - fl) + 255 * fl).astype(np.uint8)
            t = f / FPS
            if t >= FADE_IN:
                g = (g.astype(np.float32) * max(0.0, 1 - (t - FADE_IN) / (FADE_OUT - FADE_IN))).astype(np.uint8)
            if PREVIEW:
                if k in (0, n // 2, n - 1):
                    cv2.imwrite(f"{ROOT}/out/prev_{i:02d}_{k:03d}.jpg", cv2.resize(g, (384, 216)))
            else:
                enc.stdin.write(g.tobytes())
        f_global = f1
    if enc:
        enc.stdin.close()
        enc.wait()
    print("total frames", f_global, "expected", N_FRAMES, "duration", round(f_global / FPS, 3))


if __name__ == "__main__":
    main()
