#!/usr/bin/env python3
"""Generiert die Handy-Grafiken vor weissem Hintergrund.

Alle Geraete sitzen auf exakt demselben Mittelpunkt und im echten
Groessenverhaeltnis zueinander (Massstab in px pro mm). Deshalb generiert
statt gesucht: Produktfotos haetten je eigene Perspektive, Beleuchtung
und Skalierung -- dann traegt der Groessenvergleich nicht mehr.

Masse sind die Herstellerangaben (Hoehe x Breite in mm).
"""
import os
from PIL import Image, ImageDraw, ImageFont

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST  = os.path.join(PROJ, "assets", "generated")
FONT = "/usr/local/share/fonts/ch/InterDisplay-Black.ttf"
FONT_M = "/usr/local/share/fonts/ch/Inter-Medium.ttf"

BW, BH = 1080, 1440        # das weisse Band (portrait)
SS     = 3                 # Supersampling fuer saubere Kanten
CX, CY = BW // 2, 700      # gemeinsamer Mittelpunkt ALLER Geraete

WHITE  = (255, 255, 255)
BODY   = (26, 26, 28)
SCREEN = (233, 236, 240)
GHOST  = (203, 206, 211)
LABEL  = (17, 17, 19)
SUB    = (126, 130, 137)

# name, jahr, hoehe_mm, breite_mm, zoll, eckradius_mm, rahmen_mm, home-button, notch
PHONES = [
    ("iPhone",             2007, 115.0, 61.0, 3.5,  9.0, 7.0,  True,  False),
    ("iPhone 5",           2012, 123.8, 58.6, 4.0,  7.0, 5.5,  True,  False),
    ("iPhone 6",           2014, 138.1, 67.0, 4.7,  9.0, 6.5,  True,  False),
    ("iPhone 6 Plus",      2014, 158.1, 77.8, 5.5, 10.0, 7.0,  True,  False),
    ("iPhone X",           2017, 143.6, 70.9, 5.8, 12.0, 2.6,  False, True),
    ("iPhone 11 Pro Max",  2019, 158.0, 77.8, 6.5, 12.5, 2.8,  False, True),
    ("iPhone 12 Pro Max",  2020, 160.8, 78.1, 6.7, 13.0, 2.4,  False, True),
    ("iPhone 16 Pro Max",  2024, 163.0, 77.6, 6.9, 14.0, 1.6,  False, True),
]

PX_PER_MM = 1000.0 / max(p[2] for p in PHONES)   # groesstes Geraet = 1000px hoch

def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def draw_phone(d, h_mm, w_mm, rad_mm, bez_mm, home, notch, s,
               fill=BODY, outline=None, width=0, screen=True):
    h, w = h_mm * PX_PER_MM * s, w_mm * PX_PER_MM * s
    r    = rad_mm * PX_PER_MM * s
    cx, cy = CX * s, CY * s
    box = [cx - w/2, cy - h/2, cx + w/2, cy + h/2]
    rr(d, box, r, fill=fill, outline=outline, width=width)
    if not screen: return
    b = bez_mm * PX_PER_MM * s
    top = b + (home and 11 * PX_PER_MM * s or 0)   # Kinn/Stirn bei Home-Button-Geraeten
    sbox = [box[0]+b, box[1]+ (11*PX_PER_MM*s if home else b),
            box[2]-b, box[3]- (13*PX_PER_MM*s if home else b)]
    rr(d, sbox, max(2, r - b*0.8), fill=SCREEN)
    if home:
        hr = 5.5 * PX_PER_MM * s
        hy = box[3] - 7.0 * PX_PER_MM * s
        d.ellipse([cx-hr, hy-hr, cx+hr, hy+hr], outline=(70,72,78), width=max(1,int(2*s)))
    if notch:
        nw, nh = 26 * PX_PER_MM * s, 6.5 * PX_PER_MM * s
        ny = sbox[1]
        rr(d, [cx-nw/2, ny-nh*0.1, cx+nw/2, ny+nh], nh/2, fill=BODY)

def render(name, year, h_mm, w_mm, inch, rad, bez, home, notch,
           ghosts=None, out=None):
    im = Image.new("RGB", (BW*SS, BH*SS), WHITE)
    d  = ImageDraw.Draw(im)
    draw_phone(d, h_mm, w_mm, rad, bez, home, notch, SS, screen=not ghosts)
    # Umrisse der aelteren Generationen OBEN DRAUF -- darunter waeren sie
    # vom groesseren Geraet vollstaendig verdeckt (alle teilen den Mittelpunkt)
    for g in (ghosts or []):
        draw_phone(d, g[2], g[3], g[5], g[6], g[7], g[8], SS,
                   fill=None, outline=WHITE, width=max(2, int(1.8*SS)), screen=False)
        gh, gw = g[2]*PX_PER_MM*SS, g[3]*PX_PER_MM*SS
        fy = ImageFont.truetype(FONT_M, int(30*SS))
        d.text((CX*SS - gw/2 + int(16*SS), CY*SS - gh/2 + int(12*SS)),
               str(g[1]), font=fy, fill=WHITE)

    f_big = ImageFont.truetype(FONT,   int(58*SS))
    f_sub = ImageFont.truetype(FONT_M, int(34*SS))
    ty = int(1268*SS)
    for txt, fnt, col, dy in ((name, f_big, LABEL, 0),
                              (f"{year}   ·   {inch}″   ·   "
                               f"{h_mm:.0f} × {w_mm:.0f} mm", f_sub, SUB, int(74*SS))):
        bb = d.textbbox((0,0), txt, font=fnt)
        d.text(((BW*SS - (bb[2]-bb[0]))/2 - bb[0], ty+dy), txt, font=fnt, fill=col)

    im = im.resize((BW, BH), Image.LANCZOS)
    im.save(out, quality=97)
    return out

def main():
    os.makedirs(DST, exist_ok=True)
    made = []
    for i, p in enumerate(PHONES):
        out = os.path.join(DST, f"phone_{i:02d}.png")
        render(*p, out=out)
        made.append(out)
        print(f"  {p[0]:20s} {p[2]:6.1f}×{p[3]:5.1f}mm -> "
              f"{p[2]*PX_PER_MM:.0f}×{p[3]*PX_PER_MM:.0f}px")
    # Schlussbild: alle Generationen als Umriss hinter dem groessten Geraet
    out = os.path.join(DST, "phone_all.png")
    render(*PHONES[-1], ghosts=[PHONES[0]], out=out)
    made.append(out)
    print(f"  Schlussbild: 2024 mit Umriss von 2007 -> {out}")
    print(f"\nMassstab: {PX_PER_MM:.3f} px/mm  ·  gemeinsamer Mittelpunkt ({CX}, {CY})")
    return made

if __name__ == "__main__":
    main()
