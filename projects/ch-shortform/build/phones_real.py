#!/usr/bin/env python3
"""Stellt echte Geraete aus Apples Produktbildern frei und zentriert sie.

Jedes Quellbild zeigt mehrere Rueckseiten-Varianten, EIN frontales Geraet mit
leuchtendem Display und eine schmale Seitenansicht. Das frontale Geraet wird
ueber sein Display gefunden: es ist die einzige grosse, farbige Flaeche im Bild.

Daraus ergibt sich alles Weitere von selbst:
  - Mitte-x des Displays  = Mitte-x des Geraets (bei jedem iPhone mittig)
  - Maskenausdehnung dort = Ober- und Unterkante des Geraets
  - Breite                = Hoehe * (Breite_mm / Hoehe_mm), also aus den echten Massen
Freigestellt wird mit einer abgerundeten Rechteckmaske im echten Eckradius --
so schneidet nichts vom Nachbargeraet mit hinein.

Skaliert wird ueber die Hoehe in Millimetern, nicht ueber die Bildhoehe.
Deshalb bleibt der Groessenvergleich gueltig.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(PROJ, "assets", "phones_raw")
DST  = os.path.join(PROJ, "assets", "generated")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phones import (PHONES, PX_PER_MM, BW, BH, CX, CY, SS,
                    WHITE, LABEL, SUB, FONT, FONT_M)

# Quelldatei je Modell (Apple Support, "iPhone-Modell identifizieren")
# Quelldatei und Mitte-x der Frontansicht im Quellbild.
# Die Mitte ist fest eingetragen, nicht erkannt: die farbigen Rueckseiten der
# Pro-Max-Bilder sind ebenfalls stark gesaettigt, dadurch findet auch eine
# Komponentenanalyse bei vier von acht Bildern die falsche Flaeche. Abgelesen
# am Raster (build/contact_sheet-Prinzip, siehe docs). Die Automatik laeuft als
# Gegenprobe weiter und meldet grosse Abweichungen.
SRC = {
    "iPhone":            ("a_2007.jpg",  177),
    "iPhone 5":          ("a_2012.jpg",  400),
    "iPhone 6":          ("a_2014.jpg",  502),
    "iPhone 6 Plus":     ("a_2014p.jpg", 579),
    "iPhone X":          ("a_2017.jpg",  350),
    "iPhone 11 Pro Max": ("a_2019.jpg",  690),
    "iPhone 12 Pro Max": ("a_2020.jpg",  589),
    "iPhone 16 Pro Max": ("a_2024.png",  735),
}

def masks(im):
    a = np.array(im)
    rgb = a[..., :3].astype(int)
    if a[..., 3].min() < 250:
        fg = a[..., 3] > 40
    else:
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        fg = (rgb.min(axis=2) < 236) | (sat > 12)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    val = rgb.max(axis=2)
    screen = (sat > 55) & (val > 70) & fg        # leuchtendes Display
    return fg, screen

def largest_blob(m):
    """Groesste zusammenhaengende Flaeche.

    Eine Schwellwertsuche ueber Spalten- und Zeilensummen reicht hier nicht:
    bei den Pro-Max-Bildern sind auch die farbigen Rueckseiten gesaettigt und
    ziehen die Mitte nach links. Echte Komponentenanalyse trennt das Display
    der Frontansicht sauber ab.
    """
    from scipy import ndimage
    lab, n = ndimage.label(m)
    if n == 0: return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    k = int(np.argmax(sizes)) + 1
    ys, xs = np.where(lab == k)
    return xs.min(), xs.max(), ys.min(), ys.max()

def extract(path, h_mm, w_mm, rad_mm, cx):
    im = Image.open(path).convert("RGBA")
    fg, screen = masks(im)
    b = largest_blob(screen)
    if b is not None:
        auto = (b[0] + b[1]) / 2.0
        if abs(auto - cx) > 40:
            print(f"      (Automatik haette {auto:.0f} statt {cx} gewaehlt — "
                  f"feste Mitte gilt)")

    # Ober-/Unterkante aus der Maske in den Display-Spalten
    band = fg[:, max(0, int(cx) - 6): int(cx) + 7]
    rows = np.where(band.any(axis=1))[0]
    top, bot = int(rows[0]), int(rows[-1])
    H = bot - top + 1
    W = H * (w_mm / h_mm)

    box = (int(round(cx - W / 2)), top, int(round(cx + W / 2)), bot + 1)
    dev = im.crop(box).convert("RGBA")

    # Freistellen mit dem echten Eckradius, 4x ueberabgetastet fuer weiche Kanten
    r = max(1, int(round(rad_mm / h_mm * dev.height)))
    inset = 2
    m = Image.new("L", (dev.width * 4, dev.height * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [inset * 4, inset * 4, dev.width * 4 - 1 - inset * 4, dev.height * 4 - 1 - inset * 4],
        radius=r * 4, fill=255)
    dev.putalpha(m.resize(dev.size, Image.LANCZOS))
    return dev, box, H

def render(name, year, h_mm, w_mm, inch, rad, bez, home, notch, out, ghost=None):
    fn, cx = SRC[name]
    dev, box, H = extract(os.path.join(RAW, fn), h_mm, w_mm, rad, cx)
    target_h = int(round(h_mm * PX_PER_MM))
    target_w = int(round(w_mm * PX_PER_MM))
    dev = dev.resize((target_w, target_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (BW, BH), WHITE + (255,))
    canvas.alpha_composite(dev, (CX - target_w // 2, CY - target_h // 2))

    d = ImageDraw.Draw(canvas)
    if ghost:                      # Umriss einer aelteren Generation oben drauf
        gn, gy, gh, gw, _, grad, *_ = ghost
        h2, w2 = gh * PX_PER_MM, gw * PX_PER_MM
        r2 = grad * PX_PER_MM
        d.rounded_rectangle([CX - w2/2, CY - h2/2, CX + w2/2, CY + h2/2],
                            radius=r2, outline=(255, 255, 255, 235), width=3)
        d.text((CX - w2/2 + 16, CY - h2/2 + 12), str(gy),
               font=ImageFont.truetype(FONT_M, 30), fill=(255, 255, 255, 235))
    f_big = ImageFont.truetype(FONT, 58)
    f_sub = ImageFont.truetype(FONT_M, 34)
    for txt, fnt, col, dy in ((name, f_big, LABEL, 0),
                              (f"{year}   ·   {inch}″   ·   {h_mm:.0f} × {w_mm:.0f} mm",
                               f_sub, SUB, 74)):
        bb = d.textbbox((0, 0), txt, font=fnt)
        d.text(((BW - (bb[2] - bb[0])) / 2 - bb[0], 1268 + dy), txt, font=fnt, fill=col)

    canvas.convert("RGB").save(out, quality=97)
    return box, H, target_h

def main():
    os.makedirs(DST, exist_ok=True)
    for i, p in enumerate(PHONES):
        out = os.path.join(DST, f"real_{i:02d}.png")
        box, H, th = render(*p, out=out)
        print(f"  {p[0]:20s} Quellbox {str(box):22s} Hoehe {H:4d}px -> {th:4d}px "
              f"({p[2]:.1f}mm)")
    # Schlussbild: neuestes Geraet mit dem Umriss des Ur-iPhone
    out = os.path.join(DST, "real_all.png")
    render(*PHONES[-1], out=out, ghost=PHONES[0])
    print(f"  Schlussbild 2024 mit Umriss 2007 -> {out}")
    print(f"\nMassstab {PX_PER_MM:.3f} px/mm  ·  Mittelpunkt ({CX}, {CY})")

if __name__ == "__main__":
    main()
