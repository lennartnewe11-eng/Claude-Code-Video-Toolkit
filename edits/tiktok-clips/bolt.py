#!/usr/bin/env python3
"""Clip 1 – "9,58 in Echtzeit": Usain Bolt's 100 m world record with a live clock, live km/h and
distance, built for completion rate + rewatches + comments.  9:16, 1080x1920, ~14.3 s, loops.
"""
import os, sys, math
import numpy as np
import cv2
from scipy.interpolate import PchipInterpolator
import tk

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CLIPS_MEDIA", os.path.join(HERE, "media"))   # footage lives outside git
SRC = os.path.join(ROOT, "bolt", "src")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "bolt", "out", "bolt_958_echtzeit.mp4")
W, H, FPS = tk.W, tk.H, tk.FPS
VW, VH, VY = 1080, 608, 600                    # 16:9 video window

# ---- race data: Berlin 2009. Speed profile (m/s) through 0.146 s reaction, peak 12.42 m/s (44.7 km/h)
# around 60–70 m, slight fade to the line; distance is the integral, scaled to hit 100 m at 9.58 s
# (matches the official 10 m splits within ~0.5 m).
_KT = [0, 0.146, 0.6, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 6.7, 7.5, 8.5, 9.58]
_KV = [0, 0, 4.2, 6.4, 8.3, 9.6, 10.5, 11.1, 11.5, 11.75, 12.1, 12.35, 12.42, 12.3, 12.1, 12.0]
SPEED = PchipInterpolator(_KT, _KV)
_DR = SPEED.antiderivative()
_DS = 100 / float(_DR(9.58))


def dist(t):
    return float(_DR(t)) * _DS


# ---- edit (output seconds)
GUN_SRC = 3.32                                   # starter's gun in timer.mp4
SEG = [  # (out_in, out_out, file, src_in, src_out, crop(x,y,w,h) or keyframes, interp)
    (0.00, 0.60, "timer", 2.35, 2.95, (0, 0, 1920, 1080), False),          # the stare into the camera
    (0.60, 10.47, "timer", 3.00, 12.87, "race", False),                      # 9.58 s, real time
    (10.47, 11.47, "race164", 144.00, 145.00, (480, 180, 1280, 720), False),  # stadium clock 9.58
    (11.47, 12.47, "race164", 140.45, 141.30, (290, 95, 1240, 698), True),    # arms up
    (12.47, 14.30, "timer", 9.40, 10.05, "race_fast", True),                 # top-speed phase, slow-mo
]
T_END = 14.30
GUN_OUT = 0.60 + (GUN_SRC - 3.00)                # 0.92 s
FIN_OUT = 10.47


def race_rect(t_src):
    x = np.interp(t_src, [3.0, 4.6, 6.0, 12.9], [258, 300, 516, 516])
    return (x, 0, 1404, 790)                    # y ≤ 790 keeps the source's timer box out


def window(img, rect, zoom=1.0):
    return tk.warp_crop(img, rect, VW, VH, zoom)


def background(win):
    small = cv2.resize(win, (VW // 6, VH // 6))
    bw = int(VH / 6 * W / H)
    x0 = (small.shape[1] - bw) // 2
    bg = cv2.resize(small[:, x0:x0 + bw], (W, H), interpolation=cv2.INTER_LINEAR)
    bg = cv2.GaussianBlur(bg, (0, 0), 18)
    return (bg.astype(np.float32) * 0.32).astype(np.uint8)


# ---- fixed-width clock sprites
_digit_cache = {}


def clock_sprite(text, size=190, color=tk.WHITE):
    key = (text, size, color)
    if key in _digit_cache:
        return _digit_cache[key]
    f = tk.font(size)
    adv = int(f.getbbox("0")[2] * 1.02)
    comma_adv = int(adv * 0.42)
    widths = [comma_adv if c in ",." else adv if c.isdigit() else int((f.getbbox(c)[2] - f.getbbox(c)[0]) * 1.08)
              for c in text]
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (sum(widths) + 60, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 30
    for c, w in zip(text, widths):
        bb = f.getbbox(c)
        d.text((x + (w - (bb[2] - bb[0])) / 2 - bb[0], 10), c, font=f, fill=color + (255,),
               stroke_width=10, stroke_fill=(0, 0, 0, 255))
        x += w
    arr = np.array(im)
    _digit_cache[key] = arr
    return arr


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def main():
    n_total = int(round(T_END * FPS))
    enc = tk.encoder(OUT, os.path.join(ROOT, "bolt", "audio.wav"), T_END)
    title = tk.text_sprite("WELTREKORD IN ECHTZEIT", size=70, max_w=900)
    sub = tk.text_sprite("USAIN BOLT  ·  BERLIN 2009", size=42, fill=tk.YELLOW, max_w=900)
    kmh_lbl = tk.text_sprite("KM/H", size=46, fill=tk.YELLOW)
    wr = tk.text_sprite("WELTREKORD", size=96, fill=(20, 20, 20), box=tk.YELLOW, pad=22)
    top_lbl = tk.text_sprite("TOPSPEED", size=58, fill=tk.YELLOW)
    top_val = tk.text_sprite("44,72 KM/H", size=118)
    q1 = tk.text_sprite(["WIE WEIT KÄMST DU", "IN 9,58 SEKUNDEN?"], size=64, max_w=860)

    frames = []
    for (o0, o1, src, a, b, crop, interp) in SEG:
        n = int(round(o1 * FPS)) - int(round(o0 * FPS))
        fr = tk.read_clip(os.path.join(SRC, f"{src}.mp4"), a, b, n, interp=interp)
        speed = (b - a) / (n / FPS)
        for k, f in enumerate(fr):
            t_src = a + k / FPS * speed
            if crop == "race":
                rect = race_rect(t_src)
            elif crop == "race_fast":
                rect = (516, 0, 1404, 790)
            else:
                rect = crop
            frames.append((f, rect, o0))
    assert len(frames) == n_total, (len(frames), n_total)

    for i, (f, rect, seg_in) in enumerate(frames):
        t = i / FPS
        zoom = 1.0
        if t >= FIN_OUT:
            zoom = 1.0 + 0.06 * math.exp(-(t - FIN_OUT) * 6)
        if t >= 12.47:
            zoom = 1.0 + 0.05 * (t - 12.47) / (T_END - 12.47)
        win = tk.grade(window(f, rect, zoom))
        img = background(win)
        img[VY:VY + VH] = win
        cv2.rectangle(img, (0, VY - 4), (W, VY), (0, 214, 255), -1)
        cv2.rectangle(img, (0, VY + VH), (W, VY + VH + 4), (0, 214, 255), -1)

        tk.paste(img, title, W / 2, 222)
        tk.paste(img, sub, W / 2, 300)

        # clock
        rt = min(9.58, max(0.0, t - GUN_OUT))
        fin = t >= FIN_OUT - 0.5 / FPS
        if fin:
            rt = 9.58
        col = tk.YELLOW if fin else tk.WHITE
        sc = tk.pop((t - FIN_OUT) * FPS, dur=6, amount=0.22) if fin else 1.0
        tk.paste(img, clock_sprite(de(rt) + "s", 190, col), W / 2, 470, scale=sc)

        # live stats during the race
        if t < FIN_OUT:
            v = float(SPEED(rt)) * 3.6 if rt > 0 else 0.0
            d = dist(rt) if rt > 0 else 0.0
            tk.paste(img, clock_sprite(de(v, 1), 132, tk.WHITE), 420, 1320)
            tk.paste(img, kmh_lbl, 760, 1342)
            x0, x1, yb = 90, 870, 1460
            cv2.line(img, (x0, yb), (x1, yb), (90, 90, 90), 10, cv2.LINE_AA)
            xm = int(x0 + (x1 - x0) * d / 100)
            cv2.line(img, (x0, yb), (xm, yb), (0, 214, 255), 10, cv2.LINE_AA)
            cv2.circle(img, (xm, yb), 17, (0, 214, 255), -1, cv2.LINE_AA)
            cv2.circle(img, (xm, yb), 17, (0, 0, 0), 3, cv2.LINE_AA)
            tk.paste(img, clock_sprite(f"{int(d)}m", 54, tk.WHITE), x0 + 40, yb + 62)
            tk.paste(img, clock_sprite("100m", 54, (170, 170, 170)), x1 - 40, yb + 62)
        elif t < 12.47:
            tk.paste(img, wr, W / 2, 1330, scale=tk.pop((t - FIN_OUT) * FPS, dur=5, amount=0.3))
        else:
            age = (t - 12.47) * FPS
            tk.paste(img, top_lbl, W / 2, 1270, scale=tk.pop(age, 5))
            tk.paste(img, top_val, W / 2, 1365, scale=tk.pop(age - 3, 5))
            tk.paste(img, q1, W / 2, 1505, scale=tk.pop(age - 12, 5))

        # gun flash + finish flash
        fl = 0.0
        if t >= GUN_OUT:
            fl += 0.35 * math.exp(-(t - GUN_OUT) * FPS / 2)
        if t >= FIN_OUT:
            fl += 0.85 * math.exp(-(t - FIN_OUT) * FPS / 2.5)
        img = tk.flash(img, min(1, fl))
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    print("frames", n_total, "dur", T_END)


def make_audio():
    m = tk.Mix(T_END)
    m.add(tk.heartbeat(0.9), 0.02)
    m.add(tk.heartbeat(0.6), 0.30)
    m.add(tk.riser(0.6, 0.25), GUN_OUT - 0.6)
    gun = tk._hp(tk._noise(0.35, 11), 1200) * np.exp(-tk._t(0.35) / 0.03) * 1.1
    m.add(gun, GUN_OUT)
    m.add(tk.impact(0.7), GUN_OUT)
    m.beat(GUN_OUT, FIN_OUT, 136, "trap", g=0.9, bass_notes=(49, 49, 55, 58.3))
    for s in range(1, 10):                       # tick on every full race second
        m.add(tk.tick(0.5), GUN_OUT + s)
    m.add(tk.riser(1.6, 0.4), FIN_OUT - 1.6)
    m.add(tk.impact(1.1), FIN_OUT)
    m.add(tk.ding(0.55), FIN_OUT + 0.02)
    m.add(tk.whoosh(0.4, 0.5), 12.47 - 0.3)
    m.beat(FIN_OUT + 0.44, T_END, 136, "hiphop", g=0.75, bass_notes=(49, 55))
    m.write(os.path.join(ROOT, "bolt", "audio.wav"))


if __name__ == "__main__":
    make_audio()
    main()
