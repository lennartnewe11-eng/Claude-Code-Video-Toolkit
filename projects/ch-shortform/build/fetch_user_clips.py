#!/usr/bin/env python3
"""Schneidet die einzelnen Szenen aus den hochgeladenen Bildschirmmitschnitten
heraus und entfernt dabei die Instagram-Oberflaeche."""
import os, subprocess, glob, sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP   = "/root/.claude/uploads/fbc32e5c-a9f9-58cd-90f3-b3c31c377e20"
DST  = os.path.join(PROJ, "assets", "stock")

# key, Dateipraefix, Beschnitt (b:h:x:y), Startzeit, Dauer, Beschreibung
CLIPS = [
    ("u_klippe",     "18840465", "886:800:0:692",  0.6, 2.6, "Klippe, Person am Handy"),
    ("u_strasse",    "18840465", "886:800:0:692",  4.2, 2.4, "Strasse, Mann am Handy, Kind hinterher"),
    ("u_liegend",    "18840465", "886:800:0:692",  6.9, 1.8, "Frau liegend am Handy"),
    ("u_friseur",    "21fafb3d", "880:772:3:8",    0.4, 2.0, "Friseur, Kunde am Handy"),
    ("u_warten",     "21fafb3d", "880:772:3:8",    3.2, 2.4, "Wartezimmer, Aguarde ser atendido"),
    ("u_pissoir",    "21fafb3d", "880:772:3:8",    6.4, 2.4, "Pissoir, Mann am Handy"),
    ("u_spielplatz", "04443243", "880:772:3:8",    0.5, 2.8, "Kinder auf der Bank, leerer Spielplatz"),
    ("u_strassennacht","04443243","880:772:3:8",   4.6, 2.6, "Strassenszene nachts"),
]

def main():
    os.makedirs(DST, exist_ok=True)
    for key, pref, crop, ss, dur, note in CLIPS:
        src = glob.glob(f"{UP}/{pref}*.mov")
        if not src:
            print(f"  [fehlt] {key}"); continue
        out = os.path.join(DST, key + ".mp4")
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
            "-ss",f"{ss}","-i",src[0],"-t",f"{dur}",
            "-vf",f"crop={crop}",
            "-c:v","libx264","-crf","15","-preset","medium","-pix_fmt","yuv420p",
            "-an",out],check=True)
        w = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
            "-show_entries","stream=width,height","-of","csv=p=0",out],
            capture_output=True,text=True).stdout.strip()
        print(f"  {key:18s} {w:10s} {dur:.1f}s  {note}")

if __name__ == "__main__":
    main()
