"""Zeitachse.

Der Edit läuft auf *Ausgabe-Beats* k. Jeder Ausgabe-Beat ist ein Song-Beat n.
Alle Zeiten werden aus absoluten Song-Zeiten gerechnet (beats[n] - beats[a] +
Offset), nie aus aufaddierten Shotlängen, und erst ganz am Ende auf Frames
gerundet: frame(k) = round(T(k) * FPS).

Der Song läuft an einem Stück, vom ersten Beat bis zum Ausklang (ein Segment).
Der Mechanismus für mehrere Segmente bleibt; jeder Sprung müsste
(b - a) % 8 == 0 erfüllen (eine Zeile = 8 Beats), build() prüft das.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 50                    # Quellen überwiegend 25/50p (Europa), 30p-Quellen werden gehalten
LEAD = 0.40                 # s Vorlauf vor Ausgabe-Beat 0 (Einblendung)

# (erster Song-Beat, letzter Schlag). Der ganze Song, Ausgabe-Beat k = Song-Beat n:
#     0– 48 Intro (Ansager: "return to the classics", "Classic, classic, classic")
#    48–112 Strophe 1        112–144 Break (Streicher, kein Bass)
#   144–208 Strophe 2        208–240 Break ("Meine Damen, für Sie singt ...")
#   240–304 Strophe 3        304–344 Outro ("... eindrucksvoller Aufnahmen anhören")
SEGMENTS = [
    (0, 344),
]
CODA = 4.0       # s nach dem letzten Schlag: Ausklang, letztes Bild, Titel

# Abschnitte in Ausgabe-Beats (werden aus SEGMENTS abgeleitet, s. u.)
SECTIONS = {}


def load_beats():
    return np.array(json.load(open(os.path.join(HERE, 'build', 'beatmap.json')))['beats'])


def build():
    B = load_beats()
    for (a0, b0), (a1, _) in zip(SEGMENTS, SEGMENTS[1:]):
        assert (a1 - b0) % 8 == 0, f'Splice {b0}->{a1} verletzt die Zeilenphase'
    k_song = []          # Ausgabe-Beat k -> Song-Beat n
    T = []               # Ausgabe-Beat k -> Ausgabezeit (s)
    pieces = []          # (song_t0, song_t1, out_t0) für den Audioschnitt
    off = LEAD
    for a, b in SEGMENTS:
        pieces.append((B[a], B[b], off))
        for n in range(a, b):
            k_song.append(n)
            T.append(off + (B[n] - B[a]))
        off += B[b] - B[a]
    T.append(off)                     # Ende des letzten Beats
    k_song.append(SEGMENTS[-1][1])
    total = off + CODA
    return dict(B=B, T=np.array(T), k_song=np.array(k_song), pieces=pieces, total=total)


TL = build()
T = TL['T']
NK = len(T) - 1                      # Anzahl Ausgabe-Beats
TOTAL = TL['total']
NFRAMES = int(round(TOTAL * FPS))


def kt(k):
    """Ausgabezeit von (auch gebrochenem) Ausgabe-Beat k."""
    k = float(k)
    if k <= 0:
        return T[0] + k * (T[1] - T[0])
    if k >= NK:
        return T[NK] + (k - NK) * (T[NK] - T[NK - 1])
    i = int(np.floor(k))
    return T[i] + (k - i) * (T[i + 1] - T[i])


def kf(k):
    """Frame-Grenze von Ausgabe-Beat k (aus absoluter Zeit gerundet)."""
    return int(round(kt(k) * FPS))


def beat_of_time(t):
    """Gebrochener Ausgabe-Beat einer Ausgabezeit."""
    if t <= T[0]:
        return (t - T[0]) / (T[1] - T[0])
    if t >= T[NK]:
        return NK + (t - T[NK]) / (T[NK] - T[NK - 1])
    i = int(np.searchsorted(T, t, side='right') - 1)
    return i + (t - T[i]) / (T[i + 1] - T[i])


def section_bounds():
    """Abschnittsgrenzen in Ausgabe-Beats, aus der Segmentstruktur gerechnet."""
    k = 0
    out = {}
    for a, b in SEGMENTS:
        out[(a, b)] = (k, k + (b - a))
        k += b - a
    return out


if __name__ == '__main__':
    print('Ausgabe-Beats:', NK, ' Dauer: %.2f s' % TOTAL, ' Frames:', NFRAMES)
    for (a, b), (k0, k1) in section_bounds().items():
        print(f'  Song {a:3d}–{b:3d}  →  k {k0:3d}–{k1:3d}   {kt(k0):6.2f}–{kt(k1):6.2f} s')
