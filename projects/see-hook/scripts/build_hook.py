#!/usr/bin/env python3
"""Assemble the 'See' hook: cut footage to the voiceover, generate kinetic
yellow (Helvetica) karaoke captions, and grade the whole frame like a warm
old CRT tube-TV signal.

Steps:
  1. normalize each source clip (trim/scale/crop/fps) -> build/clip_*.mp4
  2. concat -> build/base.mp4
  3. generate build/captions.ass (word-synced karaoke) + build/scanlines.png
  4. final ffmpeg: subtitles -> warm grade -> bloom -> chroma shift ->
     tube curvature -> scanlines -> vignette -> analog noise, + voiceover
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS, BUILD, OUT = ROOT / "assets", ROOT / "build", ROOT / "out"
FONTS = ROOT / "fonts"
BUILD.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

FF = "ffmpeg"
HOOK_END = 22.70  # end of the tagline segment

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr[-3000:])
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])} ...")
    return p

# ---------------------------------------------------------------- shot list
manifest = {m["shot"]: m for m in json.loads((BUILD / "footage_manifest.json").read_text()) if m.get("ok")}
# shot id -> (timeline_start, timeline_end, source_in_offset)
SHOTS = [
    ("A_lake1",   0.00,  2.63, 1.0),
    ("B_lake2",   2.63,  5.57, 0.3),
    ("C_notlake", 5.57,  8.31, 2.0),
    ("D_terrain", 8.31, 12.30, 0.5),
    ("E_plateau",12.30, 15.05, 6.0),
    ("F_weather",15.05, 18.21, 2.0),
    ("G_moody",  18.21, 19.69, 8.0),
    ("H_tagline",19.69, HOOK_END, 5.0),
]

def normalize_clips():
    concat_lines = []
    for sid, t0, t1, off in SHOTS:
        src = ASSETS / manifest[sid]["file"]
        dur = round(t1 - t0, 3)
        dst = BUILD / f"clip_{sid}.mp4"
        run([FF, "-y", "-ss", str(off), "-i", str(src), "-t", str(dur),
             "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,"
                    "crop=1920:1080,fps=30,setsar=1,format=yuv420p",
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             str(dst)])
        concat_lines.append(f"file '{dst.as_posix()}'")
        print(f"  normalized {sid} ({dur}s)")
    (BUILD / "concat.txt").write_text("\n".join(concat_lines) + "\n")
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "concat.txt"),
         "-c", "copy", str(BUILD / "base.mp4")])
    print("  -> base.mp4")

# ---------------------------------------------------------------- captions
def cs(t):  # seconds -> centiseconds int
    return int(round(t * 100))

def ass_time(t):
    h = int(t // 3600); t -= h * 3600
    m = int(t // 60); t -= m * 60
    s = int(t); c = int(round((t - s) * 100))
    if c == 100:
        s += 1; c = 0
    return f"{h:d}:{m:02d}:{s:02d}.{c:02d}"

def build_lines():
    """Group transcript words into short caption lines (<=5 words, break on
    sentence/clause punctuation), keeping only words before HOOK_END."""
    words = []
    for seg in json.loads((ROOT / "audio/transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            if w["start"] < HOOK_END and w.get("score", 1) > 0.2:
                words.append(w)
    lines, cur = [], []
    for w in words:
        cur.append(w)
        txt = w["word"]
        ends_clause = txt.endswith((".", "?", "!", ",", ";", ":"))
        if len(cur) >= 5 or ends_clause:
            lines.append(cur); cur = []
    if cur:
        lines.append(cur)
    return lines

def write_ass():
    lines = build_lines()
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Liberation Sans,74,&H0000FFFF,&H001466B4,&H00101010,&H80000000,-1,0,0,0,100,100,0.6,0,1,4,3,2,140,140,120,1
"""
    ev = ["[Events]",
          "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for ln in lines:
        start = ln[0]["start"]
        end = ln[-1]["end"]
        prev = start
        parts = []
        for w in ln:
            k = max(1, cs(w["end"] - prev))   # fill duration in cs, cumulative-synced
            prev = w["end"]
            parts.append(f"{{\\kf{k}}}{w['word']} ")
        text = "".join(parts).rstrip()
        # gentle pop-in + slight breathing scale for the kinetic feel
        text = "{\\fad(110,110)\\t(0,140,\\fscx104\\fscy104)}" + text
        ev.append(f"Dialogue: 0,{ass_time(max(0,start-0.10))},{ass_time(end+0.12)},"
                  f"Cap,,0,0,0,,{text}")
    (BUILD / "captions.ass").write_text(header + "\n".join(ev) + "\n")
    print(f"  captions.ass ({len(lines)} lines)")

def write_scanlines():
    dst = BUILD / "scanlines.png"
    run([FF, "-y", "-f", "lavfi", "-i", "nullsrc=s=1920x1080",
         "-vf", "geq=lum='if(mod(Y\\,2)\\,255\\,196)':cb=128:cr=128,format=gray",
         "-frames:v", "1", str(dst)])
    print("  scanlines.png")

# ---------------------------------------------------------------- final render
def render_final():
    base = BUILD / "base.mp4"
    ass = (BUILD / "captions.ass").as_posix()
    out = OUT / "see_hook_16x9.mp4"
    vf = (
        f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()}[cap];"
        # --- warm tube grade ---
        "[cap]colortemperature=temperature=4600:mix=1:pl=1,"
        "eq=contrast=1.06:saturation=1.22:gamma=0.98:brightness=0.012,"
        "curves=r='0/0 0.5/0.57 1/1':g='0/0 0.5/0.5 1/0.99':b='0/0 0.5/0.44 1/0.94'[grade];"
        # --- bloom / tube glow ---
        "[grade]split[g1][g2];[g2]gblur=sigma=9[gb];"
        "[g1][gb]blend=all_mode=screen:all_opacity=0.30[bloom];"
        # --- chromatic aberration + tube curvature ---
        "[bloom]rgbashift=rh=2:bh=-2[ca];"
        "[ca]lenscorrection=k1=0.06:k2=0.015:i=bilinear[lens];"
        # --- scanlines ---
        "[1:v]scale=1920:1080,setsar=1[scan];"
        "[lens][scan]blend=all_mode=multiply:all_opacity=0.60[sl];"
        # --- vignette, analog noise, fades ---
        "[sl]vignette=PI/4.6,noise=alls=7:allf=t+u,"
        "fade=t=in:st=0:d=0.5,fade=t=out:st=22.2:d=0.5,format=yuv420p[v]"
    )
    run([FF, "-y",
         "-i", str(base),
         "-loop", "1", "-i", str(BUILD / "scanlines.png"),
         "-i", str(ROOT / "audio/voiceover.wav"),
         "-filter_complex", vf,
         "-map", "[v]", "-map", "2:a",
         "-af", "afade=t=out:st=22.2:d=0.5",
         "-t", str(HOOK_END),
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
         str(out)])
    print(f"  -> {out}")

if __name__ == "__main__":
    print("[1/4] normalizing clips + concat"); normalize_clips()
    print("[2/4] captions"); write_ass()
    print("[3/4] scanline overlay"); write_scanlines()
    print("[4/4] final render (CRT grade + captions + audio)"); render_final()
    print("DONE")
