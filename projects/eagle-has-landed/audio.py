"""Sound mix for THE EAGLE HAS LANDED (21.0 s).

Real NASA air-to-ground audio carries the story; the music ducks under it.
  * tension bed  : Mixkit #464 "Sci-Fi Score" from 16.45 s (its hits land on the scene cuts
                   at 0.0 / 3.0 / 7.0 / 10.0 s), hard cut at 11.40 s when the fuel call hits 30
  * resolution   : Mixkit #587 "Discover" from 28.16 s, its swell (31.5 s) lands on
                   "The Eagle has landed" at 17.04 s
  * Quindar tones (2525 / 2475 Hz, 250 ms) frame every Houston transmission, as on the real loop

    python3 audio.py   → build/mix.wav  (44.1 kHz stereo, -14 LUFS, -1 dBTP)
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

ROOT = Path(__file__).resolve().parent
SR = 44100
DUR = 21.0
AUD = ROOT / "build" / "audio"


def decode(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.4f}", "-i", str(path)]
    if dur:
        cmd += ["-t", f"{dur:.4f}"]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.check_output(cmd), np.float32).reshape(-1, 2).copy()


def db(g):
    return 10 ** (g / 20)


def fade(x, fin=0.0, fout=0.0):
    n = len(x)
    if fin:
        k = min(n, int(fin * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fout:
        k = min(n, int(fout * SR)); x[n - k:] *= np.linspace(1, 0, k)[:, None]
    return x


def place(bus, clip, t):
    i = int(round(t * SR))
    a, skip = max(0, i), max(0, -i)
    n = min(len(bus) - a, len(clip) - skip)
    if n > 0:
        bus[a:a + n] += clip[skip:skip + n]


def bandpass(x, lo, hi, order=4):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfiltfilt(sos, x, axis=0).astype(np.float32)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def tone(freq, dur, amp=0.5, attack=0.004):
    t = np.arange(int(dur * SR)) / SR
    y = amp * np.sin(2 * np.pi * freq * t)
    env = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / attack)
    y = (y * env).astype(np.float32)
    return np.stack([y, y], 1)


def master_alarm():
    """Two-tone caution & warning chirp."""
    a = np.concatenate([tone(2000, 0.07, 0.45), tone(1400, 0.07, 0.45)])
    return a


def voice(name, gain_db=0.0, target=-20.0):
    """Load a dialogue clip, level it to a common RMS and add radio grit."""
    x, sr = sf.read(AUD / f"{name}.wav", dtype="float32")
    x = bandpass(x, 250, 3600, 2) * 0.85 + x * 0.15        # keep the comm-loop colour
    speech = x[np.abs(x).max(1) > 0.02]
    x = x * db(target - rms_db(speech if len(speech) else x))
    return x * db(gain_db)


def build():
    n = int(DUR * SR)
    bus = np.zeros((n, 2), np.float32)
    voc = np.zeros((n, 2), np.float32)
    ROOT_A = ROOT / "assets"

    # ---- dialogue (start time = clip start; word offsets measured in prep) ----
    lines = [
        ("a_1202", 0.10, 1.0), ("a_goland", 2.10, 0.0), ("a_1201", 3.08, 0.0), ("a_sametype", 4.62, 0.0),
        ("a_200ft", 6.30, -4.0), ("a_60", 8.40, 1.0), ("a_dust", 10.30, 0.0), ("a_contact", 12.40, 2.0),
        ("a_landed", 13.84, 2.5), ("a_blue", 17.89, 2.0),
    ]
    for name, t, g in lines:
        place(voc, voice(name, g, target=-19.0 if name in ("a_landed", "a_blue") else -21.0), t)
    # Quindar intro/outro around Houston transmissions
    for t_in, t_out in [(1.82, 2.95), (4.34, 6.48), (8.12, 9.42), (17.62, 20.75)]:
        place(voc, tone(2525, 0.25, 0.10), t_in)
        place(voc, tone(2475, 0.25, 0.10), t_out)

    # ---- music ----
    m1 = decode(ROOT_A / "music" / "464.mp3", 16.45, 11.40)
    m1 = fade(m1, 0.0, 0.03) * db(-3)
    # duck the tension bed under voices (sidechain-style envelope)
    env = np.abs(voc).max(1)
    k = int(0.12 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1 - 0.55 * np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    place(bus, m1 * duck[: len(m1), None], 0.0)

    m2 = decode(ROOT_A / "music" / "587.mp3", 28.16, DUR - 13.70)
    m2 = fade(m2, 0.6, 0.25) * db(-1)
    duck2 = 1 - 0.35 * np.clip(env[int(13.7 * SR):] / (env.max() + 1e-9) * 3, 0, 1)
    m2 = m2 * duck2[: len(m2), None]
    place(bus, m2, 13.70)

    # ---- sound design ----
    sfx = lambda f, g: decode(ROOT_A / "sfx" / f) * db(g)
    for t in (0.0, 0.43, 0.86, 1.29):
        place(bus, master_alarm(), t)
    place(bus, sfx("2299.mp3", -4), 0.0)                    # sub hit on frame 0
    place(bus, sfx("788.mp3", -9)[: int(1.6 * SR)], 0.0)
    for t in (1.79, 2.00, 2.20, 2.41, 2.62, 2.82):          # montage cuts
        place(bus, fade(sfx("1492.mp3", -16)[: int(0.35 * SR)], 0, 0.1), t - 0.06)
    place(bus, sfx("2299.mp3", -7), 3.02)
    place(bus, fade(sfx("1490.mp3", -14)[: int(0.6 * SR)], 0, 0.2), 5.72)
    place(bus, sfx("2299.mp3", -6), 7.03)
    place(bus, fade(sfx("1490.mp3", -14)[: int(0.6 * SR)], 0, 0.2), 8.24)
    for t, g in ((10.95, -15), (11.55, -11), (12.0, -10)):     # heartbeat into the silence
        place(bus, sfx("490.mp3", g), t)
    place(bus, sfx("498.mp3", -6), 12.45)                    # contact
    place(bus, fade(sfx("1143.mp3", -16), 0, 0.8)[: int(2.0 * SR)], 17.0)  # swell lift
    place(bus, fade(sfx("1492.mp3", -18)[: int(0.4 * SR)], 0, 0.1), 19.29)
    # comm-loop hiss under the descent
    rng = np.random.default_rng(3)
    hiss = bandpass(rng.normal(0, 1, (int(12.5 * SR), 2)).astype(np.float32), 400, 5000) * db(-46)
    place(bus, fade(hiss, 0.2, 0.3), 0.0)

    bus += voc
    return fade(bus, 0.003, 0.02)


def loudnorm(src, dst, target=-14.0, tp=-1.0):
    af = f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", af, "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):])
    af2 = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
           f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:"
           f"linear=true:print_format=json")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(src), "-af", af2 + ",aresample=44100",
                        "-c:a", "pcm_s16le", str(dst)], capture_output=True, text=True)
    return js, json.loads(r.stderr[r.stderr.rfind("{"):])


def main():
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    bus = build()
    bus /= np.abs(bus).max()
    raw, lim = out / "mix_raw.wav", out / "mix_lim.wav"
    sf.write(raw, bus, SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    "alimiter=limit=0.5:attack=4:release=80:level=false", "-c:a", "pcm_f32le", str(lim)], check=True)
    pre, post = loudnorm(lim, out / "mix.wav")
    print("measured:", pre["input_i"], "LUFS", pre["input_tp"], "dBTP")
    print("output  :", post["output_i"], "LUFS", post["output_tp"], "dBTP", post["normalization_type"])
    raw.unlink(); lim.unlink()


if __name__ == "__main__":
    main()
