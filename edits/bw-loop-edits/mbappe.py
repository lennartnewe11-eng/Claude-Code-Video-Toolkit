"""Kylian Mbappé – B&W loop edit (engine.py)."""
# hd60: bilibili watermark top-right · night4k/wcgoals: BBC scoreboard top-left · rmcinema: broadcaster bug
# top-right · wcfinal22: scoreboard top-right, bilibili top-left, French subtitles at the bottom.
EDL = [
    # vocal intro
    (0, 5,   "hd60",      14.65, 16.45,  (100, 130, 1520, 855), {"interp": True, "push": 0.05}),   # juggling
    (5, 8,   "night4k",   1.00, 2.40,    (240, 100, 1600, 900), {"push": 0.04}),                   # World Cup final, the look
    (8, 12,  "hd60",      17.90, 19.25,  (100, 130, 1580, 889), {"interp": True, "push": 0.07}),   # the face
    (12, 13, "rmcinema",  178.30, 178.77, (60, 180, 1440, 810), {}),                               # ball at his feet
    # DROP
    (13, 14, "rmcinema",  179.60, 180.07, (0, 160, 1440, 810), {}),
    (14, 15, "rmcinema",  300.55, 301.02, (300, 220, 1440, 810), {}),                              # PSG–Real 2022, 94' run – 3 punch-ins
    (15, 16, "rmcinema",  301.02, 301.49, (250, 250, 1300, 731), {}),
    (16, 17, "rmcinema",  301.49, 301.96, (200, 240, 1280, 720), {}),
    (17, 18, "night4k",   40.35, 40.82,  (480, 120, 1440, 810), {}),                               # the scream
    (18, 19, "night4k",   23.00, 23.47,  (300, 110, 1440, 810), {}),                               # past Argentina
    (19, 20, "wcgoals",   120.00, 120.47, (420, 120, 1440, 810), {}),                              # profile
    (20, 21, "rmcinema",  135.75, 136.22, (600, 180, 1280, 720), {}),                              # at Courtois
    (21, 22, "rmcinema",  178.80, 179.27, (60, 180, 1440, 810), {}),
    (22, 23.333, "wcgoals", 192.65, 193.27, (100, 110, 1600, 900), {}),                            # MBAPPE 10
    (23.333, 25, "wcfinal22", 108.45, 108.88, (475, 310, 1209, 680), {"interp": True}),            # WC final 2-2 volley – strike on the cut
    (25, 26, "wcfinal22", 109.60, 110.07, (300, 250, 1280, 720), {}),                              # ball in
    (26, None, "wcgoals", 196.05, 196.65, (240, 90, 1520, 855), {"interp": True, "push": 0.06}),   # arms crossed
]
