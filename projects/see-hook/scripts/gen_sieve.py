#!/usr/bin/env python3
"""Flat-cartoon cross-section: a shallow hollow whose underground is sand/gravel.
Rain falls in, water seeps straight down THROUGH the sand and disappears into
the depth -- nothing collects. Renders build/c3_sieve/s_%04d.png."""
import pathlib, random, math
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTD = ROOT/"build"/"c3_sieve"; OUTD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
DUR = 8.75
N = int(DUR*FPS)

SKY   = (216, 228, 234)
SAND  = (216, 192, 134)          # top layer: fine sand
SANDG = (196, 170, 110)          # fine sand grains
KIES  = (176, 168, 156)          # lower layer: gravel bed (cooler/greyer)
PEB   = (138, 128, 112)
PEB2  = (104, 96, 84)
PEB3  = (150, 140, 120)
WATER = (60, 150, 200)
RAIN  = (120, 140, 158)
INK   = (44, 50, 58)

random.seed(5)
SURF = 430
SPLIT = 730                       # boundary between the sand layer and the gravel layer
def surf_y(x):
    # shallow bowl centered at 960, half-width 360, depth 95
    dx=(x-960)/360.0
    return SURF + (95*(1-dx*dx) if abs(dx)<1 else 0)

# fine sand grains (top layer only)
SANDGRAINS=[(random.randint(0,W), random.randint(SURF,SPLIT),
             random.randint(3,7), random.choice([SANDG,SAND]))
            for _ in range(600)]
# gravel stones (lower layer only) -- bigger
PEBBLES=[(random.randint(0,W), random.randint(SPLIT,H),
          random.randint(12,26), random.choice([PEB,PEB2,PEB3]))
         for _ in range(300)]
RAINDROPS=[(random.randint(0,W), random.randint(-H,0),
            random.randint(24,42), random.uniform(15,24)) for _ in range(130)]
# seeping water columns: x near the bowl, each a falling particle cycling down
SEEP=[(random.randint(660,1260), random.random()*DUR, random.uniform(1.0,1.5))
      for _ in range(46)]

def draw(i):
    t=i/FPS
    im=Image.new("RGB",(W,H),SKY)
    d=ImageDraw.Draw(im,"RGBA")
    # lower layer: gravel bed (Kies)
    d.rectangle([0,SPLIT,W,H], fill=KIES)
    for (px,py,pr,col) in PEBBLES:
        d.ellipse([px-pr,py-pr,px+pr,py+pr], fill=col+(230,))
    # top layer: fine sand, from the (bowl) surface down to SPLIT
    pts=[(0,SPLIT),(0,surf_y(0))]+[ (x,surf_y(x)) for x in range(0,W+1,20) ]+[(W,surf_y(W)),(W,SPLIT)]
    d.polygon(pts, fill=SAND)
    for (px,py,pr,col) in SANDGRAINS:
        if py>surf_y(px):
            d.ellipse([px-pr,py-pr,px+pr,py+pr], fill=col+(190,))
    # layer boundary (dashed) + surface line
    for x in range(0,W,46):
        d.line([(x,SPLIT),(x+26,SPLIT)], fill=INK+(150,), width=4)
    d.line([(x,surf_y(x)) for x in range(0,W+1,8)], fill=INK, width=5)
    # rain
    for (x,y0,ln,sp) in RAINDROPS:
        yy=(y0+t*sp*FPS)%(H+ln)-ln
        if yy<surf_y(x): d.line([(x,yy),(x-5,yy+ln)], fill=RAIN+(170,), width=3)
    # seeping water: droplets fall from sky into bowl then sink through sand, fading
    for (x,ph,sp) in SEEP:
        tt=(t*sp+ph)%DUR
        prog=(tt/DUR)
        y = 120 + prog*(H-120)
        depth=y-SURF
        a=255
        if depth>320: a=max(0,int(255*(1-(depth-320)/380)))   # fade into the deep
        r=9 if y<surf_y(x) else 7
        d.ellipse([x-r,y-r,x+r,y+r], fill=WATER+(a,))
        if y<surf_y(x):
            d.line([(x,y-14),(x,y-2)], fill=WATER+(a,), width=4)
    # a couple of downward arrows to read as 'through into the depth'
    for ax in (760,960,1160):
        ay=760+18*math.sin(t*3+ax)
        d.line([(ax,ay),(ax,ay+70)], fill=INK+(120,), width=6)
        d.polygon([(ax-16,ay+60),(ax+16,ay+60),(ax,ay+92)], fill=INK+(120,))
    return im

if __name__=="__main__":
    for i in range(N):
        draw(i).save(OUTD/f"s_{i:04d}.png")
    print(f"DONE {N} frames -> {OUTD}")
