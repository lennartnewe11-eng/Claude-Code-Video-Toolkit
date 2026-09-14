#!/usr/bin/env python3
"""Der Schlussshot des Groessenvergleichs, gezeichnet wie zuvor -- aber das
Display scrollt. Der Feed rastet pro Beat eine Karte weiter, dadurch sitzt
die Bewegung exakt auf der Musik und leitet in den Scroll-Abschnitt ueber.
"""
import os, subprocess, sys, math, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from phones import (PHONES, PX_PER_MM, BW, BH, CX, CY,
                    WHITE, BODY, SCREEN, GHOST, LABEL, SUB, FONT, FONT_M)

FPS, BEAT = 60, 0.3715
SS = 2

def feed_cards(n=40, seed=7):
    """Karten fuer den Feed: wechselnde Hoehen, damit es nicht gerastert wirkt."""
    r = random.Random(seed)
    return [r.choice([54, 78, 96, 120, 150]) for _ in range(n)]

def render_frame(i, nframes, cards, out):
    dev = PHONES[-1]; ghost = PHONES[0]
    _, year, h_mm, w_mm, inch, rad, bez, _, _ = dev
    im = Image.new("RGB", (BW*SS, BH*SS), WHITE)
    d = ImageDraw.Draw(im)

    h, w = h_mm*PX_PER_MM*SS, w_mm*PX_PER_MM*SS
    r = rad*PX_PER_MM*SS
    cx, cy = CX*SS, CY*SS
    box = [cx-w/2, cy-h/2, cx+w/2, cy+h/2]
    d.rounded_rectangle(box, radius=r, fill=BODY)

    # Displayflaeche
    b = bez*PX_PER_MM*SS
    sb = [box[0]+b, box[1]+b, box[2]-b, box[3]-b]
    sr = max(2, r-b*0.8)
    scr = Image.new("RGB", (int(sb[2]-sb[0]), int(sb[3]-sb[1])), SCREEN)
    sd = ImageDraw.Draw(scr)

    # Feed: pro Beat genau eine Karte weiter, dazwischen kurzes Nachfedern
    t = i / FPS
    beats = t / BEAT
    step = math.floor(beats)
    frac = beats - step
    ease = 1 - pow(1 - min(1.0, frac/0.45), 3)          # schnell rein, sanft aus
    unit = 150 * SS
    off = (step + ease) * unit

    pad = 16*SS
    y = -off % (sum(cards[:6]) * SS + 6*pad)
    y -= unit*2
    k = 0
    while y < scr.height:
        ch = cards[k % len(cards)] * SS
        shade = 188 + (k*37) % 40
        sd.rounded_rectangle([pad, y, scr.width-pad, y+ch],
                             radius=10*SS, fill=(shade, shade+2, shade+6))
        sd.rounded_rectangle([pad+14*SS, y+14*SS, pad+14*SS+26*SS, y+14*SS+26*SS],
                             radius=13*SS, fill=(150,152,158))
        sd.rounded_rectangle([pad+52*SS, y+20*SS, pad+150*SS, y+30*SS],
                             radius=5*SS, fill=(150,152,158))
        y += ch + pad
        k += 1

    mask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,scr.width-1,scr.height-1],
                                           radius=int(sr), fill=255)
    im.paste(scr, (int(sb[0]), int(sb[1])), mask)

    # Dynamic Island
    nw, nh = 26*PX_PER_MM*SS, 6.5*PX_PER_MM*SS
    d.rounded_rectangle([cx-nw/2, sb[1]-nh*0.1, cx+nw/2, sb[1]+nh], nh/2, fill=BODY)

    # Umriss des Ur-iPhone
    gh, gw = ghost[2]*PX_PER_MM*SS, ghost[3]*PX_PER_MM*SS
    d.rounded_rectangle([cx-gw/2, cy-gh/2, cx+gw/2, cy+gh/2],
                        radius=ghost[5]*PX_PER_MM*SS,
                        outline=(255,255,255), width=int(3*SS))
    d.text((cx-gw/2+16*SS, cy-gh/2+12*SS), str(ghost[1]),
           font=ImageFont.truetype(FONT_M, int(30*SS)), fill=(255,255,255))

    f_big = ImageFont.truetype(FONT, int(58*SS))
    f_sub = ImageFont.truetype(FONT_M, int(34*SS))
    for txt, fnt, col, dy in ((dev[0], f_big, LABEL, 0),
                              (f"{year}   ·   {inch}″   ·   {h_mm:.0f} × {w_mm:.0f} mm",
                               f_sub, SUB, int(74*SS))):
        bb = d.textbbox((0,0), txt, font=fnt)
        d.text(((BW*SS-(bb[2]-bb[0]))/2 - bb[0], int(1268*SS)+dy), txt, font=fnt, fill=col)

    im.resize((BW, BH), Image.LANCZOS).save(out, quality=95)

def main(beats=4.0):
    n = round(beats * BEAT * FPS)
    tmp = os.path.join(PROJ, "build", "_phoneanim")
    os.makedirs(tmp, exist_ok=True)
    cards = feed_cards()
    for i in range(n):
        render_frame(i, n, cards, os.path.join(tmp, f"f{i:04d}.jpg"))
    out = os.path.join(PROJ, "assets", "generated", "phone_all_anim.mp4")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate",str(FPS),"-i",os.path.join(tmp,"f%04d.jpg"),
        "-c:v","libx264","-crf","12","-preset","medium","-pix_fmt","yuv420p",out],check=True)
    subprocess.run(["rm","-rf",tmp])
    print(f"{n} Frames ({beats} Beats) -> {out}")

if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 4.0)
