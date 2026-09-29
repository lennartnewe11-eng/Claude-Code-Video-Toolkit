"""EDL v2: jeder Shot in Ausgabe-Beats k (k = Song-Beat - 416, siehe timeline.py).

Der Song läuft an einem Stück. Die Dramaturgie folgt seinen Abschnitten:

  k   0– 32  Breakdown    Aufstieg: Rosario, La Masia, Barça 2005–2017    faded → warm
  k  32– 40  Build        Niederlagen 2016–2021                           cold / bleak
  k  40– 96  Build        Parallelmontage WM-Finale 2014 | 2022            cold | neutral
  k  96–160  Refrain      Weltmeister                                     warm
  k 160–196  Refrain      MetLife 2026                                    cold / bleak
  k 196–231  Outro        Gesichter über die Jahre                        mono
  k 231–     Coda         Nachhall, Abgang in den Tunnel, Titel

Parallelmontage: zwei Finals, Moment für Moment nebeneinander — Tunnel,
Pokal, Hymne, Chance, Gegentor, letzte Chance, Schlusspfiff. Die Clips laufen
durch; auf jedem Beat springt nur die Trennlinie (Bewegung statt Schnitt). Das
Band steht still, weil der Vergleich die Veränderung trägt. Die Trennlinie
wandert zu der Seite, die den Moment hat; bei Montiels Elfmeter schiebt 2022
das Jahr 2014 aus dem Bild, der Jubel landet auf dem Refrain.

Gesichter: gleiche Höhe, gleicher Ort, Band steht still — nur das Gesicht altert.
"""

F22 = 'src/final22_hl.mp4'
GET = 'src/getafe07.mkv'
WEM = 'src/wembley11.mkv'
BIL = 'src/bilbao15.mp4'
UCL = 'src/ucl09_2h.mp4'
LMG = 'src/lamasia.mp4'
BDO = 'src/ballondor09_11.mp4'
KID = 'cuts/robinson_kid.mp4'


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


def L14(src, t, grade='cold', **kw):
    return C(src, t, grade, label='2014', **kw)


def R22(src, t, grade='neutral', **kw):
    return C(src, t, grade, label='2022', **kw)


SHOTS = [
    # ── Aufstieg (Breakdown) ─────────────────────────────────────────────────
    S(0, 4, C(BDO, 2.2), 'box43', 'faded', ['grain_heavy', 'drift'], 'ROSARIO'),
    S(4, 8, C(LMG, 62.6), 'square', 'faded', ['grain_heavy', 'drift']),
    S(8, 10, C(LMG, 51.5, focus=(0.5, 0.45)), 'box43', 'faded', ['grain', 'push'], 'BARCELONA'),
    S(10, 12, C(LMG, 193.0), 'wide', 'faded', ['grain', 'punch'], '2005'),
    S(12, 14, C(LMG, 200.0, focus=(0.45, 0.55), zoom=1.15), 'full', 'warm', ['thump', 'punch', 'grain']),
    S(14, 16, C(GET, 52.2, zoom=1.1), 'scope', 'warm', ['punch', 'grain'], '2007'),
    S(16, 17, C(GET, 61.3), 'full', 'warm', ['thump']),
    S(17, 18, C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.35), 'box43', 'warm', ['punch', 'grain_heavy'], '2009'),
    S(18, 20, C(UCL, 1639.2, focus=(0.45, 0.55), zoom=1.25), 'wide', 'warm', ['punch', 'grain']),
    S(20, 22, C(WEM, 68.9), 'full', 'warm', ['punch'], '2011'),
    S(22, 23, C(WEM, 73.9, focus=(0.4, 0.4)), 'square', 'warm', ['rgbhit']),
    S(23, 24, C(WEM, 81.9, focus=(0.45, 0.4)), 'wide', 'warm', ['punch']),
    S(24, 25, C('cuts/b15_drib.mp4', 13.3, zoom=1.2), 'full', 'warm', ['thump'], '2015'),
    S(25, 26, C('cuts/b15_drib.mp4', 14.9, zoom=1.2), 'scope', 'warm', []),
    S(26, 28, C('cuts/b15_drib.mp4', 21.2, zoom=1.15), 'wide', 'warm', ['zoom_in']),
    S(28, 30, C(BIL, 76.8, zoom=1.1), 'full', 'warm', ['punch', 'grain']),
    S(30, 32, C('cuts/m17_celeb.mp4', 5.4, focus=(0.5, 0.4), zoom=1.1), 'scope', 'warm', ['push', 'grain'], '2017'),

    # ── Niederlagen (Build) ──────────────────────────────────────────────────
    S(32, 34, C('cuts/r16_pen.mp4', 6.6, focus=(0.33, 0.42), zoom=1.45), 'wide', 'cold', ['thump', 'grain'], '2016'),
    S(34, 36, C('cuts/r16_cry.mp4', 2.8, focus=(0.42, 0.42), zoom=1.4), 'square', 'bleak', ['grain']),
    S(36, 38, C('cuts/anf19.mp4', 6.0, focus=(0.47, 0.4), zoom=1.15), 'scope', 'cold', ['grain'], '2019'),
    S(38, 40, C('cuts/n21_cry_a.mp4', 1.7, focus=(0.55, 0.42), zoom=1.3), 'wide', 'bleak', ['grain', 'dip'], '2021'),

    # ── Parallelmontage 2014 | 2022 (Build) ──────────────────────────────────
    # Tunnel · Pokal · Hymne
    PAR(40, 44, L14('cuts/w14_tunnel.mp4', 46.5, auto=True), R22('cuts/w22_tunnel.mp4', 9.0, auto=True), 0.5),
    PAR(44, 48, L14('cuts/w14_walkout.mp4', 11.0, focus=(0.4, 0.5)),
        R22('cuts/w22_walkout.mp4', 31.5, focus=(0.35, 0.5)), 0.5),
    PAR(48, 52, L14('cuts/w14_anthem.mp4', 11.0, auto=True), R22('cuts/w22_anthem.mp4', 6.5, auto=True), 0.5),
    # Messi: vorbei | drin
    PAR(52, 56, L14('cuts/w14_chance.mp4', 22.6, focus=(0.5, 0.5)), R22(F22, 69.6, focus=(0.45, 0.5)), 0.5),
    PAR(56, 60, L14('cuts/w14_chance.mp4', 5.2, auto=True), R22(F22, 59.85, 'warm', speed=0.65, auto=True), 0.44),
    # Gegentor: Götze entscheidet | Mbappé gleicht aus
    PAR(60, 64, L14('cuts/w14_goetze.mp4', 5.0, 'bleak', focus=(0.5, 0.5)),
        R22(F22, 85.4, 'cold', focus=(0.5, 0.45)), 0.56),
    # Letzte Chance: Freistoß drüber | Martínez hält
    PAR(64, 68, L14('cuts/w14_fk.mp4', 8.9, 'bleak', auto=True), R22(F22, 92.9, focus=(0.45, 0.5)), 0.5),
    # Schlusspfiff | Elfmeterschießen bis Montiel (rechts ein durchgehender Clip)
    PAR(68, 76, L14('cuts/w14_whistle.mp4', 6.3, 'bleak', focus=(0.5, 0.45)),
        R22(F22, 'MONTIEL', focus=(0.5, 0.5)), 0.62),
    PAR(76, 84, L14('cuts/w14_whistle.mp4', 35.0, 'bleak', auto=True),
        R22(F22, 'MONTIEL', focus=(0.5, 0.5)), 0.56),
    PAR(84, 96, L14('cuts/c14_alone.mp4', 4.2, 'bleak', focus=(0.5, 0.45), zoom=1.2),
        R22(F22, 'MONTIEL', 'cold', focus=(0.42, 0.47), zoom=1.3), 0.5,
        keys=[(90, 0.42), (94, 0.34), (96, 0.0)], fx=['grain']),

    # ── Weltmeister (Refrain) ────────────────────────────────────────────────
    S(96, 98, C(F22, 114.3, focus=(0.5, 0.42), zoom=1.05), 'full', 'warm', ['flash', 'punch', 'grain']),
    S(98, 100, C(F22, 116.6, focus=(0.5, 0.45)), 'wide', 'warm', ['punch']),
    SPLIT(100, 104, [C('cuts/c14_golden.mp4', 5.2, 'cold', (0.45, 0.45), label='2014'),
                     C('cuts/c22_gball.mp4', 3.2, 'warm', (0.5, 0.42), label='2022')], 'full', ['push']),
    SPLIT(104, 108, [C('cuts/c14_walk.mp4', 4.0, 'cold', (0.5, 0.5), 1.1, label='2014'),
                     C('cuts/c22_kiss.mp4', 8.0, 'warm', (0.47, 0.45), label='2022')], 'scope', ['push']),
    S(108, 110, C('cuts/c22_bisht.mp4', 0.5, focus=(0.44, 0.47), zoom=1.2), 'wide', 'warm', ['punch']),
    S(110, 112, C('cuts/c22_trophy.mp4', 4.5, focus=(0.55, 0.45), zoom=1.15), 'square', 'warm', ['punch']),
    S(112, 114, C('cuts/c22_trophy.mp4', 11.0, focus=(0.45, 0.5), zoom=1.2), 'full', 'warm', ['thump']),
    S(114, 116, C('cuts/c22_lift.mp4', 6.3, focus=(0.46, 0.5), zoom=1.18), 'scope', 'warm', ['punch', 'grain']),
    S(116, 117, C('cuts/c22_lift.mp4', 13.1, focus=(0.46, 0.5), zoom=1.18), 'full', 'warm', ['rgbhit']),
    S(117, 118, C('cuts/c22_lift.mp4', 14.3, zoom=1.1), 'square', 'warm', []),
    S(118, 119, C('cuts/c22_lift.mp4', 21.1, focus=(0.46, 0.5), zoom=1.18), 'wide', 'warm', []),
    S(119, 120, C('cuts/c22_lift.mp4', 22.2, focus=(0.46, 0.5), zoom=1.18), 'full', 'warm', ['rgbhit']),
    S(120, 124, C('cuts/c22_lift.mp4', 9.6, focus=(0.46, 0.5), zoom=1.15), 'scope', 'warm', ['zoom_in', 'grain']),
    # Vermächtnis: sechs Szenen laufen durch, auf jedem Beat springt die Anordnung
    GRID(124, 140, [C('cuts/b15_drib.mp4', 13.0, zoom=1.2), C(BIL, 70.6, zoom=1.1), C(WEM, 66.4),
                    C(GET, 44.0, zoom=1.1), C('cuts/c21_raise.mp4', 6.0, focus=(0.45, 0.4), zoom=1.3),
                    C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.3)], 'warm', ['grain']),
    S(140, 144, C('cuts/c22_kiss.mp4', 9.5, focus=(0.47, 0.42)), 'portrait', 'warm', ['push']),
    S(144, 148, C('cuts/c22_gball.mp4', 3.4, focus=(0.46, 0.3), zoom=1.32), 'full', 'warm', ['thump', 'grain']),
    S(148, 152, C('cuts/c22_lift.mp4', 1.0, focus=(0.46, 0.5), zoom=1.18), 'wide', 'warm', ['punch', 'grain']),
    S(152, 156, C('cuts/c22_lift.mp4', 16.8, focus=(0.46, 0.5), zoom=1.15), 'scope', 'warm', ['zoom_in']),
    S(156, 160, C('cuts/c22_kiss.mp4', 13.8, focus=(0.5, 0.55), zoom=1.1), 'slit', 'warm', ['drift', 'dip']),

    # ── MetLife 2026 (Refrain) ───────────────────────────────────────────────
    S(160, 164, C('cuts/c26_back.mp4', 6.0, focus=(0.42, 0.5)), 'scope', 'cold', ['grain', 'push'], '2026'),
    S(164, 166, C('cuts/c26_medal.mp4', 8.0, focus=(0.55, 0.45), zoom=1.2), 'wide', 'cold', ['grain']),
    S(166, 172, C('cuts/c26_trophy.mp4', 10.5, focus=(0.45, 0.45)), 'full', 'cold', ['push', 'grain']),
    S(172, 174, C('cuts/c26_spain.mp4', 9.0, zoom=1.1), 'scope', 'cold', ['grain']),
    S(174, 176, C('cuts/c26_spain.mp4', 3.5, focus=(0.4, 0.45), zoom=1.3), 'wide', 'cold', ['grain']),
    SPLIT(176, 180, [C('cuts/r16_cry.mp4', 12.3, 'bleak', (0.42, 0.42), 1.4, label='2016'),
                     C('cuts/c26_tears.mp4', 1.0, 'bleak', (0.55, 0.45), label='2026')], 'full', ['push']),
    S(180, 186, C('cuts/c26_tears.mp4', 17.8, focus=(0.5, 0.45), zoom=1.1), 'square', 'bleak', ['push', 'grain']),
    S(186, 188, C('cuts/c26_back.mp4', 10.9, focus=(0.4, 0.45), zoom=1.1), 'scope', 'cold', ['grain']),
    S(188, 192, C('cuts/c26_spain.mp4', 21.8, focus=(0.45, 0.45), zoom=1.1), 'wide', 'cold', ['grain']),
    SPLIT(192, 196, [C('cuts/c14_walk.mp4', 4.5, 'cold', (0.5, 0.5), 1.1, label='2014'),
                     C('cuts/c22_kiss.mp4', 9.0, 'warm', (0.47, 0.45), label='2022'),
                     C('cuts/c26_trophy.mp4', 12.0, 'cold', (0.5, 0.45), label='2026')], 'full', ['push', 'dip']),

    # ── Gesichter über die Jahre (Outro) ─────────────────────────────────────
    FACE(196, 198, C(KID, 20.0)),
    FACE(198, 200, C(KID, 17.5)),
    FACE(200, 202, C(KID, 15.0)),
    FACE(202, 204, C(KID, 12.0, face=(0.40, 0.52, 0.85))),
    FACE(204, 206, C(KID, 3.05, speed=0.45, face=(0.19, 0.52, 0.45))),
    FACE(206, 208, C(BDO, 46.8)),
    FACE(208, 210, C(WEM, 74.3, face=(0.293, 0.482, 0.286)), '2011'),
    FACE(210, 212, C('cuts/w14_anthem.mp4', 12.0), '2014'),
    FACE(212, 214, C('cuts/r16_after.mp4', 3.4), '2016'),
    FACE(214, 216, C('cuts/anf19.mp4', 6.0), '2019'),
    FACE(216, 218, C('cuts/n21_cry_b.mp4', 5.6), '2021'),
    FACE(218, 220, C('cuts/sau22.mp4', 6.0), '2022'),
    FACE(220, 224, C('cuts/c26_trophy.mp4', 10.5), '2026'),
    FACE(224, 231, C('cuts/c26_tears.mp4', 4.0, face=(0.62, 0.55, 0.85)), '2026'),

    # ── Coda: der letzte Schlag klingt aus, Abgang in den Tunnel, Titel ──────
    CODA(231, C('cuts/c26_spain.mp4', 24.9, focus=(0.5, 0.5), speed=0.5),
         'LIONEL MESSI', 'GRACIAS, LEO', fade_at=3.7, title_at=4.6),
]
