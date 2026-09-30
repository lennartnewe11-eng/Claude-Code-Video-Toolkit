"""review.py video edl.json out_prefix [per_clip]: frames sampled inside each clip of the rendered edit."""
import sys, json, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
vid, edlp, out = sys.argv[1:4]; per = int(sys.argv[4]) if len(sys.argv) > 4 else 3
edl = json.load(open(edlp)); beat = 60 / edl["bpm"]
t = 0; edge = edl["grid0"]; spans = []
for c in edl["clips"]:
    end = edge + c["beats"] * beat; spans.append((t, end, c)); t = edge = end
TW, TH = 216, 384
cells = []
for i, (a, b, c) in enumerate(spans):
    for k in range(per):
        tt = a + (b - a) * (k + 0.5) / per
        buf = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{tt:.3f}", "-i", vid, "-frames:v", "1", "-vf", f"scale={TW}:{TH}",
                              "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        im = Image.open(__import__("io").BytesIO(buf)).convert("RGB")
        d = ImageDraw.Draw(im); d.rectangle([0, 0, TW, 20], fill=(0, 0, 0))
        d.text((3, 2), f"#{i} {tt:.1f}s", fill=(255, 255, 0), font=F)
        cells.append(im)
cols = per * 4; rows_per = 3
for p in range(0, len(cells), cols * rows_per):
    chunk = cells[p:p + cols * rows_per]
    sheet = Image.new("RGB", (cols * (TW + 3), ((len(chunk) - 1) // cols + 1) * (TH + 3)), (40, 40, 40))
    for j, im in enumerate(chunk):
        sheet.paste(im, ((j % cols) * (TW + 3), (j // cols) * (TH + 3)))
    fn = f"{out}_{p // (cols * rows_per)}.jpg"; sheet.save(fn, quality=85); print(fn, sheet.size)
