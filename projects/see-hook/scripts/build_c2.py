#!/usr/bin/env python3
"""Main part - Chunk 2 (VO 14.60s -> 35.45s), same style as chunk 1.

  1  collage of scattered water 'polaroids' over a landscape   "...zwei Fragen: genug Wasser? / kann das Loch es halten?"
  2  flat-cartoon buckets in the rain (sealed fills, holed leaks) "Stell dir zwei Eimer vor..."
  3  the rain clip presented slightly zoomed-out on white        "...in den Regen stellen, voll wird trotzdem nur einer."
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C2  = MA/"c2"
IMG = C2/"img"
POL = BUILD/"c2_polaroids"
BKT = BUILD/"c2_buckets"
FF  = "ffmpeg"
SCAN = str(BUILD/"scanlines.png")

VO_START   = 14.60
SONG_OFFSET = 76.90 + VO_START          # song continues from chunk 1
D_COL, D_BKT, D_RAIN = 9.40, 6.30, 5.15
TOTAL = D_COL + D_BKT + D_RAIN          # 20.85

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

# ---- beat 1: scattered-polaroid collage -------------------------------------
# small, upright photos scattered RANDOMLY (irregular heights, no ring/oval)
# (top-left x, y, pop-in time)  paired with pol_00..06
LAYOUT = [(110, 105, 0.3), (470, 250, 2.4), (880, 95, 1.0),
          (1270, 180, 3.1), (1560, 470, 1.7), (250, 585, 3.7), (860, 600, 4.5)]

def beat_collage(dur=D_COL):
    ins = ["-loop","1","-i",str(IMG/"bg.jpg")]
    for i in range(7):
        ins += ["-loop","1","-i",str(POL/f"pol_{i:02d}.png")]
    ins += ["-loop","1","-i",SCAN]
    # bg graded, gentle slow push-in
    fc = (f"[0:v]{NORM},scale=2112:1188,"
          "crop=1920:1080:x='(iw-1920)/2+(t-4.7)*3':y='(ih-1080)/2',"
          f"{GRADE}[bg];")
    prev = "bg"
    for i,(x,y,t) in enumerate(LAYOUT):
        inp = i+1
        fc += (f"[{inp}:v]format=rgba,fade=t=in:st={t:.2f}:d=0.35:alpha=1[p{i}];"
               f"[{prev}][p{i}]overlay=x={x}:y={y}:shortest=1[o{i}];")
        prev = f"o{i}"
    fc += f"[{prev}]format=yuv420p[pre];[8:v]scale=1920:1080,setsar=1[sc];" + CRT_TAIL
    run([FF,"-y",*ins,"-filter_complex",fc,"-map","[v]","-t",str(dur),
         "-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"m2_b1.mp4")],"collage")

# ---- beat 2: bucket cartoon -------------------------------------------------
def beat_buckets(dur=D_BKT):
    fc = (f"[0:v]{NORM},{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL)
    run([FF,"-y","-framerate","30","-i",str(BKT/"b_%04d.png"),
         "-loop","1","-i",SCAN,"-filter_complex",fc,"-map","[v]","-t",str(dur),
         "-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"m2_b2.mp4")],"buckets")

# ---- beat 3: rain clip on white (no frame) + creative "REGEN" word ----------
def write_regen_ass():
    # kinetic word: two "REGEN" lines stacked at the RIGHT edge of the framed
    # clip (edge x=1660) so each word straddles it -- its left letters fall over
    # the dark video, its right letters over the white margin. Letters drop in
    # from above like rain. BLACK fill + soft white glow so it reads on both.
    style=("Style: Big,Liberation Sans,82,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,"
           "-1,0,0,0,100,100,1,0,1,3,0,5,0,0,0,1")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    letters="REGEN"; cx=1660; sp=64           # tighter; straddles the clip's right edge (1660)
    for li,ytar in enumerate((385, 530)):     # two lines under each other
        for k,ch in enumerate(letters):
            x=cx+(k-2)*sp
            st=1.20+li*0.30+k*0.10; en=4.70
            mv=f"\\move({x},-80,{x},{ytar},0,360)"
            ev.append(f"Dialogue: 1,{at(st)},{at(en)},Big,,0,0,0,,"
                      f"{{{mv}\\fad(160,360)\\blur5}}{ch}")
    header=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+style+"\n\n")
    (BUILD/"m2_regen.ass").write_text(header+"\n".join(ev)+"\n")

def beat_rain(dur=D_RAIN):
    # rain clip presented slightly zoomed-out on a genuinely WHITE background,
    # NO polaroid frame/shadow (size kept), plus the kinetic "REGEN" word.
    write_regen_ass()
    regen=(BUILD/"m2_regen.ass").as_posix()
    fc = ("color=c=white:s=1920x1080:r=30[white];"
          f"[1:v]scale=1920:1080,setsar=1[sc];"
          f"[0:v]{NORM},{GRADE}[gc];"
          "[gc][sc]blend=all_mode=multiply:all_opacity=0.30:shortest=1[cm];"
          "[cm]vignette=PI/7,noise=alls=4:allf=t,scale=1400:788,setsar=1[clip];"
          "[white][clip]overlay=x=(W-w)/2:y=(H-h)/2:shortest=1[base];"
          f"[base]ass={regen}:fontsdir={FONTS.as_posix()},format=yuv420p[v]")
    run([FF,"-y","-ss","1","-i",str(C2/"rain.mp4"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(dur),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"m2_b3.mp4")],"rain")

# ---- captions ---------------------------------------------------------------
def at(t):
    h=int(t//3600); t-=h*3600; m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is not None and VO_START-0.2 <= st < VO_START+TOTAL:
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
    (BUILD/"m2_caps.ass").write_text(header+"\n".join(ev)+"\n")

def final():
    write_captions()
    ass=(BUILD/"m2_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.0[vo];"
        f"[2:a]atrim=0:{TOTAL},volume=1.1[song];"
        f"[song][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"m2_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-ss",str(SONG_OFFSET),"-i",str(AUD/"song.mp3"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk2.mp4")],"final")
    print("  ->", OUT/"main_chunk2.mp4")

if __name__=="__main__":
    print("[1/4] collage"); beat_collage()
    print("[2/4] buckets"); beat_buckets()
    print("[3/4] rain");    beat_rain()
    (BUILD/"m2_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["m2_b1","m2_b2","m2_b3"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"m2_concat.txt"),
         "-c","copy",str(BUILD/"m2_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", TOTAL, "s")
