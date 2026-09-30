"""Cut the song on the grid, mux it under the rendered picture, encode to size.

A size budget is hit with bitrate, not CRF: two passes on the target.

    python3 build/deliver.py [--mb 60] [--video out/edit_video.mp4]
"""
import argparse
import json
import subprocess
from pathlib import Path

import edl
import render

AUDIO_KBPS = 256


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mb", type=float, default=60.0)
    ap.add_argument("--video", default=str(render.OUT / "edit_video.mp4"))
    ap.add_argument("--song", default=str(render.MEDIA / "blame.mp3"))
    ap.add_argument("--out", default=str(render.OUT / "ronaldo_nani_blame.mp4"))
    a = ap.parse_args()

    t0 = render.tb(edl.B0)
    dur = render.fb(edl.B_END) / render.FPS  # exactly the picture length
    fade = 4 * render.PER
    wav = render.OUT / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", a.song,
                    "-af", f"afade=t=in:d=0.01,afade=t=out:st={dur - fade:.4f}:d={fade:.4f}",
                    "-ar", "48000", str(wav)], check=True)

    vk = int((a.mb * 8 * 1024 * 0.97) / dur - AUDIO_KBPS)
    common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.8)}k",
              "-bufsize", f"{vk * 2}k", "-pix_fmt", "yuv420p", "-profile:v", "high", "-g", "100"]
    log = str(render.OUT / "x264pass")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, *common, "-pass", "1",
                    "-passlogfile", log, "-an", "-f", "mp4", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", str(wav), *common, "-pass", "2",
                    "-passlogfile", log, "-c:a", "aac", "-b:a", f"{AUDIO_KBPS}k", "-shortest",
                    "-movflags", "+faststart", a.out], check=True)

    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-show_entries",
         "stream=codec_type,width,height,r_frame_rate", "-of", "json", a.out],
        capture_output=True, text=True, check=True).stdout)
    size = int(info["format"]["size"])
    print(f"{a.out}: {size / 1048576:.1f} MB, {float(info['format']['duration']):.2f} s, "
          f"video {vk} kbit/s, song {t0:.3f}-{t0 + dur:.3f} s (beats {edl.B0}-{edl.B_END})")


if __name__ == "__main__":
    main()
