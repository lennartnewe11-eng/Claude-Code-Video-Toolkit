#!/usr/bin/env python3
"""Main part - Chunk 14 (VO 254.44 -> ~272.94s): the other lake-makers, and us.
Beat A: the Altarme river cut-out laid out like the reference collage (torn
subject right, editorial type nested in the left negative space, layered ghost
word behind + red-orange annotation in front), pivoting to '...der fleißigste
Seebauer sind wir selbst.' Beat B: the Tagebau Hambach time-lapse in a torn
window (Lausitz -> riesige, brandneue Seen). Type is baked into the frames;
a light CRT scanline + grain keeps the series look.
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")
RF=BUILD/"c14_river"; TF=BUILD/"c14_tag"

VO_START=254.44
SONG_OFFSET=331.34                     # continues the looped song from chunk 13
D_RIVER, D_TAG = 10.0, 8.5
TOTAL=D_RIVER+D_TAG                     # 18.5  -> ends 272.94, sentence boundary

# cool editorial paper grade + light CRT scanline tail (series signature).
# NB: the scanline multiply MUST run in RGB (gbrp) - multiplying two yuv420p
# streams mangles the chroma planes and skews the neutral paper green.
GRADE=("eq=contrast=1.05:saturation=1.02,vignette=PI/16,noise=alls=3:allf=t")

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p

def beat(frames,dur,out,label):
    fc=(f"[0:v]setsar=1,{GRADE},format=gbrp[pre];"
        f"[1:v]scale=1920:1080,setsar=1,format=gbrp[sc];"
        f"[pre][sc]blend=all_mode=multiply:all_opacity=0.22:shortest=1,format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(frames/("r_%04d.png" if label=="river"
         else "t_%04d.png")),"-loop","1","-i",SCAN,"-filter_complex",fc,"-map","[v]",
         "-t",str(dur),"-r","30","-c:v","libx264","-preset","medium","-crf","20",
         str(out)],label)

def final():
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c14_song.wav")],"songbed")
    fc=(f"[0:v]fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c14_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c14_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk14.mp4")],"final")
    print("  ->", OUT/"main_chunk14.mp4")

if __name__=="__main__":
    print("[1/3] river"); beat(RF,D_RIVER,BUILD/"c14_a.mp4","river")
    print("[2/3] tagebau"); beat(TF,D_TAG,BUILD/"c14_b.mp4","tag")
    (BUILD/"c14_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'" for o in ["c14_a","c14_b"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c14_concat.txt"),
         "-c","copy",str(BUILD/"c14_full.mp4")],"concat")
    print("[3/3] final"); final()
    print("DONE", round(TOTAL,2),"s")
