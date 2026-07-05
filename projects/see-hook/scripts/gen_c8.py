#!/usr/bin/env python3
"""Chunk 8 animations (styled to the greyscale Europe relief map):
- map_frames(): the Europe relief map with white glacial ice spreading from
  Scandinavia (N) and out of the Alps (centre), on a dark ground.
- basin_frames(): a grainy black-and-white terrain cross-section (ref: the
  stippled mountain block) with a glacier gouging a basin.
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG = ROOT/"main_assets"/"c8"/"img"
MAPD = ROOT/"build"/"c8_map"; MAPD.mkdir(parents=True, exist_ok=True)
BASD = ROOT/"build"/"c8_basin"; BASD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

# ---------- map: Europe relief + spreading ice --------------------------------
MAP_DUR = 13.64
def map_frames():
    n=int(MAP_DUR*FPS)
    m=Image.open(IMG/"europe.png").convert("RGBA")
    mw,mh=m.size; MH=1040; MW=int(mw*MH/mh)
    m=m.resize((MW,MH),Image.LANCZOS)
    MX,MY=(W-MW)//2,(H-MH)//2
    canvas=Image.new("RGBA",(W,H),(0,0,0,0)); canvas.paste(m,(MX,MY),m)
    arr=np.array(canvas).astype(np.float32)
    land=(arr[:,:,3]>28).astype(np.float32)
    gray=arr[:,:,:3].mean(2)                       # relief luminance
    Y,Xc=np.mgrid[0:H,0:W].astype(np.float32)
    # north front: Scandinavia downwards; Alps radial centre
    rng=np.random.default_rng(5); jag=rng.uniform(-30,30,W)
    jag=np.convolve(jag,np.ones(9)/9,mode="same")
    ax,ay=MX+int(0.50*MW), MY+int(0.66*MH)         # Alps centre on the map
    snow=np.array([228,236,246],np.float32)        # cool white ice
    for i in range(n):
        p=ease(i/n)
        frontY=MY+0.10*MH + 0.62*MH*p + jag[None,:]  # per-column front
        iceN=np.clip((frontY-Y)/40.0,0,1)
        r=0.10*MW+0.62*MW*p
        d=np.sqrt((Xc-ax)**2+(Y-ay)**2)
        iceA=np.clip((r-d)/40.0,0,1)
        ice=np.maximum(iceN,iceA)*land
        ice=np.array(Image.fromarray((ice*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)),np.float32)/255.0
        # snow shading keeps a little relief texture
        snow_rgb=snow[None,None,:]*(0.82+0.18*(gray[:,:,None]/255.0))
        base=np.repeat(gray[:,:,None],3,2)
        out=base*(1-ice[:,:,None])+snow_rgb*ice[:,:,None]
        out=out*land[:,:,None]+18*(1-land[:,:,None])   # dark ground off-land
        out=np.clip(out+rng.normal(0,4,out.shape),0,255).astype(np.uint8)
        Image.fromarray(out,"RGB").save(MAPD/f"m_{i:04d}.png")
    print("map frames",n)

# ---------- basin: grainy B&W terrain cross-section ---------------------------
BAS_DUR = 4.34
def _grain(shape, seed):
    rng=np.random.default_rng(seed)
    return rng.normal(0,1,shape)
def basin_frames():
    n=int(BAS_DUR*FPS)
    Y,Xc=np.mgrid[0:H,0:W].astype(np.float32)
    rng=np.random.default_rng(9)
    tex=rng.normal(0,1,(H,W))                        # static terrain grain
    tex=np.array(Image.fromarray(((tex-tex.min())/(np.ptp(tex))*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)),np.float32)/255.0
    # REAL glacier ice texture (greyscale, contrast-boosted) -> the glacier body
    g=Image.open(IMG/"glaciertex.jpg").convert("L")
    from PIL import ImageOps as _IO
    g=_IO.autocontrast(g,1); gtex=np.array(g,np.float32); GH,GW=gtex.shape
    # jagged seracs at the advancing snout (per screen-row displacement)
    jr=np.convolve(rng.uniform(-60,60,H),np.ones(19)/19,mode="same")
    def surf_of(x, depth, cx=960.0, halfw=560.0):
        dx=(x-cx)/halfw
        return 540 + (depth*(1-dx*dx) if abs(dx)<1 else 0)
    GY0=90.0   # sample from clean-ice region of the photo (skip the very top)
    for i in range(n):
        p=ease(i/n); depth=360*p
        dx=(Xc-960.0)/560.0
        surf=540 + np.where(np.abs(dx)<1, depth*(1-dx*dx), 0.0)
        ground=(Y>surf).astype(np.float32)
        val=np.where(ground>0, 150+80*(tex-0.5)*2, 255).astype(np.float32)
        # ice sheet: crest runs off the top of frame (no photo-top line); the
        # leading edge is a sloped, jagged snout that rides down onto the ground.
        gx=-560+(W+760)*p
        snout=gx+70+0.42*Y+jr[:,None]            # bottom reaches further right
        inice=(Xc<snout)&(Y<surf-4)
        # sample the real glacier texture, scrolling with the ice mass
        tx=np.clip((Xc-gx+560).astype(np.int32),0,GW-1)
        ty=np.clip((Y+GY0).astype(np.int32),0,GH-1)
        icev=gtex[ty,tx]
        val=np.where(inice, icev, val)
        line=np.abs(Y-surf)<3
        val=np.where(line & (Xc<snout+40), 30, val)
        img=Image.fromarray(np.clip(np.repeat(val[:,:,None],3,2),0,255).astype(np.uint8),"RGB")
        d=ImageDraw.Draw(img,"RGBA")
        # furrows / striations scraped into the carved basin (behind the ice)
        for k in range(1,7):
            xs=range(0,int(gx-120),12)
            pts=[(x,surf_of(x,depth)+k*7) for x in xs if surf_of(x,depth)+k*7 < H]
            if len(pts)>2: d.line(pts,fill=(120,104,84,120),width=2)
        img.save(BASD/f"b_{i:04d}.png")
    print("basin frames",n)

if __name__=="__main__":
    map_frames(); basin_frames()
