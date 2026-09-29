#!/usr/bin/env python3
"""Review-Streifen: je Shot 4 framegenaue Bilder aus dem gerenderten Chunk.
    python3 review.py a-b out.jpg"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
import render
shots = render.resolve()
lo, hi = map(int, sys.argv[1].split('-')); out = sys.argv[2]
sel = [s for s in shots if lo <= s['i'] <= hi]
TW, TH, PER = 200, 112, 4
tiles = []
for s in sel:
    n = s['f1'] - s['f0']
    ch = os.path.join(render.CHUNKS, f"shot_{s['i']:03d}.mp4")
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', ch, '-vf', f'scale={TW}:{TH}', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, TH, TW, 3)
    for p in (0.04, 0.35, 0.65, 0.96):
        tiles.append((s, Image.fromarray(fr[min(int(n * p), len(fr) - 1)])))
cols = PER * 2
rows = (len(tiles) + cols - 1) // cols
S = Image.new('RGB', (cols * TW + 12, rows * (TH + 14)), (0, 0, 0))
d = ImageDraw.Draw(S)
for i, (s, im) in enumerate(tiles):
    c = i % cols
    x, y = c * TW + (12 if c >= PER else 0), (i // cols) * (TH + 14)
    S.paste(im, (x, y + 14))
    if i % PER == 0:
        cl = s['clips'][0] if s['clips'] else {'src': 'card', 't': 0}
        d.text((x + 2, y + 1), f"#{s['i']} k{s['k'][0]} {os.path.basename(cl['src'])[:14]} @{cl['t']:.2f}" if isinstance(cl['t'], float) else f"#{s['i']}", fill=(255, 220, 0))
S.save(out, quality=88); print(out)
