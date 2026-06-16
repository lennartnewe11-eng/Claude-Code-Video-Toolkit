#!/usr/bin/env python3
"""Download free hook assets (Wikimedia Commons + archive.org) into assets/footage/.

Only fetches freely licensed material (PD / CC0 / CC-BY[-SA]). Pexels/Pixabay are
NOT included (they block automated download); grab those manually if needed.

For every Commons file it records license + author into assets/footage/CREDITS.md
so CC-BY / CC-BY-SA attribution can be honoured. archive.org films are PD/promo
but verify each item's "Rights" field before publishing.

Run from project root:  python3 scripts/fetch_assets.py
Re-running skips files already present.
"""
import os, sys, json, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(HERE, "assets", "footage")
os.makedirs(DEST, exist_ok=True)
UA = "ClaudeVideoToolkit/1.0 (asset fetch; contact lennart.newe@icloud.com)"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Commons direct upload URLs, mapped to a target basename keyed by hook shot.
COMMONS = [
    # videos (CC) — modern HSR
    ("S1-3_shinkansen_tokyo",  "https://upload.wikimedia.org/wikipedia/commons/5/59/Shinkansen_N700_Series_Bullet_Train_Tokyo_Station_by_Don_Ramey_Logan.webm"),
    ("S1-3_shinkansen_pass",   "https://upload.wikimedia.org/wikipedia/commons/c/ca/Shinkansen_bullet_train.webm"),
    ("S4-6_tgv_labenne",       "https://upload.wikimedia.org/wikipedia/commons/1/12/Passage_d%27un_TGV_en_Gare_de_Labenne.webm"),
    ("S4-6_tgv_grossgerau",    "https://upload.wikimedia.org/wikipedia/commons/2/27/TGV_durch_Gro%C3%9F-Gerau.webm"),
    ("S7-9_china_hsr_station", "https://upload.wikimedia.org/wikipedia/commons/2/26/China_Railway_High-speed_train_passing_through_station.webm"),
    ("S7-9_china_crh_yuyao",   "https://upload.wikimedia.org/wikipedia/commons/5/52/CRH_entering_Yuyao_Station_201907141725.webm"),
    ("S14-15_decay_lebanon_voa", "https://upload.wikimedia.org/wikipedia/commons/b/bf/VOA_railways_in_Lebanon_2446332_1551192434_%28Source%29.webm"),
    # stills (PD / CC) — US golden age + decline
    ("S16_golden_spike_1869",  "https://upload.wikimedia.org/wikipedia/commons/e/e4/1869-Golden_Spike.jpg"),
    ("S13b_grand_central_1941","https://upload.wikimedia.org/wikipedia/commons/9/9a/Grand_Central_Terminal%2C_New_York_City%2C_Collier%2C_John_Jr.jpg"),
    ("S16_pullman_interior",   "https://upload.wikimedia.org/wikipedia/commons/c/cb/Pullman_car_interior.jpg"),
    ("S16_dining_car_1894",    "https://upload.wikimedia.org/wikipedia/commons/2/2a/Pullman_dining_car_1894.jpg"),
    ("S16_platform_crowd_1927","https://upload.wikimedia.org/wikipedia/commons/2/20/Crowd_at_train_station_during_Native_American_visit_to_Oxford_1927_%283191872099%29.jpg"),
    ("S12_empire_state_hine",  "https://upload.wikimedia.org/wikipedia/commons/1/1c/Photograph_of_a_Workman_on_the_Framework_of_the_Empire_State_Building_-_NARA_-_518290.jpg"),
    ("S14_abandoned_overgrown","https://upload.wikimedia.org/wikipedia/commons/9/97/Abandoned_Railroad_overgrown_-_panoramio.jpg"),
]

# archive.org film identifiers (PD/promo — verify Rights). Prefer a compact mp4 derivative.
ARCHIVE = [
    ("S13a_silver_streak_zephyr", "md-86524-streamlined-vwr"),
    ("S13a_california_zephyr",    "70922CaliforniaZephyr"),
    ("S13a_passenger_train_1940", "passenger_train"),
]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90)


def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  skip (exists): {os.path.basename(path)}")
        return os.path.getsize(path)
    tmp = path + ".part"
    with get(url) as r, open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    os.replace(tmp, path)
    return os.path.getsize(path)


def commons_meta(filename):
    """Return (license, author_plain) for a Commons File:<filename>."""
    q = {"action": "query", "titles": "File:" + filename, "prop": "imageinfo",
         "iiprop": "extmetadata", "format": "json"}
    try:
        d = json.load(get(COMMONS_API + "?" + urllib.parse.urlencode(q)))
        p = next(iter(d["query"]["pages"].values()))
        em = p["imageinfo"][0]["extmetadata"]
        lic = em.get("LicenseShortName", {}).get("value", "?")
        art = em.get("Artist", {}).get("value", "")
        import re
        art = re.sub("<[^>]+>", "", art).strip()
        return lic, art
    except Exception as e:
        return "?", f"(meta failed: {e})"


def best_archive_mp4(identifier):
    meta = json.load(get(f"https://archive.org/metadata/{identifier}"))
    files = meta.get("files", [])
    mp4s = [f for f in files if f["name"].lower().endswith(".mp4")]
    # prefer a smaller derivative (512kb) over the hi-res master
    mp4s.sort(key=lambda f: (0 if "512kb" in f["name"].lower() else 1, int(f.get("size", 0) or 0)))
    return mp4s[0]["name"] if mp4s else None


def main():
    credits = ["# Asset-Credits (Hook)\n",
               "Automatisch erzeugt von `scripts/fetch_assets.py`. CC-BY/CC-BY-SA verlangen Namensnennung.\n"]
    total = 0
    print("== Wikimedia Commons ==")
    for shot, url in COMMONS:
        fname = urllib.parse.unquote(url.rsplit("/", 1)[-1])
        ext = os.path.splitext(fname)[1]
        target = os.path.join(DEST, f"{shot}{ext}")
        try:
            size = download(url, target)
            total += size
            lic, author = commons_meta(fname)
            credits.append(f"- **{shot}{ext}** — {lic} — {author or '—'}\n  Quelle: https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(fname)}")
            print(f"  ok {shot}{ext}  [{lic}]  {size//1024} KB")
        except Exception as e:
            print(f"  FAIL {shot}: {e}")
            credits.append(f"- {shot}: DOWNLOAD FAILED ({e})")

    print("== archive.org ==")
    for shot, ident in ARCHIVE:
        try:
            name = best_archive_mp4(ident)
            if not name:
                print(f"  FAIL {shot}: no mp4 in {ident}")
                continue
            url = f"https://archive.org/download/{ident}/{urllib.parse.quote(name)}"
            target = os.path.join(DEST, f"{shot}.mp4")
            size = download(url, target)
            total += size
            credits.append(f"- **{shot}.mp4** — archive.org (Rights pro Item prüfen)\n  Quelle: https://archive.org/details/{ident}")
            print(f"  ok {shot}.mp4  {size//1024//1024} MB  ({name})")
        except Exception as e:
            print(f"  FAIL {shot}: {e}")
            credits.append(f"- {shot}: DOWNLOAD FAILED ({e})")

    open(os.path.join(DEST, "CREDITS.md"), "w").write("\n".join(credits) + "\n")
    print(f"\nDone. ~{total//1024//1024} MB into {DEST}. Credits -> assets/footage/CREDITS.md")


if __name__ == "__main__":
    main()
