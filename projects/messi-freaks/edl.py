"""EDL: Messi auf „Freaks“ (Surf Curse), TikTok-Fassung, ~59 s.

Ausgabe-Beat k = Achtel des Songs (~0,334 s, siehe beatmap.py). Der Song läuft von
0:00 bis zum Ende von Refrain 1 und hört auf einer Eins auf (Schleife).

  k   0– 56  Intro         Barça: vier Solos, jedes vom Antritt bis ins Netz       warm
  k  56–120  Strophe 1     Argentinien bricht: Iran 2014, Finale 2014 (Chance,       neutral → cold
                           Götze, Pokal), Copa 2016 und Anfield 2019 ("I can't       → bleak
                           cover up my face"), Abschied aus Barcelona ("Don't cry")
  k 120–176  Refrain 1     WM 2022: Mexiko, Kroatien, Martínez, Montiel — der Ball   warm
                           ist auf dem vierten "I'm just a freak" im Netz (k 160),
                           dann der Pokal

Spielszenen sind lang genug, dass man sie versteht: Antritt, Abschluss, Netz. Wo
eine Szene länger läuft als ein Takt, wird sie mit RUN auf dem Beat in Ausschnitte
zerlegt — die Quelle läuft durch, nur Band und Zoom springen. So bleibt der Schnitt
knackig, ohne die Szene zu zerhacken. Nur HD-Quellen (1080, Barça 720) und nur
innerhalb einer Kameraeinstellung: kein In-Punkt liegt in einer Blende.
"""
import timeline as tl

F22 = 'src/final22_hl.mp4'
GET = 'src/getafe07.mkv'
BIL = 'src/bilbao15.mp4'
IRN = 'src/iran14.ts'
MEX = 'src/wc22_mex.webm'
CRO = 'src/wc22_cro.webm'
B15D = 'cuts/b15_drib.mp4'
M17G = 'cuts/m17_goal.mp4'
M17C = 'cuts/m17_celeb.mp4'
R16P = 'cuts/r16_pen.mp4'
R16C = 'cuts/r16_cry.mp4'
ANF = 'cuts/anf19.mp4'
N21B = 'cuts/n21_cry_b.mp4'
W14C = 'cuts/w14_chance.mp4'
W14G = 'cuts/w14_goetze.mp4'
WALK = 'cuts/c14_walk.mp4'
LIFT = 'cuts/c22_lift.mp4'


def C(src, t, grade=None, focus=(0.5, 0.5), zoom=1.0, speed=1.0, label=None, out=None, auto=False, face=None):
    """Clip-Referenz. out: spätester Quellpunkt (Tempo wird passend gesetzt).
    auto: Ausschnitt per Gesichtserkennung.  face: Gesicht von Hand (cx, cy, h)."""
    f = dict(cx=face[0], cy=face[1], h=face[2], manual=True) if face else None
    return dict(src=src, t=t, grade=grade, focus=focus, zoom=zoom, speed=speed, label=label, out=out,
                auto=auto, face=f)


def S(k0, k1, clip, band, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='single', clips=[clip], band=band, grade=grade, fx=list(fx), label=label)


def RUN(k0, k1, src, t, out, parts, grade, focus=(0.5, 0.5), fx=()):
    """Eine durchgehende Spielszene von t bis out über k0–k1, auf dem Beat zerlegt.
    parts: [(k, band, zoom), ...] ab k0. Die Quellzeit jedes Teils wird aus der
    absoluten Ausgabezeit gerechnet, die Szene läuft also ohne Sprung durch."""
    speed = (out - t) / (tl.kt(k1) - tl.kt(k0))
    bounds = [p[0] for p in parts] + [k1]
    shots = []
    for (ka, band, zoom), kb in zip(parts, bounds[1:]):
        ta = t + (tl.kt(ka) - tl.kt(k0)) * speed
        shots.append(S(ka, kb, C(src, round(ta, 4), focus=focus, zoom=zoom, speed=speed), band, grade,
                       fx if ka == k0 else ('punch',)))
    return shots


SHOTS = [
    # ── Intro: Barça, vier Solos ─────────────────────────────────────────────
    # Getafe 2007: Mittellinie bis Netz, in zwei Ausschnitten, dann der Abschluss
    *RUN(0, 16, GET, 43.0, 49.7, [(0, 'full', 1.0), (8, 'wide', 1.12)], 'warm', focus=(0.55, 0.5)),
    S(16, 20, C(GET, 49.8, out=51.4), 'full', 'warm', ['punch']),
    # Bayern 2015: Boateng fällt, Lupfer über Neuer
    S(20, 26, C(B15D, 13.4, zoom=1.08), 'wide', 'warm', ['punch']),
    S(26, 32, C(B15D, 21.75, zoom=1.08, focus=(0.5, 0.55)), 'full', 'warm', ['punch']),
    # Bilbao 2015: durch vier Mann
    *RUN(32, 46, BIL, 71.7, 78.9, [(32, 'wide', 1.0), (40, 'full', 1.1)], 'warm', fx=('punch',)),
    # Bernabéu 2017: der Schuss in der Nachspielzeit, das Trikot
    S(46, 51, C(M17G, 8.67, zoom=1.3, focus=(0.55, 0.58)), 'wide', 'warm', ['punch']),
    S(51, 56, C(M17C, 5.6, focus=(0.5, 0.4), zoom=1.1), 'box43', 'warm', ['thump', 'push']),

    # ── Strophe 1: Argentinien bricht ────────────────────────────────────────
    # WM 2014: der Schlenzer gegen Iran — Hoffnung
    S(56, 66, C(IRN, 50.9, out=55.9, zoom=1.08), 'full', 'neutral', ['punch']),
    S(66, 70, C(IRN, 12.3, focus=(0.5, 0.5), zoom=1.15), 'square', 'neutral', ['thump']),
    # Finale 2014: Messis Chance geht vorbei, Götze trifft, Messi am Pokal vorbei
    S(70, 78, C(W14C, 22.5, focus=(0.5, 0.55)), 'wide', 'cold', ['punch', 'grain']),
    S(78, 85, C(W14G, 5.2, focus=(0.55, 0.5)), 'scope', 'cold', ['punch', 'grain']),
    S(85, 89, C(W14G, 9.7, auto=True), 'box43', 'bleak', ['push', 'grain']),
    S(89, 97, C(WALK, 4.0, focus=(0.5, 0.5), zoom=1.1), 'scope', 'cold', ['push', 'grain']),
    # Copa 2016 nach dem verschossenen Elfmeter, Anfield 2019 — "I can't cover up my face".
    # r16_cry ist ein Reaktionsvideo, das Messi-Bild steht dort ab 4,3 s still: nur 2,6–4,27.
    S(97, 101, C(R16P, 6.6, focus=(0.33, 0.42), zoom=1.45), 'wide', 'bleak', ['thump', 'grain']),
    S(101, 106, C(R16C, 2.6, focus=(0.42, 0.42), zoom=1.4), 'square', 'bleak', ['push', 'grain']),
    S(106, 113, C(ANF, 6.1, focus=(0.47, 0.38), zoom=1.15), 'scope', 'bleak', ['push', 'grain']),
    # Abschied aus Barcelona 2021 — "Don't cry"
    S(113, 120, C(N21B, 4.0, focus=(0.45, 0.45), zoom=1.2), 'box43', 'bleak', ['push', 'grain', 'dip']),

    # ── Refrain 1: WM 2022 ───────────────────────────────────────────────────
    # Mexiko: Annahme, Schuss aus 25 m, Ball im Netz, Schrei
    S(120, 126, C(MEX, 79.3), 'full', 'warm', ['punch', 'rgbhit']),
    S(126, 131, C(MEX, 76.3, focus=(0.45, 0.62), zoom=1.25), 'wide', 'warm', ['punch']),
    S(131, 134, C(MEX, 85.0, focus=(0.5, 0.42)), 'square', 'warm', ['thump']),
    # Kroatien: Messi gegen Gvardiol, Rückpass, Álvarez trifft
    S(134, 142, C(CRO, 94.0, out=98.0, focus=(0.5, 0.58), zoom=1.2), 'full', 'warm', ['punch']),
    S(142, 148, C(CRO, 107.0, out=108.9, focus=(0.55, 0.6), zoom=1.1), 'wide', 'warm', ['punch']),
    # Finale: Martínez' Fuß in der 123. Minute, Montiels Elfmeter auf "I'm just a freak"
    S(148, 152, C(F22, 92.95, focus=(0.5, 0.55), zoom=1.1), 'full', 'warm', ['punch', 'thump']),
    S(152, 160, C(F22, 'MONTIEL', focus=(0.45, 0.5), zoom=1.45), 'wide', 'warm', ['push']),
    S(160, 164, C(F22, 114.3, focus=(0.5, 0.42), zoom=1.05), 'full', 'warm', ['flash', 'punch']),
    # der Pokal
    S(164, 168, C(LIFT, 7.95, focus=(0.5, 0.45), zoom=1.1), 'wide', 'warm', ['punch']),
    S(168, 172, C(LIFT, 13.6, focus=(0.5, 0.45), zoom=1.05), 'full', 'warm', ['thump']),
    S(172, 176, C(LIFT, 9.6, focus=(0.5, 0.55)), 'scope', 'warm', ['zoom_in', 'grain']),
]
