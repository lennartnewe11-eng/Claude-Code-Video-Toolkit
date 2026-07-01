#!/usr/bin/env python3
"""Fetch cinematic footage from Pexels for the 'See' hook shot list.

Each shot has an ordered list of queries; we try each until we find a
landscape HD clip long enough to cover the shot. Downloaded files land in
assets/ and a manifest is written to build/footage_manifest.json.
"""
import json, os, sys, urllib.parse, pathlib, time, subprocess

KEY = os.environ.get("PEXELS_KEY", "").strip()
if not KEY:
    sys.exit("PEXELS_KEY env var required")

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BUILD = ROOT / "build"
ASSETS.mkdir(exist_ok=True)
BUILD.mkdir(exist_ok=True)

# shot id -> (min_seconds_needed, [queries in priority order])
SHOTS = [
    ("A_lake1",   3.0, ["aerial lake mountains sunrise", "cinematic mountain lake drone", "aerial alpine lake"]),
    ("B_lake2",   3.4, ["calm forest lake reflection", "still lake trees morning", "misty lake forest"]),
    ("C_notlake", 3.2, ["puddle reflection sky", "small puddle water street", "rain puddle reflection clouds"]),
    ("D_terrain", 4.4, ["aerial green valley drone", "aerial landscape countryside", "drone flying over hills"]),
    ("E_plateau", 3.1, ["aerial mountain plateau", "aerial highland terrain", "drone mountain ridge"]),
    ("F_weather", 3.6, ["clouds timelapse mountains", "storm clouds moving timelapse", "dramatic sky clouds landscape"]),
    ("G_moody",   2.0, ["foggy lake dark moody", "misty lake fog eerie", "dark water fog"]),
    ("H_tagline", 3.3, ["sunset lake calm aerial", "golden hour lake cinematic", "aerial lake sunset reflection"]),
]

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def api(query):
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": 15, "orientation": "landscape", "size": "medium"})
    out = subprocess.run(
        ["curl", "-sS", "--max-time", "40", "-A", UA, "-H", f"Authorization: {KEY}", url],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return json.loads(out.stdout)

def pick_file(video):
    """Pick best mp4 <=1920 wide, prefer exactly 1920x1080."""
    cands = [f for f in video["video_files"] if f.get("file_type") == "video/mp4" and f.get("width")]
    if not cands:
        return None
    def score(f):
        w = f["width"]
        exact = 1 if (w == 1920 and f.get("height") == 1080) else 0
        under = 1 if w <= 1920 else 0
        return (exact, under, -abs(1920 - w))
    cands.sort(key=score, reverse=True)
    return cands[0]

def download(url, dest):
    out = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "240", "-A", UA, "-o", str(dest), url],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return dest.stat().st_size

manifest = []
used_ids = set()
for sid, need, queries in SHOTS:
    chosen = None
    for q in queries:
        try:
            data = api(q)
        except Exception as e:
            print(f"  [{sid}] query '{q}' error: {e}")
            time.sleep(1)
            continue
        for v in data.get("videos", []):
            if v["id"] in used_ids:
                continue
            if v.get("duration", 0) < need:
                continue
            f = pick_file(v)
            if not f:
                continue
            chosen = (q, v, f)
            break
        if chosen:
            break
    if not chosen:
        print(f"!! [{sid}] NO CLIP FOUND")
        manifest.append({"shot": sid, "ok": False})
        continue
    q, v, f = chosen
    used_ids.add(v["id"])
    dest = ASSETS / f"{sid}_{v['id']}.mp4"
    size = download(f["link"], dest)
    print(f"OK [{sid}] id={v['id']} {f['width']}x{f['height']} dur={v['duration']}s "
          f"{size//1024}KB  q='{q}'")
    manifest.append({
        "shot": sid, "ok": True, "file": dest.name, "pexels_id": v["id"],
        "width": f["width"], "height": f["height"], "duration": v["duration"],
        "query": q, "url": v["url"], "user": v["user"]["name"], "user_url": v["user"]["url"],
    })

(BUILD / "footage_manifest.json").write_text(json.dumps(manifest, indent=2))
print("\nManifest written. Success:",
      sum(1 for m in manifest if m.get("ok")), "/", len(SHOTS))
