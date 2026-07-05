#!/usr/bin/env python3
"""Chunk 8 animations:
- map_frames(): the Germany map with glacial ice creeping in from the North
  (Scandinavia) and the South (Alps).
- basin_frames(): a flat-illustration cross-section of a glacier gouging a
  basin into the ground.
"""
import pathlib, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG = ROOT/"main_assets"/"c8"/"img"
MAPD = ROOT/"build"/"c8_map"; MAPD.mkdir(parents=True, exist_ok=True)
BASD = ROOT/"build"/"c8_basin"; BASD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30

def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

# ---------- map ice creep -----------------------------------------------------
MAP_DUR = 13.64
def map_frames():
    n=int(MAP_DUR*FPS)
    m=Image.open(IMG/"map.png").convert("RGBA")
    mw,mh=m.size; MH=1000; MW=int(mw*MH/mh)
    m=m.resize((MW,MH),Image.LANCZOS)
    MX,MY=(W-MW)//2,(H-MH)//2
    base=Image.new("RGB",(W,H),(244,244,242))
    base.paste(m,(MX,MY),m)
    ICE=(214,232,244); ICE2=(180,208,228); FRONT=(120,160,196)
    random.seed(5)
    jag=[random.uniform(-26,26) for _ in range(W+2)]
    for i in range(n):
        p=ease(i/n)
        im=base.copy(); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        # top ice (from the North) advances down to ~48% of the map height
        ty=MY+int(0.50*MH*p)
        pts=[(0,0),(W,0)]+[(x,ty+int(jag[x]*(0.5+0.5*math.sin(x*0.01+i*0.1)))) for x in range(W,-1,-8)]
        d.polygon(pts,fill=ICE+(235,))
        d.line([(x,ty+int(jag[x]*(0.5+0.5*math.sin(x*0.01+i*0.1)))) for x in range(0,W+1,8)],fill=FRONT+(255,),width=5)
        # bottom ice (from the Alps) advances up to ~42%
        by=MY+MH-int(0.44*MH*p)
        pts2=[(0,H),(W,H)]+[(x,by-int(jag[W-x]*(0.5+0.5*math.sin(x*0.012+i*0.1)))) for x in range(W,-1,-8)]
        d.polygon(pts2,fill=ICE2+(235,))
        d.line([(x,by-int(jag[W-x]*(0.5+0.5*math.sin(x*0.012+i*0.1)))) for x in range(0,W+1,8)],fill=FRONT+(255,),width=5)
        # crevasse ticks on the ice
        random.seed(7)
        for _ in range(90):
            cx=random.randint(0,W); cyt=random.randint(MY-20,ty-20)
            if cyt>0: d.line([(cx,cyt),(cx+14,cyt-8)],fill=(255,255,255,150),width=3)
            cyb=random.randint(by+20,H); d.line([(cx,cyb),(cx+14,cyb-8)],fill=(255,255,255,150),width=3)
        im=Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB")
        im.save(MAPD/f"m_{i:04d}.png")
    print("map frames",n)

# ---------- glacier gouges a basin -------------------------------------------
BAS_DUR = 4.34
def basin_frames():
    n=int(BAS_DUR*FPS)
    SKY=(214,228,234); SOIL=(196,168,120); SOIL2=(170,142,96)
    ICE=(224,238,248); ICE2=(188,214,232); INK=(40,40,46)
    random.seed(9)
    grains=[(random.randint(0,W),random.randint(560,H),random.randint(3,7)) for _ in range(500)]
    for i in range(n):
        p=ease(i/n); im=Image.new("RGB",(W,H),SKY); d=ImageDraw.Draw(im,"RGBA")
        # carved basin depth grows; surface = flat sides + central bowl
        depth=int(360*p); cx=960; halfw=560
        def surf(x):
            dx=(x-cx)/halfw
            return 540 + (depth*(1-dx*dx) if abs(dx)<1 else 0)
        # soil body
        pts=[(0,H),(0,540)]+[(x,surf(x)) for x in range(0,W+1,10)]+[(W,540),(W,H)]
        d.polygon(pts,fill=SOIL)
        for (gx,gy,gr) in grains:
            if gy>surf(gx): d.ellipse([gx-gr,gy-gr,gx+gr,gy+gr],fill=SOIL2+(150,))
        d.line([(x,surf(x)) for x in range(0,W+1,8)],fill=INK,width=6)
        # glacier tongue sliding across (left->right), scraping the surface
        gx=int(-500+ (W+700)*p)
        gtop=170
        d.polygon([(gx-560,gtop),(gx+140,gtop),(gx+40,surf(gx)-8),(gx-620,surf(max(0,gx-620))-8)],
                  fill=ICE+(240,))
        d.polygon([(gx-560,gtop),(gx-180,gtop),(gx-230,surf(max(0,gx-230))-8),(gx-620,surf(max(0,gx-620))-8)],
                  fill=ICE2+(220,))
        for cxx in range(gx-560,gx+120,70):
            d.line([(cxx,gtop+10),(cxx-20,surf(max(0,cxx))-20)],fill=(255,255,255,140),width=4)
        # pushed rubble at the front
        for k in range(12):
            rx=gx+120+k*14; ry=surf(rx)-random.randint(4,20)
            d.ellipse([rx-8,ry-8,rx+8,ry+8],fill=SOIL2+(220,))
        im.save(BASD/f"b_{i:04d}.png")
    print("basin frames",n)

if __name__=="__main__":
    map_frames(); basin_frames()
