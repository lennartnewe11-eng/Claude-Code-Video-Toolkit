#!/usr/bin/env python3
"""Main part - Chunk 6 (VO 89.0 -> ~109.0s): the depression reaches the water
table, a 'window' to the groundwater, the neighbour hollow stays dry.
Editorial / cinematic style with the user's assets + sourced stills.
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C6 = MA/"c6"; FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")

VO_START = 89.00
SONG_OFFSET = 76.90 + VO_START
D_B1, D_B2, D_B3 = 5.87, 6.71, 7.42
TOTAL = D_B1 + D_B2 + D_B3

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")

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

BLK = "&H00181818"
def styles_blk():
    return [f"Style: E1,Liberation Sans,52,{BLK},{BLK},{BLK},&H00000000,0,0,0,0,100,100,3,0,1,0,0,7,0,0,0,1",
            f"Style: E2,Liberation Sans,96,{BLK},{BLK},{BLK},&H00000000,0,0,0,0,100,100,2,0,1,0,0,7,0,0,0,1",
            f"Style: E0,Liberation Sans,38,{BLK},{BLK},{BLK},&H00000000,0,0,0,0,100,100,6,0,1,0,0,7,0,0,0,1"]

# ---- beat 1: editorial diagonal cascade (reaches the water table) ------------
def beat_reach():
    a=(BUILD/"c6_b1.ass")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.1)},{at(D_B1)},E0,,0,0,0,,{{\\an7\\pos(1300,140)\\fad(200,0)}}tief genug",
        f"Dialogue: 0,{at(1.3)},{at(D_B1)},E1,,0,0,0,,{{\\an7\\pos(1250,300)\\fad(220,0)}}Schneidet sie tief genug",
        f"Dialogue: 0,{at(3.6)},{at(D_B1)},E2,,0,0,0,,{{\\an7\\pos(1150,430)\\fad(240,0)}}bis zum Spiegel"]
    a.write_text(ass_header(styles_blk())+"\n".join(ev)+"\n")
    fc=("color=c=white:s=1920x1080:r=30[bg];"
        "[1:v]setsar=1,fade=t=in:st=0.2:d=0.4[p1];[bg][p1]overlay=x=60:y=40:shortest=1[a1];"
        "[2:v]setsar=1,fade=t=in:st=0.9:d=0.4[p2];[a1][p2]overlay=x=470:y=360:shortest=1[a2];"
        "[3:v]setsar=1,fade=t=in:st=1.6:d=0.4[p3];[a2][p3]overlay=x=250:y=640:shortest=1[base];"
        f"[base]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-f","lavfi","-i","color=c=white:s=1920x1080:r=30",
         "-loop","1","-i",str(BUILD/"c6_p1.png"),"-loop","1","-i",str(BUILD/"c6_p2.png"),
         "-loop","1","-i",str(BUILD/"c6_p3.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B1),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"c6_b1.mp4")],"reach")

# ---- beat 2: a window to the groundwater ------------------------------------
def beat_window():
    a=(BUILD/"c6_b2.ass")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.1)},{at(D_B2)},E0,,0,0,0,,{{\\an7\\pos(120,150)\\fad(200,0)}}nicht durch Regen",
        f"Dialogue: 0,{at(1.4)},{at(D_B2)},E1,,0,0,0,,{{\\an7\\pos(120,240)\\fad(220,0)}}sie fühlt sich von unten",
        f"Dialogue: 0,{at(3.6)},{at(D_B2)},E2,,0,0,0,,{{\\an7\\pos(120,860)\\fad(240,0)}}ein Fenster",
        f"Dialogue: 0,{at(4.4)},{at(D_B2)},E1,,0,0,0,,{{\\an7\\pos(140,970)\\fad(240,0)}}zum Grundwasser"]
    a.write_text(ass_header(styles_blk())+"\n".join(ev)+"\n")
    # sediment video behind a centred window (940x640 glass at x=970,y=210)
    fc=("color=c=white:s=1920x1080:r=30[bg];"
        f"[0:v]{NORM},{GRADE},scale=980:680,setsar=1[sed];"
        "[bg][sed]overlay=x=850:y=200:shortest=1[b1];"
        "[1:v]setsar=1[win];[b1][win]overlay=x=850:y=200:shortest=1[base];"
        f"[base]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-stream_loop","-1","-i",str(C6/"sediment.mp4"),
         "-loop","1","-i",str(BUILD/"c6_window.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B2),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"c6_b2.mp4")],"window")

# ---- beat 3: the neighbour hollow stays dry ---------------------------------
def beat_dry():
    a=(BUILD/"c6_b3.ass")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.1)},{at(D_B3)},E0,,0,0,0,,{{\\an7\\pos(1180,150)\\fad(200,0)}}die Nachbarsenke",
        f"Dialogue: 0,{at(1.8)},{at(D_B3)},E1,,0,0,0,,{{\\an7\\pos(1180,250)\\fad(220,0)}}ein paar Meter höher",
        f"Dialogue: 0,{at(4.2)},{at(D_B3)},E0,,0,0,0,,{{\\an7\\pos(1180,430)\\fad(220,0)}}das Fenster bleibt zu",
        f"Dialogue: 0,{at(5.4)},{at(D_B3)},E2,,0,0,0,,{{\\an7\\pos(1180,520)\\fad(240,0)}}staubtrocken"]
    a.write_text(ass_header(styles_blk())+"\n".join(ev)+"\n")
    # countryside gif as a framed cinematic photo, left; editorial type right
    fc=("color=c=white:s=1920x1080:r=30[bg];"
        f"[0:v]scale=1000:667,setsar=1,{GRADE},pad=1040:707:20:20:white[ph];"
        "[bg][ph]overlay=x=70:y=190:shortest=1[base];"
        f"[base]ass={a.as_posix()}:fontsdir={FONTS.as_posix()},noise=alls=3:allf=t,format=yuv420p[v]")
    run([FF,"-y","-stream_loop","-1","-i",str(C6/"country.gif"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_B3),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","18",str(BUILD/"c6_b3.mp4")],"dry")

# ---- captions suppressed (editorial type carries the words) -----------------
def write_captions():
    (BUILD/"c6_caps.ass").write_text(ass_header(
        ["Style: Cap,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H0000E9F4,&H78101010,-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1"])
        +"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","3","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c6_song.wav")],"songbed")
    ass=(BUILD/"c6_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c6_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c6_song.wav"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk6.mp4")],"final")
    print("  ->", OUT/"main_chunk6.mp4")

if __name__=="__main__":
    print("[1/4] reach");  beat_reach()
    print("[2/4] window"); beat_window()
    print("[3/4] dry");    beat_dry()
    (BUILD/"c6_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c6_b1","c6_b2","c6_b3"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c6_concat.txt"),
         "-c","copy",str(BUILD/"c6_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", round(TOTAL,2),"s")
