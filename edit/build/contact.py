"""Contact sheets -- look instead of assume.

    python3 build/contact.py src KEY T0 T1 [STEP]   frames of a source clip, with timestamps
    python3 build/contact.py edit VIDEO [SHOT0 SHOT1] first / anchor / last frame per shot

Sheets are written to out/sheets/.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import edl  # noqa: E402
import render  # noqa: E402

OUT = render.OUT / "sheets"
TW, TH = 384, 216
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)


def grab(path, times=None, frames=None, deint=False):
    """Frames by time (seconds) or by index, as TWxTH RGB arrays."""
    out = []
    pre = "bwdif=mode=send_field," if deint else ""
    if times is not None:
        for t in times:
            buf = subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                 "-vf", f"{pre}scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2",
                 "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            out.append(np.frombuffer(buf, np.uint8).reshape(TH, TW, 3) if len(buf) == TW * TH * 3
                       else np.zeros((TH, TW, 3), np.uint8))
    else:
        sel = "+".join(f"eq(n\\,{f})" for f in frames)
        buf = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"select='{sel}',scale={TW}:{TH}",
             "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            capture_output=True).stdout
        n = len(buf) // (TW * TH * 3)
        arr = np.frombuffer(buf[: n * TW * TH * 3], np.uint8).reshape(n, TH, TW, 3)
        # select emits frames in order; map back (duplicates in `frames` collapse)
        order = sorted(set(frames))
        by = {f: arr[i] for i, f in enumerate(order[:n])}
        out = [by.get(f, np.zeros((TH, TW, 3), np.uint8)) for f in frames]
    return out


def sheet(tiles, labels, cols, dst):
    rows = (len(tiles) + cols - 1) // cols
    im = Image.new("RGB", (cols * TW, rows * (TH + 22)), (16, 16, 16))
    d = ImageDraw.Draw(im)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        x, y = (i % cols) * TW, (i // cols) * (TH + 22)
        im.paste(Image.fromarray(t), (x, y))
        d.text((x + 4, y + TH + 3), lab, font=FONT, fill=(240, 240, 240))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, quality=88)
    print("wrote", dst)


def main():
    mode = sys.argv[1]
    if mode == "src":
        key, t0, t1 = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        step = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
        p = render.probe(key)
        ts = list(np.arange(t0, min(t1, p["dur"] - 0.02), step))
        tiles = grab(p["path"], times=ts, deint=p["interlaced"])
        sheet(tiles, [f"{key} {t:.2f}s" for t in ts], 6, OUT / f"src_{key}_{t0:g}-{t1:g}.jpg")
    else:
        video = sys.argv[2]
        shots = edl.shots()
        s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        s1 = int(sys.argv[4]) if len(sys.argv) > 4 else len(shots)
        frames, labels = [], []
        for i in range(s0, s1):
            s = shots[i]
            f0, f1 = render.fb(s["b0"]), render.fb(s["b1"])
            ab = s.get("at", (0, s["b0"]))[1]
            fa = min(max(render.fb(ab), f0), f1 - 1)
            for f, tag in ((f0 + 2, "in"), (fa, f"@{ab:g}"), (f1 - 1, "out")):
                frames.append(f)
                labels.append(f"#{i} {s['b0']:g}-{s['b1']:g} {tag} f{f}  {s.get('src', 'split' if 'panels' in s else 'black')}")
        tiles = grab(video, frames=frames)
        sheet(tiles, labels, 6, OUT / f"edit_{s0}-{s1}.jpg")


if __name__ == "__main__":
    main()
