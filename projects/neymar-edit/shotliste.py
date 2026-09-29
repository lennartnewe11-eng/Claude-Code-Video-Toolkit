#!/usr/bin/env python3
"""Shotliste aus der EDL erzeugen (nie von Hand pflegen — eine Doku, die driften kann, driftet).

    python3 shotliste.py > SHOTLISTE.md
"""
import os
from collections import Counter

import render
import timeline as tl

shots = render.resolve()
fx = Counter()
lengths = Counter()
for s in shots:
    fx.update(s['fx'])
    if s['k'][1] is not None:
        lengths[s['k'][1] - s['k'][0]] += 1

print('# Shotliste\n')
print(f'Automatisch aus `edl.py` erzeugt. {len(shots)} Shots, {tl.NK} Ausgabe-Beats, '
      f'{tl.TOTAL:.2f} s, {tl.NFRAMES} Frames @ {tl.FPS} fps.\n')
print('| # | Beats | Zeit | Art | Band | Grade | Quelle @ In | FX | Label |')
print('|--:|------:|-----:|-----|------|-------|-------------|----|-------|')
for s in shots:
    k0, k1 = s['k']
    src = ' / '.join(f"{os.path.basename(c['src']).rsplit('.', 1)[0]} @{c['t']:.2f}" for c in s['clips']) or '—'
    grade = s['grade'] or ' / '.join(c['grade'] or '' for c in s['clips']) or '—'
    labels = s['label'] or ' / '.join(c['label'] for c in s['clips'] if c.get('label')) or ''
    kk = f'{k0}–{k1}' if k1 is not None else f'{k0}–'
    print(f"| {s['i']} | {kk} | {s['t0']:.2f} | {s['kind']} | {s['band']} | {grade} | {src} | "
          f"{', '.join(s['fx'])} | {labels} |")
print('\n## Schnittlängen\n')
print('| Beats | Anzahl |\n|--:|--:|')
for k, n in sorted(lengths.items()):
    print(f'| {k} | {n} |')
print('\n## Effekte\n')
print('| FX | Anzahl |\n|---|--:|')
for k, n in fx.most_common():
    print(f'| `{k}` | {n} |')
