#!/usr/bin/env python3
"""Format-Baender, Grades und Effekte fuer den 9:16-Edit.

Kernidee des Videos: der schwarze 1080x1920-Rahmen bleibt immer stehen,
aber jeder Clip sitzt in einem eigenen Seitenverhaeltnis-Band. Dadurch
wirkt es, als wechsle das Format des Videos selbst.
"""

W, H, FPS = 1080, 1920, 60
SUPER = 2          # interne Ueberaufloesung fuer sauberen Zoom

# ---------------------------------------------------------------- Baender ---
# name: (Breite, Hoehe, Standard-Y-Position)
# 'y' ist die Oberkante; None = vertikal zentriert
BANDS = {
    "strip":    (1080,  360, None),   # 3:1    ultrabreiter Streifen
    "cinema":   (1080,  452, None),   # 2.39:1 Cinemascope
    "wide":     (1080,  608, None),   # 16:9
    "classic":  (1080,  810, None),   # 4:3    Archivformat
    "square":   (1080, 1080, None),   # 1:1
    "portrait": (1080, 1440, None),   # 3:4
    "full":     (1080, 1920, 0),      # 9:16   randlos
    "tv":       ( 824,  618, None),   # 4:3 klein, "alter Fernseher"
    "mini":     ( 640,  480, None),   # 4:3 sehr klein, verloren im Schwarz
    "slab":     (1080,  270, None),   # 4:1  extremer Schlitz
    "half":     (1080,  960, None),   # 9:8  halbe Hoehe
}

def band_rect(name, y=None, x=None):
    bw, bh, dy = BANDS[name]
    by = dy if dy is not None else (H - bh) // 2
    if y == "top":      by = 0
    elif y == "upper":  by = int(H * 0.16)
    elif y == "lower":  by = H - bh - int(H * 0.16)
    elif y == "bottom": by = H - bh
    elif isinstance(y, (int, float)): by = int(y)
    bx = (W - bw) // 2 if x is None else int(x)
    return bx, by, bw, bh

# ----------------------------------------------------------------- Grades ---
GRADES = {
    "neutral":  "",
    # warmes Archivbild, angehobene Schwarzwerte, leichtes Ausbleichen
    "archive":  "curves=r='0/0.06 0.5/0.58 1/0.99':g='0/0.05 0.5/0.54 1/0.97':"
                "b='0/0.10 0.5/0.50 1/0.90',eq=saturation=0.86:contrast=1.02",
    # kraeftig, kontrastreich -- fuer die Raketen/Aufbruch-Bilder
    "punchy":   "eq=saturation=1.28:contrast=1.22:brightness=0.01,"
                "curves=all='0/0 0.25/0.18 0.75/0.84 1/1'",
    # hartes Schwarzweiss
    "bw":       "hue=s=0,eq=contrast=1.28:brightness=0.03,"
                "curves=all='0/0 0.22/0.20 0.78/0.90 1/1'",
    # kalt, entsaettigt -- Vibe Shift / Dystopie
    "cold":     "eq=saturation=0.38:contrast=1.18:brightness=-0.03,"
                "colorbalance=rs=-0.12:gs=-0.02:bs=0.18,"
                "curves=all='0/0.02 0.5/0.44 1/0.90'",
    # fast monochrom, sehr flau -- tiefster Punkt
    "bleak":    "eq=saturation=0.12:contrast=1.05:brightness=-0.06,"
                "colorbalance=rs=-0.06:bs=0.14",
    # warm und offen -- Aufloesung / Zusammenruecken
    "warm":     "eq=saturation=1.15:contrast=1.10,"
                "colorbalance=rs=0.10:gs=0.03:bs=-0.08,"
                "curves=all='0/0.03 0.5/0.53 1/1'",
}

# ------------------------------------------------------- Zoom / Bewegung ---
def zoom_expr(fx, dur):
    """zoompan-z-Ausdruck. 'on' = Ausgabe-Frameindex, T = Zeit in s."""
    t = f"(on/{FPS})"
    parts = []
    if "zoom_in"  in fx: parts.append(f"1.0+0.10*{t}/{dur}")
    if "zoom_out" in fx: parts.append(f"1.10-0.10*{t}/{dur}")
    if "push"     in fx: parts.append(f"1.0+0.22*{t}/{dur}")
    if "punch"    in fx: parts.append(f"1.0+0.085*exp(-{t}/0.11)")
    if "thump"    in fx: parts.append(f"1.0+0.16*exp(-{t}/0.07)")
    if not parts: return "1.0"
    # additiv ueberlagern, Basis 1.0 nicht mehrfach zaehlen
    expr = parts[0]
    for p in parts[1:]:
        expr = f"({expr})+(({p})-1.0)"
    return f"max(1.0,{expr})"

def pan_expr(fx, dur, axis):
    """Versatz in Pixeln zusaetzlich zur Zentrierung."""
    t = f"(on/{FPS})"
    terms = []
    if "shake" in fx:
        terms.append(f"{'14' if axis=='x' else '10'}*sin({t}*{38 if axis=='x' else 31})"
                     f"*exp(-{t}/0.16)")
    if "drift" in fx:
        terms.append(f"{'26' if axis=='x' else '0'}*{t}/{dur}")
    if "sway" in fx:
        terms.append(f"{'18' if axis=='x' else '12'}*sin({t}*{2.1 if axis=='x' else 1.6})")
    return "+".join(terms) if terms else "0"
