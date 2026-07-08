#!/usr/bin/env python3
"""Assemble the ENTIRE film: Hook -> Intro -> Teil 2 -> Hauptteil (chunks 1-16).
The three front clips are internally seamless by design (one chained song, the
Tagesschau insert in Teil 2), so they are concatenated as-is (their baked audio
kept). The Hauptteil gets one continuous VO + a music bed that CONTINUES the same
song position (76.90, exactly where Teil 2 ends), and the Teil2->Hauptteil join
is a short cross-dissolve (video is black->black there) so the audio has no seam.
"""
import subprocess, pathlib, sys, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, AUD, MA = ROOT/"build", ROOT/"out", ROOT/"audio", ROOT/"main_assets"
FF="ffmpeg"; M=BUILD/"master"; M.mkdir(parents=True, exist_ok=True)
OUTRO = MA/"outro"/"outro.mov"          # credits-collage outro (own audio, kept as-is)
SONG_MAIN=76.90                 # song time where Teil 2 ends -> Hauptteil continues it
XF=0.6

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p
def dur(path):
    p=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",p.stderr)
    h,mn,s=m.groups(); return int(h)*3600+int(mn)*60+float(s)

def concat_front():
    lst=M/"front.txt"
    lst.write_text("\n".join(f"file '{(OUT/f).as_posix()}'"
        for f in ["see_hook_16x9.mp4","intro.mp4","teil2.mp4"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",
         str(M/"front.mp4")],"concat front")

def concat_main_video():
    lst=M/"list.txt"
    lst.write_text("\n".join(f"file '{(OUT/f'main_chunk{n}.mp4').as_posix()}'" for n in range(1,17))+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(lst),"-an","-c:v","copy",
         str(M/"master_v.mp4")],"concat main")

def main_av():
    D=dur(M/"master_v.mp4")
    fc=(f"[1:a]volume=1.15,apad,asplit=2[vo1][vo2];"
        f"[2:a]atrim=0:{D},asetpts=PTS-STARTPTS,volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,"
        f"afade=t=out:st={D-2.2}:d=2.2[a]")
    run([FF,"-y","-i",str(M/"master_v.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-stream_loop","4","-ss",str(SONG_MAIN),"-i",str(AUD/"song.mp3"),
         "-filter_complex",fc,"-map","0:v","-map","[a]","-c:v","copy",
         "-c:a","aac","-b:a","192k","-t",f"{D}",str(M/"main_av.mp4")],"main_av")

def join():
    FD=dur(M/"front.mp4")
    fc=(f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={FD-XF},format=yuv420p[v];"
        f"[0:a][1:a]acrossfade=d={XF}:c1=tri:c2=tri[a]")
    run([FF,"-y","-i",str(M/"front.mp4"),"-i",str(M/"main_av.mp4"),
         "-filter_complex",fc,"-map","[v]","-map","[a]",
         "-c:v","libx264","-preset","faster","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(M/"see_film.mp4")],"join")

def append_outro():
    # scale the outro to match the film; keep its own audio track unchanged
    run([FF,"-y","-i",str(OUTRO),"-vf",
         "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
         "fps=30,setsar=1,format=yuv420p","-c:v","libx264","-preset","medium",
         "-crf","20","-c:a","copy",str(M/"outro_norm.mp4")],"outro norm")
    lst=M/"full_outro.txt"
    lst.write_text(f"file '{(M/'see_film.mp4').as_posix()}'\nfile '{(M/'outro_norm.mp4').as_posix()}'\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",
         str(OUT/"see_full.mp4")],"append outro")
    print(f"  -> {OUT/'see_full.mp4'}  ({dur(OUT/'see_full.mp4'):.2f}s incl. outro)")

if __name__=="__main__":
    print("[1/5] concat front"); concat_front()
    print("[2/5] concat main video"); concat_main_video()
    print("[3/5] main audio bed"); main_av()
    print("[4/5] join (cross-dissolve)"); join()
    print("[5/5] append outro"); append_outro()
    print("DONE")
