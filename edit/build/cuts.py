"""Camera cuts inside a source clip (so a shot never straddles one by accident).

    python3 build/cuts.py KEY [KEY ...]
"""
import subprocess
import sys

import numpy as np

import render


def cuts(key):
    """A cut is a frame difference far above the local motion level."""
    p = render.probe(key)
    w, h = 96, 54
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(p["path"]), "-vf", f"scale={w}:{h}",
                             "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    frames = []
    while True:
        buf = proc.stdout.read(w * h)
        if len(buf) < w * h:
            break
        frames.append(np.frombuffer(buf, np.uint8).astype(np.float32))
    d = np.array([np.abs(a - b).mean() for a, b in zip(frames[1:], frames[:-1])])
    out = []
    for i, v in enumerate(d):
        local = np.median(d[max(0, i - 12):i + 13])
        if v > 18 and v > 3.5 * local and (not out or i + 1 - out[-1] > 3):
            out.append(i + 1)
    return [f / p["fps"] for f in out], len(frames) / p["fps"]


if __name__ == "__main__":
    for key in sys.argv[1:]:
        c, dur = cuts(key)
        print(f"{key:13s} {dur:6.1f}s  cuts: " + " ".join(f"{t:.2f}" for t in c))
