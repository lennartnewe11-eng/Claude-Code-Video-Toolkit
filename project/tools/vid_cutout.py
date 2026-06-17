#!/usr/bin/env python3
"""Turn a video clip into an animated cut-out (transparent alpha WebM).

Pipeline: extract frames -> rembg per frame (one shared session) -> optional
B/W -> re-encode as VP9 WebM with alpha (yuva420p) for Remotion.

Usage:
  vid_cutout.py <in_video> <start_sec> <dur_sec> <out.webm> [--bw] [--width 1280]
"""
import sys, os, subprocess, tempfile
from rembg import remove, new_session
from PIL import Image, ImageOps

FFMPEG = os.path.join(os.path.dirname(__file__), "ffmpeg")


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    src, start, dur, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    bw = "--bw" in sys.argv
    width = 1280
    if "--width" in sys.argv:
        width = int(sys.argv[sys.argv.index("--width") + 1])

    tmp = tempfile.mkdtemp()
    raw, cut = os.path.join(tmp, "raw"), os.path.join(tmp, "cut")
    os.makedirs(raw); os.makedirs(cut)

    # 1) extract frames at 30fps
    run([FFMPEG, "-v", "error", "-ss", start, "-t", dur, "-i", src,
         "-vf", f"fps=30,scale={width}:-1", os.path.join(raw, "f%04d.png")])
    frames = sorted(os.listdir(raw))
    print(f"frames: {len(frames)}")

    # 2) per-frame background removal (shared u2net session)
    sess = new_session("u2net")
    for i, fn in enumerate(frames):
        im = Image.open(os.path.join(raw, fn)).convert("RGBA")
        o = remove(im, session=sess)
        if bw:
            g = ImageOps.autocontrast(ImageOps.grayscale(o.convert("RGB")), 1).convert("RGBA")
            g.putalpha(o.split()[3])
            o = g
        o.save(os.path.join(cut, fn))
        if i % 20 == 0:
            print(f"  cut {i}/{len(frames)}")

    # 3) encode VP9 with alpha
    run([FFMPEG, "-v", "error", "-framerate", "30", "-i", os.path.join(cut, "f%04d.png"),
         "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "3M",
         "-auto-alt-ref", "0", out, "-y"])
    print(f"saved {out} ({os.path.getsize(out)//1024} KB)")


if __name__ == "__main__":
    main()
