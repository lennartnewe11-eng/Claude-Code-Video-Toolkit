#!/usr/bin/env python3
"""Main part - Chunk 8 (VO 123.14 -> ~155.7s): the Ice Age carves the basins.
  1 aside: coal/sand/gravel ('another topic')
  2 animated map: ice creeps in from Scandinavia (N) and the Alps (S), bulldozers
  3 cross-section: a glacier gouges a basin
  4 editorial 3-photo grid: Bodensee / Chiemsee / Starnberger See
"""
import json, subprocess, pathlib, sys
from PIL import Image, ImageOps, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C8=MA/"c8"; IMG=C8/"img"; FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")
MAPD=BUILD/"c8_map"; BASD=BUILD/"c8_basin"

VO_START=123.14; SONG_OFFSET=76.90+VO_START
D_B1,D_B2,D_B3,D_B4=6.66,13.64,4.34,7.93
TOTAL=D_B1+D_B2+D_B3+D_B4
B1_A,B1_B=123.14,129.80

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p
def at(t):
    m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1;c=0
    return f"0:{m:02d}:{s:02d}.{c:02d}"
def ass_header(styles):
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+"\n".join(styles)+"\n\n")
BLK="&H00181818"; YEL="&H0000E9F4"; ICEBLUE="&H00C8822D"

def bordered(src,w,h,out,bw=False):
    im=Image.open(src).convert("RGB")
    if bw: im=ImageOps.autocontrast(ImageOps.grayscale(im),1).convert("RGB")
    im=ImageOps.fit(im,(w,h),Image.LANCZOS).convert("RGBA")
    pad=34; c=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",c.size,(0,0,0,0)); blk=Image.new("RGBA",(w,h),(0,0,0,110))
    sh.paste(blk,(pad+8,pad+14)); sh=sh.filter(ImageFilter.GaussianBlur(13))
    c=Image.alpha_composite(c,sh); c.paste(im,(pad,pad),im); c.save(out); return c.size

def lakes_bg():
    import numpy as np, random as _r
    from PIL import ImageDraw
    W2,H2=1920,1080; rng=np.random.default_rng(3)
    base=np.zeros((H2,W2,3),np.float32); base[:]=(232,206,120)
    base+=rng.normal(0,12,(H2,W2,3))
    img=Image.fromarray(np.clip(base,0,255).astype('uint8'),'RGB'); d=ImageDraw.Draw(img,'RGBA')
    for x in range(0,W2,60): d.line([(x,0),(x,H2)],fill=(150,120,50,24),width=1)
    for y in range(0,H2,60): d.line([(0,y),(W2,y)],fill=(150,120,50,24),width=1)
    def torn(x,y,w,h,c,seed):
        r=_r.Random(seed); pts=[]; step=26
        for xx in range(x,x+w,step): pts.append((xx+r.randint(-14,14), y+r.randint(-16,16)))
        for yy in range(y,y+h,step): pts.append((x+w+r.randint(-16,16), yy+r.randint(-14,14)))
        for xx in range(x+w,x,-step): pts.append((xx+r.randint(-14,14), y+h+r.randint(-16,16)))
        for yy in range(y+h,y,-step): pts.append((x+r.randint(-16,16), yy+r.randint(-14,14)))
        d.polygon(pts,fill=c)
    for k,(x,y,w,h,c) in enumerate([(90,120,780,540,(214,96,40,58)),(980,80,780,380,(70,120,110,70)),
                        (680,560,940,440,(210,120,50,56)),(1320,600,520,420,(60,110,110,62)),
                        (160,720,560,320,(214,96,40,46)),(430,60,520,320,(70,120,110,48))]):
        torn(x,y,w,h,c,k*13+1)
    for _ in range(70):
        yy=rng.integers(0,H2); d.line([(0,yy),(W2,yy)],fill=(255,240,200,14),width=int(rng.integers(1,4)))
    for _ in range(30):
        x0,y0=int(rng.integers(0,W2)),int(rng.integers(0,H2))
        d.line([(x0,y0),(x0+int(rng.integers(20,120)),y0)],fill=(120,90,40,55),width=2)
    img.filter(ImageFilter.GaussianBlur(0.4)).save(BUILD/"c8_lakes_bg.png")

def prep():
    for n in ["coal","sand","gravel"]:
        bordered(IMG/f"{n}.jpg",440,300,BUILD/f"c8_{n}.png",bw=True)
    for n in ["bodensee","chiemsee","starnberg"]:   # B&W first, orange filter comes later
        bordered(IMG/f"{n}.jpg",600,410,BUILD/f"c8_{n}.png",bw=True)
    lakes_bg()

# ---- beat 1: aside ----------------------------------------------------------
def beat_aside():
    a=BUILD/"c8_b1.ass"
    styles=[f"Style: L,Liberation Sans,52,{BLK},{BLK},{BLK},&H00000000,-1,0,0,0,100,100,0,0,1,0,0,8,0,0,0,1",
            f"Style: X,Liberation Sans,120,&H002A45E5,&H002A45E5,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,-4,0,1,0,0,5,0,0,0,1"]
    E=at(D_B1)
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(1.4)},{E},L,,0,0,0,,{{\\an8\\pos(432,690)\\fad(180,0)}}Kohle",
        f"Dialogue: 0,{at(1.9)},{E},L,,0,0,0,,{{\\an8\\pos(960,690)\\fad(180,0)}}Sand",
        f"Dialogue: 0,{at(2.4)},{E},L,,0,0,0,,{{\\an8\\pos(1488,690)\\fad(180,0)}}Kies",
        f"Dialogue: 0,{at(4.7)},{E},X,,0,0,0,,{{\\an5\\pos(960,540)\\frz-8\\fad(160,0)}}* anderes Thema"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    fc=("color=c=white:s=1920x1080:r=30[bg];"
        "[1:v]setsar=1[c1];[bg][c1]overlay=x=212:y=330:shortest=1[a1];"
        "[2:v]setsar=1[c2];[a1][c2]overlay=x=740:y=330:shortest=1[a2];"
        "[3:v]setsar=1[c3];[a2][c3]overlay=x=1268:y=330:shortest=1[base];"
        f"[base]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-f","lavfi","-i","color=c=white:s=1920x1080:r=30",
         "-loop","1","-i",str(BUILD/"c8_coal.png"),"-loop","1","-i",str(BUILD/"c8_sand.png"),
         "-loop","1","-i",str(BUILD/"c8_gravel.png"),"-filter_complex",fc,"-map","[v]",
         "-t",str(D_B1),"-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"c8_b1.mp4")],"aside")

# ---- beat 2: animated map ---------------------------------------------------
def beat_map():
    a=BUILD/"c8_b2.ass"
    styles=[f"Style: N,Liberation Sans,60,{ICEBLUE},{ICEBLUE},&H00FFFFFF,&H00000000,-1,0,0,0,100,100,1,0,1,3,0,8,0,0,0,1",
            f"Style: S,Liberation Sans,60,{ICEBLUE},{ICEBLUE},&H00FFFFFF,&H00000000,-1,0,0,0,100,100,1,0,1,3,0,2,0,0,0,1",
            f"Style: BD,Liberation Sans,150,&H002A45E5,&H002A45E5,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,-8,0,1,3,0,5,0,0,0,1"]
    E=at(D_B2)
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        # 'von Norden aus Skandinavien' ~134.91 -> local 5.11
        f"Dialogue: 0,{at(5.0)},{E},N,,0,0,0,,{{\\an8\\pos(960,40)\\fad(220,0)}}Skandinavien  ↓",
        # 'von Sueden aus den Alpen' ~136.78 -> local 6.98
        f"Dialogue: 0,{at(6.9)},{E},S,,0,0,0,,{{\\an5\\pos(690,860)\\fad(220,0)}}die Alpen  ↑",
        # 'kilometerdicke Bulldozer' ~141.94 -> local 12.8
        f"Dialogue: 0,{at(11.6)},{E},BD,,0,0,0,,{{\\an5\\pos(960,540)\\fad(140,0)\\t(0,200,\\fscx100\\fscy100)\\fscx160\\fscy160}}BULLDOZER"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    fc=(f"[0:v]setsar=1[bg];[bg]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},"
        "noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(MAPD/"m_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_B2),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","18",str(BUILD/"c8_b2.mp4")],"map")

# ---- beat 3: basin cross-section --------------------------------------------
def beat_basin():
    a=BUILD/"c8_b3.ass"
    styles=[f"Style: T,Liberation Sans,72,&H00181818,&H00181818,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,8,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.4)},{at(D_B3)},T,,0,0,0,,{{\\an8\\pos(960,50)\\fad(200,0)}}riesige Becken"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    fc=(f"[0:v]setsar=1[bg];[bg]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},"
        "noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(BASD/"b_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_B3),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","18",str(BUILD/"c8_b3.mp4")],"basin")

# ---- beat 4: editorial lakes grid -------------------------------------------
def beat_lakes():
    # warm-graded, textured editorial collage (ref -2.jpg): big number, grungy
    # background detail, overlapping photos, split-tone grade.
    a=BUILD/"c8_b4.ass"
    styles=[f"Style: Big,Anton,540,&H002438C4,&H002438C4,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1",
            f"Style: Nm,Anton,86,&H00203038,&H00203038,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,0,0,8,0,0,0,1",
            f"Style: Sm,Liberation Sans,38,&H00203038,&H00203038,&H00FFFFFF,&H00000000,0,0,0,0,100,100,4,0,1,0,0,7,0,0,0,1"]
    E=at(D_B4)
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.2)},{E},Sm,,0,0,0,,{{\\an7\\pos(120,60)\\fad(200,0)}}die groessten Seen",
        f"Dialogue: 0,{at(0.2)},{E},Big,,0,0,0,,{{\\an5\\pos(1560,780)\\alpha&H40&}}3",
        f"Dialogue: 0,{at(4.6)},{E},Nm,,0,0,0,,{{\\an8\\pos(430,590)\\fad(160,0)}}Bodensee",
        f"Dialogue: 0,{at(5.5)},{E},Nm,,0,0,0,,{{\\an8\\pos(1010,830)\\fad(160,0)}}Chiemsee",
        f"Dialogue: 0,{at(6.4)},{E},Nm,,0,0,0,,{{\\an8\\pos(1470,470)\\fad(160,0)}}Starnberger See"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    # photos are already B&W -> lay an orange duotone over them (black->brown,
    # white->cream/orange), then place on the warm textured bg.
    DUO=("format=gbrp,curves=r='0/0.16 0.5/0.63 1/0.99':g='0/0.06 0.5/0.40 1/0.72':"
         "b='0/0.05 0.5/0.19 1/0.36'")
    fc=("[0:v]setsar=1[bg];"
        f"[1:v]setsar=1,{DUO},fade=t=in:st=0.3:d=0.4[l1];[bg][l1]overlay=x=90:y=130:shortest=1[a1];"
        f"[2:v]setsar=1,{DUO},fade=t=in:st=1.2:d=0.4[l2];[a1][l2]overlay=x=690:y=380:shortest=1[a2];"
        f"[3:v]setsar=1,{DUO},fade=t=in:st=2.1:d=0.4[l3];[a2][l3]overlay=x=1160:y=40:shortest=1[cmp];"
        "[cmp]eq=saturation=1.02:contrast=1.03,noise=alls=4:allf=t[base];"
        f"[base]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},format=yuv420p[v]")
    run([FF,"-y","-loop","1","-i",str(BUILD/"c8_lakes_bg.png"),
         "-loop","1","-i",str(BUILD/"c8_bodensee.png"),"-loop","1","-i",str(BUILD/"c8_chiemsee.png"),
         "-loop","1","-i",str(BUILD/"c8_starnberg.png"),"-filter_complex",fc,"-map","[v]",
         "-t",str(D_B4),"-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"c8_b4.mp4")],"lakes")

# ---- captions (suppress the editorial aside) --------------------------------
def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is None: continue
            if VO_START-0.2<=st<VO_START+TOTAL and not (B1_A-0.15<=st<B1_B):
                words.append(w)
    lines,cur=[],[]
    for w in words:
        cur.append(w)
        if len(cur)>=6 or w["word"].endswith((".","?","!",",",";",":")):
            lines.append(cur); cur=[]
    if cur: lines.append(cur)
    style=("Style: Cap,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H0000E9F4,&H78101010,"
           "-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i,ln in enumerate(lines):
        s=max(0.0,ln[0]["start"]-VO_START-0.05); e=ln[-1]["end"]-VO_START+0.12
        if i+1<len(lines): e=min(e, lines[i+1][0]["start"]-VO_START-0.03)
        txt="{\\fad(90,90)\\blur7}"+" ".join(w["word"] for w in ln)
        ev.append(f"Dialogue: 0,{at(s)},{at(e)},Cap,,0,0,0,,{txt}")
    (BUILD/"c8_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c8_song.wav")],"songbed")
    ass=(BUILD/"c8_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c8_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c8_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk8.mp4")],"final")
    print("  ->", OUT/"main_chunk8.mp4")

if __name__=="__main__":
    prep()
    print("[1/5] aside"); beat_aside()
    print("[2/5] map");   beat_map()
    print("[3/5] basin"); beat_basin()
    print("[4/5] lakes"); beat_lakes()
    (BUILD/"c8_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c8_b1","c8_b2","c8_b3","c8_b4"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c8_concat.txt"),
         "-c","copy",str(BUILD/"c8_full.mp4")],"concat")
    print("[5/5] final"); final()
    print("DONE", round(TOTAL,2),"s")
