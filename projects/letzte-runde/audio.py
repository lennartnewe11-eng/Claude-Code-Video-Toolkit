"""Sound mix for "LETZTE RUNDE": music cut + SFX + loudness normalisation.

    python3 audio.py   → output/mix.wav  (44.1 kHz stereo, -14 LUFS, -1 dBTP)
"""
from __future__ import annotations

import json
import subprocess
from functools import lru_cache

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

import edl
from engine import ASSETS, ROOT

SR = 44100
OUT = ROOT / "output"


def decode(path, start=0.0, duration=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.4f}", "-i", str(path)]
    if duration:
        cmd += ["-t", f"{duration:.4f}"]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.check_output(cmd), np.float32).reshape(-1, 2).copy()


@lru_cache(maxsize=None)
def sfx(name):
    return decode(ASSETS / "sfx" / name)


def db(g):
    return 10 ** (g / 20)


def envelope(x, win=256):
    m = np.abs(x).max(axis=1)
    k = np.ones(win) / win
    return np.convolve(m, k, mode="same")


def transient(x, mode="onset"):
    env = envelope(x)
    if mode == "peak":
        return int(np.argmax(env))
    return int(np.argmax(env > 0.3 * env.max()))


def fade(x, fin=0.0, fout=0.0):
    n = len(x)
    if fin > 0:
        k = min(n, int(fin * SR))
        x[:k] *= np.linspace(0, 1, k)[:, None]
    if fout > 0:
        k = min(n, int(fout * SR))
        x[n - k:] *= np.linspace(1, 0, k)[:, None]
    return x


def ring_bell(strikes=(0.0, 0.17, 0.34)):
    """Boxing ring bell: inharmonic metal partials, three quick strikes."""
    dur = 1.6
    t = np.arange(int(dur * SR)) / SR
    partials = [(1.0, 1.0, 1.1), (2.76, 0.55, 0.7), (5.40, 0.30, 0.45), (8.93, 0.18, 0.3), (1.5, 0.25, 0.9)]
    f0 = 1180.0
    one = np.zeros_like(t)
    for ratio, amp, dec in partials:
        one += amp * np.sin(2 * np.pi * f0 * ratio * t + ratio) * np.exp(-t / dec)
    one *= 1 - np.exp(-t / 0.002)          # 2 ms strike
    one /= np.abs(one).max()
    out = np.zeros(int((strikes[-1] + dur) * SR))
    for s in strikes:
        i = int(s * SR)
        out[i:i + len(one)] += one
    out /= np.abs(out).max()
    return np.stack([out, out * 0.96], 1).astype(np.float32)


def place(bus, clip, at_sample):
    a = max(0, at_sample)
    skip = a - at_sample
    n = min(len(bus) - a, len(clip) - skip)
    if n > 0:
        bus[a:a + n] += clip[skip:skip + n]


def lowpass(x, cutoff):
    sos = butter(4, cutoff, btype="low", fs=SR, output="sos")
    return sosfiltfilt(sos, x, axis=0).astype(np.float32)


def build():
    n = int(edl.DURATION * SR)
    m = edl.MUSIC
    music = decode(ASSETS / "music" / m["file"], m["start"], m["duration"])[:n]
    music = np.pad(music, ((0, n - len(music)), (0, 0)))

    # flashback: music sounds like a memory (low-passed), crossfaded in and out
    mf = edl.MEMORY_FILTER
    lp = lowpass(music, mf["cutoff"])
    w = np.zeros(n, np.float32)
    i0, i1, xf = int(mf["t0"] * SR), int(mf["t1"] * SR), int(0.04 * SR)
    w[i0:i1] = mf["wet"]
    w[i0:i0 + xf] *= np.linspace(0, 1, xf)
    w[i1 - xf:i1] *= np.linspace(1, 0, xf)
    music = music * (1 - w[:, None]) + lp * w[:, None] * 1.25

    bus = music.copy()

    # crowd bed under the fight, gone before the silence
    cb = edl.CROWD_BED
    crowd = decode(ASSETS / "sfx" / cb["file"], cb["offset"], cb["end"] - cb["start"])
    crowd = fade(lowpass(crowd, 5000) * db(cb["gain"]), 0.3, 0.25)
    place(bus, crowd, int(cb["start"] * SR))

    for at, name, gain, opt in edl.SFX:
        clip = ring_bell() if name == "bell" else sfx(name).copy()
        if "dur" in opt:
            clip = fade(clip[: int(opt["dur"] * SR)], 0, 0.08)
        if "end" in opt:
            clip = clip[: max(0, int((opt["end"] - at) * SR))]
        clip = fade(clip, opt.get("fade_in", 0.0), opt.get("fade_out", 0.006))
        off = 0 if name == "bell" else transient(clip, opt.get("align", "onset"))
        place(bus, clip * db(gain), int(at * SR) - off)

    # hard silence where the track drops out (only heartbeat + breath remain)
    # and click-free loop points
    bus = fade(bus, 0.004, 0.004)
    return bus


def loudnorm(src, dst, target=-14.0, tp=-1.0):
    af1 = f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", af1, "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):])
    af2 = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
           f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:"
           f"offset={js['target_offset']}:linear=true:print_format=json")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(src), "-af", af2 + ",aresample=44100",
                        "-c:a", "pcm_s16le", str(dst)], capture_output=True, text=True)
    out = json.loads(r.stderr[r.stderr.rfind("{"):])
    return js, out


def main():
    OUT.mkdir(exist_ok=True)
    bus = build()
    bus /= np.abs(bus).max()
    raw, lim = OUT / "mix_raw.wav", OUT / "mix_lim.wav"
    sf.write(raw, bus, SR, subtype="FLOAT")
    # look-ahead limiter tames the stacked KO transients, then linear loudnorm
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    "alimiter=limit=0.47:attack=4:release=90:level=false", "-c:a", "pcm_f32le", str(lim)],
                   check=True)
    pre, post = loudnorm(lim, OUT / "mix.wav")
    lim.unlink()
    print("measured:", pre["input_i"], "LUFS", pre["input_tp"], "dBTP")
    print("output  :", post["output_i"], "LUFS", post["output_tp"], "dBTP", post["normalization_type"])
    raw.unlink()


if __name__ == "__main__":
    main()
