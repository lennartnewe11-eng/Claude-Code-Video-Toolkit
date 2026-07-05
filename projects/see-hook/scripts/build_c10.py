#!/usr/bin/env python3
"""Main part - Chunk 10 (VO 192.85 -> ~214.24s): Toteis / round holes.
  beat A  ice block full-screen hero (a block calved off + about to be buried)
  beat B  cross-section: block buried under Geroell -> melts -> ground sinks ->
          round hole fills with water (the same cut-out ice block, textured)
  beat C  clean B&W Mecklenburg/Brandenburg map: camera zooms across several
          lakes and highlights them, ending wide on the whole Seenplatte
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C10=MA/"c10"; FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")
MAPF=BUILD/"c10_map_f"; FORMF=BUILD/"c10_form"

VO_START=192.85
SONG_OFFSET=269.75                      # continues the looped song from chunk 9
D_A, D_B, D_C = 4.09, 9.40, 7.90
TOTAL=D_A+D_B+D_C                        # 21.39
B_A, B_B = VO_START, VO_START           # no caption suppression

GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[cg]")
# lighter treatment for the map (keep lakes crisp/legible)
MAP_GRADE=("colortemperature=temperature=5400:mix=0.25:pl=1,eq=contrast=1.03,"
           "vignette=PI/9,noise=alls=3:allf=t,format=yuv420p")

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

# ---- beat A: ice hero (slow push-in) ----------------------------------------
def beat_hero():
    nf=int(D_A*30)+2; z="min(zoom+0.0006,1.12)"
    fc=(f"[0:v]scale=2304:-1,zoompan=z='{z}':d={nf}:s=1920x1080:fps=30,setsar=1,{GRADE}[pre];"
        f"[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL+";[cg]copy[v]")
    run([FF,"-y","-loop","1","-i",str(BUILD/"c10_hero.png"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_A),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","19",str(BUILD/"c10_a.mp4")],"hero")

# ---- beat B: formation cross-section ----------------------------------------
def beat_form():
    fc=(f"[0:v]setsar=1,{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL
        +";[cg]copy[v]")
    run([FF,"-y","-framerate","30","-i",str(FORMF/"f_%04d.png"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_B),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","19",str(BUILD/"c10_b.mp4")],"form")

# ---- beat C: map camera + highlights ----------------------------------------
def beat_map():
    a=BUILD/"c10_mapcap.ass"
    styles=[f"Style: T,Liberation Sans,44,&H00FFFFFF,&H00FFFFFF,&H00202020,&H90101010,-1,0,0,0,100,100,1,0,1,2,1,7,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.3)},{at(D_C)},T,,0,0,0,,{{\\an7\\pos(70,60)\\fad(200,0)}}Mecklenburg & Brandenburg",
        f"Dialogue: 0,{at(0.3)},{at(D_C)},T,,0,0,0,,{{\\an7\\pos(70,116)\\fscx86\\fscy86\\fad(200,0)}}Toteisloecher · fast kreisrunde Seen"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    fc=(f"[0:v]setsar=1,{MAP_GRADE},ass={a.as_posix()}:fontsdir={FONTS.as_posix()}[v]")
    run([FF,"-y","-framerate","30","-i",str(MAPF/"m_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_C),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c10_c.mp4")],"map")

# ---- captions ----------------------------------------------------------------
def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is None: continue
            if VO_START-0.2<=st<VO_START+TOTAL:
                words.append(w)
    lines,cur=[],[]
    for w in words:
        cur.append(w)
        if len(cur)>=6 or w["word"].endswith((".","?","!",",",";",":")):
            lines.append(cur); cur=[]
    if cur: lines.append(cur)
    style=("Style: Cap,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H00101010,&H90101010,"
           "-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i,ln in enumerate(lines):
        s=max(0.0,ln[0]["start"]-VO_START-0.05); e=ln[-1]["end"]-VO_START+0.12
        if i+1<len(lines): e=min(e, lines[i+1][0]["start"]-VO_START-0.03)
        FIX={"sagte":"sank"}      # ASR mis-hear ("sank der Boden ... ein")
        txt="{\\fad(90,90)\\blur7}"+" ".join(FIX.get(w["word"],w["word"]) for w in ln)
        ev.append(f"Dialogue: 0,{at(s)},{at(e)},Cap,,0,0,0,,{txt}")
    (BUILD/"c10_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c10_song.wav")],"songbed")
    ass=(BUILD/"c10_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c10_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c10_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk10.mp4")],"final")
    print("  ->", OUT/"main_chunk10.mp4")

if __name__=="__main__":
    print("[1/5] hero"); beat_hero()
    print("[2/5] form"); beat_form()
    print("[3/5] map");  beat_map()
    (BUILD/"c10_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c10_a","c10_b","c10_c"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c10_concat.txt"),
         "-c","copy",str(BUILD/"c10_full.mp4")],"concat")
    print("[5/5] final"); final()
    print("DONE", round(TOTAL,2),"s")
