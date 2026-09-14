#!/usr/bin/env python3
"""Shots zusammenfuegen, Typo einbrennen, Musik anlegen."""
import os, subprocess, sys, glob, json
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def assemble(name, ass=None, audio_len=None, out=None):
    shots = sorted(glob.glob(os.path.join(P,"build","shots",f"{name}_*.mp4")))
    lst = os.path.join(P,"build",f"{name}_concat.txt")
    with open(lst,"w") as f:
        for s in shots: f.write(f"file '{s}'\n")
    silent = os.path.join(P,"build",f"{name}_silent.mp4")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat",
                    "-safe","0","-i",lst,"-c","copy",silent],check=True)
    dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",silent],capture_output=True,text=True).stdout.strip())
    out = out or os.path.join(P,"out",f"{name}.mp4")
    os.makedirs(os.path.dirname(out),exist_ok=True)
    vf = []
    if ass: vf.append(f"ass={ass}")
    # feines Korn + leichte Vignette ueber alles -> bindet die Quellen zusammen
    vf.append("noise=alls=4:allf=t,vignette=angle=PI/6:mode=backward")
    music = os.path.join(P,"assets","audio","music_bed.wav")
    fc = (f"[0:v]{','.join(vf)}[v];"
          f"[1:a]atrim=0:{dur:.4f},asetpts=PTS-STARTPTS,"
          f"afade=t=out:st={max(0,dur-0.25):.4f}:d=0.25[a]")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",silent,"-i",music,"-filter_complex",fc,"-map","[v]","-map","[a]",
        "-c:v","libx264","-crf","18","-preset","slow","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",out],check=True)
    print(f"-> {out}  ({dur:.3f}s)")
    return out

if __name__ == "__main__":
    a = sys.argv[2] if len(sys.argv)>2 else None
    assemble(sys.argv[1], a)
