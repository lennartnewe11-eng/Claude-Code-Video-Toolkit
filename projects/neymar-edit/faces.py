"""Gesicht je Clip vermessen — einmal über den Clip, nicht pro Frame.

Pro Frame gemessen würde das Gesicht pulsieren (Lehre aus dem Freistellen in
erkenntnisse.md). Deshalb: Frames im genutzten Bereich abtasten, je Frame das
größte Gesicht nehmen, Ausreißer verwerfen, Median. Ergebnis als Anteile des
Quellbilds (cx, cy, h), gecacht in build/faces.json.

Die Höhe bestimmt den Maßstab: render.py skaliert so, dass jedes Gesicht
gleich hoch im Band steht.
"""
import json
import os
import subprocess

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'media')
CACHE = os.path.join(HERE, 'build', 'faces.json')
CASCADES = [os.path.join(MEDIA, 'models', n) for n in
            ('haarcascade_frontalface_default.xml', 'haarcascade_frontalface_alt2.xml')]


def _frames(path, t0, t1, fps=6, w=640):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout
    sw, sh = map(int, out.strip().split(',')[:2])
    h = int(round(sh * w / sw / 2)) * 2
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-ss', f'{t0:.3f}', '-i', path, '-t', f'{t1 - t0:.3f}',
                          '-vf', f'fps={fps},scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w), w, h


def measure(src, t0, t1):
    fr, w, h = _frames(os.path.join(MEDIA, src), t0, t1)
    dets = []
    for cp in CASCADES:
        cc = cv2.CascadeClassifier(cp)
        for g in fr:
            g = cv2.equalizeHist(g)
            f = cc.detectMultiScale(g, scaleFactor=1.08, minNeighbors=6, minSize=(int(h * 0.12), int(h * 0.12)))
            if len(f):
                x, y, fw, fh = max(f, key=lambda r: r[2] * r[3])
                dets.append(((x + fw / 2) / w, (y + fh / 2) / h, fh / h))
        if len(dets) >= max(3, len(fr) // 4):
            break
    if len(dets) < 3:
        return None
    d = np.array(dets)
    med = np.median(d, axis=0)
    keep = (np.abs(d[:, 2] - med[2]) < 0.25 * med[2]) & (np.abs(d[:, 0] - med[0]) < 0.6 * med[2]) & \
           (np.abs(d[:, 1] - med[1]) < 0.6 * med[2])
    if keep.sum() < 3:
        return None
    m = np.median(d[keep], axis=0)
    return dict(cx=round(float(m[0]), 4), cy=round(float(m[1]), 4), h=round(float(m[2]), 4),
                n=int(keep.sum()), of=len(fr))


def get(src, t0, t1):
    key = f'{src}@{t0:.2f}-{t1:.2f}'
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    if key not in cache:
        cache[key] = measure(src, t0, t1)
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump(cache, open(CACHE, 'w'), indent=1)
    return cache[key]
