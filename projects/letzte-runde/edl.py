"""Edit decision list for "LETZTE RUNDE" (on-screen: FINAL ROUND) – a 16 s TikTok boxing edit.

Timeline = 16.0 s @ 30 fps = 480 frames, cut to the beat grid of
"Sparta" (Mixkit #370, 120 BPM) played from 0:36.0 to 0:52.0.

Beat map of that window (measured with librosa, see README):
  808/sub hits : 0.0  1.5  4.0  4.76  5.5  8.0  9.5  [silence 11.1–11.95]  12.0  12.76  13.5
  snare        : 1.0  3.0  5.0  7.0  9.0  13.0  15.0
The track's built-in drop-out (11.1–11.95 s) is where the KO punch is held,
the drop at 12.0 s is the impact.

Story (retention logic in brackets):
  0.0  HOOK      – eyes into the lens + "FINAL ROUND." + 0:12 round clock,
                   then a punch into the camera on the 1.0 s snare
                   [4th-wall break, key message < 1 s, open loop via countdown]
  1.0  PRESSURE  – he takes punches, "THEY COUNTED HIM OUT."
  4.0  MEMORY    – B/W training flashback on every beat, "NOBODY SAW HIS NIGHTS IN THE GYM."
                   [pattern interrupt every 0.5 s]
  8.0  COMEBACK  – back to colour, he lands punches, cuts accelerate
 10.0  THE LOOK  – head lifts, stares into the lens
 11.1  SILENCE   – music drops out, ultra slow-mo glove, heartbeat, clock 0:01
 12.0  K.O.      – impact exactly on the drop, clock hits 0:00
 14.0  MESSAGE   – "IT'S NOT OVER UNTIL YOU QUIT." over his stare
 16.0  LOOP      – last frame (stare) flows into first frame (stare) [rewatch]
"""
from engine import Shot

MUSIC = {"file": "370.mp3", "start": 36.0, "duration": 16.0}
DURATION = 16.0

# ---------------------------------------------------------------------------
# picture
# ---------------------------------------------------------------------------
SHOTS = [
    # --- HOOK: the winner's stare into the lens. It continues the last shot of the
    #     video frame-for-frame (40974 @ 12.95 s), so the loop point is invisible.
    Shot("40974", 0.00, 0.76, [(0.00, 12.95), (0.76, 13.71)],
         look="outro", zoom=[(0.0, 1.0), (0.76, 1.06)], focus=(0.5, 0.3)),
    # ...then a punch straight into the lens, landing on the snare at 1.0 s
    Shot("40955", 0.76, 1.00, [(0.76, 2.10), (1.00, 2.45)],
         crop=(0.36, 0.5, 1.0), zoom=[(0.76, 1.0), (1.0, 1.25)], focus=(0.5, 0.42), dehaze=0.07),
    # --- PRESSURE: blue glove lands on him exactly on the 1.5 s 808
    Shot("40973", 1.00, 2.10, [(1.00, 2.50), (2.10, 3.60)],
         zoom=[(1.0, 1.04), (2.1, 1.10)], focus=(0.5, 0.4), dehaze=0.05),
    Shot("40958", 2.10, 2.50, [(2.10, 6.55), (2.50, 6.95)],
         crop=(0.50, 0.5, 1.0), zoom=[(2.1, 1.14), (2.5, 1.05)], focus=(0.5, 0.30)),
    Shot("40970", 2.50, 3.00, [(2.50, 0.95), (3.00, 1.45)],
         zoom=[(2.5, 1.0), (3.0, 1.06)], focus=(0.5, 0.4)),
    Shot("40964", 3.00, 4.00, [(3.00, 6.30), (4.00, 7.60)],
         crop=(0.53, 0.5, 1.0), zoom=[(3.0, 1.06), (4.0, 1.16)], focus=(0.5, 0.35)),

    # --- MEMORY (black & white, one cut per beat)
    Shot("40948", 4.00, 4.50, [(4.00, 0.00), (4.50, 0.50)],
         crop=(0.60, 0.5, 1.0), look="memory", zoom=[(4.0, 1.14), (4.5, 1.05)], focus=(0.5, 0.28)),
    Shot("4596", 4.50, 5.00, [(4.50, 2.00), (5.00, 2.50)],
         crop=(0.45, 0.55, 0.75), look="memory", zoom=[(4.5, 1.0), (5.0, 1.06)], focus=(0.5, 0.5)),
    Shot("40265", 5.00, 5.50, [(5.00, 4.00), (5.50, 4.50)],
         crop=(0.45, 0.5, 1.0), look="memory", zoom=[(5.0, 1.08), (5.5, 1.0)], focus=(0.5, 0.4)),
    Shot("40948", 5.50, 6.00, [(5.50, 2.00), (6.00, 2.50)],
         crop=(0.55, 0.5, 1.0), look="memory", zoom=[(5.5, 1.1), (6.0, 1.02)], focus=(0.5, 0.4)),
    Shot("40255", 6.00, 6.50, [(6.00, 1.00), (6.50, 1.50)],
         crop=(0.60, 0.5, 1.0), look="memory", zoom=[(6.0, 1.0), (6.5, 1.08)], focus=(0.5, 0.35)),
    Shot("40266", 6.50, 7.00, [(6.50, 1.40), (7.00, 1.90)],
         crop=(0.58, 0.5, 1.0), look="memory", zoom=[(6.5, 1.08), (7.0, 1.0)], focus=(0.5, 0.4)),
    Shot("40971", 7.00, 7.50, [(7.00, 1.00), (7.50, 1.50)],
         look="memory", zoom=[(7.0, 1.0), (7.5, 1.08)], focus=(0.5, 0.35)),
    Shot("40255", 7.50, 8.00, [(7.50, 5.00), (8.00, 5.50)],
         crop=(0.66, 0.5, 1.0), look="memory", zoom=[(7.5, 1.0), (8.0, 1.12)], focus=(0.5, 0.32)),

    # --- COMEBACK: his punch lands on the 8.0 s 808, slow-mo hair whip + sweat
    Shot("40974", 8.00, 8.50, [(8.00, 5.58), (8.50, 5.88)],
         zoom=[(8.0, 1.12), (8.5, 1.02)], focus=(0.3, 0.3)),
    Shot("40966", 8.50, 9.00, [(8.50, 2.75), (9.00, 3.25)],
         crop=(0.62, 0.5, 1.0), zoom=[(8.5, 1.0), (9.0, 1.06)], focus=(0.5, 0.35), sharpen=0.6),
    Shot("40958", 9.00, 9.25, [(9.00, 15.96), (9.25, 16.21)],
         crop=(0.50, 0.5, 1.0), zoom=[(9.0, 1.06), (9.25, 1.02)], focus=(0.5, 0.35)),
    Shot("40955", 9.25, 9.50, [(9.25, 3.70), (9.50, 3.95)],
         crop=(0.40, 0.5, 1.0), zoom=[(9.25, 1.0), (9.5, 1.05)], focus=(0.5, 0.4), dehaze=0.07),
    Shot("40973", 9.50, 9.75, [(9.50, 6.05), (9.75, 6.35)],
         zoom=[(9.5, 1.08), (9.75, 1.02)], focus=(0.5, 0.35), dehaze=0.05),
    Shot("40970", 9.75, 10.00, [(9.75, 1.40), (10.00, 1.70)],
         zoom=[(9.75, 1.0), (10.0, 1.05)], focus=(0.5, 0.4)),

    # --- THE LOOK: head lifts, eyes into the lens, slow push-in
    Shot("40961", 10.00, 11.10, [(10.00, 2.90), (10.55, 4.10), (11.10, 4.75)],
         crop=(0.50, 0.42, 0.84), zoom=[(10.0, 1.0), (11.1, 1.28)], focus=(0.5, 0.24)),

    # --- SILENCE: the music drops out, the KO glove approaches at ~0.3x
    Shot("40969", 11.10, 12.00, [(11.10, 0.06), (12.00, 0.345)],
         crop=(0.45, 0.5, 1.0), look="freeze", zoom=[(11.1, 1.04), (12.0, 1.12)],
         focus=(0.5, 0.36), sharpen=0.5),

    # --- K.O.: contact on the drop, ramp 1x → 3.5x through the fall
    # wide decode + focus pan so the camera can follow him down to the canvas
    Shot("40969", 12.00, 13.50, [(12.00, 0.37), (12.40, 0.80), (12.76, 1.70), (13.20, 3.00), (13.50, 4.10)],
         crop=(0.52, 0.5, 1.0), wide=1.6, look="ko",
         zoom=[(12.0, 1.16), (12.5, 1.05), (13.5, 1.10)],
         focus_keys=[(12.0, 0.0, 0.36), (12.5, 0.05, 0.34), (13.0, 0.15, 0.30), (13.25, 0.45, 0.32),
                     (13.5, 0.90, 0.36)],
         sharpen=0.5),
    # the beaten man in the corner
    Shot("40963", 13.50, 14.00, [(13.50, 3.50), (14.00, 4.10)],
         crop=(0.47, 0.5, 0.9), look="ko", zoom=[(13.5, 1.10), (14.0, 1.02)], focus=(0.5, 0.35)),

    # --- MESSAGE + LOOP: the winner stares into the lens
    Shot("40974", 14.00, 16.00, [(14.00, 10.95), (16.00, 12.95)],
         look="outro", zoom=[(14.0, 1.12), (16.0, 1.0)], focus=(0.5, 0.3)),
]

# ---------------------------------------------------------------------------
# impacts: shake (px), zoom punch, white flash, chromatic split, decay (s)
# ---------------------------------------------------------------------------
IMPACTS = [
    dict(t=0.00, shake=6, zoom=0.00, flash=0.00, chroma=0.003, decay=0.14),
    dict(t=0.76, shake=8, zoom=0.03, flash=0.00, chroma=0.006, decay=0.08),
    dict(t=1.00, shake=20, zoom=0.07, flash=0.65, chroma=0.012, decay=0.14),
    dict(t=1.50, shake=26, zoom=0.06, flash=0.20, chroma=0.012, decay=0.16),
    dict(t=2.10, shake=8, zoom=0.03, flash=0.00, chroma=0.004, decay=0.10),
    dict(t=2.50, shake=10, zoom=0.03, flash=0.00, chroma=0.005, decay=0.10),
    dict(t=3.00, shake=10, zoom=0.03, flash=0.10, chroma=0.004, decay=0.12),
    dict(t=4.00, shake=14, zoom=0.05, flash=0.85, chroma=0.016, decay=0.14, glitch=0.12),
    dict(t=4.76, shake=6, zoom=0.03, flash=0.00, chroma=0.003, decay=0.10),
    dict(t=5.00, shake=8, zoom=0.02, flash=0.12, chroma=0.004, decay=0.10),
    dict(t=5.50, shake=10, zoom=0.03, flash=0.00, chroma=0.004, decay=0.10),
    dict(t=6.50, shake=6, zoom=0.02, flash=0.00, chroma=0.003, decay=0.10),
    dict(t=7.00, shake=8, zoom=0.02, flash=0.10, chroma=0.004, decay=0.10),
    dict(t=8.00, shake=28, zoom=0.07, flash=0.70, chroma=0.016, decay=0.16, glitch=0.07),
    dict(t=8.50, shake=12, zoom=0.03, flash=0.00, chroma=0.006, decay=0.10),
    dict(t=9.00, shake=14, zoom=0.04, flash=0.15, chroma=0.006, decay=0.10),
    dict(t=9.25, shake=10, zoom=0.03, flash=0.00, chroma=0.005, decay=0.08),
    dict(t=9.50, shake=18, zoom=0.04, flash=0.00, chroma=0.008, decay=0.10),
    dict(t=9.75, shake=12, zoom=0.03, flash=0.00, chroma=0.006, decay=0.08),
    dict(t=10.00, shake=6, zoom=0.00, flash=0.25, chroma=0.004, decay=0.12),
    dict(t=12.00, shake=46, zoom=0.11, flash=1.00, chroma=0.026, decay=0.22, glitch=0.06),
    dict(t=12.76, shake=20, zoom=0.04, flash=0.00, chroma=0.010, decay=0.14),
    dict(t=13.50, shake=12, zoom=0.03, flash=0.00, chroma=0.006, decay=0.12),
    dict(t=14.00, shake=6, zoom=0.00, flash=0.35, chroma=0.004, decay=0.12),
    dict(t=15.00, shake=4, zoom=0.015, flash=0.00, chroma=0.002, decay=0.12),
]

# ---------------------------------------------------------------------------
# typography – Anton caps, {accent} = red text, [box] = white on a red box. y is the centre of the text block,
# kept inside TikTok's safe area (clear of the right action rail and caption).
# ---------------------------------------------------------------------------
TEXT_X = 520
TEXT_Y = 1210
TEXTS = [
    dict(lines=[("FINAL", 0.00), ("ROUND.", 0.00)], size=236, t_out=1.46, first_frame_solid=True),
    dict(lines=[("THEY COUNTED", 1.50), ("HIM {OUT.}", 2.00)], size=160, t_out=3.96),
    dict(lines=[("NOBODY SAW", 4.50), ("HIS {NIGHTS}", 5.00), ("IN THE GYM.", 5.50)], size=150, t_out=7.96),
    dict(lines=[("{K.O.}", 12.00)], size=420, t_out=13.46, y=1180, heavy=True),
    dict(lines=[("IT'S NOT OVER", 14.00), ("UNTIL [YOU] QUIT.", 14.50)], size=144, t_out=99,
         y=1400),
]

# round clock: 0:12 at t=0, one tick per second, 0:00 on the KO
CLOCK = dict(y=250, start=12, ko=12.0, hide=13.5, heartbeat=[11.15, 11.60])

# per-look finishing
FINISH = {
    "fight":  dict(grain=0.018, vignette=0.40, bloom=0.20),
    "memory": dict(grain=0.045, vignette=0.75, bloom=0.30),
    "freeze": dict(grain=0.028, vignette=0.85, bloom=0.12),
    "ko":     dict(grain=0.018, vignette=0.45, bloom=0.30),
    "outro":  dict(grain=0.018, vignette=0.50, bloom=0.22),
}

# ---------------------------------------------------------------------------
# sound design: (time of the transient, file, gain dB, extra)
# ---------------------------------------------------------------------------
SFX = [
    # hook
    (0.00, "2299.mp3", -6, {}),                  # sub hit under the first frame
    (0.76, "1492.mp3", -12, {}),                 # whoosh into the punch
    (1.00, "2050.mp3", -9, {"align": "peak"}),    # whistle of the punch into the lens
    (1.00, "2155.mp3", -4, {}),                  # impact on the cut
    (1.50, "2165.mp3", -3, {}),                  # blue glove to the face
    (1.50, "2299.mp3", -8, {}),
    (2.10, "1492.mp3", -16, {}),
    (2.52, "2164.mp3", -10, {}),
    (3.05, "2056.mp3", -14, {}),                 # exhale in the corner
    # memory
    (4.00, "1088.mp3", -11, {"dur": 0.9}),       # tape rewind into the flashback
    (4.00, "498.mp3", -8, {}),
    (5.02, "2103.mp3", -10, {}),                 # bag
    (5.52, "2051.mp3", -11, {}),                 # pads
    (6.52, "2103.mp3", -12, {}),
    (7.02, "2053.mp3", -12, {}),
    (7.92, "1492.mp3", -10, {"align": "peak"}),  # whoosh back to the present
    # comeback
    (8.00, "2155.mp3", -3, {}),
    (8.00, "2299.mp3", -7, {}),
    (8.52, "2164.mp3", -8, {}),
    (9.02, "2165.mp3", -8, {}),
    (9.27, "2053.mp3", -12, {}),
    (9.50, "2143.mp3", -7, {}),
    (9.77, "2164.mp3", -10, {}),
    # the look + silence
    (10.05, "1143.mp3", -14, {"dur": 0.95}),
    (11.15, "490.mp3", -13, {}),                   # heartbeat in the silence
    (11.60, "490.mp3", -10, {}),
    (11.40, "2054.mp3", -22, {"dur": 0.45}),     # breath
    (12.00, "2050.mp3", -12, {"align": "peak"}),  # the punch whistles in
    # K.O.
    (12.00, "2155.mp3", 0, {}),
    (12.00, "788.mp3", -3, {}),                   # cinematic boom
    (12.00, "498.mp3", -4, {}),
    (12.30, "462.mp3", -11, {"fade_in": 0.5, "fade_out": 0.8, "end": 15.95}),  # crowd erupts
    (13.00, "bell", -10, {}),                     # synthesized ring bell
    (14.00, "1490.mp3", -16, {}),
]
CROWD_BED = dict(file="458.mp3", gain=-24, start=0.0, end=11.05, offset=4.0)
# music is low-passed during the flashback (sounds like a memory)
MEMORY_FILTER = dict(t0=4.0, t1=7.95, cutoff=1400.0, wet=0.85)
