"""Beat grid for the track, measured rather than assumed.

Fits period and phase against the kick-drum onset envelope (energy below 150 Hz)
and writes grid.json. Every cut boundary in the edit is derived from this:
t(beat) = offset + beat * period, rounded to a frame per boundary, never summed.

    python3 build/grid.py media/blame.mp3
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

HOP = 128


def kick_envelope(y, sr):
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    return np.maximum(0, np.diff(np.log1p(S[f < 150].sum(0))))


def main(path):
    y, sr = librosa.load(path, sr=44100, mono=True)
    kick = kick_envelope(y, sr)
    tt = np.arange(len(kick)) * HOP / sr

    # coarse: librosa's tracker, then a least-squares line through its beats
    _, beats = librosa.beat.beat_track(y=y, sr=sr, tightness=400, units="time")
    idx = np.arange(len(beats))
    per0, off0 = np.linalg.lstsq(np.vstack([idx, np.ones_like(idx)]).T, beats, rcond=None)[0]

    # fine: maximise kick energy on the grid (tracker beats sit ~40 ms late)
    best = (-1, per0, off0)
    for per in np.linspace(per0 - 0.0008, per0 + 0.0008, 161):
        for off in np.linspace(off0 - 0.06, off0 + 0.02, 161):
            t = off + np.arange(80, 432) * per
            s = np.interp(t, tt, kick).sum()
            if s > best[0]:
                best = (s, per, off)
    _, per, off = best

    # how far the real kicks stray from the grid inside the drops
    dev = []
    for b in list(range(120, 152)) + list(range(256, 288)) + list(range(368, 432)):
        t = off + b * per
        m = (tt > t - 0.04) & (tt < t + 0.04)
        dev.append(tt[m][np.argmax(kick[m])] - t)
    dev = np.array(dev) * 1000

    out = {
        "source": Path(path).name,
        "duration": len(y) / sr,
        "period": round(float(per), 6),
        "bpm": round(60 / float(per), 3),
        "offset": round(float(off), 4),
        "kick_dev_ms": {"mean": round(float(dev.mean()), 1), "std": round(float(dev.std()), 1)},
        # measured from RMS/low-band energy per bar, see README
        "sections": {
            "build_2": [248, 256],
            "drop_2": [256, 288],
            "breakdown": [288, 352],
            "build_3": [352, 368],
            "drop_3": [368, 432],
            "outro": [432, 441],
        },
    }
    Path(__file__).with_name("grid.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "media/blame.mp3")
