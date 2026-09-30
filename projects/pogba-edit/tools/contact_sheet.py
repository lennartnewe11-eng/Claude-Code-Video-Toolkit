"""Scene-detect a video and write contact sheets: one thumb per shot, labelled with shot index + time range."""
import sys, os, json, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)

def detect(path, thr=0.35, min_len=0.5):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prev = None; cuts = [0.0]; i = 0; frames = {}
    while True:
        ok = cap.grab()
        if not ok: break
        if i % 2 == 0:
            ok, fr = cap.retrieve()
            if not ok: break
            small = cv2.resize(fr, (160, 90))
            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            h = cv2.calcHist([hsv], [0, 1, 2], None, [16, 8, 8], [0, 180, 0, 256, 0, 256]); h = cv2.normalize(h, h).flatten()
            if prev is not None:
                d = cv2.compareHist(prev, h, cv2.HISTCMP_BHATTACHARYYA)
                t = i / fps
                if d > thr and t - cuts[-1] >= min_len: cuts.append(t)
            prev = h
        i += 1
    dur = i / fps
    cap.release()
    shots = [(cuts[k], cuts[k+1] if k+1 < len(cuts) else dur) for k in range(len(cuts))]
    return shots, fps, dur

def thumbs(path, shots, per=1):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    out = []
    for (a, b) in shots:
        ims = []
        for k in range(per):
            t = a + (b - a) * (k + 1) / (per + 1)
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, fr = cap.read()
            if not ok: fr = np.zeros((180, 320, 3), np.uint8)
            h, w = fr.shape[:2]
            tw = 320; th = int(h * tw / w)
            ims.append(Image.fromarray(cv2.cvtColor(cv2.resize(fr, (tw, th)), cv2.COLOR_BGR2RGB)))
        out.append(ims)
    return out

def make_sheets(name, path, shots, ims, outdir, cols=5, rows=6):
    tw = ims[0][0].width; th = max(i[0].height for i in ims)
    per = len(ims[0])
    cellw = tw * per + 6; cellh = th + 22
    pages = []
    for p in range(0, len(shots), cols * rows):
        sheet = Image.new("RGB", (cols * cellw, rows * cellh), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for j, idx in enumerate(range(p, min(p + cols * rows, len(shots)))):
            x = (j % cols) * cellw; y = (j // cols) * cellh
            for k, im in enumerate(ims[idx]): sheet.paste(im, (x + k * tw, y + 20))
            a, b = shots[idx]
            d.text((x + 3, y + 2), f"#{idx} {a:.1f}-{b:.1f} ({b-a:.1f}s)", fill=(255, 255, 0), font=FONT)
        fn = os.path.join(outdir, f"{name}_p{p // (cols*rows)}.jpg"); sheet.save(fn, quality=80); pages.append(fn)
    return pages

if __name__ == "__main__":
    path = sys.argv[1]; outdir = sys.argv[2]
    name = os.path.splitext(os.path.basename(path))[0]
    shots, fps, dur = detect(path)
    json.dump({"fps": fps, "dur": dur, "shots": shots}, open(os.path.join(outdir, name + ".json"), "w"))
    ims = thumbs(path, shots)
    pages = make_sheets(name, path, shots, ims, outdir)
    print(name, f"{dur:.0f}s", len(shots), "shots", len(pages), "pages")
