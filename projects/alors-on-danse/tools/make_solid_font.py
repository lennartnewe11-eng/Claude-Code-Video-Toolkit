"""Make fonts/Ballet-Solid.ttf from the variable fonts/Ballet.ttf.

Ballet's glyphs are built from overlapping contours. Rasterised as they are,
the overlaps come out as holes, so thick strokes look hollow or hatched. This
pins the optical-size axis at 16 (the form used in the edit) and merges the
overlaps into single outlines.

usage: pip install fonttools skia-pathops && python3 make_solid_font.py
"""
import os

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
font = TTFont(os.path.join(FONTS, "Ballet.ttf"))
solid = instancer.instantiateVariableFont(font, {"opsz": 16},
                                          overlap=instancer.OverlapMode.REMOVE)
solid.save(os.path.join(FONTS, "Ballet-Solid.ttf"))
print("wrote fonts/Ballet-Solid.ttf")
