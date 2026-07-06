#!/usr/bin/env python3
"""Chunk 12 assets (Deutschlandkarte - the payoff: lakes cluster where the ice was).
The source relief has no marked lakes, so the two lake CLUSTERS are shown as
red-orange dot swarms (North = Mecklenburg Seenplatte + SH + Havelland; South =
Alpenvorland) that reveal in sync with the VO; the middle stays empty.
Small camera moves (gentle push-in + slight drift N->S->wide) are baked here.
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c12"/"img"
BUILD= ROOT/"build"
MAPF = BUILD/"c12_map_f"; MAPF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
W2, H2 = 2200, 1238                          # oversized base canvas for camera moves
YMAP=np.array([247,233,25],np.float32)
ORG =(232,58,26); ORGG=(242,120,40)
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

DUR=14.0
N_REVEAL, S_REVEAL = 4.2, 7.0                # dot cluster reveal times (VO-rel)

def _build_base():
    im=Image.open(IMG/"de_relief.png").convert("RGBA")
    a=np.asarray(im).astype(np.float32); A=a[...,3]
    ys,xs=np.where(A>25); im=im.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
    a=np.asarray(im).astype(np.float32); mh,mw,_=a.shape
    land=a[...,3]>25
    gray=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    gl=gray[land]; lo,hi=np.percentile(gl,3),np.percentile(gl,99)
    shade=np.clip((gray-lo)/(hi-lo),0,1)
    grey=np.clip(70+shade*150,0,255)                       # relief grey on yellow
    # fit map ~1150 tall, centred in the oversized canvas
    th=1150; s=th/mh; tw=int(mw*s)
    reliefR=Image.fromarray(grey.astype(np.uint8),"L").resize((tw,th),Image.LANCZOS)
    landR  =Image.fromarray((land*255).astype(np.uint8),"L").resize((tw,th),Image.LANCZOS)
    mx=(W2-tw)//2; my=(H2-th)//2
    canvas=np.empty((H2,W2,3),np.float32); canvas[:]=YMAP[None,None,:]
    # white graticule across the whole poster
    gl_img=Image.new("L",(W2,H2),0); gdr=ImageDraw.Draw(gl_img)
    step=150; ox,oy=50,40
    majx=set(range(ox,W2,step*3)); majy=set(range(oy,H2,step*3))
    for xx in range(ox,W2,step): gdr.line([(xx,0),(xx,H2)],fill=255,width=2 if xx in majx else 1)
    for yy in range(oy,H2,step): gdr.line([(0,yy),(W2,yy)],fill=255,width=2 if yy in majy else 1)
    ga=(np.asarray(gl_img.filter(ImageFilter.GaussianBlur(0.4)),np.float32)/255.*0.5)[...,None]
    canvas=canvas*(1-ga)+np.array([255,255,255],np.float32)[None,None,:]*ga
    relA=np.asarray(landR,np.float32)/255.; relG=np.asarray(reliefR,np.float32)
    for c in range(3):
        canvas[my:my+th,mx:mx+tw,c]=canvas[my:my+th,mx:mx+tw,c]*(1-relA)+relG*relA
    rng=np.random.default_rng(4); canvas=np.clip(canvas+rng.normal(0,2.0,canvas.shape),0,255)
    return Image.fromarray(canvas.astype(np.uint8),"RGB"), (mx,my,tw,th)

def _dots(box):
    mx,my,tw,th=box; rng=np.random.default_rng(12); D=[]
    def scatter(n,fx0,fx1,fy0,fy1,rmin,rmax,cl):
        for _ in range(n):
            fx=rng.uniform(fx0,fx1); fy=rng.uniform(fy0,fy1)
            x=mx+fx*tw; y=my+fy*th; r=rng.uniform(rmin,rmax)
            el=rng.uniform(1.0,2.1); ang=rng.uniform(0,math.pi)
            D.append((x,y,r,el,ang,cl))
    # NORTH: SH + Mecklenburg Seenplatte + Havelland/Brandenburg
    scatter(10,0.34,0.52,0.05,0.13,4,8,"N")            # Schleswig-Holstein
    scatter(16,0.52,0.82,0.11,0.25,5,11,"N")           # Mecklenburg Seenplatte (dense)
    scatter(9 ,0.46,0.72,0.25,0.34,4,9,"N")            # Havelland / Brandenburg
    # SOUTH: Alpenvorland incl. Bodensee
    scatter(3 ,0.18,0.26,0.85,0.90,6,10,"S")           # Bodensee corner
    scatter(14,0.38,0.80,0.81,0.91,4,10,"S")           # Alpenvorland lakes
    return D

def _draw_dots(img, D, box, cam, t):
    cx,cy,wh=cam; ww=wh*16/9; left=cx-ww/2; top=cy-wh/2; sc=W/ww
    d=ImageDraw.Draw(img,"RGBA")
    pulse=0.5+0.5*math.sin(t*3.3)
    revN=ease((t-N_REVEAL)/0.7); revS=ease((t-S_REVEAL)/0.7)
    for (x,y,r,el,ang,cl) in D:
        rev=revN if cl=="N" else revS
        if rev<=0.01: continue
        sx=(x-left)*sc; sy=(y-top)*sc; rr=r*sc
        if not(-30<sx<W+30 and -30<sy<H+30): continue
        a_core=int(235*rev*(0.75+0.25*pulse)); a_glow=int(120*rev*(0.5+0.5*pulse))
        dx=rr*el*math.cos(ang); dy=rr*el*math.sin(ang)
        # glow
        d.ellipse([sx-rr*el-6,sy-rr*el-6,sx+rr*el+6,sy+rr*el+6],fill=ORGG+(a_glow,))
        d.ellipse([sx-rr*el,sy-rr*el,sx+rr*el,sy+rr*el],fill=ORG+(a_core,))
    return img

def _cam(t):
    kf=[(0.0,1100,619,1180),(2.0,1100,610,1120),(4.6,1100,585,1082),
        (6.2,1100,600,1076),(7.6,1100,656,1082),(9.6,1100,642,1088),
        (11.7,1100,619,1158),(DUR,1100,619,1158)]
    for i in range(len(kf)-1):
        t0,x0,y0,w0=kf[i]; t1,x1,y1,w1=kf[i+1]
        if t0<=t<=t1:
            p=ease((t-t0)/max(1e-6,t1-t0))
            return (x0+(x1-x0)*p, y0+(y1-y0)*p, w0+(w1-w0)*p)
    return kf[-1][1:]

def de_frames():
    base,box=_build_base(); D=_dots(box)
    base.save(BUILD/"c12_base.png")
    n=int(DUR*FPS)
    for i in range(n):
        t=i/FPS; cx,cy,wh=_cam(t); ww=wh*16/9
        left=cx-ww/2; top=cy-wh/2
        crop=base.crop((int(left),int(top),int(left+ww),int(top+wh))).resize((W,H),Image.LANCZOS)
        crop=_draw_dots(crop,D,box,(cx,cy,wh),t)
        crop.save(MAPF/f"m_{i:04d}.png")
    print("de_frames",n,"dots",len(D))

if __name__=="__main__":
    de_frames()
