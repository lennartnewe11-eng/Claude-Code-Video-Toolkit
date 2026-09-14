#!/usr/bin/env python3
"""Laedt Quellclips aus Public-Domain-Archiven (NASA, Internet Archive/Prelinger)
und -- wenn der Key gerade durchkommt -- Pexels.

Alle Archivquellen sind Public Domain bzw. gemeinfrei; Herkunft wird in
assets/source/CREDITS.json mitgeschrieben.
"""
import json, os, subprocess, sys, time, urllib.parse

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST  = os.path.join(PROJ, "assets", "source")
os.makedirs(DST, exist_ok=True)

NASA = [
    ("nasa_saturnv",   "Ultimate Saturn V Launch w Enhanced Sound"),
    ("nasa_mga_reel",  "HD 049 Mercury_Gemini_Apollo_Resource Reel 1"),
]

# Internet Archive / Prelinger -- alle gemeinfrei
IA = [
    ("ia_telephone20",  "6136_How_the_Telephone_Talks_01_26_45_28"),
    ("ia_telephone65",  "0355_We_Learn_About_the_Telephone_I_09_01_02_00"),
    ("ia_electronics66","0823_Electronics_on_Parade_M04040_07_02_59_00"),
    ("ia_logicmachine", "0577_Logic_by_Machine_15_01_03_00"),
    ("ia_rhythmprod",   "0594_Rhythm_of_Production_Automatic_Mass_Production_with_Progress_Th_11_34_56_00"),
    ("ia_dynamiccity",  "0229_Dynamic_American_City_The_23_00_35_24-0035"),
    ("ia_highlights65", "highlights_1965_1"),
    # ("ia_turmoil67",  "201376_America_in_Turmoil"),  ENTFERNT:
    #   "America in Turmoil" (1967) ist ein Propagandafilm der Liberty Lobby
    #   (rechtsextrem, antisemitisch, segregationistisch -- Eigenwerbung im
    #   Vorspann: "You are about to see an Extremist Motion Picture").
    #   In einem Video gegen Spaltung ist dieses Material nicht verwendbar.
]

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def curl(url, out, tries=4):
    for t in range(tries):
        r = subprocess.run(["curl", "-sSL", "--max-time", "900", "--retry", "2",
                            "-o", out, url])
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 200_000:
            return True
        time.sleep(2 ** t)
    return False

def fetch_nasa(key, nasa_id):
    out = os.path.join(DST, key + ".mp4")
    if os.path.exists(out) and os.path.getsize(out) > 200_000:
        print(f"  [skip] {key}"); return {"key": key, "file": out, "source": "NASA", "id": nasa_id}
    api = "https://images-api.nasa.gov/asset/" + urllib.parse.quote(nasa_id)
    r = run(["curl", "-sS", "--max-time", "90", api])
    try:
        hrefs = [i["href"] for i in json.loads(r.stdout)["collection"]["items"]]
    except Exception as e:
        print(f"  [FAIL api] {key}: {e}"); return None
    # kleinste brauchbare Variante bevorzugen: medium > small > large > orig
    pick = None
    for suf in ["~medium.mp4", "~small.mp4", "~large.mp4", "~orig.mp4"]:
        for h in hrefs:
            if h.endswith(suf): pick = h; break
        if pick: break
    if not pick:
        print(f"  [FAIL nofile] {key}"); return None
    pick = pick.replace("http://", "https://")
    pick = urllib.parse.quote(pick, safe=":/~?=&")
    ok = curl(pick, out)
    print(f"  [{'ok' if ok else 'FAIL'}] {key}  {os.path.getsize(out)//1048576 if ok else 0}MB")
    return {"key": key, "file": out, "source": "NASA (public domain)",
            "id": nasa_id, "url": pick} if ok else None

def fetch_ia(key, ident):
    out = os.path.join(DST, key + ".mp4")
    if os.path.exists(out) and os.path.getsize(out) > 200_000:
        print(f"  [skip] {key}"); return {"key": key, "file": out, "source": "Internet Archive", "id": ident}
    r = run(["curl", "-sS", "--max-time", "90", f"https://archive.org/metadata/{ident}"])
    try:
        meta = json.loads(r.stdout); files = meta["files"]
    except Exception as e:
        print(f"  [FAIL meta] {key}: {e}"); return None
    SIZE_CAP = 400 * 1048576          # nichts ueber 400MB ziehen
    cands = [f for f in files
             if f["name"].lower().endswith((".mp4", ".m4v", ".ogv", ".mpeg"))
             and int(f.get("size", 1 << 40)) < SIZE_CAP
             and int(f.get("size", 0)) > 3_000_000]
    if not cands:
        print(f"  [FAIL nofile] {key}"); return None
    def rank(f):
        px = int(f.get("width", 0) or 0) * int(f.get("height", 0) or 0)
        h264 = 1 if (f.get("format", "").lower() == "h.264") else 0
        return (px, h264, -int(f.get("size", 0)))
    # hoechste Aufloesung, bei Gleichstand h.264 und kleinere Datei
    pick = max(cands, key=rank)
    url = f"https://archive.org/download/{ident}/" + urllib.parse.quote(pick["name"])
    ok = curl(url, out)
    lic = meta.get("metadata", {}).get("licenseurl", "public domain / Prelinger")
    print(f"  [{'ok' if ok else 'FAIL'}] {key}  {os.path.getsize(out)//1048576 if ok else 0}MB  ({pick['name'][:40]})")
    return {"key": key, "file": out, "source": "Internet Archive / Prelinger",
            "id": ident, "url": url, "license": lic} if ok else None

def main():
    creds = []
    print("NASA:")
    for k, i in NASA:
        c = fetch_nasa(k, i)
        if c: creds.append(c)
    print("Internet Archive / Prelinger:")
    for k, i in IA:
        c = fetch_ia(k, i)
        if c: creds.append(c)
    json.dump(creds, open(os.path.join(DST, "CREDITS.json"), "w"), indent=1)
    print(f"\n{len(creds)} Quellen geladen -> {DST}")

if __name__ == "__main__":
    main()
