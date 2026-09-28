"""The edit: every shot, text and effect is placed on the song's beat grid.

Song structure (bar = 4 beats, ~117.6 bpm, times are song seconds):
  bar   0  5.07  intro fade-in             bar  56 118.57 "la la la" / alors on chante
  bar   4 12.80  synth riff                bar  64 134.83 build (kick back)
  bar   8 20.94  "alors on danse" x4       bar  70 147.03 pre-drop break (silence 149.7)
  bar  12 29.08  verse 1 ("qui dit ...")   bar  72 151.10 DROP 2 / chorus 2
  bar  28 61.61  DROP 1 / chorus 1         bar  87 181.62 breakdown ("encore")
  bar  44 94.17  "c'est fini" + break      bar  96 199.92 final chorus
  bar  48 102.29 verse 2                   bar 104 216.20 outro
Clips are grouped by trip leg and play in travel order:
Praha -> Wien -> Budapest -> Alps/Bled -> train to Croatia -> Rijeka coast ->
Istria -> last leg (Sep).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

MONEY = "C8E8B15B-0FC8-4285-9392-381CD4DFA550"   # portrait clip (euro notes)
NIGHT = "F004091A-F728-4E64-A85C-648E6E44041D"   # portrait clip (city at night)


def load_beats():
    with open(os.path.join(HERE, "beats.json")) as f:
        return json.load(f)["beats"]


def at(bar, beat=0.0):
    """Beat index of `beat` within `bar` (bar 0 downbeat = beat index 3)."""
    return 3 + 4 * bar + beat


# ----------------------------------------------------------------------------
# shots
# ----------------------------------------------------------------------------

def V(src, t, b, **kw):
    return dict(kind="v", src=src, t=t, b=b, **kw)


def P(src, b, **kw):
    return dict(kind="p", src=src, b=b, **kw)


def SPLIT(srcs, b, **kw):
    return dict(kind="split", src=srcs, b=b, **kw)


def STROBE(items, each=0.5, **kw):
    out = []
    for i, (src, t) in enumerate(items):
        out.append(V(src, t, each, punch=0.10, flash=0.55, flash_tau=0.05, strobe=True, **kw))
    return out


def shots():
    S = []
    add = S.append
    ext = S.extend

    # --- A  intro, bars 0-3: black & white, birds, letterboxed ----------------
    add(V("IMG_3827", 0.2, 8, look="bw", z0=1.0, z1=1.12, sp=0.8))
    add(V("IMG_3851", 5.35, 8, look="bw", z0=1.04, z1=1.18, flash=0.25))

    # --- B  riff, bars 4-7: Praha by day -------------------------------------
    add(V("IMG_3760", 0.4, 2, punch=0.14, flash=1.0, shake=10))
    add(V("IMG_3762", 1.0, 2, punch=0.10, sp=1.3))
    add(V("IMG_3762", 6.4, 2, punch=0.10, sp=1.3))
    add(SPLIT(["IMG_3770", "IMG_3796"], 2, reveal=1.0, focus=[(0.5, 0.35), (0.5, 0.3)]))
    add(V("IMG_3824", 0.8, 4, z0=1.0, z1=1.12, look="warm"))
    add(V("IMG_3827", 8.6, 4, sp=0.9, look="warm", punch=0.06))

    # --- C  "alors on danse" x4, bars 8-11: Praha evening ----------------------
    add(V("IMG_3828", 0.8, 4, punch=0.12, flash=0.9, sp=1.3))
    add(V("IMG_3828", 8.4, 4, sp=0.95))
    add(V("IMG_3831", 0.5, 4, z0=1.12, z1=1.0, look="warm"))
    add(V("IMG_3833", 1.0, 2, look="night", ev=1.25))
    add(V("IMG_3833", 11.0, 2, look="night", ev=1.2, z0=1.0, z1=1.15))

    # --- D  verse 1, bars 12-27: Praha at dawn -> train -> Wien ---------------
    add(V("IMG_3847", 0.2, 4, look="night", z0=1.0, z1=1.08, flash=0.5))       # bar 12
    add(V("IMG_3852", 0.3, 4, z0=1.08, z1=1.0))                                # bar 13
    add(V("IMG_3860", 1.0, 1, punch=0.08))                                     # bar 14
    add(V(MONEY, 0.1, 3, mode="tri", reveal=1.0, punch=0.06, sp=0.75))
    add(V("IMG_3860", 6.0, 4, z0=1.12, z1=1.0))                                # bar 15
    add(V("IMG_3870", 1.0, 4, look="warm"))                                    # bar 16
    add(V("IMG_3870", 7.5, 4, look="warm", z0=1.0, z1=1.1))                    # bar 17
    add(P("IMG_3850", 4, z0=1.0, z1=1.14, fy=0.5, look="warm"))                # bar 18
    add(V("IMG_3870", 16.6, 2, look="warm", punch=0.08))                       # bar 19
    add(V("IMG_3870", 18.8, 2, look="warm", punch=0.08))
    add(V("IMG_3870", 20.8, 4, look="warm", z0=1.05, z1=1.0))                  # bar 20
    add(V("IMG_3860", 13.0, 4, z0=1.0, z1=1.18))                               # bar 21
    add(V("IMG_3875", 0.3, 4))                                                 # bar 22
    add(V("IMG_3879", 0.5, 4, z0=1.0, z1=1.06))                                # bar 23
    add(SPLIT(["IMG_3876", "IMG_3877", "IMG_3878"], 3, reveal=1.0,             # bar 24
              focus=[(0.5, 0.55), (0.5, 0.55), (0.45, 0.55)]))
    add(V("IMG_3871", 0.6, 3, punch=0.16, flash=0.6, shake=6))                 # "réveil"
    add(V("IMG_3879", 5.0, 2, sp=1.2))
    add(V("IMG_3882", 0.5, 4, look="night", z0=1.0, z1=1.08, flash=0.4))       # bar 26
    add(V("IMG_3885", 0.5, 2, look="night", ev=1.15))                          # bar 27
    ext(STROBE([("IMG_3886", 0.3), ("IMG_3885", 3.0), ("IMG_3886", 1.4), ("IMG_3882", 5.0)],
               look="night"))

    # --- E  DROP 1 / chorus 1, bars 28-43: Wien -> Budapest -------------------
    add(V("IMG_3886", 3.2, 4, punch=0.2, flash=1.0, flash_tau=0.25, shake=22, look="night"))
    add(V("IMG_3897", 0.0, 2, sp=2.0, punch=0.10, look="vivid"))              # bar 29
    add(V("IMG_3897", 4.4, 2, punch=0.08, look="vivid"))
    add(V("IMG_3903", 0.2, 1, punch=0.10, rot0=-4, rot1=4))                    # bar 30
    add(V("IMG_3903", 4.3, 1, punch=0.10, rot0=4, rot1=-4))
    add(V("IMG_3903", 6.0, 1, punch=0.10, rot0=-4, rot1=4))
    add(V("IMG_3903", 7.7, 1, punch=0.10, rot0=4, rot1=-4))
    add(V("IMG_3903", 10.0, 2, punch=0.08))                                    # bar 31
    add(V("IMG_3904", 3.0, 2, punch=0.08))
    add(V("IMG_3904", 22.2, 2, punch=0.08, look="warm"))                       # bar 32
    add(V("IMG_3904", 29.0, 2, z0=1.1, z1=1.0))
    add(V("IMG_3917", 0.5, 2, punch=0.12, flash=0.8))                          # bar 33
    add(V("IMG_3918", 0.5, 2, punch=0.08))
    add(V("IMG_3925", 3.0, 2, sp=2.0, vel=True))                               # bar 34
    add(V("IMG_3925", 14.0, 2, sp=1.5, vel=True))
    add(V("IMG_3925", 27.5, 2, sp=1.5, vel=True, look="night"))                # bar 35
    add(V("IMG_3937", 1.0, 2, z0=1.1, z1=1.0))
    add(V("IMG_3959", 7.0, 2, sp=2.0, vel=True))                               # bar 36
    add(V("IMG_3959", 30.0, 2, sp=2.0, vel=True))
    add(V("IMG_3960", 6.0, 4, sp=2.0, punch=0.08))                             # bar 37
    add(V("IMG_3961", 4.0, 2, punch=0.08))                                     # bar 38
    add(V("IMG_3961", 9.0, 2, punch=0.08))
    add(V("IMG_3962", 0.5, 2, sp=1.5, vel=True, look="vivid"))                 # bar 39
    add(V("IMG_3962", 8.0, 2, sp=1.5, vel=True, look="vivid"))
    add(V("IMG_3966", 1.0, 2, punch=0.08))                                     # bar 40
    add(V("IMG_3969", 1.0, 2, punch=0.08))
    add(V("IMG_3968", 0.05, 4))                                                # bar 41 car wipe
    add(V("IMG_3970", 1.0, 2, look="warm"))                                    # bar 42
    add(V("IMG_3971", 1.2, 2))
    add(V("IMG_3974", 1.5, 8, sp=0.8, look="dream", z0=1.0, z1=1.12))          # bars 43-44

    # --- F  "c'est fini" + break, bars 45-47: train into the Alps -------------
    add(V("IMG_3992", 0.5, 4, look="dream", z0=1.05, z1=1.0))                  # bar 45
    add(V("IMG_3992", 5.5, 4, look="dream", z0=1.0, z1=1.08, sp=0.9))          # bar 46
    add(V("IMG_3998", 1.0, 4, look="dream", z0=1.0, z1=1.1, sp=0.8))           # bar 47

    # --- G  verse 2, bars 48-55: Slovenian Alps -> Bled ----------------------
    add(V("IMG_4001", 0.5, 2, punch=0.15, flash=1.0, shake=16, look="vivid"))  # bar 48
    add(V("IMG_3997", 0.5, 2, punch=0.08, look="vivid"))
    add(V("IMG_1073", 1.0, 2, punch=0.08, look="vivid"))                       # bar 49
    add(V("IMG_1074", 1.0, 2, punch=0.08, look="vivid"))
    add(V("IMG_4026", 1.0, 4, z0=1.0, z1=1.1, look="vivid"))                   # bar 50
    add(V("IMG_4027", 1.0, 2, punch=0.08, look="vivid"))                       # bar 51
    add(V("IMG_4028", 0.5, 2, punch=0.08, look="vivid"))
    add(V("IMG_4029", 1.22, 4, look="vivid"))                                  # bar 52 run ...
    add(V("IMG_4029", 3.25, 2, punch=0.15, flash=0.8, shake=14, look="vivid")) # bar 53 splash
    add(V("IMG_4029", 10.5, 2, look="vivid"))
    add(V("IMG_4029", 13.0, 4, z0=1.0, z1=1.15, look="vivid"))                 # bar 54
    add(V("IMG_4044", 0.5, 4, z0=1.08, z1=1.0))                                # bar 55

    # --- H  "la la la", bars 56-63: train to Croatia -------------------------
    add(V("IMG_4055", 1.0, 2, flash=0.5))                                      # bar 56
    add(V("IMG_4055", 8.5, 2))
    add(V("IMG_4056", 4.0, 4, z0=1.0, z1=1.06))                                # bar 57
    add(V("IMG_4057", 1.0, 4, z0=1.0, z1=1.1))                                 # bar 58
    add(V("IMG_4058", 1.0, 2))                                                 # bar 59
    add(V("IMG_4061", 1.0, 2))
    add(V("IMG_4062", 0.5, 4))                                                 # bar 60
    add(V("IMG_4064", 0.5, 4, z0=1.06, z1=1.0))                                # bar 61
    add(V("IMG_4065", 0.5, 4))                                                 # bar 62
    add(V("IMG_4065", 6.0, 2, punch=0.06))                                     # bar 63
    add(V("IMG_4064", 5.0, 2, punch=0.06))

    # --- I  build, bars 64-69: Kvarner coast ---------------------------------
    add(V("IMG_4069", 0.5, 4, punch=0.12, flash=0.8, look="warm"))             # bar 64
    add(V("IMG_4075", 1.0, 2, punch=0.08))                                     # bar 65
    add(V("IMG_4077", 1.0, 2, punch=0.08, look="warm"))
    add(V("IMG_4079", 1.5, 2, punch=0.08, look="warm"))                        # bar 66
    add(V("IMG_4080", 2.0, 2, punch=0.08))
    add(V("IMG_4080", 20.0, 2, sp=2.0, vel=True))                              # bar 67
    add(V("IMG_4079", 12.0, 2, look="warm"))
    add(V("IMG_4085", 1.0, 2, punch=0.08))                                     # bar 68
    add(V("IMG_4083", 1.0, 2, punch=0.08))
    add(V("IMG_4084", 1.0, 4, z0=1.0, z1=1.06))                                # bar 69

    # --- J  pre-drop break, bars 70-71: the dive, frozen in the silence -------
    add(V("IMG_4084", 5.0, 4, z0=1.06, z1=1.3, desat=[(0, 0.0), (2.0, 0.85)]))  # bar 70
    add(V("IMG_4082", 0.0, 4, tmap=[(0.0, 0.0), (0.61, 0.21), (1.23, 0.235), (2.03, 0.46)],
          desat=[(0.0, 0.5), (0.55, 1.0), (1.22, 1.0), (1.5, 0.3)],
          z0=1.18, z1=1.05, blend=True))

    # --- K  DROP 2 / chorus 2, bars 72-86: Croatian coast + Istria -----------
    add(V("IMG_4082", 0.46, 4, punch=0.22, flash=1.0, flash_tau=0.3, shake=26, look="vivid"))
    add(V("IMG_4085", 5.0, 2, punch=0.08))                                     # bar 73
    add(P("IMG_4088", 2, fy=0.35, z0=1.12, z1=1.0, look="night"))
    add(V("IMG_4101", 1.0, 2, punch=0.08, look="warm"))                        # bar 74
    add(V("IMG_4115", 1.0, 2, punch=0.08))
    add(V("IMG_4136", 0.5, 2, punch=0.08, look="vivid"))                       # bar 75
    add(V("IMG_4177", 0.3, 2, punch=0.08, look="vivid"))
    add(V("IMG_4128", 2.4, 4, look="night", ev=1.1))                           # bar 76
    add(SPLIT(["IMG_4126", "IMG_4127"], 2, reveal=1.0,                         # bar 77
              focus=[(0.5, 0.45), (0.5, 0.45)], look="night"))
    add(P("IMG_4156", 2, fy=0.55, z0=1.0, z1=1.12))
    add(V("IMG_4181", 1.0, 2, punch=0.08, look="vivid"))                       # bar 78
    add(V("IMG_4182", 0.5, 2, punch=0.08, look="vivid"))
    add(V("IMG_1247", 1.17, 4, look="vivid"))                                  # bar 79 jump
    add(V("IMG_1247", 3.2, 2, punch=0.18, flash=0.9, shake=18, look="vivid"))  # bar 80 splash
    add(P("IMG_1284", 2, fy=0.5, z0=1.1, z1=1.0))
    add(V("IMG_4212", 1.0, 2, punch=0.10))                                     # bar 81
    add(V("IMG_4212", 4.5, 2, punch=0.10))
    add(V("IMG_4212", 9.3, 4, z0=1.0, z1=1.1))                                 # bar 82
    for src, t in (("IMG_4136", 3.5), ("IMG_4177", 1.5), ("IMG_4181", 7.5), ("IMG_4182", 3.5),
                   ("IMG_4115", 8.0), ("IMG_4128", 5.0), ("IMG_4212", 12.0), ("IMG_1247", 5.0)):
        add(V(src, t, 1, punch=0.12, flash=0.35, look="vivid"))              # bars 83-84
    add(V("IMG_4182", 4.5, 2, look="vivid"))                                   # bar 85
    add(V("IMG_4148", 70.0, 2, look="warm"))
    ext(STROBE([("IMG_4101", 4.0), ("IMG_4085", 8.0), ("IMG_4128", 1.0), ("IMG_4136", 5.0),
                ("IMG_4212", 6.0), ("IMG_4181", 11.0), ("IMG_4119", 1.0), ("IMG_4148", 76.0)],
               look="vivid"))                                                  # bar 86

    # --- L  breakdown "encore", bars 87-95: golden hour -> night -------------
    add(V("IMG_4119", 0.3, 4, look="warm", z0=1.0, z1=1.1, flash=0.3))         # bar 87
    add(V("IMG_4121", 5.5, 4, look="warm", z0=1.08, z1=1.0))                   # bar 88
    add(V("IMG_4148", 20.0, 4, look="warm", z0=1.0, z1=1.08))                  # bar 89
    add(V("IMG_4148", 50.0, 4, look="warm", z0=1.1, z1=1.0))                   # bar 90
    add(V("IMG_4207", 0.3, 4, z0=1.0, z1=1.08))                                # bar 91
    add(V("IMG_4203", 0.5, 4, look="night", z0=1.08, z1=1.0))                  # bar 92
    add(V("IMG_4130", 0.5, 4, look="night", ev=1.3, z0=1.0, z1=1.1))           # bar 93
    add(V("IMG_4208", 0.5, 4, look="night", ev=1.25))                          # bar 94
    add(V("IMG_4208", 3.2, 4, look="night", ev=1.25, z0=1.12, z1=1.0))         # bar 95

    # --- M  final chorus, bars 96-103: the last leg + recap strobe -----------
    add(V("IMG_4380", 0.5, 2, punch=0.2, flash=1.0, flash_tau=0.25, shake=22, look="warm"))
    add(V("IMG_4408", 0.5, 2, punch=0.08, look="warm"))
    add(V("IMG_4393", 0.5, 2, punch=0.08))                                     # bar 97
    add(V("IMG_4407", 0.5, 2, punch=0.08))
    add(V("IMG_4424", 0.3, 4, z0=1.0, z1=1.1, look="warm"))                    # bar 98
    add(V(NIGHT, 3.3, 4, mode="blur", look="night", ev=1.35, z0=1.0, z1=1.08))          # bar 99
    add(V("IMG_4393", 2.2, 2, punch=0.08))                                     # bar 100
    add(V("IMG_4380", 3.5, 2, punch=0.08, look="warm"))
    ext(STROBE([                                                               # bars 101-103
        ("IMG_3827", 10.0), ("IMG_3824", 4.0), ("IMG_3831", 5.0), ("IMG_3860", 20.0),
        ("IMG_3870", 12.0), ("IMG_3903", 8.0), ("IMG_3904", 24.0), ("IMG_3925", 20.0),
        ("IMG_3937", 6.0), ("IMG_3960", 12.0), ("IMG_3962", 11.0), ("IMG_4026", 4.0),
        ("IMG_4029", 3.5), ("IMG_4055", 5.0), ("IMG_4057", 6.0), ("IMG_4079", 9.0),
        ("IMG_4082", 0.8), ("IMG_4119", 2.0), ("IMG_4128", 4.6), ("IMG_4148", 41.0),
        ("IMG_1247", 3.4), ("IMG_4212", 5.5), ("IMG_4424", 2.0), ("IMG_4426", 3.0)]))

    # --- N  outro, bars 104-105: dinner with friends, fading to black & white -
    add(V("IMG_4426", 0.4, 8, look="cine", z0=1.0, z1=1.12, flash=0.8, flash_tau=0.4,
          desat=[(0.0, 0.0), (2.0, 1.0)]))
    return S


# section checkpoints (bar at which a new section must start) -> sanity check
CHECKPOINTS = [0, 4, 8, 12, 28, 45, 48, 56, 64, 70, 72, 87, 96, 104, 106]


# ----------------------------------------------------------------------------
# global effects
# ----------------------------------------------------------------------------

# letterbox amount keyframes (beat index, 0..1)
LETTERBOX = [
    (at(0), 1), (at(4) - 0.01, 1), (at(4), 0),
    (at(44, 2), 0), (at(45, 2), 1), (at(48) - 0.01, 1), (at(48), 0),
    (at(70), 0), (at(70, 2), 1), (at(72) - 0.01, 1), (at(72), 0),
    (at(87), 0), (at(87, 1), 1), (at(96) - 0.01, 1), (at(96), 0),
    (at(104), 0), (at(105), 1), (at(107), 1),
]

# beat bounce (zoom pulse on every beat) per bar range: (bar0, bar1, amplitude)
BOUNCE = [
    (4, 8, 0.018), (8, 12, 0.03), (12, 28, 0.014), (28, 44, 0.035),
    (48, 56, 0.03), (56, 64, 0.01), (64, 70, 0.025), (72, 87, 0.035),
    (87, 96, 0.008), (96, 104, 0.035),
]

# extra white blinks (beat index, amplitude, tau seconds)
def blinks():
    B = []
    # build before drop 1: blinks on every half beat, growing
    for i in range(8):
        B.append((at(27, i * 0.5), 0.25 + 0.08 * i, 0.04))
    # music comes back after the silence
    B.append((at(71, 2.45), 0.6, 0.05))
    # every chorus downbeat gets a soft flash
    for bar in list(range(29, 44, 2)) + list(range(73, 86, 2)) + list(range(97, 101)):
        B.append((at(bar), 0.28, 0.07))
    # verse 2 / build kick accents
    for bar in range(48, 56):
        B.append((at(bar), 0.2, 0.06))
    for bar in range(64, 70):
        B.append((at(bar), 0.2, 0.06))
    return B

# global fade (beat index, brightness multiplier)
FADE = [(at(0), 0.0), (at(1, 2), 1.0), (at(105, 1), 1.0), (at(106, 1), 0.0), (at(110), 0.0)]

# end of the video in beat index (a little after the last bar)
END_BEAT = at(106, 1)
