#!/usr/bin/env python3
"""Clip 3 – "3 Tore, die eigentlich unmöglich sind": countdown #3 -> #1 with a live list.
Teases #1 in the first 0.6 s (retention), list fills as each ball hits the net, ends on a
comment question.  9:16, ~15 s, loops into the teaser.
"""
import os, sys, math
import numpy as np
import cv2
import tk

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CLIPS_MEDIA", os.path.join(HERE, "media"))   # footage lives outside git
SRC = os.path.join(ROOT, "rank", "src")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "rank", "out", "3_unmoegliche_tore.mp4")
W, H, FPS = tk.W, tk.H, tk.FPS
VW, VH, VY = 1080, 810, 400
WESTHAM_PRE = ("crop=1746:978:206:50,scale=1920:1080:flags=lanczos,setsar=1", 1920, 1080)

# (out_dur, file, src_in, src_out, crop keyframes [(t, x0)] , y0, w, h, interp, pre, tag)
SHOTS = [
    (0.60, "cr7", 61.50, 61.80, [(0, 300)], 60, 1253, 940, True, None, "teaser"),
    # #3 Lamine Yamal vs France, EURO 2024 semi-final
    (1.10, "yamal_pure", 75.50, 76.15, [(0, 330)], 0, 1440, 1080, True, None, "y_strike"),
    (1.05, "yamal_pure", 76.50, 77.25, [(0, 480)], 0, 1440, 1080, True, None, "y_net"),
    (1.00, "yamal_wide", 7.90, 8.90, [(0, 380)], 140, 1040, 780, False, None, "y_cel"),
    # #2 Eden Hazard solo vs West Ham, April 2019
    (4.72, "hazard", 149.50, 155.40, [(149.5, 300), (154.3, 300), (154.9, 60), (155.4, 60)], 100, 1307, 980,
     False, None, "h_solo"),
    (1.00, "hazard_wh", 91.90, 92.70, [(0, 470)], 200, 1000, 750, True, WESTHAM_PRE, "h_cel"),
    # #1 Cristiano Ronaldo bicycle kick vs Juventus, UCL 2018
    (0.80, "cr7", 61.15, 61.95, [(0, 300)], 60, 1253, 940, False, None, "c_live"),
    (2.10, "cr7", 74.44, 75.40, [(0, 330)], 100, 1253, 940, True, None, "c_replay"),
    (0.80, "cr7", 63.17, 63.85, [(0, 620)], 150, 1093, 820, False, None, "c_net"),
    (0.70, "cr7", 84.15, 84.85, [(0, 360)], 60, 1200, 900, False, None, "c_zidane"),
    (1.40, "cr7", 87.05, 88.25, [(0, 380)], 60, 1200, 900, True, None, "c_heart"),
]
STARTS = np.cumsum([0] + [s[0] for s in SHOTS])
T_END = float(STARTS[-1])
TAG = {s[10]: float(STARTS[i]) for i, s in enumerate(SHOTS)}
SEG3, SEG2, SEG1 = TAG["y_strike"], TAG["h_solo"], TAG["c_live"]
STRIKES = [TAG["y_strike"] + (75.80 - 75.50) / (0.65 / 1.10),
           TAG["h_solo"] + (154.65 - 149.50) / (5.90 / 4.72),
           TAG["c_replay"] + (74.88 - 74.44) / (0.96 / 2.10)]
GOALS = [TAG["y_net"] + 0.15, TAG["h_solo"] + (155.10 - 149.50) / (5.90 / 4.72), TAG["c_net"] + 0.10]

ROWS = [("#1", "RONALDO", "FALLRÜCKZIEHER IN TURIN"),
        ("#2", "HAZARD", "SOLO DURCH DIE ABWEHR"),
        ("#3", "YAMAL", "MIT 16 IM EM-HALBFINALE")]


def background(win):
    small = cv2.resize(win, (VW // 8, VH // 8))
    bw = int(VH / 8 * W / H)
    x0 = (small.shape[1] - bw) // 2
    bg = cv2.resize(small[:, x0:x0 + bw], (W, H), interpolation=cv2.INTER_LINEAR)
    bg = cv2.GaussianBlur(bg, (0, 0), 20)
    return (bg.astype(np.float32) * 0.28).astype(np.uint8)


def paste_left(img, sp, x, cy, scale=1.0, alpha=1.0):
    return tk.paste(img, sp, x + sp.shape[1] * scale / 2, cy, scale, alpha)


def main():
    n_total = int(round(T_END * FPS))
    enc = tk.encoder(OUT, os.path.join(ROOT, "rank", "audio.wav"), T_END)
    title = tk.text_sprite(["3 TORE, DIE EIGENTLICH", "UNMÖGLICH SIND"], size=82, max_w=920, line_gap=0.05)
    teaser = tk.text_sprite("#1 KOMMT ZUM SCHLUSS", size=48, fill=(15, 15, 15), box=tk.YELLOW, pad=16)
    badges = {r: tk.text_sprite(r, size=150, fill=tk.YELLOW, stroke=10) for r in ("#3", "#2", "#1")}
    row_open = {r[0]: tk.text_sprite(f"{r[0]}  {r[1]}", size=50, fill=tk.WHITE, max_w=820, pad=6) for r in ROWS}
    row_fact = {r[0]: tk.text_sprite(r[2], size=34, fill=tk.YELLOW, max_w=820, pad=4) for r in ROWS}
    row_hidden = {r[0]: tk.text_sprite(f"{r[0]}  ???", size=50, fill=(150, 150, 150), max_w=820, pad=6) for r in ROWS}
    end1 = tk.text_sprite(["WELCHES IST", "DEINE NR. 1?"], size=78, max_w=880, line_gap=0.05)
    end2 = tk.text_sprite("SCHREIB'S IN DIE KOMMENTARE", size=40, fill=tk.YELLOW)
    reveal_t = {"#3": GOALS[0], "#2": GOALS[1], "#1": GOALS[2]}

    frames = []
    for i, (dur, src, a, b, kf, y0, w, h, interp, pre, tag) in enumerate(SHOTS):
        n = int(round(STARTS[i + 1] * FPS)) - int(round(STARTS[i] * FPS))
        kw = dict(interp=interp)
        if pre:
            kw.update(pre=pre[0], sw=pre[1], sh=pre[2])
        fr = tk.read_clip(os.path.join(SRC, f"{src}.mp4"), a, b, n, **kw)
        speed = (b - a) / (n / FPS)
        for k, f in enumerate(fr):
            ts = a + k / FPS * speed
            x0 = kf[0][1] if len(kf) == 1 else float(np.interp(ts, [p[0] for p in kf], [p[1] for p in kf]))
            frames.append((tag, f, (x0, y0, w, h)))
    assert len(frames) == n_total, (len(frames), n_total)

    for fi, (tag, f, rect) in enumerate(frames):
        t = fi / FPS
        zoom = 1.0
        for st in STRIKES:
            if t >= st:
                zoom += 0.08 * math.exp(-(t - st) * FPS / 3)
        win = tk.grade(tk.warp_crop(f, rect, VW, VH, zoom))
        if tag == "teaser":
            win = (win.astype(np.float32) * 0.75).astype(np.uint8)
        img = background(win)
        img[VY:VY + VH] = win
        cv2.rectangle(img, (0, VY - 6), (W, VY), (0, 214, 255), -1)
        cv2.rectangle(img, (0, VY + VH), (W, VY + VH + 6), (0, 214, 255), -1)
        tk.paste(img, title, W / 2, 245)

        if tag == "teaser":
            tk.paste(img, teaser, W / 2, VY + VH / 2, scale=tk.pop(fi, 5, 0.25))
        # rank badge at the start of each block
        for r, st in (("#3", SEG3), ("#2", SEG2), ("#1", SEG1)):
            if st <= t < st + 1.2:
                age = (t - st) * FPS
                al = 1.0 if t < st + 0.9 else max(0, 1 - (t - st - 0.9) / 0.3)
                tk.paste(img, badges[r], 150, VY + 110, scale=tk.pop(age, 5, 0.35), alpha=al)

        # live list (#1 on top), hidden until that goal hits the net
        for j, r in enumerate(ROWS):
            y = VY + VH + 95 + j * 112
            rt = reveal_t[r[0]]
            if t >= rt:
                age = (t - rt) * FPS
                paste_left(img, row_open[r[0]], 70, y, scale=tk.pop(age, 5, 0.2))
                paste_left(img, row_fact[r[0]], 76, y + 50, alpha=min(1, age / 4))
            else:
                paste_left(img, row_hidden[r[0]], 70, y, alpha=0.8)

        if tag == "c_heart":
            age = (t - TAG["c_heart"]) * FPS
            tk.paste(img, end1, W / 2, VY + 170, scale=tk.pop(age - 3, 5))
            tk.paste(img, end2, W / 2, VY + 290, scale=tk.pop(age - 9, 5))

        fl = 0.0
        for g in GOALS:
            if t >= g:
                fl += 0.7 * math.exp(-(t - g) * FPS / 2.2)
        img = tk.flash(img, min(1, fl))
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    print("frames", n_total, "dur", round(T_END, 3), "strikes", np.round(STRIKES, 2), "goals", np.round(GOALS, 2))


def make_audio():
    m = tk.Mix(T_END)
    m.add(tk.riser(0.6, 0.35), 0.0)
    m.beat(SEG3, T_END, 128, "hiphop", g=0.75, bass_notes=(55, 49, 58.3, 52))
    for st in (SEG3, SEG2, SEG1):
        m.add(tk.whoosh(0.4, 0.55), st - 0.25)
    for s in STRIKES:
        m.add(tk.impact(0.9), s)
    for g in GOALS:
        m.add(tk.ding(0.55), g)
    m.add(tk.riser(1.0, 0.35), STRIKES[2] - 1.0)
    m.write(os.path.join(ROOT, "rank", "audio.wav"))


if __name__ == "__main__":
    make_audio()
    main()
