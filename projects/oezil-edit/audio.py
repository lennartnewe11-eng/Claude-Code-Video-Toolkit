#!/usr/bin/env python3
"""Musikbett: der Song läuft an einem Stück, nichts wird geschnitten, nichts darübergelegt.

Die Ansager-Samples des Songs (Intro, zweiter Break, Outro) sind selbst die
"historische" Tonebene; das Bild antwortet darauf mit Archivmaterial.

Beat 0 liegt bei 0,197 s Songzeit, der Vorlauf (timeline.LEAD) ist länger:
der Anfang wird mit Stille aufgefüllt statt den Song zu verschieben.

    python3 audio.py  ->  build/music.wav
"""
import os
import subprocess

import numpy as np

import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SONG = os.path.join(HERE, 'media', 'audio', 'song.mp3')

CHORUS_K = 48              # Bass-Einsatz Strophe 1: Weißblitz im Bild, Prüfpunkt für deliver.py
DROPOUT = (0, 1)           # im Renderer nur für 'squeeze' (hier ungenutzt)
SYNC = {}                  # Quellereignis -> Ausgabe-Beat (hier keine)
FADE_OUT = 2.0
PEAK = 0.95


def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '2', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def build(out):
    song = decode(SONG)
    total = int(round(tl.TOTAL * SR))
    mix = np.zeros((total, 2), np.float32)
    s0, _, o0 = tl.TL['pieces'][0]
    a = int(round((s0 - o0) * SR))          # Songposition, die bei Ausgabezeit 0 liegt (negativ: Stille davor)
    dst = max(0, -a)
    src = max(0, a)
    n = min(len(song) - src, total - dst)
    mix[dst:dst + n] = song[src:src + n]
    fo = int(FADE_OUT * SR)
    mix[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None] ** 2
    peak = np.abs(mix).max()
    mix *= PEAK / peak                     # Bildschirmaufnahme liegt bei -3,9 dBFS: auf Spitzenpegel heben
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s16le', out], input=mix.tobytes(), check=True)
    print(out, f'{total / SR:.2f}s', 'Song ab', f'{a / SR:+.3f}s', 'Strophe 1 bei', f'{tl.kt(CHORUS_K):.3f}s',
          'peak', round(float(peak), 3))


if __name__ == '__main__':
    build(os.path.join(HERE, 'build', 'music.wav'))
