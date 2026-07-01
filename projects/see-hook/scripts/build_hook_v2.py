#!/usr/bin/env python3
"""Build the 'See' hook v2.

Structure (T = final timeline seconds, VO delayed by OFFSET):
  0.0 - 6.0   song-only intro over the birds clip
  6.75        voiceover starts ("Das ist ein See")  -> birds still on screen
  ~8.6        dissolve into the aerial lake ("auch ein See")
  11.6        puddle ("kein See")
  14.3        terrain -> Mr Bean #1 -> clouds  (the confusing facts)
  24.2        Mr Bean #2 ("Wie kann das sein?")
  25.7        outro card: lake shrinks onto white bg + big "Seen oder geseen werden"

Captions: modern, crisp, yellow Helvetica, overlaid AFTER the grade (so they
break the retro look). Grade: warm CRT but toned down.
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS, BUILD, OUT = ROOT / "assets", ROOT / "build", ROOT / "out"
UF, AUD, FONTS = ROOT / "user_footage", ROOT / "audio", ROOT / "fonts"
BUILD.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
FF = "ffmpeg"
LIB_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

OFFSET = 6.0          # voiceover starts this many seconds in
VO_TAGLINE = 19.69    # vo-time where the tagline begins (handled by outro card)
END = 28.85           # total length

manifest = {m["shot"]: m for m in json.loads((BUILD / "footage_manifest.json").read_text()) if m.get("ok")}
def pex(shot): return str(ASSETS / manifest[shot]["file"])

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")

def run(cmd, label=""):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"\n### FAIL {label}\n" + p.stderr[-3500:])
        raise SystemExit(1)
    return p

def clip(src, t_in, dur, dst, extra=""):
    vf = NORM + (("," + extra) if extra else "")
    run([FF, "-y", "-ss", str(t_in), "-i", src, "-t", str(round(dur, 3)),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", str(BUILD / dst)], dst)

# ----------------------------------------------------------- 1. clips
def build_clips():
    # birds + aerial lake get a dissolve, rendered together as seg_intro.mp4
    clip(str(UF / "birds.mp4"),   0.0, 8.88, "_birds.mp4")
    clip(pex("A_lake1"),          1.0, 3.19, "_lake1.mp4")
    run([FF, "-y", "-i", str(BUILD/"_birds.mp4"), "-i", str(BUILD/"_lake1.mp4"),
         "-filter_complex",
         "[0][1]xfade=transition=dissolve:duration=0.5:offset=8.38,format=yuv420p[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         str(BUILD/"seg_intro.mp4")], "xfade-intro")   # 0 -> 11.57

    clip(pex("C_notlake"), 2.0, 2.72, "seg_C.mp4")            # 11.57-14.29
    clip(pex("D_terrain"), 0.5, 3.71, "seg_D.mp4")            # 14.29-18.0
    clip(str(UF/"mrbean.mp4"), 0.4, 2.20, "seg_bean1.mp4")    # 18.0-20.2
    clip(pex("F_weather"), 2.0, 4.01, "seg_F.mp4")            # 20.2-24.21
    clip(str(UF/"mrbean.mp4"), 4.2, 1.48, "seg_bean2.mp4")    # 24.21-25.69

    parts = ["seg_intro","seg_C","seg_D","seg_bean1","seg_F","seg_bean2"]
    (BUILD/"concat_main.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{p}.mp4').as_posix()}'" for p in parts)+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"concat_main.txt"),
         "-c","copy",str(BUILD/"main.mp4")], "concat-main")

# ----------------------------------------------------------- 2. grade (toned down warmth)
def grade_main():
    run([FF,"-y","-i",str(BUILD/"main.mp4"),
         "-loop","1","-i",str(BUILD/"scanlines.png"),
         "-filter_complex",
         "[0:v]colortemperature=temperature=5200:mix=0.65:pl=1,"
         "eq=contrast=1.045:saturation=1.10:gamma=0.99:brightness=0.006,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98'[grade];"
         "[grade]split[g1][g2];[g2]gblur=sigma=8[gb];"
         "[g1][gb]blend=all_mode=screen:all_opacity=0.22[bloom];"
         "[bloom]rgbashift=rh=2:bh=-2[ca];"
         "[ca]lenscorrection=k1=0.05:k2=0.012:i=bilinear[lens];"
         "[1:v]scale=1920:1080,setsar=1[scan];"
         "[lens][scan]blend=all_mode=multiply:all_opacity=0.50:shortest=1[sl];"
         "[sl]vignette=PI/5,noise=alls=5:allf=t+u,format=yuv420p[v]",
         "-map","[v]","-c:v","libx264","-preset","veryfast","-crf","16",
         str(BUILD/"main_graded.mp4")], "grade")

# ----------------------------------------------------------- 3. outro card (clean, modern)
def write_outro_ass():
    txt = r"{\pos(960,858)\an5\fad(280,0)}Seen oder\Ngeseen werden"
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,Liberation Sans,132,&H0000E9F4,&H0000E9F4,&H00141414,&H64000000,-1,0,0,0,100,100,1,0,1,6,3,5,60,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:03.20,Big,,0,0,0,,{txt}
"""
    (BUILD/"outro_text.ass").write_text(ass)

def build_outro():
    lake = pex("H_tagline")
    write_outro_ass()
    # white bg + shrunk lake (upper) + big two-line pun text via libass, fading in
    fc = (
        "color=c=white:s=1920x1080:d=3.2:r=30[bg];"
        "[1:v]scale=900:506,setsar=1,format=yuv420p[small];"
        "[bg][small]overlay=(W-w)/2:90[c1];"
        f"[c1]ass={(BUILD/'outro_text.ass').as_posix()},format=yuv420p[card]"
    )
    run([FF,"-y","-f","lavfi","-i","nullsrc=s=1920x1080",
         "-i",lake,"-filter_complex",fc,"-map","[card]","-t","3.2",
         "-c:v","libx264","-preset","veryfast","-crf","18",str(BUILD/"_card.mp4")],"card")
    # short full lake lead, then dissolve into the card (the 'shrink')
    clip(lake, 5.0, 0.9, "_lakefull.mp4")
    run([FF,"-y","-i",str(BUILD/"_lakefull.mp4"),"-i",str(BUILD/"_card.mp4"),
         "-filter_complex",
         "[0][1]xfade=transition=dissolve:duration=0.4:offset=0.5,format=yuv420p[v]",
         "-map","[v]","-c:v","libx264","-preset","medium","-crf","19",
         str(BUILD/"outro.mp4")],"outro-xfade")   # ~3.1s

def concat_full():
    (BUILD/"concat_full.txt").write_text(
        f"file '{(BUILD/'main_graded.mp4').as_posix()}'\n"
        f"file '{(BUILD/'outro.mp4').as_posix()}'\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"concat_full.txt"),
         "-c","copy",str(BUILD/"full.mp4")],"concat-full")

# ----------------------------------------------------------- 4. modern captions
def ass_time(t):
    h=int(t//3600); t-=h*3600; m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

def write_captions():
    words=[]
    for seg in json.loads((AUD/"transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            if w["start"] < VO_TAGLINE and w.get("score",1) > 0.2:
                words.append(w)
    # group into short phrases
    lines,cur=[],[]
    for w in words:
        cur.append(w)
        if len(cur)>=6 or w["word"].endswith((".","?","!",",",";",":")):
            lines.append(cur); cur=[]
    if cur: lines.append(cur)
    header=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Liberation Sans,76,&H0000E9F4,&H0000E9F4,&H00141414,&H64000000,-1,0,0,0,100,100,0.4,0,1,4.5,2,2,180,180,150,1
"""
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for ln in lines:
        start=ln[0]["start"]+OFFSET
        end=ln[-1]["end"]+OFFSET
        text=" ".join(w["word"] for w in ln)
        text="{\\fad(120,120)}"+text
        ev.append(f"Dialogue: 0,{ass_time(start-0.06)},{ass_time(end+0.14)},Cap,,0,0,0,,{text}")
    (BUILD/"captions_v2.ass").write_text(header+"\n".join(ev)+"\n")
    print(f"  captions_v2.ass ({len(lines)} lines)")

# ----------------------------------------------------------- 5. final mux
def final():
    ass=(BUILD/"captions_v2.ass").as_posix()
    run([FF,"-y",
         "-i",str(BUILD/"full.mp4"),
         "-i",str(AUD/"song.mp3"),
         "-i",str(AUD/"voiceover.wav"),
         "-filter_complex",
         f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
         f"fade=t=out:st={END-0.5}:d=0.5[v];"
         # song is a very quiet track -> boost a lot; loud in intro, ducked under VO
         f"[1:a]atrim=0:{END},volume='if(lt(t,{OFFSET+0.5}),6.3,2.6)':eval=frame,"
         f"afade=t=in:d=1.2,afade=t=out:st={END-1.2}:d=1.2[song];"
         # VO already peaks near 0 dBFS -> keep at unity, don't amplify
         f"[2:a]adelay={int(OFFSET*1000)}|{int(OFFSET*1000)},volume=1.0[vo];"
         f"[song][vo]amix=inputs=2:normalize=0:duration=first,"
         f"alimiter=limit=0.95:level=disabled[a]",
         "-map","[v]","-map","[a]","-t",str(END),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"see_hook_16x9.mp4")],"final")

if __name__=="__main__":
    import os
    force = os.environ.get("FORCE")
    print("[1/5] clips + concat")
    if force or not (BUILD/"main.mp4").exists(): build_clips()
    else: print("  skip (main.mp4 exists)")
    print("[2/5] grade")
    if force or not (BUILD/"main_graded.mp4").exists(): grade_main()
    else: print("  skip (main_graded.mp4 exists)")
    print("[3/5] outro card");          build_outro(); concat_full()
    print("[4/5] captions");            write_captions()
    print("[5/5] final mux");           final()
    print("DONE ->", OUT/"see_hook_16x9.mp4")
