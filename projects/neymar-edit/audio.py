#!/usr/bin/env python3
"""Musikbett: der Song läuft an einem Stück (Song-Beat 152 bis Ende), nichts wird geschnitten.

Darüber eine einzige Schicht Originalton, der Clean Feed aus dem Maracanã 2016
(ohne Kommentar):
- ab vier Beats vor Drop 3 leise das angespannte Stadion vor Neymars Elfmeter,
- auf Drop 3 (Song-Beat 368) der Jubel, als der Ball im Netz ist,
- in der Coda leiser Stadion-Teppich unter dem natürlichen Ausklang des Songs.

Die Position ergibt sich aus der Songstruktur (Beat 368), nicht aus Sekunden.

    python3 audio.py  ->  build/music.wav
"""
import os
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt

import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SONG = os.path.join(HERE, 'media', 'audio', 'song.mp3')
PEN = os.path.join(HERE, 'media', 'cuts', 'oly_pen.mp4')
PEN_NET = 43.60            # Quellzeit: Ball im Netz (Frame nachgemessen)
PEN_ROAR = 43.85           # Quellzeit: Jubel setzt ein (Hüllkurve nachgemessen)

A0 = tl.SEGMENTS[0][0]
CHORUS_K = 368 - A0        # Drop 3 = der Treffer
DROPOUT = (CHORUS_K - 4, CHORUS_K)   # 'squeeze' im Renderer: die vier Beats vor dem Schuss
SYNC = {'PEN': (PEN_NET, CHORUS_K)}  # Quellereignis -> Ausgabe-Beat (render.py)
FADE_IN = 0.6


def decode(path, t0=None, dur=None):
    cmd = ['ffmpeg', '-v', 'error']
    if t0 is not None:
        cmd += ['-ss', f'{t0:.4f}']
    cmd += ['-i', path]
    if dur is not None:
        cmd += ['-t', f'{dur:.4f}']
    cmd += ['-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def place(mix, clip, t_out, gain_env):
    i0 = int(round(t_out * SR))
    n = min(len(clip), len(mix) - i0)
    mix[i0:i0 + n] += clip[:n] * gain_env[:n, None]


def build(out):
    song = decode(SONG)
    total = int(round(tl.TOTAL * SR))
    mix = np.zeros((total, 2), np.float32)
    s0, _, o0 = tl.TL['pieces'][0]
    a = int(round((s0 - o0) * SR))
    seg = song[a:a + total]
    mix[:len(seg)] += seg
    fi = int(FADE_IN * SR)
    mix[:fi] *= (np.linspace(0, 1, fi, dtype=np.float32) ** 1.5)[:, None]

    # Stadion vor dem Schuss und der Jubel auf dem Drop
    t_hit = tl.kt(CHORUS_K)
    pre = tl.kt(CHORUS_K) - tl.kt(CHORUS_K - 4)
    crowd = decode(PEN, PEN_ROAR - pre, pre + 5.0)
    crowd = sosfilt(butter(2, 120, 'high', fs=SR, output='sos'), crowd, axis=0).astype(np.float32)
    n = len(crowd)
    env = np.zeros(n, np.float32)
    k = int(pre * SR)
    env[:k] = np.linspace(0.15, 0.55, k) ** 1.2          # Spannung steigt
    r = n - k
    env[k:] = 1.25 * np.exp(-np.arange(r) / (SR * 2.2)) + 0.0
    env[-int(0.8 * SR):] *= np.linspace(1, 0, int(0.8 * SR))
    place(mix, crowd, t_hit - pre, env)

    # Coda: Stadion-Teppich unter dem Ausklang
    t_last = tl.kt(tl.NK)
    carpet = decode(PEN, 150.0, 7.0)
    carpet = sosfilt(butter(2, 1600, 'low', fs=SR, output='sos'), carpet, axis=0).astype(np.float32)
    n = len(carpet)
    env = np.ones(n, np.float32) * 0.5
    env[:int(1.2 * SR)] *= np.linspace(0, 1, int(1.2 * SR))
    env[-int(3.0 * SR):] *= np.linspace(1, 0, int(3.0 * SR)) ** 1.5
    place(mix, carpet, t_last - 0.8, env)

    fo = int(1.4 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None] ** 2
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s16le', out], input=mix.tobytes(), check=True)
    print(out, f'{total / SR:.2f}s', 'Treffer k', CHORUS_K, f'{t_hit:.3f}s', 'letzter Schlag', f'{t_last:.3f}s',
          'peak', round(float(peak), 3))


if __name__ == '__main__':
    build(os.path.join(HERE, 'build', 'music.wav'))
