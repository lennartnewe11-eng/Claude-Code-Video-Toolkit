#!/usr/bin/env python3
"""Ansichtsfassungen fuer die Weitergabe.

Zwei Codecs, weil nicht jeder Browser H.264 kann: Chromium-Builds ohne
proprietaere Codecs (unter Linux verbreitet) spielen eine H.264-Datei gar
nicht ab. Der Browser nimmt per <source> automatisch, was er dekodieren kann.

720p ist der Standard: weniger als die halbe Pixelmenge, gut ein Drittel der
Groesse, und es laedt auch bei schmaler Leitung sofort.
"""
import json, math, os, subprocess, sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(PROJ, "out")

def run(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a], check=True)

def size(p):
    return os.path.getsize(p) / 1048576

def bitrate(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=bit_rate",
                          "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(out.stdout.strip())

def duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(out.stdout.strip())

# --- Download-Fassung --------------------------------------------------------
# Das Artefakt liefert hoechstens 15 MB je Datei und 64 MB je Version aus, das
# Master hat 729 MB. Also eine eigene Downloadfassung, so hoch wie das Budget
# hergibt -- und in Stuecke zerlegt, die einzeln unter das Dateilimit passen.
# Byteweise geteilt und byteweise wieder gefuegt ergibt exakt dieselbe Datei;
# die Ansichtsseite setzt sie im Browser zusammen.
PART_MAX  = 12 * 1000 * 1000     # je Stueck, mit Abstand unter dem 15-MB-Limit
HQ_BUDGET = 36 * 1000 * 1000     # ganze Datei; der Rest des Versionsbudgets
                                 # gehoert den drei Ansichtsfassungen

def encode_hq(src, dst, budget=HQ_BUDGET, audio_kbit=192):
    """Zwei Durchgaenge auf eine Zielgroesse. CRF trifft keine Groesse --
    bei einem festen Budget ist die Bitrate das vorzugebende Mass."""
    dur = duration(src)
    v_kbit = int((budget * 8 / dur - audio_kbit * 1000) / 1000 * 0.97)
    log = os.path.join(os.path.dirname(dst), "x264_2pass")
    common = ["-i", src, "-c:v", "libx264", "-b:v", f"{v_kbit}k",
              "-preset", "slow", "-profile:v", "high", "-level", "5.0",
              "-g", "120", "-keyint_min", "60", "-pix_fmt", "yuv420p",
              "-passlogfile", log]
    run(*common, "-pass", "1", "-an", "-f", "mp4", os.devnull)
    run(*common, "-pass", "2", "-c:a", "aac", "-b:a", f"{audio_kbit}k", "-ac", "2",
        "-movflags", "+faststart", dst)
    for f in os.listdir(os.path.dirname(dst)):
        if f.startswith("x264_2pass"):
            os.remove(os.path.join(os.path.dirname(dst), f))
    return v_kbit

def de(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")

def split_parts(src, out_dir, stem, part_max=PART_MAX):
    """Zerlegt die Datei in Stuecke und schreibt einen Index dazu.

    Die Stuecke heissen .p0.mp4 usw., obwohl nur das letzte fuer sich genommen
    ein gueltiges MP4 waere: das Artefakt liefert nur bekannte Web-Dateitypen
    aus, eine Endung wie .000 lehnt es ab. Uebertragen werden die Bytes so oder
    so unveraendert -- abgeholt wird ueber fetch, nicht ueber ein video-Element.
    """
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.startswith(stem):
            os.remove(os.path.join(out_dir, f))
    total = os.path.getsize(src)
    n = math.ceil(total / part_max)
    chunk = math.ceil(total / n)
    parts = []
    with open(src, "rb") as fh:
        for i in range(n):
            name = f"{stem}.p{i}.mp4"
            data = fh.read(chunk)
            with open(os.path.join(out_dir, name), "wb") as o:
                o.write(data)
            parts.append({"name": name, "bytes": len(data)})
    index = {"file": os.path.basename(src), "bytes": total,
             "type": "video/mp4", "parts": parts}
    with open(os.path.join(out_dir, stem + ".json"), "w") as o:
        json.dump(index, o, indent=1)
    return index

def write_manifest(hq, hi, mp4, index, v_kbit, out_dir):
    """Index fuer die Downloadknoepfe der Ansichtsseite.

    Groessen und Stueckliste gehoeren hierher und nicht in die HTML-Seite:
    dort standen sie schon einmal veraltet drin, und eine falsche Groesse
    laesst die Laengenpruefung im Browser fehlschlagen.
    """
    items = [
        {"label": "1080 × 1920 · 60 fps",
         "meta":  f"H.264 High · {de(v_kbit/1000)} Mbit/s · {de(size(hq))} MB · volle Bildrate",
         "save":  "ch_akt1_1080p60.mp4",
         "bytes": os.path.getsize(hq),
         "parts": ["hq/" + q["name"] for q in index["parts"]]},
        {"label": "1080 × 1920 · 30 fps",
         "meta":  f"H.264 High · {de(bitrate(hi)/1e6)} Mbit/s · {de(size(hi))} MB",
         "save":  "ch_akt1_1080p30.mp4",
         "bytes": os.path.getsize(hi),
         "parts": ["act1.mp4"]},      # unter diesem Namen liegt sie auf der Seite
        {"label": "720 × 1280 · 30 fps",
         "meta":  f"H.264 Main · {de(bitrate(mp4)/1e6)} Mbit/s · {de(size(mp4))} MB",
         "save":  "ch_akt1_720p30.mp4",
         "bytes": os.path.getsize(mp4),
         "parts": [os.path.basename(mp4)]},
    ]
    with open(os.path.join(out_dir, "downloads.json"), "w") as o:
        json.dump({"items": items}, o, ensure_ascii=False, indent=1)
    return items

def main(src=None):
    src = src or os.path.join(OUT, "act1.mp4")
    base = os.path.splitext(os.path.basename(src))[0]

    # 720p H.264 -- Main/Level 4.0 laeuft ueberall in Hardware
    mp4 = os.path.join(OUT, f"{base}_720.mp4")
    run("-i", src, "-vf", "fps=30,scale=720:1280:flags=lanczos",
        "-c:v", "libx264", "-crf", "25", "-preset", "slower",
        "-profile:v", "main", "-level", "4.0",
        "-maxrate", "1600k", "-bufsize", "3200k",
        "-g", "60", "-keyint_min", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "112k", "-ac", "2",
        "-movflags", "+faststart", mp4)

    # 720p VP9/Opus -- Ausweichquelle fuer Browser ohne H.264
    webm = os.path.join(OUT, f"{base}_720.webm")
    run("-i", src, "-vf", "fps=30,scale=720:1280:flags=lanczos",
        "-c:v", "libvpx-vp9", "-crf", "34", "-b:v", "0",
        "-speed", "3", "-row-mt", "1", "-tile-columns", "1",
        "-g", "60", "-pix_fmt", "yuv420p",
        "-c:a", "libopus", "-b:a", "96k", webm)

    # 1080p H.264 als Umschaltoption
    hi = os.path.join(OUT, f"{base}_web.mp4")
    run("-i", src, "-vf", "fps=30",
        "-c:v", "libx264", "-crf", "24", "-preset", "slower",
        "-profile:v", "high", "-level", "4.1",
        "-maxrate", "2300k", "-bufsize", "4600k",
        "-g", "60", "-keyint_min", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", hi)

    # 1080p60 zum Herunterladen -- volle Bildrate, rund das Dreifache der
    # Bitrate der Ansichtsfassung
    hq = os.path.join(OUT, f"{base}_1080p60.mp4")
    v_kbit = encode_hq(src, hq)
    index = split_parts(hq, os.path.join(OUT, "hq"), f"{base}_1080p60")

    write_manifest(hq, hi, mp4, index, v_kbit, os.path.join(OUT, "hq"))

    poster = os.path.join(OUT, f"{base}_poster.jpg")
    run("-ss", "1.2", "-i", src, "-frames:v", "1",
        "-vf", "scale=540:960", "-q:v", "4", poster)

    for p in (mp4, webm, hi, poster):
        print(f"  {os.path.basename(p):26s} {size(p):6.2f} MB")
    print(f"  {os.path.basename(hq):26s} {size(hq):6.2f} MB  "
          f"({v_kbit} kbit/s Video, in {len(index['parts'])} Stuecken)")
    for q in index["parts"]:
        print(f"    hq/{q['name']:24s} {q['bytes']/1048576:6.2f} MB")

    ship = [mp4, webm, hi, poster] + [os.path.join(OUT, "hq", q["name"]) for q in index["parts"]]
    total = sum(os.path.getsize(p) for p in ship)
    big = [p for p in ship if os.path.getsize(p) > 15 * 1000 * 1000]
    print(f"\nAusgeliefert: {total/1048576:.1f} MB in {len(ship)} Dateien "
          f"(Limit 15 MB je Datei, 64 MB je Version).")
    if big:
        print("ZU GROSS: " + ", ".join(os.path.basename(p) for p in big))

if __name__ == "__main__":
    main(*sys.argv[1:])
