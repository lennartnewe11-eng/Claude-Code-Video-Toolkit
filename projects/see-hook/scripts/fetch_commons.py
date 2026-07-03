#!/usr/bin/env python3
"""Fetch distinct, freely-licensed images from Wikimedia Commons (keyless) for
the Chunk-2 'two questions' collage. Saves 960px thumbs + records attribution."""
import json, subprocess, urllib.parse, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG = ROOT/"main_assets"/"c2"/"img"; IMG.mkdir(parents=True, exist_ok=True)
UA = "SeeVideoBot/1.0 (educational; contact lennart.newe@icloud.com)"

# id -> search term (all distinct topics; nothing reused elsewhere)
SHOTS = [
    ("bg",      "foggy forest hills germany"),
    ("lake1",   "aerial lake forest"),
    ("lake2",   "mountain lake reflection"),
    ("pond",    "small pond meadow"),
    ("dry",     "dry cracked lake bed"),
    ("puddle",  "rain puddle reflection"),
    ("ripple",  "water surface ripples"),
    ("clay",    "clay soil texture"),
    ("gravel",  "gravel pit sand"),
    ("river",   "forest river stream"),
]

def search(term):
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           "&generator=search&gsrnamespace=6&gsrlimit=4"
           "&gsrsearch=" + urllib.parse.quote(term) +
           "&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=960")
    o = subprocess.run(["curl","-sS","--max-time","40","-A",UA,url],
                       capture_output=True, text=True)
    try: return json.loads(o.stdout)
    except Exception: return {}

def dl(url, dest):
    o = subprocess.run(["curl","-sS","-L","--max-time","120","-A",UA,"-o",str(dest),url],
                       capture_output=True, text=True)
    return dest.exists() and dest.stat().st_size>15000

creds=[]
for sid, term in SHOTS:
    dest = IMG/f"{sid}.jpg"
    if dest.exists() and dest.stat().st_size>15000:
        print(f"[cached] {sid}"); continue
    d = search(term)
    pages = list(d.get("query",{}).get("pages",{}).values())
    # prefer wide, jpeg, decent size
    def ok(p):
        ii=(p.get("imageinfo") or [{}])[0]
        return ii.get("mime")=="image/jpeg" and ii.get("thumburl") and ii.get("width",0)>=ii.get("height",1)
    pages=[p for p in pages if ok(p)] or pages
    done=False
    for p in pages:
        ii=(p.get("imageinfo") or [{}])[0]
        turl=ii.get("thumburl")
        if turl and dl(turl, dest):
            title=p.get("title","")
            meta=ii.get("extmetadata",{})
            art=meta.get("Artist",{}).get("value","") if isinstance(meta.get("Artist"),dict) else ""
            lic=meta.get("LicenseShortName",{}).get("value","") if isinstance(meta.get("LicenseShortName"),dict) else ""
            print(f"[ok] {sid:7s} <- {title}")
            creds.append(f"- **{sid}** ({term}) — {title} · {lic}")
            done=True; break
    if not done: print(f"[FAIL] {sid}")
(IMG/"CREDITS.txt").write_text("Wikimedia Commons collage images (Chunk 2):\n"+"\n".join(creds)+"\n")
print("DONE")
