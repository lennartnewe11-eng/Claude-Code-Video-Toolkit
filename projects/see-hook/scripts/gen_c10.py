#!/usr/bin/env python3
"""Chunk 10 assets (Toteis / round holes).
- map_prep(): turn the coloured Mecklenburg/Brandenburg map into a clean B&W
  map with all labels/borders removed. Water = bright low-saturation pixels;
  the sea/background is the border-connected water, enclosed water = lakes.
- (ice hero + Toteis formation animation are rendered in build_c10.py / here.)
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c10"/"img"
BUILD= ROOT/"build"
MAPF = BUILD/"c10_map_f"; MAPF.mkdir(parents=True, exist_ok=True)
FORMF= BUILD/"c10_form"; FORMF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

# ------------------------------------------------------------- clean B&W map --
def map_prep():
    im=Image.open(IMG/"map_mv_bb.jpg").convert("RGB")
    a=np.array(im).astype(np.int16); mh,mw,_=a.shape
    mx=a.max(2); mn=a.min(2); sat=mx-mn
    water=((mn>192)&(sat<26)).astype(np.uint8)*255          # lakes+sea+bg
    wm=Image.fromarray(water,"L")
    # close thin text/roads that cut across water, then open to de-speckle
    wm=wm.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    # flood the border-connected water -> that is sea / outside
    sea=wm.copy(); seed=(255)
    fillm=sea.load()
    ImageDraw.floodfill(sea,(2,2),128,thresh=40)
    for p in [(mw//2,2),(mw-3,2),(2,mh//2),(mw-3,mh//2),(2,mh-3),(mw//2,mh-3),(mw-3,mh-3)]:
        if sea.getpixel(p)==255: ImageDraw.floodfill(sea,p,128,thresh=40)
    seaA=np.array(sea)
    is_water=np.array(wm)>127
    is_sea=(seaA==128)
    # close the sea mask so labels sitting in the sea get swallowed
    seaimg=Image.fromarray((is_sea*255).astype(np.uint8),"L")
    seaimg=seaimg.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    is_sea=np.array(seaimg)>127
    is_lake=is_water&~is_sea
    # open the lake mask: thin (text) strokes vanish, blobby lakes survive
    lk=Image.fromarray((is_lake*255).astype(np.uint8),"L")
    lk=lk.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    is_lake=np.array(lk)>127
    # ---- render clean B&W map (flat land -> all land labels vanish) -------
    out=np.full((mh,mw,3),150,np.float32)                   # land flat grey
    for c in range(3): out[:,:,c]=np.where(is_sea, 232.0, out[:,:,c])   # sea light
    # lakes: soft anti-aliased white with a dark rim (avoids blocky edges)
    lakeL=Image.fromarray((is_lake*255).astype(np.uint8),"L").filter(ImageFilter.GaussianBlur(1.4))
    lakeA=(np.array(lakeL,np.float32)/255.0)[:,:,None]
    rimL=(Image.fromarray((is_lake*255).astype(np.uint8),"L")
          .filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.7)))
    rimA=np.clip(np.array(rimL,np.float32)/255.0-lakeA[:,:,0],0,1)[:,:,None]
    out=out*(1-rimA)+70.0*rimA          # dark rim
    out=out*(1-lakeA)+250.0*lakeA       # water
    # subtle paper grain
    rng=np.random.default_rng(2); out=np.clip(out+rng.normal(0,4,out.shape),0,255)
    Image.fromarray(out.astype(np.uint8),"RGB").save(BUILD/"c10_map.png")
    # also save the lake mask (for highlight placement)
    Image.fromarray((is_lake*255).astype(np.uint8),"L").save(BUILD/"c10_lakes.png")
    print("map_prep -> c10_map.png  lake%%", round(is_lake.mean()*100,2))

# ------------------------------------------------- ice block full-screen hero -
def ice_hero_img():
    bg=Image.open(IMG/"iceblock_orig.jpg").convert("RGB")
    bg=ImageOps.fit(bg,(W,H),Image.LANCZOS).filter(ImageFilter.GaussianBlur(22))
    bg=ImageOps.autocontrast(bg,2)
    bg=Image.eval(bg,lambda v:int(v*0.62))                 # darken backdrop
    cvs=bg.convert("RGBA")
    ice=Image.open(IMG/"iceblock.png").convert("RGBA")
    cw=1480; ch=int(ice.height*cw/ice.width)
    ice=ice.resize((cw,ch),Image.LANCZOS)
    px,py=(W-cw)//2,(H-ch)//2
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rectangle([px+20,py+30,px+cw+20,py+ch+30],fill=(0,0,0,150))
    sh=sh.filter(ImageFilter.GaussianBlur(30))
    cvs=Image.alpha_composite(cvs,sh)
    cvs.alpha_composite(ice,(px,py))
    cvs.convert("RGB").save(BUILD/"c10_hero.png")
    print("ice hero ->", BUILD/"c10_hero.png")

# ---------------------------------------- Toteis formation cross-section ------
FORM_DUR = 9.40
def _rounded_mask(w,h,rad):
    m=Image.new("L",(w,h),0); d=ImageDraw.Draw(m)
    d.rounded_rectangle([0,0,w-1,h-1],radius=rad,fill=255); return m

def formation_frames():
    n=int(FORM_DUR*FPS)
    ice=Image.open(IMG/"iceblock.png").convert("RGBA")   # cut-out ice block
    # soil + sky bases
    Y,X=np.mgrid[0:H,0:W].astype(np.float32)
    rng=np.random.default_rng(11)
    soilg=rng.normal(0,1,(H,W))
    soilg=np.array(Image.fromarray(((soilg-soilg.min())/np.ptp(soilg)*255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.7)),np.float32)/255.0
    stones=rng.random((H,W))                      # for debris stipple
    cx=960.0; surf_base=560.0
    def clamp(v): return max(0.0,min(1.0,v))
    for i in range(n):
        t=i/FPS
        burial=clamp((t-0.5)/1.7)
        melt  =clamp((t-2.8)/2.7)
        collapse=clamp((t-5.2)/2.4)
        fill  =clamp((t-7.3)/1.9)
        g=np.exp(-((X-cx)/300.0)**2)
        mound=70*burial*(1-collapse)
        bowl =260*ease(collapse)
        surf =surf_base - mound*g + bowl*g
        ground=(Y>surf)
        # base image: warm sky over grainy soil
        img=np.empty((H,W,3),np.float32)
        sky=np.array([233,224,205],np.float32); soil=np.array([150,126,98],np.float32)
        base=soil[None,None,:]*(0.7+0.6*soilg[:,:,None])
        img[:]=np.where(ground[:,:,None], np.clip(base,0,255), sky[None,None,:])
        pim=Image.fromarray(img.astype(np.uint8),"RGB")
        # ---- ice block (embedded), shrinking as it melts ----
        scale=1.0-0.99*melt
        if scale>0.10:
            bw=int(520*scale); bh=int(300*scale**0.7)
            ib=ice.resize((bw,bh),Image.LANCZOS)
            # tint a touch bluer + fade near full melt
            byi=int(660 - 0*bh)             # block vertical centre
            bx0=int(cx-bw/2); by0=int(byi-bh/2)
            m=ib.split()[3].point(lambda v:int(v*(1-0.4*melt)))
            pim.paste(ib.convert("RGB"),(bx0,by0),m)
        d=ImageDraw.Draw(pim,"RGBA")
        # ---- meltwater puddle where the ice was (grows with melt, then bowl) ----
        # ---- Geroell: debris band hugging the surface over the centre ----
        if burial>0:
            dband=(Y>surf)&(Y<surf+90)&(g[:,:]>0.18)
            arr=np.asarray(pim).astype(np.float32)
            db=np.array([96,84,70],np.float32)
            arr[dband]=arr[dband]*0.4+db*0.6
            # stone speckle
            spot=dband&(stones>0.86)
            arr[spot]=np.array([60,52,44])
            spot2=dband&(stones<0.06)
            arr[spot2]=np.array([180,168,150])
            pim=Image.fromarray(arr.astype(np.uint8),"RGB"); d=ImageDraw.Draw(pim,"RGBA")
        # ---- falling debris particles during burial ----
        if 0.5<t<2.4:
            pr=np.random.default_rng(1000+i)
            for _ in range(70):
                sx=cx+pr.uniform(-330,330); prog=pr.random()
                sy=120+prog*(surf_base-150)
                r=pr.uniform(2,5); c=int(pr.uniform(60,120))
                d.ellipse([sx-r,sy-r,sx+r,sy+r],fill=(c,c-8,c-18,220))
        # ---- water fills the collapsed bowl (rises from the deepest point) ----
        if fill>0:
            arr=np.asarray(pim).astype(np.float32)
            bottom=surf_base+bowl; near_rim=surf_base+18
            wl=bottom-(bottom-near_rim)*fill          # water surface descends -> rises in cup
            water=(Y>wl)&(Y<surf)                     # between water level and cup floor
            wcol=np.array([70,120,150],np.float32)
            shim=rng.normal(0,5,(H,W))
            for c in range(3):
                arr[:,:,c]=np.where(water, np.clip(wcol[c]+shim,0,255), arr[:,:,c])
            pim=Image.fromarray(arr.astype(np.uint8),"RGB")
        pim.save(FORMF/f"f_{i:04d}.png")
    print("formation frames",n)

# ------------------------------------------------------- lake blob detection --
def _lake_blobs(minarea=70):
    from collections import deque
    m=np.array(Image.open(BUILD/"c10_lakes.png").convert("L"))>127
    mh,mw=m.shape; seen=np.zeros_like(m,bool); blobs=[]
    ys,xs=np.where(m)
    for sy,sx in zip(ys.tolist(),xs.tolist()):
        if seen[sy,sx]: continue
        q=deque([(sy,sx)]); seen[sy,sx]=True; comp=[]
        while q:
            y,x=q.popleft(); comp.append((y,x))
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<mh and 0<=nx<mw and m[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True; q.append((ny,nx))
        comp=np.array(comp); a=len(comp)
        if a<minarea: continue
        blobs.append((a, comp[:,1].mean(), comp[:,0].mean(),
                      max(comp[:,1].max()-comp[:,1].min(), comp[:,0].max()-comp[:,0].min())))
    blobs.sort(reverse=True)
    return blobs   # (area, cx, cy, diam) in map pixels

# --------------------------------------------------- map camera + highlights --
MAP_DUR = 7.90
def map_frames():
    mp=Image.open(BUILD/"c10_map.png").convert("RGB")
    MW,MH=mp.size
    blobs=_lake_blobs()
    # focal lakes (map px): Mueritz, Schweriner See, cluster over Mueritz
    foc=[(581,839),(265,740),(560,760)]
    # camera keyframes: (t, cx, cy, win_w)   win aspect 16:9
    kf=[(0.0, 581,839,560),(2.1, 581,839,540),(3.4, 300,760,560),
        (5.0, 560,770,640),(6.0, 540,820,1060),(MAP_DUR,540,820,1060)]
    def cam(t):
        for i in range(len(kf)-1):
            t0,x0,y0,w0=kf[i]; t1,x1,y1,w1=kf[i+1]
            if t0<=t<=t1:
                p=ease((t-t0)/max(1e-6,t1-t0))
                return (x0+(x1-x0)*p, y0+(y1-y0)*p, w0+(w1-w0)*p)
        return kf[-1][1:]
    n=int(MAP_DUR*FPS)
    for i in range(n):
        t=i/FPS; cx,cy,w=cam(t); h=w*9/16
        left=cx-w/2; top=cy-h/2
        left=min(max(left,0),MW-w); top=min(max(top,0),MH-h)
        crop=mp.crop((int(left),int(top),int(left+w),int(top+h))).resize((W,H),Image.LANCZOS)
        d=ImageDraw.Draw(crop,"RGBA")
        sc=W/w
        # which lakes to highlight: close-ups -> focal; wide -> all
        wide = w>820
        pulse=0.5+0.5*math.sin(t*4.2)
        for a,bx,by,dia in blobs:
            sx=(bx-left)*sc; sy=(by-top)*sc
            if not(-40<sx<W+40 and -40<sy<H+40): continue
            if wide:
                r=max(9,dia*sc*0.6)+3*pulse
                d.ellipse([sx-r,sy-r,sx+r,sy+r],outline=(226,88,36,150),width=3)
            else:
                # only ring the lake nearest the current camera centre
                if (bx-cx)**2+(by-cy)**2 < 60**2:
                    r=max(26,dia*sc*0.7)
                    for k,al in ((14,60),(7,110),(0,220)):
                        d.ellipse([sx-r-k,sy-r-k,sx+r+k,sy+r+k],outline=(226,88,36,al),width=4)
        crop.convert("RGB").save(MAPF/f"m_{i:04d}.png")   # grain added in ffmpeg
    print("map frames",n,"blobs",len(blobs))

if __name__=="__main__":
    map_prep(); map_frames()
