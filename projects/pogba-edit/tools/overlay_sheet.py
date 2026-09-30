"""overlay_sheet.py edl.json out_prefix: first/middle/last source frame of every clip with a 10% grid, to locate logos."""
import sys, json, subprocess, io
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
edl = json.load(open(sys.argv[1])); beat = 60 / edl["bpm"]
TW, TH = 400, 225
def grab(src, t):
    b = subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.3f}","-i",src,"-frames:v","1","-vf",f"scale={TW}:{TH}","-f","image2pipe","-vcodec","png","-"],capture_output=True).stdout
    return Image.open(io.BytesIO(b)).convert("RGB")
t = 0; edge = edl["grid0"]; cells = []
for i, c in enumerate(edl["clips"]):
    end = edge + c["beats"] * beat; dur = end - t; t = edge = end
    sd = dur * c.get("speed", 1)
    ims = []
    for tt in (c["in"] + 0.05, c["in"] + sd * 0.5, c["in"] + sd - 0.05):
        im = grab(c["src"], tt); d = ImageDraw.Draw(im)
        for g in range(1, 10):
            x = TW * g // 10; y = TH * g // 10
            d.line([(x, 0), (x, 6)], fill=(255, 255, 0), width=2); d.line([(x, TH - 6), (x, TH)], fill=(255, 255, 0), width=2)
            d.line([(0, y), (6, y)], fill=(0, 255, 255), width=2); d.line([(TW - 6, y), (TW, y)], fill=(0, 255, 255), width=2)
        ims.append(im)
    cells.append((i, c["src"].split("/")[-1][:12], ims))
per = 8
for p in range(0, len(cells), per):
    chunk = cells[p:p + per]
    sheet = Image.new("RGB", (3 * (TW + 4), len(chunk) * (TH + 20)), (15, 15, 15)); d = ImageDraw.Draw(sheet)
    for r, (i, name, ims) in enumerate(chunk):
        y = r * (TH + 20); d.text((3, y + 2), f"#{i} {name}", fill=(0, 255, 0), font=F)
        for k, im in enumerate(ims): sheet.paste(im, (k * (TW + 4), y + 19))
    fn = f"{sys.argv[2]}_{p // per}.jpg"; sheet.save(fn, quality=85); print(fn)
