"""Find every frame where the full phrase "Alors on danse" is on screen and pack
them for web/frames.html.

A frame counts once "danse" is completely written on (its write-on runs over
the sung duration) and until the phrase starts fading out. The frames come
straight from the typography timeline, so the ranges are exact.

Output in OUTDIR: packs/pack_XX.mp4 (JPGs concatenated into <=14 MB files; the
artifact host allows at most 511 files), packs/index.json (byte offsets per
frame) and thumbs/occ_XX.jpg (one contact sheet per occurrence).

usage: python3 make_frame_gallery.py MASTER.mp4 OUTDIR
"""
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import typography as TY  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
PACK = 14_000_000
TW, TH, COLS = 320, 180, 6


def occurrences():
    with open(os.path.join(HERE, "..", "beats.json")) as f:
        t0 = json.load(f)["beats"][3]
    occ = []
    for ev in TY.texts():
        if ev["style"] != "script" or [w["text"].lower() for w in ev["words"]] != ["alors", "on", "danse"]:
            continue
        danse = ev["words"][2]
        f0 = math.ceil((danse["t"] + max(0.12, danse["d"]) - t0) * FPS)   # danse fully written
        f1 = math.floor((ev["t1"] - 0.15 - t0) * FPS)                      # before the fade-out
        if f1 >= f0:
            occ.append((f0, f1))
    return occ


def main():
    master, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(out, "packs"), exist_ok=True)
    os.makedirs(os.path.join(out, "thumbs"), exist_ok=True)
    occ = occurrences()
    packs, cur, index = [], bytearray(), []

    def flush():
        nonlocal cur
        if cur:
            name = f"pack_{len(packs):02d}.mp4"
            with open(os.path.join(out, "packs", name), "wb") as f:
                f.write(cur)
            packs.append({"name": name, "size": len(cur)})
            cur = bytearray()

    for i, (f0, f1) in enumerate(occ):
        frames, tiles = [], []
        for n in range(f0, f1 + 1):
            jpg = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", master, "-vf", f"select=eq(n\\,{n})", "-vsync", "0",
                 "-frames:v", "1", "-q:v", "2", "-f", "image2pipe", "-c:v", "mjpeg", "-"],
                capture_output=True, check=True).stdout
            if len(cur) + len(jpg) > PACK:
                flush()
            frames.append({"n": n, "p": len(packs), "o": len(cur), "l": len(jpg)})
            cur += jpg
            img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
            tiles.append(cv2.resize(img, (TW, TH), interpolation=cv2.INTER_AREA))
        rows = (len(tiles) + COLS - 1) // COLS
        sheet = np.zeros((rows * TH, COLS * TW, 3), np.uint8)
        for k, t in enumerate(tiles):
            sheet[(k // COLS) * TH:(k // COLS + 1) * TH, (k % COLS) * TW:(k % COLS + 1) * TW] = t
        sprite = f"thumbs/occ_{i + 1:02d}.jpg"
        cv2.imwrite(os.path.join(out, sprite), sheet, [cv2.IMWRITE_JPEG_QUALITY, 82])
        index.append({"no": i + 1, "f0": f0, "f1": f1, "t0": round(f0 / FPS, 3),
                      "t1": round((f1 + 1) / FPS, 3), "sprite": sprite, "cols": COLS,
                      "tw": TW, "th": TH, "frames": frames})
        print(f"{i + 1:2d}: frames {f0}-{f1} ({f1 - f0 + 1})")
    flush()
    with open(os.path.join(out, "packs", "index.json"), "w") as f:
        json.dump({"fps": FPS, "size": 1920, "packs": packs, "occurrences": index}, f,
                  separators=(",", ":"))
    print(f"{len(occ)} occurrences, {sum(len(o['frames']) for o in index)} frames, {len(packs)} packs")


if __name__ == "__main__":
    main()
