"""Neymar Jr – the original edit, expressed for engine.py (must render bit-identical)."""
EDL = [
    # vocal intro – slow and cinematic
    (0, 5,   "rare",       38.90, 40.66, (220, 110, 1600, 900), {"interp": True, "push": 0.05}),   # UCL warm-up juggling
    (5, 8,   "skills1819", 242.35, 243.76, (240, 135, 1440, 810), {"push": 0.04}),                 # feet + ball close-up
    (8, 12,  "skills1819", 444.82, 446.00, (480, 135, 1440, 810), {"interp": True, "push": 0.07}), # the face
    (12, 13, "skills1819", 679.80, 680.27, (240, 135, 1440, 810), {}),                             # ball at the feet
    # DROP – white flash, one cut per beat
    (13, 14, "skills1819", 603.85, 604.32, (480, 135, 1440, 810), {}),
    (14, 15, "scene8k",    11.25, 11.72, (200, 90, 1600, 900), {}),        # vs Real Madrid, Bernabéu 2018
    (15, 16, "scene8k",    11.72, 12.19, (200, 90, 1600, 900), {}),
    (16, 17, "scene8k",    12.19, 12.66, (460, 120, 1280, 720), {}),
    (17, 18, "faces",      79.08, 79.55, (0, 105, 1529, 860), {}),         # hands on face
    (18, 19, "scene8k",    13.15, 13.62, (320, 60, 1600, 900), {}),        # vs Bayern, CHAMPIONS LEAGUE board
    (19, 20, "scene8k",    22.55, 23.02, (0, 80, 1600, 900), {}),          # profile, Bernabéu crowd
    (20, 21, "skills1819", 342.42, 342.89, (300, 135, 1440, 810), {}),     # close dribble
    (21, 22, "skills1819", 456.00, 456.47, (400, 135, 1440, 810), {}),     # feet on the ball
    (22, 23.333, "faces",  77.92, 78.54, (170, 110, 1493, 840), {}),       # NEYMAR JR 10
    (23.333, 25, "uclpsg", 31.08, 31.86, (0, 20, 1660, 934), {}),          # free kick vs Red Star, strike on the cut
    (25, 26, "uclpsg",     32.45, 32.92, (320, 130, 1600, 900), {}),       # ball in
    (26, None, "uclpsg",   105.20, 106.40, (40, 120, 1600, 900), {"interp": True, "push": 0.06}),  # crossed arms
]
