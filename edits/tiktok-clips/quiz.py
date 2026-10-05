#!/usr/bin/env python3
"""Clip 2 – "Erkennst du ihn am Jubel?": 5 pixelated celebrations, 3-2-1 countdown, reveal.
Built for comments ("wie viele hattest du?") + rewatches (people replay to check).  9:16, 14.4 s.
"""
import os, sys, math
import numpy as np
import cv2
import tk

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CLIPS_MEDIA", os.path.join(HERE, "media"))   # footage lives outside git
SRC = os.path.join(ROOT, "quiz", "src")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "quiz", "out", "jubel_quiz.mp4")
W, H, FPS = tk.W, tk.H, tk.FPS
VW, VH, VY = 1080, 810, 430                       # 4:3 window
BEAT = 0.45                                       # 133.3 BPM; a round = 4 beats guessing + 2 beats reveal

ROUNDS = [  # file, src_in, src_out, crop keyframes [(t_src, cx)], cy, h, name, pre
    ("siu", 75.06, 76.60, [(75.06, 960), (76.6, 960)], 585, 990, "CRISTIANO RONALDO", None),
    ("mbappe", 195.40, 196.50, [(195.4, 800), (196.1, 1200), (196.5, 1200)], 590, 980, "KYLIAN MBAPPÉ", None),
    ("pogba", 156.00, 157.30, [(156.0, 753), (157.3, 753)], 590, 980, "PAUL POGBA",
     ("setsar=1", 1440, 1080)),
    ("hazard", 91.75, 92.95, [(91.75, 1050), (92.95, 1050)], 575, 750, "EDEN HAZARD",
     ("crop=1746:978:206:50,scale=1920:1080:flags=lanczos,setsar=1", 1920, 1080)),
    ("vardy", 30.40, 33.70, [(30.4, 740), (31.8, 1240), (32.6, 1050), (33.3, 860), (33.7, 860)], 520, 820,
     "JAMIE VARDY", None),
]
GUESS_BEATS, REVEAL_BEATS, LAST_REVEAL_BEATS = 4, 2, 4


def round_times():
    t = 0.0
    out = []
    for i in range(len(ROUNDS)):
        rb = LAST_REVEAL_BEATS if i == len(ROUNDS) - 1 else REVEAL_BEATS
        start, reveal, end = t, t + GUESS_BEATS * BEAT, t + (GUESS_BEATS + rb) * BEAT
        out.append((start, reveal, end))
        t = end
    return out


RT = round_times()
T_END = RT[-1][2]


def background(win):
    small = cv2.resize(win, (VW // 8, VH // 8))
    bw = int(VH / 8 * W / H)
    x0 = (small.shape[1] - bw) // 2
    bg = cv2.resize(small[:, x0:x0 + bw], (W, H), interpolation=cv2.INTER_LINEAR)
    bg = cv2.GaussianBlur(bg, (0, 0), 20)
    return (bg.astype(np.float32) * 0.30).astype(np.uint8)


def pixelate(img, block):
    if block <= 1:
        return img
    h, w = img.shape[:2]
    small = cv2.resize(img, (max(1, w // block), max(1, h // block)), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def countdown_sprite(d):
    from PIL import Image, ImageDraw
    s = 210
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse([6, 6, s - 6, s - 6], fill=(255, 214, 0, 255), outline=(0, 0, 0, 255), width=8)
    f = tk.font(140)
    bb = f.getbbox(d)
    dr.text(((s - (bb[2] - bb[0])) / 2 - bb[0], (s - (bb[3] - bb[1])) / 2 - bb[1]), d, font=f, fill=(15, 15, 15, 255))
    return np.array(im)


def main():
    n_total = int(round(T_END * FPS))
    enc = tk.encoder(OUT, os.path.join(ROOT, "quiz", "audio.wav"), T_END)
    title = tk.text_sprite(["ERKENNST DU IHN", "AM JUBEL?"], size=92, max_w=900, line_gap=0.05)
    names = [tk.text_sprite(r[6], size=78, fill=(15, 15, 15), box=tk.YELLOW, pad=20, max_w=880) for r in ROUNDS]
    cds = {d: countdown_sprite(d) for d in "321"}
    end1 = tk.text_sprite("WIE VIELE HATTEST DU?", size=74, max_w=880)
    end2 = tk.text_sprite("SCHREIB'S IN DIE KOMMENTARE", size=46, fill=tk.YELLOW, max_w=880)

    frames = []
    for i, (src, a, b, kf, cy, h, name, pre) in enumerate(ROUNDS):
        r0, rv, r1 = RT[i]
        n = int(round(r1 * FPS)) - int(round(r0 * FPS))
        kw = dict(interp=True)
        if pre:
            kw.update(pre=pre[0], sw=pre[1], sh=pre[2])
        fr = tk.read_clip(os.path.join(SRC, f"{src}.mp4"), a, b, n, **kw)
        speed = (b - a) / (n / FPS)
        for k, f in enumerate(fr):
            ts = a + k / FPS * speed
            cx = float(np.interp(ts, [p[0] for p in kf], [p[1] for p in kf]))
            w = h * 4 / 3
            sw = f.shape[1]
            x0 = min(max(cx - w / 2, 0), sw - w)
            frames.append((i, f, (x0, cy - h / 2, w, h)))
    assert len(frames) == n_total, (len(frames), n_total)

    for fi, (i, f, rect) in enumerate(frames):
        t = fi / FPS
        r0, rv, r1 = RT[i]
        win = tk.grade(tk.warp_crop(f, rect, VW, VH))
        revealed = t >= rv
        if not revealed:
            p = (t - r0) / (rv - r0)
            block = int(round(64 - 38 * p))          # 64 px -> 26 px blocks, still unreadable
            win = pixelate(win, block)
        img = background(win)
        img[VY:VY + VH] = win
        cv2.rectangle(img, (0, VY - 6), (W, VY), (0, 214, 255), -1)
        cv2.rectangle(img, (0, VY + VH), (W, VY + VH + 6), (0, 214, 255), -1)

        tk.paste(img, title, W / 2, 255)
        # progress pills  ● ● ○ ○ ○
        for j in range(len(ROUNDS)):
            x = W / 2 + (j - 2) * 64
            col = (0, 214, 255) if j < i or (j == i and revealed) else ((255, 255, 255) if j == i else (90, 90, 90))
            cv2.circle(img, (int(x), VY + VH + 70), 17 if j == i else 13, col, -1, cv2.LINE_AA)
        tk.paste(img, tk.text_sprite(f"{i + 1}/{len(ROUNDS)}", size=44), 150, VY + VH + 70)

        if not revealed:
            k = min(2, int((t - r0) / ((rv - r0) / 3)))
            d = "321"[k]
            tk_age = (t - (r0 + k * (rv - r0) / 3)) * FPS
            tk.paste(img, cds[d], W / 2, VY + VH / 2, scale=tk.pop(tk_age, 4, 0.25), alpha=0.92)
        else:
            age = (t - rv) * FPS
            tk.paste(img, names[i], W / 2, VY + VH + 175, scale=tk.pop(age, 5, 0.3))
            if i == len(ROUNDS) - 1 and t >= rv + 2 * BEAT:
                a2 = (t - rv - 2 * BEAT) * FPS
                tk.paste(img, end1, W / 2, VY + 120, scale=tk.pop(a2, 5))
                tk.paste(img, end2, W / 2, VY + 200, scale=tk.pop(a2 - 4, 5))
        fl = 0.8 * math.exp(-(t - rv) * FPS / 2.2) if revealed else 0.0
        img = tk.flash(img, min(1, fl))
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    print("frames", n_total, "dur", round(T_END, 3))


def make_audio():
    m = tk.Mix(T_END)
    m.beat(0.0, T_END, 1 / BEAT * 60, "hiphop", g=0.7, bass_notes=(55, 55, 49, 49, 65.4, 61.7))
    for (r0, rv, r1) in RT:
        for k in range(3):
            m.add(tk.tick(0.75), r0 + k * (rv - r0) / 3)
        m.add(tk.whoosh(0.35, 0.45), rv - 0.33)
        m.add(tk.ding(0.6), rv)
        m.add(tk.impact(0.55), rv)
    m.write(os.path.join(ROOT, "quiz", "audio.wav"))


if __name__ == "__main__":
    make_audio()
    main()
