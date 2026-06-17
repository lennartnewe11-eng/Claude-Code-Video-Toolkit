#!/usr/bin/env python3
"""Search Freesound and download an HQ preview (token auth, no OAuth needed).

Usage:
  freesound_fetch.py search "<query>" [count]
  freesound_fetch.py get <sound_id> <outpath>

Reads FREESOUND_API_KEY from the environment.
"""
import sys, os, json, urllib.parse, urllib.request

KEY = os.environ["FREESOUND_API_KEY"]
UA = "usa-train-video/1.0"
BASE = "https://freesound.org/apiv2"


def _get(url):
    req = urllib.request.Request(
        url, headers={"Authorization": f"Token {KEY}", "User-Agent": UA}
    )
    return urllib.request.urlopen(req, timeout=40)


def search(query, count=8):
    qs = urllib.parse.urlencode({
        "query": query, "page_size": count,
        "fields": "id,name,license,duration,previews",
        "filter": "duration:[0.2 TO 12]",
        "sort": "rating_desc",
    })
    d = json.load(_get(f"{BASE}/search/text/?{qs}"))
    out = [{
        "id": r["id"], "name": r["name"], "license": r["license"],
        "duration": round(r.get("duration", 0), 1),
    } for r in d.get("results", [])]
    print(json.dumps(out, indent=2, ensure_ascii=False))


def get(sound_id, outpath):
    d = json.load(_get(f"{BASE}/sounds/{sound_id}/"))
    url = d["previews"]["preview-hq-mp3"]
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with _get(url) as r, open(outpath, "wb") as f:
        f.write(r.read())
    print(json.dumps({"saved": outpath, "id": sound_id,
                      "name": d["name"], "license": d["license"],
                      "bytes": os.path.getsize(outpath)}, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1] == "search":
        search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    elif sys.argv[1] == "get":
        get(sys.argv[2], sys.argv[3])
