#!/usr/bin/env python3
"""Hockney 'joiner' collage from a video: cut each frame into many small,
variably-sized, overlapping tiles (white border, slight rotation) that
reassemble the central subject (the tree). Tiles pop in over time.
Renders build/c3_hockney/h_%04d.png (+ a single still with STILL=1)."""
import os, pathlib, random, math, subprocess
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC  = ROOT/"main_assets"/"c3"/"tree.mp4"
SRCD = ROOT/"build"/"c3_src"; SRCD.mkdir(parents=True, exist_ok=True)
OUTD = ROOT/"build"/"c3_hockney"; OUTD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
DUR = 3.0
N = int(DUR*FPS)
BG = (238, 234, 226)            # warm paper white
random.seed(11)

def extract():
    if not any(SRCD.glob("s_*.png")):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(SRC),
                        "-vf",f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                        f"crop={W}:{H},fps={FPS}", str(SRCD/"s_%04d.png")], check=True)

def build_tiles():
    """Irregular grid: rows of jittered heights, each split into jittered cols.
    Denser (smaller) tiles in the central band where the tree is."""
    tiles=[]
    ys=[0]
    while ys[-1] < H-40:
        ys.append(min(H, ys[-1]+random.randint(120, 220)))
    ys[-1]=H
    for r in range(len(ys)-1):
        y0,y1=ys[r],ys[r+1]
        x=0; xs=[0]
        # central rows get narrower columns (more detail on the tree)
        cy=(y0+y1)/2
        base = 150 if 250<cy<820 else 240
        while xs[-1] < W-40:
            xs.append(min(W, xs[-1]+random.randint(base-40, base+90)))
        xs[-1]=W
        for c in range(len(xs)-1):
            x0,x1=xs[c],xs[c+1]
            tiles.append((x0,y0,x1-x0,y1-y0))
    return tiles

def make_tile_png(src_im, tile):
    x,y,w,h=tile
    crop=src_im.crop((x,y,x+w,y+h)).convert("RGBA")
    b=4
    card=Image.new("RGBA",(w+2*b,h+2*b),(252,250,245,255))
    card.paste(crop,(b,b))
    ang=random.uniform(-3.5,3.5)
    rot=card.rotate(ang,expand=True,resample=Image.BICUBIC)
    pad=22
    canvas=Image.new("RGBA",(rot.width+2*pad,rot.height+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",canvas.size,(0,0,0,0))
    shm=rot.split()[3].point(lambda a:int(a*0.30))
    black=Image.new("RGBA",rot.size,(0,0,0,255)); black.putalpha(shm)
    sh.paste(black,(pad+4,pad+7),black); sh=sh.filter(ImageFilter.GaussianBlur(7))
    canvas=Image.alpha_composite(canvas,sh); canvas.paste(rot,(pad,pad),rot)
    return canvas, ang

def main():
    extract()
    frames=sorted(SRCD.glob("s_*.png"))
    tiles=build_tiles()
    # per-tile: jittered placement offset + reveal time (center-out)
    cx,cy=W/2, 470
    meta=[]
    for t in tiles:
        x,y,w,h=t
        ox=random.randint(-16,16); oy=random.randint(-14,14)
        d=math.hypot((x+w/2)-cx,(y+h/2)-cy)
        meta.append((t,ox,oy,d))
    dmax=max(m[3] for m in meta) or 1
    order=sorted(range(len(meta)), key=lambda i: meta[i][3])   # center first
    reveal={}
    for rank,i in enumerate(order):
        reveal[i]=0.15 + (rank/len(order))*2.0                 # spread over ~2.0s

    still = os.environ.get("STILL")
    rng_states=[random.Random(1000+i) for i in range(len(meta))]
    for fi in range(N):
        t=fi/FPS
        src=Image.open(frames[min(fi,len(frames)-1)]).convert("RGB")
        out=Image.new("RGBA",(W,H),BG+(255,))
        for i,(tile,ox,oy,d) in enumerate(meta):
            rt=reveal[i]
            if t < rt-0.01 and not still: continue
            random.seed(2000+i)                                # stable tile look
            card,ang=make_tile_png(src,tile)
            x,y,w,h=tile
            px=int(x-22+ox); py=int(y-22+oy)
            if still:
                out.alpha_composite(card,(px,py)); continue
            # quick pop-in: fade + tiny scale
            p=max(0.0,min(1.0,(t-rt)/0.35))
            if p<=0: continue
            if p<1.0:
                s=0.86+0.14*p
                cw,ch=int(card.width*s),int(card.height*s)
                c2=card.resize((cw,ch),Image.BICUBIC)
                a=c2.split()[3].point(lambda v:int(v*p)); c2.putalpha(a)
                out.alpha_composite(c2,(px+(card.width-cw)//2,py+(card.height-ch)//2))
            else:
                out.alpha_composite(card,(px,py))
        out.convert("RGB").save(OUTD/f"h_{fi:04d}.png")
        if still:
            out.convert("RGB").save(ROOT/"build"/"c3_hockney_still.png"); break
    print(f"DONE {'still' if still else N} frames, {len(meta)} tiles")

if __name__=="__main__":
    main()
