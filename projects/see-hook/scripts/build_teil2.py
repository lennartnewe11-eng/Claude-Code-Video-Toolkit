#!/usr/bin/env python3
"""Build Teil 2 of the See video (VO 24.9s-53.5s of the transcript).

Timeline (T2 seconds):
  0.00-5.17   flower video on white; Loch Ness collage + "mystic" x5 slide in
  5.17-8.07   Tagesschau TikTok clip (VO pauses, only music)
  8.07-14.28  "...nackt baden ... Hollywood-Romance"  -> swim clips
  14.28-18.38 "...jemanden verschwinden lassen"       -> red EYES gif
  18.38-27.71 "...Zufluchtsort vor der Hitze ..."      -> summer / city / getaway
  27.71-31.78 "...warum hier Wasser und hier nicht?"   -> lake vs dry basin

Music continues seamlessly from the intro (song offset 42.25s). Yellow glow
captions synced to the VO (paused during the TikTok clip).
"""
import json, subprocess, pathlib, sys, glob
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from make_intro import ink_strength, draw_order, smooth   # reuse stroke logic
A, BUILD, OUT = ROOT/"assets", ROOT/"build", ROOT/"out"
T2A, UF, AUD, FONTS = ROOT/"teil2_assets", ROOT/"user_footage", ROOT/"audio", ROOT/"fonts"
PX = T2A/"pexels"
BUILD.mkdir(exist_ok=True)
FF = "ffmpeg"
SCAN = str(BUILD/"scanlines.png")
LIB_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def g(pattern, base):   # first file matching a glob under base
    hits = sorted(glob.glob(str(base/pattern)))
    if not hits: sys.exit("missing asset: "+pattern)
    return hits[0]

FLOWER   = g("*Minimal vision board*.mp4", T2A)
LOCHNESS = str(T2A/"Download (25).jpeg")
TIKTOK   = g("v2*.mp4", T2A)
EYES     = g("*election season*.gif", T2A)
FIELD    = str(T2A/"4f1d1b7c9b2f87ad25dbac53530e7be6.jpg")
CYCLIST  = str(T2A/"Download (26)-Photoroom.png")
WADE     = g("*Explore these 21 Fresh travel*.gif", UF)
UNDER    = g("*Boho home decor*.gif", UF)
C2       = str(A/"C2_notlake_37533724.mp4")

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
SONG_OFFSET = 42.25          # continue the track from the end of the intro
TIKTOK_DUR = 4.84            # full length of the (new, better) Tagesschau excerpt
TOTAL = 34.65

def run(cmd, label=""):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3200:]); raise SystemExit(1)
    return p

# ---- graded realistic segment (warm CRT look, matches the hook) ------------
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")

def seg_graded(src, tin, dur, dst, loop=False, image=False):
    inp = []
    if image: inp = ["-loop","1","-t",str(dur),"-i",src]
    elif loop: inp = ["-stream_loop","-1","-ss",str(tin),"-t",str(dur),"-i",src]
    else: inp = ["-ss",str(tin),"-t",str(dur),"-i",src]
    fc = (f"[0:v]{NORM},{GRADE}[gc];[1:v]scale=1920:1080,setsar=1[sc];"
          "[gc][sc]blend=all_mode=multiply:all_opacity=0.38:shortest=1[m];"
          "[m]vignette=PI/5.5,noise=alls=5:allf=t,format=yuv420p[v]")
    run([FF,"-y",*inp,"-loop","1","-i",SCAN,"-filter_complex",fc,
         "-map","[v]","-t",str(dur),"-r","30","-c:v","libx264","-preset","veryfast",
         "-crf","18",str(BUILD/dst)], dst)

def gen_stroke_frames(png, outdir, dur, fps=30, dstart=0.12, ddur=2.45):
    """Stroke-by-stroke reveal frames (black ink + soft glow), like the intro."""
    outdir=pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.png"): f.unlink()
    alpha0=ink_strength(png); order,ink=draw_order(alpha0); H,W=order.shape
    ink_rgb=np.zeros((H,W,4),np.uint8)
    glow_rgb=np.zeros((H,W,4),np.uint8); glow_rgb[:,:,:3]=250
    for i in range(int(dur*fps)):
        t=i/fps; p=smooth((t-dstart)/ddur)
        factor=np.clip((p-order)/0.02,0,1)
        al=(np.minimum(alpha0*1.5,255)*factor).astype(np.uint8)
        ga=Image.fromarray(al,"L").filter(ImageFilter.GaussianBlur(5))
        gl=glow_rgb.copy(); gl[:,:,3]=(np.array(ga).astype(np.float32)*0.5).astype(np.uint8)
        ik=ink_rgb.copy(); ik[:,:,3]=al
        Image.alpha_composite(Image.fromarray(gl,"RGBA"),Image.fromarray(ik,"RGBA")).save(
            outdir/f"f_{i:04d}.png")

def build_s12c(dur, dst):
    """Summer field still (graded) with the cyclist sketch drawn on stroke by
    stroke, bottom-centred so its road roughly aligns with the field path."""
    fdir=BUILD/"t2_cyc_frames"
    gen_stroke_frames(CYCLIST, fdir, dur)
    fc=(f"[0:v]{NORM},{GRADE}[gc];[2:v]scale=1920:1080,setsar=1[sc];"
        "[gc][sc]blend=all_mode=multiply:all_opacity=0.38:shortest=1[m];"
        "[m]vignette=PI/5.5,noise=alls=5:allf=t[bg];"
        "[1:v]scale=-1:1000,setsar=1[cyc];"
        "[bg][cyc]overlay=x=(W-w)/2:y=H-h:shortest=1,format=yuv420p[v]")
    run([FF,"-y","-loop","1","-t",str(dur),"-i",FIELD,
         "-framerate","30","-i",str(fdir/"f_%04d.png"),
         "-loop","1","-i",SCAN,"-filter_complex",fc,"-map","[v]","-t",str(dur),
         "-r","30","-c:v","libx264","-preset","veryfast","-crf","18",str(BUILD/dst)],dst)

# ---- phase A: flower on white + Loch Ness collage + mystic ------------------
def write_mystic_ass(dur):
    lines=[]
    for i in range(5):
        y=150+i*185
        d=300+i*80                # appear early, one after another
        lines.append(f"Dialogue: 0,0:00:00.00,0:00:{dur:05.2f},M,,0,0,0,,"
                     f"{{\\an4\\pos(95,{y})\\fs150\\1c&H000000&\\bord0\\alpha&HFF&"
                     f"\\t({d},{d+260},\\alpha&H00&)}}mystic")
    ass=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
         "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
         "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
         "Style: M,Liberation Sans,150,&H00000000,&H00000000,&H00000000,&H00000000,"
         "-1,0,0,0,100,100,0,0,1,0,0,4,0,0,0,1\n\n"
         "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
         + "\n".join(lines)+"\n")
    (BUILD/"mystic.ass").write_text(ass)

MYTH_YEAR = "1933"     # modern Loch Ness Monster myth (first reports, 1933)

def phase_a1():
    """Flower on white (short) with mystic x5 on the left."""
    dur=2.53
    write_mystic_ass(dur)
    fc=("[0:v]negate,eq=saturation=0.14:brightness=0.16:contrast=1.05,"
        "scale=1920:1920:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[fl];"
        f"[fl]ass={(BUILD/'mystic.ass').as_posix()}:fontsdir={FONTS.as_posix()},"
        "format=yuv420p[v]")
    run([FF,"-y","-stream_loop","-1","-i",FLOWER,"-filter_complex",fc,
         "-map","[v]","-t",str(dur),"-r","30","-c:v","libx264","-preset","veryfast",
         "-crf","18",str(BUILD/"t2_A1.mp4")],"phaseA1")

def write_year_ass(dur):
    ass=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
         "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
         "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
         "Style: Y,Liberation Sans,500,&H00000000,&H00000000,&H00000000,&H00000000,"
         "-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n"
         "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
         f"Dialogue: 0,0:00:00.00,0:00:{dur:05.2f},Y,,0,0,0,,"
         f"{{\\an5\\pos(960,250)\\fad(280,0)}}{MYTH_YEAR}\n")
    (BUILD/"year.ass").write_text(ass)

def phase_a2():
    """Loch Ness gets its own white frame, large, with the myth year big
    behind/above it."""
    dur=2.57
    write_year_ass(dur)
    fc=(f"color=c=white:s=1920x1080:r=30:d={dur}[bg];"
        f"[bg]ass={(BUILD/'year.ass').as_posix()}:fontsdir={FONTS.as_posix()}[num];"
        "[0:v]scale=780:-1,pad=iw+26:ih+26:13:13:white[ln];"
        "[num][ln]overlay=x=(W-w)/2:y=345:shortest=1,format=yuv420p[v]")
    run([FF,"-y","-loop","1","-t",str(dur),"-i",LOCHNESS,"-filter_complex",fc,
         "-map","[v]","-t",str(dur),"-r","30","-c:v","libx264","-preset","veryfast",
         "-crf","18",str(BUILD/"t2_A2.mp4")],"phaseA2")

def phase_tiktok():
    dur=TIKTOK_DUR
    fc=("[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "gblur=sigma=30,eq=brightness=-0.05[bg];"
        "[0:v]scale=-1:1040,setsar=1[fg];"
        "[bg][fg]overlay=x=(W-w)/2:y=(H-h)/2,fps=30,format=yuv420p[v]")
    run([FF,"-y","-i",TIKTOK,"-filter_complex",fc,"-map","[v]","-t",str(dur),
         "-r","30","-c:v","libx264","-preset","veryfast","-crf","18",
         str(BUILD/"t2_tiktok.mp4")],"tiktok")

# ---- assemble video --------------------------------------------------------
def build_segments():
    phase_a1()
    phase_a2()
    phase_tiktok()
    seg_graded(WADE, 0, 4.11, "t2_s10a.mp4", loop=True)   # +1s silent beat after the TikTok
    seg_graded(UNDER, 0, 3.10, "t2_s10b.mp4", loop=True)
    seg_graded(EYES, 0, 4.10, "t2_s11.mp4", loop=True)
    seg_graded(str(PX/"s12_lake.mp4"), 1.0, 3.10, "t2_s12a.mp4")
    seg_graded(str(PX/"s12_city.mp4"), 1.0, 3.10, "t2_s12b.mp4")
    build_s12c(3.13, "t2_s12c.mp4")
    seg_graded(str(PX/"s13_lake.mp4"), 1.0, 3.17, "t2_s13a.mp4")  # lake stays until "...Wasser"
    seg_graded(C2, 39.0, 0.90, "t2_s13b.mp4")                     # then cut to dry basin
    order=["t2_A1","t2_A2","t2_tiktok","t2_s10a","t2_s10b","t2_s11",
           "t2_s12a","t2_s12b","t2_s12c","t2_s13a","t2_s13b"]
    (BUILD/"t2_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in order)+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"t2_concat.txt"),
         "-c","copy",str(BUILD/"t2_full.mp4")],"concat")

# ---- captions (yellow glow, mapped to T2) ----------------------------------
def at(t):
    h=int(t//3600); t-=h*3600; m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

VO_A0, VO_A1, VO_B0, VO_B_T2 = 24.70, 29.80, 29.89, 10.94   # trims / offset
# VO_B_T2 = phaseA(5.10) + TikTok(4.84) + ~1s silent beat -> VO resumes at 10.94

def vo_to_t2(t):
    if t < VO_A1: return t - VO_A0            # phase A
    return VO_B_T2 + (t - VO_B0)              # phase B (after tiktok)

def write_captions():
    words=[]
    for seg in json.loads((AUD/"transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            if 24.85 <= w["start"] < 53.55 and w.get("score",1)>0.2:
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
    for ln in lines:
        ts, te = ln[0]["start"], ln[-1]["end"]
        if ts < VO_A1:                       # phase A line: map both ends in A
            s, e = ts-VO_A0, min(te-VO_A0, 5.08)
        else:                                # phase B line
            s, e = VO_B_T2+(ts-VO_B0), VO_B_T2+(te-VO_B0)
        txt="{\\fad(110,110)\\blur7}"+" ".join(w["word"] for w in ln)
        ev.append(f"Dialogue: 0,{at(s-0.05)},{at(e+0.12)},Cap,,0,0,0,,{txt}")
    header=("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+style+"\n\n")
    (BUILD/"t2_caps.ass").write_text(header+"\n".join(ev)+"\n")

# ---- final mux: captions + audio (VO with pause + continued song) ----------
def final():
    write_captions()
    ass=(BUILD/"t2_caps.ass").as_posix()
    silence=round(TIKTOK_DUR+1.00, 2)     # TikTok + ~1s extra beat
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        # VO part A, then silence during tiktok, then VO part B
        f"[1:a]atrim={VO_A0}:{VO_A1},asetpts=PTS-STARTPTS,volume=1.0[voa];"
        f"[2:a]atrim={VO_B0}:53.60,asetpts=PTS-STARTPTS,volume=1.0[vob];"
        f"anullsrc=r=44100:cl=stereo,atrim=0:{silence}[sil];"
        f"[voa][sil][vob]concat=n=3:v=0:a=1[vo];"
        # song 1: quieter overall, DROPS out just before "Aber jetzt mal
        # wirklich" (T2 27.68) and stays silent after
        f"[3:a]atrim=0:{TOTAL},volume=2.0,afade=t=out:st=30.32:d=0.30[song];"
        # Tagesschau clip audio, synced to its slot (T2 5.10 .. 5.10+dur)
        f"[4:a]atrim=0:{TIKTOK_DUR},adelay=5100|5100,volume=1.15[tk];"
        # soundtrack 2 (sachlicher): begins at the drop and runs to the end
        f"[5:a]atrim=0:4.6,afade=t=in:d=0.8,volume=1.5,adelay=30620|30620[st2];"
        f"[song][vo][tk][st2]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"t2_full.mp4"),"-i",str(AUD/"voiceover.wav"),
         "-i",str(AUD/"voiceover.wav"),"-ss",str(SONG_OFFSET),"-i",str(AUD/"song.mp3"),
         "-i",TIKTOK,"-i",str(AUD/"soundtrack2.mp3"),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(TOTAL),
         "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"teil2.mp4")],"final")
    print("  ->", OUT/"teil2.mp4")

if __name__=="__main__":
    print("[1/3] segments"); build_segments()
    print("[2/3] (captions in final)")
    print("[3/3] final mux"); final()
    print("DONE ->", OUT/"teil2.mp4")
