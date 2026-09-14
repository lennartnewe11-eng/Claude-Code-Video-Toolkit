#!/usr/bin/env python3
"""Zweite Quellenrunde: Wikimedia Commons (Mauerfall, Reagan, Bush 2001),
Internet Archive (Handy-Werbespots) und der vom Nutzer gelieferte
Keynote-Mitschnitt.

Lizenzen werden mitgeschrieben -- sie sind hier NICHT einheitlich:
Public Domain (US-Regierungswerk), CC BY / CC BY-SA (Namensnennung noetig)
und Werbespots ohne Lizenzangabe.
"""
import json, os, re, subprocess, time, urllib.parse

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST  = os.path.join(PROJ, "assets", "source")
UA   = "ch-shortform-research/1.0 (Claude Code; test project)"
os.makedirs(DST, exist_ok=True)

# key, Commons-Dateiname, (ss, dauer) oder None fuer ganze Datei
WIKIMEDIA = [
    ("wm_mauerfall_potsdam", "Grenzöffnung am Potsdamer Platz.webm", None),
    ("wm_mauerfall_grenze",  "Grenzöffnung November 1989 - Selmsdorf (DDR) - Lübeck-Schlutup.webm", None),
    ("wm_reagan_wall",       "President Ronald Reagan's Speech at the Berlin Wall, June 12, 1987.webm", (1180, 180)),
    ("wm_bush_2001",         "September 2001 George W. Bush speech to a joint session of Congress.webm", (300, 420)),
]

IA_EXTRA = [
    ("ia_gte_cell89",  "CLE-B27_68299-69279"),               # GTE MobileNet Cellular 1989
    ("ia_nokia95",     "NokiaMobileCommunicationsAdvert"),    # Nokia 1995
    ("ia_nokia8110",   "1996-commercial-for-nokia-8110"),     # Nokia 8110, 1996
]

USER_CLIPS = [
    ("user_keynote_iphone",
     "/root/.claude/uploads/fbc32e5c-a9f9-58cd-90f3-b3c31c377e20/"
     "1ccbd89e-ScreenRecording_09-14-2026_18-52-12_1.mov"),
]

def commons_info(name):
    args = ["curl","-sS","--max-time","90","-A",UA,"-G",
            "https://commons.wikimedia.org/w/api.php",
            "--data-urlencode","action=query",
            "--data-urlencode",f"titles=File:{name}",
            "--data-urlencode","prop=imageinfo",
            "--data-urlencode","iiprop=url|size|extmetadata",
            "--data-urlencode","format=json"]
    for t in range(3):
        out = subprocess.run(args,capture_output=True,text=True).stdout
        if out.strip().startswith("{"):
            for p in json.loads(out)["query"]["pages"].values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii:
                    em = ii.get("extmetadata", {})
                    return {"url": ii["url"].split("?")[0],
                            "lic": em.get("LicenseShortName",{}).get("value","?"),
                            "artist": re.sub("<[^>]*>","",em.get("Artist",{}).get("value","?")),
                            "w": ii.get("width"), "h": ii.get("height")}
        time.sleep(2**t)
    return None

def grab(url, out, window=None):
    """ffmpeg kommt ueber den CONNECT-Proxy nicht an https:// heran
    (kein Proxy-Support fuer TLS). Also mit curl laden und lokal schneiden."""
    tmp = out + ".src"
    ok = False
    for t in range(4):
        r = subprocess.run(["curl","-sSL","--max-time","1800","--retry","2",
                            "-A",UA,"-o",tmp,url])
        if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 100_000:
            ok = True; break
        time.sleep(2**t)
    if not ok:
        return False
    cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y"]
    if window:
        ss, d = window
        cmd += ["-ss",str(ss),"-i",tmp,"-t",str(d)]
    else:
        cmd += ["-i",tmp]
    cmd += ["-c:v","libx264","-crf","16","-preset","veryfast","-an",out]
    rc = subprocess.run(cmd).returncode
    os.remove(tmp)
    return rc == 0 and os.path.exists(out) and os.path.getsize(out) > 100_000

def ia_grab(key, ident):
    out = os.path.join(DST, key + ".mp4")
    if os.path.exists(out) and os.path.getsize(out) > 200_000:
        print(f"  [skip] {key}"); return None
    meta = json.loads(subprocess.run(["curl","-sS","--max-time","90",
        f"https://archive.org/metadata/{ident}"],capture_output=True,text=True).stdout)
    cands = [f for f in meta["files"]
             if f["name"].lower().endswith((".mp4",".m4v",".ogv"))
             and 1_000_000 < int(f.get("size", 1<<40)) < 400*1048576]
    pick = max(cands, key=lambda f: int(f.get("width",0) or 0)*int(f.get("height",0) or 0))
    url = f"https://archive.org/download/{ident}/" + urllib.parse.quote(pick["name"])
    ok = subprocess.run(["curl","-sSL","--max-time","900","-o",out,url]).returncode == 0
    print(f"  [{'ok' if ok else 'FAIL'}] {key}  {pick.get('width')}x{pick.get('height')}")
    return {"key":key,"file":out,"source":"Internet Archive","id":ident,
            "license":meta.get("metadata",{}).get("licenseurl","keine Lizenzangabe - Werbespot, Rechte beim Markeninhaber"),
            "note":meta.get("metadata",{}).get("title","")} if ok else None

def main():
    creds = []
    cp = os.path.join(DST,"CREDITS.json")
    if os.path.exists(cp): creds = json.load(open(cp))
    have = {c["key"] for c in creds}

    print("Wikimedia Commons:")
    for key, name, win in WIKIMEDIA:
        out = os.path.join(DST, key + ".mp4")
        if os.path.exists(out) and os.path.getsize(out) > 200_000:
            print(f"  [skip] {key}"); continue
        info = commons_info(name)
        if not info: print(f"  [FAIL api] {key}"); continue
        ok = grab(info["url"], out, win)
        print(f"  [{'ok' if ok else 'FAIL'}] {key}  {info['w']}x{info['h']}  {info['lic']}")
        if ok and key not in have:
            creds.append({"key":key,"file":out,"source":"Wikimedia Commons",
                          "id":name,"url":info["url"],"license":info["lic"],
                          "attribution":info["artist"]})
    print("Internet Archive (Werbespots):")
    for key, ident in IA_EXTRA:
        c = ia_grab(key, ident)
        if c and key not in have: creds.append(c)

    print("Vom Nutzer geliefert:")
    for key, src in USER_CLIPS:
        out = os.path.join(DST, key + ".mp4")
        if not os.path.exists(out):
            # Rotationsmetadaten aufloesen -> liegt danach als 1920x886 vor
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",src,
                            "-c:v","libx264","-crf","16","-preset","veryfast","-an",out],check=True)
        print(f"  [ok] {key}")
        if key not in have:
            creds.append({"key":key,"file":out,"source":"vom Nutzer geliefert",
                          "id":os.path.basename(src),
                          "license":"Apple Keynote 2007 - Rechte bei Apple",
                          "attribution":"Apple Inc."})
    json.dump(creds, open(cp,"w"), indent=1, ensure_ascii=False)
    print(f"\n{len(creds)} Quellen insgesamt")

if __name__ == "__main__":
    main()
