#!/usr/bin/env python3
"""Stellt Personen aus einem Clip frei (rembg/u2net) und legt die Frames als
RGBA-PNG ab. Fuer die Collage: Figuren ohne ihre Umgebung, allein auf Schwarz.
"""
import os, subprocess, sys
from PIL import Image, ImageFilter
from rembg import remove, new_session

FPS = 60


def figure_bbox(im, thr=128, erode=5, pad=6):
    """Kasten um die Figur -- ohne die Sprenkel, die u2net im Rest des Bildes
    stehen laesst. Ein blosses getbbox() faengt jeden einzelnen Restpunkt ein
    und liefert dann fast den ganzen Rahmen zurueck; die Figur wird beim
    Einpassen entsprechend winzig. MinFilter frisst alles, was duenner als
    `erode` Pixel ist, also genau diese Reste.
    """
    a = im.split()[3]
    m = a.point(lambda v: 255 if v >= thr else 0).filter(ImageFilter.MinFilter(erode))
    bb = m.getbbox() or a.getbbox()
    if not bb:
        return None
    x0, y0, x1, y1 = bb
    return (max(0, x0 - pad), max(0, y0 - pad),
            min(im.width, x1 + pad), min(im.height, y1 + pad))


def clip_figure_box(frame_dir, sample=3):
    """Ein fester Kasten fuer den ganzen Clip. Pro Frame schwankt der Rand um
    einige Dutzend Pixel; croppt man einzeln, pulsiert die Figur in der Groesse.
    Also einmal messen -- aber nicht als blosse Vereinigung aller Frames: ein
    einziger Frame, in dem ein groesserer Rest der Umgebung stehen bleibt,
    zoege den Kasten sonst auf und die Figur schrumpfte im ganzen Clip.
    Darum zuerst die Ausreisser weg (Kasten deutlich groesser als der
    Mittelwert), dann den Rest vereinigen.
    """
    files = sorted(f for f in os.listdir(frame_dir) if f.endswith(".png"))
    boxes = []
    for f in files[::max(1, sample)]:
        bb = figure_bbox(Image.open(os.path.join(frame_dir, f)).convert("RGBA"))
        if bb:
            boxes.append(bb)
    if not boxes:
        return None
    med = lambda v: sorted(v)[len(v) // 2]
    mh = med([b[3] - b[1] for b in boxes])
    mw = med([b[2] - b[0] for b in boxes])
    keep = [b for b in boxes
            if b[3] - b[1] <= mh * 1.3 and b[2] - b[0] <= mw * 1.3]
    if not keep:
        keep = boxes
    return (min(b[0] for b in keep), min(b[1] for b in keep),
            max(b[2] for b in keep), max(b[3] for b in keep))


def cutout_frames(src, ss, dur, out_dir, height=860, model="u2net"):
    os.makedirs(out_dir, exist_ok=True)
    raw = out_dir + "_raw"; os.makedirs(raw, exist_ok=True)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-ss",f"{ss:.3f}","-i",src,"-t",f"{dur+0.2:.3f}",
        "-vf",f"fps={FPS},scale=-2:{height}",
        os.path.join(raw,"%04d.png")],check=True)
    sess = new_session(model)
    files = sorted(f for f in os.listdir(raw) if f.endswith(".png"))
    for i, f in enumerate(files):
        im = Image.open(os.path.join(raw, f)).convert("RGB")
        remove(im, session=sess).save(os.path.join(out_dir, f))
    subprocess.run(["rm","-rf",raw])
    return len(files)


if __name__ == "__main__":
    a = sys.argv[1:]
    n = cutout_frames(a[0], float(a[1]), float(a[2]), a[3])
    print(f"{n} Frames freigestellt -> {a[3]}")
