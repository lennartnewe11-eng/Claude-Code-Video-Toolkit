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

import random, json
def borderless(src, w, h):
    # borderless photo (no polaroid frame) with a soft drop shadow
    im=ImageOps.fit(Image.open(src).convert("RGB"),(w,h),Image.LANCZOS).convert("RGBA")
    pad=34
    canvas=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",canvas.size,(0,0,0,0))
    blk=Image.new("RGBA",(w,h),(0,0,0,110)); sh.paste(blk,(pad+8,pad+14))
    sh=sh.filter(ImageFilter.GaussianBlur(13))
    canvas=Image.alpha_composite(canvas,sh); canvas.paste(im,(pad,pad),im)
    return canvas, pad

def cascade_photos():
    # diagonal staircase; generate each photo separately + a layout for the
    # fly-in animation. The pad offset is baked in, so the layout x/y already
    # account for it.
    ids=["q1","q2","q3","q4","q5","q6","q7","q8","q9","q10","q11"]
    random.seed(3); x,y=40,-10; layout=[]
    for i,q in enumerate(ids):
        p=IMG/f"{q}.jpg"
        if not p.exists(): continue
        w=random.randint(420,520); h=int(w*random.uniform(0.62,0.72))
        card,pad=borderless(p,w,h)
        f=BUILD/f"c6_ph_{i:02d}.png"; card.save(f)
        px=x+random.randint(-20,20); py=y+random.randint(-16,16)
        layout.append({"file":f.name,"x":px-pad,"y":py-pad,"id":q})
        x+=random.randint(105,135); y+=random.randint(58,78)
    # extra foreground blue-hole card (bigger)
    bh,pad=borderless(IMG/"q3.jpg",820,560); bh.save(BUILD/"c6_bluehole.png")
    (BUILD/"c6_layout.json").write_text(json.dumps(
        {"photos":layout,"bh":{"file":"c6_bluehole.png","x":int(960-(820+2*pad)/2),"y":260}}))
    print("cascade photos:",len(layout))

if __name__=="__main__":
    cascade_photos()
    print(window(BUILD/"c6_window.png"))
