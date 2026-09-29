#!/usr/bin/env python3
"""Musikbett: der Song läuft an einem Stück, nichts wird herausgeschnitten.

- Einblendung über den Vorlauf vor Ausgabe-Beat 0.
- Vor dem Refrain wird die Musik zwei Beats lang *abgesenkt*, nicht stumm
  geschaltet — der Song läuft hörbar weiter, darüber das Stadion bei Montiels
  Elfmeter. Der Jubel landet exakt auf dem ersten Refrain-Beat. Die Position
  wird aus der Songstruktur gerechnet (Song-Beat 512), nicht als Sekundenzahl.
- Nach dem letzten Schlag: der natürliche Ausklang des Songs, ein Nachhall aus
  dem letzten Schlag und leiser Stadion-Teppich (Clean Feed 2014, ohne
  Kommentar), dann Ausblendung.

    python3 audio.py  ->  build/music.wav
"""
import os
import subprocess

import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SONG = os.path.join(HERE, 'media', 'audio', 'song.mp3')
ROAR_SRC = os.path.join(HERE, 'media', 'src', 'final22_hl.mp4')
ROAR_HIT = 106.90          # Quellzeit, an der der Jubel einsetzt (Hüllkurve nachgemessen)
CROWD = os.path.join(HERE, 'media', 'src', 'crowd14.wav')

A0 = tl.SEGMENTS[0][0]
CHORUS_K = 512 - A0        # Refrain 2 beginnt auf Song-Beat 512
DROPOUT = (CHORUS_K - 2, CHORUS_K)
DUCK = 0.28                # Pegel der Musik während der Absenkung
FADE_IN = 0.9              # s


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


def reverb_ir(rt60=3.2, length=4.5, seed=3):
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.91 * t / rt60)
    ir = rng.normal(0, 1, (n, 2)) * env[:, None]
    ir[: int(0.012 * SR)] = 0                       # Vorverzögerung
    sos = butter(2, 5200, 'low', fs=SR, output='sos')
    ir = sosfilt(sos, ir, axis=0)
    return ir / np.sqrt((ir ** 2).sum(0))[None, :]


def build(out):
    song = decode(SONG)
    total = int(round(tl.TOTAL * SR))
    mix = np.zeros((total, 2), np.float32)
    s0, _, o0 = tl.TL['pieces'][0]
    # Song an einem Stück: ab (erster Beat - Vorlauf) bis zum Dateiende
    a = int(round((s0 - o0) * SR))
    seg = song[a:a + total]
    mix[:len(seg)] += seg
    fi = int(FADE_IN * SR)
    mix[:fi] *= (np.linspace(0, 1, fi, dtype=np.float32) ** 1.6)[:, None]

    # Absenkung vor dem Refrain (Song läuft weiter)
    d0, d1 = tl.kt(DROPOUT[0]), tl.kt(DROPOUT[1])
    i0, i1 = int(round((d0 - 0.012) * SR)), int(round((d1 - 0.012) * SR))
    g = np.ones(total, np.float32)
    f = int(0.03 * SR)
    g[i0:i1] = DUCK
    g[i0 - f:i0] = np.linspace(1, DUCK, f)
    g[i1 - f:i1] = np.linspace(DUCK, 1, f)
    mix *= g[:, None]

    # Stadion: ab Beginn der Absenkung, Jubel exakt auf dem Refrain-Beat
    pre = d1 - d0
    roar = decode(ROAR_SRC, ROAR_HIT - pre, pre + 2.2)
    env = np.ones(len(roar), np.float32)
    k = int(pre * SR)
    env[k:] = np.linspace(1.0, 0.0, len(roar) - k) ** 1.5 * 0.55
    env[k:k + int(0.08 * SR)] = np.linspace(1.0, 0.55, int(0.08 * SR))
    roar *= env[:, None] * 1.2
    r0 = int(round(d0 * SR))
    n = min(len(roar), total - r0)
    mix[r0:r0 + n] += roar[:n]

    # Coda: Nachhall aus dem letzten Schlag
    t_last = tl.kt(tl.NK)
    L = int(round(t_last * SR))
    dry = mix[L - int(0.03 * SR):L + int(0.45 * SR)].copy()
    dry *= np.hanning(len(dry))[:, None] ** 0.3
    ir = reverb_ir()
    wet = np.stack([fftconvolve(dry[:, c], ir[:, c]) for c in range(2)], axis=1).astype(np.float32)
    wet *= 0.55 * np.abs(mix[L:L + int(0.3 * SR)]).max() / max(1e-6, np.abs(wet).max())
    w0 = L - int(0.03 * SR)
    n = min(len(wet), total - w0)
    mix[w0:w0 + n] += wet[:n]

    # Coda: Stadion-Teppich, tiefpassgefiltert (fern)
    crowd = decode(CROWD)
    crowd = sosfilt(butter(2, 1400, 'low', fs=SR, output='sos'), crowd, axis=0).astype(np.float32)
    c0 = L - int(0.6 * SR)
    n = min(len(crowd), total - c0)
    cenv = np.ones(n, np.float32)
    ci = int(1.4 * SR)
    cenv[:ci] = np.linspace(0, 1, ci)
    co = int(3.5 * SR)
    cenv[-co:] = np.linspace(1, 0, co) ** 1.4
    crowd_rms = np.sqrt((crowd ** 2).mean())
    mix[c0:c0 + n] += crowd[:n] * cenv[:, None] * (0.045 / max(crowd_rms, 1e-6))

    fo = int(1.5 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None] ** 2
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s16le', out], input=mix.tobytes(), check=True)
    print(out, f'{total / SR:.2f}s', 'Absenkung k', DROPOUT, f'{d0:.3f}-{d1:.3f}s',
          'letzter Schlag', f'{t_last:.3f}s', 'peak', round(float(peak), 3))


if __name__ == '__main__':
    build(os.path.join(HERE, 'build', 'music.wav'))
