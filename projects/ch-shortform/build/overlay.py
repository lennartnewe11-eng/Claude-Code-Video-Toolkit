#!/usr/bin/env python3
"""Vektor-Overlay im Stil der Referenzen: cyanfarbene Wireframes ueber dem
Material, technische Annotationen, Momente in denen nur noch die Linien auf
Schwarz stehen, dazu Scanlines, duenne Linealstriche und horizontale
Glitch-Schlieren.

Die Knoten werden aus dem Bild selbst gewonnen (Gradientenmaximum je
Rasterzelle) und auf jedem Beat neu gesetzt. Dadurch sitzt das Neuzeichnen
per Konstruktion exakt auf der Musik -- nichts muss von Hand getimt werden.
"""
import os, math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

FPS, BEAT = 60, 0.3715
CYAN   = (56, 232, 222)
CYAN_D = (24, 148, 146)
ORANGE = (232, 92, 40)
PAPER  = (226, 226, 222)
FONT_M = "/usr/local/share/fonts/ch/Inter-Medium.ttf"

def nodes_from(img, n=26, grid=7):
    """Markante Punkte: staerkster Gradient je Rasterzelle, gleichmaessig verteilt."""
    g = np.asarray(img.convert("L"), dtype=np.float32)
    gx = ndimage.sobel(g, axis=1); gy = ndimage.sobel(g, axis=0)
    mag = np.hypot(gx, gy)
    H, W = mag.shape
    pts = []
    for j in range(grid):
        for i in range(grid):
            y0, y1 = j*H//grid, (j+1)*H//grid
            x0, x1 = i*W//grid, (i+1)*W//grid
            sub = mag[y0:y1, x0:x1]
            if sub.size == 0: continue
            k = int(np.argmax(sub)); yy, xx = divmod(k, sub.shape[1])
            pts.append((x0+xx, y0+yy, float(sub[yy, xx])))
    pts.sort(key=lambda p: -p[2])
    return [(p[0], p[1]) for p in pts[:n]]

def edges_between(pts, rnd, near=3, far=4):
    """Nachbarschaftsnetz plus ein paar weite Spannen -- das Geruest-Gefuehl."""
    E = set()
    for i, a in enumerate(pts):
        d = sorted(((math.dist(a, b), j) for j, b in enumerate(pts) if j != i))
        for _, j in d[:near]:
            E.add((min(i, j), max(i, j)))
    for _ in range(far):
        i, j = rnd.randrange(len(pts)), rnd.randrange(len(pts))
        if i != j: E.add((min(i, j), max(i, j)))
    return sorted(E)

def label_text(rnd):
    return rnd.choice([
        f"{rnd.randrange(10,99)}.{rnd.randrange(100,999)}",
        f"N{rnd.randrange(100,999)}",
        f"Δ{rnd.randrange(10,99)}ms",
        f"{rnd.randrange(1,9)}.{rnd.randrange(10,99)}s",
        f"TRK-{rnd.randrange(10,99)}",
    ])

def glitch_rows(arr, rnd, strength):
    """Horizontale Bandverschiebung -- die Schlieren aus der Standbild-Referenz."""
    if strength <= 0: return arr
    H, W = arr.shape[:2]
    out = arr.copy()
    for _ in range(int(3 + strength*9)):
        h = rnd.randrange(2, max(3, int(H*0.045)))
        y = rnd.randrange(0, max(1, H-h))
        dx = int(rnd.uniform(-1, 1) * W * 0.09 * strength)
        out[y:y+h] = np.roll(arr[y:y+h], dx, axis=1)
    return out

def render(src, dst, dur, W=1080, H=1920, ss=0.0, solo=False,
           glitch=0.0, scan=True, rules=True, seed=1, speed=1.0):
    """src=None -> reines Wireframe auf Schwarz (solo)."""
    n = round(dur * FPS)
    tmp = dst + "_frames"; os.makedirs(tmp, exist_ok=True)

    if src:
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
            "-ss",f"{ss:.3f}","-i",src,
            "-vf",(f"fps={FPS},setpts=PTS/{speed},"
                   f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"),
            "-frames:v",str(n),os.path.join(tmp,"s%04d.png")],check=True)

    rnd = random.Random(seed)
    f_lbl = ImageFont.truetype(FONT_M, 23)
    pts, E, labels = [], [], []
    last_beat = -1

    for i in range(n):
        t = i / FPS
        beat = int(t / BEAT)
        sp = os.path.join(tmp, f"s{i+1:04d}.png")
        base = Image.open(sp).convert("RGB") if (src and os.path.exists(sp)) \
               else Image.new("RGB", (W, H), (0, 0, 0))

        if beat != last_beat:                      # auf jedem Beat neu setzen
            last_beat = beat
            ref = base if src else None
            # flache Baender brauchen weniger Knoten, sonst wird es Brei
            nn = 26 if H > W*0.9 else (18 if H > W*0.4 else 12)
            gg = 7 if H > W*0.9 else (6 if H > W*0.4 else 5)
            pts = nodes_from(ref, n=nn, grid=gg) if ref is not None else \
                  [(rnd.randrange(W), rnd.randrange(H)) for _ in range(nn)]
            E = edges_between(pts, rnd)
            labels = [(k, label_text(rnd)) for k in
                      rnd.sample(range(len(pts)), min(6, len(pts)))]

        arr = np.asarray(base).copy()
        if glitch > 0:
            phase = (t / BEAT) % 1.0
            arr = glitch_rows(arr, rnd, glitch * max(0.0, 1.0 - phase*2.2))
        im = Image.fromarray(arr)
        if solo:
            im = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(im, "RGBA")

        drift = math.sin(t*5.0) * 3
        P = [(x + drift*math.cos(k), y + drift*math.sin(k*1.7))
             for k, (x, y) in enumerate(pts)]

        for a, b in E:                       # dunkler Unterzug -> liest auch auf Hellem
            d.line([P[a], P[b]], fill=(0, 0, 0, 90), width=4)
        for a, b in E:
            d.line([P[a], P[b]], fill=CYAN + (215 if solo else 185,), width=2)
        for x, y in P:
            d.rectangle([x-4, y-4, x+4, y+4], outline=CYAN + (245,), width=2)
        for k, txt in labels:
            x, y = P[k]
            d.line([x+5, y-5, x+22, y-20], fill=CYAN_D + (210,), width=2)
            d.text((x+25, y-34), txt, font=f_lbl, fill=(0, 0, 0, 150))
            d.text((x+24, y-35), txt, font=f_lbl, fill=CYAN + (240,))

        if scan:
            for y in range(0, H, 3):
                d.line([0, y, W, y], fill=(0, 0, 0, 30), width=1)
        if rules:
            for frac, col in ((0.26, ORANGE), (0.74, ORANGE), (0.5, PAPER)):
                yy = int(H*frac)
                d.line([0, yy, W, yy], fill=col + (120,), width=1)

        im.save(os.path.join(tmp, f"o{i:04d}.png"))

    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate",str(FPS),"-i",os.path.join(tmp,"o%04d.png"),
        "-c:v","libx264","-crf","13","-preset","fast","-pix_fmt","yuv420p",dst],check=True)
    subprocess.run(["rm","-rf",tmp])
    return dst

if __name__ == "__main__":
    a = sys.argv[1:]
    render(a[0] if a[0] != "-" else None, a[1], float(a[2]),
           ss=float(a[3]) if len(a) > 3 else 0.0,
           solo=(len(a) > 4 and a[4] == "solo"),
           glitch=float(a[5]) if len(a) > 5 else 0.0)
