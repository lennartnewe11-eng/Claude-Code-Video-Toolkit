"""EDL: Neymar — OUSADIA E ALEGRIA.

Eine Emotion: Freude. Sie wird gespielt (Skills), dann angehalten (Druck im
Maracanã) und bricht mit dem letzten Elfmeter für Brasiliens erstes
olympisches Gold als Freudentränen wieder aus.

Ausgabe-Beat k = Song-Beat - 152 (der Song läuft an einem Stück, siehe timeline.py).

  k   0– 60  Groove      GINGA      Santos, London, Confed Cup: der Junge, der spielt   faded → warm
  k  60– 96  Mitte       SHOW       Barça, PSG, Seleção: Skills, im Hochformat, wo     warm
                                    die Quelle hochkant ist
  k  96–104  Loch        Atem       ein Gesicht in Zeitlupe                             mono
  k 104–136  Drop 2      Skills     die schnellste Stelle: Dribblings in Einer-Trauben, warm
                                    Kroatien 2022, am Ende der Freistoß im Maracanã
  k 136–200  Breakdown   DRUCK      Maracanã bei Nacht, Elfmeterschießen, Stille       bleak / mono
  k 200–216  Build       ANLAUF     Neymar legt sich den Ball hin, Schnitte werden     bleak
                                    schneller, Band zieht sich zusammen
  k 216–244  Drop 3      ALEGRIA    Ball im Netz genau auf dem Drop, Freudentränen     warm
  k 244–248  Loch        Tränen     ein Bild, still
  k 248–280  Finale      Gold       Medaille, Samba, jedes Lachen noch einmal           warm
  Coda                              Ausklang, Titel

Hochformat-Quellen (TikTok-Schnitte, Samba) laufen im Portrait-Band: das Band
zeigt, woher das Bild kommt, statt es aufzublasen.
"""

LON = 'src/london12.mp4'
SCO = 'src/santos_colo.mp4'
SFI = 'src/santos_final11.mp4'
AUS = 'src/aus13.ts'
CON = 'src/confed13_hl.mp4'
FRI = 'src/friends.ts'
SPE = 'src/speciale.mkv'
PSG = 'src/psg17_end.mp4'
TIK = 'src/tiktok_skills.mp4'
HUM = 'src/humiliated.webm'
SAM = 'src/samba.mp4'
CRO = 'cuts/cro22.mp4'
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
    # ── GINGA ────────────────────────────────────────────────────────────────
    S(0, 4, C(SCO, 333.8, focus=(0.5, 0.4), zoom=1.1), 'box43', 'faded', ['grain_heavy', 'push'], 'SANTOS'),
    S(4, 6, C(SCO, 349.2, zoom=1.1), 'full', 'faded', ['grain']),
    S(6, 8, C(SCO, 361.0, zoom=1.1), 'scope', 'faded', ['grain']),
    S(8, 9, C(SCO, 355.0, zoom=1.2), 'wide', 'faded', []),
    S(9, 10, C(SCO, 367.3, zoom=1.1), 'full', 'faded', ['thump']),
    S(10, 12, C(SCO, 358.0, zoom=1.1), 'scope', 'warm', ['punch']),
    S(12, 16, C(SCO, 372.6, focus=(0.5, 0.4), zoom=1.1), 'wide', 'warm', ['thump', 'grain']),
    S(16, 18, C(LON, 9.5, focus=(0.55, 0.45), zoom=1.2), 'square', 'mono', ['grain_heavy']),
    S(18, 20, C(LON, 19.5, focus=(0.53, 0.54), zoom=1.12), 'box43', 'mono', ['grain_heavy']),
    S(20, 22, C(SFI, 373.5, focus=(0.5, 0.45), zoom=1.1), 'full', 'warm', ['punch', 'grain']),
    S(22, 24, C(SFI, 401.0, focus=(0.5, 0.45), zoom=1.1), 'scope', 'warm', ['grain']),
    S(24, 26, C(LON, 40.0, focus=(0.53, 0.54), zoom=1.12), 'full', 'warm', ['punch']),
    S(26, 27, C(LON, 43.0, focus=(0.53, 0.54), zoom=1.12), 'wide', 'warm', []),
    S(27, 28, C(LON, 57.0, focus=(0.53, 0.54), zoom=1.12), 'scope', 'warm', []),
    S(28, 29, C(LON, 60.5, focus=(0.53, 0.54), zoom=1.12), 'full', 'warm', ['thump']),
    S(29, 30, C(LON, 63.0, focus=(0.53, 0.54), zoom=1.12), 'square', 'warm', ['rgbhit']),
    S(30, 32, C(LON, 73.0, focus=(0.53, 0.54), zoom=1.12), 'wide', 'warm', ['punch']),
    S(32, 36, C(AUS, 36.0, focus=(0.5, 0.4), zoom=1.1), 'full', 'warm', ['push', 'thump']),
    S(36, 38, C(CON, 403.6, zoom=1.1), 'scope', 'warm', ['punch']),
    S(38, 40, C(CON, 404.6, zoom=1.1), 'wide', 'warm', ['grain']),
    S(40, 44, C(FRI, 16.0, focus=(0.5, 0.4)), 'box43', 'warm', ['push']),
    S(44, 46, C(FRI, 47.0, zoom=1.2), 'full', 'warm', ['punch']),
    S(46, 48, C(FRI, 50.0, zoom=1.2), 'scope', 'warm', []),
    # Mosaik: vier Szenen laufen durch, auf jedem Beat springt die Anordnung
    GRID(48, 56, [C(SCO, 350.0, zoom=1.1), C(LON, 58.0, focus=(0.53, 0.54), zoom=1.12), C(LON, 74.0, focus=(0.53, 0.54), zoom=1.12), C(SCO, 362.0, zoom=1.1),
                  C(LON, 158.0, focus=(0.53, 0.54), zoom=1.12), C(FRI, 41.0, zoom=1.2)], 'warm', ['grain']),
    S(56, 58, C(CON, 769.6, focus=(0.5, 0.45), zoom=1.1), 'square', 'warm', ['push']),
    S(58, 60, C(CON, 772.3, focus=(0.5, 0.45), zoom=1.1), 'wide', 'warm', ['dip']),

    # ── SHOW ─────────────────────────────────────────────────────────────────
    S(60, 64, C(SPE, 485.0, focus=(0.5, 0.45)), 'full', 'warm', ['open', 'push'], 'BARCELONA'),
    S(64, 68, C(HUM, 7.0, zoom=1.15), 'portrait', 'warm', ['push']),
    S(68, 70, C(HUM, 19.5, zoom=1.15), 'portrait', 'warm', []),
    S(70, 72, C(TIK, 3.0, zoom=1.3), 'portrait', 'warm', ['punch']),
    S(72, 74, C(PSG, 292.5, focus=(0.5, 0.4), zoom=1.1), 'scope', 'warm', ['thump']),
    S(74, 76, C(PSG, 300.5, focus=(0.5, 0.4), zoom=1.1), 'square', 'warm', []),
    S(76, 80, C(TIK, 10.0, zoom=1.3), 'portrait', 'warm', ['push']),
    S(80, 82, C(SPE, 648.0, zoom=1.1), 'full', 'warm', ['punch']),
    S(82, 84, C(SPE, 655.0, zoom=1.1), 'wide', 'warm', []),
    S(84, 86, C(HUM, 33.5, zoom=1.15), 'portrait', 'warm', ['thump']),
    S(86, 88, C(TIK, 38.0, zoom=1.3), 'portrait', 'warm', []),
    S(88, 92, C(LON, 92.0, focus=(0.53, 0.45), zoom=1.12), 'full', 'warm', ['push']),
    S(92, 96, C(LON, 160.0, focus=(0.53, 0.54), zoom=1.12), 'scope', 'warm', ['drift', 'dip']),

    # ── Atem ─────────────────────────────────────────────────────────────────
    S(96, 104, C(FRI, 20.0, focus=(0.5, 0.55), zoom=1.25, speed=0.5), 'slit', 'mono', ['push', 'grain']),

    # ── Skills (Drop 2) ──────────────────────────────────────────────────────
    S(104, 106, C(CRO, 24.5), 'full', 'warm', ['open', 'punch']),
    S(106, 108, C(CRO, 28.0), 'scope', 'warm', []),
    S(108, 109, C(CRO, 31.0), 'full', 'warm', ['thump']),
    S(109, 110, C(CRO, 76.0, focus=(0.5, 0.4)), 'square', 'warm', ['rgbhit']),
    S(110, 112, C(TIK, 16.0, zoom=1.3), 'portrait', 'warm', ['punch']),
    S(112, 113, C(TIK, 40.0, zoom=1.3), 'portrait', 'warm', []),
    S(113, 114, C(HUM, 21.5, zoom=1.15), 'portrait', 'warm', []),
    S(114, 116, C(LON, 61.0, focus=(0.53, 0.54), zoom=1.12), 'wide', 'warm', ['punch']),
    S(116, 117, C(LON, 75.0, focus=(0.53, 0.54), zoom=1.12), 'full', 'warm', []),
    S(117, 118, C(LON, 162.0, focus=(0.53, 0.54), zoom=1.12), 'scope', 'warm', ['thump']),
    S(118, 120, C(LON, 118.0, focus=(0.53, 0.54), zoom=1.12), 'wide', 'warm', ['punch']),
    S(120, 122, C(FRI, 52.0, zoom=1.2), 'full', 'warm', []),
    S(122, 123, C(SPE, 652.0, zoom=1.1), 'scope', 'warm', []),
    S(123, 124, C(HUM, 9.0, zoom=1.15), 'portrait', 'warm', ['rgbhit']),
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
