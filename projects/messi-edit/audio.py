#!/usr/bin/env python3
"""Musikbett bauen: Song-Segmente auf Beat-Grenzen aneinandersetzen.

- Jeder Splice sitzt SPLICE_PRE vor dem Beat, damit der Transient des neuen
  Beats unangetastet bleibt; gleichleistende Überblendung über XF Sekunden.
- Programmierter Aussetzer: die zwei Beats vor dem Refrain (aus der Segment-
  struktur gerechnet, nicht als feste Sekundenzahl) ist die Musik stumm. Man
  hört nur das Stadion beim letzten Elfmeter 2022; der Jubel landet exakt auf
  dem ersten Refrain-Beat.

    python3 audio.py  ->  build/music.wav
"""
import os
import subprocess

import numpy as np

import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SPLICE_PRE = 0.012
XF = 0.010
SONG = os.path.join(HERE, 'media', 'audio', 'song.mp3')
ROAR_SRC = os.path.join(HERE, 'media', 'src', 'final22_hl.mp4')
ROAR_HIT = 106.90          # Quellzeit, an der der Jubel einsetzt (Hüllkurve nachgemessen)

# Refrain beginnt 32 Beats nach Beginn des Segments (480, 576) -> Song-Beat 512
CHORUS_K = tl.section_bounds()[(480, 576)][0] + (512 - 480)
DROPOUT = (CHORUS_K - 2, CHORUS_K)


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


def ramp(n, up=True):
    x = np.linspace(0, np.pi / 2, n, dtype=np.float32)
    return (np.sin(x) if up else np.cos(x))[:, None]


def build(out):
    song = decode(SONG)
    total = int(round(tl.TOTAL * SR))
    mix = np.zeros((total, 2), np.float32)
    xf = int(XF * SR)
    pieces = tl.TL['pieces']
    for i, (s0, s1, o0) in enumerate(pieces):
        a = int(round((s0 - SPLICE_PRE) * SR))
        last = i == len(pieces) - 1
        b = len(song) if last else int(round((s1 - SPLICE_PRE) * SR)) + xf
        seg = song[a:b].copy()
        if i > 0:
            seg[:xf] *= ramp(xf, True)
        if not last:
            seg[-xf:] *= ramp(xf, False)
        o = int(round((o0 - SPLICE_PRE) * SR))
        n = min(len(seg), total - o)
        mix[o:o + n] += seg[:n]
    # Einblendung
    fi = int(tl.LEAD * SR)
    mix[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
    # Aussetzer
    d0, d1 = tl.kt(DROPOUT[0]), tl.kt(DROPOUT[1])
    i0, i1 = int(round((d0 - SPLICE_PRE) * SR)), int(round((d1 - SPLICE_PRE) * SR))
    g = np.ones(total, np.float32)
    f = int(0.015 * SR)
    g[i0:i1] = 0
    g[i0 - f:i0] = np.linspace(1, 0, f)
    g[i1 - f:i1] = np.linspace(0, 1, f)
    mix *= g[:, None]
    # Stadion: ab Anfang des Aussetzers, Jubel exakt auf dem Refrain-Beat
    pre = d1 - d0
    roar = decode(ROAR_SRC, ROAR_HIT - pre, pre + 2.2)
    env = np.ones(len(roar), np.float32)
    k = int(pre * SR)
    tail = len(roar) - k
    env[k:] = np.linspace(1.0, 0.0, tail) ** 1.5 * 0.55 + 0.0
    env[k:k + int(0.08 * SR)] = np.linspace(1.0, 0.55, int(0.08 * SR))
    roar *= env[:, None] * 1.25
    r0 = int(round(d0 * SR))
    n = min(len(roar), total - r0)
    mix[r0:r0 + n] += roar[:n]
    # Ausklang
    fo = int(1.2 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None] ** 2
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s16le', out], input=mix.tobytes(), check=True)
    print(out, f'{total / SR:.2f}s', 'Aussetzer k', DROPOUT, f'{d0:.3f}-{d1:.3f}s', 'peak', round(float(peak), 3))


if __name__ == '__main__':
    build(os.path.join(HERE, 'build', 'music.wav'))
