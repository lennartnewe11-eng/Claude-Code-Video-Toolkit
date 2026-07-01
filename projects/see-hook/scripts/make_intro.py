#!/usr/bin/env python3
"""Build the ~12s 'Past.Present.Future.' intro.

Background: the uploaded field clip, washed + softly graded.
Foreground: the pencil sketch, drawn on stroke-by-stroke — revealed along a
geodesic order that spreads along the ink from the base of the vase upward,
so it looks like a pen tracing the lines. Bottom-right: Helvetica credit.
"""
import subprocess, pathlib, sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
IA, BUILD, OUT = ROOT/"intro_assets", ROOT/"build", ROOT/"out"
BG = ROOT/"intro_assets_v2"/"newbg.mp4"      # new, higher-quality background
DRAWING = ROOT/"intro_assets_v3"/"drawing.png"   # foreground sketch (new crowd png)
AUD = ROOT/"audio"
FRAMES = BUILD/"intro_frames"
FRAMES.mkdir(parents=True, exist_ok=True)
FF = "ffmpeg"

FPS = 30
TOTAL = 12.0
DRAW_START, DRAW_DUR = 0.6, 8.6      # sketch drawn between 0.6s and 9.2s
INK = (26, 24, 22)                    # charcoal
GLOW = (250, 250, 250)                # soft light halo so ink reads on the moody bg
SONG_OFFSET = 30.25                   # continue the hook's song seamlessly (hook END)

def run(cmd, label=""):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3000:]); raise SystemExit(1)
    return p

def draw_order(alpha):
    """Geodesic BFS distance along ink from the bottom; disconnected parts are
    seeded afterwards (lowest first) so everything draws as continuous strokes."""
    ink = alpha > 20
    H, W = ink.shape
    dist = np.full((H, W), -1, np.int32)
    ys, xs = np.where(ink)
    ymax, ymin = ys.max(), ys.min()
    seed_y = ymax - 0.02*(ymax - ymin)
    dq = deque()
    for y, x in zip(ys, xs):
        if y >= seed_y:
            dist[y, x] = 0; dq.append((y, x))
    nb = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def bfs():
        while dq:
            y, x = dq.popleft(); d = dist[y, x]
            for dy, dx in nb:
                ny, nx = y+dy, x+dx
                if 0 <= ny < H and 0 <= nx < W and ink[ny, nx] and dist[ny, nx] < 0:
                    dist[ny, nx] = d+1; dq.append((ny, nx))
    bfs()
    # seed remaining components (lowest y first), continuing the distance count
    while True:
        rem = ink & (dist < 0)
        if not rem.any(): break
        rys, rxs = np.where(rem)
        i = np.argmax(rys); sy, sx = rys[i], rxs[i]
        start = dist[dist >= 0].max() + 40
        dist[sy, sx] = start; dq.append((sy, sx)); bfs()
    order = dist.astype(np.float32)
    order[~ink] = np.inf
    order[ink] = order[ink] / order[ink].max()
    return order, ink

def smooth(x):
    x = max(0.0, min(1.0, x)); return x*x*(3-2*x)

def ink_strength(path):
    """Return a 0..255 ink-coverage map from a drawing PNG, whether it has a
    transparent background (use alpha) or a white background (use darkness)."""
    im = Image.open(path).convert("RGBA")
    a = np.array(im).astype(np.float32)
    alpha = a[:, :, 3]
    if (alpha < 250).mean() > 0.02:          # real transparency present
        s = alpha
    else:                                    # white bg -> ink = darkness
        gray = a[:, :, :3].mean(2)
        s = np.clip(255.0 - gray, 0, 255)
        s[s < 28] = 0                        # drop near-white paper
    return s

def gen_frames():
    alpha0 = ink_strength(DRAWING)
    order, ink = draw_order(alpha0)
    H, W = order.shape
    ink_rgb = np.zeros((H, W, 4), np.uint8)
    ink_rgb[:, :, 0], ink_rgb[:, :, 1], ink_rgb[:, :, 2] = INK
    glow_rgb = np.zeros((H, W, 4), np.uint8)
    glow_rgb[:, :, 0], glow_rgb[:, :, 1], glow_rgb[:, :, 2] = GLOW
    fw = 0.02
    n = int(TOTAL*FPS)
    for i in range(n):
        t = i/FPS
        p = smooth((t-DRAW_START)/DRAW_DUR)
        factor = np.clip((p-order)/fw, 0, 1)          # 1 behind frontier, soft edge
        al = (np.minimum(alpha0*1.5, 255)*factor).astype(np.uint8)
        # soft light halo behind the dark ink -> readable over the moody bg
        glow_a = Image.fromarray(al, "L").filter(ImageFilter.GaussianBlur(7))
        glow_layer = glow_rgb.copy()
        glow_layer[:, :, 3] = (np.array(glow_a).astype(np.float32)*0.65).astype(np.uint8)
        ink_layer = ink_rgb.copy(); ink_layer[:, :, 3] = al
        out = Image.alpha_composite(Image.fromarray(glow_layer, "RGBA"),
                                    Image.fromarray(ink_layer, "RGBA"))
        out.save(FRAMES/f"f_{i:04d}.png")
    print(f"  generated {n} frames (ink {int(ink.sum())}px)")

def write_credit_ass():
    # white text with a glow (blurred white halo + faint dark shadow), appears
    # at the half-way point.
    ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cr,Liberation Sans,44,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H64000000,0,0,0,0,100,100,0.4,0,1,2.4,1,3,70,80,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:06.00,0:00:12.00,Cr,,0,0,0,,{\\fad(650,300)\\blur6}eine Past.Present.Future. Produktion
"""
    (BUILD/"credit.ass").write_text(ass)

def compose():
    write_credit_ass()
    vf = (
        # NO video filter -- clean high-quality upscale only (better resolution)
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1920:1080,fps=30,setsar=1[bg];"
        # drawing overlay (with its own soft glow baked in), centred slightly high
        "[1:v]scale=760:-1[draw];"
        "[bg][draw]overlay=x=(W-w)/2:y=(H-h)/2-40:shortest=1[cmp];"
        f"[cmp]ass={(BUILD/'credit.ass').as_posix()},"
        f"fade=t=in:d=0.6,fade=t=out:st={TOTAL-0.6}:d=0.6,format=yuv420p[v];"
        # song: continue the hook's track from SONG_OFFSET, small fade-up
        f"[2:a]atrim=0:{TOTAL},volume=4.2,afade=t=in:d=2.0,"
        f"afade=t=out:st={TOTAL-0.6}:d=0.6,alimiter=limit=0.95[a]"
    )
    run([FF, "-y",
         "-stream_loop", "-1", "-i", str(BG),
         "-framerate", str(FPS), "-i", str(FRAMES/"f_%04d.png"),
         "-ss", str(SONG_OFFSET), "-i", str(AUD/"song.mp3"),
         "-filter_complex", vf, "-map", "[v]", "-map", "[a]", "-t", str(TOTAL),
         "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(OUT/"intro.mp4")], "compose")
    print("  ->", OUT/"intro.mp4")

if __name__ == "__main__":
    print("[1/2] generating stroke-by-stroke frames"); gen_frames()
    print("[2/2] composing intro"); compose()
    print("DONE ->", OUT/"intro.mp4")
