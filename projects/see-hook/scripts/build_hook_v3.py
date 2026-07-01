#!/usr/bin/env python3
"""Build the 'See' hook v3.

Changes vs v2:
  - "kein See" now uses an empty dry reservoir basin (Vertiefung ohne Wasser)
  - hook extended through "Wie entsteht eigentlich ein See?"
  - captions: smaller, no black outline, soft yellow GLOW (libass \blur)
  - outro: the lake video ANIMATES from fullscreen down into the small
    framed version on white (time-based scale), and the pun text is BLACK
    and animated creatively across the whole screen (breaks caption format)
"""
import json, subprocess, pathlib, sys, os

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS, BUILD, OUT = ROOT/"assets", ROOT/"build", ROOT/"out"
UF, AUD, FONTS = ROOT/"user_footage", ROOT/"audio", ROOT/"fonts"
BUILD.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
FF = "ffmpeg"

OFFSET = 6.0
VO_TAG_START, VO_TAG_END = 19.69, 22.60   # tagline -> handled by animated pun
END = 30.25

manifest = {m["shot"]: m for m in json.loads((BUILD/"footage_manifest.json").read_text()) if m.get("ok")}
def pex(shot): return str(ASSETS/manifest[shot]["file"])
C2 = str(ASSETS/"C2_notlake_37533724.mp4")   # empty dry reservoir basin

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.65:pl=1,"
         "eq=contrast=1.045:saturation=1.10:gamma=0.99:brightness=0.006,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',"
         "split[g1][g2];[g2]gblur=sigma=8[gb];"
         "[g1][gb]blend=all_mode=screen:all_opacity=0.22[bloom];"
         "[bloom]rgbashift=rh=2:bh=-2[ca];"
         "[ca]lenscorrection=k1=0.05:k2=0.012:i=bilinear[lens];"
         "[1:v]scale=1920:1080,setsar=1[scan];"
         "[lens][scan]blend=all_mode=multiply:all_opacity=0.50:shortest=1[sl];"
         "[sl]vignette=PI/5,noise=alls=5:allf=t+u,format=yuv420p")

def run(cmd, label=""):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p

def clip(src, t_in, dur, dst):
    run([FF,"-y","-ss",str(t_in),"-i",src,"-t",str(round(dur,3)),"-vf",NORM,"-an",
         "-c:v","libx264","-preset","veryfast","-crf","18",str(BUILD/dst)], dst)

def grade(src, dst):
    run([FF,"-y","-i",str(BUILD/src),"-loop","1","-i",str(BUILD/"scanlines.png"),
         "-filter_complex","[0:v]"+GRADE+"[v]","-map","[v]",
         "-c:v","libx264","-preset","veryfast","-crf","16",str(BUILD/dst)], "grade "+dst)

# ---------------------------------------------------------- 1. clips
def build_clips():
    clip(str(UF/"birds.mp4"), 0.0, 8.88, "_birds.mp4")
    clip(pex("A_lake1"),      1.0, 3.19, "_lake1.mp4")
    run([FF,"-y","-i",str(BUILD/"_birds.mp4"),"-i",str(BUILD/"_lake1.mp4"),
         "-filter_complex",
         "[0][1]xfade=transition=dissolve:duration=0.5:offset=8.38,format=yuv420p[v]",
         "-map","[v]","-c:v","libx264","-preset","veryfast","-crf","18",
         str(BUILD/"seg_intro.mp4")],"xfade-intro")            # 0-11.57
    clip(C2,               38.5, 2.72, "seg_C.mp4")            # 11.57-14.29 dry basin
    clip(pex("D_terrain"),  0.5, 3.71, "seg_D.mp4")           # 14.29-18.0
    clip(str(UF/"mrbean.mp4"), 0.4, 2.20, "seg_bean1.mp4")    # 18.0-20.2
    clip(pex("F_weather"),  2.0, 4.01, "seg_F.mp4")           # 20.2-24.21
    clip(str(UF/"mrbean.mp4"), 4.2, 1.48, "seg_bean2.mp4")    # 24.21-25.69
    clip(str(UF/"lake_bikes.mp4"), 0.4, 1.68, "seg_question.mp4")  # 28.62-30.30 (lake, not the cat)
    parts=["seg_intro","seg_C","seg_D","seg_bean1","seg_F","seg_bean2"]
    (BUILD/"concat_main.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{p}.mp4').as_posix()}'" for p in parts)+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"concat_main.txt"),
         "-c","copy",str(BUILD/"main.mp4")],"concat-main")

# ---------------------------------------------------------- 2. animated outro
def write_outro_pun():
    style=("Style: Pun,Liberation Sans,150,&H00000000,&H00000000,&H00FFFFFF,&H00000000,"
           "-1,0,0,0,100,100,0,0,1,2.4,0,5,0,0,0,1")
    # word: (text, fs, rot, x1,y1, x2,y2, delay_ms)
    W=[("Seen",158,3,   300,300,  600,300,   0),
       ("oder",112,-5, 1330,250, 1330,470, 260),
       ("geseen",172,2, 920,660,  620,660, 520),
       ("werden",150,-3,1300,1060,1300,835,820)]
    ev=[]
    for t,fs,rot,x1,y1,x2,y2,d in W:
        ov=(f"{{\\an5\\fs{fs}\\frz{rot}\\blur6\\bord2.4\\3c&HFFFFFF&\\1c&H000000&"
            f"\\fscx60\\fscy60\\alpha&HFF&"
            f"\\move({x1},{y1},{x2},{y2},{d},{d+460})"
            f"\\t({d},{d+240},\\alpha&H00&)\\t({d},{d+440},\\fscx104\\fscy104)}}")
        ev.append(f"Dialogue: 0,0:00:00.45,0:00:02.95,Pun,,0,0,0,,{ov}{t}")
    ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
    (BUILD/"outro_pun.ass").write_text(ass)

def build_outro():
    write_outro_pun()
    lake = pex("H_tagline")
    # animated shrink: full 1920x1080 -> 900x506 over t in [0.25,1.5];
    # composite onto a white bg with per-frame-centered overlay (pad can't
    # re-center a size-changing input), then the animated black pun on top.
    E = "clip((t-0.25)/1.25,0,1)"
    w = f"floor((1920-1020*({E}))/2)*2"
    h = f"floor((1080-574*({E}))/2)*2"
    fc = (f"color=c=white:s=1920x1080:r=30[bg];"
          f"[0:v]scale=w='{w}':h='{h}':eval=frame,setsar=1[lk];"
          f"[bg][lk]overlay=x='(W-w)/2':y='(H-h)/2':eval=frame:shortest=1[ov];"
          f"[ov]ass={(BUILD/'outro_pun.ass').as_posix()},format=yuv420p[v]")
    run([FF,"-y","-ss","5.0","-i",lake,"-t","2.93","-filter_complex",fc,
         "-map","[v]","-r","30","-c:v","libx264","-preset","medium","-crf","18",
         str(BUILD/"outro.mp4")],"outro")

# ---------------------------------------------------------- 3. glow captions
def ass_time(t):
    h=int(t//3600); t-=h*3600; m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

def write_captions():
    words=[]
    for seg in json.loads((AUD/"transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            t=w["start"]
            if w.get("score",1)<=0.2: continue
            if t>=24.05: continue                      # stop after the question
            if VO_TAG_START<=t<VO_TAG_END: continue    # tagline handled by pun
            words.append(w)
    lines,cur=[],[]
    for w in words:
        cur.append(w)
        if len(cur)>=6 or w["word"].endswith((".","?","!",",",";",":")):
            lines.append(cur); cur=[]
    if cur: lines.append(cur)
    # glow style: yellow fill, yellow soft halo (blur), faint dark bloom, no hard border
    style=("Style: Cap,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H0000E9F4,&H78101010,"
           "-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for ln in lines:
        start=ln[0]["start"]+OFFSET; end=ln[-1]["end"]+OFFSET
        text="{\\fad(120,120)\\blur7}"+" ".join(w["word"] for w in ln)
        ev.append(f"Dialogue: 0,{ass_time(start-0.06)},{ass_time(end+0.14)},Cap,,0,0,0,,{text}")
    header=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style}

"""
    (BUILD/"captions_v3.ass").write_text(header+"\n".join(ev)+"\n")
    print(f"  captions_v3.ass ({len(lines)} lines)")

# ---------------------------------------------------------- 4. assemble + mux
def concat_full():
    (BUILD/"concat_full.txt").write_text(
        f"file '{(BUILD/'main_graded.mp4').as_posix()}'\n"
        f"file '{(BUILD/'outro.mp4').as_posix()}'\n"
        f"file '{(BUILD/'question_graded.mp4').as_posix()}'\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"concat_full.txt"),
         "-c","copy",str(BUILD/"full.mp4")],"concat-full")

def final():
    ass=(BUILD/"captions_v3.ass").as_posix()
    run([FF,"-y","-i",str(BUILD/"full.mp4"),"-i",str(AUD/"song.mp3"),"-i",str(AUD/"voiceover.wav"),
         "-filter_complex",
         f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},fade=t=out:st={END-0.5}:d=0.5[v];"
         f"[1:a]atrim=0:{END},volume='if(lt(t,{OFFSET+0.5}),6.3,2.6)':eval=frame,"
         f"afade=t=in:d=1.2,afade=t=out:st={END-1.2}:d=1.2[song];"
         f"[2:a]adelay={int(OFFSET*1000)}|{int(OFFSET*1000)},volume=1.0[vo];"
         f"[song][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]",
         "-map","[v]","-map","[a]","-t",str(END),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"see_hook_16x9.mp4")],"final")

if __name__=="__main__":
    force=os.environ.get("FORCE")
    print("[1/6] clips");    build_clips() if (force or not (BUILD/"main.mp4").exists()) else print("  skip")
    print("[2/6] grade main");    grade("main.mp4","main_graded.mp4") if (force or not (BUILD/"main_graded.mp4").exists()) else print("  skip")
    print("[3/6] grade question");grade("seg_question.mp4","question_graded.mp4")
    print("[4/6] outro");    build_outro()
    print("[5/6] captions"); write_captions()
    print("[6/6] concat + mux"); concat_full(); final()
    print("DONE ->", OUT/"see_hook_16x9.mp4")
