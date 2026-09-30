"""Edit decision list: Ronaldo & Nani, Manchester United -- "Blame" (Calvin Harris).

Song excerpt: beat 248 (build before drop 2) to beat 438 (tail of the outro),
89.15 s. All positions are absolute song beats from build/grid.json.

    248-256  build_2    intro, one-beat stabs into the drop
    256-288  drop_2     RONALDO -- the big ones, 4-8 beat reading units
    288-352  breakdown  NANI -- cold grade, slow motion, 8-beat units
    352-368  build_3    split screen, both run on, layout jumps each beat;
                        366 is the silent beat before the drop -> black
    368-432  drop_3     both, alternating, warm grade; 396-399 bass break
    432-438  outro      last image, fade

Shot fields
    b0, b1   song beats (b1 exclusive)
    src      clip key in media/src
    at       (source_seconds, beat): that source moment lands on that beat
    speed    constant or [(beat, speed), ...] keyframes (linear between)
    fx       punch thump thump_soft grain grain_heavy flash rgbhit dip open close
    shake    beats that get a hit-shake (ball in the net)
    grade    base cold warm mono
    label / title / end   text overlays
    panels + layouts      split screen (see build_3)

Source moments marked TODO are placeholders until the clip has been looked at
on a contact sheet (build/contact.py). No anchor is taken from memory.
"""

B0, B_END = 248, 438


def S(b0, b1, src=None, **kw):
    d = dict(b0=b0, b1=b1, **kw)
    if src:
        d["src"] = src
    return d


# rects are (x0, y0, x1, y1) in 0..1; one per panel
def _lr(split):
    return [(0, 0, split, 1), (split, 0, 1, 1)]


LAYOUTS_BUILD3 = [
    (352, _lr(0.50)),
    (354, _lr(0.66)),
    (356, _lr(0.34)),
    (358, [(0, 0, 1, 0.5), (0, 0.5, 1, 1)]),
    (360, _lr(0.72)),
    (361, _lr(0.28)),
    (362, _lr(0.62)),
    (363, _lr(0.38)),
    (364, _lr(0.80)),
    (365, _lr(0.20)),
]


def shots():
    G = ("grain",)
    return [
        # ---- build_2: who this is about --------------------------------
        S(248, 252, "r_face", at=(0.0, 248), speed=0.6, fx=("open", "grain"), open_beats=1,
          push=(1.0, 1.06), title="RONALDO|7"),
        S(252, 253, "r_skill1", at=(0.0, 252), fx=("punch",) + G),
        S(253, 254, "n_face", at=(0.0, 253), fx=("punch",) + G),
        S(254, 255, "r_skill2", at=(0.0, 254), fx=("punch",) + G),
        S(255, 256, "n_skill1", at=(0.0, 255), fx=("punch", "rgbhit") + G),

        # ---- drop_2: Ronaldo -------------------------------------------
        S(256, 264, "r_porto", at=(4.0, 260), speed=[(256, 1.0), (260.5, 1.0), (261.5, 0.45)],
          fx=("flash", "punch", "thump") + G, shake=(260,), label="VS FC PORTO  ·  2009"),
        S(264, 266, "r_celeb1", at=(0.0, 264), fx=("punch",) + G),
        S(266, 272, "r_arsenal_fk", at=(3.0, 269), speed=[(266, 1.0), (269.5, 1.0), (270.5, 0.5)],
          fx=("punch", "thump") + G, shake=(269,), label="VS ARSENAL  ·  2009"),
        S(272, 274, "r_skill3", at=(0.0, 272), fx=("punch",) + G),
        S(274, 280, "r_pompey_fk", at=(3.0, 277), speed=[(274, 1.0), (277.5, 1.0), (278.5, 0.5)],
          fx=("punch", "thump") + G, shake=(277,), label="VS PORTSMOUTH  ·  2008"),
        S(280, 284, "r_roma", at=(2.0, 282), speed=[(280, 1.0), (281.5, 0.5), (283, 0.8)],
          fx=("punch", "thump") + G, label="VS AS ROMA  ·  2008"),
        S(284, 288, "r_final", at=(2.0, 286), speed=[(284, 1.0), (285.5, 0.5)],
          fx=("punch", "thump") + G, label="UCL FINAL  ·  MOSCOW 2008"),

        # ---- breakdown: Nani, cold, slow ------------------------------
        S(288, 296, "n_face2", at=(0.0, 288), speed=0.5, grade="cold", fx=("dip", "grain"),
          push=(1.0, 1.08), title="NANI|17", title_delay=1),
        S(296, 304, "n_spurs", at=(3.0, 300), speed=[(296, 1.0), (299, 1.0), (300, 0.5)],
          grade="cold", fx=("grain",), push=(1.0, 1.05), label="VS TOTTENHAM  ·  2007"),
        S(304, 308, "n_flip", at=(0.0, 304), speed=0.6, grade="cold", fx=("grain",)),
        S(308, 316, "n_bayern", at=(3.0, 312), speed=[(308, 1.0), (311, 1.0), (312, 0.5)],
          grade="cold", fx=("grain",), label="VS BAYERN  ·  2010"),
        S(316, 320, "n_skill2", at=(0.0, 316), speed=0.8, grade="cold", fx=("grain",)),
        S(320, 328, "n_chelsea", at=(3.0, 323), speed=[(320, 1.0), (322.5, 1.0), (323.5, 0.5)],
          grade="cold", fx=("grain",), push=(1.0, 1.05), label="VS CHELSEA  ·  2011"),
        S(328, 336, "n_city", at=(5.0, 334), speed=[(328, 1.15), (333, 1.0), (334.5, 0.5)],
          grade="cold", fx=("grain",), label="VS MAN CITY  ·  COMMUNITY SHIELD 2011"),
        S(336, 344, "n_boro", at=(3.0, 338), speed=[(336, 1.0), (338, 1.0), (339, 0.5)],
          grade="cold", fx=("grain",), label="VS MIDDLESBROUGH"),
        S(344, 352, "n_flip2", at=(0.0, 344), speed=0.5, grade="cold", fx=("grain_heavy",),
          push=(1.0, 1.1)),

        # ---- build_3: both at once, layout moves on every beat --------
        S(352, 366, panels=[
            dict(src="r_skills", at=(0.0, 352), focus=(0.5, 0.5)),
            dict(src="n_skills", at=(0.0, 352), focus=(0.5, 0.5)),
        ], layouts=LAYOUTS_BUILD3, fx=G),
        S(366, 367, black=True),  # the silent beat: nothing on screen either
        S(367, 368, "r_stare", at=(0.0, 367), grade="mono", fx=("punch", "rgbhit")),

        # ---- drop_3: both, warm ---------------------------------------
        S(368, 374, "r_goal_a", at=(3.0, 371), speed=[(368, 1.0), (371.5, 1.0), (372.5, 0.5)],
          grade="warm", fx=("flash", "punch", "thump") + G, shake=(371,)),
        S(374, 376, "r_kneeslide", at=(0.0, 374), grade="warm", fx=("punch",) + G),
        S(376, 382, "n_goal_b", at=(3.0, 379), speed=[(376, 1.0), (379.5, 1.0), (380.5, 0.5)],
          grade="warm", fx=("punch", "thump") + G, shake=(379,)),
        S(382, 384, "n_flip", at=(1.0, 382), grade="warm", fx=("punch",) + G),
        S(384, 390, "r_villa", at=(3.0, 387), speed=[(384, 1.0), (387.5, 1.0), (388.5, 0.5)],
          grade="warm", fx=("punch", "thump") + G, label="VS ASTON VILLA  ·  2008"),
        S(390, 392, "r_skill4", at=(0.0, 390), grade="warm", fx=("punch",) + G),
        S(392, 396, "n_goal_d", at=(2.0, 394), grade="warm", fx=("punch", "thump") + G, shake=(394,)),
        S(396, 397, "r_celeb2", at=(0.0, 396), grade="warm", fx=("punch", "rgbhit") + G),
        S(397, 398, "n_celeb2", at=(0.0, 397), grade="warm", fx=("punch",) + G),
        S(398, 399, "r_celeb3", at=(0.0, 398), grade="warm", fx=("punch",) + G),
        S(399, 400, "n_celeb3", at=(0.0, 399), grade="warm", fx=("punch",) + G),
        S(400, 406, "r_pompey06", at=(3.0, 403), speed=[(400, 1.0), (403.5, 1.0), (404.5, 0.5)],
          grade="warm", fx=("flash", "punch", "thump") + G, shake=(403,), label="VS PORTSMOUTH  ·  2006"),
        S(406, 408, "r_celeb4", at=(0.0, 406), grade="warm", fx=("punch",) + G),
        S(408, 414, "n_goal_f", at=(3.0, 411), speed=[(408, 1.0), (411.5, 1.0), (412.5, 0.5)],
          grade="warm", fx=("punch", "thump") + G, shake=(411,)),
        S(414, 416, "n_celeb4", at=(0.0, 414), grade="warm", fx=("punch",) + G),
        S(416, 422, "r_goal_g", at=(3.0, 419), speed=[(416, 1.0), (419.5, 1.0), (420.5, 0.5)],
          grade="warm", fx=("punch", "thump") + G, shake=(419,)),
        S(422, 424, "r_celeb5", at=(0.0, 422), grade="warm", fx=("punch",) + G),
        S(424, 428, "rn_together", at=(0.0, 424), speed=0.7, grade="warm", fx=("punch", "thump_soft") + G),
        S(428, 432, "r_pose", at=(0.0, 428), speed=0.6, grade="warm", fx=("punch", "thump_soft") + G),

        # ---- outro ------------------------------------------------------
        S(432, 438, "rn_together2", at=(0.0, 432), speed=0.4, grade="warm", fx=("grain", "close"),
          close_beats=4, push=(1.0, 1.08), end="RONALDO  &  NANI|MANCHESTER UNITED", end_delay=0.5),
    ]
