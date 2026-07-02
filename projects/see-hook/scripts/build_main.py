#!/usr/bin/env python3
"""Build the 'main' explainer part, piece by piece, in the same style
(warm CRT grade + yellow glow captions, music continues).

Chunk 1 (0-14.6s):
  1  park animation ~3x speed          "Die Antwort ... simpel"
  2  water (fg) + cave (underground)   "...nicht ueber der Erde sondern unter ihr"
  3  man stencil over an aesthetic lake"Denn eine Vertiefung ... ein Loch ..."
  4  calm meadow / field               "...ganz normale Wiese entscheiden zwei Fragen"
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
A, BUILD, OUT, MA, AUD, FONTS = (ROOT/"assets", ROOT/"build", ROOT/"out",
                                 ROOT/"main_assets", ROOT/"audio", ROOT/"fonts")
FF = "ffmpeg"
SCAN = str(BUILD/"scanlines.png")
SONG_OFFSET = 76.90          # song time continues from the end of Teil 2
NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
GRADE_TAIL = ("[1:v]scale=1920:1080,setsar=1[sc];"
              "[gc][sc]blend=all_mode=multiply:all_opacity=0.38:shortest=1[m];"
              "[m]vignette=PI/5.5,noise=alls=5:allf=t,format=yuv420p[v]")

def run(cmd, label=""):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3200:]); raise SystemExit(1)
    return p

def enc(extra_in, fc, dur, dst, pre="veryfast", crf="18"):
    run([FF,"-y",*extra_in,"-loop","1","-i",SCAN,"-filter_complex",fc,
         "-map","[v]","-t",str(dur),"-r","30","-c:v","libx264","-preset",pre,
         "-crf",crf,str(BUILD/dst)], dst)

# ---- beat 1: park animation, ~3x speed --------------------------------------
def beat1(dur=3.5):
    fc=(f"[0:v]setpts=PTS/3.0,{NORM},{GRADE}[gc];"+GRADE_TAIL)
    enc(["-i",str(MA/"park_anim.mp4")], fc, dur, "m_b1.mp4")

# ---- beat 2: water (fg) screen-blended over the cave (underground) ----------
def beat2(dur=3.1):
    # water stream in the BACKGROUND, enhanced cave cutout scaled to COVER the
    # whole frame so its rock hugs the edges and frames the water flowing through
    # the transparent opening (like looking out of a cave).
    fc=(f"[0:v]{NORM}[watbg];"
        "[1:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,setsar=1[cave];"
        "[watbg][cave]overlay=0:0:shortest=1[comp];"
        f"[comp]{GRADE}[gc];"
        "[2:v]scale=1920:1080,setsar=1[sc];"
        "[gc][sc]blend=all_mode=multiply:all_opacity=0.38:shortest=1[m];"
        "[m]vignette=PI/5.5,noise=alls=5:allf=t,format=yuv420p[v]")
    run([FF,"-y","-i",str(MA/"water.mp4"),"-loop","1","-i",str(MA/"cave_hi.png"),
         "-loop","1","-i",SCAN,"-filter_complex",fc,"-map","[v]","-t",str(dur),
         "-r","30","-c:v","libx264","-preset","veryfast","-crf","18",
         str(BUILD/"m_b2.mp4")],"beat2")

# ---- beat 3: backlit lake zooms out to cobalt blue, "See" words circle it ----
def beat3(dur=5.0):
    lake=str(MA/"lake_backlight.mp4")
    E="clip((t-0.4)/1.3,0,1)"
    w=f"floor((1920-1280*({E}))/2)*2"    # 1920 -> 640
    h=f"floor((1080-720*({E}))/2)*2"     # 1080 -> 360
    fc=(f"[0:v]{NORM},{GRADE}[lgc];"
        "[2:v]scale=1920:1080,setsar=1[sc];"
        "[lgc][sc]blend=all_mode=multiply:all_opacity=0.38:shortest=1[lm];"
        "[lm]vignette=PI/6,noise=alls=4:allf=t[lake];"
        "color=c=0x0001BE:s=1920x1080:r=30[aqua];"
        f"[lake]scale=w='{w}':h='{h}':eval=frame,setsar=1[lk];"
        "[aqua][lk]overlay=x='(W-w)/2':y='(H-h)/2':eval=frame:shortest=1,format=gbrp[comp];"
        # spinning white "See" words, faded in after the zoom-out, screen-keyed.
        # NOTE: screen-blend MUST run in RGB (gbrp) -- on yuv420p it mangles the
        # chroma planes and floods the frame magenta.
        "[1:v]scale=1920:1080,setsar=1,fade=t=in:st=1.3:d=0.6,format=gbrp[spin];"
        "[comp][spin]blend=all_mode=screen:shortest=1,format=yuv420p[v]")
    run([FF,"-y","-ss","2","-i",lake,"-stream_loop","-1","-i",str(MA/"spin_see.mp4"),
         "-loop","1","-i",SCAN,"-filter_complex",fc,"-map","[v]","-t",str(dur),
         "-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"m_b3.mp4")],"beat3")

# ---- beat 4: meadow video ---------------------------------------------------
def beat4(dur=3.0):
    fc=(f"[0:v]{NORM},{GRADE}[gc];"+GRADE_TAIL)
    enc(["-ss","3","-i",str(MA/"meadow.mp4")], fc, dur, "m_b4.mp4")

# ---- captions ---------------------------------------------------------------
def at(t):
    h=int(t//3600); t-=h*3600; m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

def write_captions(end):
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            if w["start"]<end:            # keep all real words (scores here run low)
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
        s=ln[0]["start"]-0.05; e=ln[-1]["end"]+0.12
        if i+1<len(lines):                       # don't overlap the next line
            e=min(e, lines[i+1][0]["start"]-0.03)
        txt="{\\fad(90,90)\\blur7}"+" ".join(w["word"] for w in ln)
        ev.append(f"Dialogue: 0,{at(s)},{at(e)},Cap,,0,0,0,,{txt}")
    header=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+style+"\n\n")
    (BUILD/"m_caps.ass").write_text(header+"\n".join(ev)+"\n")

def final(total):
    write_captions(total)
    ass=(BUILD/"m_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={total-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim=0:{total},volume=1.0[vo];"
        f"[2:a]atrim=0:{total},volume=1.1[song];"
        f"[song][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"m_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-ss",str(SONG_OFFSET),"-i",str(AUD/"song.mp3"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(total),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk1.mp4")],"final")
    print("  ->", OUT/"main_chunk1.mp4")

if __name__=="__main__":
    beat1(); beat2(); beat3(); beat4()
    order=["m_b1","m_b2","m_b3","m_b4"]
    (BUILD/"m_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in order)+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"m_concat.txt"),
         "-c","copy",str(BUILD/"m_full.mp4")],"concat")
    TOTAL=3.5+3.1+5.0+3.0
    final(TOTAL)
    print("DONE", TOTAL,"s")
