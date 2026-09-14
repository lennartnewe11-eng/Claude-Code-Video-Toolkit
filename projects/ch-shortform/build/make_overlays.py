#!/usr/bin/env python3
"""Erzeugt die Overlay-Clips fuer den Scroll-/Isolationsabschnitt.
Jeder Clip wird etwas laenger gerendert als gebraucht -- die EDL schneidet
framegenau zu."""
import os, sys
from concurrent.futures import ThreadPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
PROJ=os.path.dirname(HERE)
import overlay

S=lambda n: os.path.join(PROJ,"assets","stock",n+".mp4")
A=lambda n: os.path.join(PROJ,"assets","source",n+".mp4")
G=lambda n: os.path.join(PROJ,"assets","generated",n+".mp4")

# Jeder Clip wird in der Groesse seines Zielbands gerendert. Sonst verteilt
# sich das Netz ueber 1080x1920 und das Band schneidet fast alles weg --
# in schmalen Baendern bliebe kaum eine Linie stehen.
from looks import band_rect

# key, quelle, dauer, in-punkt, solo?, glitch, seed, zielband
JOBS=[
 ("ov_bed_over",    S("scroll_mx02"), 1.05, 4.0, False, 0.50, 11, "portrait"),
 ("ov_bed_solo",    S("scroll_mx02"), 0.55, 6.0, True,  0.00, 12, "full"),
 ("ov_hand_over",   S("scroll_mx00"), 1.05, 1.5, False, 0.45, 13, "full"),
 ("ov_hand_solo",   S("scroll_mx00"), 0.55, 3.0, True,  0.00, 14, "square"),
 ("ov_glasses_over",S("scroll_mx03"), 0.55, 2.0, False, 0.60, 15, "cinema"),
 ("ov_eye_over",    S("night_cv07"),  0.55, 1.5, False, 0.70, 16, "slab"),
 ("ov_eye_solo",    S("night_cv07"),  0.55, 3.0, True,  0.00, 17, "wide"),
 ("ov_subway_over", S("hand_mx09"),   1.05, 3.0, False, 0.30, 18, "cinema"),
 ("ov_subway_solo", S("hand_mx09"),   0.55, 6.0, True,  0.00, 19, "full"),
 ("ov_switch_over", A("ia_telephone65"), 1.05, 1179.0, False, 0.50, 20, "wide"),
 ("ov_bench_over",  S("alone_mx03"),  1.05, 3.0, False, 0.20, 21, "wide"),
 ("ov_bench_solo",  S("alone_mx03"),  1.05, 6.0, True,  0.00, 22, "mini"),
]

def one(j):
    key, src, dur, ss, solo, gl, seed, band = j
    _, _, bw, bh = band_rect(band)
    overlay.render(src, G(key), dur, W=bw, H=bh, ss=ss, solo=solo,
                   glitch=gl, seed=seed)
    print(f"  {key:18s} {bw}x{bh:<5d} {dur:4.2f}s {'solo' if solo else 'over'}")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(one, JOBS))
    print(f"\n{len(JOBS)} Overlay-Clips erzeugt")
