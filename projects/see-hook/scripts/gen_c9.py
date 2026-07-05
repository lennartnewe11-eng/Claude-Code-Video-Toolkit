#!/usr/bin/env python3
"""Chunk 9 assets.
- tongue_frame(): the tongue photo (Wortwitz Gletscher-ZUNGE) on a full-frame
  yellow field.
- editorial_frames(): the ref_b look -> a grey VO waveform (Tonspur) on white at
  the top with a moving playhead, and collages accumulating below (depth->250 m,
  Geschiebemergel liner + water = wasserdicht, 2-in-1 Bagger-Service badge).
"""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c9"
C8   = ROOT/"main_assets"/"c8"/"img"
C4   = ROOT/"main_assets"/"c4"
BUILD= ROOT/"build"
EDD  = BUILD/"c9_ed"; EDD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
YEL = (255,205,0)
ANTON = "/home/user/Claude-Code-Video-Toolkit/projects/see-hook/fonts/Anton-Regular.ttf"
LIB   = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIBB  = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
def anton(s): return ImageFont.truetype(ANTON, s)
def lib(s):   return ImageFont.truetype(LIB, s)
def libb(s):  return ImageFont.truetype(LIBB, s)
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

# ---------------------------------------------------------------- tongue frame
def tongue_frame():
    im=Image.open(IMG/"ref"/"ref_c.jpg").convert("RGB")
    a=np.array(im)
    # bounding box of the non-yellow inner photo (the mouth)
    yellow=(np.abs(a[:,:,0]-255)<24)&(np.abs(a[:,:,1]-205)<28)&(a[:,:,2]<70)
    photo=~yellow
    ys,xs=np.where(photo)
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    mouth=im.crop((x0,y0,x1+1,y1+1))
    # place as a portrait card, centred on a full-frame yellow field
    cvs=Image.new("RGB",(W,H),YEL)
    ch=int(H*0.82); cw=int(mouth.width*ch/mouth.height)
    mouth=mouth.resize((cw,ch),Image.LANCZOS)
    # soft drop shadow
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    px,py=(W-cw)//2,(H-ch)//2
    sd.rectangle([px+14,py+20,px+cw+14,py+ch+20],fill=(120,90,0,120))
    sh=sh.filter(ImageFilter.GaussianBlur(22))
    cvs=Image.alpha_composite(cvs.convert("RGBA"),sh).convert("RGB")
    cvs.paste(mouth,(px,py))
    cvs.save(BUILD/"c9_tongue.png")
    print("tongue frame ->", BUILD/"c9_tongue.png")

# ---------------------------------------------------------------- editorial ---
ED_DUR = 30.01           # 162.84 .. 192.85
WAVE_L, WAVE_R = 90, 1830
WAVE_Y0, WAVE_Y1 = 46, 300      # bigger Tonspur
BG = (248,247,243)
INK= (38,36,34)
ORG= (226,88,36)

def _duotone(path, w, h, dark, light):
    im=ImageOps.grayscale(Image.open(path).convert("RGB"))
    im=ImageOps.autocontrast(im,2)
    im=ImageOps.fit(im,(w,h),Image.LANCZOS)
    g=np.asarray(im,np.float32)/255.0
    d=np.array(dark,np.float32); l=np.array(light,np.float32)
    out=d[None,None,:]*(1-g[:,:,None])+l[None,None,:]*g[:,:,None]
    return Image.fromarray(out.astype("uint8"),"RGB")

def _card(photo, pad=10, border=(30,28,26)):
    w,h=photo.size
    c=Image.new("RGBA",(w+2*pad,h+2*pad),(255,255,255,255))
    d=ImageDraw.Draw(c); d.rectangle([0,0,w+2*pad-1,h+2*pad-1],outline=border,width=3)
    c.paste(photo,(pad,pad)); return c

# --- pre-rendered region layers (full-canvas RGBA, transparent elsewhere) -----
def _layer(): return Image.new("RGBA",(W,H),(0,0,0,0))

def depth_layer():
    """left region: vertical 0->250 m depth scale, Koelner Dom submerged."""
    L=_layer(); d=ImageDraw.Draw(L)
    xc0=150; wcol=230; ysurf=375; yfloor=995; scale=(yfloor-ysurf)/250.0  # px/m
    cx=xc0+wcol//2
    # water column tint
    d.rectangle([xc0,ysurf,xc0+wcol,yfloor],fill=(150,186,206,95))
    # surface + floor rules
    d.line([(xc0-32,ysurf),(xc0+wcol+16,ysurf)],fill=INK,width=4)
    d.line([(xc0-32,yfloor),(xc0+wcol+16,yfloor)],fill=INK,width=4)
    for m in range(0,251,50):
        y=ysurf+m*scale; d.line([(xc0-32,y),(xc0-12,y)],fill=INK,width=3)
        d.text((xc0-92,y-15),f"{m}",font=lib(28),fill=INK)
    d.text((xc0-92,ysurf-44),"0 m · Oberflaeche",font=lib(24),fill=INK)
    d.text((xc0-92,yfloor+10),"250 m · Grund",font=lib(24),fill=INK)
    # Koelner Dom silhouette (157 m) standing on the floor -> fully submerged
    domH=157*scale; base=yfloor; top=base-domH
    body_w=104
    d.rectangle([cx-body_w//2, top+domH*0.42, cx+body_w//2, base],fill=(48,44,40,255))
    for sx in (cx-30,cx+30):                       # the two spires
        d.polygon([(sx-20,top+domH*0.45),(sx+20,top+domH*0.45),(sx,top)],fill=(48,44,40,255))
        d.line([(sx,top),(sx,top-16)],fill=(48,44,40,255),width=3)
    d.text((cx,base-domH-30),"Koelner Dom",font=lib(22),fill=(30,28,26),anchor="mm")
    d.text((cx,base-domH-8),"157 m — komplett unter Wasser",font=lib(19),fill=(90,86,80),anchor="mm")
    # drop arrow surface -> floor (just right of the column)
    ax=xc0+wcol+34
    d.line([(ax,ysurf+6),(ax,yfloor-12)],fill=ORG,width=5)
    d.polygon([(ax-13,yfloor-32),(ax+13,yfloor-32),(ax,yfloor-6)],fill=ORG)
    # big number, upper-right of the region (clear of the Dom)
    nx=490
    d.text((nx,430),"deshalb so tief:",font=lib(24),fill=INK,anchor="mm")
    d.text((nx,510),"250",font=anton(120),fill=(20,20,20),anchor="mm")
    d.text((nx,600),"METER TIEF",font=libb(30),fill=ORG,anchor="mm")
    return L

def mergel_layer():
    """centre region: basin bowl lined with Geschiebemergel (no water yet)."""
    L=_layer(); d=ImageDraw.Draw(L)
    bx0,bx1=670,1230; by0,by1=405,978
    Y,X=np.mgrid[by0:by1,bx0:bx1]
    cx=(bx0+bx1)/2; hw=(bx1-bx0)/2*0.94
    rim=by0+118; bowl_d=376
    surf=rim + bowl_d*np.clip(1-((X-cx)/hw)**2,0,1)   # concave bowl (deep centre)
    rock=(Y>surf)
    rgb=np.zeros((by1-by0,bx1-bx0,3),np.uint8); alpha=np.zeros((by1-by0,bx1-bx0),np.uint8)
    rng=np.random.default_rng(4); grain=rng.normal(0,10,rock.shape)
    base=np.clip(196+grain,0,255)
    for c in range(3): rgb[:,:,c]=np.where(rock,base,0)
    alpha[rock]=255
    # Geschiebemergel liner: a real cracked-clay photo band coating the bowl
    # surface (Ton = toniger Schutt -> the actual sealing material)
    clay=np.asarray(_duotone(C4/"dry.jpg", bx1-bx0, by1-by0, (44,34,24),(150,120,84)))
    liner=(Y>surf)&(Y<surf+42)
    for c in range(3): rgb[:,:,c][liner]=clay[:,:,c][liner]
    reg=Image.fromarray(np.dstack([rgb,alpha]),"RGBA")
    L.paste(reg,(bx0,by0),reg)
    d=ImageDraw.Draw(L)
    d.rectangle([bx0-4,by0-4,bx1+4,by1+4],outline=INK,width=3)
    d.text(((bx0+bx1)//2, by0-40),"DER ABDICHTUNGS-SERVICE",font=libb(34),fill=INK,anchor="mm")
    # label pointing to the liner
    d.line([(cx+150,by1-60),(bx1+70,by1-20)],fill=INK,width=2)
    d.text((bx1+80,by1-42),"Geschiebemergel",font=libb(28),fill=(78,64,48))
    d.text((bx1+80,by1-10),"toniger Schutt · dichtet ab",font=lib(22),fill=INK)
    return L, (bx0,bx1,surf,by0,by1)

def water_layer(geom):
    bx0,bx1,surf,by0,by1=geom
    L=_layer()
    Y,X=np.mgrid[by0:by1,bx0:bx1]
    wlevel=by0+165
    water=(Y>wlevel)&(Y<surf)          # water sits inside the concave bowl
    rgb=np.zeros((by1-by0,bx1-bx0,3),np.uint8); alpha=np.zeros((by1-by0,bx1-bx0),np.uint8)
    rng=np.random.default_rng(7); shim=rng.normal(0,6,water.shape)
    rgb[:,:,0]=np.where(water,np.clip(60+shim,0,255),0)
    rgb[:,:,1]=np.where(water,np.clip(122+shim,0,255),0)
    rgb[:,:,2]=np.where(water,np.clip(150+shim,0,255),0)
    alpha[water]=205
    reg=Image.fromarray(np.dstack([rgb,alpha]),"RGBA")
    L.paste(reg,(bx0,by0),reg)
    return L

def seal_layer():
    """right region: 2-in-1 stamp badge."""
    L=_layer(); d=ImageDraw.Draw(L)
    cx,cy=1560,590; r=185
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=ORG,width=8)
    d.ellipse([cx-r+16,cy-r+16,cx+r-16,cy+r-16],outline=ORG,width=3)
    d.text((cx,cy-118),"2-in-1",font=anton(118),fill=(20,20,20),anchor="mm")
    grn=(40,150,80)
    for i,t in enumerate(["ausbaggern","abdichten"]):
        yy=cy+18+i*62; bx=cx-150
        d.rounded_rectangle([bx,yy-22,bx+40,yy+18],radius=6,outline=grn,width=4)
        d.line([(bx+9,yy-1),(bx+17,yy+11)],fill=grn,width=5)     # tick
        d.line([(bx+17,yy+11),(bx+34,yy-14)],fill=grn,width=5)
        d.text((bx+58,yy-2),t,font=libb(38),fill=INK,anchor="lm")
    d.text((cx,cy+146),"im selben Arbeitsgang",font=lib(28),fill=INK,anchor="mm")
    # teaser at the bottom
    d.text((cx,cy+r+64),"… und das war noch nicht alles",font=libb(30),fill=ORG,anchor="mm")
    return L

def _paste(base, layer, p, slide=46):
    """alpha-composite `layer` onto base with reveal progress p (fade + slide-up)."""
    if p<=0: return base
    e=ease(p); dy=int((1-e)*slide)
    a=layer.split()[3].point(lambda v:int(v*e))
    lay=layer.copy(); lay.putalpha(a)
    shifted=Image.new("RGBA",(W,H),(0,0,0,0))
    shifted.paste(lay,(0,-dy),lay)
    return Image.alpha_composite(base, shifted)

def editorial_frames():
    n=int(ED_DUR*FPS)
    wave=Image.open(BUILD/"c9_wave.png").convert("RGBA")
    # tint waveform grey + place
    wl=wave.resize((WAVE_R-WAVE_L, WAVE_Y1-WAVE_Y0),Image.LANCZOS)
    # base canvas (white, faint grid, baseline) built once
    canvas0=Image.new("RGBA",(W,H),BG+(255,))
    g=ImageDraw.Draw(canvas0)
    for x in range(0,W,64): g.line([(x,0),(x,H)],fill=(210,206,198,90),width=1)
    for y in range(0,H,64): g.line([(0,y),(W,y)],fill=(210,206,198,90),width=1)
    g.line([(WAVE_L,(WAVE_Y0+WAVE_Y1)//2),(WAVE_R,(WAVE_Y0+WAVE_Y1)//2)],fill=(200,196,188,255),width=1)
    canvas0.alpha_composite(wl,(WAVE_L,WAVE_Y0))
    g=ImageDraw.Draw(canvas0)
    # tiny timeline tick labels under the waveform (ref look)
    ticks=[(0.0,"01"),(0.20,"02"),(0.42,"03"),(0.62,"04"),(0.82,"05")]
    for fr,lab in ticks:
        x=int(WAVE_L+(WAVE_R-WAVE_L)*fr)
        g.line([(x,WAVE_Y1+4),(x,WAVE_Y1+16)],fill=INK,width=1)
        g.text((x,WAVE_Y1+22),lab,font=lib(20),fill=(120,116,110))
    g.text((WAVE_L,20),"TONSPUR · Eiszeit / Becken",font=libb(24),fill=INK)
    # region layers
    Ldepth=depth_layer()
    Lmergel,geom=mergel_layer()
    Lwater=water_layer(geom)
    Lseal=seal_layer()
    # reveal times (local seconds within editorial)
    t_depth=1.9; t_mergel=6.9; t_water=16.4; t_seal=21.3
    for i in range(n):
        t=i/FPS
        base=canvas0.copy()
        base=_paste(base,Ldepth, (t-t_depth)/0.7)
        base=_paste(base,Lmergel,(t-t_mergel)/0.7)
        base=_paste(base,Lwater, (t-t_water)/1.2, slide=0)
        base=_paste(base,Lseal,  (t-t_seal)/0.7)
        # moving playhead across the waveform
        px=int(WAVE_L+(WAVE_R-WAVE_L)*(t/ED_DUR))
        d=ImageDraw.Draw(base)
        d.line([(px,WAVE_Y0-10),(px,WAVE_Y1+2)],fill=ORG,width=3)
        d.ellipse([px-5,WAVE_Y0-16,px+5,WAVE_Y0-6],fill=ORG)
        base.convert("RGB").save(EDD/f"e_{i:04d}.png")
    print("editorial frames",n)

if __name__=="__main__":
    tongue_frame(); editorial_frames()
