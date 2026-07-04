#!/usr/bin/env python3
"""Main part - Chunk 5 (VO 74.55s -> ~89.0s): the groundwater factor.

  1  editorial water frame (ref blue.jpg): water gif fills the lower third of a
     blue board, B&W photo strip + circles + type   "Damit kommen wir zum zweiten Faktor, dem Grundwasser"
  2  archive.org mine-shaft descent                  "Tief unter uns ... vollgesogen wie ein Schwamm"
  3  the ornate mirror as a centred subject (ref: the hand plate), its glass
     filled with drifting clouds                      "... nennt man Grundwasserspiegel"
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C5 = MA/"c5"; IMG = C5/"img"
FF = "ffmpeg"; SCAN = str(BUILD/"scanlines.png")

VO_START = 74.55
SONG_OFFSET = 76.90 + VO_START
D_B1, D_B2, D_B3 = 5.05, 4.39, 5.01
TOTAL = D_B1 + D_B2 + D_B3
B1_A, B1_B = 74.55, 79.60            # editorial water frame carries its own text
B3_A, B3_B = 83.99, 89.00            # mirror frame carries its own label

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[v]")

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

# ---- beat 1: editorial water frame ------------------------------------------
def write_b1_ass():
    # black editorial type (white background now)
    styles=[
        "Style: T1,Liberation Sans,54,&H00181818,&H00181818,&H00181818,&H00000000,0,0,0,0,100,100,3,0,1,0,0,7,0,0,0,1",
        "Style: T2,Liberation Sans,118,&H00181818,&H00181818,&H00181818,&H00000000,0,0,0,0,100,100,2,0,1,0,0,7,0,0,0,1",
        "Style: T0,Liberation Sans,40,&H00181818,&H00181818,&H00181818,&H00000000,0,0,0,0,100,100,6,0,1,0,0,7,0,0,0,1",
    ]
    END=at(D_B1)
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.2)},{END},T0,,0,0,0,,{{\\an7\\pos(1150,120)\\fad(200,0)}}Faktor  zwei",
        f"Dialogue: 0,{at(1.5)},{END},T1,,0,0,0,,{{\\an7\\pos(700,300)\\fad(220,0)}}der zweite Faktor",
        f"Dialogue: 0,{at(3.0)},{END},T2,,0,0,0,,{{\\an7\\pos(700,400)\\fad(240,0)}}das Grundwasser"]
    (BUILD/"c5_b1.ass").write_text(ass_header(styles)+"\n".join(ev)+"\n")

def beat_water():
    write_b1_ass()
    a=(BUILD/"c5_b1.ass").as_posix()
    # WHITE bg, water gif in the lower third, then ALL objects (photos, circles)
    # + type in the foreground on top.
    fc=("color=c=white:s=1920x1080:r=30[bg];"
        "[1:v]scale=1920:400,setsar=1[wat];"
        "[bg][wat]overlay=x=0:y=690:shortest=1[base];"
        "[2:v]setsar=1[fg];[base][fg]overlay=x=0:y=0:shortest=1[comp];"
        f"[comp]ass={a}:fontsdir={FONTS.as_posix()},noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-f","lavfi","-i","color=c=white:s=1920x1080:r=30",
         "-stream_loop","-1","-i",str(C5/"water.gif"),
         "-loop","1","-i",str(BUILD/"c5_b1_fg.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B1),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"c5_b1.mp4")],"water")

# ---- beat 2: mine-shaft descent ---------------------------------------------
def beat_mine():
    # old B&W pit-head winding tower -> cage (archive.org 1950s coal film);
    # warm CRT grade gives it an archival sepia tone. Slight push-in.
    fc=(f"[0:v]crop=iw:ih-54:0:6,{NORM},scale=2112:1188,"
        f"crop=1920:1080:x='(iw-1920)/2':y='(ih-1080)*t/{D_B2}',"
        f"{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL)
    run([FF,"-y","-ss","0.3","-i",str(C5/"mine_bw.mp4"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_B2),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"c5_b2.mp4")],"mine")

# ---- beat 3: mirror ('Grundwasserspiegel') ----------------------------------
def write_b3_ass():
    styles=["Style: Cap5,Liberation Sans,44,&H00202024,&H00202024,&H00FFFFFF,&H00000000,0,1,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
            "Style: Num,Liberation Sans,40,&H00202024,&H00202024,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(1.4)},{at(D_B3)},Cap5,,0,0,0,,{{\\an7\\pos(150,930)\\fad(240,0)}}die Oberkante des Schwamms — der Grundwasserspiegel",
        f"Dialogue: 0,{at(1.4)},{at(D_B3)},Num,,0,0,0,,{{\\an7\\pos(1780,980)\\fad(240,0)}}14"]
    (BUILD/"c5_b3.ass").write_text(ass_header(styles)+"\n".join(ev)+"\n")

def beat_mirror():
    write_b3_ass()
    a=(BUILD/"c5_b3.ass").as_posix()
    # mirror scaled to h=980 (426x640 -> 652x980), centred at x=960, y=50.
    # clouds (Ken-Burns drift) masked to the glass oval, laid over the mirror.
    nf=int(D_B3*30)+2
    fc=("color=c=0xF2F0EA:s=1920x1080:r=30[white];"
        "[1:v]scale=652:980,setsar=1[mir];"
        "[white][mir]overlay=x=634:y=50:shortest=1[base];"
        f"[0:v]scale=900:1150,zoompan=z='min(zoom+0.0006,1.2)':d={nf}:s=652x980:fps=30,setsar=1[cl];"
        "[2:v]scale=652:980,format=gray[mask];"
        "[cl][mask]alphamerge[clg];"
        "[base][clg]overlay=x=634:y=50:shortest=1[comp];"
        f"[comp]ass={a}:fontsdir={FONTS.as_posix()},noise=alls=2:allf=t,format=yuv420p[v]")
    run([FF,"-y","-loop","1","-i",str(IMG/"clouds.jpg"),"-loop","1","-i",str(C5/"mirror.png"),
         "-loop","1","-i",str(BUILD/"c5_mirror_mask.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B3),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"c5_b3.mp4")],"mirror")

# ---- captions (suppress the two typographic frames) -------------------------
def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is None: continue
            if VO_START-0.2<=st<VO_START+TOTAL and not (B1_A-0.15<=st<B1_B) \
                    and not (B3_A-0.15<=st<B3_B):
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
    (BUILD/"c5_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","3","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c5_song.wav")],"songbed")
    ass=(BUILD/"c5_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c5_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c5_song.wav"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk5.mp4")],"final")
    print("  ->", OUT/"main_chunk5.mp4")

if __name__=="__main__":
    print("[1/4] water");  beat_water()
    print("[2/4] mine");   beat_mine()
    print("[3/4] mirror"); beat_mirror()
    (BUILD/"c5_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c5_b1","c5_b2","c5_b3"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c5_concat.txt"),
         "-c","copy",str(BUILD/"c5_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", round(TOTAL,2),"s")
