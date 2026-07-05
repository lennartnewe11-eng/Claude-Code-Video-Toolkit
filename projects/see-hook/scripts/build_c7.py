#!/usr/bin/env python3
"""Main part - Chunk 7 (VO 109.0 -> ~123.14s): recap of the two factors, the
question 'where do the holes come from?', and the reveal -- the Ice Age.
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C7 = MA/"c7"; IMG = C7/"img"; FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")

VO_START = 109.0
SONG_OFFSET = 76.90 + VO_START
D_B1, D_B2, D_B3 = 5.06, 3.90, 5.18
TOTAL = D_B1 + D_B2 + D_B3
B1_A, B1_B = 109.0, 114.06            # editorial recap carries its own text

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[cg]")

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p

def at(t):
    m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"0:{m:02d}:{s:02d}.{c:02d}"

def ass_header(styles):
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+"\n".join(styles)+"\n\n")

BLK="&H00181818"; YEL="&H0000E9F4"

def kb(img, dur, dst, z="min(zoom+0.0006,1.18)", extra=""):
    nf=int(dur*30)+2
    fc=(f"[0:v]scale=2400:-1,zoompan=z='{z}':d={nf}:s=1920x1080:fps=30,setsar=1,{NORM},{GRADE}"
        f"{extra}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL+";[cg]copy[v]")
    run([FF,"-y","-loop","1","-i",str(img),"-loop","1","-i",SCAN,"-filter_complex",fc,
         "-map","[v]","-t",str(dur),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","18",str(BUILD/dst)],dst)

# ---- beat 1: recap (two factors) --------------------------------------------
def beat_recap():
    a=(BUILD/"c7_b1.ass")
    styles=[f"Style: S,Liberation Sans,44,{BLK},{BLK},{BLK},&H00000000,0,0,0,0,100,100,5,0,1,0,0,7,0,0,0,1",
            f"Style: B,Liberation Sans,96,{BLK},{BLK},{BLK},&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
            f"Style: N,Liberation Sans,110,{BLK},{BLK},{BLK},&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.2)},{at(D_B1)},S,,0,0,0,,{{\\an7\\pos(120,120)\\fad(200,0)}}es kommt auf zwei Dinge an",
        f"Dialogue: 0,{at(1.2)},{at(D_B1)},N,,0,0,0,,{{\\an7\\pos(220,320)\\fad(220,0)}}01",
        f"Dialogue: 0,{at(1.4)},{at(D_B1)},B,,0,0,0,,{{\\an7\\pos(360,345)\\fad(220,0)}}Bodenbeschaffenheit",
        f"Dialogue: 0,{at(2.8)},{at(D_B1)},N,,0,0,0,,{{\\an7\\pos(220,560)\\fad(220,0)}}02",
        f"Dialogue: 0,{at(3.0)},{at(D_B1)},B,,0,0,0,,{{\\an7\\pos(360,585)\\fad(220,0)}}Grundwasserspiegel"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    fc=(f"color=c=white:s=1920x1080:r=30[bg];[bg]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},"
        "noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-f","lavfi","-i","color=c=white:s=1920x1080:r=30","-filter_complex",fc,
         "-map","[v]","-t",str(D_B1),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","18",str(BUILD/"c7_b1.mp4")],"recap")

# ---- beat 2: the question ---------------------------------------------------
def beat_question():
    a=(BUILD/"c7_b2.ass")
    styles=[f"Style: Q,Liberation Sans,300,{YEL},{YEL},{YEL},&H78101010,-1,0,0,0,100,100,0,0,1,3,3,7,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.3)},{at(D_B2)},Q,,0,0,0,,{{\\an7\\pos(1300,60)\\fad(220,0)\\blur8}}?"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    kb(IMG/"hole.jpg", D_B2, "c7_b2_v.mp4", z="max(1.16-0.0006*on,1.02)")  # slow pull-out
    # overlay the big '?'
    fc=(f"[0:v]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},format=yuv420p[v]")
    run([FF,"-y","-i",str(BUILD/"c7_b2_v.mp4"),"-filter_complex",fc,"-map","[v]",
         "-t",str(D_B2),"-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"c7_b2.mp4")],"question")

# ---- beat 3: the Ice Age reveal ---------------------------------------------
def beat_iceage():
    a=(BUILD/"c7_b3.ass")
    styles=[f"Style: R,Liberation Sans,190,&H00FFFFFF,&H00FFFFFF,&H00202024,&H90000000,-1,0,0,0,100,100,6,0,1,3,3,5,0,0,0,1"]
    # 'DIE EISZEIT' slams in at local 122.44-117.96 = 4.48s
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(4.30)},{at(D_B3)},R,,0,0,0,,{{\\an5\\pos(960,540)\\fad(120,0)"
        f"\\t(0,220,\\fscx100\\fscy100)\\fscx160\\fscy160\\blur4}}DIE EISZEIT"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    kb(IMG/"glacier.jpg", D_B3, "c7_b3_v.mp4", z="min(1.0+0.00075*on,1.16)")
    fc=(f"[0:v]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},format=yuv420p[v]")
    run([FF,"-y","-i",str(BUILD/"c7_b3_v.mp4"),"-filter_complex",fc,"-map","[v]",
         "-t",str(D_B3),"-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"c7_b3.mp4")],"iceage")

# ---- captions (suppress the editorial recap) --------------------------------
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
    (BUILD/"c7_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","3","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c7_song.wav")],"songbed")
    ass=(BUILD/"c7_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c7_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c7_song.wav"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk7.mp4")],"final")
    print("  ->", OUT/"main_chunk7.mp4")

if __name__=="__main__":
    print("[1/4] recap");    beat_recap()
    print("[2/4] question"); beat_question()
    print("[3/4] iceage");   beat_iceage()
    (BUILD/"c7_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c7_b1","c7_b2","c7_b3"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c7_concat.txt"),
         "-c","copy",str(BUILD/"c7_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", round(TOTAL,2),"s")
