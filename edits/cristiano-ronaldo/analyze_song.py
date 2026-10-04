#!/usr/bin/env python3
"""Lyrics + beat grid + drum drop-outs for the song used in the Ronaldo edit.

Prints word timestamps (faster-whisper, German), the 135 BPM grid snapped to the
kick drum, and the per-beat kick/snare levels. A beat with no kick/snare is a
drop-out: the edit starts in one (a-cappella hook) and lands the SIU in another.

usage: python3 analyze_song.py media/audio/song.wav
"""
import sys
import numpy as np
import librosa

path = sys.argv[1] if len(sys.argv) > 1 else "media/audio/song.wav"
y, sr = librosa.load(path, sr=22050, mono=True)

try:
    from faster_whisper import WhisperModel
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path, word_timestamps=True, language="de", clip_timestamps=[29.5, 50.6])
    for s in segs:
        print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
except ImportError:
    print("faster-whisper not installed – skipping lyric timestamps")

hop = 128
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
t = librosa.times_like(env, sr=sr, hop_length=hop)
best = None
for P in np.arange(0.43, 0.46, 0.0001):
    for ph in np.arange(0, P, 0.003):
        s = env[np.searchsorted(t, np.arange(32 + ph, 57, P))].sum()
        if best is None or s > best[0]:
            best = (s, P, ph)
P, anchor = best[1], 32 + best[2]
print(f"\nbeat {P:.4f}s = {60 / P:.2f} BPM, grid anchor {anchor:.3f}s")

S = np.abs(librosa.stft(y, hop_length=64, n_fft=2048))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
low = S[(f > 25) & (f < 120)].sum(0); low /= np.percentile(low, 99)
snr = S[(f > 1500) & (f < 5000)].sum(0); snr /= np.percentile(snr, 99)
lt = np.arange(len(low)) * 64 / sr
for k in range(-6, 43):
    b = anchor + k * P
    j = np.searchsorted(lt, b)
    lo, sn = low[j:j + 8].max(), snr[j:j + 8].max()
    tag = "  <- drop-out" if lo < 0.05 and sn < 0.6 else ""
    print(f"k={k:3d} {b:7.3f}s kick={lo:.2f} snare={sn:.2f}{tag}")
