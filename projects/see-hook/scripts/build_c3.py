#!/usr/bin/env python3
"""Main part - Chunk 3 (VO 35.45s -> ~49.58s), same style + 3 new tools.

  1  Hockney 'joiner' of the tree filler video (reassembled from tiles)  "Mit dem Boden unter unseren Fuessen ist es genau dasselbe"
  2  flat-cartoon cross-section: sand/gravel = sieve, water seeps away    "Steht der Untergrund aus Sand oder Kies ... verschwindet in der Tiefe"
  3  red poster-typography beat (scattered thin words + 'regnet' cascade) "Egal wie viel es regnet, hier bleibt nichts stehen"
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF = "ffmpeg"
SCAN = str(BUILD/"scanlines.png")
HOCK = BUILD/"c3_hockney"
SIEVE = BUILD/"c3_sieve"

VO_START   = 35.45
SONG_OFFSET = 76.90 + VO_START
D_HOCK, D_SIEVE, D_RED = 3.00, 8.73, 2.40
TOTAL = D_HOCK + D_SIEVE + D_RED           # 14.13
RED_A, RED_B = 47.20, 49.58                 # absolute range covered by beat 3
REDHEX = "0xD73533"

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[v]")

def run(cmd, label=""):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p

def enc_seq(seqdir, pat, dur, dst):
    fc=(f"[0:v]{NORM},{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL)
    run([FF,"-y","-framerate","30","-i",str(seqdir/pat),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(dur),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/dst)],dst)

# beat 1: just show the tree filler clip plainly (the Hockney joiner effect is
# kept in gen_hockney.py for a later video, not used here).
def beat_tree():
    fc=(f"[0:v]{NORM},{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL)
    run([FF,"-y","-i",str(MA/'c3'/'tree.mp4'),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_HOCK),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"m3_b1.mp4")],"tree")

def beat_sieve():   enc_seq(SIEVE,"s_%04d.png",D_SIEVE,"m3_b2.mp4")

# ---- beat 3: red poster typography ------------------------------------------
def at(t):
    h=int(t//3600); t-=h*3600; m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

def write_red_ass():
    styles=[
        "Style: Word,Liberation Sans,74,&H00101014,&H00101014,&H00101014,&H00000000,0,0,0,0,100,100,2,0,1,0,0,7,0,0,0,1",
        "Style: WordU,Liberation Sans,88,&H00101014,&H00101014,&H00101014,&H00000000,0,0,1,0,100,100,2,0,1,0,0,7,0,0,0,1",
        "Style: Casc,Liberation Sans,60,&H00101014,&H00101014,&H00101014,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
    ]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    END=at(D_RED)
    # scattered thin words (\an7 = top-left anchor at pos); bottom-right kept
    # clear for the black & white photo.
    scattered=[("Egal",240,170,0.10,"Word"),("wie viel",770,150,0.30,"Word"),
               ("es",1300,160,0.50,"Word"),("hier bleibt",720,430,0.70,"Word"),
               ("nichts",1060,470,0.95,"WordU"),("stehen",760,720,1.15,"Word")]
    for txt,x,y,st,sty in scattered:
        ev.append(f"Dialogue: 0,{at(st)},{END},{sty},,0,0,0,,"
                  f"{{\\pos({x},{y})\\fad(220,180)}}{txt}")
    # 'regnet' cascade down the left-centre, overlapping, staggered (rain-like)
    x0,y0,step=210,415,44
    for k in range(11):
        x=x0+((k%3)-1)*10; y=y0+k*step
        st=0.45+k*0.11
        ev.append(f"Dialogue: 0,{at(st)},{END},Casc,,0,0,0,,"
                  f"{{\\pos({x},{y})\\fad(140,120)}}regnet")
    header=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+"\n".join(styles)+"\n\n")
    (BUILD/"m3_red.ass").write_text(header+"\n".join(ev)+"\n")

def beat_red():
    write_red_ass()
    red=(BUILD/"m3_red.ass").as_posix()
    # red poster bg + scattered/cascading type, with an aesthetic B&W photo set
    # hard-edged into the bottom-right (like the portrait in the reference).
    fc=(f"color=c={REDHEX}:s=1920x1080:r=30[bg];"
        # B&W photo is present from the start (with the red bg); only the type
        # animates in on top of it.
        "[0:v]scale=640:-1,setsar=1[bw];"
        f"[bg][bw]overlay=x=1170:y=560:shortest=1[base];"
        f"[base]ass={red}:fontsdir={FONTS.as_posix()}[pre];"
        "[1:v]scale=1920:1080,setsar=1[sc];"
        "[pre][sc]blend=all_mode=multiply:all_opacity=0.12:shortest=1[m];"
        "[m]noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-loop","1","-i",str(MA/'c3'/'bw.jpg'),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_RED),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","18",str(BUILD/"m3_b3.mp4")],"red")

# ---- captions (skip the red-typography range; that beat carries its own text)-
def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is None: continue
            if VO_START-0.2 <= st < VO_START+TOTAL and not (RED_A-0.15 <= st < RED_B):
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
        s=ln[0]["start"]-VO_START-0.05; e=ln[-1]["end"]-VO_START+0.12
        if i+1<len(lines):
            e=min(e, lines[i+1][0]["start"]-VO_START-0.03)
        s=max(0.0,s)
        txt="{\\fad(90,90)\\blur7}"+" ".join(w["word"] for w in ln)
        ev.append(f"Dialogue: 0,{at(s)},{at(e)},Cap,,0,0,0,,{txt}")
    header=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+style+"\n\n")
    (BUILD/"m3_caps.ass").write_text(header+"\n".join(ev)+"\n")

def final():
    write_captions()
    ass=(BUILD/"m3_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.0[vo];"
        f"[2:a]atrim=0:{TOTAL},volume=1.1[song];"
        f"[song][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"m3_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-ss",str(SONG_OFFSET),"-i",str(AUD/"song.mp3"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk3.mp4")],"final")
    print("  ->", OUT/"main_chunk3.mp4")

if __name__=="__main__":
    print("[1/4] tree (plain)"); beat_tree()
    print("[2/4] sieve");          beat_sieve()
    print("[3/4] red typography"); beat_red()
    (BUILD/"m3_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["m3_b1","m3_b2","m3_b3"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"m3_concat.txt"),
         "-c","copy",str(BUILD/"m3_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", TOTAL, "s")
