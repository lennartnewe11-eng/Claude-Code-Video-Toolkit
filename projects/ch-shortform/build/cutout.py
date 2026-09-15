#!/usr/bin/env python3
"""Stellt Personen aus einem Clip frei (rembg/u2net) und legt die Frames als
RGBA-PNG ab. Fuer die Collage: Figuren ohne ihre Umgebung, allein auf Schwarz.
"""
import os, subprocess, sys
from PIL import Image
from rembg import remove, new_session

FPS = 60

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
