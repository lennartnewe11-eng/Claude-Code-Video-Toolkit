#!/usr/bin/env python3
"""Musikbett: „Freaks“ läuft an einem Stück, nichts geschnitten, nichts darübergelegt.

Das Video ist für TikTok gedacht: dort wird der Originalton stumm geschaltet und
derselbe Song aus der TikTok-Bibliothek ab 0:00 daruntergelegt. Deshalb gibt es
hier bewusst keine Absenkung und keinen Stadionton wie im Messi-Edit: was man in
dieser Datei hört, ist genau das, was auf TikTok läuft. Der erste Anschlag liegt
bei timeline.LEAD (0,06 s).

    python3 audio.py  ->  build/music.wav
"""
import os
import subprocess

import numpy as np

import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SONG = os.path.join(HERE, 'media', 'audio', 'song.mp3')

CHORUS_K = 296             # Refrain 2: Montiels Elfmeter ist im Netz (render.py, Sync-Punkt MONTIEL)
ROAR_HIT = 106.90          # Quellzeit in final22_hl.mp4: Ball im Netz, Jubel setzt ein (nachgemessen)
DROPOUT = (CHORUS_K - 2, CHORUS_K)   # nur für das Renderer-FX 'squeeze' (hier ungenutzt)
FADE_OUT = 1.5
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
    a = int(round((s0 - o0) * SR))          # Songposition bei Ausgabezeit 0
    n = min(len(song) - a, total)
    mix[:n] = song[a:a + n]
    fo = int(FADE_OUT * SR)
    mix[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None] ** 2
    peak = np.abs(mix).max()
    mix *= PEAK / peak
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s16le', out], input=mix.tobytes(), check=True)
    print(out, f'{total / SR:.2f}s', 'Song ab', f'{a / SR:.3f}s', 'Refrain 2 bei', f'{tl.kt(CHORUS_K):.3f}s',
          'peak vorher', round(float(peak), 3))


if __name__ == '__main__':
    build(os.path.join(HERE, 'build', 'music.wav'))
