#!/usr/bin/env python3
"""ASS-Untertitel erzeugen. libass kann Positionierung, \\fad, \\t-Transformationen
und Karaoke-Timing -- damit laesst sich die typische Wort-fuer-Wort-Typo des
Edit-Stils bauen. (drawtext fehlt in diesem ffmpeg-Build.)"""
import os

W, H = 1080, 1920

HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Inter Display,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,7,0,5,60,60,60,1
Style: Slot,Inter Display,46,&H009A9A9A,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,2,0,1,0,0,5,60,60,60,1
Style: SlotSub,Inter Display,34,&H00636363,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,60,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

def dialogue(t0, t1, style, text, x=None, y=None, layer=0):
    pos = f"{{\\pos({int(x)},{int(y)})}}" if x is not None else ""
    return f"Dialogue: {layer},{ts(t0)},{ts(t1)},{style},,0,0,0,,{pos}{text}\n"

def write_ass(path, events):
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEAD)
        for e in events: f.write(e)
    return path
