"""EDL: jeder Shot in Ausgabe-Beats k (siehe timeline.py).

Dramaturgie in fünf Teilen, jeder an einen Song-Abschnitt gebunden:

  k   0– 16  Intro (Song 16–32)     Kindheit, erstes Tor            faded, 4:3-Band
  k  16– 64  Drop A (Song 32–80)    Barça 2005–2017, Aufstieg       warm
  k  64– 96  Teil B (Song 96–128)   Niederlagen 2014–2021           cold / bleak
  k  96–128  Build (Song 480–512)   Copa 2021, WM 2022 bis Montiel  warm → bleak
  k 128–192  Refrain (Song 512–576) Weltmeister, 2014 vs. 2022      warm
  k 192–231  Outro (Song 608–647)   MetLife 2026, Abgang            cold / bleak

Gegenüberstellung: Niederlage und Erfolg stehen als Diptychon nebeneinander
(2014 Golden Ball | 2022 Golden Ball, 2014 Gang | 2022 Kuss, 2016 MetLife |
2026 MetLife) und am Ende als Triptychon der drei Begegnungen mit dem Pokal.
Die Grades tragen den Umschlag, nicht neue Effekte.
"""

# Quellen (relativ zu media/)
F22 = 'src/final22_hl.mp4'
GET = 'src/getafe07.mkv'
WEM = 'src/wembley11.mkv'
BIL = 'src/bilbao15.mp4'
UCL = 'src/ucl09_2h.mp4'
LMG = 'src/lamasia.mp4'
BDO = 'src/ballondor09_11.mp4'
PSG = 'src/psg17_end.mp4'


def C(src, t, grade=None, focus=(0.5, 0.5), zoom=1.0, speed=1.0, label=None, out=None):
    """Clip-Referenz. out: spätester Quellpunkt; Tempo wird dann passend gesetzt."""
    return dict(src=src, t=t, grade=grade, focus=focus, zoom=zoom, speed=speed, label=label, out=out)


def S(k0, k1, clip, band, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='single', clips=[clip], band=band, grade=grade, fx=list(fx),
                label=label)


def SPLIT(k0, k1, clips, band, fx=()):
    return dict(k=(k0, k1), kind='split', clips=clips, band=band, grade=None, fx=list(fx), label=None)


def GRID(k0, k1, clips, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='grid', clips=clips, band='full', grade=grade, fx=list(fx), label=label)


def CARD(k0, k1, title, sub):
    return dict(k=(k0, k1), kind='card', clips=[], band='full', grade=None, fx=[], label=None,
                title=title, sub=sub)


# Fokuspunkte (x, y relativ zum Quellbild) aus den Kontaktbögen abgelesen.
M = (0.50, 0.42)

SHOTS = [
    # ── Intro: Kindheit, La Masia, erstes Tor ────────────────────────────────
    S(0, 4, C(BDO, 2.2), 'box43', 'faded', ['grain_heavy', 'drift'], '1995'),
    S(4, 8, C(LMG, 62.6), 'square', 'faded', ['grain_heavy', 'drift']),
    S(8, 12, C(LMG, 51.5, focus=(0.5, 0.45)), 'box43', 'faded', ['grain', 'push']),
    S(12, 16, C(LMG, 193.0, speed=1.35), 'wide', 'faded', ['grain', 'zoom_in'], '2005'),

    # ── Drop A: Barça ────────────────────────────────────────────────────────
    S(16, 18, C(LMG, 200.0, focus=(0.45, 0.55), zoom=1.15), 'full', 'warm', ['open', 'thump', 'punch', 'grain']),
    GRID(18, 26, [C(GET, 43.0, zoom=1.15), C(GET, 52.2, zoom=1.1), C(GET, 55.6, zoom=1.1)], 'warm',
         ['grain'], '2007'),
    S(26, 28, C(GET, 61.3), 'scope', 'warm', ['punch', 'grain']),
    S(28, 30, C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.35), 'box43', 'warm', ['punch', 'grain_heavy'], '2009'),
    S(30, 32, C(UCL, 1639.2, focus=(0.45, 0.55), zoom=1.25), 'wide', 'warm', ['punch', 'grain']),
    S(32, 34, C(WEM, 68.9), 'full', 'warm', ['punch'], '2011'),
    S(34, 35, C(WEM, 70.9), 'scope', 'warm', ['thump']),
    S(35, 36, C(WEM, 73.9, focus=(0.4, 0.4)), 'square', 'warm', ['punch']),
    S(36, 38, C(WEM, 81.9, focus=(0.45, 0.4)), 'full', 'warm', ['rgbhit', 'grain']),
    S(38, 40, C(WEM, 27.2, focus=(0.42, 0.35)), 'portrait', 'warm', ['punch']),
    S(40, 42, C('cuts/b15_drib.mp4', 13.3, zoom=1.2), 'full', 'warm', ['punch', 'grain'], '2015'),
    S(42, 43, C('cuts/b15_drib.mp4', 14.9, zoom=1.2), 'wide', 'warm', ['thump']),
    S(43, 44, C('cuts/b15_drib.mp4', 16.3, zoom=1.2), 'scope', 'warm', ['punch']),
    S(44, 46, C('cuts/b15_drib.mp4', 21.2, zoom=1.15), 'full', 'warm', ['zoom_in']),
    S(46, 48, C('cuts/b15_drib.mp4', 22.2, zoom=1.1), 'square', 'warm', ['punch']),
    S(48, 49, C(BIL, 71.0, zoom=1.1), 'full', 'warm', ['grain']),
    S(49, 50, C(BIL, 72.4, zoom=1.1), 'scope', 'warm', []),
    S(50, 51, C(BIL, 74.6, zoom=1.1), 'wide', 'warm', []),
    S(51, 52, C(BIL, 76.8, zoom=1.1), 'full', 'warm', ['rgbhit']),
    S(52, 54, C(BIL, 88.4, zoom=1.1), 'scope', 'warm', ['punch']),
    S(54, 56, C(BIL, 96.4, zoom=1.1), 'full', 'warm', ['punch', 'grain']),
    S(56, 60, C('cuts/m17_celeb.mp4', 5.4, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm',
      ['push', 'thump', 'grain'], '2017'),
    S(60, 62, C(PSG, 229.0, focus=(0.4, 0.4), zoom=1.1), 'square', 'warm', ['punch']),
    S(62, 64, C(PSG, 147.5, focus=(0.5, 0.45), zoom=1.1), 'full', 'warm', ['grain', 'dip']),

    # ── Teil B: Niederlagen ──────────────────────────────────────────────────
    S(64, 66, C('cuts/c14_ref.mp4', 2.1, focus=(0.47, 0.42), zoom=1.1), 'scope', 'cold',
      ['grain', 'push'], '2014'),
    S(66, 68, C('cuts/c14_alone.mp4', 4.2, focus=(0.5, 0.45), zoom=1.2), 'wide', 'cold', ['grain']),
    S(68, 72, C('cuts/c14_golden.mp4', 5.0, focus=(0.45, 0.45)), 'portrait', 'cold', ['push', 'grain']),
    S(72, 76, C('cuts/c14_pitch.mp4', 17.4, focus=(0.62, 0.45)), 'scope', 'bleak', ['drift', 'grain']),
    S(76, 78, C('cuts/r16_pen.mp4', 6.6, focus=(0.33, 0.42), zoom=1.45), 'wide', 'cold',
      ['punch', 'grain'], '2016'),
    S(78, 80, C('cuts/r16_cry.mp4', 2.8, focus=(0.42, 0.42), zoom=1.4), 'square', 'bleak', ['grain']),
    S(80, 82, C('cuts/r16_cry.mp4', 12.3, focus=(0.42, 0.42), zoom=1.4), 'scope', 'cold', ['grain']),
    S(82, 84, C('cuts/r16_after.mp4', 3.4, focus=(0.45, 0.42), zoom=1.45), 'wide', 'cold', ['grain']),
    S(84, 86, C('cuts/anf19.mp4', 6.0, focus=(0.47, 0.4), zoom=1.15), 'full', 'cold', ['grain'], '2019'),
    S(86, 88, C('cuts/n21_cry_a.mp4', 1.7, focus=(0.55, 0.42), zoom=1.3), 'scope', 'bleak',
      ['grain'], '2021'),
    S(88, 92, C('cuts/n21_cry_b.mp4', 5.6, focus=(0.5, 0.45), zoom=1.05), 'square', 'bleak',
      ['push', 'grain']),
    S(92, 96, C('cuts/c14_walk.mp4', 3.5, focus=(0.5, 0.5), zoom=1.15), 'slit', 'cold',
      ['drift', 'grain_heavy', 'close']),

    # ── Build: Copa 2021, Saudi-Arabien, Finale 2022 ─────────────────────────
    S(96, 98, C('cuts/c21_pile.mp4', 3.5, zoom=1.15, focus=(0.5, 0.45)), 'full', 'warm',
      ['open', 'punch', 'grain'], '2021'),
    S(98, 100, C('cuts/c21_raise.mp4', 6.0, focus=(0.45, 0.4), zoom=1.3), 'wide', 'warm', ['punch']),
    S(100, 102, C('cuts/c21_smile.mp4', 4.4, focus=(0.38, 0.55), zoom=1.2), 'square', 'warm', ['punch']),
    S(102, 104, C('cuts/c21_raise.mp4', 30.6, focus=(0.5, 0.4), zoom=1.3), 'scope', 'warm', ['thump']),
    S(104, 106, C('cuts/sau22.mp4', 6.0, focus=(0.5, 0.42)), 'portrait', 'cold', ['grain'], '2022'),
    S(106, 108, C(F22, 55.0, zoom=1.1), 'full', 'warm', ['punch']),
    S(108, 110, C(F22, 59.6, focus=(0.5, 0.42)), 'square', 'warm', ['punch']),
    S(110, 112, C(F22, 85.4, focus=(0.5, 0.45)), 'scope', 'cold', ['rgbhit']),
    S(112, 114, C(F22, 49.5, focus=(0.5, 0.45)), 'wide', 'cold', ['grain']),
    S(114, 115, C(F22, 92.9), 'full', 'neutral', ['thump']),
    S(115, 116, C(F22, 101.5, zoom=1.1), 'square', 'neutral', ['thump']),
    # Geister früherer Finals, je ein Beat
    S(116, 117, C('cuts/c14_ref.mp4', 2.0, focus=(0.47, 0.42), zoom=1.2), 'slit', 'bleak', ['grain_heavy']),
    S(117, 118, C('cuts/r16_pen.mp4', 7.0, focus=(0.33, 0.42), zoom=1.5), 'scope', 'bleak', ['grain_heavy']),
    S(118, 119, C('cuts/anf19.mp4', 6.6, focus=(0.47, 0.4), zoom=1.2), 'slit', 'bleak', ['grain_heavy']),
    # Montiel: Bild und Stadionton laufen synchron in den Aussetzer (audio.py)
    S(119, 128, C(F22, 'MONTIEL', focus=(0.42, 0.47), zoom=1.55), 'scope', 'bleak',
      ['push', 'grain_heavy', 'squeeze']),

    # ── Refrain: Weltmeister ─────────────────────────────────────────────────
    S(128, 130, C(F22, 114.3, focus=(0.5, 0.42), zoom=1.05), 'full', 'warm', ['flash', 'punch', 'grain']),
    S(130, 132, C(F22, 116.6, focus=(0.5, 0.45)), 'wide', 'warm', ['punch']),
    SPLIT(132, 136, [C('cuts/c14_golden.mp4', 5.2, 'cold', (0.45, 0.45), label='2014'),
                     C('cuts/c22_gball.mp4', 3.2, 'warm', (0.5, 0.42), label='2022')], 'full', ['push']),
    SPLIT(136, 140, [C('cuts/c14_walk.mp4', 4.0, 'cold', (0.5, 0.5), 1.1, label='2014'),
                     C('cuts/c22_kiss.mp4', 8.0, 'warm', (0.47, 0.45), label='2022')], 'scope', ['push']),
    S(140, 142, C('cuts/c22_bisht.mp4', 0.5, focus=(0.45, 0.45), zoom=1.15), 'wide', 'warm', ['punch']),
    S(142, 144, C('cuts/c22_trophy.mp4', 4.5, focus=(0.55, 0.45), zoom=1.15), 'square', 'warm', ['punch']),
    S(144, 146, C('cuts/c22_trophy.mp4', 11.0, focus=(0.5, 0.5), zoom=1.2), 'full', 'warm', ['thump']),
    S(146, 148, C('cuts/c22_lift.mp4', 6.3, zoom=1.1), 'scope', 'warm', ['punch', 'grain']),
    S(148, 149, C('cuts/c22_lift.mp4', 13.1, zoom=1.1), 'full', 'warm', ['rgbhit']),
    S(149, 150, C('cuts/c22_lift.mp4', 14.3, zoom=1.1), 'square', 'warm', []),
    S(150, 151, C('cuts/c22_lift.mp4', 21.1, zoom=1.1), 'wide', 'warm', []),
    S(151, 152, C('cuts/c22_lift.mp4', 22.2, zoom=1.1), 'full', 'warm', ['rgbhit']),
    S(152, 156, C('cuts/c22_lift.mp4', 9.6, zoom=1.05), 'scope', 'warm', ['zoom_in', 'grain']),
    # Vermächtnis-Wand: sechs Szenen laufen durch, auf jedem Beat springt nur die Anordnung
    GRID(156, 172, [C('cuts/b15_drib.mp4', 13.0, zoom=1.2), C(BIL, 70.6, zoom=1.1), C(WEM, 66.4),
                    C(GET, 44.0, zoom=1.1), C('cuts/m17_celeb.mp4', 5.4, focus=(0.5, 0.4)),
                    C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.3)], 'warm', ['grain']),
    S(172, 176, C('cuts/c22_kiss.mp4', 9.5, focus=(0.47, 0.42)), 'portrait', 'warm', ['push']),
    S(176, 180, C('cuts/c22_gball.mp4', 3.4, focus=(0.5, 0.38), zoom=1.2), 'full', 'warm', ['thump', 'grain']),
    S(180, 184, C('cuts/c22_lift.mp4', 1.0, zoom=1.1), 'wide', 'warm', ['punch', 'grain']),
    S(184, 188, C('cuts/c22_lift.mp4', 16.8), 'scope', 'warm', ['zoom_in']),
    S(188, 192, C('cuts/c22_kiss.mp4', 13.8, focus=(0.5, 0.55), zoom=1.1), 'slit', 'warm', ['drift', 'dip']),

    # ── Outro: MetLife 2026 ──────────────────────────────────────────────────
    S(192, 194, C('cuts/c26_back.mp4', 6.0, focus=(0.42, 0.5)), 'scope', 'cold', ['grain'], '2026'),
    S(194, 196, C('cuts/c26_medal.mp4', 8.0, focus=(0.55, 0.45), zoom=1.2), 'wide', 'cold', ['grain']),
    S(196, 200, C('cuts/c26_trophy.mp4', 10.5, focus=(0.45, 0.45)), 'full', 'cold', ['push', 'grain']),
    S(200, 202, C('cuts/c26_spain.mp4', 9.0, zoom=1.1), 'scope', 'cold', ['grain']),
    S(202, 204, C('cuts/c26_spain.mp4', 3.5, focus=(0.4, 0.45), zoom=1.3), 'wide', 'cold', ['grain']),
    SPLIT(204, 208, [C('cuts/r16_cry.mp4', 12.3, 'bleak', (0.42, 0.42), 1.4, label='2016'),
                     C('cuts/c26_tears.mp4', 1.0, 'bleak', (0.55, 0.45), label='2026')], 'full', ['push']),
    S(208, 212, C('cuts/c26_tears.mp4', 4.0, focus=(0.55, 0.45)), 'square', 'bleak', ['push', 'grain']),
    S(212, 214, C('cuts/c26_tears.mp4', 18.0, focus=(0.5, 0.45), zoom=1.1), 'scope', 'cold', ['grain']),
    S(214, 216, C('cuts/c26_back.mp4', 10.9, focus=(0.4, 0.45), zoom=1.1), 'wide', 'cold', ['grain']),
    SPLIT(216, 220, [C('cuts/c14_walk.mp4', 4.5, 'cold', (0.5, 0.5), 1.1, label='2014'),
                     C('cuts/c22_kiss.mp4', 9.0, 'warm', (0.47, 0.45), label='2022'),
                     C('cuts/c26_trophy.mp4', 12.0, 'cold', (0.5, 0.45), label='2026')], 'full', ['push']),
    S(220, 231, C('cuts/c26_spain.mp4', 24.9, focus=(0.5, 0.5), out=28.85), 'scope', 'cold',
      ['drift', 'grain', 'close']),
    CARD(231, None, 'LIONEL MESSI', '2004 — 2026'),
]
