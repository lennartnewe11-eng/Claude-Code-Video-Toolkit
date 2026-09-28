#!/usr/bin/env python3
"""Beat-Map des Songs.

Der Track startet bei 161,5 BPM, zieht aber über die Laufzeit auf ~168 BPM an
(gemessen per Autokorrelation in 16-s-Fenstern). Ein starres 0,3715-s-Raster
läge nach einer Minute mehrere Beats daneben. Deshalb: Beat-Tracking mit
zeitvariablem Tempo, jeder Beat bekommt seine eigene absolute Zeit.

Index-Konvention: beats[n], n = 0 ist der erste Beat, bei dem n % 4 == 0 auf
die Takt-Eins fällt (Drop n=32, Refrain n=256 / n=512).

    python3 beatmap.py media/audio/song.mp3 build/beatmap.json
"""
import json
import sys

import librosa
import numpy as np
from scipy.ndimage import median_filter


def tempo_curve(y, sr, hop=64, win=16.0, step=4.0):
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop))
    b = np.log1p(S.sum(0) * 10)
    env = np.maximum(0, np.diff(b, prepend=b[0]))
    t = np.arange(len(env)) * hop / sr
    dt = t[1]
    rows = []
    for w in np.arange(12, t[-1] - win, step):
        m = (t >= w) & (t < w + win)
        x = env[m] - env[m].mean()
        ac = np.correlate(x, x, 'full')[len(x) - 1:]
        lags = np.arange(len(ac)) * dt
        est = []
        for n in (4, 8):
            mm = (lags > n * 0.34) & (lags < n * 0.38)
            j = np.where(mm)[0][np.argmax(ac[mm])]
            a, c0, c = ac[j - 1], ac[j], ac[j + 1]
            est.append((lags[j] + 0.5 * (a - c) / (a - 2 * c0 + c) * dt) / n)
        rows.append((w + win / 2, float(np.median(est))))
    return np.array(rows)


def main(song, out):
    y, sr = librosa.load(song, sr=22050, mono=True)
    tc = tempo_curve(y, sr)
    per = median_filter(tc[:, 1], 5)
    tt = np.concatenate([[0], tc[:, 0], [len(y) / sr]])
    pp = np.concatenate([[0.3715], per, [per[-1]]])
    hop = 128
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    te = librosa.times_like(env, sr=sr, hop_length=hop)
    bpm = 60 / np.interp(te, tt, pp)
    _, beats = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop, bpm=bpm,
                                       tightness=400, units='time', trim=False)
    beats = np.asarray(beats)
    # Takt-Eins: der Sub-Bass setzt am Drop einen Beat nach Tracker-Index 32 ein
    # (Energie je Beat nachgemessen), also Index um 1 verschieben.
    beats = beats[1:]
    res = []
    for i in range(4, len(beats) - 4):
        k = np.arange(-4, 5)
        p = np.polyfit(k, beats[i - 4:i + 5], 1)
        res.append(beats[i] - np.polyval(p, 0))
    res = np.array(res) * 1000
    info = {
        'song': song, 'n_beats': int(len(beats)),
        'jitter_ms_std': round(float(res[20:].std()), 2),
        'bpm_start': round(60 / float(np.median(np.diff(beats[32:64]))), 2),
        'bpm_end': round(60 / float(np.median(np.diff(beats[560:620]))), 2),
        'duration': round(len(y) / sr, 3),
    }
    json.dump({'info': info, 'beats': [round(float(b), 5) for b in beats]}, open(out, 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
