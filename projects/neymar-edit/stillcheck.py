#!/usr/bin/env python3
"""Standbild-Prüfung an den gerenderten Chunks: längster Lauf identischer Frames am
Shot-Anfang gegen das, was Quell-fps und Zeitlupe erklären.
    python3 stillcheck.py a-b"""
import json, math, os, subprocess, sys
import numpy as np
import render
shots = render.resolve()
lo, hi = map(int, sys.argv[1].split('-'))
for s in shots:
    if not lo <= s['i'] <= hi or s['kind'] != 'single':
        continue
    c = s['clips'][0]
    ch = f"{render.CHUNKS}/shot_{s['i']:03d}.mp4"
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', ch, '-vf', 'scale=160:90', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.int16)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    run = 0
    for v in d[:40]:
        if v < 0.6: run += 1
        else: break
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                            'stream=r_frame_rate', '-of', 'json', os.path.join(render.MEDIA, c['src'])]))
    a, b = j['streams'][0]['r_frame_rate'].split('/')
    fps = float(a) / float(b)
    if fps > 55: fps = 50
    exp = math.ceil(50 / (fps * c['speed'])) - 1
    flag = '  <-- STAND' if run > exp + 1 else ''
    print(f"#{s['i']:2d} k{s['k'][0]:3d} {c['src']:24s} run {run:2d} (erwartet <= {exp}){flag}")
