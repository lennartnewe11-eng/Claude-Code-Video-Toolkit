"""EDL: Messi-Edit auf „Freaks“ (Surf Curse). Storyline, Clips und Schnitt-Vokabular
wie im Messi-Edit v3 (../messi-edit), neu auf die Songstruktur gelegt.

Ausgabe-Beat k = Achtel des Songs (~0,334 s, siehe beatmap.py). Der Song läuft ganz.

  k   0– 56  Intro         Aufstieg: Rosario, La Masia, erstes Profitor          faded
  k  56–120  Strophe 1     Barça (und das Iran-Tor 2014), bis Paris 2017         warm
  k 120–176  Refrain 1     Niederlagen: 2016, Anfield 2019; dazwischen die       cold / bleak
                           Copa 2021; Abschied aus Barcelona, Saudi-Arabien 2022
  k 176–240  Zwischenteil  WM-Finale 2014 ↔ 2022, ruhig: Tunnel, Einlauf, Hymne  cold ↔ warm
  k 240–296  Strophe 2     2014 ↔ 2022 im Spiel, Wechsel wird schneller; Montiels
                           Elfmeter ist genau auf Refrain 2 im Netz
  k 296–352  Refrain 2     Weltmeister                                           warm
  k 352–380  Outro         MetLife 2026                                          cold / bleak
  k 380–416  Outro         Gesichter über die Jahre                              mono
  Coda                     Ausklang, Abgang in den Tunnel, Titel

2014 ↔ 2022: harte Schnitte hin und her, nie beide gleichzeitig, bis auf den
Schluss: bei Montiels Anlauf steht 2014 noch einmal daneben und wird aus dem
Bild geschoben. 2014 immer im Scope-Band und kalt, 2022 immer im Vollbild und
warm. Der Wechsel wird schneller: Achter (Tunnel bis Hymne), Vierer, Zweier,
eine Einer-Traube, dann der Split.

Gesichter: gleiche Höhe, gleicher Ort, Band steht still — nur das Gesicht altert.
Keine Jahreszahlen im Video.
"""

F22 = 'src/final22_hl.mp4'
GET = 'src/getafe07.mkv'
WEM = 'src/wembley11.mkv'
BIL = 'src/bilbao15.mp4'
UCL = 'src/ucl09_2h.mp4'
LMG = 'src/lamasia.mp4'
BDO = 'src/ballondor09_11.mp4'
FG = 'src/first_goal05.mp4'
IRN = 'src/iran14.ts'
KID = 'cuts/robinson_kid.mp4'
PSG = 'src/psg17_end.mp4'
B15D = 'cuts/b15_drib.mp4'
M17C = 'cuts/m17_celeb.mp4'
R16P = 'cuts/r16_pen.mp4'
R16C = 'cuts/r16_cry.mp4'
R16A = 'cuts/r16_after.mp4'
ANF = 'cuts/anf19.mp4'
C21L = 'cuts/c21_lift.mp4'
C21S = 'cuts/c21_smile.mp4'
C21R = 'cuts/c21_raise.mp4'
N21A = 'cuts/n21_cry_a.mp4'
N21B = 'cuts/n21_cry_b.mp4'
W14T, W22T = 'cuts/w14_tunnel.mp4', 'cuts/w22_tunnel.mp4'
W14W, W22W = 'cuts/w14_walkout.mp4', 'cuts/w22_walkout.mp4'
W14A, W22A = 'cuts/w14_anthem.mp4', 'cuts/w22_anthem.mp4'
W14C = 'cuts/w14_chance.mp4'
W14R = 'cuts/w14_react.mp4'
W14G = 'cuts/w14_goetze.mp4'
W14F = 'cuts/w14_fk.mp4'
W14X = 'cuts/w14_whistle.mp4'
W22P = 'cuts/w22_pen.mp4'
LIFT = 'cuts/c22_lift.mp4'


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
    # ── Aufstieg (Intro, nur Gitarre) ────────────────────────────────────────
    S(0, 8, C(BDO, 2.2), 'box43', 'faded', ['grain_heavy', 'drift'], 'ROSARIO'),
    S(8, 12, C(BDO, 10.15, focus=(0.45, 0.55), zoom=1.1), 'wide', 'faded', ['grain_heavy']),
    S(12, 16, C(LMG, 62.6), 'square', 'faded', ['grain_heavy', 'drift']),
    S(16, 24, C(LMG, 51.62, focus=(0.5, 0.45)), 'box43', 'faded', ['grain', 'push'], 'BARCELONA'),
    S(24, 28, C(LMG, 102.5), 'wide', 'faded', ['grain']),
    S(28, 32, C(LMG, 110.0), 'full', 'faded', ['grain']),
    S(32, 36, C(LMG, 115.3), 'scope', 'faded', ['grain']),
    S(36, 40, C(LMG, 168.5, focus=(0.4, 0.5), zoom=1.05), 'square', 'faded', ['push', 'grain']),
    S(40, 44, C(LMG, 177.0, focus=(0.6, 0.45)), 'box43', 'faded', ['grain']),
    S(44, 48, C(FG, 54.0, focus=(0.5, 0.4), zoom=1.1), 'wide', 'faded', ['grain']),
    S(48, 52, C(FG, 32.0, focus=(0.5, 0.35), zoom=1.3), 'scope', 'warm', ['grain']),
    S(52, 56, C(LMG, 193.0, speed=1.35), 'full', 'warm', ['grain', 'zoom_in']),

    # ── Barça (Strophe 1) ────────────────────────────────────────────────────
    S(56, 58, C(LMG, 200.0, focus=(0.45, 0.55), zoom=1.15), 'wide', 'warm', ['open', 'thump', 'punch', 'grain']),
    S(58, 62, C(FG, 119.4, focus=(0.5, 0.45), zoom=1.15), 'square', 'warm', ['punch']),
    GRID(62, 70, [C(GET, 43.0, zoom=1.15), C(GET, 52.2, zoom=1.1), C(GET, 55.6, zoom=1.1)], 'warm', ['grain']),
    S(70, 72, C(GET, 61.3), 'scope', 'warm', ['punch', 'grain']),
    S(72, 74, C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.35), 'box43', 'warm', ['punch', 'grain_heavy']),
    S(74, 76, C(UCL, 1639.2, focus=(0.45, 0.55), zoom=1.25), 'wide', 'warm', ['punch', 'grain']),
    S(76, 78, C(WEM, 68.9), 'full', 'warm', ['punch']),
    S(78, 79, C(WEM, 73.9, focus=(0.4, 0.4)), 'square', 'warm', ['rgbhit']),
    S(79, 80, C(WEM, 81.9, focus=(0.45, 0.4)), 'wide', 'warm', ['punch']),
    S(80, 82, C(BDO, 41.0, focus=(0.32, 0.5), zoom=1.15), 'scope', 'warm', ['push', 'grain']),
    S(82, 84, C(BDO, 44.6, focus=(0.62, 0.5), zoom=1.15), 'full', 'warm', ['punch']),
    S(84, 86, C(IRN, 49.6, focus=(0.42, 0.55), zoom=1.3), 'wide', 'warm', ['punch']),
    S(86, 88, C(IRN, 12.3, focus=(0.5, 0.5), zoom=1.15), 'square', 'warm', ['thump']),
    S(88, 89, C(B15D, 13.3, zoom=1.2), 'full', 'warm', ['thump']),
    S(89, 90, C(B15D, 14.9, zoom=1.2), 'scope', 'warm', []),
    S(90, 92, C(B15D, 21.2, zoom=1.15), 'wide', 'warm', ['zoom_in']),
    S(92, 96, C(B15D, 22.2, zoom=1.1), 'square', 'warm', ['punch']),
    S(96, 97, C(BIL, 71.0, zoom=1.1), 'scope', 'warm', ['grain']),
    S(97, 98, C(BIL, 72.4, zoom=1.1), 'wide', 'warm', []),
    S(98, 99, C(BIL, 74.6, zoom=1.1), 'full', 'warm', []),
    S(99, 100, C(BIL, 76.8, zoom=1.1), 'square', 'warm', ['rgbhit']),
    S(100, 102, C(BIL, 88.4, zoom=1.1), 'scope', 'warm', ['punch']),
    S(102, 104, C(BIL, 96.4, zoom=1.1), 'full', 'warm', ['punch', 'grain']),
    S(104, 108, C(M17C, 5.4, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['push', 'thump', 'grain']),
    S(108, 112, C(PSG, 229.0, focus=(0.4, 0.4), zoom=1.1), 'square', 'warm', ['push']),
    # "Don't cry": der Abend in Paris klingt aus
    S(112, 120, C(PSG, 147.5, focus=(0.5, 0.45), zoom=1.1), 'full', 'warm', ['grain', 'dip']),

    # ── Niederlagen (Refrain 1: "I'm just a freak") ──────────────────────────
    S(120, 122, C(R16P, 6.6, focus=(0.33, 0.42), zoom=1.45), 'wide', 'cold', ['thump', 'grain']),
    S(122, 124, C(R16P, 8.3, focus=(0.38, 0.38), zoom=1.45), 'scope', 'cold', ['grain']),
    S(124, 128, C(R16C, 2.8, focus=(0.42, 0.42), zoom=1.4), 'square', 'bleak', ['push', 'grain']),
    S(128, 130, C(R16C, 20.0, focus=(0.32, 0.42), zoom=1.55), 'full', 'bleak', ['grain']),
    S(130, 132, C(R16C, 14.4, focus=(0.42, 0.42), zoom=1.45), 'scope', 'cold', ['grain']),
    S(132, 134, C(R16A, 4.4, focus=(0.45, 0.42), zoom=1.35), 'wide', 'cold', ['grain']),
    S(134, 138, C(R16A, 6.0, focus=(0.42, 0.38), zoom=1.45), 'square', 'bleak', ['push', 'grain']),
    S(138, 140, C(R16A, 27.0, focus=(0.4, 0.45), zoom=1.3), 'scope', 'cold', ['grain']),
    S(140, 142, C(R16A, 19.0, focus=(0.25, 0.45), zoom=1.5), 'wide', 'cold', ['grain']),
    S(142, 146, C(ANF, 6.7, focus=(0.47, 0.38), zoom=1.2), 'box43', 'cold', ['push', 'grain']),
    # Copa América 2021: endlich ein Titel
    S(146, 148, C(C21L, 10.3, focus=(0.5, 0.35), zoom=1.25), 'full', 'warm', ['punch']),
    S(148, 152, C(C21S, 4.4, focus=(0.38, 0.55), zoom=1.2), 'square', 'warm', ['push']),
    S(152, 154, C(C21S, 8.0, focus=(0.72, 0.45), zoom=1.4), 'wide', 'warm', ['punch']),
    S(154, 156, C(C21R, 6.0, focus=(0.45, 0.4), zoom=1.3), 'scope', 'warm', ['thump']),
    S(156, 160, C(C21L, 20.8, focus=(0.6, 0.4), zoom=1.3), 'full', 'warm', ['push']),
    # Abschied aus Barcelona
    S(160, 161, C(N21B, 6.2, focus=(0.45, 0.42), zoom=1.3), 'wide', 'bleak', ['grain']),
    S(161, 162, C(N21A, 5.0, focus=(0.5, 0.45), zoom=1.2), 'square', 'bleak', []),
    S(162, 163, C(N21B, 7.5, focus=(0.45, 0.42), zoom=1.3), 'scope', 'bleak', []),
    S(163, 164, C(N21A, 5.6, focus=(0.55, 0.45), zoom=1.2), 'full', 'bleak', ['rgbhit']),
    S(164, 168, C(N21B, 4.0, focus=(0.45, 0.45), zoom=1.2, speed=0.6), 'slit', 'bleak', ['drift', 'grain']),
    # Saudi-Arabien 2022: die letzte Niederlage vor dem Finale
    S(168, 176, C('cuts/sau22.mp4', 6.0, focus=(0.48, 0.42), speed=0.55), 'portrait', 'cold', ['push', 'grain', 'dip']),

    # ── WM-Finale 2014 ↔ 2022, ruhig (Zwischenteil) ──────────────────────────
    A14(176, 184, W14T, 46.5, auto=True, fx=('grain', 'push')),
    B22(184, 192, W22T, 9.0, auto=True, fx=('push',)),
    A14(192, 200, W14W, 11.0, focus=(0.45, 0.42), zoom=1.35, fx=('grain', 'push')),
    B22(200, 208, W22W, 31.5, focus=(0.35, 0.5), fx=('push',)),
    A14(208, 216, W14A, 9.0, auto=True, fx=('grain', 'push')),
    B22(216, 224, W22A, 6.5, auto=True, fx=('push',)),
    A14(224, 228, W14A, 14.5, focus=(0.5, 0.4), zoom=1.1),
    B22(228, 232, W22A, 43.5, focus=(0.6, 0.45), zoom=1.1),
    A14(232, 236, W14C, 10.6, focus=(0.45, 0.5), zoom=1.1),
    B22(236, 240, F22, 13.4, focus=(0.35, 0.6), zoom=1.6),

    # ── 2014 ↔ 2022 im Spiel (Strophe 2) ─────────────────────────────────────
    # Zweier: Chance, Reaktion, Gegentor, letzte Chance, Schlusspfiff | Elfmeterschießen
    A14(240, 242, W14C, 22.6, focus=(0.5, 0.5)),
    B22(242, 244, F22, 69.6, focus=(0.45, 0.5), fx=('punch',)),
    A14(244, 246, W14C, 5.2, auto=True),
    B22(246, 248, F22, 59.85, speed=0.65, auto=True),
    A14(248, 250, W14G, 14.3, 'bleak', focus=(0.42, 0.5), zoom=1.2, fx=('thump', 'grain')),
    B22(250, 252, F22, 85.4, 'neutral', focus=(0.5, 0.45), fx=('thump',)),
    A14(252, 254, W14R, 11.3, 'bleak', auto=True),
    B22(254, 256, F22, 49.6, 'neutral', focus=(0.5, 0.45), zoom=1.1),
    A14(256, 258, W14F, 9.8, 'bleak', auto=True),
    B22(258, 260, F22, 92.9, focus=(0.45, 0.5), fx=('punch',)),
    A14(260, 262, W14F, 28.3, 'bleak', focus=(0.45, 0.4), zoom=1.15),
    B22(262, 264, W22P, 1.3, focus=(0.45, 0.35), zoom=1.2),
    A14(264, 266, W14X, 7.5, 'bleak', focus=(0.5, 0.45)),
    B22(266, 268, W22P, 6.8, auto=True),
    A14(268, 270, W14X, 35.2, 'bleak', auto=True),
    B22(270, 272, W22P, 29.0, auto=True),
    # Einer-Traube
    A14(272, 273, W14X, 23.0, 'bleak', focus=(0.5, 0.5)),
    B22(273, 274, W22P, 39.3, focus=(0.5, 0.5), fx=('thump',)),
    A14(274, 275, W14G, 21.0, 'bleak', focus=(0.5, 0.45), zoom=1.1),
    B22(275, 276, F22, 101.6, focus=(0.4, 0.6), zoom=1.3),
    A14(276, 277, W14X, 40.5, 'bleak', focus=(0.45, 0.45), zoom=1.1),
    B22(277, 278, W22P, 41.0, focus=(0.5, 0.45), fx=('thump',)),
    A14(278, 279, W14R, 13.0, 'bleak', auto=True),
    B22(279, 280, W22P, 7.6, focus=(0.5, 0.4), zoom=1.1),
    A14(280, 284, 'cuts/c14_ref.mp4', 2.1, 'bleak', auto=True, fx=('grain', 'push')),
    # 2014 steht daneben, 2022 schiebt es aus dem Bild; Montiels Ball ist auf Refrain 2 im Netz
    PAR(284, 296, C('cuts/c14_alone.mp4', 4.2, 'bleak', (0.5, 0.45), 1.2),
        C(F22, 'MONTIEL', 'cold', (0.42, 0.47), 1.3), 0.5,
        keys=[(288, 0.42), (292, 0.34), (296, 0.0)], fx=['grain']),

    # ── Weltmeister (Refrain 2) ──────────────────────────────────────────────
    S(296, 298, C(F22, 114.3, focus=(0.5, 0.42), zoom=1.05), 'full', 'warm', ['flash', 'punch', 'grain']),
    S(298, 300, C(F22, 116.6, focus=(0.5, 0.45)), 'wide', 'warm', ['punch']),
    # Golden Ball und Pokal, ebenfalls im Wechsel
    A14(300, 302, 'cuts/c14_golden.mp4', 5.2, focus=(0.28, 0.5), zoom=1.1, fx=('push',)),
    B22(302, 304, 'cuts/c22_gball.mp4', 3.2, focus=(0.5, 0.42), fx=('push',)),
    A14(304, 306, 'cuts/c14_walk.mp4', 4.0, focus=(0.5, 0.5), zoom=1.1, fx=('push',)),
    B22(306, 308, 'cuts/c22_kiss.mp4', 8.0, focus=(0.47, 0.45), fx=('push',)),
    S(308, 310, C('cuts/c22_bisht.mp4', 0.5, focus=(0.44, 0.47), zoom=1.2), 'wide', 'warm', ['punch']),
    S(310, 312, C('cuts/c22_trophy.mp4', 4.5, focus=(0.55, 0.45), zoom=1.15), 'square', 'warm', ['punch']),
    S(312, 314, C('cuts/c22_trophy.mp4', 11.0, focus=(0.45, 0.5), zoom=1.2), 'full', 'warm', ['thump']),
    S(314, 316, C(LIFT, 6.3, focus=(0.46, 0.5), zoom=1.18), 'scope', 'warm', ['punch', 'grain']),
    S(316, 317, C(LIFT, 13.1, focus=(0.46, 0.5), zoom=1.18), 'full', 'warm', ['rgbhit']),
    S(317, 318, C(LIFT, 14.3, zoom=1.1), 'square', 'warm', []),
    S(318, 319, C(LIFT, 21.1, focus=(0.46, 0.5), zoom=1.18), 'wide', 'warm', []),
    S(319, 320, C(LIFT, 22.2, focus=(0.46, 0.5), zoom=1.18), 'full', 'warm', ['rgbhit']),
    S(320, 324, C(LIFT, 9.6, focus=(0.46, 0.5), zoom=1.15), 'scope', 'warm', ['zoom_in', 'grain']),
    # Vermächtnis: sechs Szenen laufen durch, auf jedem Beat springt die Anordnung
    GRID(324, 336, [C(B15D, 13.0, zoom=1.2), C(BIL, 70.6, zoom=1.1), C(WEM, 66.4),
                    C(GET, 44.0, zoom=1.1), C(C21R, 6.0, focus=(0.45, 0.4), zoom=1.3),
                    C(UCL, 1637.6, focus=(0.5, 0.5), zoom=1.3)], 'warm', ['grain']),
    S(336, 340, C('cuts/c22_kiss.mp4', 9.5, focus=(0.47, 0.42)), 'portrait', 'warm', ['push']),
    S(340, 344, C('cuts/c22_gball.mp4', 3.4, focus=(0.46, 0.3), zoom=1.32), 'full', 'warm', ['thump', 'grain']),
    S(344, 348, C(LIFT, 16.8, focus=(0.46, 0.5), zoom=1.15), 'scope', 'warm', ['zoom_in']),
    S(348, 352, C('cuts/c22_kiss.mp4', 13.8, focus=(0.5, 0.55), zoom=1.1), 'slit', 'warm', ['drift', 'dip']),

    # ── MetLife 2026 (Outro) ─────────────────────────────────────────────────
    S(352, 356, C('cuts/c26_back.mp4', 6.0, focus=(0.42, 0.5)), 'scope', 'cold', ['grain', 'push']),
    S(356, 358, C('cuts/c26_medal.mp4', 8.0, focus=(0.55, 0.45), zoom=1.2), 'wide', 'cold', ['grain']),
    S(358, 364, C('cuts/c26_trophy.mp4', 10.5, focus=(0.45, 0.45)), 'full', 'cold', ['push', 'grain']),
    S(364, 366, C('cuts/c26_spain.mp4', 9.0, zoom=1.1), 'scope', 'cold', ['grain']),
    S(366, 368, C('cuts/c26_spain.mp4', 3.5, focus=(0.4, 0.45), zoom=1.3), 'wide', 'cold', ['grain']),
    SPLIT(368, 372, [C(R16C, 12.3, 'bleak', (0.42, 0.42), 1.4),
                     C('cuts/c26_tears.mp4', 1.0, 'bleak', (0.55, 0.45))], 'full', ['push']),
    S(372, 376, C('cuts/c26_tears.mp4', 17.8, focus=(0.5, 0.45), zoom=1.1), 'square', 'bleak', ['push', 'grain']),
    SPLIT(376, 380, [C('cuts/c14_walk.mp4', 4.5, 'cold', (0.5, 0.5), 1.1),
                     C('cuts/c22_kiss.mp4', 9.0, 'warm', (0.47, 0.45)),
                     C('cuts/c26_trophy.mp4', 12.0, 'cold', (0.5, 0.45))], 'full', ['push', 'dip']),

    # ── Gesichter über die Jahre (Outro) ─────────────────────────────────────
    FACE(380, 382, C(KID, 20.0)),
    FACE(382, 384, C(KID, 17.5)),
    FACE(384, 386, C(KID, 15.0)),
    FACE(386, 388, C(KID, 12.0, face=(0.40, 0.52, 0.85))),
    FACE(388, 390, C(KID, 3.05, speed=0.45, face=(0.19, 0.52, 0.45))),
    FACE(390, 392, C(BDO, 46.8)),
    FACE(392, 394, C(WEM, 74.3, face=(0.293, 0.482, 0.286))),
    FACE(394, 396, C(W14A, 12.0)),
    FACE(396, 398, C(R16A, 3.4)),
    FACE(398, 400, C(ANF, 6.0)),
    FACE(400, 402, C(N21B, 5.6)),
    FACE(402, 404, C(W22T, 32.0)),
    FACE(404, 408, C('cuts/c26_trophy.mp4', 10.5)),
    FACE(408, 416, C('cuts/c26_tears.mp4', 4.0, face=(0.62, 0.55, 0.85))),

    # ── Coda: der letzte Anschlag klingt aus, Abgang in den Tunnel, Titel ────
    CODA(416, C('cuts/c26_spain.mp4', 24.9, focus=(0.5, 0.5), speed=0.5),
         'LIONEL MESSI', 'GRACIAS, LEO', fade_at=2.4, title_at=2.8),
]
