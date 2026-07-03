#!/usr/bin/env python3
"""Companion to gen_sieve, same flat-illustration style, but the lower layer is
an IMPERMEABLE clay bed: water can't escape, it dams up in the sand and the
hollow slowly fills into a pond ('Es staut sich und die Mulde laeuft voll').
Renders build/c4_clay/c_%04d.png."""
import pathlib, random, math
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTD = ROOT/"build"/"c4_clay"; OUTD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
DUR = 6.05
N = int(DUR*FPS)

SKY   = (58, 186, 201)
GRASS = (150, 193, 140)
GRASSD= (86, 146, 92)
SAND  = (221, 138, 78)
SANDG = (198, 112, 58)
SANDW = (150, 92, 58)           # water-saturated (wet) sand
CLAY  = (150, 96, 82)           # impermeable clay bed (terracotta-brown)
CLAYD = (126, 78, 66)
WATER = (58, 150, 202)
WATERS= (120, 196, 226)         # surface highlight
RAIN  = (150, 172, 188)
INK   = (26, 26, 30)
FLW_P = (150, 108, 178)
FLW_Y = (232, 208, 92)

random.seed(8)
SURF = 430
TOP  = 40
SPLIT= 730
def surf_y(x):
    dx=(x-960)/360.0
    return SURF + (95*(1-dx*dx) if abs(dx)<1 else 0)
BOWL_BOTTOM = SURF+95
def bowl_x_at(y):
    # inverse of surf_y within the bowl: half-width at depth
    if y<=SURF: return 0
    frac=(y-SURF)/95.0
    if frac>1: frac=1
    hw=360*math.sqrt(max(0.0,1-frac))
    return hw

TOPPTS=[(x,surf_y(x)) for x in range(0,W+1,12)]
SANDGRAINS=[(random.randint(0,W), random.randint(SURF+TOP,SPLIT),
             random.randint(3,7), random.choice([SANDG,SAND])) for _ in range(500)]
RAINDROPS=[(random.randint(0,W), random.randint(-H,0),
            random.randint(24,42), random.uniform(15,24)) for _ in range(120)]
VEG=[]
for _ in range(24):
    x=random.choice([random.randint(60,560), random.randint(1360,1860)])
    VEG.append((x, random.choice(["flower","flower","tuft"]),
                random.choice([FLW_P,FLW_Y]), random.randint(46,86)))

def draw(i):
    t=i/FPS; prog=t/DUR
    im=Image.new("RGB",(W,H),SKY)
    d=ImageDraw.Draw(im,"RGBA")
    # --- impermeable clay bed with subtle sedimentary banding ---
    d.rectangle([0,SPLIT,W,H], fill=CLAY)
    for yy in range(SPLIT+26, H, 40):
        d.line([(0,yy),(W,yy)], fill=CLAYD+(120,), width=3)
    d.line([(0,SPLIT),(W,SPLIT)], fill=INK, width=6)   # solid, sealed boundary
    # --- sand layer ---
    sand=[(0,SPLIT)]+[(x,surf_y(x)+TOP) for x in range(0,W+1,12)]+[(W,SPLIT)]
    d.polygon(sand, fill=SAND)
    for (px,py,pr,col) in SANDGRAINS:
        if py>surf_y(px)+TOP: d.ellipse([px-pr,py-pr,px+pr,py+pr], fill=col+(170,))
    # --- water table rising in the sand (wet sand from SPLIT up to wl) ---
    wl = SPLIT - prog*(SPLIT-560)
    d.rectangle([0,wl,W,SPLIT], fill=SANDW+(150,))
    # --- grassy topsoil ---
    grass=[(x,surf_y(x)) for x in range(0,W+1,12)]+[(x,surf_y(x)+TOP) for x in range(W,-1,-12)]
    d.polygon(grass, fill=GRASS)
    # --- pond filling the hollow (rises from bowl bottom toward the surface) ---
    pond_y = BOWL_BOTTOM - prog*(BOWL_BOTTOM-(SURF+6))
    if pond_y < BOWL_BOTTOM:
        hw=bowl_x_at(pond_y)
        poly=[(960-hw,pond_y),(960+hw,pond_y)]
        # follow the bowl floor down and back
        for x in range(int(960+hw),int(960-hw)-1,-8):
            poly.append((x,surf_y(x)))
        d.polygon(poly, fill=WATER+(220,))
        d.line([(960-hw,pond_y),(960+hw,pond_y)], fill=WATERS, width=6)
    d.line(TOPPTS, fill=INK, width=6)
    # --- vegetation ---
    for (x,kind,col,hgt) in VEG:
        y0=surf_y(x)
        if kind=="tuft":
            for dxb in (-14,-6,2,10,16):
                d.line([(x,y0),(x+dxb,y0-hgt+random.randint(-6,6))], fill=GRASSD, width=4)
        else:
            d.line([(x,y0),(x,y0-hgt)], fill=GRASSD, width=4)
            for (fx,fy) in [(x,y0-hgt),(x-12,y0-hgt+10),(x+12,y0-hgt+8),(x,y0-hgt-10)]:
                d.ellipse([fx-9,fy-9,fx+9,fy+9], fill=col+(255,), outline=INK+(120,), width=1)
    # --- rain ---
    for (x,y0,ln,sp) in RAINDROPS:
        yy=(y0+t*sp*FPS)%(H+ln)-ln
        top = pond_y if abs(x-960)<bowl_x_at(pond_y) else surf_y(x)
        if yy<top: d.line([(x,yy),(x-5,yy+ln)], fill=RAIN+(200,), width=3)
    # --- 'blocked' marks: water can't pass the clay (small back-up arrows) ---
    for ax in (770,960,1150):
        ay=SPLIT-30
        d.line([(ax,ay),(ax,ay-54)], fill=INK+(120,), width=6)          # pointing UP (dammed)
        d.polygon([(ax-15,ay-46),(ax+15,ay-46),(ax,ay-76)], fill=INK+(120,))
    return im

if __name__=="__main__":
    for i in range(N):
        draw(i).save(OUTD/f"c_{i:04d}.png")
    print(f"DONE {N} frames -> {OUTD}")
