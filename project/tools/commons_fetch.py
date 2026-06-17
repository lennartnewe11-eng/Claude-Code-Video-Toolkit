#!/usr/bin/env python3
"""Search Wikimedia Commons and download CC media candidates.

Usage:
  commons_fetch.py search  "<query>" <video|image> [count]
  commons_fetch.py get     "File:Name.ext" <outpath>

Lists title, license, mime, size, dimensions so we can pick deliberately.
"""
import sys, json, os, urllib.parse, urllib.request

UA = "usa-train-video/1.0 (lennart.newe@icloud.com)"
API = "https://commons.wikimedia.org/w/api.php"


def _get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=40))


def search(query, kind, count=8):
    # mime filter
    mimes = ("video/",) if kind == "video" else ("image/jpeg", "image/png")
    d = _get({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:{kind} {query}", "gsrnamespace": 6,
        "gsrlimit": count * 3,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    })
    pages = (d.get("query", {}) or {}).get("pages", {})
    rows = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        mime = ii.get("mime", "")
        if not any(mime.startswith(m) for m in mimes):
            continue
        ext = ii.get("extmetadata", {})
        lic = (ext.get("LicenseShortName", {}) or {}).get("value", "?")
        rows.append({
            "title": p.get("title"),
            "license": lic,
            "mime": mime,
            "w": ii.get("width"), "h": ii.get("height"),
            "size_mb": round((ii.get("size") or 0) / 1e6, 1),
            "url": ii.get("url"),
        })
    rows = rows[:count]
    print(json.dumps(rows, indent=2, ensure_ascii=False))


def get(title, outpath):
    d = _get({
        "action": "query", "format": "json", "titles": title,
        "prop": "imageinfo", "iiprop": "url|extmetadata",
    })
    p = next(iter(d["query"]["pages"].values()))
    ii = p["imageinfo"][0]
    url = ii["url"]
    ext = ii.get("extmetadata", {})
    lic = (ext.get("LicenseShortName", {}) or {}).get("value", "?")
    artist = (ext.get("Artist", {}) or {}).get("value", "?")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(outpath, "wb") as f:
        f.write(r.read())
    print(json.dumps({"saved": outpath, "src_url": url,
                      "license": lic, "artist": artist,
                      "bytes": os.path.getsize(outpath)}, ensure_ascii=False))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        search(sys.argv[2], sys.argv[3],
               int(sys.argv[4]) if len(sys.argv) > 4 else 8)
    elif cmd == "get":
        get(sys.argv[2], sys.argv[3])
