#!/usr/bin/env python3
"""Main part - Chunk 13 (VO 242.84 -> ~254.44s): 'not only the ice' - the Eifel
volcanism. Beat A: the volcano clip, sky keyed to white, full-width bottom, with
layered yellow editorial type (MAGMA behind / EIFEL front). Beat B: the round
Dauner Maare aerial ('kreisrunde Krater ... Maare voll Wasser'). Editorial typo
carries it - no running subtitles.
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png"); VF=BUILD/"c13_volc"

VO_START=242.84
SONG_OFFSET=319.74                      # continues the looped song from chunk 12
D_VOLC, D_MAAR = 8.0, 3.6
TOTAL=D_VOLC+D_MAAR                      # 11.6

GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[cg]")
# editorial white beat: keep the paper clean, only a whisper of vignette + grain.
# deflicker smooths the volcano cam's exposure/key flicker; grain kept low.
WHITE_GRADE=("deflicker=size=5,eq=contrast=1.03:saturation=1.04,vignette=PI/18,"
             "noise=alls=2:allf=t,format=yuv420p")

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

# ---- beat A: volcano on white (type baked into the frames) -------------------
def beat_volc():
    fc=(f"[0:v]setsar=1,{WHITE_GRADE}[v]")
    run([FF,"-y","-framerate","30","-i",str(VF/"f_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_VOLC),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","19",str(BUILD/"c13_a.mp4")],"volc")

# ---- beat B: round Maar lakes ------------------------------------------------
def beat_maar():
    a=BUILD/"c13_maar.ass"
    YEL="&H0000BEFC"    # brand yellow in ASS BGR (R252 G190 B0)
    BK="&H00181410"
    styles=[
      f"Style: Big,Anton,120,&H00FFFFFF,&H00FFFFFF,&H00181410,&H90101010,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
      f"Style: Sub,Liberation Sans,34,&H00FFFFFF,&H00FFFFFF,&H00181410,&H90101010,-1,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
      f"Style: Tag,Liberation Sans,28,&H00FFFFFF,&H00FFFFFF,&H00181410,&H90101010,-1,0,0,0,100,100,2,0,1,0,0,3,0,0,0,1"]
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{at(0.3)},{at(D_MAAR)},Big,,0,0,0,,{{\\pos(80,60)\\fad(240,0)}}MAARE",
        f"Dialogue: 0,{at(0.3)},{at(D_MAAR)},Sub,,0,0,0,,{{\\pos(86,196)\\fad(280,0)}}kreisrunde Krater · voll Wasser",
        f"Dialogue: 0,{at(0.5)},{at(D_MAAR)},Tag,,0,0,0,,{{\\pos(1840,1012)\\fad(280,0)}}Vulkaneifel · vom Magma gesprengt"]
    a.write_text(ass_header(styles)+"\n".join(ev)+"\n")
    nf=int(D_MAAR*30)+2; z="min(zoom+0.0007,1.08)"
    fc=(f"[0:v]scale=2304:-1,zoompan=z='{z}':d={nf}:s=1920x1080:fps=30,setsar=1,{GRADE}[pre];"
        f"[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL
        +f";[cg]ass={a.as_posix()}:fontsdir={FONTS.as_posix()}[v]")
    run([FF,"-y","-loop","1","-i",str(BUILD/"c13_maar.png"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_MAAR),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","20",str(BUILD/"c13_b.mp4")],"maar")

def final():
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c13_song.wav")],"songbed")
    fc=(f"[0:v]fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c13_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c13_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk13.mp4")],"final")
    print("  ->", OUT/"main_chunk13.mp4")

if __name__=="__main__":
    print("[1/3] volc"); beat_volc()
    print("[2/3] maar"); beat_maar()
    (BUILD/"c13_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c13_a","c13_b"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c13_concat.txt"),
         "-c","copy",str(BUILD/"c13_full.mp4")],"concat")
    print("[3/3] final"); final()
    print("DONE", round(TOTAL,2),"s")
