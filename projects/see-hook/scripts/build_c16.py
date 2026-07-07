#!/usr/bin/env python3
"""Main part - Chunk 16, the FINALE (VO 289.44 -> 313.90s).
Beat A (Verlandung): the misty dawn lake, yellow captions - sand/leaves/silt
drift in, reeds creep from the shore. Beat B: the editorial progression
SEE -> SUMPF -> WIESE. Beat C (the close): the Pusteblume (dandelion, symbol of
transience) then birds at sunset, with the poetic last lines animated as
SCATTERED glowing title words across the screen (like the reference).
"""
import subprocess, pathlib, sys, json, random

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF="ffmpeg"; IMG=MA/"c16"/"img"; SCAN=str(BUILD/"scanlines.png")

VO_START=289.44
SONG_OFFSET=366.34
TOTAL=24.46                              # -> ends 313.90 (VO end)

# segment durations / xfade offsets (see comments)
LAKE_D=15.8; PB_D=6.2; BIRD_D=3.46
XF=0.5; OFF1=15.3; OFF2=21.0             # OFF1: lake->pb ; OFF2: (x1)->birds

GRADE=("eq=contrast=1.05:saturation=1.05:gamma=0.98,"
       "curves=r='0/0.02 1/0.99':b='0/0.03 1/0.965',vignette=PI/5,"
       "noise=alls=5:allf=t")

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p
def at(t):
    if t<0: t=0.0
    m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"0:{m:02d}:{s:02d}.{c:02d}"
def ass_header(styles):
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+"\n".join(styles)+"\n\n")

# ---- prepare a graded 1920x1080 30fps segment from a source clip -------------
def seg(src, ss, dur, out):
    vf=(f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        f"fps=30,{GRADE},setsar=1")
    run([FF,"-y","-ss",str(ss),"-t",str(dur),"-i",str(IMG/src),"-vf",vf,"-an",
         "-r","30","-c:v","libx264","-preset","medium","-crf","20",str(out)],"seg "+src)

def assemble():
    seg("lake.mp4", 9.0, LAKE_D, BUILD/"c16_lake.mp4")
    seg("pusteblume.mp4", 3.5, PB_D, BUILD/"c16_pb.mp4")
    seg("birds.mp4", 2.0, BIRD_D, BUILD/"c16_birds.mp4")
    fc=(f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={OFF1}[x1];"
        f"[x1][2:v]xfade=transition=fade:duration={XF}:offset={OFF2}[v]")
    run([FF,"-y","-i",str(BUILD/"c16_lake.mp4"),"-i",str(BUILD/"c16_pb.mp4"),
         "-i",str(BUILD/"c16_birds.mp4"),"-filter_complex",fc,"-map","[v]",
         "-t",str(TOTAL),"-r","30","-c:v","libx264","-preset","medium","-crf","20",
         str(BUILD/"c16_v.mp4")],"assemble")

# ---- ASS: yellow captions + SEE->SUMPF->WIESE + scattered title text ---------
SCAT_POOL=[(360,232),(980,196),(1540,300),(300,530),(1200,560),(1630,616),
           (520,792),(1010,840),(1452,812),(742,392),(1320,428),(628,300),
           (900,660),(1120,300),(430,660)]

def build_ass():
    d=json.load(open(AUD/"main_transcript.json"))
    words=[]
    def walk(o):
        if isinstance(o,list):[walk(x) for x in o]
        elif isinstance(o,dict):
            if 'start' in o and 'word' in o and len(o['word'])<20: words.append(o)
            [walk(v) for v in o.values() if isinstance(v,(list,dict))]
    walk(d)
    words=[w for w in words if w.get('start') is not None]
    def rel(x): return x-VO_START

    YEL="&H0000E9F4"
    styles=[
      f"Style: Cap,Liberation Sans,52,{YEL},{YEL},{YEL},&H78101010,-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1",
      f"Style: Prog,Anton,116,&H00FFFFFF,&H00FFFFFF,&H00201810,&H64000000,0,0,0,0,100,100,2,0,1,2,3,5,0,0,0,1",
      f"Style: Scat,Liberation Sans,56,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H50000000,-1,0,0,0,100,100,1.5,0,1,2,3,5,0,0,0,1"]
    E=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    def dlg(st,en,style,txt,layer=0):
        E.append(f"Dialogue: {layer},{at(st)},{at(en)},{style},,0,0,0,,{txt}")

    # -- yellow running captions: Verlandung + 'Ganz langsam ... wieder auf' ----
    capw=[w for w in words if 289.44<=w['start']<301.35]
    lines,cur=[],[]
    for w in capw:
        cur.append(w)
        if len(cur)>=5 or w['word'].endswith((".",",","!","?",";",":")): lines.append(cur); cur=[]
    if cur: lines.append(cur)
    for i,ln in enumerate(lines):
        s=max(0.0,rel(ln[0]['start'])-0.05); e=rel(ln[-1]['end'])+0.12
        if i+1<len(lines): e=min(e, rel(lines[i+1][0]['start'])-0.03)
        dlg(s,e,"Cap","{\\fad(90,90)\\blur7}"+" ".join(w['word'] for w in ln))

    # -- SEE -> SUMPF -> WIESE (the transformation) ----------------------------
    pe=rel(301.4)  # progression window until the lake segment ends (~15.3)
    pend=OFF1+XF
    prog=[("SEE",480,548,12.19),("\\h→\\h",706,548,12.55),
          ("SUMPF",900,548,12.75),("\\h→\\h",1210,548,14.35),("WIESE",1408,548,14.93)]
    for txt,x,y,st in prog:
        dlg(st,pend,"Prog",f"{{\\an5\\pos({x},{y})\\fad(300,350)\\blur3}}{txt}")

    # -- scattered glowing title words for the close ---------------------------
    waves=[("W1",16.4,18.9,["NICHTS","EWIGES"]),
           ("W2",18.6,21.15,["NUR","EIN","KURZER","NASSER","MOMENT"]),
           ("W3",20.9,22.5,["GESCHICHTE","EINER","LANDSCHAFT"]),
           ("W4",22.2,TOTAL,["WIR","HABEN","DAS","GLÜCK","ERLEBEN","ZU","DÜRFEN"])]
    # map VO word starts for staggered appearance
    def vstart(word, after):
        for w in words:
            if w['word'].strip(".,–!?").upper()==word and w['start']>after:
                return rel(w['start'])
        return None
    for name,t0,t1,wl in waves:
        rng=random.Random(hash(name)&0xffff)
        anchors=SCAT_POOL[:]; rng.shuffle(anchors)
        after=VO_START+t0-0.6
        for j,word in enumerate(wl):
            x,y=anchors[j%len(anchors)]; x+=rng.randint(-26,26); y+=rng.randint(-22,22)
            fs=rng.choice([50,54,58,62])
            vs=vstart(word, after); ap=max(t0, (vs-0.12) if vs else t0+j*0.18)
            dlg(ap,t1,"Scat",f"{{\\an5\\pos({x},{y})\\fs{fs}\\fad(420,520)\\blur7}}{word}")

    a=BUILD/"c16.ass"; a.write_text(ass_header(styles)+"\n".join(E)+"\n"); return a

def final():
    a=build_ass()
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c16_song.wav")],"songbed")
    fc=(f"[0:v]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.5,fade=t=out:st={TOTAL-1.0}:d=1.0,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c16_v.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c16_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk16.mp4")],"final")
    print("  ->", OUT/"main_chunk16.mp4")

if __name__=="__main__":
    print("[1/2] assemble"); assemble()
    print("[2/2] final"); final()
    print("DONE", round(TOTAL,2),"s")
