#!/usr/bin/env python3
"""Kontaktbogen -> Shots finden.
Zeit eines Kachelbildes:  t = start + (row*cols + col) * every   (0-indiziert)
"""
import subprocess, sys, math
src, out, every, cols = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
start = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
end   = float(sys.argv[6]) if len(sys.argv) > 6 else None
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
       "-of","csv=p=0",src],capture_output=True,text=True).stdout.strip())
if end: dur = min(dur, end)
n = int((dur - start) / every)
rows = max(1, math.ceil(n / cols))
vf = (f"fps=1/{every},scale=232:174:force_original_aspect_ratio=decrease,"
      f"pad=236:178:(ow-iw)/2:(oh-ih)/2:0x202020,"
      f"tile={cols}x{rows}:margin=2:padding=2:color=0x404040")
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(start),"-i",src,
                "-vf",vf,"-frames:v","1","-q:v","4",out],check=True)
print(f"{out}\n  n={n} grid={cols}x{rows} start={start}s every={every}s "
      f"-> t = {start} + (row*{cols}+col)*{every}")
