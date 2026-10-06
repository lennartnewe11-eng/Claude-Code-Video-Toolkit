"""Finishing pass over the HyperFrames render: impact shake, white flashes,
chromatic split, soft bloom and luminance-weighted film grain, then mux.

    python3 post.py build/picture_hf.mp4 build/mix.wav output/eagle-has-landed_tiktok.mp4
"""
from __future__ import annotations

import math
import subprocess
import sys

import cv2
import numpy as np

W, H, FPS = 1080, 1920, 30
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)

# (time, shake px, chroma, white flash, decay s) – synced to scene cuts and real audio
IMPACTS = [
    (0.00, 14, 0.008, 0.00, 0.16), (0.43, 6, 0.004, 0.0, 0.10), (0.86, 9, 0.006, 0.0, 0.12),
    (1.29, 6, 0.004, 0.0, 0.10), (1.79, 12, 0.008, 0.35, 0.12),
    (2.00, 6, 0.004, 0.12, 0.08), (2.20, 6, 0.004, 0.12, 0.08), (2.41, 6, 0.004, 0.12, 0.08),
    (2.62, 6, 0.004, 0.12, 0.08), (2.82, 6, 0.004, 0.12, 0.08),
    (3.02, 14, 0.010, 0.40, 0.14), (3.10, 8, 0.006, 0.0, 0.10), (5.80, 10, 0.006, 0.30, 0.12),
    (7.03, 16, 0.010, 0.20, 0.14), (8.32, 10, 0.006, 0.30, 0.12), (8.45, 8, 0.005, 0.0, 0.10),
    (11.40, 18, 0.012, 0.0, 0.16), (12.45, 22, 0.016, 0.90, 0.20),
    (17.04, 0, 0.004, 0.25, 0.30), (17.85, 6, 0.004, 0.20, 0.12), (19.35, 6, 0.004, 0.30, 0.14),
]
rng = np.random.default_rng(11)
PH = [rng.uniform(0, 6.283, 4) for _ in IMPACTS]


def envelopes(t):
    sx = sy = chroma = flash = 0.0
    for (t0, sh, ch, fl, d), ph in zip(IMPACTS, PH):
        dt = t - t0
        if dt < -1e-6 or dt > 1.0:
            continue
        e = math.exp(-dt / d)
        sx += sh * e * (0.65 * math.sin(2 * math.pi * 21 * dt + ph[0]) + 0.35 * math.sin(2 * math.pi * 33 * dt + ph[1]))
        sy += sh * e * (0.65 * math.sin(2 * math.pi * 17 * dt + ph[2]) + 0.35 * math.sin(2 * math.pi * 29 * dt + ph[3]))
        chroma += ch * e
        flash = max(flash, fl * math.exp(-dt / (d * 0.5)))
    return sx, sy, chroma, flash


def make_grain(n=8, seed=5):
    r = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = cv2.GaussianBlur(r.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6)
        out.append((g / g.std())[..., None])
    return out


def chroma_split(x, amt):
    if amt < 0.0006:
        return x
    o = x.copy()
    for c, s in ((0, 1 + amt), (2, 1 - amt)):
        M = np.array([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]], np.float32)
        o[..., c] = cv2.warpAffine(x[..., c], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return o


def bloom(x, k=0.16, thr=0.78):
    s = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    m = np.clip((s @ LUMA - thr) / (1 - thr), 0, 1)[..., None]
    g = cv2.GaussianBlur(s * m, (0, 0), 12)
    g = cv2.resize(g, (W, H)) * np.array([1.0, 0.9, 0.8], np.float32)
    return 1 - (1 - x) * (1 - g * k)


def main(src, wav, dst):
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", "scale=in_color_matrix=bt709,format=rgb24",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd,format=yuv420p",
                            "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", "16", "-maxrate", "14M",
                            "-bufsize", "28M", "-profile:v", "high", "-level", "4.2", "-g", str(FPS * 2),
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", "-shortest", dst],
                           stdin=subprocess.PIPE)
    grain = make_grain()
    yy, xx = np.mgrid[-1:1:complex(0, H), -1:1:complex(0, W)].astype(np.float32)
    vign = (1 - 0.22 * np.clip(np.sqrt((xx * 0.9) ** 2 + (yy * 0.6) ** 2) - 0.4, 0, None) ** 1.5)[..., None]
    f = 0
    size = W * H * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        t = f / FPS
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        sx, sy, ch, fl = envelopes(t)
        if abs(sx) + abs(sy) > 0.05:
            s = 1.0 + (abs(sx) + abs(sy)) / 900          # zoom a hair so edges never show
            M = np.array([[s, 0, (1 - s) * W / 2 + sx], [0, s, (1 - s) * H / 2 + sy]], np.float32)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        x = img.astype(np.float32) / 255
        x = bloom(x)
        x = chroma_split(x, ch)
        x = x * vign
        if fl > 0.002:
            x = x + (1 - x) * fl
        l = (x @ LUMA)[..., None]
        x = x + grain[(f * 3) % len(grain)] * 0.022 * (4 * l * (1 - l) + 0.12)
        enc.stdin.write((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        f += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print("post done,", f, "frames")


if __name__ == "__main__":
    main(*sys.argv[1:4])
