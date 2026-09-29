#!/usr/bin/env python3
"""Renderer: EDL -> Frames -> Video.

    python3 render.py [--scale 0.5] [--only 40-60] [--jobs 4]

Jeder Shot wird als eigener Chunk mit exakt kf(k1) - kf(k0) Frames gerendert
(Grenzen aus absoluter Zeit, siehe timeline.py) und danach verlustfrei
aneinandergehängt. Alles, was auf dem Beat passiert (thump, Grid-Anordnung,
Aussetzer-Squeeze), wird aus dem gebrochenen Ausgabe-Beat berechnet, nicht
von Hand getimt.
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import audio
import edl
import faces
import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'media')
BUILD = os.path.join(HERE, 'build')
CHUNKS = os.path.join(BUILD, 'chunks')
FONT_TITLE = os.path.join(MEDIA, 'fonts', 'Oswald.ttf')
FONT_MONO = os.path.join(MEDIA, 'fonts', 'IBMPlexMono.ttf')

W0, H0 = 1920, 1080
BANDS = {                      # sichtbares Fenster (w, h) im 16:9-Rahmen
    'full': (1920, 1080),
    'wide': (1920, 960),       # 2:1
    'scope': (1920, 804),      # 2,39:1
    'slit': (1920, 600),       # 3,2:1
    'box43': (1440, 1080),
    'square': (1080, 1080),
    'portrait': (608, 1080),   # 9:16
}
GAP = 8
FACE_H = 0.44                  # Gesichtshöhe als Anteil der Bandhöhe (Höhe bestimmt den Maßstab)
WOBBLE = 0.022                 # Trennlinie springt auf jedem Beat um ±2,2 % der Breite

GRADES = {  # sat, contrast, gamma, lift(r,g,b), gain(r,g,b)
    'warm':    (1.10, 1.10, 0.97, (0.020, 0.012, 0.000), (1.05, 1.00, 0.88)),
    'cold':    (0.48, 1.14, 1.06, (0.000, 0.010, 0.030), (0.92, 0.98, 1.06)),
    'bleak':   (0.10, 1.26, 1.14, (0.000, 0.004, 0.012), (0.95, 1.00, 1.03)),
    'faded':   (0.68, 0.88, 0.95, (0.070, 0.060, 0.040), (1.03, 0.99, 0.86)),
    'neutral': (0.95, 1.06, 1.00, (0.000, 0.000, 0.000), (1.00, 1.00, 1.00)),
    'mono':    (0.00, 1.12, 1.02, (0.010, 0.010, 0.012), (1.00, 1.00, 1.00)),   # Gesichter-Reihe
}


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ── Grade ──────────────────────────────────────────────────────────────────
_LUTS = {}


def grade_lut(name):
    if name not in _LUTS:
        sat, con, gam, lift, gain = GRADES[name]
        x = np.arange(256, dtype=np.float32) / 255.0
        chans = []
        for c in (2, 1, 0):          # BGR-Reihenfolge: b, g, r aus (r, g, b)
            y = x ** gam
            y = 0.5 + (y - 0.5) * con
            y = lift[c] + y * gain[c] * (1 - lift[c])
            chans.append(np.clip(y * 255 + 0.5, 0, 255).astype(np.uint8))
        _LUTS[name] = (sat, np.stack(chans, axis=1).reshape(256, 1, 3))
    return _LUTS[name]


def apply_grade(img, name):
    if not name:
        return img
    sat, lut = grade_lut(name)
    if abs(sat - 1) > 1e-3:
        g = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        img = cv2.addWeighted(img, sat, g, 1 - sat, 0)
    return cv2.LUT(img, lut)


# ── Quellen ────────────────────────────────────────────────────────────────
_PROBE = {}


def probe(path):
    if path not in _PROBE:
        out = subprocess.check_output(['ffprobe', '-v', 'quiet', '-select_streams', 'v:0', '-show_entries',
                                       'stream=width,height,r_frame_rate,field_order', '-show_entries',
                                       'format=duration', '-of', 'json', path])
        j = json.loads(out)
        s = j['streams'][0]
        num, den = s['r_frame_rate'].split('/')
        fps = float(num) / float(den)
        inter = s.get('field_order', 'progressive') not in ('progressive', 'unknown')
        if fps > 100:            # TS-Dateien melden Feldraten
            fps = 25.0
        _PROBE[path] = dict(w=s['width'], h=s['height'], fps=fps, inter=inter,
                            dur=float(j['format']['duration']))
    return _PROBE[path]


class ClipReader:
    """Liest eine Quelle vorwärts ab t0, skaliert auf Höhe hh."""

    def __init__(self, rel, t0, hh):
        self.path = os.path.join(MEDIA, rel)
        p = probe(self.path)
        self.fps = 50.0 if p['inter'] else p['fps']
        ww = int(round(p['w'] * p.get('sar', 1.0) * hh / p['h'] / 2)) * 2
        self.w, self.h = ww, hh
        vf = (['yadif=1'] if p['inter'] else []) + [f'scale={ww}:{hh}:flags=bicubic']
        # fps_mode passthrough: rawvideo ist ein CFR-Muxer; liegt der erste Frame nach dem Seek
        # hinter t=0 (TS-Zeitstempel), füllt ffmpeg die Lücke sonst mit Kopien des ersten
        # Frames auf — bis zu 29 Frames Standbild am Shot-Anfang (nachgemessen).
        self.proc = subprocess.Popen(['ffmpeg', '-v', 'fatal', '-ss', f'{t0:.4f}', '-i', self.path, '-an',
                                      '-vf', ','.join(vf), '-fps_mode', 'passthrough',
                                      '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                                     stdout=subprocess.PIPE, bufsize=ww * hh * 3 * 4)
        self.n = -1
        self.frame = np.zeros((hh, ww, 3), np.uint8)
        self.eof = False

    def get(self, rel_t):
        want = int(np.floor(max(rel_t, 0) * self.fps + 1e-4))
        while self.n < want and not self.eof:
            buf = self.proc.stdout.read(self.w * self.h * 3)
            if len(buf) < self.w * self.h * 3:
                self.eof = True
                break
            self.frame = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.n += 1
        return self.frame

    def close(self):
        try:
            self.proc.stdout.close()
            self.proc.kill()
            self.proc.wait()
        except Exception:
            pass


def fit(src, rw, rh, focus, zoom, dx=0.0):
    """Cover-Einpassung mit Zoom und Fokus, subpixelgenau (warpAffine)."""
    h, w = src.shape[:2]
    s = max(rw / w, rh / h) * zoom
    if s < 0.55:                                     # stark verkleinern: erst flächig mitteln
        f = min(1.0, 1.6 * s)
        src = cv2.resize(src, (max(2, int(w * f)), max(2, int(h * f))), interpolation=cv2.INTER_AREA)
        h, w = src.shape[:2]
        s = max(rw / w, rh / h) * zoom
    cx = (focus[0] + dx) * w
    cy = focus[1] * h
    half_w, half_h = rw / s / 2, rh / s / 2
    cx = min(max(cx, half_w), w - half_w)
    cy = min(max(cy, half_h), h - half_h)
    M = np.float32([[s, 0, rw / 2 - s * cx], [0, s, rh / 2 - s * cy]])
    return cv2.warpAffine(src, M, (rw, rh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# ── Grain, Vignette, Text ──────────────────────────────────────────────────
class Grain:
    def __init__(self, W, H, n=6, seed=7):
        rng = np.random.default_rng(seed)
        self.tex = []
        for _ in range(n):
            g = rng.normal(0, 1, (H // 2 + 8, W // 2 + 8)).astype(np.float32)
            g = cv2.resize(g, (W + 16, H + 16), interpolation=cv2.INTER_LINEAR)
            self.tex.append(g)
        self.W, self.H = W, H

    def apply(self, img, amp, f):
        t = self.tex[f % len(self.tex)]
        ox, oy = (f * 7) % 16, (f * 11) % 16
        g = t[oy:oy + img.shape[0], ox:ox + img.shape[1]]
        out = img.astype(np.float32) + g[..., None] * amp
        return np.clip(out, 0, 255).astype(np.uint8)


def vignette(W, H, strength=0.22):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    v = 1 - strength * np.clip(r, 0, 1) ** 2.2
    return v[..., None].astype(np.float32)


_TXT = {}


def text_img(txt, font, size, track=0.0, color=(255, 255, 255)):
    key = (txt, font, size, track, color)
    if key not in _TXT:
        f = ImageFont.truetype(font, size)
        ws = [f.getbbox(ch)[2] - f.getbbox(ch)[0] if ch != ' ' else size * 0.35 for ch in txt]
        tw = int(sum(ws) + track * size * (len(txt) - 1)) + 8
        asc, desc = f.getmetrics()
        im = Image.new('RGBA', (tw, asc + desc + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x = 4
        for ch, wch in zip(txt, ws):
            d.text((x - f.getbbox(ch)[0] if ch != ' ' else x, 4), ch, font=f, fill=color + (255,))
            x += wch + track * size
        a = np.array(im)
        _TXT[key] = (a[..., :3][..., ::-1].astype(np.float32), a[..., 3:].astype(np.float32) / 255.0)
    return _TXT[key]


def blit(canvas, timg, x, y, alpha):
    rgb, a = timg
    h, w = a.shape[:2]
    x, y = int(x), int(y)
    if alpha <= 0 or x >= canvas.shape[1] or y >= canvas.shape[0]:
        return
    h = min(h, canvas.shape[0] - y)
    w = min(w, canvas.shape[1] - x)
    roi = canvas[y:y + h, x:x + w].astype(np.float32)
    aa = a[:h, :w] * alpha
    canvas[y:y + h, x:x + w] = (roi * (1 - aa) + rgb[:h, :w] * aa).astype(np.uint8)


def label_alpha(tl_, dur):
    vis = min(dur, 1.2)
    return ease_out(tl_ / 0.12) * (1 - ease_io((tl_ - vis + 0.25) / 0.25))


# ── Grid-Anordnungen (Einheiten eines 6×6-Rasters) ─────────────────────────
L3 = [
    [(0, 0, 2, 6), (2, 0, 2, 6), (4, 0, 2, 6)],
    [(0, 0, 4, 6), (4, 0, 2, 3), (4, 3, 2, 3)],
    [(0, 0, 6, 2), (0, 2, 6, 2), (0, 4, 6, 2)],
    [(2, 0, 4, 6), (0, 0, 2, 3), (0, 3, 2, 3)],
    [(0, 0, 6, 4), (0, 4, 3, 2), (3, 4, 3, 2)],
    [(0, 0, 4, 6), (4, 0, 2, 3), (4, 3, 2, 3)],
    [(0, 0, 2, 6), (2, 0, 2, 6), (4, 0, 2, 6)],
    [(0, 0, 6, 6), None, None],
]
L6 = [
    [(0, 0, 2, 3), (2, 0, 2, 3), (4, 0, 2, 3), (0, 3, 2, 3), (2, 3, 2, 3), (4, 3, 2, 3)],
    [(0, 0, 4, 4), (4, 0, 2, 2), (4, 2, 2, 2), (4, 4, 2, 2), (0, 4, 2, 2), (2, 4, 2, 2)],
    [(0, 0, 1, 6), (1, 0, 1, 6), (2, 0, 1, 6), (3, 0, 1, 6), (4, 0, 1, 6), (5, 0, 1, 6)],
    [(0, 0, 3, 2), (3, 0, 3, 2), (0, 2, 3, 2), (3, 2, 3, 2), (0, 4, 3, 2), (3, 4, 3, 2)],
    [(2, 0, 4, 4), (0, 0, 2, 2), (0, 2, 2, 2), (0, 4, 2, 2), (2, 4, 2, 2), (4, 4, 2, 2)],
]


def grid_layout(n, j, nbeats):
    """Anordnung für Beat j eines Grid-Shots: Vorlage + Permutation aus dem Beatindex."""
    if n == 3:
        lay = L3[min(j, len(L3) - 1)] if nbeats == len(L3) else L3[j % len(L3)]
        perm = [(i + j) % 3 for i in range(3)] if lay[1] is not None else [0, 1, 2]
    else:
        if j == nbeats - 1:
            return [(0, 0, 6, 6) if i == 3 else None for i in range(n)]
        lay = L6[j % len(L6)]
        perm = [(i * 5 + j * 2) % 6 for i in range(6)]
    slots = [None] * n
    for ci in range(n):
        slots[ci] = lay[perm[ci]]
    return slots


def unit_rect(u):
    x, y, w, h = u
    X0, Y0 = int(round(x * W0 / 6)), int(round(y * H0 / 6))
    X1, Y1 = int(round((x + w) * W0 / 6)), int(round((y + h) * H0 / 6))
    g = GAP // 2
    return (X0 + (g if x > 0 else 0), Y0 + (g if y > 0 else 0),
            X1 - (g if x + w < 6 else 0), Y1 - (g if y + h < 6 else 0))


# ── Shot-Auflösung ─────────────────────────────────────────────────────────
def resolve():
    shots = []
    for i, s in enumerate(edl.SHOTS):
        s = dict(s)
        k0, k1 = s['k']
        f0 = tl.kf(k0)
        f1 = tl.NFRAMES if k1 is None else tl.kf(k1)
        t0 = tl.kt(k0)
        if i == 0:                   # Vorlauf vor Beat 0 gehört zum ersten Shot (Einblendung)
            f0, t0 = 0, 0.0
        s.update(i=i, f0=f0, f1=f1, t0=t0, t1=(tl.TOTAL if k1 is None else tl.kt(k1)))
        dur = s['t1'] - s['t0']
        clips = []
        for c in s['clips']:
            c = dict(c)
            if isinstance(c['t'], str):                     # Sync-Punkt: Quellereignis auf einen Beat legen
                src_t, k_hit = audio.SYNC[c['t']]
                c['t'] = src_t - c['speed'] * (tl.kt(k_hit) - tl.kt(k0))
            if c['out'] is not None:
                c['speed'] = (c['out'] - c['t']) / dur
            if c.get('auto'):                               # Ausschnitt aufs Gesicht zentrieren
                fa = faces.get(c['src'], c['t'], c['t'] + min(dur, 2.0) * c['speed'])
                if fa:
                    c['focus'] = (fa['cx'], min(0.62, fa['cy'] + 0.1 * fa['h']))
            if s['kind'] == 'face' and not c.get('face'):
                c['face'] = faces.get(c['src'], c['t'], c['t'] + min(dur, 2.0) * c['speed'])
                if not c['face']:
                    raise SystemExit(f"Kein Gesicht gefunden: Shot {i} {c['src']} @{c['t']}")
            clips.append(c)
        s['clips'] = clips
        if s['kind'] == 'split' and len(clips) == 2 and s.get('split') is not None:
            prev = shots[-1] if shots else None
            v = s['split']
            v0 = prev['split_keys'][-1][1] if prev and prev.get('split_keys') else v
            keys = [(k0, v0), (k0 + 0.5, v)] + [tuple(x) for x in s.get('keys', [])]
            s['split_keys'] = sorted(keys)
        shots.append(s)
    return shots


def src_time(c, tl_, t0_shot):
    """Quellzeit relativ zu c['t'] zur lokalen Shot-Zeit tl_.
    ramp=(k_a, k_b, slow): zwischen den Ausgabe-Beats k_a..k_b läuft der Clip mit
    Faktor slow (Zeitlupe), davor und danach mit c['speed']. Die Rampe sitzt so
    per Konstruktion auf dem Takt."""
    sp = c['speed']
    r = c.get('ramp')
    if not r:
        return tl_ * sp
    ta, tb = tl.kt(r[0]) - t0_shot, tl.kt(r[1]) - t0_shot
    if tl_ <= ta:
        return tl_ * sp
    if tl_ <= tb:
        return ta * sp + (tl_ - ta) * r[2]
    return ta * sp + (tb - ta) * r[2] + (tl_ - tb) * sp


def split_at(keys, beat):
    if beat <= keys[0][0]:
        return keys[0][1]
    for (ka, va), (kb, vb) in zip(keys, keys[1:]):
        if beat <= kb:
            return va + (vb - va) * ease_io((beat - ka) / max(kb - ka, 1e-6))
    return keys[-1][1]


def check(shots):
    """Plausibilität: lückenlos, Quelllängen reichen, Band wechselt (mit Begründung)."""
    ok = True
    if shots[0]['f0'] != 0 or shots[-1]['f1'] != tl.NFRAMES:
        print('ABDECKUNG', shots[0]['f0'], shots[-1]['f1'], tl.NFRAMES); ok = False
    for a, b in zip(shots, shots[1:]):
        if a['f1'] != b['f0']:
            print('LÜCKE', a['i'], b['i']); ok = False
        if a['band'] == b['band'] and a['kind'] == b['kind'] == 'single':
            print(f"Band bleibt stehen: Shot {a['i']}->{b['i']} ({a['band']})")
    for s in shots:
        for c in s['clips']:
            p = probe(os.path.join(MEDIA, c['src']))
            end = c['t'] + src_time(c, s['t1'] - s['t0'], s['t0'])
            if end > p['dur'] - 0.05 or c['t'] < 0:
                print(f"QUELLE ZU KURZ: Shot {s['i']} {c['src']} {c['t']:.2f}-{end:.2f} / {p['dur']:.2f}")
                ok = False
    return ok


# ── Rendern ────────────────────────────────────────────────────────────────
def render_shot(args):
    s, scale = args
    Wc, Hc = int(W0 * scale) // 2 * 2, int(H0 * scale) // 2 * 2
    sc = Wc / W0
    out = os.path.join(CHUNKS, f"shot_{s['i']:03d}.mp4")
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{Wc}x{Hc}',
                            '-r', str(tl.FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10',
                            '-pix_fmt', 'yuv444p', out], stdin=subprocess.PIPE)
    grain = Grain(Wc, Hc)
    vig = vignette(Wc, Hc)
    readers = [ClipReader(c['src'], c['t'], Hc) for c in s['clips']]
    fx = set(s['fx'])
    dur = s['t1'] - s['t0']
    k0 = s['k'][0]
    nbeats = (s['k'][1] - k0) if s['k'][1] is not None else 0
    lab_font = int(34 * sc)
    for f in range(s['f0'], s['f1']):
        t = f / tl.FPS
        tl_ = max(0.0, t - s['t0'])
        u = min(1.0, tl_ / dur) if dur > 0 else 0
        beat = tl.beat_of_time(t)
        bph = beat - np.floor(beat + 1e-6)
        canvas = np.zeros((Hc, Wc, 3), np.uint8)

        if s['kind'] == 'coda':
            c = s['clips'][0]
            bw, bh = [int(round(v * sc)) // 2 * 2 for v in BANDS[s['band']]]
            bx, by = (Wc - bw) // 2, (Hc - bh) // 2
            fade = 1 - ease_io((tl_ - s['fade_at']) / 1.1)
            if fade > 0:
                fr = readers[0].get(src_time(c, tl_, s['t0']))
                img = fit(fr, bw, bh, c['focus'], c['zoom'] * (1 + 0.06 * ease_io(u)))
                img = apply_grade(img, s['grade'])
                img = (img.astype(np.float32) * vig[by:by + bh, bx:bx + bw]).astype(np.uint8)
                canvas[by:by + bh, bx:bx + bw] = grain.apply(img, 8, f)
                canvas = cv2.convertScaleAbs(canvas, alpha=fade)
            a = ease_out((tl_ - s['title_at']) / 0.7) * (1 - ease_io((tl_ - (dur - 0.9)) / 0.9))
            if a > 0:
                ti = text_img(s['title'], FONT_TITLE, int(92 * sc), track=0.28)
                su = text_img(s['sub'], FONT_MONO, int(26 * sc), track=0.18, color=(170, 170, 170))
                blit(canvas, ti, (Wc - ti[1].shape[1]) / 2, Hc / 2 - ti[1].shape[0] * 0.62, a)
                blit(canvas, su, (Wc - su[1].shape[1]) / 2, Hc / 2 + ti[1].shape[0] * 0.48, a * 0.9)
            canvas = grain.apply(canvas, 5, f)
            enc.stdin.write(canvas.tobytes())
            continue

        if s['kind'] == 'card':
            a = ease_out(tl_ / 0.35) * (1 - ease_io((tl_ - (dur - 0.7)) / 0.7))
            ti = text_img(s['title'], FONT_TITLE, int(92 * sc), track=0.28)
            su = text_img(s['sub'], FONT_MONO, int(26 * sc), track=0.18, color=(170, 170, 170))
            blit(canvas, ti, (Wc - ti[1].shape[1]) / 2, Hc / 2 - ti[1].shape[0] * 0.62, a)
            blit(canvas, su, (Wc - su[1].shape[1]) / 2, Hc / 2 + ti[1].shape[0] * 0.48, a * 0.9)
            canvas = grain.apply(canvas, 6, f)
            enc.stdin.write(canvas.tobytes())
            continue

        # Band (sichtbares Fenster)
        bw, bh = BANDS[s['band']]
        bw, bh = bw * sc, bh * sc
        if 'open' in fx:
            p = ease_out((beat - k0) / 0.5)
            bh = 600 * sc + (bh - 600 * sc) * p
        if 'close' in fx:
            p = ease_io((beat - (s['k'][1] - 1.5)) / 1.5)
            bh = bh * (1 - p)
        if 'squeeze' in fx:
            p = ease_io((beat - audio.DROPOUT[0]) / (audio.DROPOUT[1] - audio.DROPOUT[0]))
            bh = bh * (1 - 0.38 * p)
        bw, bh = int(round(bw)) // 2 * 2, int(round(bh)) // 2 * 2
        if bh < 2:
            enc.stdin.write(canvas.tobytes())
            continue
        bx, by = (Wc - bw) // 2, (Hc - bh) // 2

        # Kamera-Bewegung
        z = 1.0
        dx = 0.0
        if 'punch' in fx:
            z *= 1 + 0.10 * (1 - ease_out(tl_ / 0.22))
        if 'thump' in fx:
            z *= 1 + 0.035 * np.exp(-bph * 7)
        if 'push' in fx:
            z *= 1 + 0.07 * ease_io(u)
        if 'zoom_in' in fx:
            z *= 1 + 0.17 * u ** 1.2
        if 'squeeze' in fx:
            z *= 1 + 0.10 * ease_io((beat - audio.DROPOUT[0]) / 2)
        if 'drift' in fx:
            dx = (u - 0.5) * 0.06
            z *= 1.05

        labels = []
        if s['kind'] == 'single':
            c = s['clips'][0]
            fr = readers[0].get(src_time(c, tl_, s['t0']))
            img = fit(fr, bw, bh, c['focus'], c['zoom'] * z, dx)
            img = apply_grade(img, s['grade'])
            canvas[by:by + bh, bx:bx + bw] = img
            if s['label']:
                labels.append((s['label'], bx, by + bh))
        elif s['kind'] == 'split' and s.get('split_keys'):
            # Parallelmontage: die Trennlinie trägt den Takt, die Clips laufen durch
            v = split_at(s['split_keys'], beat)
            j = int(np.floor(beat + 1e-6))
            wj, wp = (WOBBLE if j % 2 == 0 else -WOBBLE), (WOBBLE if j % 2 == 1 else -WOBBLE)
            w = wp + (wj - wp) * ease_out(bph / 0.2)
            v = v + w * min(1.0, v / 0.1, (1 - v) / 0.1)
            v = min(max(v, 0.0), 1.0)
            g = GAP * sc * min(1.0, v / 0.02, (1 - v) / 0.02)
            xs = int(round(bx + v * bw - g / 2))
            xe = int(round(bx + v * bw + g / 2))
            panels = [(bx, xs), (xe, bx + bw)]
            for ci, c in enumerate(s['clips']):
                fr = readers[ci].get(src_time(c, tl_, s['t0']))       # läuft weiter, auch wenn schmal
                x0, x1 = panels[ci]
                if x1 - x0 < 4:
                    continue
                img = fit(fr, x1 - x0, bh, c['focus'], c['zoom'] * z, dx)
                img = apply_grade(img, c['grade'])
                canvas[by:by + bh, x0:x1] = img
                if c['label'] and (x1 - x0) > 0.14 * Wc:
                    labels.append((c['label'], x0, by + bh, 'persist'))
        elif s['kind'] == 'split':
            n = len(s['clips'])
            pw = (bw - GAP * sc * (n - 1)) / n
            for ci, c in enumerate(s['clips']):
                x0 = int(round(bx + ci * (pw + GAP * sc)))
                x1 = int(round(bx + ci * (pw + GAP * sc) + pw))
                fr = readers[ci].get(src_time(c, tl_, s['t0']))
                img = fit(fr, x1 - x0, bh, c['focus'], c['zoom'] * z, dx)
                img = apply_grade(img, c['grade'])
                canvas[by:by + bh, x0:x1] = img
                if c['label']:
                    labels.append((c['label'], x0, by + bh))
        elif s['kind'] == 'face':
            # Band steht still, nur das Gesicht wechselt: gleiche Höhe, gleicher Ort
            c = s['clips'][0]
            fc = c['face']
            fr = readers[0].get(src_time(c, tl_, s['t0']))
            h_src, w_src = fr.shape[:2]
            s0 = max(bw / w_src, bh / h_src)
            zf = max(1.0, FACE_H * bh / (fc['h'] * h_src * s0))
            img = fit(fr, bw, bh, (fc['cx'], fc['cy'] + 0.06 * fc['h']), zf * (1 + 0.035 * u))
            img = apply_grade(img, s['grade'])
            canvas[by:by + bh, bx:bx + bw] = img
            if s['label']:
                labels.append((s['label'], bx, by + bh, 'year'))
        elif s['kind'] == 'grid':
            j = int(np.floor(beat - k0 + 1e-6))
            j = min(max(j, 0), nbeats - 1)
            slots = grid_layout(len(s['clips']), j, nbeats)
            zz = 1 + 0.03 * np.exp(-bph * 7)          # jede Umordnung sitzt auf dem Beat
            for ci, c in enumerate(s['clips']):
                fr = readers[ci].get(src_time(c, tl_, s['t0']))   # Clips laufen durch, auch unsichtbar
                if slots[ci] is None:
                    continue
                X0, Y0, X1, Y1 = [int(round(v * sc)) for v in unit_rect(slots[ci])]
                img = fit(fr, X1 - X0, Y1 - Y0, c['focus'], c['zoom'] * zz)
                img = apply_grade(img, s['grade'])
                canvas[Y0:Y1, X0:X1] = img
            if s['label']:
                labels.append((s['label'], 0, Hc))

        # Look
        region = canvas[by:by + bh, bx:bx + bw]
        region = (region.astype(np.float32) * vig[by:by + bh, bx:bx + bw]).astype(np.uint8)
        if 'grain_heavy' in fx or 'squeeze' in fx:
            region = grain.apply(region, 15, f)
        elif 'grain' in fx:
            region = grain.apply(region, 8, f)
        else:
            region = grain.apply(region, 3, f)
        canvas[by:by + bh, bx:bx + bw] = region
        if 'rgbhit' in fx and tl_ < 0.14:
            o = int(round(18 * sc * (1 - tl_ / 0.14)))
            if o > 0:
                b_, g_, r_ = cv2.split(canvas)
                r_ = np.roll(r_, o, axis=1)
                b_ = np.roll(b_, -o, axis=1)
                canvas = cv2.merge([b_, g_, r_])
        if 'thump' in fx:
            canvas = cv2.convertScaleAbs(canvas, alpha=1 + 0.10 * np.exp(-bph * 9))
        if 'flash' in fx and tl_ < 0.4:
            a = (1 - tl_ / 0.4) ** 1.6
            canvas = cv2.addWeighted(canvas, 1 - a, np.full_like(canvas, 255), a, 0)
        if 'dip' in fx:
            p = ease_io((beat - (s['k'][1] - 0.6)) / 0.6)
            if p > 0:
                canvas = cv2.convertScaleAbs(canvas, alpha=1 - p)
        if t < tl.LEAD:
            canvas = cv2.convertScaleAbs(canvas, alpha=ease_io(t / tl.LEAD))
        for lab in labels:
            txt, x, ybot = lab[:3]
            mode = lab[3] if len(lab) > 3 else None
            if mode == 'year':
                ti = text_img(txt, FONT_MONO, int(46 * sc), track=0.10)
                blit(canvas, ti, bx + bw + 28 * sc, ybot - ti[1].shape[0] - 10 * sc, 0.92)
                continue
            ti = text_img(txt, FONT_MONO, lab_font, track=0.12)
            a = 0.9 if mode == 'persist' else label_alpha(tl_, dur)
            blit(canvas, ti, x + 26 * sc, ybot - ti[1].shape[0] - 18 * sc, a)
        enc.stdin.write(canvas.tobytes())
    for r in readers:
        r.close()
    enc.stdin.close()
    enc.wait()
    return s['i'], s['f1'] - s['f0']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--only', default=None, help='Shotbereich a-b')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--out', default=os.path.join(BUILD, 'messi_edit_master.mp4'))
    a = ap.parse_args()
    os.makedirs(CHUNKS, exist_ok=True)
    shots = resolve()
    if not check(shots):
        sys.exit(1)
    sel = shots
    if a.only:
        lo, hi = map(int, a.only.split('-'))
        sel = [s for s in shots if lo <= s['i'] <= hi]
    order = sorted(sel, key=lambda s: -(s['f1'] - s['f0']) * max(1, len(s['clips'])))
    with ProcessPoolExecutor(a.jobs) as ex:
        for i, n in ex.map(render_shot, [(s, a.scale) for s in order]):
            print(f'shot {i:3d}  {n:4d} frames', flush=True)
    if a.only:
        return
    lst = os.path.join(CHUNKS, 'list.txt')
    with open(lst, 'w') as fh:
        for s in shots:
            fh.write(f"file 'shot_{s['i']:03d}.mp4'\n")
    music = os.path.join(BUILD, 'music.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', music,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                    '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '256k',
                    '-movflags', '+faststart', '-shortest', a.out], check=True)
    print('->', a.out)


if __name__ == '__main__':
    main()
