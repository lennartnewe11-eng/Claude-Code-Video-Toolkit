#!/usr/bin/env python3
"""Main part - Chunk 9 (VO 155.71 -> 192.85s): the lakes are the footprint of a
glacier TONGUE (Wortwitz), so they are deep (Bodensee 250 m), and the glacier
delivered the seal too (Geschiebemergel = watertight liner) -> 2-in-1 service.

  beat 1a  tongue photo on a full-frame yellow field (Gletscher-ZUNGE pun)
  beat 1b  real glacier-front video
  beat 2   editorial spread: grey VO waveform (Tonspur) on white + collages
           (depth/250 m, Geschiebemergel liner + water, 2-in-1 badge)
Captions are intentionally dropped here (yellow glow is unreadable on the yellow
tongue and white editorial; the reference carries no caption bar).
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C9=MA/"c9"; FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")
EDD=BUILD/"c9_ed"

VO_START=155.71
SONG_OFFSET=232.61                     # continues the looped song from chunk 8
D_T, D_G = 3.40, 3.73                  # tongue, glacier video
D_ED = 30.01                           # editorial (162.84 .. 192.85)
TOTAL = D_T + D_G + D_ED               # 37.14

NORM = ("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,fps=30,setsar=1,format=yuv420p")
GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[cg]")

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p

# ---- beat 1a: tongue on yellow ----------------------------------------------
def beat_tongue():
    fc=("[0:v]scale=1920:1080,setsar=1,noise=alls=5:allf=t,vignette=PI/8,"
        "format=yuv420p[v]")
    run([FF,"-y","-loop","1","-i",str(BUILD/"c9_tongue.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_T),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","19",str(BUILD/"c9_b1a.mp4")],"tongue")

# ---- beat 1b: real glacier front --------------------------------------------
def beat_glacier():
    fc=(f"[0:v]{NORM},{GRADE}[pre];[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL
        +";[cg]copy[v]")
    run([FF,"-y","-ss","2.0","-i",str(C9/"ref"/"ref_vid.mp4"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_G),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","19",str(BUILD/"c9_b1b.mp4")],"glacier")

# ---- beat 2: editorial waveform + collages ----------------------------------
def beat_editorial():
    # frames already carry waveform/playhead/collages; keep the white, add grain
    fc=("[0:v]setsar=1,noise=alls=3:allf=t,vignette=PI/10,format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(EDD/"e_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_ED),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c9_b2.mp4")],"editorial")

def final():
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c9_song.wav")],"songbed")
    fc=(f"[0:v]fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c9_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c9_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk9.mp4")],"final")
    print("  ->", OUT/"main_chunk9.mp4")

if __name__=="__main__":
    print("[1/4] tongue");    beat_tongue()
    print("[2/4] glacier");   beat_glacier()
    print("[3/4] editorial"); beat_editorial()
    (BUILD/"c9_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'"
                  for o in ["c9_b1a","c9_b1b","c9_b2"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c9_concat.txt"),
         "-c","copy",str(BUILD/"c9_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", round(TOTAL,2),"s")
