"""Edit decision list: Ronaldo & Nani, Manchester United -- "Blame" (Calvin Harris).

Song excerpt: beat 248 (build before drop 2) to beat 438 (tail of the outro),
89.15 s. All positions are absolute song beats from build/grid.json.

    248-256  build_2    both names on their backs, then four one-beat stabs
    256-288  drop_2     RONALDO: Portsmouth FK, Arsenal FK, Roma header, Moscow header
    288-352  breakdown  NANI: cold grade, slow motion: Spurs, Boro, the Rooney
                        assist, City, and his somersaults
    352-368  build_3    split screen, 7 against 17: both keep running, the layout jumps on
                        every beat; 366 is the silent beat before the drop -> black
    368-432  drop_3     both, alternating, warm grade; 396-399 bass break -> stabs
    432-438  outro      Ronaldo and Nani together, fade

Shot fields
    b0, b1   song beats (b1 exclusive)
    src      clip key in media/src (cut by build/cut_segments.py)
    at       (source_seconds, beat): that source moment lands on that beat --
             every anchor below was read off a contact sheet (build/contact.py)
    speed    constant or [(beat, speed), ...] keyframes (linear between)
    fx       punch thump thump_soft grain grain_heavy flash rgbhit dip open close
    shake    beats that get a hit-shake (ball in the net)
    grade    base cold warm mono
    label / title / end   text overlays
    panels + layouts      split screen (build_3)
"""

B0, B_END = 248, 438

# burned-in broadcast graphics (scorebugs, channel logos) cut away per source,
# as (x0, y0, x1, y1) with equal width and height so 16:9 survives
CROP = {
    "r_pompey": (0.0, 0.09, 0.91, 1.0),     # Sky Sports bug top right
    "n_spurs07": (0.0, 0.09, 0.91, 1.0),
    "n_boro": (0.0, 0.09, 0.91, 1.0),
    "r_fulham": (0.0, 0.09, 0.91, 1.0),
    "r_city09": (0.0, 0.09, 0.91, 1.0),
    "r_roma": (0.07, 0.14, 0.93, 1.0),      # MUTV score top left, logo top right
    "r_arsfk": (0.055, 0.11, 0.945, 1.0),   # ITV score bar + logo
    "r_arscounter": (0.055, 0.11, 0.945, 1.0),
    "n_city": (0.055, 0.11, 0.945, 1.0),    # Sky score + logo
    "n_rooney": (0.055, 0.11, 0.945, 1.0),
    "n_ars82": (0.10, 0.10, 0.99, 0.99),    # score, logo, LIVE badge bottom left
}


def S(b0, b1, src=None, **kw):
    d = dict(b0=b0, b1=b1, **kw)
    if src:
        d["src"] = src
        d.setdefault("crop", CROP.get(src))
    return d


def P(src, **kw):
    return dict(src=src, crop=CROP.get(src), **kw)


def _lr(split):
    return [(0, 0, split, 1), (split, 0, 1, 1)]


def _tb(split):
    return [(0, 0, 1, split), (0, split, 1, 1)]


# the layout carries the beat while both runs play on
LAYOUTS_BUILD3 = [
    (352, _lr(0.50)),
    (354, _lr(0.64)),
    (356, _lr(0.36)),
    (358, _tb(0.50)),
    (360, _lr(0.70)),
    (361, _lr(0.30)),
    (362, _tb(0.62)),
    (363, _tb(0.38)),
    (364, _lr(0.78)),
    (365, _lr(0.22)),
]

W = "warm"


def slow_after(b, v=0.5, ease=0.4):
    """Real time up to beat b, then ease into slow motion."""
    return [(b, 1.0), (b + ease, v)]


def shots():
    return [
        # ---- build_2: whose edit this is ---------------------------------
        S(248, 250, "r_arscounter", at=(114.2, 248), speed=0.8, fx=("open", "grain"), open_beats=1,
          push=(1.0, 1.05), title="RONALDO|7"),
        S(250, 252, "n_city", at=(79.1, 250), speed=0.8, fx=("punch", "grain"), title="NANI|17"),
        S(252, 253, "r_pompey", at=(7.0, 252), fx=("punch",)),
        S(253, 254, "n_spurs07", at=(13.62, 253), speed=0.9, fx=("punch",)),  # caption bar from 14.1
        S(254, 255, "r_city09", at=(6.0, 254), fx=("punch",)),
        S(255, 256, "n_spurs07", at=(18.9, 255), fx=("punch", "rgbhit")),

        # ---- drop_2: Ronaldo ---------------------------------------------
        # Portsmouth 2008: the strike from low behind him, then the dip under the bar
        S(256, 260, "r_pompey", at=(29.8, 258), speed=slow_after(258.1, 0.55),
          fx=("flash", "punch", "thump"), label="VS PORTSMOUTH  ·  2008"),
        S(260, 264, "r_pompey", at=(32.5, 262), speed=slow_after(262.1, 0.5),
          fx=("punch", "thump"), shake=(262,)),
        # Arsenal 2009: from behind the run-up, the net, the celebration
        S(264, 268, "r_arsfk", at=(48.05, 267), speed=slow_after(267.1, 0.6),
          fx=("punch", "thump"), label="VS ARSENAL  ·  2009"),
        S(268, 270, "r_arsfk", at=(54.6, 269), speed=0.8, fx=("punch",), shake=(269,)),
        S(270, 272, "r_arsfk", at=(64.4, 270), fx=("punch",)),
        # Roma 2008: the diving header from the side, then the net
        S(272, 278, "r_roma", at=(55.3, 274), speed=slow_after(274.2, 0.45),
          fx=("punch", "thump"), shake=(274,), label="VS AS ROMA  ·  2008"),
        S(278, 280, "r_roma", at=(69.9, 278), fx=("punch",)),
        # Moscow 2008: header from behind the goal, then the scream
        S(280, 286, "r_final", at=(82.1, 283), speed=slow_after(283.2, 0.5),
          fx=("punch", "thump"), label="CL-FINALE  ·  MOSKAU 2008"),
        S(286, 288, "r_final", at=(27.1, 286), speed=0.8, fx=("punch",)),

        # ---- breakdown: Nani, cold, slow ---------------------------------
        S(288, 296, "n_ars82", at=(24.0, 288), speed=0.7, grade="cold", fx=("dip", "grain"),
          push=(1.0, 1.08)),
        S(296, 304, "n_spurs07", at=(12.9, 301), speed=slow_after(301, 0.4), grade="cold",
          fx=("grain",), push=(1.0, 1.06), label="VS TOTTENHAM  ·  2007"),
        S(304, 306, "n_spurs07", at=(13.6, 304), speed=0.48, grade="cold", fx=("grain",)),
        S(306, 312, "n_spurs07", at=(19.4, 306), speed=0.68, grade="cold", fx=("grain",)),
        S(312, 320, "n_boro", at=(8.65, 312), grade="cold", fx=("grain",), label="VS MIDDLESBROUGH  ·  2007"),
        S(320, 324, "n_boro", at=(13.2, 320), speed=0.6, grade="cold", fx=("grain",)),
        S(324, 328, "n_rooney", at=(53.5, 324), grade="cold", fx=("grain",)),
        S(328, 332, "n_rooney", at=(62.45, 330), speed=slow_after(330, 0.5), grade="cold", fx=("grain",),
          label="VORLAGE NANI  ·  2011"),
        S(332, 340, "n_city", at=(66.6, 336), speed=slow_after(336.3, 0.45), grade="cold",
          fx=("grain",), push=(1.0, 1.05), label="VS MAN CITY  ·  2011"),
        S(340, 344, "n_city", at=(77.1, 340), speed=0.9, grade="cold", fx=("grain",)),
        S(344, 352, "n_city", at=(29.4, 344), speed=0.4, grade="cold", fx=("grain_heavy",),
          push=(1.0, 1.1)),

        # ---- build_3: both runs at once, the layout moves on every beat --
        S(352, 366, panels=[
            P("r_arscounter", at=(115.0, 352), speed=0.76, focus=(0.42, 0.42)),  # 7, from behind
            P("n_ars82", at=(26.65, 352), speed=0.54, focus=(0.47, 0.42)),      # 17, head down
        ], layouts=LAYOUTS_BUILD3, fx=("grain",)),
        S(366, 367, black=True),  # the silent beat: nothing on screen either
        S(367, 368, "r_fulham", at=(13.2, 367), grade="mono", fx=("punch", "rgbhit")),

        # ---- drop_3: both, warm ------------------------------------------
        # Arsenal 2009 counter: the back-heel that starts it, the finish, the net
        S(368, 370, "r_arscounter", at=(86.7, 368), grade=W, fx=("flash", "punch")),
        S(370, 374, "r_arscounter", at=(90.35, 371.75), speed=slow_after(371.85, 0.8), grade=W,
          fx=("punch", "thump"), label="VS ARSENAL  ·  2009"),
        S(374, 376, "r_arscounter", at=(96.6, 374), grade=W, fx=("punch",)),
        S(376, 378, "r_fulham", at=(13.0, 376), grade=W, fx=("punch",)),
        # Nani's chip, Arsenal 2011
        S(378, 384, "n_ars82", at=(19.95, 381), grade=W, fx=("punch", "thump"),
          label="VS ARSENAL  ·  2011"),
        S(384, 386, "n_spurs07", at=(22.9, 384), grade=W, fx=("punch",)),
        # Fulham 2007, the late winner
        S(386, 392, "r_fulham", at=(30.0, 389), speed=slow_after(389.1, 0.6), grade=W,
          fx=("punch", "thump"), shake=(389.5,), label="VS FULHAM  ·  2007"),
        S(392, 396, "r_fulham", at=(15.4, 392), speed=0.95, grade=W, fx=("punch", "thump_soft")),
        # bass break: four faces, one beat each
        S(396, 397, "r_pompey", at=(7.6, 396), grade=W, fx=("punch", "rgbhit")),
        S(397, 398, "n_boro", at=(14.75, 397), grade=W, fx=("punch",)),
        S(398, 399, "r_arsfk", at=(65.0, 398), grade=W, fx=("punch",)),
        S(399, 400, "n_city", at=(79.2, 399), grade=W, fx=("punch",)),
        # Man City 2009 free kick, arms out
        S(400, 406, "r_city09", at=(3.35, 402), speed=slow_after(404, 0.6), grade=W,
          fx=("flash", "punch", "thump"), label="VS MAN CITY  ·  2009"),
        S(406, 408, "r_city09", at=(5.95, 406), grade=W, fx=("punch",)),
        # Moscow again, from behind the net: the ball hits the camera
        S(408, 414, "r_final", at=(73.25, 413), speed=slow_after(413, 0.5), grade=W,
          fx=("punch", "thump"), shake=(413,)),
        S(414, 416, "r_arsfk", at=(68.8, 414), grade=W, fx=("punch",)),
        # Nani: City 2011 from the main camera, then the Boro dribble
        S(416, 420, "n_city", at=(21.1, 418), speed=slow_after(418.2, 0.6), grade=W,
          fx=("punch", "thump"), shake=(418.2,)),
        S(420, 424, "n_boro", at=(5.8, 420), speed=1.1, grade=W, fx=("punch", "thump")),
        S(424, 428, "r_final", at=(33.0, 424), grade=W, fx=("punch", "thump_soft")),
        S(428, 432, "r_city09", at=(10.0, 428), grade=W, fx=("punch", "thump_soft")),

        # ---- outro: the two of them -------------------------------------
        S(432, 438, "r_pompey", at=(39.5, 432), speed=0.47, grade=W, fx=("grain", "close"),
          close_beats=4, push=(1.0, 1.08), end="RONALDO  &  NANI|MANCHESTER UNITED", end_delay=0.5),
    ]
