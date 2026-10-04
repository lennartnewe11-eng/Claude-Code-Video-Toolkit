"""Eden Hazard – B&W loop edit (engine.py). Beats: intro 0–13 · drop 13 · one cut per beat · name 22 · strike 23.3→25."""
# comp1819 is letterboxed (picture at y 120–960) with an NT bug top-right; top10 has a bilibili
# watermark top-left and a round UI button at x≈1830, y≈450; westham is pillarboxed with a scorebar.
PRE = {"westham": ("crop=1746:978:206:50,scale=1920:1080:flags=lanczos,setsar=1", 1920, 1080)}

EDL = [
    # vocal intro – Belgium training, World Cup 2018
    (0, 5,   "comp1819", 162.05, 163.90, (280, 160, 1351, 760), {"interp": True, "push": 0.05}),  # ball on the head
    (5, 8,   "comp1819", 157.00, 158.40, (300, 140, 1351, 760), {"push": 0.04}),                  # head down
    (8, 12,  "comp1819", 294.30, 296.00, (300, 140, 1351, 760), {"interp": True, "push": 0.07}),  # the stare (Chelsea bench)
    (12, 13, "top10",    16.30, 16.77,   (360, 150, 1420, 799), {}),                               # ball at his feet
    # DROP
    (13, 14, "top10",    125.30, 125.77, (330, 150, 1440, 810), {}),                               # sprint
    (14, 15, "top10",    179.50, 179.97, (100, 150, 1440, 810), {}),                               # vs Liverpool – 3 punch-ins
    (15, 16, "top10",    179.97, 180.44, (160, 200, 1280, 720), {}),
    (16, 17, "top10",    180.44, 180.91, (150, 240, 1120, 630), {}),
    (17, 18, "comp1819", 299.00, 299.47, (300, 140, 1351, 760), {}),                               # smile
    (18, 19, "top10",    181.00, 181.47, (0, 150, 1440, 810), {}),
    (19, 20, "top10",    14.55, 15.02,   (360, 120, 1440, 810), {}),                               # face, Europa League night
    (20, 21, "top10",    125.90, 126.37, (430, 200, 1280, 720), {}),
    (21, 22, "top10",    150.00, 150.47, (220, 150, 1440, 810), {}),                               # West Ham run begins
    (22, 23.333, "top10", 174.87, 175.49, (480, 150, 1300, 731), {}),                              # HAZARD 10
    (23.333, 25, "top10", 153.97, 154.75, (300, 150, 1440, 810), {}),                              # solo vs West Ham – strike on the cut
    (25, 26, "top10",    155.00, 155.47, (0, 150, 1440, 810), {}),                                 # ball in
    (26, None, "westham", 91.75, 92.95,  (330, 190, 1300, 731), {"interp": True, "push": 0.06}),   # hands behind the ears
]
