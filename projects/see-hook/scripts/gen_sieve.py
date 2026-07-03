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
SAND  = (214, 190, 132)
SAND2 = (198, 172, 112)
PEB   = (150, 132, 96)
PEB2  = (120, 104, 74)
WATER = (60, 150, 200)
RAIN  = (120, 140, 158)
INK   = (44, 50, 58)

random.seed(5)
SURF = 430
def surf_y(x):
    # shallow bowl centered at 960, half-width 360, depth 95
    dx=(x-960)/360.0
    return SURF + (95*(1-dx*dx) if abs(dx)<1 else 0)

PEBBLES=[(random.randint(0,W), random.randint(SURF+10,H),
          random.randint(6,16), random.choice([PEB,PEB2,SAND2]))
         for _ in range(520)]
RAINDROPS=[(random.randint(0,W), random.randint(-H,0),
            random.randint(24,42), random.uniform(15,24)) for _ in range(130)]
# seeping water columns: x near the bowl, each a falling particle cycling down
SEEP=[(random.randint(660,1260), random.random()*DUR, random.uniform(1.0,1.5))
      for _ in range(46)]

def draw(i):
    t=i/FPS
    im=Image.new("RGB",(W,H),SKY)
    d=ImageDraw.Draw(im,"RGBA")
    # underground sand fill
    pts=[(0,H),(0,surf_y(0))]+[ (x,surf_y(x)) for x in range(0,W+1,20) ]+[(W,surf_y(W)),(W,H)]
    d.polygon(pts, fill=SAND)
    # pebbles / gravel
    for (px,py,pr,col) in PEBBLES:
        if py>surf_y(px):
            d.ellipse([px-pr,py-pr,px+pr,py+pr], fill=col+(210,))
    # surface line
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
