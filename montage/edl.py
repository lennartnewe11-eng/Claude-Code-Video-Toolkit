#!/usr/bin/env python3
"""The edit decision list: which shot, from where, how long, how fast.

Shot lengths are counted in BEATS, not seconds. Fitting a uniform grid to
"Still Life" gives 108.33 BPM - one beat every 0.554s. 283 beats fill the
film. Cut positions are accumulated in beats and converted to frames
once, so they sit on the grid instead of drifting off it.

Density is varied deliberately rather than held steady: a run of 4-beat
shots drops to 2, or to 1, and comes back. The staccato passage cuts on
the half beat.

The act boundaries sit on measured swells in the same track: a very quiet
opening (0-10s, around -33 dBFS), swells roughly every twelve seconds
through the middle, a second peak at 110-120s, a breakdown at 120-130s
and a fade from 150s.

  Akt 1  night city      0.0  -  47.6s    85 beats
  Akt 2  travel         47.6  - 110.4s   113 beats
  Akt 3  sea and light 110.4  - 157.7s    85 beats

Slow motion is spent where a person is moving in the middle of frame -
the jump into the water, the swimmers, the walk down the alley. Sunsets
and sea surfaces run close to real time; slowing them buys nothing and
only makes the film feel sluggish.

Fields per shot:
  clip  source stem
  at    in-point as a fraction of the source duration
  beats length on the finished timeline, in beats (0.5 allowed)
  rate  playback speed (0.4 = strong slow motion, 6.0 = very fast)
  look  which grade from looks.LOOKS
  tin   transition into this shot: None = hard cut, else (xfade name, seconds)
  move  in-shot camera move: "in", "out" or None
  amb   take the clip's own sound, quietly, under the music
"""

TARGET_DURATION = 157.71   # exact length of the soundtrack
BPM = 108.33               # fitted to the track, not just estimated
BEAT = 60.0 / BPM          # 0.5539s
GRID_OFFSET = 0.410        # where the fitted grid starts

# A uniform grid still sits about 90 ms from the detected beats on average:
# an ambient score is not metronomic, so there is no exact beat to hit. The
# grid is here to give the cutting a steady pulse, not a false precision.


# --- Vorspann: laeuft VOR der Musik, nur mit dem Ton der Clips -----------
# Erst ein paar ruhige Einstellungen, dann der doppelt so schnell
# geschnittene Teil - und erst danach setzt der Soundtrack ein.
PROLOG_CALM = [
    ("IMG_3926", 0.30,  7,  1.00, "dark", None,           None, True),
    ("IMG_4209", 0.40,  6,  1.00, "dark", ("fade", 0.20), None, True),
    ("IMG_4128", 0.20,  6,  1.00, "dark", None,           None, True),
    ("IMG_4208", 0.30,  5,  1.00, "dark", None,           None, True),
]

PROLOG_FAST = [
    ("IMG_4064", 0.30, 0.5, 1.00, "mid", None, None, False),
    ("IMG_3871", 0.35, 0.5, 1.00, "mid", None, None, False),
    ("IMG_4056", 0.55, 0.5, 1.00, "mid", None, None, False),
    ("IMG_3828", 0.55, 0.5, 1.00, "mid", None, None, False),
    ("IMG_4101", 0.60, 0.5, 1.00, "mid", None, None, False),
    ("IMG_3997", 0.30, 0.5, 1.00, "mid", None, None, False),
    ("IMG_3998", 0.60, 0.5, 1.00, "mid", None, None, False),
    ("IMG_4207", 0.30, 0.5, 1.00, "mid", None, None, False),
    ("IMG_3824", 0.55, 0.5, 1.00, "mid", None, None, False),
    ("IMG_4177", 0.55, 0.5, 1.00, "mid", None, None, False),
    ("IMG_1074", 0.55, 0.5, 1.00, "mid", None, None, False),
    ("IMG_4028", 0.55, 0.5, 1.00, "mid", None, None, False),
    ("IMG_3960", 0.60, 0.5, 1.00, "mid", None, None, False),
    ("IMG_4085", 0.55, 0.5, 1.00, "mid", None, None, False),
]

PROLOG = PROLOG_CALM + PROLOG_FAST

# --- Akt 1: Nacht - 85 Beats ---------------------------------------------
ACT1 = [
    # clip        at   beats rate  look    transition in   move   amb
    ("IMG_3926", 0.30, 12,  0.80, "dark", None,           "in", True),
    ("IMG_4090", 0.25,  8,  0.70, "dark", None,           None, True),
    ("IMG_4209", 0.40,  6,  0.80, "dark", ("fade", 0.20), None,  True),
    ("IMG_4128", 0.20,  6,  0.50, "dark", None,           None, True),   # Gang
    ("IMG_4208", 0.30,  4,  1.00, "dark", None,           None, True),
    # Verdichtung: vier Shots auf je zwei Beats
    ("IMG_3927", 0.35,  2,  1.00, "dark", None,           None, True),
    ("IMG_3885", 0.25,  2,  1.00, "dark", None,           None, True),
    ("IMG_4130", 0.30,  2,  1.00, "dark", None,           None, True),
    ("IMG_3833", 0.35,  2,  1.00, "dark", None,           None, True),
    # und wieder aufmachen
    ("IMG_3847", 0.25,  4,  1.00, "dark", None,           None, True),
    ("IMG_4426", 0.30,  6,  0.60, "dark", None,           None, True),   # Tisch
    ("IMG_3925", 0.20, 13,  0.80, "dark", ("fade", 0.17), "in",  True),
    ("IMG_3882", 0.30, 10,  0.90, "dark", None,           None, True),
    ("IMG_4119", 0.25,  8,  0.70, "dark", ("fade", 0.23), None,  True),
]

# --- Akt 2: Bewegung - 113 Beats -----------------------------------------
ACT2 = [
    ("IMG_3886", 0.25,  4,  1.00, "mid", ("fade", 0.20), None, True),    # Bahnhof
    ("IMG_4148", 0.55,  2,  1.00, "mid", None,           None, False),
    ("IMG_3960", 0.30,  4,  1.00, "mid", None,           None, False),
    ("IMG_4121", 0.35,  8,  0.90, "mid", None,           None, False),
    ("IMG_3959", 0.45,  2,  1.00, "mid", None,           None, False),
    ("IMG_4115", 0.30,  4,  0.90, "mid", ("fade", 0.13), None, False),
    ("IMG_3961", 0.30,  2,  1.00, "mid", None,           None, True),    # Zug
    ("IMG_4079", 0.35,  8,  0.90, "mid", None,           None, True),    # Meer
    ("IMG_4055", 0.30,  1,  1.00, "mid", None,           None, False),   # ein Beat
    ("IMG_3870", 0.40,  7,  0.90, "mid", None,           None, False),
    ("IMG_4062", 0.30,  1,  1.00, "mid", None,           None, False),   # ein Beat
    ("IMG_3974", 0.35,  5,  0.90, "mid", ("fade", 0.17), None, False),
    ("IMG_4044", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3831", 0.30,  5,  1.00, "mid", None,           None, False),
    ("IMG_4056", 0.30,  4,  1.00, "mid", None,           None, False),
    ("IMG_4061", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3917", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3828", 0.30,  4,  1.00, "mid", None,           None, False),
    ("IMG_4057", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_4058", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_4101", 0.30,  4,  1.00, "mid", None,           None, False),
    ("IMG_3966", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3918", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3998", 0.30,  4,  0.90, "mid", ("fade", 0.13), None, False),
    ("IMG_4027", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_4085", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_4177", 0.25,  2,  1.00, "mid", None,           None, False),
    ("IMG_1074", 0.30,  4,  1.00, "mid", None,           None, False),
    ("IMG_4028", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3824", 0.30,  2,  1.00, "mid", None,           None, False),
    ("IMG_3968", 0.30,  2,  1.00, "mid", None,           None, False),
    # --- Aufloesung
    ("IMG_3904", 0.30,  6,  0.70, "mid", ("fade", 0.20), "in", False),
    ("IMG_3860", 0.35,  4,  1.00, "mid", None,           None, False),
    ("IMG_3903", 0.30,  4,  0.90, "mid", ("fade", 0.17), None, False),
]

# --- Akt 3: Licht - 85 Beats ---------------------------------------------
ACT3 = [
    ("IMG_4407", 0.30,  6,  0.90, "bright", ("fade", 0.23), "in",  True),
    ("IMG_4182", 0.30,  6,  0.90, "bright", None,           None,  False),
    ("IMG_4084", 0.35,  6,  0.70, "bright", None,           None,  True),   # Steg
    ("IMG_4181", 0.40, 10,  0.40, "bright", ("fade", 0.13), None,  True),   # Sprung
    ("IMG_4029", 0.35,  8,  0.50, "bright", None,           None,  True),   # Schwimmen
    ("IMG_1247", 0.30,  6,  0.55, "bright", None,           None,  True),   # Schwimmer
    ("IMG_4075", 0.30,  6,  0.90, "bright", ("fade", 0.17), None,  False),
    ("IMG_4393", 0.30,  4,  0.80, "bright", None,           None,  False),
    ("IMG_4082", 0.25,  4,  0.60, "bright", None,           None,  True),
    ("IMG_4212", 0.10, 10,  0.70, "bright", ("fade", 0.20), "out", True),   # Wellen
    ("IMG_3879", 0.30,  6,  0.90, "bright", None,           None,  False),
    ("IMG_4424", 0.25,  5,  0.90, "bright", None,           "out", False),
    ("IMG_3827", 0.30,  8,  0.90, "bright", ("fade", 0.23), "in",  False),
]

TIMELINE = PROLOG + ACT1 + ACT2 + ACT3
N_PROLOG = len(PROLOG)

ACT_STARTS = {N_PROLOG: "akt1", N_PROLOG + len(ACT1): "akt2",
              N_PROLOG + len(ACT1) + len(ACT2): "akt3"}
BURST_RANGE = (len(PROLOG_CALM), len(PROLOG))   # jetzt im Vorspann

# The opening carries a steady pulse of clicks rather than scattered
# accents: every second beat from here to here, so it reads as a rhythm.
OPENING_PULSE = (2.4, 22.0, 2)     # from, to, every N beats

MUSIC_SWELLS = [11.5, 35.6, 47.6, 59.7, 71.6, 83.6, 89.6, 92.7, 100.0,
                104.9, 128.5, 134.5, 138.3, 145.0, 150.1]
MUSIC_BREAKDOWN = (120.0, 130.0)
