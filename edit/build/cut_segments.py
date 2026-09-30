"""Cut the segments in build/segments.txt out of their archive.org sources.

A source is read from media/raw/<alias>.mp4 when it has been downloaded,
otherwise straight from archive.org over HTTP (ffmpeg seeks with range
requests, so a 2-hour match is never fetched whole). Segments are re-encoded
at constant frame rate so every frame can be addressed exactly.

    python3 build/cut_segments.py [key ...]
"""
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BUILD, MEDIA = ROOT / "build", ROOT / "media"


def table(name, ncols):
    rows = []
    for line in (BUILD / name).read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            parts = line.split(None, ncols - 1) if ncols else line.split()
            rows.append(parts)
    return rows


def sources():
    out = {}
    for line in (BUILD / "archive_sources.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        alias, rest = line.split(None, 1)
        path = rest.split("   ")[0].strip()  # description follows after 3+ spaces
        local = MEDIA / "raw" / f"{alias}.mp4"
        out[alias] = str(local) if local.exists() and local.stat().st_size > 0 else \
            "https://archive.org/download/" + quote(path)
    return out


def main():
    src = sources()
    want = set(sys.argv[1:])
    (MEDIA / "src").mkdir(parents=True, exist_ok=True)
    for key, alias, start, dur, *_ in table("segments.txt", 5):
        if want and key not in want:
            continue
        dst = MEDIA / "src" / f"{key}.mp4"
        st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                        "stream=r_frame_rate,field_order", "-of", "json", src[alias]],
                                       capture_output=True, text=True).stdout)["streams"][0]
        rate, order = st["r_frame_rate"], st.get("field_order", "progressive")
        vf = "bwdif=mode=send_frame," if order not in ("progressive", "unknown", "") else ""
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", start, "-i", src[alias], "-t", dur,
                        "-vf", f"{vf}fps={rate}", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "14",
                        "-g", "12", "-pix_fmt", "yuv420p", str(dst)], check=True)
        print(f"{key:14s} {alias} {start}+{dur}s -> {dst.name} ({rate} fps, {order})")


if __name__ == "__main__":
    main()
