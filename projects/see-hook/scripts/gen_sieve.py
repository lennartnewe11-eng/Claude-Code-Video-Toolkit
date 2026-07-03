#!/usr/bin/env python3
"""Flat-illustration cross-section (style ref: 'cyclist on a red road'):
teal sky, green grassy surface with flowers/vegetation beside a hollow, and
two underground layers -- warm orange SAND over a darker KIES (gravel) bed with
engraving hatch. Rain seeps straight down through both and vanishes into the
depth; the hollow never fills. Renders build/c3_sieve/s_%04d.png."""
import pathlib, random, math
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTD = ROOT/"build"/"c3_sieve"; OUTD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
DUR = 8.75
N = int(DUR*FPS)

SKY   = (58, 186, 201)          # teal
GRASS = (150, 193, 140)         # mint topsoil
GRASSD= (86, 146, 92)           # darker blades/stems
SAND  = (221, 138, 78)          # warm ochre-orange
SANDG = (198, 112, 58)          # darker sand grain
KIES  = (120, 118, 104)         # muted olive-grey gravel bed
PEB   = (92, 90, 78)
PEB2  = (68, 66, 58)
PEB3  = (146, 143, 126)
WATER = (58, 150, 202)
RAIN  = (150, 172, 188)
INK   = (26, 26, 30)
FLW_P = (150, 108, 178)
FLW_Y = (232, 208, 92)

random.seed(5)
SURF = 430
TOP  = 40                        # grassy topsoil thickness
SPLIT= 730                       # sand | gravel boundary
def surf_y(x):
    dx=(x-960)/360.0
    return SURF + (95*(1-dx*dx) if abs(dx)<1 else 0)
def on_flat(x):                  # flat ground beside the hollow (vegetation zone)
    return x<595 or x>1325

TOPPTS=[(x,surf_y(x)) for x in range(0,W+1,12)]
SANDGRAINS=[(random.randint(0,W), random.randint(SURF+TOP,SPLIT),
             random.randint(3,7), random.choice([SANDG,SAND])) for _ in range(500)]
PEBBLES=[(random.randint(0,W), random.randint(SPLIT,H),
          random.randint(12,26), random.choice([PEB,PEB2,PEB3])) for _ in range(300)]
RAINDROPS=[(random.randint(0,W), random.randint(-H,0),
            random.randint(24,42), random.uniform(15,24)) for _ in range(120)]
SEEP=[(random.randint(690,1230), random.random()*DUR, random.uniform(1.0,1.5))
      for _ in range(44)]
# vegetation: flower clusters + grass tufts rooted on the flats
VEG=[]
for _ in range(26):
    x=random.choice([random.randint(60,560), random.randint(1360,1860)])
    VEG.append((x, random.choice(["flower","flower","tuft"]),
                random.choice([FLW_P,FLW_Y]), random.randint(46,86)))

def draw(i):
    t=i/FPS
    im=Image.new("RGB",(W,H),SKY)
    d=ImageDraw.Draw(im,"RGBA")
    # --- gravel bed (Kies) with engraving hatch ---
    d.rectangle([0,SPLIT,W,H], fill=KIES)
    for hx in range(-H, W, 34):                     # diagonal engraving hatch
        d.line([(hx,H),(hx+ (H-SPLIT),SPLIT)], fill=INK+(28,), width=2)
    for (px,py,pr,col) in PEBBLES:
        d.ellipse([px-pr,py-pr,px+pr,py+pr], fill=col+(235,), outline=INK+(120,), width=2)
    d.line([(0,SPLIT),(W,SPLIT)], fill=INK, width=5)
    # --- sand layer (orange) ---
    sand=[(0,SPLIT)]+[(x,surf_y(x)+TOP) for x in range(0,W+1,12)]+[(W,SPLIT)]
    d.polygon(sand, fill=SAND)
    for (px,py,pr,col) in SANDGRAINS:
        if py>surf_y(px)+TOP: d.ellipse([px-pr,py-pr,px+pr,py+pr], fill=col+(170,))
    # --- grassy topsoil band ---
    grass=[(x,surf_y(x)) for x in range(0,W+1,12)]+[(x,surf_y(x)+TOP) for x in range(W,-1,-12)]
    d.polygon(grass, fill=GRASS)
    # surface outline (bold)
    d.line(TOPPTS, fill=INK, width=6)
    # --- vegetation on the flats (rooted at the surface) ---
    for (x,kind,col,hgt) in VEG:
        y0=surf_y(x)
        if kind=="tuft":
            for dxb in (-14,-6,2,10,16):
                d.line([(x,y0),(x+dxb,y0-hgt+random.randint(-6,6))], fill=GRASSD, width=4)
        else:
            d.line([(x,y0),(x,y0-hgt)], fill=GRASSD, width=4)           # stem
            for (fx,fy) in [(x,y0-hgt),(x-12,y0-hgt+10),(x+12,y0-hgt+8),(x,y0-hgt-10)]:
                d.ellipse([fx-9,fy-9,fx+9,fy+9], fill=col+(255,), outline=INK+(120,), width=1)
    # --- rain ---
    for (x,y0,ln,sp) in RAINDROPS:
        yy=(y0+t*sp*FPS)%(H+ln)-ln
        if yy<surf_y(x): d.line([(x,yy),(x-5,yy+ln)], fill=RAIN+(200,), width=3)
    # --- seeping water: into the hollow, then down through both layers, fading ---
    for (x,ph,sp) in SEEP:
        tt=(t*sp+ph)%DUR; y=120+(tt/DUR)*(H-120); depth=y-SURF
        a=255
        if depth>340: a=max(0,int(255*(1-(depth-340)/380)))
        r=9 if y<surf_y(x) else 7
        d.ellipse([x-r,y-r,x+r,y+r], fill=WATER+(a,))
        if y<surf_y(x): d.line([(x,y-14),(x,y-2)], fill=WATER+(a,), width=4)
    # --- 'through into the depth' arrows ---
    for ax in (770,960,1150):
        ay=780+16*math.sin(t*3+ax)
        d.line([(ax,ay),(ax,ay+66)], fill=INK+(120,), width=6)
        d.polygon([(ax-15,ay+58),(ax+15,ay+58),(ax,ay+88)], fill=INK+(120,))
    return im

if __name__=="__main__":
    for i in range(N):
        draw(i).save(OUTD/f"s_{i:04d}.png")
    print(f"DONE {N} frames -> {OUTD}")
