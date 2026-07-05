#!/usr/bin/env python3
"""PIL assets for Chunk 6 (rest of the groundwater part):
- b1_p1/2/3.png : thin-bordered cinematic photos for the editorial diagonal cascade
- c6_window.png : a white window frame (muntin cross, transparent glass) to lay
  over the sediment video -> 'ein Fenster zum Grundwasser'
"""
import pathlib
from PIL import Image, ImageOps, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG = ROOT/"main_assets"/"c6"/"img"
BUILD = ROOT/"build"; BUILD.mkdir(exist_ok=True)

def bordered(src, w, h, out, border=12):
    im = ImageOps.fit(Image.open(src).convert("RGB"), (w, h), Image.LANCZOS)
    card = Image.new("RGB", (w+2*border, h+2*border), (250, 248, 244)).convert("RGBA")
    card.paste(im, (border, border))
    pad = 34
    canvas = Image.new("RGBA", (card.width+2*pad, card.height+2*pad), (0,0,0,0))
    sh = Image.new("RGBA", canvas.size, (0,0,0,0))
    shm = card.split()[3].point(lambda a:int(a*0.30))
    blk = Image.new("RGBA", card.size, (0,0,0,255)); blk.putalpha(shm)
    sh.paste(blk,(pad+8,pad+14),blk); sh=sh.filter(ImageFilter.GaussianBlur(12))
    canvas=Image.alpha_composite(canvas,sh); canvas.paste(card,(pad,pad),card)
    canvas.save(out); return canvas.size

def window(out, w=980, h=680, frame=30, muntin=16):
    im = Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    col=(238,236,230,255); edge=(120,116,104,255)
    # outer frame (glass stays transparent in the middle)
    d.rectangle([0,0,w-1,h-1], outline=edge, width=2)
    d.rectangle([0,0,w-1,frame], fill=col); d.rectangle([0,h-frame,w-1,h-1], fill=col)
    d.rectangle([0,0,frame,h-1], fill=col); d.rectangle([w-frame,0,w-1,h-1], fill=col)
    # muntin cross
    cx,cy=w//2,h//2
    d.rectangle([cx-muntin//2,0,cx+muntin//2,h], fill=col)
    d.rectangle([0,cy-muntin//2,w,cy+muntin//2], fill=col)
    # thin inner shadow lines on the frame
    for (x0,y0,x1,y1) in [(frame,frame,w-frame,frame+2),(frame,frame,frame+2,h-frame),
                          (cx-muntin//2,frame,cx-muntin//2+2,h-frame)]:
        d.rectangle([x0,y0,x1,y1], fill=(150,146,134,180))
    im.save(out); return (w,h)

import random
def cascade(out):
    # dense diagonal staircase of many overlapping photos (ref insp1)
    W,H=1920,1080
    canvas=Image.new("RGBA",(W,H),(0,0,0,0))
    ids=["q1","q2","q3","q4","q5","q6","q7","q8","q9","q10","q11"]
    random.seed(3)
    x,y=40,-10
    for i,q in enumerate(ids):
        p=IMG/f"{q}.jpg"
        if not p.exists(): continue
        w=random.randint(420,520); h=int(w*random.uniform(0.62,0.72))
        b=10
        im=ImageOps.fit(Image.open(p).convert("RGB"),(w,h),Image.LANCZOS)
        card=Image.new("RGB",(w+2*b,h+2*b),(250,248,244)).convert("RGBA")
        card.paste(im,(b,b))
        sh=Image.new("RGBA",(card.width+30,card.height+30),(0,0,0,0))
        blk=Image.new("RGBA",card.size,(0,0,0,70)); sh.paste(blk,(18,22))
        sh=sh.filter(ImageFilter.GaussianBlur(9))
        px=x+random.randint(-20,20); py=y+random.randint(-16,16)
        canvas.alpha_composite(sh,(px-6,py-6)); canvas.alpha_composite(card,(px,py))
        x+=random.randint(105,135); y+=random.randint(58,78)
    canvas.save(out); print("cascade ok")

if __name__=="__main__":
    cascade(BUILD/"c6_cascade.png")
    print(window(BUILD/"c6_window.png"))
