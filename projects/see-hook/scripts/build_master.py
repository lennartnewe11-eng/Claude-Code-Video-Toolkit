#!/usr/bin/env python3
"""Assemble the whole main video (chunks 1-16) into one file with a SINGLE,
continuous audio track laid fresh over the concatenated visuals - so there are
no seams. The per-chunk audio is discarded; the clean VO (main_vo.wav) is laid
from 0 (chunk 1 starts at VO 0 and the chunks are contiguous) and the music
(song.mp3) is looped continuously and ducked under the VO. The video is stream-
copied (no quality loss); only the audio is (re)built.
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, AUD = ROOT/"build", ROOT/"out", ROOT/"audio"
FF="ffmpeg"; M=BUILD/"master"; M.mkdir(parents=True, exist_ok=True)
N=16

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p
def dur(path):
    import re
    p=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",p.stderr)
    h,mn,s=m.groups(); return int(h)*3600+int(mn)*60+float(s)

def concat_video():
    lst=M/"list.txt"
    lst.write_text("\n".join(f"file '{(OUT/f'main_chunk{n}.mp4').as_posix()}'" for n in range(1,N+1))+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(lst),"-an","-c:v","copy",
         str(M/"master_v.mp4")],"concat")

def final():
    D=dur(M/"master_v.mp4")                      # ~317 s
    # VO padded to full length (so the music carries the ~3 s finale tail);
    # music looped to cover the whole film and ducked under the VO.
    fc=(f"[1:a]volume=1.15,apad,asplit=2[vo1][vo2];"
        f"[2:a]atrim=0:{D},asetpts=PTS-STARTPTS,volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,"
        f"afade=t=in:d=0.6,afade=t=out:st={D-2.2}:d=2.2[a]")
    run([FF,"-y","-i",str(M/"master_v.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-stream_loop","3","-i",str(AUD/"song.mp3"),
         "-filter_complex",fc,"-map","0:v","-map","[a]","-c:v","copy",
         "-c:a","aac","-b:a","192k","-movflags","+faststart","-t",f"{D}",
         str(OUT/"main_full.mp4")],"master")
    print(f"  -> {OUT/'main_full.mp4'}  ({D:.2f}s)")

if __name__=="__main__":
    print("[1/2] concat video"); concat_video()
    print("[2/2] lay fresh audio"); final()
    print("DONE")
