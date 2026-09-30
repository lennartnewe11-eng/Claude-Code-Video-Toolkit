"""letterbox_check.py edl.json [overrides.json]: report burnt-in black bars at the top/bottom of each clip's source."""
import json, subprocess, numpy as np
import sys
e = json.load(open(sys.argv[1])); o = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
beat = 0.5; t = 0; edge = e["grid0"]
for i, c in enumerate(e["clips"]):
    end = edge + c["beats"] * beat; dur = end - t; t = edge = end
    c = dict(c, **o.get(str(i), {}))
    W, H = map(int, subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",c["src"]]).decode().strip().split(","))
    tops, bots = [], []
    for k in (0.1, 0.5, 0.9):
        tt = c["in"] + dur * c.get("speed", 1) * k
        b = subprocess.run(["ffmpeg","-v","error","-ss",f"{tt:.3f}","-i",c["src"],"-frames:v","1","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True).stdout
        f = np.frombuffer(b, np.uint8).reshape(H, W).astype(float)
        rows = f.mean(1) ; rmax = f.max(1)
        top = 0
        while top < H // 3 and rows[top] < 6 and rmax[top] < 60: top += 1
        bot = 0
        while bot < H // 3 and rows[H - 1 - bot] < 6 and rmax[H - 1 - bot] < 60: bot += 1
        tops.append(top / H); bots.append(bot / H)
    T, B = max(tops), max(bots)
    if T > 0.004 or B > 0.004:
        print(f"#{i:2d} {c['src'].split('/')[-1][:12]} in={c['in']:<7} bar_top={T:.3f} bar_bot={B:.3f}  ylim16={c.get('ylim')}")
