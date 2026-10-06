"""Prepare every media file the HyperFrames composition and the sound mix need.

Footage   NASA film HQ-194 "Eagle Has Landed: The Flight of Apollo 11" (1969) is a
          telecined 16 mm transfer (720x486, interlaced, 6:5 pixels). It is inverse-
          telecined back to its original progressive film frames, converted to square
          pixels, cleaned, cropped and upscaled per shot, with speed changes baked in.
Photos    Hasselblad scans from the NASA Image Library, cropped to 9:16 with headroom
          for the camera moves done in HTML.
Audio     The original air-to-ground loop cut word-exact (timestamps measured with
          faster-whisper medium.en, see README) plus NASA's clean audio releases.

    python3 prep.py
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "assets"
HF = ROOT / "hf" / "assets"
AUD = ROOT / "build" / "audio"

HQ = SRC / "nasa" / "hq194.mp4"          # 720x486 TFF, telecined film
MOCR = SRC / "nasa" / "broll_mocr.mp4"   # B-roll excerpt from 1255 s, 1280x720 pillarboxed 4:3

# inverse telecine → progressive 23.976 film frames → square pixels (864x486)
IVTC = "fieldmatch=order=tff:combmatch=full,yadif=deint=interlaced,decimate,scale=864:486:flags=lanczos,setsar=1"
CLEAN = "hqdn3d=1.5:1.2:4:3"
SHARP = "unsharp=5:5:0.55:5:5:0.0"


def run(cmd):
    subprocess.run(cmd, check=True)


def footage(name, src, t0, t1, speed, crop, size, pre=IVTC, extra=""):
    """Cut [t0,t1] from src, play it at `speed`, crop (w,h,x,y in the square-pixel
    frame) and scale to `size` (w,h). Output is an all-intra friendly H.264 file."""
    w, h, x, y = crop
    W, H = size
    pre_roll = min(1.0, t0)
    vf = ",".join(f for f in [
        pre, f"trim=start={pre_roll:.3f}:duration={t1 - t0:.3f}", "setpts=PTS-STARTPTS",
        CLEAN, f"crop={w}:{h}:{x}:{y}", f"scale={W}:{H}:flags=lanczos", SHARP,
        f"setpts=PTS/{speed}", "fps=30", extra, "format=yuv420p"] if f)
    out = HF / f"{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0 - pre_roll:.3f}", "-i", str(src),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
         "-g", "15", "-bf", "0", str(out)])
    return out


def photo(name, src, cx, cy, w_frac, out_w, out_h):
    """9:16 crop centred at (cx, cy) (0..1), `w_frac` = crop width / image width."""
    im = Image.open(SRC / "nasa" / src).convert("RGB")
    W, H = im.size
    cw = W * w_frac
    ch = cw * out_h / out_w
    if ch > H:
        ch = H
        cw = ch * out_w / out_h
    x0 = min(max(0, cx * W - cw / 2), W - cw)
    y0 = min(max(0, cy * H - ch / 2), H - ch)
    im = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
    im = im.resize((out_w, out_h), Image.LANCZOS)
    im.save(HF / f"{name}.jpg", quality=92, subsampling=0)


def audio(name, src, t0, t1, fade=0.012):
    AUD.mkdir(parents=True, exist_ok=True)
    d = t1 - t0
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", str(src), "-t", f"{d:.3f}",
         "-af", f"afade=t=in:d={fade},afade=t=out:st={d - fade:.3f}:d={fade}",
         "-ac", "2", "-ar", "44100", "-c:a", "pcm_f32le", str(AUD / f"{name}.wav")])


def main():
    HF.mkdir(parents=True, exist_ok=True)

    # --- footage -------------------------------------------------------------
    # descent through Aldrin's window (16 mm DAC, shot at 6 fps)
    footage("desc_alarm", HQ, 742.0, 755.0, 4.7, (648, 486, 108, 0), (960, 720))
    footage("desc_boulders", HQ, 765.0, 772.0, 2.8, (486, 486, 189, 0), (1080, 1080))
    footage("desc_fuel_a", HQ, 778.0, 790.0, 6.0, (486, 486, 189, 0), (1080, 1080))
    footage("desc_fuel_b", HQ, 790.0, 795.2, 2.5, (486, 486, 189, 0), (1080, 1080))
    footage("desc_contact", HQ, 795.2, 797.4, 1.0, (486, 486, 189, 0), (1080, 1080))
    # crew in the command module (montage flash)
    footage("crew", HQ, 482.6, 483.6, 2.0, (486, 486, 160, 0), (1080, 1080))
    # Mission Control (B-roll, pillarboxed 4:3 inside 1280x720)
    mocr_pre = "setsar=1"
    footage("mocr_wide", MOCR, 20.4, 21.4, 2.0, (960, 720, 160, 0), (1080, 810), pre=mocr_pre)
    footage("mocr_faces", MOCR, 24.0, 25.6, 1.0, (720, 720, 280, 0), (1080, 1080), pre=mocr_pre)

    # --- photos (9:16 with ~25 % headroom for camera moves) ---------------------
    photo("p_landing", "as11-37-5437.jpg", 0.42, 0.62, 0.56, 1350, 2400)
    photo("p_launch", "6901000.jpg", 0.47, 0.50, 0.62, 1350, 2400)
    photo("p_earth", "as11-44-6552.jpg", 0.50, 0.50, 0.56, 1350, 2400)
    photo("p_lm", "as11-44-6642.jpg", 0.43, 0.55, 0.54, 1350, 2400)
    photo("p_aldrin", "as11-40-5903.jpg", 0.46, 0.50, 0.55, 2160, 3840)
    photo("p_boot", "as11-40-5878.jpg", 0.55, 0.62, 0.50, 1350, 2400)

    # --- real air-to-ground audio (film timecodes, faster-whisper medium.en) ----
    audio("a_1202", HQ, 714.92, 716.42)          # "...1202 program alarm."
    audio("a_goland", HQ, 727.60, 728.52)        # "You're go for landing."
    audio("a_1201", HQ, 747.80, 748.46)          # "1201."
    audio("a_sametype", HQ, 752.90, 754.72)      # "We're go. Same type. We're go."
    audio("a_200ft", HQ, 763.20, 764.66)         # "Coming down nicely, two hundred feet."
    audio("a_60", HQ, 768.08, 769.06)            # "Sixty seconds."
    audio("a_dust", HQ, 785.56, 786.42)          # "Picking up some dust."
    audio("a_contact", HQ, 796.26, 797.70)       # "Contact light."
    audio("a_stop", HQ, 798.04, 798.92)          # "Okay, engine stop."
    nasa = SRC / "nasa"
    audio("a_landed", nasa / "569462main_eagle_has_landed.mp3", 0.80, 4.90)  # "Houston, Tranquility Base here..."
    audio("a_blue", nasa / "590333main_ringtone_eagleHasLanded_extended.mp3", 9.92, 12.72)  # "...turn blue. We're breathing again."
    audio("quindar", nasa / "578628main_hskquindar.mp3", 0.0, 24.4, fade=0.002)
    print("prep done")


if __name__ == "__main__":
    main()
