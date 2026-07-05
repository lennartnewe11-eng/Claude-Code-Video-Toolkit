#!/usr/bin/env python3
"""Chunk 10 assets (Toteis / round holes).
- map_prep(): turn the coloured Mecklenburg/Brandenburg map into a clean B&W
  map with all labels/borders removed. Water = bright low-saturation pixels;
  the sea/background is the border-connected water, enclosed water = lakes.
- (ice hero + Toteis formation animation are rendered in build_c10.py / here.)
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
from collections import deque

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c10"/"img"
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
LIB  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIBB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
ANTON= str(FONTS/"Anton-Regular.ttf")
MAPF = BUILD/"c10_map_f"; MAPF.mkdir(parents=True, exist_ok=True)
FORMF= BUILD/"c10_form"; FORMF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
YEL=(255,205,0)
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def _f(path,size): return ImageFont.truetype(path,size)
def _tsp(d,xy,txt,font,fill,sp=0):        # letter-spaced text
    x,y=xy
    for ch in txt:
        d.text((x,y),ch,font=font,fill=fill)
        x+=d.textlength(ch,font=font)+sp

# ---------------------------------------------- clean B&W shaded-relief map ---
# Source is a coloured shaded-relief render of Mecklenburg-Vorpommern with an
# Alamy watermark (tiled "alamy" letters + a big centre wordmark + a black
# footer bar).  We: crop the footer, turn the relief into a dark B&W hillshade,
# inpaint the centre wordmark, and detect the *real* lakes (genuinely cyan,
# B>>R) so the scattered neutral watermark letters are never mistaken for water.
def map_prep():
    im=Image.open(IMG/"relief_mv.jpg").convert("RGB").crop((0,0,1300,880))
    a=np.asarray(im).astype(np.float32); mh,mw,_=a.shape
    R,G,B=a[...,0],a[...,1],a[...,2]
    mx=a.max(2); mn=a.min(2); sat=mx-mn
    gray=0.299*R+0.587*G+0.114*B
    white=(mn>236)&(sat<16); land=~white                    # paper vs landmass
    # ---- lake candidates: pale, low-sat, and clearly cyan (B>=R) ----
    lake0=(mn>150)&(sat<62)&(B>=R-4)&land
    bgm=Image.fromarray((white*255).astype(np.uint8),"L").filter(
        ImageFilter.MaxFilter(9)).filter(ImageFilter.MaxFilter(9))
    near_bg=np.asarray(bgm.filter(ImageFilter.GaussianBlur(6)),np.float32)>40
    lakec=lake0&~near_bg                                     # drop coastal fringe
    lc=Image.fromarray((lakec*255).astype(np.uint8),"L").filter(
        ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    lakec=np.asarray(lc)>127
    # keep only blobs that are genuinely cyan (mean B-R>18) -> real water;
    # scattered watermark letters are neutral (B-R<10) and are rejected.
    seen=np.zeros_like(lakec,bool); clean=np.zeros_like(lakec,bool)
    ys,xs=np.where(lakec)
    for sy,sx in zip(ys.tolist(),xs.tolist()):
        if seen[sy,sx]: continue
        q=deque([(sy,sx)]); seen[sy,sx]=True; comp=[]
        while q:
            y,x=q.popleft(); comp.append((y,x))
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                ny,nx=y+dy,x+dx
                if 0<=ny<mh and 0<=nx<mw and lakec[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True; q.append((ny,nx))
        comp=np.array(comp); ar=len(comp)
        if ar<45: continue
        cy,cx=comp[:,0],comp[:,1]
        if (B[cy,cx]-R[cy,cx]).mean()<18: continue          # neutral -> watermark
        for y,x in comp: clean[y,x]=True
    # round the lake blobs so they read as the near-circular Toteisloecher
    lkr=(Image.fromarray((clean*255).astype(np.uint8),"L")
         .filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
         .filter(ImageFilter.GaussianBlur(1.6)))
    is_lake=np.asarray(lkr)>110
    # ---- remove the Alamy watermark (centre wordmark + tiled "alamy" letters).
    # It is a semi-transparent WHITE overlay: watermarked pixels are brighter AND
    # more desaturated than their local neighbourhood.  Detect that thin stroke
    # mask, then diffusion-inpaint (blur-and-restore) so the surrounding relief
    # texture flows back in -> no flat grey patches, no readable letters.
    def blurf(x,r): return np.asarray(Image.fromarray(np.clip(x,0,255)
                        .astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),np.float32)
    bg=blurf(gray,7); bsat=blurf(sat,7)
    lowbg=np.asarray(Image.fromarray(gray.astype(np.uint8)).resize(
        (mw//14,mh//14),Image.BOX).resize((mw,mh),Image.BILINEAR),np.float32)
    wm=((gray-bg)>6)&((bsat-sat)>4)&land&(~is_lake)
    wmi=Image.fromarray((wm*255).astype(np.uint8),"L").filter(ImageFilter.MaxFilter(5))
    wm=np.asarray(wmi)>127
    # seed with the low-frequency background (removes the big centre wordmark's
    # brightness bias) then diffuse neighbouring relief texture back in.
    grf=gray.copy(); grf[wm]=lowbg[wm]
    for _ in range(60): gb=blurf(grf,1.6); grf[wm]=gb[wm]
    # the bold centre wordmark is a DENSE cluster of thick strokes -> even after
    # diffusion its letter pattern faintly survives.  Isolate that dense cluster
    # (close nearby strokes, then erode so only the big solid block remains; the
    # sparse tiled letters do not survive) and flatten the whole block toward the
    # low-freq background with a soft edge, so no letter structure is left.
    dense=(wmi.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.MinFilter(21))
           .filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(9)))
    dm=np.asarray(dense,np.float32)/255.0
    grf=grf*(1-dm)+lowbg*dm
    # ---- render dark B&W hillshade (lakes rendered dark; yellow added later) --
    gl=grf[land]; lo,hi=np.percentile(gl,3),np.percentile(gl,99)
    shade=np.clip((grf-lo)/(hi-lo),0,1)
    out=np.full((mh,mw),19.0,np.float32)                    # near-black backdrop
    out[land]=48+shade[land]*168                            # shaded grey relief
    lmask_soft=np.asarray(Image.fromarray((is_lake*255).astype(np.uint8),"L")
                          .filter(ImageFilter.GaussianBlur(1.1)),np.float32)/255.0
    out=out*(1-lmask_soft)+34.0*lmask_soft                  # lake bed a touch dark
    rng=np.random.default_rng(2); out=np.clip(out+rng.normal(0,2.5,out.shape),0,255)
    Image.fromarray(out.astype(np.uint8),"L").convert("RGB").save(BUILD/"c10_map.png")
    Image.fromarray((is_lake*255).astype(np.uint8),"L").save(BUILD/"c10_lakes.png")
    print("map_prep -> c10_map.png  lake%%", round(is_lake.mean()*100,3))

# ------------------------------------------------- ice block full-screen hero -
def ice_hero_img():
    # the real photograph of the ice block, full frame (no cut-out)
    bg=Image.open(IMG/"iceblock_orig.jpg").convert("RGB")
    bg=ImageOps.fit(bg,(W,H),Image.LANCZOS,centering=(0.5,0.45))
    bg=ImageOps.autocontrast(bg,1)
    bg.save(BUILD/"c10_hero.png")
    print("ice hero (full photo) ->", BUILD/"c10_hero.png")

# ---------------------------------------- Toteis formation cross-section ------
FORM_DUR = 9.40
def _rounded_mask(w,h,rad):
    m=Image.new("L",(w,h),0); d=ImageDraw.Draw(m)
    d.rounded_rectangle([0,0,w-1,h-1],radius=rad,fill=255); return m

# phases: (start_t, step, title, sub)
_PH=[(0.5,"01","BEGRABEN","Eisblock unter Geroell verschuettet"),
     (2.8,"02","SCHMILZT","der Eisklotz taut im Untergrund"),
     (5.2,"03","SACKT EIN","der Boden bricht ueber dem Hohlraum nach"),
     (7.3,"04","WASSERLOCH","ein fast kreisrunder See bleibt")]
_FK=_f(LIBB,21); _FS=_f(LIB,25); _FN=_f(ANTON,120); _FT=_f(ANTON,58)
def _editorial_overlay(pim,t):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    ink=(30,27,22); ink2=(96,88,74)
    # top-left kicker + rule
    _tsp(d,(72,52),"TOTEIS",_FK,ink+(255,),6)
    _tsp(d,(210,55),"·  ENGL. DEAD ICE",_FK,ink2+(255,),4)
    d.line([(74,90),(74+372,90)],fill=ink+(120,),width=2)
    # current phase (with a short fade-in on change)
    idx=0
    for k,(st,*_) in enumerate(_PH):
        if t>=st: idx=k
    st,step,title,sub=_PH[idx]
    fade=ease(min(1.0,(t-st)/0.4)); A=int(255*fade)
    d.rectangle([74,112,90,168],fill=YEL+(A,))              # accent bar
    d.text((108,104),title,font=_FT,fill=ink+(A,))
    _tsp(d,(110,176),sub,_FS,ink2+(int(220*fade),),1)
    # top-right ghost step number + label
    num=step; nw=d.textlength(num,font=_FN)
    d.text((1848-nw,44),num,font=_FN,fill=(150,140,120,150))
    lab="SCHRITT"; lw=d.textlength(lab,font=_FK)
    _tsp(d,(1848-lw-6,26),lab,_FK,ink2+(200,),5)
    # four-step progress ticks (bottom-left, above caption safe area)
    for k in range(4):
        on = k<=idx
        x=110+k*30
        d.ellipse([x-6,900-6,x+6,900+6],
                  fill=(YEL+(230,)) if on else (0,0,0,0),
                  outline=(ink+(200,)) if not on else (YEL+(255,)),width=2)
    return Image.alpha_composite(pim.convert("RGBA"),ov).convert("RGB")

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
        pim=_editorial_overlay(pim,t)
        pim.save(FORMF/f"f_{i:04d}.png")
    print("formation frames",n)

# ------------------------------------------------------- lake blob detection --
def _lake_blobs(minarea=45):
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
                      max(np.ptp(comp[:,1]), np.ptp(comp[:,0]))))
    blobs.sort(reverse=True)
    return blobs   # (area, cx, cy, diam) in map pixels

# --------------------------------------------- map camera + pulsing yellow ----
MAP_DUR = 7.90
def map_frames():
    mp=Image.open(BUILD/"c10_map.png").convert("RGB")
    MW,MH=mp.size
    # pre-blur the lake mask once for the bloom halo
    lk=Image.open(BUILD/"c10_lakes.png").convert("L")
    lk_core=lk                                             # crisp water body
    lk_glow=lk.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(11))
    blobs=_lake_blobs()
    big=[b for b in blobs if b[0]>=120]                    # focal lakes for pans
    # camera keyframes: (t, cx, cy, win_w)  aspect 16:9, over the Seenplatte
    kf=[(0.0, 708,682, 560),(2.0, 660,660, 520),(3.5, 589,655, 500),
        (5.0, 660,668, 860),(6.4, 690,650,1290),(MAP_DUR,690,650,1290)]
    def cam(t):
        for i in range(len(kf)-1):
            t0,x0,y0,w0=kf[i]; t1,x1,y1,w1=kf[i+1]
            if t0<=t<=t1:
                p=ease((t-t0)/max(1e-6,t1-t0))
                return (x0+(x1-x0)*p, y0+(y1-y0)*p, w0+(w1-w0)*p)
        return kf[-1][1:]
    n=int(MAP_DUR*FPS)
    yc=np.array(YEL,np.float32); yg=np.array([255,178,60],np.float32)
    for i in range(n):
        t=i/FPS; cx,cy,w=cam(t); h=w*9/16
        left=min(max(cx-w/2,0),MW-w); top=min(max(cy-h/2,0),MH-h)
        box=(int(left),int(top),int(left+w),int(top+h))
        base=np.asarray(mp.crop(box).resize((W,H),Image.LANCZOS),np.float32)
        core=np.asarray(lk_core.crop(box).resize((W,H),Image.LANCZOS),np.float32)/255.0
        glow=np.asarray(lk_glow.crop(box).resize((W,H),Image.BILINEAR),np.float32)/255.0
        pulse=0.5+0.5*math.sin(t*3.6)                      # gentle heartbeat
        ga=(0.30+0.45*pulse)*glow[...,None]                # halo bloom
        ca=(0.72+0.28*pulse)*core[...,None]                # bright water fill
        out=base*(1-ga)+yg[None,None,:]*ga
        out=out*(1-ca)+yc[None,None,:]*ca
        crop=Image.fromarray(np.clip(out,0,255).astype(np.uint8),"RGB")
        # thin pulsing ring on the lake nearest the camera centre (close-ups)
        if w<720:
            d=ImageDraw.Draw(crop,"RGBA"); sc=W/w
            for a,bx,by,dia in big:
                if (bx-cx)**2+(by-cy)**2<70**2:
                    sx=(bx-left)*sc; sy=(by-top)*sc; r=max(30,dia*sc*0.72)
                    for k,al in ((16,55),(8,110)):
                        al=int(al*(0.6+0.4*pulse))
                        d.ellipse([sx-r-k,sy-r-k,sx+r+k,sy+r+k],outline=YEL+(al,),width=3)
                    break
        crop.save(MAPF/f"m_{i:04d}.png")                   # grain added in ffmpeg
    print("map frames",n,"blobs",len(blobs),"focal",len(big))

if __name__=="__main__":
    import sys
    steps=sys.argv[1:] or ["hero","form","map"]
    if "hero" in steps: ice_hero_img()
    if "form" in steps: formation_frames()
    if "map"  in steps: map_prep(); map_frames()
