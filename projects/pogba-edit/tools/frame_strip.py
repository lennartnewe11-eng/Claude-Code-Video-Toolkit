"""strip.py OUT.jpg src:in:dur[:n] ...  -> grid of frames with x-ticks (tenths) and timestamps, one row per spec."""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
TW = 400
def grab(src, t):
    b = subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.3f}","-i",src,"-frames:v","1","-f","image2pipe","-vcodec","png","-"],capture_output=True).stdout
    im = cv2.imdecode(np.frombuffer(b,np.uint8), cv2.IMREAD_COLOR)
    return im
rows = []
for spec in sys.argv[2:]:
    p = spec.split(":"); src=p[0]; t0=float(p[1]); dur=float(p[2]); n=int(p[3]) if len(p)>3 else 6
    ims=[]
    for k in range(n):
        t = t0 + dur*k/max(1,n-1)
        im = grab(src, t)
        if im is None: im = np.zeros((225,TW,3),np.uint8)
        h,w = im.shape[:2]; th=int(h*TW/w)
        im = cv2.resize(im,(TW,th))
        pil = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(pil)
        for g in range(1,10):
            x=int(TW*g/10); d.line([(x,0),(x,8)],fill=(255,255,0),width=2); d.line([(x,th-8),(x,th)],fill=(255,255,0),width=2)
            d.text((x-4,9),str(g),fill=(255,255,0),font=F)
        for g in range(1,10):
            y=int(th*g/10); d.line([(0,y),(6,y)],fill=(0,255,255),width=2)
        d.rectangle([0,th-20,150,th],fill=(0,0,0)); d.text((3,th-19),f"{t:.2f}s",fill=(255,255,255),font=F)
        ims.append(pil)
    rows.append((spec, ims))
cols = max(len(r[1]) for r in rows)
th = max(im.height for r in rows for im in r[1])
sheet = Image.new("RGB",(cols*(TW+4), len(rows)*(th+20)),(15,15,15)); d=ImageDraw.Draw(sheet)
for ri,(spec,ims) in enumerate(rows):
    y = ri*(th+20)
    d.text((2,y+2),spec.split('/')[-1],fill=(0,255,0),font=F)
    for ci,im in enumerate(ims): sheet.paste(im,(ci*(TW+4), y+18))
sheet.save(sys.argv[1], quality=82)
print(sys.argv[1], sheet.size)
