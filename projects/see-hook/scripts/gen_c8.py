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
    for i in range(n):
        p=ease(i/n); depth=360*p; cx=960.0; halfw=560.0
        dx=(Xc-cx)/halfw
        surf=540 + np.where(np.abs(dx)<1, depth*(1-dx*dx), 0.0)
        ground=(Y>surf).astype(np.float32)
        # terrain: mid-grey with heavy stipple grain
        val=np.where(ground>0, 150+80*(tex-0.5)*2, 255).astype(np.float32)
        # glacier tongue (white, grainy) sliding L->R, carving
        gx=-500+(W+700)*p
        gy_top=170.0
        gslope=(surf-gy_top)/np.maximum(1.0,(Xc-(gx-620)))
        inice=(Xc>gx-620)&(Xc<gx+120)&(Y>gy_top)&(Y<surf-6)
        val=np.where(inice, 236+40*(tex-0.5)*2, val)
        # ink surface line
        line=np.abs(Y-surf)<3
        val=np.where(line & (Xc<gx+130), 30, val)
        val=np.clip(val,0,255).astype(np.uint8)
        img=np.repeat(val[:,:,None],3,2)
        Image.fromarray(img,"RGB").save(BASD/f"b_{i:04d}.png")
    print("basin frames",n)

if __name__=="__main__":
    map_frames(); basin_frames()
