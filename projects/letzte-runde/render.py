"""Render the picture of "LETZTE RUNDE" and mux it with the sound mix.

    python3 render.py                 # full render → output/letzte-runde_tiktok.mp4
    python3 render.py --frames 0,360  # write single PNG stills for review
"""
from __future__ import annotations

import argparse
import math
import time
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

import edl
from engine import (FPS, H, ROOT, RED, WHITE, Grain, bloom, chroma_split, clamp, composite, ease_in_out,
                    ease_out_cubic, grade, load_shot, open_encoder, pill, place, render_line, sample_source,
                    vignette_mask)

OUT = ROOT / "output"
grain = Grain()
rng = np.random.default_rng(3)
PHASES = [rng.uniform(0, 2 * np.pi, 4) for _ in edl.IMPACTS]


# ---------------------------------------------------------------------------
# impact envelopes
# ---------------------------------------------------------------------------
def impacts(t):
    sx = sy = rot = zoom = flash = chroma = 0.0
    glitch = 0.0
    for e, ph in zip(edl.IMPACTS, PHASES):
        dt = t - e["t"]
        if dt < -1e-6 or dt > 1.2:
            continue
        d = e["decay"]
        env = math.exp(-dt / d)
        a = e["shake"] * env
        sx += a * (0.65 * math.sin(2 * math.pi * 19 * dt + ph[0]) + 0.35 * math.sin(2 * math.pi * 33 * dt + ph[1]))
        sy += a * (0.65 * math.sin(2 * math.pi * 23 * dt + ph[2]) + 0.35 * math.sin(2 * math.pi * 29 * dt + ph[3]))
        rot += 0.03 * a * math.sin(2 * math.pi * 13 * dt + ph[1])
        zoom += e["zoom"] * math.exp(-dt / (d * 1.3))
        flash = max(flash, e["flash"] * math.exp(-dt / (d * 0.45)))
        chroma += e["chroma"] * env
        if dt < e.get("glitch", 0):
            glitch = max(glitch, 1 - dt / e["glitch"])
    return sx, sy, rot, zoom, flash, chroma, glitch


def glitch_fx(x, amount, frame):
    r = np.random.default_rng(frame * 31 + 5)
    out = x.copy()
    y = 0
    while y < H:
        h = int(r.integers(18, 140))
        if r.random() < 0.45 * amount + 0.15:
            dx = int(r.integers(-60, 60) * amount)
            out[y:y + h] = np.roll(x[y:y + h], dx, axis=1)
            if r.random() < 0.5:
                out[y:y + h, :, 0] = np.roll(x[y:y + h, :, 0], dx + int(14 * amount), axis=1)
        y += h
    return out


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------
def draw_texts(img, t, shake):
    for card in edl.TEXTS:
        lines = card["lines"]
        t_out = card["t_out"]
        if t < lines[0][1] - 1e-6 or t >= t_out:
            continue
        size = card["size"]
        heavy = card.get("heavy", False)
        cy = card.get("y", edl.TEXT_Y)
        n = len(lines)
        lh = size * 1.04
        top = cy - lh * (n - 1) / 2
        out_k = clamp((t_out - t) / 0.07)          # quick fade on exit
        # soft dark scrim behind the block keeps white type readable on any shot
        vis = clamp((t - lines[0][1]) / 0.12) * out_k
        if vis > 0:
            img *= 1 - 0.38 * vis * scrim(cy, lh * n)
        for i, (txt, ta) in enumerate(lines):
            dt = t - ta
            if dt < -1e-6:
                continue
            if card.get("first_frame_solid") and ta == 0:
                s = 1 + 0.14 * (1 - ease_out_cubic(dt / 0.20))
                op = 1.0
            else:
                k = (0.6 if heavy else 0.28)
                s = 1 + k * (1 - ease_out_cubic(dt / (0.20 if heavy else 0.15)))
                op = clamp(dt / 0.05)
            # small pop with the beat impacts
            s *= 1 + 0.35 * impacts_cache[3]
            layer = render_line(txt, "anton", size, WHITE, RED, 0.01)
            sx, sy = shake[0] * 0.45, shake[1] * 0.45
            if heavy:
                # white echo bursting outwards behind the main word
                echo = render_line(txt, "anton", size, WHITE, WHITE, 0.01, False)
                e = clamp(dt / 0.45)
                if e < 1:
                    composite(img, echo, edl.TEXT_X + sx, top + i * lh + sy, s * (1 + 0.55 * ease_out_cubic(e)),
                              (1 - e) * 0.55 * out_k)
            composite(img, layer, edl.TEXT_X + sx, top + i * lh + sy, s, op * out_k,
                      blur_y=max(0.0, (s - 1) * 60))
    return img


@lru_cache(maxsize=16)
def scrim(cy, block_h):
    y = np.arange(H, dtype=np.float32)
    a = np.exp(-((y - cy) / (block_h * 0.5 + 170)) ** 2)
    return a[:, None, None]


def draw_clock(img, t):
    c = edl.CLOCK
    if t >= c["hide"] + 0.25:
        return img
    ko = c["ko"]
    if t < ko:
        val = c["start"] - int(math.floor(t + 1e-6))
        val = max(val, 1)
    else:
        val = 0
    tick_dt = (t + 1e-6) % 1.0 if t < ko else t - ko
    scale = 1.0 + 0.10 * (1 - ease_out_cubic(tick_dt / 0.18))
    color = WHITE
    op = 1.0
    if 4.0 <= t < 8.0:
        op = 0.55
    if 11.1 <= t < ko:
        u = ease_in_out((t - 11.1) / 0.35)
        scale *= 1 + 0.45 * u
        color = RED
        for hb in c["heartbeat"]:
            if t >= hb:
                scale *= 1 + 0.16 * math.exp(-(t - hb) / 0.10)
    if t >= ko:
        color = RED
        scale *= 1.45 - 0.45 * ease_out_cubic((t - ko) / 0.4)
        if t >= ko + 0.3:
            op = 1.0 if int((t - ko) / 0.18) % 2 == 0 else 0.15
        if t >= c["hide"]:
            op *= clamp(1 - (t - c["hide"]) / 0.25)
    txt = f"0:{val:02d}"
    base_w, base_h = 250, 96
    bg = pill(int(base_w * scale) // 2 * 2, int(base_h * scale) // 2 * 2)
    composite(img, bg, 540, c["y"], 1.0, op)
    lay = render_line(txt, "barlow_black", 86, color, RED, 0.02, False)
    composite(img, lay, 540 + 26 * scale, c["y"] + 2 * scale, scale, op)
    if (t < ko and (t % 1.0) < 0.6) or t >= ko:   # blinking "live" dot
        d = int(22 * scale) // 2 * 2
        composite(img, pill(d, d, RED, 1.0), 540 - 82 * scale, c["y"], 1.0, op)
    return img


impacts_cache = (0, 0, 0, 0, 0, 0, 0)


def unsharp(x, amount, sigma=1.1):
    if amount <= 0:
        return x
    b = cv2.GaussianBlur(x, (0, 0), sigma)
    return np.clip(x + amount * (x - b), 0, 1)


def render_frame(shot, f):
    global impacts_cache
    t = f / FPS
    sx, sy, rot, zp, flash, chroma, glitch = impacts_cache = impacts(t)
    look = shot.look
    fin = edl.FINISH[look]
    src = sample_source(shot, t)
    pan = shot.pan_at(t)
    if look == "memory":  # gate weave
        r = np.random.default_rng(f)
        pan = (pan[0] + r.normal(0, 1.5), pan[1] + r.normal(0, 1.5))
    z = shot.zoom_at(t) * (1 + zp)
    img = place(src, z, shot.focus_at(t), (sx, sy), rot, pan).astype(np.float32) / 255.0
    img = unsharp(img, shot.sharpen)
    if shot.dehaze:
        img = np.clip((img - shot.dehaze) / (1 - shot.dehaze), 0, 1)
    img = grade(img, look)
    if look == "memory":
        img = img * (1 + 0.035 * np.random.default_rng(f + 99).normal())
    img = bloom(img, fin["bloom"])
    img = chroma_split(img, chroma)
    img = img * vignette_mask(fin["vignette"])
    if look == "ko" and t < 12.5:   # red pulse on the knockout
        k = math.exp(-(t - 12.0) / 0.18)
        img = img * (1 - 0.25 * k) + np.array([0.55, 0.02, 0.02], np.float32) * 0.25 * k
    if flash > 0.002:
        img = img + (1 - img) * flash
    if glitch > 0:
        img = glitch_fx(img, glitch, f)
    img = grain.apply(np.clip(img, 0, 1), fin["grain"], f)
    img = np.ascontiguousarray(img, dtype=np.float32)
    img = draw_texts(img, t, (sx, sy))
    img = draw_clock(img, t)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def shot_for_frame(f):
    t = f / FPS
    for s in edl.SHOTS:
        if s.t0 - 1e-6 <= t < s.t1 - 1e-6:
            return s
    return edl.SHOTS[-1]


def max_zoom(shot):
    zs = [z for _, z in shot.zoom]
    punch = max([e["zoom"] for e in edl.IMPACTS if shot.t0 - 0.01 <= e["t"] < shot.t1] + [0])
    return max(zs) * (1 + punch) * 1.02


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", help="comma separated frame numbers to export as PNG")
    ap.add_argument("--out", default=str(OUT / "picture.mp4"))
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    total = int(round(edl.DURATION * FPS))
    wanted = None
    if args.frames:
        wanted = sorted(int(x) for x in args.frames.split(","))
    enc = None if wanted else open_encoder(Path(args.out))
    loaded = None
    t_start = time.time()
    for f in range(total):
        if wanted is not None and f not in wanted:
            continue
        shot = shot_for_frame(f)
        if loaded is not shot:
            if loaded is not None:
                loaded.frames = None
            load_shot(shot, max_zoom(shot))
            loaded = shot
        frame = render_frame(shot, f)
        if enc:
            enc.stdin.write(frame.tobytes())
        else:
            p = OUT / f"still_{f:03d}.png"
            cv2.imwrite(str(p), frame[:, :, ::-1])
            print("wrote", p)
        if f % 30 == 0:
            print(f"frame {f}/{total}  {time.time() - t_start:.1f}s", flush=True)
    if enc:
        enc.stdin.close()
        enc.wait()
        print("picture done", time.time() - t_start)


if __name__ == "__main__":
    main()
