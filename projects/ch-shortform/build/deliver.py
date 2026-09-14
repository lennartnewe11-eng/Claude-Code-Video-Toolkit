#!/usr/bin/env python3
"""Ansichtsfassungen fuer die Weitergabe.

Zwei Codecs, weil nicht jeder Browser H.264 kann: Chromium-Builds ohne
proprietaere Codecs (unter Linux verbreitet) spielen eine H.264-Datei gar
nicht ab. Der Browser nimmt per <source> automatisch, was er dekodieren kann.

720p ist der Standard: weniger als die halbe Pixelmenge, gut ein Drittel der
Groesse, und es laedt auch bei schmaler Leitung sofort.
"""
import os, subprocess, sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(PROJ, "out")

def run(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a], check=True)

def size(p):
    return os.path.getsize(p) / 1048576

def main(src=None):
    src = src or os.path.join(OUT, "act1.mp4")
    base = os.path.splitext(os.path.basename(src))[0]

    # 720p H.264 -- Main/Level 4.0 laeuft ueberall in Hardware
    mp4 = os.path.join(OUT, f"{base}_720.mp4")
    run("-i", src, "-vf", "fps=30,scale=720:1280:flags=lanczos",
        "-c:v", "libx264", "-crf", "25", "-preset", "slower",
        "-profile:v", "main", "-level", "4.0",
        "-maxrate", "1600k", "-bufsize", "3200k",
        "-g", "60", "-keyint_min", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "112k", "-ac", "2",
        "-movflags", "+faststart", mp4)

    # 720p VP9/Opus -- Ausweichquelle fuer Browser ohne H.264
    webm = os.path.join(OUT, f"{base}_720.webm")
    run("-i", src, "-vf", "fps=30,scale=720:1280:flags=lanczos",
        "-c:v", "libvpx-vp9", "-crf", "34", "-b:v", "0",
        "-speed", "3", "-row-mt", "1", "-tile-columns", "1",
        "-g", "60", "-pix_fmt", "yuv420p",
        "-c:a", "libopus", "-b:a", "96k", webm)

    # 1080p H.264 als Umschaltoption
    hi = os.path.join(OUT, f"{base}_web.mp4")
    run("-i", src, "-vf", "fps=30",
        "-c:v", "libx264", "-crf", "24", "-preset", "slower",
        "-profile:v", "high", "-level", "4.1",
        "-maxrate", "2300k", "-bufsize", "4600k",
        "-g", "60", "-keyint_min", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", hi)

    poster = os.path.join(OUT, f"{base}_poster.jpg")
    run("-ss", "1.2", "-i", src, "-frames:v", "1",
        "-vf", "scale=540:960", "-q:v", "4", poster)

    for p in (mp4, webm, hi, poster):
        print(f"  {os.path.basename(p):22s} {size(p):6.2f} MB")
    print("\nAlle Dateien bleiben unter 15 MB -- das ist das Limit pro Datei "
          "fuer Artifact-Anhaenge.")

if __name__ == "__main__":
    main(*sys.argv[1:])
