#!/usr/bin/env python3
"""Beat-Map für „Freaks“ (Surf Curse), Aufnahme des Auftraggebers.

Nachgemessen: Viertel bei ~89–90 BPM, das Tempo schwankt leicht (88,3–90,7 BPM in
16-Beat-Fenstern, Band ohne Klick). Geschnitten wird auf **Achteln** (~0,334 s):
die Gitarre schlägt Achtel, und ein Achtel ist so lang wie ein Beat im Messi-Song
(0,37 s) — Zweierschnitte, Einer-Trauben und Vierer-Pausen bleiben dieselben.

Vorgehen:
1. Viertel per Beat-Tracking mit zeitvariablem Tempo (Autokorrelation in 10-s-Fenstern).
2. Ränder reparieren: der Tracker springt in den ersten fünf Vierteln (Einschwingen)
   und in den letzten sechs (Ausklang); dort wird mit der lokalen Periode
   extrapoliert.
3. Achtel = Viertel + Mitten; jedes Achtel auf den nächsten starken Onset (±35 ms)
   gezogen, dann lokal linear geglättet (9 Punkte). Rest-Jitter ~8 ms.
4. Index 0 = erster Gitarrenanschlag = Takt-Eins (Akkord- und Basswechsel liegen
   je Takt auf Viertelphase 3 → 0, also auf den Achteln 0, 8, 16, …).

Abschnitte (Achtel-Index k, 8 Achtel = 1 Takt = 2,68 s), aus Text und Pegel:
    0– 56 Intro (Gitarre)          56–120 Strophe 1    120–176 Refrain 1
  176–240 Zwischenteil („My head is“) 240–296 Strophe 2  296–352 Refrain 2
  352–416 Outro (Gitarre)          416 letzter Anschlag

    python3 beatmap.py media/audio/song.mp3 build/beatmap.json
"""
import json
import sys

import librosa
import numpy as np
from scipy.ndimage import median_filter


def tempo_curve(y, sr, hop=64, win=10.0, step=2.0):
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop))
    b = np.log1p(S.sum(0) * 10)
    env = np.maximum(0, np.diff(b, prepend=b[0]))
    t = np.arange(len(env)) * hop / sr
    dt = t[1]
    rows = []
    for w in np.arange(2, t[-1] - win, step):
        m = (t >= w) & (t < w + win)
        x = env[m] - env[m].mean()
        ac = np.correlate(x, x, 'full')[len(x) - 1:]
        lags = np.arange(len(ac)) * dt
        est = []
        for n in (1, 2, 4):
            mm = (lags > n * 0.62) & (lags < n * 0.72)
            j = np.where(mm)[0][np.argmax(ac[mm])]
            a, c0, c = ac[j - 1], ac[j], ac[j + 1]
            est.append((lags[j] + 0.5 * (a - c) / (a - 2 * c0 + c) * dt) / n)
        rows.append((w + win / 2, float(np.median(est))))
    return np.array(rows)


def main(song, out):
    y, sr = librosa.load(song, sr=22050, mono=True)
    tc = tempo_curve(y, sr)
    per = median_filter(tc[:, 1], 5)
    hop = 128
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    te = librosa.times_like(env, sr=sr, hop_length=hop)
    tt = np.concatenate([[0], tc[:, 0], [len(y) / sr]])
    pp = np.concatenate([[per[0]], per, [per[-1]]])
    _, q = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop, bpm=60 / np.interp(te, tt, pp),
                                   tightness=400, units='time', trim=False)
    q = np.asarray(q)
    # Ränder: Einschwingen und Ausklang mit lokaler Periode extrapolieren
    p0 = np.median(np.diff(q[5:15]))
    head = [x for x in (q[5] - p0 * np.arange(5, 0, -1)) if x > 1.7]
    q = np.concatenate([head, q[5:]])
    p1 = np.median(np.diff(q[-25:-8]))
    good = q[:-6]
    tail = good[-1] + p1 * np.arange(1, 8)
    q = np.concatenate([good, tail[tail < len(y) / sr - 0.4]])
    # Achtel, auf Onsets gezogen und geglättet
    e = np.sort(np.concatenate([q, (q[:-1] + q[1:]) / 2]))
    env64 = librosa.onset.onset_strength(y=y, sr=sr, hop_length=64)
    t64 = librosa.times_like(env64, sr=sr, hop_length=64)
    thr = np.percentile(env64, 75)
    r = e.copy()
    for i, x in enumerate(e):
        m = (t64 > x - 0.035) & (t64 < x + 0.035)
        if env64[m].max() > thr:
            r[i] = t64[m][np.argmax(env64[m])]
    s = r.copy()
    for i in range(4, len(r) - 4):
        k = np.arange(-4, 5)
        s[i] = np.polyval(np.polyfit(k, r[i - 4:i + 5], 1), 0)
    s = np.concatenate([[s[0] - (s[1] - s[0])], s])      # erster Anschlag = Takt-Eins
    res = (r - s[1:]) * 1000
    info = dict(song=song, unit='Achtel', n_beats=int(len(s)), first=round(float(s[0]), 3),
                bpm_quarter=round(60 / float(np.median(np.diff(s[::2]))), 2),
                jitter_ms_std=round(float(res[4:-4].std()), 2), duration=round(len(y) / sr, 3))
    json.dump({'info': info, 'beats': [round(float(b), 5) for b in s]}, open(out, 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
