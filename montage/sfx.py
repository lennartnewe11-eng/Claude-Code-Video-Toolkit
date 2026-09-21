#!/usr/bin/env python3
"""Synthesised effect layer, voiced and levelled against a reference mix.

Measuring the reference's sound design settled two things this module is
built around:

* Level. Its bed sits near -26 dBFS and its peaks near -10 dBFS, and
  individual accents rise only about +4 to +8 dB above the bed, +13 at the
  very most. So effects are mixed *against the music underneath them*:
  `render` reads the music's local level at each event and sets that
  event's gain relative to it, instead of using absolute amplitudes.

* Voice. Across 40 measured transients not one was bass-dominated - low
  band energy never passed 0.20 of the total. The reference is mid and
  air forward, not boomy. Every voice here is high-passed accordingly and
  the heaviest one still centres above 90 Hz.

Everything is generated from noise and oscillators, so the layer is
licence-free and needs no sample library.
"""
import numpy as np
from scipy import signal

SR = 48000


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

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


def _butter(x, cutoff, btype, order=2):
    """Zero-phase Butterworth. Vectorised - a per-sample Python loop over a
    two-and-a-half minute bus is far too slow to be usable."""
    nyq = SR / 2
    if btype == "band":
        wn = [max(cutoff[0], 20) / nyq, min(cutoff[1], nyq * 0.98) / nyq]
    else:
        wn = min(max(cutoff, 20), nyq * 0.98) / nyq
    b, a = signal.butter(order, wn, btype=btype)
    return signal.filtfilt(b, a, x)


def _lp(x, cutoff):
    """Low-pass. A per-sample cutoff array gives a swept filter, done by
    crossfading a small bank of fixed-cutoff passes."""
    c = np.asarray(cutoff, dtype=np.float64)
    if c.ndim == 0:
        return _butter(x, float(c), "low")
    steps = np.geomspace(max(c.min(), 60), min(c.max(), SR / 2 * 0.95), 12)
    bank = np.stack([_butter(x, f, "low") for f in steps])
    idx = np.interp(c, steps, np.arange(steps.size))
    lo = np.clip(np.floor(idx).astype(int), 0, steps.size - 1)
    hi = np.clip(lo + 1, 0, steps.size - 1)
    frac = idx - lo
    cols = np.arange(x.size)
    return bank[lo, cols] * (1 - frac) + bank[hi, cols] * frac


def _hp(x, cutoff):
    return _butter(x, float(np.min(cutoff)), "high")


def _bp(x, lo, hi):
    return _butter(x, (float(lo), float(hi)), "band")


def _norm(y, level=1.0):
    peak = np.max(np.abs(y))
    return y / peak * level if peak > 0 else y


# --------------------------------------------------------------------------
# voices - all mid/air forward, nothing below ~90 Hz
# --------------------------------------------------------------------------

def air_whoosh(dur=0.7, seed=1, direction="up"):
    """Air movement across a fast cut. Band-limited 400 Hz - 7 kHz."""
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    sweep = (700 + 5600 * t ** 1.5) if direction == "up" else (6300 - 5600 * t ** 0.65)
    y = _bp(_noise(n, seed), 400, 7000)
    y = _lp(y, sweep)
    y = _hp(y, 380)
    return _norm(y * _env(n, 0.26, 0.58, 1.6))


def soft_thud(dur=0.55, seed=2, pitch=120.0):
    """Weighted accent for a hard cut - a body around 120 Hz, not a sub."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = pitch * np.exp(-5.0 * t) + 90.0
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-7.5 * t)
    snap = _bp(_noise(n, seed), 900, 5200) * np.exp(-26 * t)
    y = _hp(body * 0.55 + snap * 0.62, 85)
    return _norm(y)


def tick(dur=0.16, seed=3):
    """Dry mid click for staccato cuts."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    y = _bp(_noise(n, seed), 1100, 6500) * np.exp(-40 * t)
    return _norm(y)


def swell(dur=2.2, seed=4):
    """Airy build into a change. No sub content, resolves on the cut."""
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    y = _lp(_bp(_noise(n, seed), 500, 9000), 900 + 5200 * t ** 2.2)
    shimmer = np.sin(2 * np.pi * np.cumsum(900 + 2600 * t ** 2) / SR) * 0.16 * t ** 2.5
    y = _norm(y) + shimmer
    return _norm(y * (t ** 1.8))


def reverse_air(dur=1.5, seed=5):
    """Reverse-swell that lands on the cut."""
    n = int(SR * dur)
    y = _hp(_noise(n, seed), 900)
    return _norm(y * np.linspace(0, 1, n) ** 2.8)


def drop(dur=1.6, seed=6):
    """Section marker. Descending, but kept above 90 Hz."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 320 * np.exp(-2.6 * t) + 95
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-2.2 * t)
    air = _hp(_noise(n, seed), 2600) * np.exp(-5.0 * t) * 0.30
    return _norm(_hp(y * 0.8 + air, 88))


VOICES = {
    "air_whoosh": air_whoosh,
    "soft_thud": soft_thud,
    "tick": tick,
    "swell": swell,
    "reverse_air": reverse_air,
    "drop": drop,
}


# --------------------------------------------------------------------------
# mix
# --------------------------------------------------------------------------

def _peak_window_rms(x, window=0.040):
    """RMS of the signal's loudest short window - what a transient reads as."""
    w = max(int(SR * window), 1)
    if x.size <= w:
        return np.sqrt(np.mean(x ** 2))
    power = np.convolve(x ** 2, np.ones(w) / w, mode="valid")
    return np.sqrt(power.max())


def _local_db(music_mono, t, window=0.8):
    """How loud the music READS around time t, in dBFS.

    Measured as its loudest short window, not the average over `window`:
    an accent is heard against the music's peaks, and levelling against a
    long-window average puts the effect below them, where it vanishes.
    """
    if music_mono is None:
        return None
    a = max(int((t - window / 2) * SR), 0)
    b = min(int((t + window / 2) * SR), music_mono.size)
    if b <= a:
        return -60.0
    return 20 * np.log10(_peak_window_rms(music_mono[a:b]) + 1e-9)


def render(events, total_dur, music_mono=None, default_over_db=5.0):
    """Mix timestamped events, levelled against the music underneath.

    events: list of (time_seconds, voice, kwargs). `kwargs` may carry
    `over_db` - how far this accent should sit above the music's local
    level - and any voice parameter. With no music supplied the events
    fall back to a fixed modest level.
    """
    n = int(SR * total_dur) + SR
    bus = np.zeros(n, dtype=np.float64)

    for i, (t, kind, kw) in enumerate(events):
        kw = dict(kw)
        over = kw.pop("over_db", default_over_db)
        sig = VOICES[kind](seed=101 + i * 7, **kw)

        bed = _local_db(music_mono, max(t, 0.0)) if music_mono is not None else -20.0
        # `over` is how far the MIX should rise at this moment. Music and
        # effect sum there, so the effect itself sits a little lower; and a
        # transient's overall RMS says nothing about how loud it reads, so
        # the level is set on its loudest 40 ms window.
        rise = 10 ** (over / 20)
        target_db = bed + 20 * np.log10(max(rise ** 2 - 1.0, 1e-3)) / 2
        sig = sig * (10 ** (target_db / 20) / (_peak_window_rms(sig) + 1e-9))

        start = int(t * SR)
        if start < 0:
            sig, start = sig[-start:], 0
        end = min(start + sig.size, n)
        if end > start:
            bus[start:end] += sig[:end - start]

    bus = _hp(bus, 45)                                  # keep the low end clean

    # Spread the layer slightly around the music. A wide delay decorrelates
    # the channels, and a mono downmix then loses ~3 dB of everything set
    # above - so keep the delay short and restore the mono level by
    # measurement rather than trusting it.
    delay = int(0.0018 * SR)
    right = np.concatenate([np.zeros(delay), bus[:-delay]]) * 0.97
    stereo = np.stack([bus, right], axis=1)

    ref = _peak_window_rms(bus)
    got = _peak_window_rms(stereo.mean(axis=1))
    if got > 1e-9 and ref > 1e-9:
        stereo *= ref / got

    # Soft-limit only what would actually clip. Scaling the whole bus to a
    # fixed ceiling instead would silently undo every per-event level set
    # above - loud settings all collapse onto the same output.
    return np.tanh(stereo / 0.88) * 0.88


def write_wav(path, stereo):
    import wave
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def load_mono(path):
    """Read a wav down to mono float, for level measurement."""
    import wave
    with wave.open(str(path), "rb") as w:
        n, ch = w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768
    return a.reshape(-1, ch).mean(axis=1).astype(np.float64)
