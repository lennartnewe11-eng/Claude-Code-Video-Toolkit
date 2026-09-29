"""EDL: Neymar — OUSADIA E ALEGRIA.

Eine Emotion: Freude. Sie wird gespielt (Skills), dann angehalten (Druck im
Maracanã) und bricht mit dem letzten Elfmeter für Brasiliens erstes
olympisches Gold als Freudentränen wieder aus.

Ausgabe-Beat k = Song-Beat - 152 (der Song läuft an einem Stück, siehe timeline.py).

  k   0– 60  Strophe 2   GINGA      Santos (Solotor, Libertadores-Finale), London,      faded → warm
                                    Confed-Cup-Finale: jedes Tor ganz, mit Jubel
  k  60– 96  Pre-Chorus  BARCELONA  Saison 14/15: Athletic (Dribbling, Tor), Freistoß    warm
                                    in Sevilla aus Sicht des Torwarts
  k  96–104  Loch        Atem       Regenbogen-Lupfer im Pokalfinale, Zeitlupe          mono
  k 104–136  Drop 2      Berlin     CL-Finale, 95. Minute: das 3:1; dann der Freistoß   warm
                                    im Olympia-Finale
  k 136–200  Breakdown   DRUCK      Maracanã bei Nacht, Elfmeterschießen, Stille       bleak / mono
  k 200–216  Build       ANLAUF     Neymar legt sich den Ball hin, Schnitte werden     bleak
                                    schneller, Band zieht sich zusammen
  k 216–244  Drop 3      ALEGRIA    Ball im Netz genau auf dem Drop, Freudentränen     warm
  k 244–248  Loch        Tränen     ein Bild, still
  k 248–280  Finale      Gold       Medaille, Samba, jedes Lachen noch einmal           warm
  Coda                              Ausklang, Titel

Bis zum Elfmeterschießen nur Tore und Skills, jede Szene lang genug, um sie
zu verstehen (4–12 Beats je Shot). Hochformat-Quellen (Samba) laufen im
Portrait-Band: das Band zeigt, woher das Bild kommt, statt es aufzublasen.
"""

LON = 'src/london12.mp4'
SCO = 'src/santos_colo.mp4'
SFI = 'src/santos_final11.mp4'
AUS = 'src/aus13.ts'
CON = 'src/confed13_hl.mp4'
PSG = 'src/psg17_end.mp4'
SAM = 'src/samba.mp4'
CRO = 'cuts/cro22.mp4'
B1 = 'src/b1415_1.mp4'
B2 = 'src/b1415_2.mp4'
BER = 'src/berlin95.mkv'
FK = 'cuts/oly_fk.mp4'
PRE = 'cuts/oly_pre.mp4'
STA = 'cuts/oly_stadium.mp4'
SO = 'cuts/oly_so.mp4'
PEN = 'cuts/oly_pen.mp4'
MED = 'cuts/oly_medal.mp4'


def C(src, t, grade=None, focus=(0.5, 0.5), zoom=1.0, speed=1.0, label=None, out=None, auto=False, face=None,
      ramp=None):
    f = dict(cx=face[0], cy=face[1], h=face[2], manual=True) if face else None
    return dict(src=src, t=t, grade=grade, focus=focus, zoom=zoom, speed=speed, label=label, out=out,
                auto=auto, face=f, ramp=ramp)


def S(k0, k1, clip, band, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='single', clips=[clip], band=band, grade=grade, fx=list(fx), label=label)


def GRID(k0, k1, clips, grade, fx=(), label=None):
    return dict(k=(k0, k1), kind='grid', clips=clips, band='full', grade=grade, fx=list(fx), label=label)


def CODA(k0, clip, title, sub, fade_at, title_at, band='scope', grade='warm'):
    return dict(k=(k0, None), kind='coda', clips=[clip], band=band, grade=grade, fx=[], label=None,
                title=title, sub=sub, fade_at=fade_at, title_at=title_at)


SHOTS = [
    # ── GINGA (Strophe 2): Santos, das Solotor gegen Colo-Colo ──────────────
    S(0, 8, C(SCO, 352.6, focus=(0.5, 0.5), zoom=1.15), 'box43', 'faded', ['grain_heavy', 'push'], 'SANTOS'),
    S(8, 16, C(SCO, 365.9, focus=(0.55, 0.5), zoom=1.1), 'full', 'faded', ['grain', 'push']),
    S(16, 20, C(SCO, 370.5, zoom=1.05), 'full', 'warm', ['punch', 'grain']),
    S(20, 24, C(SCO, 372.5, focus=(0.5, 0.4), zoom=1.1, speed=0.5), 'wide', 'warm', ['thump', 'grain']),
    # Libertadores-Finale 2011: das 1:0, dann der Jubel
    S(24, 32, C(SFI, 368.0, focus=(0.35, 0.5), zoom=1.45), 'full', 'warm', ['push', 'grain']),
    S(32, 36, C(SFI, 373.55, focus=(0.5, 0.4), zoom=1.1, speed=0.5), 'wide', 'warm', ['punch', 'grain']),
    # London 2012: zwei Dribblings, jedes ganz
    S(36, 44, C(LON, 58.2, focus=(0.53, 0.54), zoom=1.12), 'full', 'warm', ['push'], 'SELEÇÃO'),
    S(44, 52, C(LON, 71.0, focus=(0.53, 0.54), zoom=1.12), 'wide', 'warm', ['push']),
    # Confed-Cup-Finale 2013 gegen Spanien: das 2:0
    S(52, 60, C(CON, 398.3, focus=(0.35, 0.5), zoom=1.4), 'full', 'warm', ['push']),

    # ── BARCELONA (Pre-Chorus) ───────────────────────────────────────────────
    S(60, 64, C(CON, 403.5, focus=(0.5, 0.4), zoom=1.1, speed=0.75), 'wide', 'warm', ['punch']),
    S(64, 72, C(B1, 316.3, speed=0.95), 'scope', 'warm', ['push'], 'BARCELONA'),
    S(72, 80, C(B1, 320.0, focus=(0.55, 0.5), zoom=1.2), 'full', 'warm', ['push']),
    S(80, 84, C(B1, 328.6, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['punch']),
    # Sevilla 2015: Freistoß, aus Sicht des Torwarts bis ins Netz
    S(84, 86, C(B2, 1795.0, focus=(0.5, 0.4), zoom=1.1), 'scope', 'warm', ['push']),
    S(86, 96, C(B2, 1833.5, focus=(0.5, 0.5), zoom=1.1), 'full', 'warm', ['push', 'dip']),

    # ── Atem (Loch): der Regenbogen-Lupfer im Pokalfinale, Zeitlupe ─────────
    S(96, 104, C(B2, 3520.3, focus=(0.5, 0.5), zoom=1.25, speed=0.8), 'wide', 'mono', ['push', 'grain']),

    # ── Drop 2: Berlin, Champions-League-Finale, 95. Minute ─────────────────
    S(104, 116, C(BER, 51.3, focus=(0.55, 0.55), zoom=1.3), 'full', 'warm', ['open', 'push']),
    S(116, 120, C(BER, 57.9, focus=(0.5, 0.45), zoom=1.1, speed=0.88), 'scope', 'warm', ['punch']),
    S(120, 124, C(B2, 1807.4, focus=(0.5, 0.45), zoom=1.1, speed=0.65), 'wide', 'warm', ['thump']),
    # Brücke: Freistoß im Olympia-Finale
    S(124, 128, C(FK, 41.6, focus=(0.5, 0.5), zoom=1.3), 'full', 'warm', ['push']),
    S(128, 130, C(FK, 46.5), 'scope', 'warm', ['thump']),
    S(130, 136, C(FK, 50.0, focus=(0.5, 0.45), zoom=1.1), 'wide', 'warm', ['push', 'dip']),

    # ── Druck (Breakdown) ────────────────────────────────────────────────────
    S(136, 144, C(STA, 12.0), 'slit', 'cold', ['drift', 'grain'], 'MARACANÃ'),
    S(144, 148, C(PRE, 46.0, focus=(0.5, 0.2), zoom=1.2), 'box43', 'bleak', ['push', 'grain']),
    S(148, 152, C(SO, 5.0, zoom=1.1), 'scope', 'bleak', ['grain']),
    S(152, 156, C(PEN, 18.5, focus=(0.5, 0.55), zoom=1.25), 'wide', 'bleak', ['push', 'grain']),
    S(156, 160, C(SO, 206.0, focus=(0.5, 0.4), zoom=1.1), 'square', 'bleak', ['grain']),
    S(160, 164, C(PEN, 11.0, focus=(0.5, 0.55), zoom=1.2), 'scope', 'bleak', ['grain']),
    S(164, 168, C(SO, 183.0, zoom=1.1), 'wide', 'bleak', ['push', 'grain']),
    S(168, 176, C(PEN, 20.5, focus=(0.4, 0.45), zoom=1.3, speed=0.6), 'scope', 'mono', ['push', 'grain']),
    S(176, 180, C(PRE, 70.0, focus=(0.5, 0.4), zoom=1.2), 'box43', 'mono', ['grain']),
    S(180, 184, C(SO, 133.0, zoom=1.1), 'slit', 'bleak', ['grain']),
    S(184, 192, C(PEN, 24.0, focus=(0.35, 0.45), zoom=1.2, speed=0.5), 'wide', 'mono', ['push', 'grain']),
    S(192, 196, C(SO, 207.5, focus=(0.5, 0.4), zoom=1.2), 'square', 'bleak', ['grain']),
    S(196, 200, C(PEN, 29.0, focus=(0.6, 0.52), zoom=1.9), 'slit', 'mono', ['grain']),

    # ── Anlauf (Build) ───────────────────────────────────────────────────────
    S(200, 202, C(PEN, 25.5, focus=(0.35, 0.45), zoom=1.3), 'scope', 'bleak', ['grain_heavy']),
    S(202, 204, C(SO, 209.0, focus=(0.5, 0.4), zoom=1.2), 'wide', 'bleak', ['grain']),
    S(204, 205, C(PRE, 48.0, focus=(0.5, 0.4), zoom=1.3), 'square', 'mono', ['thump']),
    S(205, 206, C(SO, 185.0, zoom=1.2), 'scope', 'bleak', []),
    S(206, 207, C(PEN, 19.0, focus=(0.5, 0.55), zoom=1.3), 'wide', 'bleak', []),
    S(207, 208, C(PEN, 26.5, focus=(0.36, 0.35), zoom=1.3), 'wide', 'mono', ['thump']),
    S(208, 212, C(PEN, 36.0, focus=(0.6, 0.52), zoom=1.9), 'scope', 'mono', ['push', 'grain']),
    # der Schuss: Ball im Netz genau auf dem Drop (Sync-Punkt PEN, audio.py)
    S(212, 216, C(PEN, 'PEN', focus=(0.6, 0.52), zoom=2.0, speed=0.5), 'scope', 'mono', ['squeeze']),

    # ── ALEGRIA (Drop 3) ─────────────────────────────────────────────────────
    S(216, 218, C(PEN, 44.8, focus=(0.5, 0.5), zoom=1.3), 'full', 'warm', ['flash', 'punch', 'grain']),
    S(218, 220, C(PEN, 50.0, focus=(0.5, 0.55), zoom=1.3), 'wide', 'warm', ['thump']),
    S(220, 222, C(PEN, 57.5, focus=(0.5, 0.55), zoom=1.2), 'scope', 'warm', ['punch']),
    S(222, 224, C(PEN, 66.0, focus=(0.5, 0.55), zoom=1.25), 'full', 'warm', ['thump']),
    S(224, 228, C(PEN, 108.5, focus=(0.5, 0.45), zoom=1.1), 'square', 'warm', ['push']),
    S(228, 232, C(PEN, 134.0, focus=(0.5, 0.45), zoom=1.1), 'wide', 'warm', ['push', 'grain']),
    S(232, 236, C(PEN, 150.5, focus=(0.5, 0.45), zoom=1.1), 'full', 'warm', ['push']),
    S(236, 240, C(PEN, 128.5, focus=(0.5, 0.45), zoom=1.1), 'scope', 'warm', ['grain']),
    S(240, 244, C(PEN, 111.8, focus=(0.5, 0.45), zoom=1.15), 'wide', 'warm', ['push', 'dip']),

    # ── Tränen (Loch) ────────────────────────────────────────────────────────
    S(244, 248, C(PEN, 152.0, focus=(0.5, 0.45), zoom=1.2, speed=0.4), 'slit', 'mono', ['push']),

    # ── Gold (Finale) ────────────────────────────────────────────────────────
    S(248, 250, C(MED, 24.3, focus=(0.5, 0.4), zoom=1.1), 'full', 'warm', ['open', 'punch']),
    S(250, 252, C(MED, 121.0), 'wide', 'warm', ['thump']),
    S(252, 256, C(SAM, 25.0), 'portrait', 'warm', ['push']),
    S(256, 258, C(PSG, 301.5, focus=(0.5, 0.4), zoom=1.1), 'scope', 'warm', ['punch']),
    S(258, 260, C(SFI, 374.0, focus=(0.5, 0.45), zoom=1.1), 'full', 'warm', []),
    S(260, 262, C(AUS, 38.0, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['thump']),
    S(262, 264, C(CRO, 77.0, focus=(0.5, 0.4)), 'square', 'warm', ['punch']),
    GRID(264, 272, [C(SCO, 323.0, focus=(0.5, 0.4)), C(PSG, 292.0, focus=(0.5, 0.4)), C(LON, 93.0, focus=(0.53, 0.54), zoom=1.12),
                    C(MED, 65.0, focus=(0.5, 0.4)), C(CRO, 78.0, focus=(0.5, 0.4)), C(AUS, 40.0, focus=(0.5, 0.4))],
         'warm', ['grain']),
    S(272, 276, C(SAM, 34.0), 'portrait', 'warm', ['push']),
    S(276, 280, C(MED, 124.0), 'wide', 'warm', ['push', 'grain']),

    # ── Coda ─────────────────────────────────────────────────────────────────
    CODA(280, C(MED, 20.0, focus=(0.5, 0.42), zoom=1.1, speed=0.6), 'NEYMAR JR', 'OUSADIA E ALEGRIA',
         fade_at=2.6, title_at=2.9),
]
