#!/usr/bin/env python3
"""Download clips from share links and build a manifest of what arrived.

Usage:
    python3 montage/ingest.py links.txt --out footage/

links.txt holds one URL per line (blank lines and #-comments ignored).
An optional "URL  name.mp4" second column forces the local filename.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def direct_link(url: str) -> str:
    """Rewrite common share links into ones curl can actually fetch."""
    if "dropbox.com" in url:
        url = re.sub(r"[?&]dl=0", "", url)
        return url + ("&" if "?" in url else "?") + "dl=1"
    if "drive.google.com" in url:
        m = re.search(r"/d/([A-Za-z0-9_-]+)", url) or re.search(r"[?&]id=([A-Za-z0-9_-]+)", url)
        if m:
            return f"https://drive.usercontent.google.com/download?id={m.group(1)}&export=download&confirm=t"
    if "1drv.ms" in url or "onedrive.live.com" in url:
        return url + ("&" if "?" in url else "?") + "download=1"
    return url


def filename_for(url: str, index: int) -> str:
    name = Path(urlparse(url).path).name
    qs = parse_qs(urlparse(url).query)
    if "id" in qs and not name:
        name = qs["id"][0]
    if not name or "." not in name:
        name = f"clip{index:02d}.mp4"
    return name


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  exists, skipping: {dest.name}")
        return True
    cmd = ["curl", "-fL", "--retry", "3", "--retry-delay", "2",
           "-A", "Mozilla/5.0", "-o", str(dest), direct_link(url)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  FAILED ({result.returncode}): {url}", file=sys.stderr)
        dest.unlink(missing_ok=True)
        return False
    return True


def probe(path: Path) -> dict | None:
    cmd = ["ffprobe", "-v", "error", "-print_format", "json",
           "-show_format", "-show_streams", str(path)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    data = json.loads(out.stdout)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    if video is None:
        return None
    num, den = (video.get("r_frame_rate") or "0/1").split("/")
    fps = round(int(num) / int(den), 3) if int(den) else 0
    width, height = int(video["width"]), int(video["height"])
    # rotation metadata means a phone clip is displayed turned
    rotation = 0
    for side in video.get("side_data_list") or []:
        if "rotation" in side:
            rotation = int(side["rotation"])
    if abs(rotation) in (90, 270):
        width, height = height, width
    return {
        "file": str(path),
        "name": path.name,
        "duration": round(float(data["format"].get("duration", 0)), 3),
        "width": width,
        "height": height,
        "aspect": round(width / height, 3) if height else 0,
        "orientation": "landscape" if width >= height else "portrait",
        "fps": fps,
        "codec": video.get("codec_name"),
        "has_audio": audio is not None,
        "size_mb": round(path.stat().st_size / 1e6, 1),
        "rotation": rotation,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("links", help="text file with one share URL per line")
    parser.add_argument("--out", default="footage", help="download directory")
    args = parser.parse_args()

    if not shutil.which("ffprobe"):
        print("ffprobe not found - install ffmpeg first", file=sys.stderr)
        return 1

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    entries = []
    for line in Path(args.links).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split()
            entries.append((parts[0], parts[1] if len(parts) > 1 else None))

    manifest, failed = [], []
    for i, (url, forced) in enumerate(entries, 1):
        name = forced or filename_for(url, i)
        dest = outdir / name
        print(f"[{i}/{len(entries)}] {name}")
        if not download(url, dest):
            failed.append(url)
            continue
        info = probe(dest)
        if info is None:
            print(f"  not a readable video: {dest.name}", file=sys.stderr)
            failed.append(url)
            continue
        manifest.append(info)

    manifest_path = outdir / "clips.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"\n{len(manifest)} clip(s) ready, {len(failed)} failed")
    total = sum(c["duration"] for c in manifest)
    print(f"total footage: {total / 60:.1f} min")
    for c in manifest:
        print(f"  {c['name']:<32} {c['width']}x{c['height']:<6} "
              f"{c['duration']:>7.1f}s {c['fps']:>5}fps {c['orientation']}")
    if failed:
        print("\nfailed:", *failed, sep="\n  ")
    print(f"\nmanifest: {manifest_path}")
    return 0 if manifest else 1


if __name__ == "__main__":
    raise SystemExit(main())
