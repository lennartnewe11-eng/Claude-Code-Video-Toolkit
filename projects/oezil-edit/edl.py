"""EDL: Mesut Özil — CLASSIC (v2: nur Özil).

Der Song fragt im Intro nach "the classics" und schließt jede Strophe mit
"Classic". Das Edit antwortet: der Klassiker ist Özil, der Zehner, dessen
Klasse im Pass liegt, im ersten Kontakt, im Freistoß, im Lupfer. Jedes Bild
zeigt Özil: seine Tore, seine Vorlagen, seinen Jubel.

Ausgabe-Beat k = Song-Beat (der Song läuft ganz, 162 BPM, eine Zeile = 8 Beats).

  k   0– 48  Intro        Ansager "my next number ... the classics": s/w, ÖZIL 11 von hinten,
                          Trikotdruck, Hymne 2010; "Classic, classic, classic": Real, Arsenal, DFB
  k  48–112  Strophe 1    REAL MADRID: Tor gegen Atlético (Ronaldo umarmt ihn), 1:1 in München,
                          Pass auf Ronaldo zum 2:0 gegen Bayern, Pass zum Siegtor im Camp Nou
  k 112–144  Break        Streicher: Ronaldo feiert mit der 10; Özils Freistoßtor
  k 144–208  Strophe 2    DEUTSCHLAND: Tor gegen Ghana 2010, Vorlage zum 4:0 gegen Argentinien,
                          Tor gegen Belgien 2011, Tor gegen Algerien 2014, der WM-Pokal
  k 208–240  Break        "Meine Damen ...": Vorstellung bei Arsenal 2013, auf "Liebling" sein Jubel an der Eckfahne
  k 240–304  Strophe 3    ARSENAL: Napoli 2013, Man United 2015, FA-Cup-Sieg, Ludogorets 2016
                          (Torwart umkurvt, Lupfer), mit Sánchez, ÖZIL 11
  k 304–344  Outro        Gesichter 2010 bis 2018, "eine ganze Reihe eindrucksvoller Aufnahmen"
  Coda                    Titel

Fremde Einblendungen der Quellen (Senderlogos, Wasserzeichen) werden über
focus/zoom aus dem Bild geschoben.
"""

BEST = 'src/best.mp4'             # "Mesut Özil, Top 5 Goals" (Fan-Schnitt, Gesichts-Logo links unten)
RMB = 'cuts/rmb12_20.mp4'         # Real - Bayern 2012: Özils Pass, Ronaldo 2:0
BRM = 'cuts/brm12_oz.mp4'         # Bayern - Real 2012: Özils 1:1
CR = 'src/cr1112.avi'             # Ronaldo, alle Tore 2011/12 (Camp Nou, Jubel mit der 10)
ARG = 'cuts/arg10.mp4'            # WM 2010 Argentinien - Deutschland, Hymne
ARG4 = 'cuts/arg10_40.mp4'        # dieselbe Partie: Özils Vorlage zum 4:0
ALG = 'cuts/alg14hd.mp4'          # WM 2014 Deutschland - Algerien, Weltbild HD: Özils 2:1
CER = 'cuts/wc14_cer2.mp4'        # WM-Finale 2014, Siegerehrung, Weltbild HD
A13S = 'cuts/a13_sign.mp4'        # Arsenal-Saisonrückblick 13/14: Vorstellung, Fotoshooting
NAP = 'cuts/a13_nap0.mp4'         # dasselbe: Arsenal - Napoli 2013, Özils Volley
MU = 'src/ars_mu15.mp4'           # Arsenal - Man United 3:0, 2015: Özils Tor
FAC = 'cuts/fac15.mp4'            # FA-Cup-Finale 2015, Arsenal - Aston Villa
LUD = 'src/ars_ludo16.mp4'        # Arsenal - Ludogorets 6:0, 2016, Özils Hattrick
SWA = 'src/ars_swa16.mp4'         # Arsenal - Swansea 3:2, 2016: Özils Tor
WHU = 'src/ars_whu16.mp4'         # West Ham - Arsenal 1:5, 2016: mit Sánchez
KOR = 'cuts/kor18.mp4'            # WM 2018 Südkorea - Deutschland, Hymne

LOGO = dict(focus=(0.6, 0.4), zoom=1.35)       # BEST: Gesichts-Logo links unten raus
QR = dict(focus=(0.45, 0.52), zoom=1.4)        # WHU: QR-Code oben rechts, Schriftzug unten links raus


def C(src, t, grade=None, focus=(0.5, 0.5), zoom=1.0, speed=1.0, label=None, out=None, auto=False, face=None,
      ramp=None):
    f = dict(cx=face[0], cy=face[1], h=face[2], manual=True) if face else None
    return dict(src=src, t=t, grade=grade, focus=focus, zoom=zoom, speed=speed, label=label, out=out,
                auto=auto, face=f, ramp=ramp)


def S(k0, k1, clip, band, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='single', clips=[clip], band=band, grade=grade, fx=list(fx), label=label)


def FACE(k0, k1, clip, label=None):
    return dict(k=(k0, k1), kind='face', clips=[clip], band='square', grade='mono', fx=[], label=label)


def CODA(k0, clip, title, sub, fade_at, title_at, band='scope', grade='mono'):
    return dict(k=(k0, None), kind='coda', clips=[clip], band=band, grade=grade, fx=[], label=None,
                title=title, sub=sub, fade_at=fade_at, title_at=title_at)


SHOTS = [
    # ── Intro: "And now for my next number, I'd like to return to the classics" ──
    S(0, 13, C(WHU, 139.0, speed=0.55, **QR), 'box43', 'mono', ['grain_heavy', 'open', 'push']),   # ÖZIL 11
    S(13, 25, C(SWA, 317.0, focus=(0.5, 0.45), zoom=1.15, speed=0.6), 'box43', 'mono', ['grain_heavy', 'push']),
    S(25, 31.5, C(A13S, 0.8, zoom=1.1), 'box43', 'mono', ['grain_heavy']),                          # Trikotdruck
    # "... the most famous classic": die Hymne 2010
    S(31.5, 42, C(ARG, 25.4, focus=(0.5, 0.42), zoom=1.15, speed=0.8), 'box43', 'mono', ['grain', 'push']),
    # "Classic, classic, classic": Real, Arsenal, DFB
    S(42, 43.25, C(BRM, 55.0, focus=(0.5, 0.4), zoom=1.1), 'full', 'warm', ['thump', 'rgbhit']),
    S(43.25, 45.25, C(LUD, 270.5, focus=(0.5, 0.4)), 'full', 'warm', ['thump', 'rgbhit']),
    S(45.25, 48, C(ALG, 106.0, focus=(0.55, 0.45), zoom=1.1), 'full', 'warm', ['thump']),

    # ── Strophe 1: REAL MADRID ───────────────────────────────────────────────
    S(48, 56, C(BEST, 16.3, **LOGO), 'full', 'warm', ['flash', 'push'], 'REAL MADRID'),             # gegen Atlético
    S(56, 60, C(BEST, 19.2, focus=(0.6, 0.35), zoom=1.3), 'wide', 'warm', ['punch']),                # Ronaldo umarmt ihn
    S(60, 72, C(BRM, 47.9, focus=(0.6, 0.5), zoom=1.25), 'full', 'warm', ['push']),                  # 1:1 in München
    S(72, 78, C(BRM, 52.6, focus=(0.5, 0.4), zoom=1.1), 'scope', 'warm', ['punch']),
    S(78, 82, C(BRM, 59.9, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['punch']),
    S(82, 94, C(RMB, 81.0, focus=(0.5, 0.5), zoom=1.2), 'full', 'warm', ['push']),                   # Pass auf Ronaldo
    S(94, 100, C(RMB, 38.3, focus=(0.5, 0.45), zoom=1.1), 'scope', 'warm', ['thump']),
    S(100, 111, C(CR, 1454.0, focus=(0.5, 0.44), zoom=1.45), 'full', 'warm', ['push']),      # Camp Nou 2012
    # "Classic": Ronaldo feiert mit der 10
    S(111, 122, C(CR, 1398.5, focus=(0.4, 0.4), zoom=1.3, speed=0.75), 'wide', 'neutral', ['push', 'grain']),

    # ── Break: Streicher, der Freistoß ───────────────────────────────────────
    S(122, 134, C(BEST, 98.7, **LOGO), 'scope', 'neutral', ['drift', 'grain']),
    S(134, 144, C(BEST, 105.4, focus=(0.6, 0.4), zoom=1.3, speed=0.8), 'full', 'warm', ['push', 'dip']),

    # ── Strophe 2: DEUTSCHLAND ───────────────────────────────────────────────
    S(144, 152, C(BEST, 40.8, **LOGO), 'full', 'warm', ['open', 'push'], 'DEUTSCHLAND'),            # Ghana 2010
    S(152, 156, C(BEST, 38.35, focus=(0.6, 0.35), zoom=1.3, speed=0.5), 'wide', 'warm', ['punch']),
    S(156, 172, C(ARG4, 42.0, focus=(0.55, 0.5), zoom=1.3), 'full', 'warm', ['push']),              # Vorlage zum 4:0
    S(172, 182, C(BEST, 79.6, **LOGO), 'full', 'warm', ['push']),                                   # Belgien 2011
    S(182, 194, C(ALG, 90.6, focus=(0.5, 0.5), zoom=1.05), 'full', 'warm', ['push']),               # Algerien 2014
    S(194, 200, C(ALG, 101.9, focus=(0.5, 0.45), zoom=1.05), 'wide', 'warm', ['punch']),           # mit Schürrle
    S(200, 207, C(CER, 55.2, focus=(0.5, 0.35), zoom=1.1), 'full', 'warm', ['flash', 'push']),      # der Pokal
    # "Classic"
    S(207, 216, C(CER, 57.6, focus=(0.5, 0.3), zoom=1.1, speed=0.8), 'scope', 'warm', ['push', 'grain']),

    # ── Break: "Meine Damen, für Sie singt ihr erklärter Liebling" ──────────
    S(216, 226, C(A13S, 4.6, focus=(0.45, 0.35), zoom=1.3), 'full', 'warm', ['open'], 'ARSENAL'),
    S(226, 231, C(A13S, 107.6, focus=(0.72, 0.5), zoom=1.6), 'wide', 'warm', ['push']),
    S(231, 240, C(SWA, 343.8, focus=(0.45, 0.55), zoom=1.2, speed=0.8), 'scope', 'warm', ['push']),  # "Liebling"

    # ── Strophe 3: ARSENAL ───────────────────────────────────────────────────
    S(240, 248, C(NAP, 27.4, focus=(0.55, 0.45), zoom=1.3), 'full', 'warm', ['punch']),             # Napoli 2013
    S(248, 252, C(NAP, 35.3, focus=(0.5, 0.45), zoom=1.1), 'wide', 'warm', ['punch']),
    S(252, 262, C(MU, 184.8, focus=(0.6, 0.5), zoom=1.5), 'full', 'warm', ['push']),               # Man United 2015
    S(262, 268, C(MU, 189.0, focus=(0.55, 0.45), zoom=1.1), 'wide', 'warm', ['punch']),
    S(268, 272, C(FAC, 17.7, focus=(0.6, 0.45), zoom=1.1), 'scope', 'warm', ['punch']),             # FA-Cup-Finale 2015
    S(272, 282, C(LUD, 191.2, focus=(0.45, 0.5), zoom=1.1), 'full', 'warm', ['push']),              # Ludogorets 2016
    S(282, 290, C(LUD, 239.4, focus=(0.5, 0.5), zoom=1.1), 'full', 'warm', ['push']),               # der Lupfer
    S(290, 298, C(LUD, 243.0, focus=(0.5, 0.5), zoom=1.1), 'wide', 'warm', ['push']),
    S(298, 302.5, C(WHU, 143.0, **QR), 'full', 'warm', ['thump']),                                  # mit Sánchez
    # "Classic"
    S(302.5, 308, C(SWA, 325.0, focus=(0.5, 0.45), zoom=1.15, speed=0.95), 'full', 'warm', ['thump', 'dip']),

    # ── Outro: Gesichter 2010 - 2018 ─────────────────────────────────────────
    FACE(308, 314, C(ARG, 28.3, speed=0.85)),
    FACE(314, 320, C(BRM, 89.0, speed=0.85, face=(0.44, 0.29, 0.31))),
    FACE(320, 326, C(A13S, 111.4, speed=0.6, face=(0.53, 0.37, 0.5))),
    FACE(326, 332, C(CER, 56.0, face=(0.534, 0.293, 0.206))),
    FACE(332, 338, C(LUD, 271.0)),
    FACE(338, 344, C(KOR, 12.4)),

    # ── Coda ─────────────────────────────────────────────────────────────────
    CODA(344, C(KOR, 14.6, focus=(0.62, 0.3), zoom=1.5, speed=0.5), 'MESUT ÖZIL', 'CLASSIC',
         fade_at=0.8, title_at=1.2),
]
