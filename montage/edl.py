#!/usr/bin/env python3
"""The edit decision list: which shot, from where, how long, how fast.

The act boundaries are not guesses - they sit on measured swells in the
soundtrack. Analysing "Still Life" gave a very quiet opening (0-10s, around
-33 dBFS), a rise to -16 by 0:20, swells roughly every twelve seconds
through the middle (35.6, 47.6, 59.7, 71.6, 83.6, 89.6, 92.7, 100.0,
104.9s), a second peak at 110-120s, a clear breakdown at 120-130s
(-24.6 dBFS) and a fade from 150s.

So:
  Akt 1  night city      0.0  -  47.6s   ends on the 47.6s swell
  Akt 2  travel         47.6  - 110.4s   staccato burst on the 100/105 pair
  Akt 3  sea and light 110.4  - 157.7s   opens on the second peak, breathes
                                         through the 120-130s breakdown

Fields per shot:
  clip  source stem
  at    in-point as a fraction of the source duration
  out   length on the finished timeline, in seconds
  rate  playback speed (0.4 = strong slow motion, 6.0 = very fast)
  look  which grade from looks.LOOKS
  tin   transition into this shot: None = hard cut, else (xfade name, seconds)

Measuring the reference settled the cutting style: it runs 80% hard cuts,
and where it does dissolve the dissolve lasts 0.10-0.23s (median 0.17) -
three to seven frames. Wipes, slides, pixelise and the rest of that
vocabulary do not appear in it at all. So there is one soft transition
here, a short dissolve, used on 13 of 71 cuts.
  move  in-shot camera move: "in", "out" or None
"""

TARGET_DURATION = 157.71   # exact length of the soundtrack

# --- Akt 1: Nacht - lange Einstellungen -----------------------------------
ACT1 = [
    # clip          at    out  rate  look     transition in        move
    ("IMG_3926", 0.30,  5.0, 0.60, "dark", None, "in"),
    ("IMG_4090", 0.25,  3.4, 0.50, "dark", None, None),
    ("IMG_4209", 0.40,  4.2, 0.60, "dark", ("fade", 0.20), None),
    ("IMG_4128", 0.20,  3.8, 1.00, "dark", None, None),
    ("IMG_4208", 0.30,  3.2, 0.80, "dark", None, None),
    ("IMG_3927", 0.35,  2.4, 1.50, "dark", None, None),
    ("IMG_3885", 0.25,  2.4, 1.20, "dark", None, None),
    ("IMG_4130", 0.30,  2.8, 1.00, "dark", None, None),
    ("IMG_3833", 0.35,  3.2, 0.70, "dark", None, None),
    ("IMG_4426", 0.30,  2.6, 1.00, "dark", None, None),
    ("IMG_3847", 0.25,  2.4, 1.20, "dark", None, None),
    ("IMG_3925", 0.20,  5.6, 0.50, "dark", ("fade", 0.17), "in"),
    ("IMG_3882", 0.30,  3.6, 0.80, "dark", None, None),
    ("IMG_4119", 0.25,  3.0, 0.50, "dark", ("fade", 0.23), None),
]

# --- Akt 2: Bewegung - Tempowechsel ---------------------------------------
ACT2 = [
    ("IMG_3886", 0.25,  2.2, 2.00, "mid", ("fade", 0.20), None),
    ("IMG_4148", 0.55,  1.5, 3.00, "mid", None, None),
    ("IMG_3960", 0.30,  1.9, 2.50, "mid", None, None),
    ("IMG_4121", 0.35,  2.4, 0.60, "mid", None, None),
    ("IMG_3959", 0.45,  1.7, 4.00, "mid", None, None),
    ("IMG_4115", 0.30,  2.2, 0.50, "mid", ("fade", 0.13), None),
    ("IMG_3961", 0.30,  1.9, 3.00, "mid", None, None),
    ("IMG_4079", 0.35,  2.8, 0.70, "mid", None, None),
    ("IMG_4055", 0.30,  1.4, 6.00, "mid", None, None),
    ("IMG_3870", 0.40,  2.8, 0.60, "mid", None, None),
    ("IMG_4062", 0.30,  1.4, 5.00, "mid", None, None),
    ("IMG_3974", 0.35,  2.2, 0.50, "mid", ("fade", 0.17), None),
    ("IMG_4044", 0.30,  1.7, 3.00, "mid", None, None),
    ("IMG_3831", 0.30,  2.2, 1.00, "mid", None, None),
    ("IMG_4056", 0.30,  2.4, 1.50, "mid", None, None),
    ("IMG_4061", 0.30,  1.4, 4.00, "mid", None, None),
    ("IMG_3917", 0.30,  1.4, 3.00, "mid", None, None),
    ("IMG_3828", 0.30,  2.6, 0.80, "mid", None, None),
    ("IMG_4057", 0.30,  1.9, 2.00, "mid", None, None),
    ("IMG_4058", 0.30,  1.9, 2.00, "mid", None, None),
    ("IMG_4101", 0.30,  2.2, 1.20, "mid", None, None),
    ("IMG_3966", 0.30,  1.7, 2.50, "mid", None, None),
    ("IMG_3918", 0.30,  1.5, 2.00, "mid", None, None),
    ("IMG_3998", 0.30,  2.4, 0.70, "mid", ("fade", 0.13), None),
    ("IMG_4027", 0.30,  1.7, 2.00, "mid", None, None),
    ("IMG_4085", 0.30,  1.1, 0.80, "mid", None, None),
    ("IMG_3968", 0.30,  1.3, 2.60, "mid", None, None),
    # --- Stakkato: 14 Schnitte in unter drei Sekunden, auf dem Swell-Paar
    ("IMG_4064", 0.30, 0.20, 4.00, "mid", None, None),
    ("IMG_3871", 0.35, 0.20, 5.00, "mid", None, None),
    ("IMG_4056", 0.55, 0.20, 6.00, "mid", None, None),
    ("IMG_3828", 0.55, 0.20, 4.00, "mid", None, None),
    ("IMG_4101", 0.60, 0.20, 5.00, "mid", None, None),
    ("IMG_3997", 0.30, 0.20, 4.00, "mid", None, None),
    ("IMG_3998", 0.60, 0.20, 5.00, "mid", None, None),
    ("IMG_4207", 0.30, 0.20, 4.00, "mid", None, None),
    ("IMG_3824", 0.30, 0.20, 5.00, "mid", None, None),
    ("IMG_4177", 0.25, 0.20, 3.00, "mid", None, None),
    ("IMG_1074", 0.30, 0.20, 6.00, "mid", None, None),
    ("IMG_4028", 0.30, 0.20, 4.00, "mid", None, None),
    ("IMG_3960", 0.60, 0.20, 6.00, "mid", None, None),
    ("IMG_4085", 0.55, 0.20, 5.00, "mid", None, None),
    # --- Aufloesung
    ("IMG_3904", 0.30,  3.2, 0.50, "mid", ("fade", 0.20), "in"),
    ("IMG_3860", 0.35,  2.4, 1.50, "mid", None, None),
    ("IMG_3903", 0.30,  2.6, 0.60, "mid", ("fade", 0.17), None),
]

# --- Akt 3: Licht - langes Ausatmen ---------------------------------------
ACT3 = [
    ("IMG_4407", 0.30,  4.0, 0.50, "bright", ("fade", 0.23), "in"),
    ("IMG_4182", 0.30,  3.2, 0.60, "bright", None, None),
    ("IMG_4084", 0.35,  3.2, 0.70, "bright", None, None),
    ("IMG_4181", 0.40,  3.0, 0.40, "bright", ("fade", 0.13), None),
    ("IMG_4029", 0.35,  3.2, 0.60, "bright", None, None),
    ("IMG_1247", 0.30,  2.8, 0.70, "bright", None, None),
    ("IMG_4075", 0.30,  3.2, 0.60, "bright", ("fade", 0.17), None),
    ("IMG_4393", 0.30,  2.6, 0.80, "bright", None, None),
    ("IMG_4082", 0.25,  2.2, 1.00, "bright", None, None),
    ("IMG_4212", 0.10,  6.5, 0.60, "bright", ("fade", 0.20), "out"),
    ("IMG_3879", 0.30,  3.2, 0.70, "bright", None, None),
    ("IMG_4424", 0.25,  3.8, 0.50, "bright", None, "out"),
    ("IMG_3827", 0.30,  6.4, 0.60, "bright", ("fade", 0.23), "in"),
]

TIMELINE = ACT1 + ACT2 + ACT3

ACT_STARTS = {0: "akt1", len(ACT1): "akt2", len(ACT1) + len(ACT2): "akt3"}
BURST_RANGE = (len(ACT1) + 27, len(ACT1) + 41)

# where the soundtrack builds, measured from its own envelope - the sound
# design leans on these rather than on the cut list
MUSIC_SWELLS = [11.5, 35.6, 47.6, 59.7, 71.6, 83.6, 89.6, 92.7, 100.0,
                104.9, 128.5, 134.5, 138.3, 145.0, 150.1]
MUSIC_BREAKDOWN = (120.0, 130.0)
