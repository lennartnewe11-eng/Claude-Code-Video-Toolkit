#!/usr/bin/env python3
"""Synthesise the VFX sound layer: whooshes, impacts, risers, sub drops.

Everything here is generated from noise and oscillators, so the result is
licence-free and needs no sample library.
"""
import numpy as np

SR = 48000


def _env(n, attack, release, curve=2.0):
    a = max(int(n * attack), 1)
    r = max(int(n * release), 1)
    s = max(n - a - r, 0)
    return np.concatenate([
        np.linspace(0, 1, a) ** curve,
        np.ones(s),
        np.linspace(1, 0, r) ** curve,
    ])[:n]


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def _onepole(x, cutoff):
    """Cheap low-pass; cutoff may be a scalar or a per-sample array."""
    a = np.clip(1.0 - np.exp(-2 * np.pi * np.asarray(cutoff) / SR), 1e-5, 1.0)
    a = np.broadcast_to(a, x.shape).astype(np.float64)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(x.size):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def whoosh(dur=0.75, seed=1, direction="up", intensity=1.0):
    """Air movement for a fast transition - noise swept through a filter."""
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    sweep = (300 + 5200 * t ** 1.6) if direction == "up" else (5500 - 5200 * t ** 0.7)
    x = _noise(n, seed)
    y = _onepole(x, sweep)
    y -= _onepole(y, 120)                      # strip rumble
    y *= _env(n, 0.22, 0.55, curve=1.7)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.55 * intensity


def impact(dur=1.1, seed=2, pitch=64.0, intensity=1.0):
    """Low hit for a hard cut: pitch-dropping sine plus a noise transient."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = pitch * np.exp(-3.4 * t)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-4.2 * t)
    click = _onepole(_noise(n, seed), 2600) * np.exp(-38 * t)
    y = body * 0.92 + click * 0.32
    return y / (np.max(np.abs(y)) + 1e-9) * 0.72 * intensity


def riser(dur=2.4, seed=3, intensity=1.0):
    """Tension build before a big change."""
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    sweep = 180 + 4200 * t ** 2.4
    y = _onepole(_noise(n, seed), sweep)
    shimmer = np.sin(2 * np.pi * np.cumsum(220 + 1500 * t ** 2) / SR) * 0.22 * t ** 2
    y = y / (np.max(np.abs(y)) + 1e-9) + shimmer
    y *= t ** 1.9
    return y / (np.max(np.abs(y)) + 1e-9) * 0.42 * intensity


def sub_drop(dur=2.0, seed=4, intensity=1.0):
    """Deep drop marking an act change."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 105 * np.exp(-1.9 * t) + 26
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-1.5 * t)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8 * intensity


def reverse_swell(dur=1.8, seed=5, intensity=1.0):
    """Reverse-cymbal style swell that resolves on the cut."""
    n = int(SR * dur)
    y = _onepole(_noise(n, seed), 7000)
    y -= _onepole(y, 700)
    y *= np.linspace(0, 1, n) ** 2.6
    return y / (np.max(np.abs(y)) + 1e-9) * 0.4 * intensity


def render(events, total_dur):
    """Mix timestamped events onto one stereo bed.

    events: list of (time_seconds, kind, kwargs)
    """
    n = int(SR * total_dur) + SR
    bus = np.zeros(n)
    makers = {"whoosh": whoosh, "impact": impact, "riser": riser,
              "sub_drop": sub_drop, "reverse_swell": reverse_swell}
    for i, (t, kind, kw) in enumerate(events):
        sig = makers[kind](seed=100 + i, **kw)
        start = int(t * SR)
        if start < 0:
            sig, start = sig[-start:], 0
        end = min(start + sig.size, n)
        if end > start:
            bus[start:end] += sig[:end - start]

    peak = np.max(np.abs(bus))
    if peak > 0.94:
        bus *= 0.94 / peak
    # gentle stereo spread so the layer sits around the music
    delay = int(0.006 * SR)
    left = bus
    right = np.concatenate([np.zeros(delay), bus[:-delay]]) * 0.96
    return np.stack([left, right], axis=1)


def write_wav(path, stereo):
    import wave
    pcm = np.clip(stereo, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
