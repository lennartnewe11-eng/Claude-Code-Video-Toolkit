#!/usr/bin/env python3
"""Beat grid + lyric timestamps for "Alors on danse".

Fits the beat period on the onset envelope, then snaps the grid to the kick drum
(the onset envelope sits ~22 ms late). Prints where each "danse" lands.

usage: python3 analyze_song.py media/audio/song.wav
"""
import sys
import numpy as np
import librosa

path = sys.argv[1] if len(sys.argv) > 1 else "media/audio/song.wav"
y, sr = librosa.load(path, sr=22050, mono=True)

try:
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path, word_timestamps=True, language="fr", clip_timestamps=[54, 92])
    for s in segs:
        for w in s.words:
            if "dans" in w.word.lower():
                print(f"  'danse' {w.start:7.2f}")
except ImportError:
    print("faster-whisper not installed – skipping lyric timestamps")

hop = 128
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
t = librosa.times_like(env, sr=sr, hop_length=hop)
best = None
for P in np.arange(0.40, 0.60, 0.0002):
    for ph in np.arange(0, P, 0.004):
        s = env[np.searchsorted(t, np.arange(55 + ph, 100, P))].sum()
        if best is None or s > best[0]:
            best = (s, P, ph)
P, anchor = best[1], 55 + best[2]

# snap to kick drum (30-150 Hz rising edge)
S = np.abs(librosa.stft(y, hop_length=64, n_fft=2048))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
low = S[(f > 30) & (f < 150)].sum(0)
tl = np.arange(len(low)) * 64 / sr
rise = np.maximum(0, np.diff(low, prepend=low[0]))
offs = []
for k in range(13, 50):
    b = anchor + k * P
    m = (tl > b - 0.07) & (tl < b + 0.07)
    offs.append(tl[np.argmax(rise * m)] - b)
anchor += float(np.median(offs))
print(f"beat {P:.4f}s = {60 / P:.2f} BPM;  B(k) = {anchor:.4f} + {P:.4f}*k  (k=13 is the drop)")
