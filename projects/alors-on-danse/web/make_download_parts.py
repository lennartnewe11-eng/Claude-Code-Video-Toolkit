"""Split the download MP4 into <=14 MB parts + parts/manifest.json for web/download.html.

The artifact host serves files up to 15 MB each; the page fetches the parts,
checks every size, joins them into one Blob and hands it to the viewer's save
dialog, so the result is byte-identical to the input file.

usage: python3 make_download_parts.py Alors_on_danse_1080p.mp4 OUTDIR
"""
import hashlib
import json
import os
import sys

src, out = sys.argv[1], sys.argv[2]
CHUNK = 14_000_000
os.makedirs(os.path.join(out, "parts"), exist_ok=True)
parts, h = [], hashlib.sha256()
with open(src, "rb") as f:
    while True:
        b = f.read(CHUNK)
        if not b:
            break
        h.update(b)
        name = f"part_{len(parts):02d}.mp4"
        with open(os.path.join(out, "parts", name), "wb") as o:
            o.write(b)
        parts.append({"name": name, "size": len(b)})
manifest = {"filename": os.path.basename(src), "size": os.path.getsize(src),
            "sha256": h.hexdigest(), "parts": parts}
with open(os.path.join(out, "parts", "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=1)
print(f"{len(parts)} parts, {manifest['size']} bytes")
