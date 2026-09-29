#!/usr/bin/env python3
"""Beat-Map des Neymar-Songs.

Nachgemessen (Autokorrelation, 16-s-Fenster über den ganzen Song): das Tempo
ist konstant, 127,88 BPM (0,4692 s), Streuung der Fensterwerte < 0,1 %. Also
ein starres Raster: Periode und Phase per Least-Squares an die stärksten
Onsets gefittet, Beat 0 auf die erste Takt-Eins gelegt (Takt-Eins = die
Phase mit der meisten Kick-/Sub-Energie über den ganzen Song).

    python3 beatmap.py media/audio/song.mp3 build/beatmap.json
"""
import json
import sys

import librosa
import numpy as np


def main(song, out):
    y, sr = librosa.load(song, sr=22050, mono=True)
    hop = 64
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    t = librosa.times_like(env, sr=sr, hop_length=hop)
    # grobe Phase bei P0, dann Feinfit über lokale Onset-Maxima
    P = 0.46920
    best = None
    for ph in np.arange(0, P, 0.002):
        tt = ph + np.arange(int((t[-1] - ph) / P)) * P
        v = np.interp(tt, t, env).sum()
        if best is None or v > best[0]:
            best = (v, ph)
    ph = best[1]
    for _ in range(3):
        n = np.arange(int((t[-1] - ph) / P))
        tt = ph + n * P
        pk, kk = [], []
        for k, x in zip(n, tt):
            m = (t > x - 0.04) & (t < x + 0.04)
            if not m.any():
                continue
            i = np.argmax(env[m])
            if env[m][i] > np.percentile(env, 80):
                pk.append(t[m][i]); kk.append(k)
        P, ph = np.polyfit(kk, pk, 1)
    res = (np.array(pk) - (np.array(kk) * P + ph)) * 1000
    # Takt-Eins: Sub+Kick je Beat-Phase
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=256))
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    lo = S[f < 150].sum(0)
    tl = librosa.times_like(lo, sr=sr, hop_length=256)
    beats = ph + np.arange(int((len(y) / sr - ph) / P)) * P
    e = np.array([lo[(tl >= b) & (tl < b + 0.12)].mean() if b + 0.12 < tl[-1] else 0 for b in beats])
    phase_e = [e[p::4].mean() for p in range(4)]
    one = int(np.argmax(phase_e))
    beats = beats[one:]
    info = dict(song=song, bpm=round(60 / P, 3), period=round(P, 6), n_beats=len(beats),
                jitter_ms_std=round(float(res.std()), 2), downbeat_phase_energy=[round(float(x), 1) for x in phase_e],
                duration=round(len(y) / sr, 3))
    json.dump({'info': info, 'beats': [round(float(b), 5) for b in beats]}, open(out, 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
