#!/usr/bin/env python3
"""Qualitaetskontrolle: mittlere Helligkeit je Shot -- findet schwarze
oder abgesoffene Einstellungen."""
import subprocess, json, sys, os, glob, re
PROJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edl=json.load(open(sys.argv[1])); name=sys.argv[2]
import sys as _s; _s.path.insert(0,os.path.join(PROJ,"build"))
from looks import band_rect
def luma(p, band="wide", y=None, x=None):
    bx,by,bw,bh = band_rect(band,y,x)
    r=subprocess.run(["ffmpeg","-hide_banner","-i",p,"-vf",
        f"crop={bw}:{bh}:{bx}:{by},signalstats,metadata=print:key=lavfi.signalstats.YAVG",
        "-f","null","-"],capture_output=True,text=True).stderr
    v=[float(m) for m in re.findall(r"YAVG=([\d.]+)",r)]
    return (sum(v)/len(v) if v else 0.0, min(v) if v else 0, max(v) if v else 0)
print(f"{'#':>3} {'YAVG':>6} {'min':>6} {'max':>6}  band      quelle            note")
bad=[]
for i,s in enumerate(edl["shots"]):
    p=os.path.join(PROJ,"build","shots",f"{name}_{i:03d}.mp4")
    if not os.path.exists(p): continue
    a,lo,hi=luma(p, s.get('band','wide'), s.get('y'), s.get('x'))
    flag="  <<< ZU DUNKEL" if a<28 else ("  < dunkel" if a<42 else "")
    if a<28: bad.append(i)
    print(f"{i:3d} {a:6.1f} {lo:6.1f} {hi:6.1f}  {s.get('band','?'):9s} "
          f"{str(s.get('src'))[:16]:16s}  {s.get('note','')[:34]}{flag}")
print("\nzu dunkel:",bad)
