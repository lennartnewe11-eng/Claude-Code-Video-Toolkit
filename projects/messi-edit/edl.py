"""EDL v3: jeder Shot in Ausgabe-Beats k (k = Song-Beat - 384, siehe timeline.py).

Der Song läuft an einem Stück. Die Dramaturgie folgt seinen Abschnitten:

  k   0– 64  Breakdown    Aufstieg: Rosario, La Masia, Barça 2005–2017    faded → warm
  k  64– 72  Build        Niederlagen 2016–2021                           cold / bleak
  k  72–128  Build        WM-Finale 2014 ↔ 2022, im Wechsel geschnitten   cold ↔ warm
  k 128–192  Refrain      Weltmeister                                     warm
  k 192–228  Refrain      MetLife 2026                                    cold / bleak
  k 228–263  Outro        Gesichter über die Jahre                        mono
  k 263–     Coda         Nachhall, Abgang in den Tunnel, Titel

2014 ↔ 2022: harte Schnitte hin und her, nie beide gleichzeitig — bis auf den
Schluss (wie in v2): bei Montiels Anlauf steht 2014 noch einmal daneben und
wird von 2022 aus dem Bild geschoben, der Jubel landet auf dem Refrain.
Ohne Jahreszahlen trägt das Band die Unterscheidung: 2014 immer im Scope-Band
und kalt, 2022 immer im Vollbild und warm. Der Wechsel wird schneller:
Vierer (Tunnel, Einlauf), Zweier (Hymne bis letzte Chance), Einer (Schlusspfiff
gegen Elfmeterschießen).

Gesichter: gleiche Höhe, gleicher Ort, Band steht still — nur das Gesicht altert.
Keine Jahreszahlen im ganzen Video.
"""

F22 = 'src/final22_hl.mp4'
GET = 'src/getafe07.mkv'
WEM = 'src/wembley11.mkv'
BIL = 'src/bilbao15.mp4'
UCL = 'src/ucl09_2h.mp4'
LMG = 'src/lamasia.mp4'
BDO = 'src/ballondor09_11.mp4'
KID = 'cuts/robinson_kid.mp4'
PSG = 'src/psg17_end.mp4'


def C(src, t, grade=None, focus=(0.5, 0.5), zoom=1.0, speed=1.0, label=None, out=None, auto=False, face=None):
    """Clip-Referenz. out: spätester Quellpunkt (Tempo wird passend gesetzt).
    auto: Ausschnitt per Gesichtserkennung.  face: Gesicht von Hand (cx, cy, h)."""
    f = dict(cx=face[0], cy=face[1], h=face[2], manual=True) if face else None
    return dict(src=src, t=t, grade=grade, focus=focus, zoom=zoom, speed=speed, label=label, out=out,
                auto=auto, face=f)


def S(k0, k1, clip, band, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='single', clips=[clip], band=band, grade=grade, fx=list(fx), label=label)


def SPLIT(k0, k1, clips, band, fx=()):
    return dict(k=(k0, k1), kind='split', clips=clips, band=band, grade=None, fx=list(fx), label=None)


def PAR(k0, k1, left, right, split, keys=(), fx=()):
    """Parallelmontage: split = Breitenanteil links (2014); keys = weitere (k, Anteil)."""
    return dict(k=(k0, k1), kind='split', clips=[left, right], band='full', grade=None, fx=list(fx),
                label=None, split=split, keys=list(keys))


def GRID(k0, k1, clips, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='grid', clips=clips, band='full', grade=grade, fx=list(fx), label=label)


def FACE(k0, k1, clip, label=None):
    return dict(k=(k0, k1), kind='face', clips=[clip], band='square', grade='mono', fx=[], label=label)


def CODA(k0, clip, title, sub, fade_at, title_at):
    return dict(k=(k0, None), kind='coda', clips=[clip], band='scope', grade='bleak', fx=[], label=None,
                title=title, sub=sub, fade_at=fade_at, title_at=title_at)


def A14(k0, k1, src, t, grade='cold', fx=('grain',), **kw):
    """2014: immer Scope-Band, kalt. Das Band allein sagt, welches Finale läuft."""
    return S(k0, k1, C(src, t, **kw), 'scope', grade, fx)


def B22(k0, k1, src, t, grade='warm', fx=(), **kw):
    """2022: immer Vollbild, warm."""
    return S(k0, k1, C(src, t, **kw), 'full', grade, fx)


SHOTS = [
    # ── Aufstieg (Breakdown) ─────────────────────────────────────────────────
    S(0, 4, C(BDO, 2.2), 'box43', 'faded', ['grain_heavy', 'drift'], 'ROSARIO'),
    S(4, 8, C(LMG, 62.6), 'square', 'faded', ['grain_heavy', 'drift']),
    S(8, 12, C(LMG, 51.5, focus=(0.5, 0.45)), 'box43', 'faded', ['grain', 'push'], 'BARCELONA'),
    S(12, 16, C(LMG, 193.0, speed=1.35), 'wide', 'faded', ['grain', 'zoom_in']),
    S(16, 18, C(LMG, 200.0, focus=(0.45, 0.55), zoom=1.15), 'full', 'warm', ['open', 'thump', 'punch', 'grain']),
    GRID(18, 26, [C(GET, 43.0, zoom=1.15), C(GET, 52.2, zoom=1.1), C(GET, 55.6, zoom=1.1)], 'warm', ['grain']),
    S(26, 28, C(GET, 61.3), 'scope', 'warm', ['punch', 'grain']),
    S(28, 30, C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.35), 'box43', 'warm', ['punch', 'grain_heavy']),
    S(30, 32, C(UCL, 1639.2, focus=(0.45, 0.55), zoom=1.25), 'wide', 'warm', ['punch', 'grain']),
    S(32, 34, C(WEM, 68.9), 'full', 'warm', ['punch']),
    S(34, 35, C(WEM, 73.9, focus=(0.4, 0.4)), 'square', 'warm', ['rgbhit']),
    S(35, 36, C(WEM, 81.9, focus=(0.45, 0.4)), 'wide', 'warm', ['punch']),
    S(36, 38, C(BDO, 41.0, focus=(0.32, 0.5), zoom=1.15), 'scope', 'warm', ['push', 'grain']),
    S(38, 39, C('cuts/b15_drib.mp4', 13.3, zoom=1.2), 'full', 'warm', ['thump']),
    S(39, 40, C('cuts/b15_drib.mp4', 14.9, zoom=1.2), 'scope', 'warm', []),
    S(40, 42, C('cuts/b15_drib.mp4', 21.2, zoom=1.15), 'wide', 'warm', ['zoom_in']),
    S(42, 44, C('cuts/b15_drib.mp4', 22.2, zoom=1.1), 'square', 'warm', ['punch']),
    S(44, 45, C(BIL, 71.0, zoom=1.1), 'full', 'warm', ['grain']),
    S(45, 46, C(BIL, 72.4, zoom=1.1), 'scope', 'warm', []),
    S(46, 47, C(BIL, 74.6, zoom=1.1), 'wide', 'warm', []),
    S(47, 48, C(BIL, 76.8, zoom=1.1), 'full', 'warm', ['rgbhit']),
    S(48, 50, C(BIL, 88.4, zoom=1.1), 'scope', 'warm', ['punch']),
    S(50, 52, C(BIL, 96.4, zoom=1.1), 'full', 'warm', ['punch', 'grain']),
    S(52, 56, C('cuts/m17_celeb.mp4', 5.4, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['push', 'thump', 'grain']),
    S(56, 60, C(PSG, 229.0, focus=(0.4, 0.4), zoom=1.1), 'square', 'warm', ['push']),
    S(60, 64, C(PSG, 147.5, focus=(0.5, 0.45), zoom=1.1), 'full', 'warm', ['grain', 'dip']),

    # ── Niederlagen (Build) ──────────────────────────────────────────────────
    S(64, 66, C('cuts/r16_pen.mp4', 6.6, focus=(0.33, 0.42), zoom=1.45), 'wide', 'cold', ['thump', 'grain']),
    S(66, 68, C('cuts/r16_cry.mp4', 2.8, focus=(0.42, 0.42), zoom=1.4), 'square', 'bleak', ['grain']),
    S(68, 70, C('cuts/anf19.mp4', 6.0, focus=(0.47, 0.4), zoom=1.15), 'scope', 'cold', ['grain']),
    S(70, 72, C('cuts/n21_cry_a.mp4', 1.7, focus=(0.55, 0.42), zoom=1.3), 'wide', 'bleak', ['grain', 'dip']),

    # ── WM-Finale 2014 ↔ 2022 (Build), im Wechsel ────────────────────────────
    # Vierer: Tunnel, Einlauf am Pokal vorbei
    A14(72, 76, 'cuts/w14_tunnel.mp4', 46.5, auto=True, fx=('grain', 'push')),
    B22(76, 80, 'cuts/w22_tunnel.mp4', 9.0, auto=True, fx=('push',)),
    A14(80, 84, 'cuts/w14_walkout.mp4', 11.0, focus=(0.45, 0.42), zoom=1.35),
    B22(84, 88, 'cuts/w22_walkout.mp4', 31.5, focus=(0.35, 0.5)),
    # Zweier: Hymne, Chance, Reaktion, Gegentor, letzte Chance
    A14(88, 90, 'cuts/w14_anthem.mp4', 11.0, auto=True),
    B22(90, 92, 'cuts/w22_anthem.mp4', 6.5, auto=True),
    A14(92, 94, 'cuts/w14_chance.mp4', 22.6, focus=(0.5, 0.5)),
    B22(94, 96, F22, 69.6, focus=(0.45, 0.5), fx=('punch',)),
    A14(96, 98, 'cuts/w14_chance.mp4', 5.2, auto=True),
    B22(98, 100, F22, 59.85, speed=0.65, auto=True),
    A14(100, 102, 'cuts/w14_goetze.mp4', 14.3, 'bleak', focus=(0.42, 0.5), zoom=1.2, fx=('thump', 'grain')),
    B22(102, 104, F22, 85.4, 'neutral', focus=(0.5, 0.45), fx=('thump',)),
    A14(104, 106, 'cuts/w14_fk.mp4', 9.8, 'bleak', auto=True),
    B22(106, 108, F22, 92.9, focus=(0.45, 0.5), fx=('punch',)),
    # Schlusspfiff 2014 gegen Elfmeterschießen 2022
    A14(108, 110, 'cuts/w14_whistle.mp4', 7.5, 'bleak', focus=(0.5, 0.45)),
    B22(110, 112, 'cuts/w22_pen.mp4', 6.8, auto=True),
    # Einer-Traube
    A14(112, 113, 'cuts/w14_whistle.mp4', 35.2, 'bleak', auto=True),
    B22(113, 114, 'cuts/w22_pen.mp4', 39.3, focus=(0.5, 0.5), fx=('thump',)),
    A14(114, 115, 'cuts/w14_whistle.mp4', 23.0, 'bleak', focus=(0.5, 0.5)),
    B22(115, 116, 'cuts/w22_pen.mp4', 29.0, auto=True),
    A14(116, 117, 'cuts/w14_react.mp4', 11.3, 'bleak', auto=True),
    B22(117, 118, F22, 101.5, focus=(0.5, 0.5), fx=('thump',)),
    A14(118, 119, 'cuts/c14_ref.mp4', 2.1, 'bleak', auto=True),
    B22(119, 120, 'cuts/w22_pen.mp4', 41.0, focus=(0.5, 0.45)),
    # Schluss wie v2: 2014 steht daneben, 2022 schiebt es aus dem Bild
    PAR(120, 128, C('cuts/c14_alone.mp4', 4.2, 'bleak', (0.5, 0.45), 1.2),
        C(F22, 'MONTIEL', 'cold', (0.42, 0.47), 1.3), 0.5,
        keys=[(123, 0.42), (126, 0.34), (128, 0.0)], fx=['grain']),

    # ── Weltmeister (Refrain) ────────────────────────────────────────────────
    S(128, 130, C(F22, 114.3, focus=(0.5, 0.42), zoom=1.05), 'full', 'warm', ['flash', 'punch', 'grain']),
    S(130, 132, C(F22, 116.6, focus=(0.5, 0.45)), 'wide', 'warm', ['punch']),
    # Golden Ball und Pokal, ebenfalls im Wechsel
    A14(132, 134, 'cuts/c14_golden.mp4', 5.2, focus=(0.28, 0.5), zoom=1.1, fx=('push',)),
    B22(134, 136, 'cuts/c22_gball.mp4', 3.2, focus=(0.5, 0.42), fx=('push',)),
    A14(136, 138, 'cuts/c14_walk.mp4', 4.0, focus=(0.5, 0.5), zoom=1.1, fx=('push',)),
    B22(138, 140, 'cuts/c22_kiss.mp4', 8.0, focus=(0.47, 0.45), fx=('push',)),
    S(140, 142, C('cuts/c22_bisht.mp4', 0.5, focus=(0.44, 0.47), zoom=1.2), 'wide', 'warm', ['punch']),
    S(142, 144, C('cuts/c22_trophy.mp4', 4.5, focus=(0.55, 0.45), zoom=1.15), 'square', 'warm', ['punch']),
    S(144, 146, C('cuts/c22_trophy.mp4', 11.0, focus=(0.45, 0.5), zoom=1.2), 'full', 'warm', ['thump']),
    S(146, 148, C('cuts/c22_lift.mp4', 6.3, focus=(0.46, 0.5), zoom=1.18), 'scope', 'warm', ['punch', 'grain']),
    S(148, 149, C('cuts/c22_lift.mp4', 13.1, focus=(0.46, 0.5), zoom=1.18), 'full', 'warm', ['rgbhit']),
    S(149, 150, C('cuts/c22_lift.mp4', 14.3, zoom=1.1), 'square', 'warm', []),
    S(150, 151, C('cuts/c22_lift.mp4', 21.1, focus=(0.46, 0.5), zoom=1.18), 'wide', 'warm', []),
    S(151, 152, C('cuts/c22_lift.mp4', 22.2, focus=(0.46, 0.5), zoom=1.18), 'full', 'warm', ['rgbhit']),
    S(152, 156, C('cuts/c22_lift.mp4', 9.6, focus=(0.46, 0.5), zoom=1.15), 'scope', 'warm', ['zoom_in', 'grain']),
    # Vermächtnis: sechs Szenen laufen durch, auf jedem Beat springt die Anordnung
    GRID(156, 172, [C('cuts/b15_drib.mp4', 13.0, zoom=1.2), C(BIL, 70.6, zoom=1.1), C(WEM, 66.4),
                    C(GET, 44.0, zoom=1.1), C('cuts/c21_raise.mp4', 6.0, focus=(0.45, 0.4), zoom=1.3),
                    C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.3)], 'warm', ['grain']),
    S(172, 176, C('cuts/c22_kiss.mp4', 9.5, focus=(0.47, 0.42)), 'portrait', 'warm', ['push']),
    S(176, 180, C('cuts/c22_gball.mp4', 3.4, focus=(0.46, 0.3), zoom=1.32), 'full', 'warm', ['thump', 'grain']),
    S(180, 184, C('cuts/c22_lift.mp4', 1.0, focus=(0.46, 0.5), zoom=1.18), 'wide', 'warm', ['punch', 'grain']),
    S(184, 188, C('cuts/c22_lift.mp4', 16.8, focus=(0.46, 0.5), zoom=1.15), 'scope', 'warm', ['zoom_in']),
    S(188, 192, C('cuts/c22_kiss.mp4', 13.8, focus=(0.5, 0.55), zoom=1.1), 'slit', 'warm', ['drift', 'dip']),

    # ── MetLife 2026 (Refrain) ───────────────────────────────────────────────
    S(192, 196, C('cuts/c26_back.mp4', 6.0, focus=(0.42, 0.5)), 'scope', 'cold', ['grain', 'push']),
    S(196, 198, C('cuts/c26_medal.mp4', 8.0, focus=(0.55, 0.45), zoom=1.2), 'wide', 'cold', ['grain']),
    S(198, 204, C('cuts/c26_trophy.mp4', 10.5, focus=(0.45, 0.45)), 'full', 'cold', ['push', 'grain']),
    S(204, 206, C('cuts/c26_spain.mp4', 9.0, zoom=1.1), 'scope', 'cold', ['grain']),
    S(206, 208, C('cuts/c26_spain.mp4', 3.5, focus=(0.4, 0.45), zoom=1.3), 'wide', 'cold', ['grain']),
    SPLIT(208, 212, [C('cuts/r16_cry.mp4', 12.3, 'bleak', (0.42, 0.42), 1.4),
                     C('cuts/c26_tears.mp4', 1.0, 'bleak', (0.55, 0.45))], 'full', ['push']),
    S(212, 218, C('cuts/c26_tears.mp4', 17.8, focus=(0.5, 0.45), zoom=1.1), 'square', 'bleak', ['push', 'grain']),
    S(218, 220, C('cuts/c26_back.mp4', 10.9, focus=(0.4, 0.45), zoom=1.1), 'scope', 'cold', ['grain']),
    S(220, 224, C('cuts/c26_spain.mp4', 21.8, focus=(0.45, 0.45), zoom=1.1), 'wide', 'cold', ['grain']),
    SPLIT(224, 228, [C('cuts/c14_walk.mp4', 4.5, 'cold', (0.5, 0.5), 1.1),
                     C('cuts/c22_kiss.mp4', 9.0, 'warm', (0.47, 0.45)),
                     C('cuts/c26_trophy.mp4', 12.0, 'cold', (0.5, 0.45))], 'full', ['push', 'dip']),

    # ── Gesichter über die Jahre (Outro) ─────────────────────────────────────
    FACE(228, 230, C(KID, 20.0)),
    FACE(230, 232, C(KID, 17.5)),
    FACE(232, 234, C(KID, 15.0)),
    FACE(234, 236, C(KID, 12.0, face=(0.40, 0.52, 0.85))),
    FACE(236, 238, C(KID, 3.05, speed=0.45, face=(0.19, 0.52, 0.45))),
    FACE(238, 240, C(BDO, 46.8)),
    FACE(240, 242, C(WEM, 74.3, face=(0.293, 0.482, 0.286))),
    FACE(242, 244, C('cuts/w14_anthem.mp4', 12.0)),
    FACE(244, 246, C('cuts/r16_after.mp4', 3.4)),
    FACE(246, 248, C('cuts/anf19.mp4', 6.0)),
    FACE(248, 250, C('cuts/n21_cry_b.mp4', 5.6)),
    FACE(250, 252, C('cuts/sau22.mp4', 6.0)),
    FACE(252, 256, C('cuts/c26_trophy.mp4', 10.5)),
    FACE(256, 263, C('cuts/c26_tears.mp4', 4.0, face=(0.62, 0.55, 0.85))),

    # ── Coda: der letzte Schlag klingt aus, Abgang in den Tunnel, Titel ──────
    CODA(263, C('cuts/c26_spain.mp4', 24.9, focus=(0.5, 0.5), speed=0.5),
         'LIONEL MESSI', 'GRACIAS, LEO', fade_at=3.7, title_at=4.6),
]
