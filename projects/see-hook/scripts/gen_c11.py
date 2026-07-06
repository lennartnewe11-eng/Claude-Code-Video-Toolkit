#!/usr/bin/env python3
"""Chunk 11 assets (Rinnenseen / Schleswig-Holstein).
- sh_poster_prep(): turn the coloured SH relief (with roads/rivers/labels, and
  mirror-flipped) into a STATIC Swiss-poster: yellow ground, grey B&W hillshade,
  white lat/long graticule; the long, narrow Rinnenseen get a red-orange accent.
- sh_poster_frames(): hold the poster, pulse the lakes (no camera move).
- glencoe_hero(): the 35mm film-strip photo of a glacial valley placed on a warm
  dark backdrop, full-frame, ready for a slow film-camera push-in.
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
from collections import deque

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c11"/"img"
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
MAPF = BUILD/"c11_map_f"; MAPF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
YMAP=np.array([247,233,25],np.float32)      # Swiss-poster yellow ground
ORG =np.array([232,58,26],np.float32)       # red-orange lake accent
ORGG=np.array([242,120,40],np.float32)      # lake glow
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def _tsp(d,xy,txt,font,fill,sp=0):
    x,y=xy
    for ch in txt:
        d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp

def _blurf(x,r):
    return np.asarray(Image.fromarray(np.clip(x,0,255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(r)),np.float32)

# ------------------------------------------------- static SH Swiss-poster ------
def sh_poster_prep():
    im=Image.open(IMG/"sh_relief.png").convert("RGBA")   # source orientation (Ostsee = east/right)
    a=np.asarray(im).astype(np.float32)
    A=a[...,3]; land0=A>40
    ys,xs=np.where(land0); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    im=im.crop((int(x0),int(y0),int(x1)+1,int(y1)+1))
    a=np.asarray(im).astype(np.float32); mh,mw,_=a.shape
    R,G,B,A=a[...,0],a[...,1],a[...,2],a[...,3]
    land=A>40
    gray=0.299*R+0.587*G+0.114*B
    # ---- classify overlays to erase from the relief ----
    road=(R-G>32)&(R-B>44)&(R>140)&land                 # strongly-red roads only
    water=(B>R+10)&(B>G+2)&(B>110)&land                 # lakes + rivers (blue)
    ink =(gray<36)&land                                 # near-black labels/borders
    # thin dark linework (roads/rivers/borders/labels) = darker than local bg but
    # NOT broad mountain shadow (which the local blur also darkens)
    lines=((_blurf(gray,3)-gray)>15)&land
    erase=(road|water|ink|lines)&land
    # coastal fringe (shallow blue drawn around the shoreline) -> not a lake
    nonland=Image.fromarray(((~land)*255).astype(np.uint8),"L")
    near_coast=np.asarray(nonland.filter(ImageFilter.MaxFilter(9)).filter(
        ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(8)),np.float32)>30
    # ---- lakes = SIZABLE inland blue blobs (Rinnenseen); thin rivers dropped ----
    lk=Image.fromarray(((water&~near_coast)*255).astype(np.uint8),"L").filter(
        ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    wm=np.asarray(lk)>127
    seen=np.zeros_like(wm,bool); clean=np.zeros_like(wm,bool)
    for sy,sx in zip(*[c.tolist() for c in np.where(wm)]):
        if seen[sy,sx]: continue
        q=deque([(sy,sx)]); seen[sy,sx]=True; comp=[]
        while q:
            y,x=q.popleft(); comp.append((y,x))
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<mh and 0<=nx<mw and wm[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True; q.append((ny,nx))
        if len(comp)<120: continue                      # drop river specks
        for y,x in comp: clean[y,x]=True
    is_lake=clean
    # ---- clean grey hillshade: inpaint roads/rivers/labels by diffusion ----
    grf=gray.copy(); bg=_blurf(gray,8)
    m=erase; grf[m]=bg[m]
    for _ in range(48): gb=_blurf(grf,1.6); grf[m]=gb[m]
    grf=_blurf(grf,0.9)                                 # soften the harsh emboss
    gl=grf[land]; lo,hi=np.percentile(gl,4),np.percentile(gl,99)
    shade=np.clip((grf-lo)/(hi-lo),0,1)
    grey=np.clip(96+shade*130,0,255)                    # lighter poster relief 96..226
    # ---- fit whole map into a poster box, right-aligned with margins ----
    def fit(imgL, boxw, boxh):
        s=min(boxw/mw, boxh/mh); return imgL.resize((int(mw*s),int(mh*s)),Image.LANCZOS), s
    reliefL=Image.fromarray(grey.astype(np.uint8),"L")
    landL  =Image.fromarray((land*255).astype(np.uint8),"L")
    lakeL  =Image.fromarray((is_lake*255).astype(np.uint8),"L")
    BOXW,BOXH=1330,940
    reliefR,s=fit(reliefL,BOXW,BOXH)
    landR =landL.resize(reliefR.size,Image.LANCZOS)
    lakeR =lakeL.resize(reliefR.size,Image.LANCZOS)
    px=(W-reliefR.size[0])//2+70; py=(H-reliefR.size[1])//2  # centred, slight right bias
    # yellow canvas + white graticule (full poster frame)
    canvas=np.empty((H,W,3),np.float32); canvas[:]=YMAP[None,None,:]
    gl_img=Image.new("L",(W,H),0); gdr=ImageDraw.Draw(gl_img)
    step=150; ox,oy=60,40
    majx=set(range(ox,W,step*3)); majy=set(range(oy,H,step*3))
    for xx in range(ox,W,step): gdr.line([(xx,0),(xx,H)],fill=255,width=2 if xx in majx else 1)
    for yy in range(oy,H,step): gdr.line([(0,yy),(W,yy)],fill=255,width=2 if yy in majy else 1)
    ga=(np.asarray(gl_img.filter(ImageFilter.GaussianBlur(0.4)),np.float32)/255.*0.5)[...,None]
    canvas=canvas*(1-ga)+np.array([255,255,255],np.float32)[None,None,:]*ga
    # paste relief (grey) where land, using land alpha
    full_land=np.zeros((H,W),np.float32); full_lake=np.zeros((H,W),np.float32)
    relA=np.asarray(landR,np.float32)/255.
    relG=np.asarray(reliefR,np.float32)
    yy0,yy1=max(0,py),min(H,py+reliefR.size[1]); xx0,xx1=max(0,px),min(W,px+reliefR.size[0])
    sy0,sx0=yy0-py,xx0-px
    sub_a=relA[sy0:sy0+(yy1-yy0), sx0:sx0+(xx1-xx0)]
    sub_g=relG[sy0:sy0+(yy1-yy0), sx0:sx0+(xx1-xx0)]
    for c in range(3):
        canvas[yy0:yy1,xx0:xx1,c]=canvas[yy0:yy1,xx0:xx1,c]*(1-sub_a)+sub_g*sub_a
    full_land[yy0:yy1,xx0:xx1]=sub_a
    lkA=np.asarray(lakeR,np.float32)/255.
    full_lake[yy0:yy1,xx0:xx1]=lkA[sy0:sy0+(yy1-yy0), sx0:sx0+(xx1-xx0)]
    rng=np.random.default_rng(3); canvas=np.clip(canvas+rng.normal(0,2.0,canvas.shape),0,255)
    Image.fromarray(canvas.astype(np.uint8),"RGB").save(BUILD/"c11_map.png")
    Image.fromarray((full_lake*255).astype(np.uint8),"L").save(BUILD/"c11_lakes.png")
    print("sh_poster_prep -> c11_map.png  lake%%",round(full_lake.mean()*100,3),
          "map scale",round(s,3))

# ---------------------------------------------- pulsing lakes (no camera) ------
MAP_DUR=5.5
def sh_poster_frames():
    base=np.asarray(Image.open(BUILD/"c11_map.png").convert("RGB"),np.float32)
    core=np.asarray(Image.open(BUILD/"c11_lakes.png").convert("L"),np.float32)/255.
    glow=np.asarray(Image.open(BUILD/"c11_lakes.png").convert("L")
                    .filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(12)),
                    np.float32)/255.
    n=int(MAP_DUR*FPS)
    for i in range(n):
        t=i/FPS; pulse=0.5+0.5*math.sin(t*3.4)
        ga=(0.26+0.42*pulse)*glow[...,None]; ca=(0.80+0.20*pulse)*core[...,None]
        out=base*(1-ga)+ORGG[None,None,:]*ga
        out=out*(1-ca)+ORG[None,None,:]*ca
        Image.fromarray(np.clip(out,0,255).astype(np.uint8),"RGB").save(MAPF/f"m_{i:04d}.png")
    print("sh_poster_frames",n)

# ---------- 35mm film-strip frame (ref: the Glencoe negative) for the filler ---
# window where the GIF shows through; everything else = film base + sprockets +
# light-leak + frame numbers.  Saved as one RGBA overlay (window = transparent).
WIN=(96,168,1824,912)                       # x0,y0,x1,y1 photo window
def film_frame():
    ov=Image.new("RGBA",(W,H),(20,17,14,255))          # film base (warm near-black)
    d=ImageDraw.Draw(ov)
    x0,y0,x1,y1=WIN
    # sprocket perforations, two rows
    cream=(232,226,208,255); pw,ph=78,86; pitch=120
    for (by0,by1) in [(30,30+ph),(H-30-ph,H-30)]:
        x=28
        while x+pw<W-10:
            d.rounded_rectangle([x,by0,x+pw,by1],radius=15,fill=cream)
            x+=pitch
    # frame numbers + tick ruler along the bottom rebate (film-orange)
    fo=(234,150,44,255)
    try: fn=ImageFont.truetype(str(FONTS/"Anton-Regular.ttf"),46)
    except: fn=ImageFont.load_default()
    d.text((150,y1+14),"14",font=fn,fill=fo)
    d.text((980,y1+14),"14A",font=fn,fill=fo)
    tx=x0
    while tx<x1:
        h=18 if (tx//30)%5==0 else 10
        d.line([(tx,H-30),(tx,H-30-h)],fill=(210,196,150,220),width=2); tx+=30
    # carve the transparent photo window
    win=Image.new("L",(W,H),0); ImageDraw.Draw(win).rectangle([x0,y0,x1,y1],fill=255)
    ov.putalpha(Image.composite(Image.new("L",(W,H),0), ov.getchannel("A"), win))
    # ---- light-leak layer: soft coloured fog along the top edge, bleeding down --
    leak=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(leak)
    blobs=[(180,(255,40,80),150),(520,(255,120,40),150),(900,(255,60,120),140),
           (1300,(255,150,40),130),(1650,(40,200,210),120)]
    for cx,col,al in blobs:
        ld.ellipse([cx-260,-160,cx+260,300],fill=col+(al,))
    leak=leak.filter(ImageFilter.GaussianBlur(70))
    # keep the leak mostly to the top third
    fade=Image.new("L",(W,H),0)
    for yy in range(H):
        v=max(0,int(200*(1-yy/430))) if yy<430 else 0
        ImageDraw.Draw(fade).line([(0,yy),(W,yy)],fill=v)
    leak.putalpha(Image.composite(leak.getchannel("A"),Image.new("L",(W,H),0),fade))
    Image.alpha_composite(leak,ov).save(BUILD/"c11_film.png")   # leak under frame base
    print("film_frame -> c11_film.png  window",WIN)

# ---------- Hochdruckreiniger: cut-out on white, blue editorial type layered ---
BLUE=(18,58,208)
def washer_hero():
    w=Image.open(IMG/"washer.png").convert("RGBA")
    ys,xs=np.where(np.asarray(w)[...,3]>10)
    w=w.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
    th=930; tw=int(w.width*th/w.height); w=w.resize((tw,th),Image.LANCZOS)
    cvs=Image.new("RGB",(W,H),(247,246,243))           # near-white paper
    d=ImageDraw.Draw(cvs)
    fb=ImageFont.truetype(str(FONTS/"Anton-Regular.ttf") if False else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",232)
    def ctext(txt,y,fill):
        twid=d.textlength(txt,font=fb); d.text(((W-twid)/2,y),txt,font=fb,fill=fill)
    # BEHIND: big blue word, then the machine occludes its lower half
    ctext("HOCHDRUCK",150,BLUE)
    wx=(W-tw)//2; wy=(H-th)//2+16
    # soft contact shadow under the machine
    sh=Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(sh).ellipse([wx+40,wy+th-60,wx+tw-40,wy+th+70],fill=(0,0,0,60))
    cvs=Image.alpha_composite(cvs.convert("RGBA"),sh.filter(ImageFilter.GaussianBlur(22))).convert("RGB")
    cvs.paste(w,(wx,wy),w)
    d=ImageDraw.Draw(cvs)
    # IN FRONT: big blue word over the machine's lower body
    ctext("REINIGER",690,BLUE)
    # small editorial tag
    ft=ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",30)
    _tsp(d,(96,96),"UNTER ENORMEM DRUCK",ft,BLUE,4)
    ft2=ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",30)
    d.text((96,H-70),"Schmelzwasser · wie ein Hochdruckreiniger",font=ft2,fill=BLUE)
    cvs.save(BUILD/"c11_wash.png"); print("washer_hero -> c11_wash.png")

if __name__=="__main__":
    import sys
    steps=sys.argv[1:] or ["map","film","wash"]
    if "map"  in steps: sh_poster_prep(); sh_poster_frames()
    if "film" in steps: film_frame()
    if "wash" in steps: washer_hero()
