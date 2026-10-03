#!/usr/bin/env python3
"""Find the "Destroy it all" entry point and the bar grid of the song.

The track is half-time phonk at ~86.85 BPM. Every bar ends in a short full-band
silence followed by a big hit; those hits are the hard cut points of the edit.

usage: python3 analyze_song.py media/audio/song.wav
"""
import sys
import numpy as np
import librosa

path = sys.argv[1] if len(sys.argv) > 1 else "media/audio/song.wav"
y, sr = librosa.load(path, sr=44100, mono=True)

# 1) lyrics with word timestamps (optional: needs faster-whisper)
try:
    from faster_whisper import WhisperModel
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path, word_timestamps=True, language="en")
    for s in segs:
        print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
except ImportError:
    print("faster-whisper not installed – skipping lyric timestamps")

# 2) silence gaps (>40 dB below peak) -> the hit right after each gap
hop = 220  # 5 ms
rms = librosa.feature.rms(y=y, frame_length=882, hop_length=hop)[0]
db = 20 * np.log10(rms + 1e-9)
t = np.arange(len(rms)) * hop / sr
quiet = db < db.max() - 40
gaps, start = [], None
for i, q in enumerate(quiet):
    if q and start is None:
        start = i
    elif not q and start is not None:
        if (i - start) * hop / sr > 0.03:
            gaps.append((t[start], t[i]))
        start = None
print("\nsilence gaps (start -> hit):")
for a, b in gaps:
    print(f"  {a:7.3f} -> {b:7.3f}")

# 3) beat period from onset autocorrelation
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
te = librosa.times_like(env, sr=sr, hop_length=512)
m = (te > 3) & (te < 46)
e = env[m] - env[m].mean()
ac = np.correlate(e, e, "full")[len(e) - 1:]
lags = np.arange(len(ac)) * 512 / sr
win = (lags > 2.6) & (lags < 2.9)
bar = lags[np.argmax(ac * win)]
print(f"\nbar length ≈ {bar:.4f}s  ->  {4 * 60 / bar:.2f} BPM (4 beats/bar)")
