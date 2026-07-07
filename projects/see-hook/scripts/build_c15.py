#!/usr/bin/env python3
"""Main part - Chunk 15 (VO 272.94 -> ~289.44s), collage rebuild in two parts.
Part 1 (0-12s): DIE BEDINGUNG - the basin carved into a real SOIL cross-section
with a 3-D lake (the keyed lake photo) laid over it, editorial equation, water
fills -> drains ("trockene Senke"). Then the frame BREAKS OPEN into
Part 2 (12-16.5s): the water video with the woman video blended faintly over it
(low visibility), now carrying the yellow glow subtitles.
"""
import subprocess, pathlib, sys, json

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF="ffmpeg"; BF=BUILD/"c15_basin"; IMG=MA/"c15"/"img"

VO_START=272.94
SONG_OFFSET=349.84
D1=12.0; D2=5.0; XF=0.5
TOTAL=D1+D2-XF                          # 16.5 -> ends 289.44
CAP_FROM=284.85                         # part-2 captions start here (VO abs)

GRADE1="eq=contrast=1.02:saturation=1.02,noise=alls=2:allf=t"

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

# ---- part 1: the collage basin (type baked in the frames) -------------------
def part1():
    fc=f"[0:v]setsar=1,{GRADE1},format=yuv420p[v]"
    run([FF,"-y","-framerate","30","-i",str(BF/"b_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D1),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c15_a.mp4")],"part1")

# ---- part 2: water video + faint keyed woman overlay ------------------------
def part2():
    fc=("[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "setsar=1,eq=contrast=1.05:saturation=0.92,curves=b='0/0.04 1/1'[wat];"
        "[1:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "setsar=1,format=rgba,lumakey=threshold=0.82:tolerance=0.13:softness=0.10,"
        "colorchannelmixer=aa=0.30[wom];"
        "[wat][wom]overlay=0:0:format=auto,vignette=PI/5,format=yuv420p[v]")
    run([FF,"-y","-t",str(D2),"-i",str(IMG/"water.mp4"),"-t",str(D2),"-i",str(IMG/"woman.mp4"),
         "-filter_complex",fc,"-map","[v]","-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c15_b.mp4")],"part2")

def combine():
    fc=(f"[0:v][1:v]xfade=transition=smoothup:duration={XF}:offset={D1-XF},"
        f"format=yuv420p[v]")
    run([FF,"-y","-i",str(BUILD/"c15_a.mp4"),"-i",str(BUILD/"c15_b.mp4"),
         "-filter_complex",fc,"-map","[v]","-t",str(TOTAL),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","20",str(BUILD/"c15_full.mp4")],"combine")

# ---- yellow glow captions for part 2 only -----------------------------------
def write_captions():
    d=json.load(open(AUD/"main_transcript.json"))
    words=[]
    def walk(o):
        if isinstance(o,list): [walk(x) for x in o]
        elif isinstance(o,dict):
            if 'start' in o and 'word' in o and len(o['word'])<20:
                words.append(o)
            [walk(v) for v in o.values() if isinstance(v,(list,dict))]
    walk(d)
    words=[w for w in words if w.get('start') is not None
           and CAP_FROM<=w['start']<VO_START+TOTAL]
    words.sort(key=lambda w:w['start'])
    lines,cur=[],[]
    for w in words:
        cur.append(w)
        if len(cur)>=5 or w['word'].endswith((".","!","?",",",";",":")):
            lines.append(cur); cur=[]
    if cur: lines.append(cur)
    style=("Style: Cap,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H0000E9F4,&H78101010,"
           "-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i,ln in enumerate(lines):
        s=max(0.0,ln[0]['start']-VO_START-0.05); e=ln[-1]['end']-VO_START+0.12
        if i+1<len(lines): e=min(e, lines[i+1][0]['start']-VO_START-0.03)
        txt="{\\fad(90,90)\\blur7}"+" ".join(w['word'] for w in ln)
        ev.append(f"Dialogue: 0,{at(s)},{at(e)},Cap,,0,0,0,,{txt}")
    (BUILD/"c15_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c15_song.wav")],"songbed")
    caps=(BUILD/"c15_caps.ass").as_posix()
    fc=(f"[0:v]ass={caps}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c15_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c15_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk15.mp4")],"final")
    print("  ->", OUT/"main_chunk15.mp4")

if __name__=="__main__":
    print("[1/4] part1"); part1()
    print("[2/4] part2"); part2()
    print("[3/4] combine (break open)"); combine()
    print("[4/4] final"); final()
    print("DONE", round(TOTAL,2),"s")
