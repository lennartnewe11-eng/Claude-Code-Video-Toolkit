#!/usr/bin/env python3
"""Beat-Map des Özil-Songs.

Nachgemessen (Onset-Fit je Strophe): das Tempo ist konstant, 162,00 BPM
(0,37037 s) in allen drei Strophen, gerappt wird auf halber Zeit (81 BPM,
eine Zeile = 8 Beats = 2,96 s). Also ein starres Raster: Periode und Phase
per Least-Squares an die stärksten Onsets gefittet (Jitter ~11 ms).

Beat 0 ist der erste Rasterpunkt des Songs. Die Abschnitte liegen dann alle
auf Vielfachen von 8 (Bass setzt bei Beat 48, 144 und 240 ein, siehe
timeline.py); build() prüft das an der Bassenergie.

    python3 beatmap.py media/audio/song.mp3 build/beatmap.json
"""
import json
import sys

import librosa
import numpy as np

P0 = 0.37037
VERSES = (48, 144, 240)          # Bass-Einsätze der drei Strophen (Song-Beats)


def main(song, out):
    y, sr = librosa.load(song, sr=22050, mono=True)
    hop = 64
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    t = librosa.times_like(env, sr=sr, hop_length=hop)
    P = P0
    best = None
    for ph in np.arange(0, P, 0.002):
        tt = ph + np.arange(int((t[-1] - ph) / P)) * P
        v = np.interp(tt, t, env).sum()
        if best is None or v > best[0]:
            best = (v, ph)
    ph = best[1]
    for _ in range(3):
        n = np.arange(int((t[-1] - ph) / P))
        pk, kk = [], []
        for k, x in zip(n, ph + n * P):
            m = (t > x - 0.035) & (t < x + 0.035)
            if m.any() and env[m].max() > np.percentile(env, 90):
                pk.append(t[m][np.argmax(env[m])])
                kk.append(k)
        P, ph = np.polyfit(kk, pk, 1)
    res = (np.array(pk) - (np.array(kk) * P + ph)) * 1000
    ph = ph % P
    beats = ph + np.arange(int((len(y) / sr - ph) / P)) * P
    # Kontrolle: Bass (30-120 Hz) im Takt vor und nach jedem Strophen-Einsatz
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    lo = S[(f > 30) & (f < 120)].sum(0)
    ts = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=512)

    def bass(a, b):
        return float(lo[(ts >= beats[a]) & (ts < beats[b])].mean())
    check = {v: [round(bass(v - 8, v), 1), round(bass(v, v + 8), 1)] for v in VERSES}
    for v, (before, after) in check.items():
        assert after > 3 * before, f'Bass-Einsatz nicht auf Beat {v}: {before} -> {after}'
    info = dict(song=song, bpm=round(60 / P, 3), period=round(float(P), 6), n_beats=len(beats),
                jitter_ms_std=round(float(res.std()), 2), bass_before_after=check,
                duration=round(len(y) / sr, 3))
    json.dump({'info': info, 'beats': [round(float(b), 5) for b in beats]}, open(out, 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
