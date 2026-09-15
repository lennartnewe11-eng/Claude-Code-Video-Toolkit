#!/usr/bin/env python3
"""Panel-Choreographie: mehrere Clips gleichzeitig, jeder bleibt lange genug
stehen um lesbar zu sein -- den Takt traegt die Bewegung, nicht der Schnitt.

Ein Beat sind 0,3715s. Zu kurz, um eine Szene zu erfassen. Deshalb laufen
die Clips hier durchgehend weiter (ihre eigene Zeit laeuft mit), und auf
jedem Beat springt nur ihre Position und Groesse in eine neue Anordnung.
"""
import os, subprocess, sys, json
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
W, H, FPS, BEAT = 1080, 1920, 60, 0.3715

# Anordnungen als Bruchteile des Rahmens (x, y, breite, hoehe)
LAYOUTS = [
    [(0.06,0.17,0.88,0.31),(0.06,0.52,0.88,0.31)],                       # 0  zwei gestapelt
    [(0.00,0.15,0.62,0.33),(0.38,0.52,0.62,0.33)],                       # 1  zwei versetzt
    [(0.04,0.16,0.92,0.30),(0.04,0.50,0.44,0.30),(0.52,0.50,0.44,0.30)], # 2  eins oben, zwei unten
    [(0.04,0.16,0.44,0.28),(0.52,0.16,0.44,0.28),(0.12,0.48,0.76,0.32)], # 3  zwei oben, eins unten
    [(0.04,0.17,0.44,0.28),(0.52,0.17,0.44,0.28),
     (0.04,0.49,0.44,0.28),(0.52,0.49,0.44,0.28)],                       # 4  Vierer-Raster
    [(0.08,0.26,0.84,0.44)],                                             # 5  eins gross
    # 6/7 Freisteller-Streuung: ueber die volle Hoehe verteilt statt in einer
    # Reihe in der Mitte. Im 9:16 sind sonst oben und unten je ein Viertel leer
    # und in der Mitte ueberlappt alles.
    [(0.02,0.04,0.36,0.20),(0.56,0.17,0.42,0.22),(0.06,0.35,0.40,0.22),
     (0.52,0.56,0.46,0.22),(0.08,0.75,0.38,0.21)],                       # 6
    [(0.56,0.03,0.40,0.21),(0.03,0.18,0.40,0.22),(0.50,0.38,0.46,0.23),
     (0.05,0.58,0.40,0.22),(0.46,0.76,0.48,0.21)],                       # 7
]

def cover(im, w, h):
    """Fuellt das Rechteck, beschneidet mittig -- kein Verzerren."""
    sw, sh = im.size
    s = max(w/sw, h/sh)
    im = im.resize((max(1,int(sw*s)), max(1,int(sh*s))), Image.LANCZOS)
    x, y = (im.width-w)//2, (im.height-h)//2
    return im.crop((x, y, x+w, y+h))

def extract(src, ss, dur, key, tmp, height=460):
    """Frames eines Clips vorab auf Platte -- spart Speicher beim Setzen."""
    d = os.path.join(tmp, key); os.makedirs(d, exist_ok=True)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-ss",f"{ss:.3f}","-i",src,"-t",f"{dur+0.3:.3f}",
        "-vf",f"fps={FPS},scale=-2:{height}",
        os.path.join(d,"%04d.png")],check=True)
    return d

def render(clips, beats, dst, tmp_root=None, cut_keys=()):
    """clips: {key: (pfad, src_in)}   beats: [(layout_idx, [key,...]), ...]"""
    tmp = tmp_root or (dst + "_tmp"); os.makedirs(tmp, exist_ok=True)
    n_beats = len(beats)
    dur = n_beats * BEAT
    n = round(dur * FPS)

    first, last = {}, {}             # von welchem bis zu welchem Beat sichtbar
    for bi, (_, keys) in enumerate(beats):
        for k in keys:
            first.setdefault(k, bi); last[k] = bi

    dirs, counts, boxes = {}, {}, {}
    for k, (src, ss) in clips.items():
        if k not in first: continue
        need = (last[k] + 1 - first[k]) * BEAT
        if k in cut_keys:
            from cutout import cutout_frames, clip_figure_box
            d = os.path.join(tmp, k); cutout_frames(src, ss, need, d)
            dirs[k] = d
            boxes[k] = clip_figure_box(d)   # einmal messen, fuer den ganzen Clip
        else:
            dirs[k] = extract(src, ss, need, k, tmp)
        counts[k] = len([f for f in os.listdir(dirs[k]) if f.endswith(".png")])

    out_dir = os.path.join(tmp, "_out"); os.makedirs(out_dir, exist_ok=True)
    for i in range(n):
        t = i / FPS
        bi = min(n_beats-1, int(t / BEAT))
        li, keys = beats[bi]
        rects = LAYOUTS[li]
        canvas = Image.new("RGB", (W, H), (0, 0, 0))
        for slot, k in enumerate(keys):
            if slot >= len(rects) or k not in dirs: continue
            fx, fy, fw, fh = rects[slot]
            rw, rh = max(2,int(fw*W)), max(2,int(fh*H))
            # eigene Zeit des Clips laeuft ab seinem ersten Auftritt durch
            local = t - first[k]*BEAT
            idx = min(counts[k], max(1, int(local*FPS)+1))
            fp = os.path.join(dirs[k], f"{idx:04d}.png")
            if not os.path.exists(fp): continue
            src_im = Image.open(fp)
            if k in cut_keys:                  # freigestellt: mit Alpha einsetzen
                src_im = src_im.convert("RGBA")
                # auf die Figur beschneiden -- sonst skaliert man vor allem
                # den leeren Raum drumherum und die Figur wird winzig.
                # Der Kasten steht fuer den ganzen Clip fest, sonst pulsiert
                # die Figur mit jedem Frame in der Groesse.
                bb = boxes.get(k)
                if bb: src_im = src_im.crop(bb)
                sc = min(rh/src_im.height, (rw*3.2)/src_im.width)  # Hoehe bestimmt, Gruppen duerfen breiter werden
                nw, nh = max(1,int(src_im.width*sc)), max(1,int(src_im.height*sc))
                src_im = src_im.resize((nw, nh), Image.LANCZOS)
                # Gruppen duerfen breiter als ihr Feld werden -- dann aber
                # in den Rahmen schieben statt am Rand abzuschneiden
                px = min(max(int(fx*W)+(rw-nw)//2, 0), max(0, W-nw))
                py = min(max(int(fy*H)+(rh-nh), 0), max(0, H-nh))
                canvas.paste(src_im, (px, py), src_im)
            else:
                canvas.paste(cover(src_im.convert("RGB"), rw, rh),
                             (int(fx*W), int(fy*H)))
        canvas.save(os.path.join(out_dir, f"f{i:04d}.jpg"), quality=94)

    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate",str(FPS),"-i",os.path.join(out_dir,"f%04d.jpg"),
        "-c:v","libx264","-crf","13","-preset","medium","-pix_fmt","yuv420p",dst],check=True)
    subprocess.run(["rm","-rf",tmp])
    print(f"{n} Frames ({n_beats} Beats, {dur:.2f}s) -> {dst}")
    return dst

if __name__ == "__main__":
    S = lambda n: os.path.join(PROJ,"assets","stock",n+".mp4")
    CLIPS = {
        "friseur":    (S("u_friseur"), 0.2),
        "warten":     (S("u_warten"), 0.4),
        "klippe":     (S("u_klippe"), 0.4),
        "strasse":    (S("u_strasse"), 0.3),
        "pissoir":    (S("u_pissoir"), 0.5),
        "spielplatz": (S("u_spielplatz"), 0.4),
        # dieselben Szenen, nur freigestellt -- zwei Beats lang loest sich die
        # Umgebung auf und es bleiben die Menschen mit ihren Geraeten uebrig
        "c_warten":   (S("u_warten"), 0.4),
        "c_pissoir":  (S("u_pissoir"), 0.5),
        "c_strasse":  (S("u_strasse"), 0.3),
        "c_klippe":   (S("u_klippe"), 0.4),
        "c_spiel":    (S("u_spielplatz"), 0.4),
    }
    CUT = ("c_warten","c_pissoir","c_strasse","c_klippe","c_spiel")
    BEATS = [
        (0, ["friseur","warten"]),
        (1, ["friseur","warten"]),
        (2, ["warten","friseur","klippe"]),
        (3, ["friseur","klippe","warten"]),
        (1, ["klippe","strasse"]),
        (4, ["friseur","klippe","strasse","pissoir"]),
        (6, ["c_warten","c_pissoir","c_strasse","c_klippe","c_spiel"]),
        (7, ["c_pissoir","c_klippe","c_warten","c_spiel","c_strasse"]),
        (3, ["pissoir","strasse","spielplatz"]),
        (2, ["spielplatz","strasse","pissoir"]),
        (5, ["spielplatz"]),
        (5, ["spielplatz"]),
    ]
    render(CLIPS, BEATS, os.path.join(PROJ,"assets","generated","collage_end.mp4"),
           cut_keys=CUT)
