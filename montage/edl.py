#!/usr/bin/env python3
"""The edit decision list: which shot, from where, how long, how fast.

Three acts following the brightness arc of the footage.
  Akt 1  night city, slow and dark
  Akt 2  travel, dark and bright alternating, speed ramps, one burst
  Akt 3  sea and summer, bright, opening out

Fields per shot:
  clip  source stem
  at    in-point as a fraction of the source duration
  out   length on the finished timeline, in seconds
  rate  playback speed (0.4 = strong slow motion, 6.0 = very fast)
  look  which grade from looks.LOOKS
  tin   transition into this shot: None = hard cut, else (kind, seconds)
"""

TARGET_DURATION = 157.71   # exact length of the soundtrack

ACT1 = [
    # shot            at    out  rate  look     transition in
    ("IMG_3926", 0.30,  5.0, 0.60, "dark", ("black", 1.6)),
    ("IMG_4090", 0.25,  3.6, 0.50, "dark", ("fade", 0.9)),
    ("IMG_4209", 0.40,  4.4, 0.60, "dark", ("fade", 0.7)),
    ("IMG_4128", 0.20,  4.0, 1.00, "dark", None),
    ("IMG_4208", 0.30,  3.4, 0.80, "dark", None),
    ("IMG_3927", 0.35,  2.6, 1.50, "dark", None),
    ("IMG_3885", 0.25,  2.4, 1.20, "dark", ("fade", 0.5)),
    ("IMG_4130", 0.30,  3.0, 1.00, "dark", None),
    ("IMG_3833", 0.35,  3.4, 0.70, "dark", None),
    ("IMG_4426", 0.30,  2.8, 1.00, "dark", None),
    ("IMG_3847", 0.25,  2.6, 1.20, "dark", None),
    ("IMG_3925", 0.20,  6.2, 0.50, "dark", ("fade", 0.8)),
    ("IMG_3882", 0.30,  4.0, 0.80, "dark", None),
    ("IMG_4119", 0.25,  5.0, 0.50, "dark", ("fade", 1.0)),
]

ACT2 = [
    ("IMG_3886", 0.25,  2.4, 2.00, "mid", ("white", 0.25)),
    ("IMG_4148", 0.55,  1.6, 3.00, "mid", None),
    ("IMG_3960", 0.30,  2.0, 2.50, "mid", None),
    ("IMG_4121", 0.35,  2.6, 0.60, "mid", ("fade", 0.6)),
    ("IMG_3959", 0.45,  1.8, 4.00, "mid", None),
    ("IMG_4115", 0.30,  2.4, 0.50, "mid", ("fade", 0.5)),
    ("IMG_3961", 0.30,  2.0, 3.00, "mid", None),
    ("IMG_4079", 0.35,  3.0, 0.70, "mid", None),
    ("IMG_4055", 0.30,  1.5, 6.00, "mid", None),
    ("IMG_3870", 0.40,  3.0, 0.60, "mid", ("fade", 0.6)),
    ("IMG_4062", 0.30,  1.5, 5.00, "mid", None),
    ("IMG_3974", 0.35,  2.4, 0.50, "mid", None),
    ("IMG_4044", 0.30,  1.8, 3.00, "mid", None),
    ("IMG_3831", 0.30,  2.4, 1.00, "mid", None),
    ("IMG_4061", 0.30,  1.5, 4.00, "mid", None),
    ("IMG_3917", 0.30,  1.5, 3.00, "mid", None),
    ("IMG_4057", 0.30,  2.0, 2.00, "mid", None),
    ("IMG_4058", 0.30,  2.0, 2.00, "mid", ("fade", 0.4)),
    ("IMG_3966", 0.30,  1.8, 2.50, "mid", None),
    ("IMG_3918", 0.30,  1.6, 2.00, "mid", None),
    ("IMG_4027", 0.30,  1.8, 2.00, "mid", None),
    ("IMG_3968", 0.30,  1.4, 3.00, "mid", None),
    # --- Burst: Stakkato-Schnitte, angelehnt an die Referenz ---
    ("IMG_4064", 0.30, 0.22, 4.00, "mid", None),
    ("IMG_3871", 0.35, 0.18, 5.00, "mid", None),
    ("IMG_4056", 0.30, 0.18, 6.00, "mid", None),
    ("IMG_3828", 0.30, 0.22, 4.00, "mid", None),
    ("IMG_4101", 0.30, 0.18, 5.00, "mid", None),
    ("IMG_3997", 0.30, 0.18, 4.00, "mid", None),
    ("IMG_3998", 0.30, 0.22, 5.00, "mid", None),
    ("IMG_4207", 0.30, 0.18, 4.00, "mid", None),
    ("IMG_3824", 0.30, 0.18, 5.00, "mid", None),
    ("IMG_4177", 0.25, 0.22, 3.00, "mid", None),
    ("IMG_1074", 0.30, 0.18, 6.00, "mid", None),
    ("IMG_4028", 0.30, 0.18, 4.00, "mid", None),
    ("IMG_3960", 0.60, 0.22, 6.00, "mid", None),
    ("IMG_4085", 0.30, 0.18, 5.00, "mid", None),
    # --- Auflösung des Bursts ---
    ("IMG_3904", 0.30,  3.4, 0.50, "mid", ("white", 0.3)),
    ("IMG_3860", 0.35,  2.6, 1.50, "mid", None),
    ("IMG_3903", 0.30,  2.8, 0.60, "mid", None),
]

ACT3 = [
    ("IMG_4407", 0.30,  4.2, 0.50, "bright", ("fade", 1.2)),
    ("IMG_4182", 0.30,  3.4, 0.60, "bright", None),
    ("IMG_4084", 0.35,  3.4, 0.70, "bright", None),
    ("IMG_4181", 0.40,  3.2, 0.40, "bright", ("fade", 0.5)),
    ("IMG_4029", 0.35,  3.4, 0.60, "bright", None),
    ("IMG_1247", 0.30,  3.0, 0.70, "bright", None),
    ("IMG_4075", 0.30,  3.4, 0.60, "bright", ("fade", 0.6)),
    ("IMG_4393", 0.30,  2.8, 0.80, "bright", None),
    ("IMG_4082", 0.25,  2.4, 1.00, "bright", None),
    ("IMG_4212", 0.10,  5.2, 0.60, "bright", ("fade", 0.7)),
    ("IMG_3879", 0.30,  3.4, 0.70, "bright", None),
    ("IMG_4424", 0.25,  4.0, 0.50, "bright", ("fade", 0.9)),
    ("IMG_3827", 0.30,  4.6, 0.60, "bright", ("fade", 1.1)),
]

TIMELINE = ACT1 + ACT2 + ACT3

# act boundaries as indices into TIMELINE, used for sound design accents
ACT_STARTS = {0: "akt1", len(ACT1): "akt2", len(ACT1) + len(ACT2): "akt3"}
BURST_RANGE = (len(ACT1) + 22, len(ACT1) + 36)
