#!/usr/bin/env python3
"""Main part - Chunk 4 (VO 49.64s -> ~74.56s), same style.

  1  clay pottery clip (top-down, spinning) feathered into WHITE + yellow
     poster-typography                         "Liegt ... eine undurchlaessige Schicht, Ton, Lehm oder massiver Fels"
  2  clay cross-section: water dams, hollow fills  "keine Chance zu entkommen ... Mulde laeuft voll"
  3  photo comparison See vs. staubtrockene Senke  "der erste Grund ... 500 m weiter staubtrocken"
  4  split cross-section Ton | Sand/Kies           "unter dem einen Ton, unter dem anderen Sand-/Kiesschicht"

The song is only ~2:12, so it is looped for continuity from here on.
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF = "ffmpeg"; SCAN = str(BUILD/"scanlines.png")
CLAYSEQ = BUILD/"c4_clay"; SIEVESEQ = BUILD/"c3_sieve"; CARDSEQ = BUILD/"c4_cards"
FEATHER = str(BUILD/"c4_feather2.png")

VO_START = 49.64
SONG_OFFSET = 76.90 + VO_START
D_B1, D_B2, D_B3, D_B4 = 7.42, 6.05, 6.49, 4.96
TOTAL = D_B1 + D_B2 + D_B3 + D_B4
B1_A, B1_B = 49.64, 57.06            # captions suppressed here (typographic beat)
B4_A, B4_B = 69.59, 74.55            # editorial beat carries its own text

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

# ---- beat 1: clay clip feathered into white + yellow typography --------------
def write_b1_ass():
    # clean, thin, well-spaced yellow poster type (ref 510.jpg) -- NO shadow,
    # NO glow. A thin dark outline only, so it stays legible over white/clay.
    styles=[
        "Style: YB,Liberation Sans,124,&H0000E9F4,&H0000E9F4,&H002A2A2E,&H00000000,0,0,0,0,100,100,4,0,1,2,0,5,0,0,0,1",
        "Style: YM,Liberation Sans,80,&H0000E9F4,&H0000E9F4,&H002A2A2E,&H00000000,0,0,0,0,100,100,4,0,1,2,0,5,0,0,0,1",
        "Style: YS,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H002A2A2E,&H00000000,0,0,1,0,100,100,5,0,1,2,0,5,0,0,0,1",
    ]
    END=at(D_B1)
    words=[("undurchlässige Schicht",560,160,2.35,"YS"),
           ("Ton",560,330,4.55,"YB"),
           ("Lehm",1330,470,5.30,"YM"),
           ("oder massiver",600,720,5.85,"YS"),
           ("Fels",1300,760,6.30,"YM")]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for txt,x,y,st,sty in words:
        ev.append(f"Dialogue: 0,{at(st)},{END},{sty},,0,0,0,,{{\\an5\\pos({x},{y})\\fad(240,160)}}{txt}")
    (BUILD/"m4_b1.ass").write_text(ass_header(styles)+"\n".join(ev)+"\n")

def beat_clay_title():
    write_b1_ass()
    a=(BUILD/"m4_b1.ass").as_posix()
    # natural clay clip dissolved into white with a big soft feather (like the
    # Teil-2 flower clip): the dark background lifts to white and the edges melt
    # away, so there is no visible frame/transition.
    fc=("color=c=white:s=1920x1080:r=30[white];"
        "[0:v]setpts=1.35*PTS,eq=brightness=0.07:contrast=1.06,"
        "scale=760:1160,setsar=1,format=gbrp[clip];"
        "[1:v]format=gray,scale=760:1160[mask];"
        "[clip][mask]alphamerge[clipa];"
        "[white][clipa]overlay=x=(W-w)/2:y=(H-h)/2:shortest=1[base];"
        f"[base]ass={a}:fontsdir={FONTS.as_posix()},format=yuv420p[v]")
    run([FF,"-y","-ss","4.0","-i",str(MA/"c4_clay.mp4"),"-loop","1","-i",FEATHER,
         "-filter_complex",fc,"-map","[v]","-t",str(D_B1),
         "-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"m4_b1.mp4")],"clay_title")

# ---- beat 2: clay cross-section ---------------------------------------------
def beat_clay_section():
    fc=(f"[0:v]{NORM},{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL)
    run([FF,"-y","-framerate","30","-i",str(CLAYSEQ/"c_%04d.png"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_B2),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","18",str(BUILD/"m4_b2.mp4")],"clay_section")

# ---- beat 3: See vs. staubtrockene Senke (photos) ---------------------------
def write_label_ass(fname, left, right):
    styles=["Style: Lbl,Liberation Sans,66,&H0000E9F4,&H0000E9F4,&H00202024,&H00202024,-1,0,0,0,100,100,2,0,1,4,2,5,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.3)},{at(9)},Lbl,,0,0,0,,{{\\pos(480,940)\\fad(240,0)\\blur3}}{left}",
        f"Dialogue: 0,{at(0.3)},{at(9)},Lbl,,0,0,0,,{{\\pos(1440,940)\\fad(240,0)\\blur3}}{right}"]
    (BUILD/fname).write_text(ass_header(styles)+"\n".join(ev)+"\n")

def beat_compare():
    # two photo cards stacked on white, each pulled to the front when spoken;
    # the narration captions carry the words, so no extra labels here.
    fc=("[0:v]setsar=1,noise=alls=2:allf=t,format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(CARDSEQ/"k_%04d.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B3),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"m4_b3.mp4")],"compare")

# ---- beat 4: editorial typography (last animated beat) ----------------------
def write_b4_ass():
    # editorial black-on-white (ref 510.jpg), exactly like the previous version:
    # "durchlässig" cascaded left-aligned; the spoken sentence on the right.
    # This types goes OVER the two stacked animation videos.
    styles=[
        "Style: Casc,Liberation Sans,80,&H00181818,&H00181818,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
        "Style: RB,Liberation Sans,104,&H00181818,&H00181818,&H00FFFFFF,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1",
        "Style: RM,Liberation Sans,72,&H00181818,&H00181818,&H00FFFFFF,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1",
    ]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    END=at(D_B4)
    for k in range(9):
        y=250+k*76; st=2.9+k*0.11
        ev.append(f"Dialogue: 0,{at(st)},{END},Casc,,0,0,0,,"
                  f"{{\\an7\\pos(70,{y})\\fad(150,0)}}durchlässig")
    right=[("Unter dem einen",1330,180,0.10,"RM"),("liegt Ton",1520,320,0.92,"RB"),
           ("unter dem anderen",1280,500,1.70,"RM"),
           ("eine durchlässige",1330,650,3.37,"RM"),
           ("Sand-",1300,800,4.09,"RB"),("oder Kies",1560,800,4.55,"RB")]
    for txt,x,y,st,sty in right:
        ev.append(f"Dialogue: 0,{at(st)},{END},{sty},,0,0,0,,{{\\an5\\pos({x},{y})\\fad(220,120)}}{txt}")
    (BUILD/"m4_b4.ass").write_text(ass_header(styles)+"\n".join(ev)+"\n")

def beat_split():
    # two animation videos (clay + sieve cross-sections) stacked vertically,
    # near full width, with the editorial typography laid OVER them.
    write_b4_ass()
    a=(BUILD/"m4_b4.ass").as_posix()
    CROP="crop=1920:840:0:150,scale=1180:516,setsar=1"     # same as the frame before
    fc=(f"color=c=white:s=1920x1080:r=30[bg];"
        f"[0:v]{CROP},drawbox=w=iw:h=ih:color=black:t=5[clay];"
        f"[1:v]{CROP},drawbox=w=iw:h=ih:color=black:t=5[sieve];"
        "[bg][clay]overlay=x=55:y=30:shortest=1[a];"
        "[a][sieve]overlay=x=55:y=560:shortest=1[b];"
        f"[b]ass={a}:fontsdir={FONTS.as_posix()},format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(CLAYSEQ/"c_%04d.png"),
         "-framerate","30","-i",str(SIEVESEQ/"s_%04d.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B4),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","18",str(BUILD/"m4_b4.mp4")],"editorial")

# ---- captions (suppress the typographic beat 1) -----------------------------
def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is None: continue
            if VO_START-0.2<=st<VO_START+TOTAL and not (B1_A-0.15<=st<B1_B) \
                    and not (B4_A-0.15<=st<B4_B):
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
    (BUILD/"m4_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    # pre-render a bounded, looped song bed (the song is only ~2:12, so it wraps)
    run([FF,"-y","-stream_loop","3","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"m4_song.wav")],"songbed")
    ass=(BUILD/"m4_caps.ass").as_posix()
    # duck the music under the voice so every line (incl. "Das ist schon der
    # erste Grund") stays clearly audible over the looped song.
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[songd];"
        f"[songd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"m4_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"m4_song.wav"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk4.mp4")],"final")
    print("  ->", OUT/"main_chunk4.mp4")

if __name__=="__main__":
    print("[1/5] clay title");   beat_clay_title()
    print("[2/5] clay section"); beat_clay_section()
    print("[3/5] compare");      beat_compare()
    print("[4/5] split");        beat_split()
    (BUILD/"m4_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["m4_b1","m4_b2","m4_b3","m4_b4"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"m4_concat.txt"),
         "-c","copy",str(BUILD/"m4_full.mp4")],"concat")
    print("[5/5] final"); final()
    print("DONE", round(TOTAL,2),"s")
