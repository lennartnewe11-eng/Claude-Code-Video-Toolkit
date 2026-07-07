#!/usr/bin/env python3
"""Main part - Chunk 15 (VO 272.94 -> ~284.94s): DIE BEDINGUNG - the universal
recipe. One editorial beat on plain white: a basin cross-section fills with water
('ein Loch das Wasser halten kann + genug Wasser das hineinlaeuft = EIN SEE'),
then drains ('Fehlt nur eines von beidem -> trockene Senke'). Type baked in.
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, AUD = ROOT/"build", ROOT/"out", ROOT/"audio"
FF="ffmpeg"; BF=BUILD/"c15_basin"

VO_START=272.94
SONG_OFFSET=349.84                     # continues the looped song from chunk 14
TOTAL=12.0                             # ends 284.94, sentence boundary

# plain white editorial ground - clean paper, whisper of grain only
GRADE="eq=contrast=1.02:saturation=1.02,noise=alls=2:allf=t"

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p

def beat():
    fc=f"[0:v]setsar=1,{GRADE},fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v]"
    run([FF,"-y","-framerate","30","-i",str(BF/"b_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(TOTAL),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c15_full.mp4")],"beat")

def final():
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c15_song.wav")],"songbed")
    fc=(f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c15_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c15_song.wav"),"-filter_complex",fc,"-map","0:v","-map","[a]",
         "-t",str(TOTAL),"-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk15.mp4")],"final")
    print("  ->", OUT/"main_chunk15.mp4")

if __name__=="__main__":
    print("[1/2] beat"); beat()
    print("[2/2] final"); final()
    print("DONE", round(TOTAL,2),"s")
