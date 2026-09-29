#!/usr/bin/env python3
"""Contact Sheet aus den gerenderten Chunks: je Shot ein Frame bei 15 % und 70 %.

    python3 contact.py [a-b] [out.jpg]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

import render

HERE = os.path.dirname(os.path.abspath(__file__))
shots = render.resolve()
lo, hi = (map(int, sys.argv[1].split('-')) if len(sys.argv) > 1 else (0, len(shots) - 1))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'build', 'contact_sheet.jpg')
sel = [s for s in shots if lo <= s['i'] <= hi]
TW, TH = 288, 162
cols = 8
tiles = []
for s in sel:
    ch = os.path.join(render.CHUNKS, f"shot_{s['i']:03d}.mp4")
    n = s['f1'] - s['f0']
    for p in (0.15, 0.7):
        fn = '/tmp/_cs.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', ch, '-vf', f"select=eq(n\\,{int(n * p)}),scale={TW}:{TH}",
                        '-frames:v', '1', fn])
        im = Image.open(fn).convert('RGB') if os.path.exists(fn) else Image.new('RGB', (TW, TH))
        tiles.append((s, p, im.copy()))
        os.remove(fn)
rows = (len(tiles) + cols - 1) // cols
S = Image.new('RGB', (cols * TW, rows * (TH + 16)), (12, 12, 12))
d = ImageDraw.Draw(S)
for i, (s, p, im) in enumerate(tiles):
    x, y = (i % cols) * TW, (i // cols) * (TH + 16)
    S.paste(im, (x, y + 16))
    k0, k1 = s['k']
    d.text((x + 3, y + 2), f"#{s['i']} k{k0}-{k1} {s['band']} {s['grade'] or ''} {'.' if p < .5 else '..'}",
           fill=(255, 220, 0))
S.save(out, quality=88)
print(out, len(tiles))
