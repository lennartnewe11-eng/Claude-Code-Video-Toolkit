"""EDL: Mesut Özil — CLASSIC.

Der Song fragt im Intro nach "the classics" und schließt jede Strophe mit
"Classic". Das Edit antwortet: der Klassiker ist Özil, der Zehner, dessen
Klasse im Pass liegt, im ersten Kontakt, im Lupfer. Die Ansager-Samples des
Songs (Liberace-Zeit, deutsche Schallplatten-Ansage) bekommen Archivbilder,
die Referenzen im Text (Niki Lauda, Kobe Bryant, Rembrandt, Apple Keynote)
kurze Einschübe genau auf dem Wort.

Ausgabe-Beat k = Song-Beat (der Song läuft ganz, 162 BPM, eine Zeile = 8 Beats).

  k   0– 48  Intro        Ansager "return to the classics" (Liberace, s/w), dann Özil 2010
                          im selben s/w-Fenster; "Classic, classic, classic": Real, Arsenal, DFB
  k  48–112  Strophe 1    REAL MADRID: sein 1:1 in München 2012, Ronaldo umarmt ihn;
                          sein Pass auf Ronaldo zum 2:0 gegen Bayern; Jubel mit Ronaldo
  k 112–144  Break        Streicher: Özil geht vom Platz, Zeitlupe
  k 144–208  Strophe 2    DEUTSCHLAND: WM 2014, sein Tor gegen Algerien; Niki Lauda auf
                          "brennt ... Niki Lauda", Kobe auf "Kobe Bryant trifft",
                          sein Rücken auf "hinter meinem Rücken"
  k 208–240  Break        "Meine Damen, für Sie singt ihr erklärter Liebling": Wochenschau
                          1926, auf "Liebling" Özil bei Arsenal
  k 240–304  Strophe 3    ARSENAL: Tor gegen United, FA-Cup-Sieg, Ludogorets (Torwart umkurvt, Lupfer),
                          Fotoshooting auf "Selfie", Nachtwache auf "Rembrandt",
                          Jobs mit dem iPhone auf "Apple Keynote"
  k 304–344  Outro        Gesichter 2010 bis 2018, "eine ganze Reihe eindrucksvoller Aufnahmen"
  Coda                    Titel

Wortzeiten aus der Transkription (faster-whisper large-v3), in Beats umgerechnet.
"""

LIB = 'src/ref_liberace.mp4'      # Liberace Christmas Show, 1950er, s/w
LAU = 'src/ref_lauda.mp4'         # Tagesschau-Nachruf 2019 mit Archiv 1976
NAC = 'cuts/ref_nachtwacht.mp4'   # Polygoon 1976: die Nachtwache nach der Restaurierung
WHI = 'cuts/ref_whiteman.mp4'     # Polygoon 1926: Paul Whiteman
KOB = 'cuts/ref_kobe.mp4'         # Lakers - Suns 2006, Kobes Wurf in der Verlängerung
JOB = 'cuts/ref_jobs.mp4'         # Macworld 2007, das erste iPhone
RMB = 'cuts/rmb12_20.mp4'         # Real - Bayern 2012: Özils Pass, Ronaldo 2:0
BRM = 'cuts/brm12_oz.mp4'         # Bayern - Real 2012: Özils 1:1
BRS = 'cuts/brm12_sub.mp4'        # dieselbe Partie: Özil geht vom Platz
CR = 'src/cr1112.avi'             # Ronaldo, alle Tore 2011/12
ARG = 'cuts/arg10.mp4'            # WM 2010 Argentinien - Deutschland, Hymne
ALG = 'cuts/alg14.mp4'            # WM 2014 Deutschland - Algerien, Özils 2:0
A13S = 'cuts/a13_sign.mp4'        # Arsenal-Saisonrückblick 13/14: Vorstellung
MU = 'src/ars_mu15.mp4'           # Arsenal - Man United 3:0, 2015, MOTD: Özils Tor
FAC = 'cuts/fac15.mp4'            # FA-Cup-Finale 2015, Arsenal - Aston Villa
LUD = 'src/ars_ludo16.mp4'        # Arsenal - Ludogorets 6:0, 2016, Özils Hattrick
KOR = 'cuts/kor18.mp4'            # WM 2018 Südkorea - Deutschland, Hymne


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
    S(0, 13, C(LIB, 40.0, zoom=1.05), 'box43', 'mono', ['grain_heavy', 'open', 'push']),
    S(13, 25, C(LIB, 49.5, focus=(0.5, 0.4), zoom=1.1), 'box43', 'mono', ['grain_heavy', 'push']),
    S(25, 31.5, C(LIB, 70.0, focus=(0.5, 0.4), zoom=1.2), 'box43', 'mono', ['grain_heavy']),
    # "... the most famous classic": Özil, WM 2010, im selben Fenster
    S(31.5, 42, C(ARG, 26.0, focus=(0.5, 0.42), zoom=1.15), 'box43', 'mono', ['grain', 'push']),
    # "Classic, classic, classic": Real, Arsenal, DFB
    S(42, 43.25, C(BRM, 55.0, focus=(0.5, 0.4), zoom=1.1), 'full', 'warm', ['thump', 'rgbhit']),
    S(43.25, 45.25, C(LUD, 270.5, focus=(0.5, 0.4)), 'full', 'warm', ['thump', 'rgbhit']),
    S(45.25, 48, C(ALG, 69.5, focus=(0.55, 0.4)), 'full', 'warm', ['thump']),

    # ── Strophe 1: REAL MADRID ───────────────────────────────────────────────
    # München 2012: Özils 1:1, live
    S(48, 60, C(BRM, 47.9, focus=(0.6, 0.5), zoom=1.25), 'full', 'warm', ['flash', 'push'], 'REAL MADRID'),
    S(60, 68, C(BRM, 52.6, focus=(0.5, 0.4), zoom=1.1), 'scope', 'warm', ['punch']),
    S(68, 72, C(BRM, 59.9, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['punch']),         # Ronaldo umarmt ihn
    # Bernabéu 2012: Özils Pass, Ronaldo 2:0
    S(72, 84, C(RMB, 81.0, focus=(0.5, 0.5), zoom=1.2), 'full', 'warm', ['push']),
    S(84, 92, C(RMB, 38.3, focus=(0.5, 0.45), zoom=1.1), 'scope', 'warm', ['thump']),
    S(92, 100, C(RMB, 45.5, zoom=1.1), 'wide', 'warm', ['push']),
    S(100, 111, C(CR, 1062.9, focus=(0.6, 0.4), zoom=1.3), 'full', 'warm', ['push']),      # Ronaldo und die 10
    # "Classic": Özils Profil
    S(111, 122, C(BRM, 89.2, focus=(0.4, 0.35), zoom=1.1, speed=0.7), 'wide', 'neutral', ['push', 'grain']),

    # ── Break: Streicher ─────────────────────────────────────────────────────
    S(122, 132, C(BRS, 5.0, focus=(0.5, 0.35), zoom=1.2, speed=0.8), 'scope', 'neutral', ['drift', 'grain']),
    S(132, 144, C(BRS, 9.0, focus=(0.5, 0.35), zoom=1.1, speed=0.8), 'full', 'neutral', ['push', 'dip']),

    # ── Strophe 2: DEUTSCHLAND, Lauda, Kobe ──────────────────────────────────
    S(144, 156, C(ALG, 2.95, focus=(0.3, 0.5), zoom=1.5), 'full', 'warm', ['open', 'push'], 'DEUTSCHLAND'),
    S(156, 160, C(ALG, 7.6, focus=(0.45, 0.55), zoom=1.5), 'full', 'warm', ['punch']),
    S(160, 166, C(ALG, 56.0, focus=(0.4, 0.5), zoom=1.1), 'wide', 'warm', ['push']),
    S(166, 169.5, C(ALG, 69.3, focus=(0.55, 0.4)), 'full', 'warm', ['thump']),
    # "Nach ner Schelle brennt dir deine Fresse, Niki Lauda"
    S(169.5, 172.5, C(LAU, 6.6, zoom=1.05), 'box43', 'faded', ['grain_heavy']),
    S(172.5, 176, C(LAU, 22.3, focus=(0.5, 0.4), zoom=1.05), 'box43', 'faded', ['grain_heavy', 'push']),
    S(176, 184, C(RMB, 87.0, focus=(0.5, 0.5), zoom=1.1), 'full', 'warm', ['punch']),
    S(184, 194, C(BRM, 70.0, focus=(0.5, 0.5), zoom=1.1), 'scope', 'warm', ['push']),
    # "... es wie Kobe Bryant trifft"
    S(194, 197.5, C(KOB, 12.0), 'box43', 'neutral', ['grain']),
    S(197.5, 200, C(KOB, 14.0, focus=(0.5, 0.45), zoom=1.1), 'box43', 'neutral', ['grain', 'thump']),
    S(200, 202, C(BRM, 84.3, zoom=1.1), 'full', 'warm', ['punch']),
    # "Denn sie reden hinter meinem Rücken"
    S(202, 205.5, C(BRM, 105.1, focus=(0.5, 0.6), zoom=1.1), 'wide', 'warm', ['push']),      # ÖZIL 10 von hinten
    # "Classic"
    S(205.5, 216, C(BRS, 14.5, focus=(0.5, 0.35), zoom=1.2, speed=0.8), 'scope', 'neutral', ['drift', 'grain']),

    # ── Break: "Meine Damen, für Sie singt ihr erklärter Liebling" ──────────
    S(216, 224, C(WHI, 7.0), 'box43', 'mono', ['grain_heavy', 'push']),
    S(224, 231, C(WHI, 45.5, focus=(0.5, 0.4), zoom=1.1), 'box43', 'mono', ['grain_heavy', 'push']),
    S(231, 236, C(A13S, 5.0, focus=(0.4, 0.45), zoom=1.1), 'full', 'warm', ['open'], 'ARSENAL'),
    S(236, 240, C(A13S, 0.3, zoom=1.1), 'scope', 'warm', ['push']),

    # ── Strophe 3: ARSENAL ───────────────────────────────────────────────────
    S(240, 252, C(MU, 189.0, focus=(0.55, 0.45), zoom=1.1), 'full', 'warm', ['punch']),     # sein Tor gegen United
    S(252, 256, C(FAC, 17.7, focus=(0.6, 0.45), zoom=1.1), 'wide', 'warm', ['punch']),      # FA-Cup-Finale, mit Bellerín
    S(256, 265.5, C(LUD, 191.2, focus=(0.45, 0.5), zoom=1.1), 'full', 'warm', ['push']),
    # "Dein Album ist ein Selfie, unser Album ist ein Rembrandt"
    S(265.5, 269.5, C(A13S, 108.5, focus=(0.8, 0.5), zoom=1.3), 'wide', 'warm', ['thump']),
    S(269.5, 273.5, C(NAC, 4.5, zoom=1.05), 'box43', 'faded', ['grain_heavy', 'push']),
    S(273.5, 280, C(LUD, 195.6, focus=(0.55, 0.4), zoom=1.05), 'scope', 'warm', ['punch']),
    # der Lupfer
    S(280, 288, C(LUD, 239.4, focus=(0.5, 0.5), zoom=1.1), 'full', 'warm', ['push']),
    S(288, 299.5, C(LUD, 243.0, focus=(0.5, 0.5), zoom=1.1), 'wide', 'warm', ['push']),
    # "Haben Internet-Hype wie ne Apple Keynote"
    S(299.5, 302.5, C(JOB, 50.0), 'wide', 'neutral', ['grain']),
    # "Classic"
    S(302.5, 308, C(LUD, 270.3, focus=(0.5, 0.4)), 'full', 'warm', ['thump', 'dip']),

    # ── Outro: Gesichter 2010 - 2018 ─────────────────────────────────────────
    FACE(308, 314, C(ARG, 28.0)),
    FACE(314, 320, C(BRM, 89.0, speed=0.85, face=(0.44, 0.29, 0.31))),
    FACE(320, 326, C(A13S, 8.0)),
    FACE(326, 332, C(ALG, 70.8)),
    FACE(332, 338, C(LUD, 271.0)),
    FACE(338, 344, C(KOR, 12.4)),

    # ── Coda ─────────────────────────────────────────────────────────────────
    CODA(344, C(KOR, 14.6, focus=(0.62, 0.3), zoom=1.5, speed=0.5), 'MESUT ÖZIL', 'CLASSIC',
         fade_at=0.8, title_at=1.2),
]
