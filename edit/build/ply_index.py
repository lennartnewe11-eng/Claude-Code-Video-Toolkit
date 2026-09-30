"""Index a "Premier League Years" review by its match captions.

Every match in the review opens with a lower third (blue bar, "MANCHESTER UTD
2-0 PORTSMOUTH / JANUARY 30 2008"). One pass at 1 fps over the bar region,
detect when the bar is up, OCR the first frame of each appearance.

    python3 build/ply_index.py media/raw/ply0708.mp4   -> build/ply_index/ply0708.tsv
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

X0, Y0, W, H = 300, 845, 1120, 125  # caption region in a 1920x1080 frame


def main(path):
    path = Path(path)
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-skip_frame", "nokey", "-i", str(path), "-vf",
         f"fps=1,crop={W}:{H}:{X0}:{Y0}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)
    size = W * H * 3
    rows, prev_on, t = [], False, -1
    tmp = Path("/tmp") / f"cap_{path.stem}.png"
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        t += 1
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(int)
        # the bar: saturated blue/purple band behind the first text line
        band = img[10:65, :900]
        blue = ((band[..., 2] > 90) & (band[..., 2] > band[..., 1] + 40)).mean()
        on = blue > 0.45
        if on and not prev_on:
            gray = 255 - img[5:120, 20:1100].mean(2)  # white text -> dark on light
            g = np.clip((gray - 60) * 2.2, 0, 255).astype(np.uint8)
            Image.fromarray(g).resize((g.shape[1] * 2, g.shape[0] * 2)).save(tmp)
            try:  # some noisy frames make tesseract spin for minutes
                txt = subprocess.run(["tesseract", str(tmp), "-", "--psm", "6"], capture_output=True,
                                     text=True, timeout=5, env={"OMP_THREAD_LIMIT": "1"}).stdout
            except subprocess.TimeoutExpired:
                txt = ""
            txt = " / ".join(x.strip() for x in txt.splitlines() if x.strip())
            rows.append(f"{t}\t{t // 60}:{t % 60:02d}\t{txt}")
            print(rows[-1], flush=True)
        prev_on = on
    out = Path(__file__).with_name("ply_index") / f"{path.stem}.tsv"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(rows) + "\n")
    print("wrote", out, len(rows), "captions")


if __name__ == "__main__":
    main(sys.argv[1])
