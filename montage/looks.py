#!/usr/bin/env python3
"""Colour grades for the three acts, plus the shared film treatment.

The grades share one filmic S-curve and one grain/vignette pass so that
clips shot hours apart still read as one colour world; only lift, warmth
and saturation change between acts.
"""

# shared across every shot: subtle grain + vignette hold the look together
FILM = "noise=alls=3:allf=t,vignette=a=PI/9"

LOOKS = {
    # night city: crushed blacks, teal shadows, pulled-back colour
    "dark": (
        # the footage is already dark - lift it so it stays readable and
        # carry the mood with cool shadows instead of less exposure
        "eq=contrast=1.14:brightness=0.030:saturation=0.74:gamma=1.10,"
        "curves=r='0/0 0.2/0.19 0.6/0.62 1/0.97':"
        "g='0/0 0.2/0.20 0.6/0.63 1/0.98':"
        "b='0/0.02 0.2/0.24 0.6/0.65 1/1',"
        "colorbalance=rs=-0.06:bs=0.10:rm=-0.02:bm=0.04"
    ),
    # travel / contrast act: punchy S-curve, neutral-cool, still restrained
    "mid": (
        "eq=contrast=1.18:brightness=0.005:saturation=0.86:gamma=1.00,"
        "curves=r='0/0.005 0.25/0.23 0.75/0.79 1/0.99':"
        "g='0/0.006 0.25/0.24 0.75/0.79 1/0.99':"
        "b='0/0.020 0.25/0.26 0.75/0.78 1/0.975',"
        "colorbalance=rs=-0.03:bs=0.05:rh=0.03:bh=-0.02"
    ),
    # sea / summer: lifted, warm, airy, open highlights
    "bright": (
        # keep the blacks honest so the sea holds contrast, warmth up top
        "eq=contrast=1.14:brightness=0.015:saturation=0.98:gamma=1.02,"
        "curves=r='0/0.012 0.3/0.32 0.7/0.74 1/1':"
        "g='0/0.012 0.3/0.31 0.7/0.72 1/0.995':"
        "b='0/0.022 0.3/0.30 0.7/0.69 1/0.965',"
        "colorbalance=rh=0.05:bh=-0.045:rm=0.02:bm=-0.015"
    ),
}


def fit_filter(width, height, target=(1920, 1080)):
    """Scale a source into the 16:9 frame.

    Landscape sources fill the frame; portrait ones sit on a blurred
    version of themselves rather than black bars.
    """
    tw, th = target
    if width / height >= (tw / th) - 0.01:
        return (f"scale={tw}:{th}:force_original_aspect_ratio=increase,"
                f"crop={tw}:{th},setsar=1")
    return (
        f"split[bg][fg];"
        f"[bg]scale={tw}:{th}:force_original_aspect_ratio=increase,"
        f"crop={tw}:{th},gblur=sigma=42,eq=brightness=-0.12[bgb];"
        f"[fg]scale={tw}:{th}:force_original_aspect_ratio=decrease[fgs];"
        f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1"
    )


# a shot that moves is fitted to this first, so the zoom crops into real
# detail instead of upscaling a frame already cut to the target size
OVERSCAN = (2112, 1188)
ZOOM = 0.05        # barely perceptible; a strong push reads as a slideshow


def move_filter(kind, frames, target=(1920, 1080), fps=30):
    """Slow push in or pull out across the shot."""
    tw, th = target
    n = max(frames - 1, 1)
    if kind == "in":
        z = f"min(1.0+{ZOOM}*on/{n},{1.0 + ZOOM})"
    elif kind == "out":
        z = f"max({1.0 + ZOOM}-{ZOOM}*on/{n},1.0)"
    else:
        return None
    return (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d=1:s={tw}x{th}:fps={fps}")


def build_chain(width, height, rate, look, fps=30, move=None, src_frames=None):
    """Full per-segment chain: fit -> move -> speed -> grade -> film -> format.

    The move runs BEFORE the speed change. zoompan's own fps setting
    rewrites the frame rate, which discards the stretch setpts applied - in
    slow motion the segment then ran out of frames and the fps filter
    padded it by holding the last one, freezing the shot before the cut.
    Its ramp is therefore counted in source frames, not timeline frames.
    """
    moving = move in ("in", "out") and src_frames
    parts = [fit_filter(width, height, OVERSCAN if moving else (1920, 1080))]
    if moving:
        parts.append(move_filter(move, src_frames, fps=fps))
    if abs(rate - 1.0) > 1e-3:
        parts.append(f"setpts={1.0 / rate:.6f}*PTS")
    parts.append(LOOKS[look])
    parts.append(FILM)
    parts.append(f"fps={fps}")
    parts.append("format=yuv420p")
    return ",".join(parts)
