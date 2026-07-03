#!/usr/bin/env python3
"""Two photo cards (See, dry earth) stacked behind each other on a plain white
background; each is pulled to the FRONT when it is being talked about.
Renders build/c4_cards/k_%04d.png."""
import pathlib, math
from PIL import Image, ImageOps, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
C4 = ROOT/"main_assets"/"c4"
OUTD = ROOT/"build"/"c4_cards"; OUTD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
DUR = 6.49
N = int(DUR*FPS)
SWAP0, SWAP1 = 2.85, 3.45            # See-front -> dry-front transition window

CW, CH, BORD = 900, 600, 20
def make_card(path):
    im = ImageOps.fit(Image.open(path).convert("RGB"), (CW-2*BORD, CH-2*BORD), Image.LANCZOS)
    card = Image.new("RGB", (CW, CH), (252, 250, 246))
    card.paste(im, (BORD, BORD))
    return card.convert("RGBA")

CARD_SEE = make_card(C4/"see.jpg")
CARD_DRY = make_card(C4/"dry.jpg")

# front / back placement (card centre, scale, rotation)
FRONT = (910, 545, 1.00, 0.0)
BACK  = (1080, 470, 0.84, -5.0)

def lerp(a, b, u): return a+(b-a)*u
def place(u):       # u=0 front, u=1 back
    return (lerp(FRONT[0],BACK[0],u), lerp(FRONT[1],BACK[1],u),
            lerp(FRONT[2],BACK[2],u), lerp(FRONT[3],BACK[3],u))

def blit(base, card, cx, cy, scale, rot):
    w,h=int(CW*scale),int(CH*scale)
    c=card.resize((w,h),Image.LANCZOS).rotate(rot,expand=True,resample=Image.BICUBIC)
    pad=40
    canvas=Image.new("RGBA",(c.width+2*pad,c.height+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",canvas.size,(0,0,0,0))
    shm=c.split()[3].point(lambda a:int(a*0.32))
    blk=Image.new("RGBA",c.size,(0,0,0,255)); blk.putalpha(shm)
    sh.paste(blk,(pad+6,pad+12),blk); sh=sh.filter(ImageFilter.GaussianBlur(16))
    canvas=Image.alpha_composite(canvas,sh); canvas.paste(c,(pad,pad),c)
    base.alpha_composite(canvas,(int(cx-canvas.width/2),int(cy-canvas.height/2)))

def smooth(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

def draw(i):
    t=i/FPS
    p=smooth((t-SWAP0)/(SWAP1-SWAP0))      # 0 -> See front, 1 -> dry front
    base=Image.new("RGBA",(W,H),(255,255,255,255))
    see=place(p)          # See: front(0) -> back(1)
    dry=place(1-p)        # dry: back(0) -> front(1)
    if p<0.5:             # See in front -> draw dry first
        blit(base,CARD_DRY,*dry); blit(base,CARD_SEE,*see)
    else:
        blit(base,CARD_SEE,*see); blit(base,CARD_DRY,*dry)
    return base.convert("RGB")

if __name__=="__main__":
    for i in range(N): draw(i).save(OUTD/f"k_{i:04d}.png")
    print(f"DONE {N} frames -> {OUTD}")
