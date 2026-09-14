#!/usr/bin/env python3
"""Laedt Produktfotos von Wikimedia Commons fuer den Groessenvergleich."""
import json, os, subprocess, time, sys

UA  = "ch-shortform-research/1.0 (Claude Code; test project)"
PROJ= os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(PROJ, "assets", "phones_raw")

def api(params, tries=3):
    args=["curl","-sS","--max-time","90","-A",UA,"-G","https://commons.wikimedia.org/w/api.php"]
    for k,v in params.items(): args += ["--data-urlencode", f"{k}={v}"]
    for t in range(tries):
        out=subprocess.run(args,capture_output=True,text=True).stdout
        if out.strip().startswith("{"): return json.loads(out)
        time.sleep(2**t)
    return {}

def info(names):
    r=api({"action":"query","titles":"|".join("File:"+n for n in names),
           "prop":"imageinfo","iiprop":"url|size|extmetadata","format":"json"})
    out={}
    for p in r.get("query",{}).get("pages",{}).values():
        ii=(p.get("imageinfo") or [{}])[0]
        if not ii: continue
        em=ii.get("extmetadata",{})
        out[p["title"][5:]]={"url":ii["url"].split("?")[0],
            "w":ii.get("width"),"h":ii.get("height"),
            "lic":em.get("LicenseShortName",{}).get("value","?")}
    return out

def fetch(name, key, width=1600):
    """Special:FilePath kuemmert sich um Kodierung und Weiterleitung --
    selbst gebaute thumb/-URLs scheitern an Leerzeichen, Kommas und Klammern."""
    import urllib.parse
    os.makedirs(RAW, exist_ok=True)
    i=info([name]).get(name)
    if not i: print(f"  [FAIL] {key}: {name}"); return None
    u=i["url"]
    enc=urllib.parse.quote(name.replace(" ","_"))
    thumb=f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"
    ext=".png" if u.lower().endswith(".png") else ".jpg"
    dst=os.path.join(RAW, key+ext)
    for url in (thumb, u):
        if subprocess.run(["curl","-sSL","--max-time","300","-A",UA,"-o",dst,url]).returncode==0 \
           and os.path.exists(dst) and os.path.getsize(dst)>20_000:
            print(f"  [ok] {key:12s} {i['w']}x{i['h']} {i['lic'][:18]:18s} {name[:44]}")
            return {"key":key,"file":dst,"name":name,"license":i["lic"],"url":u}
    print(f"  [FAIL dl] {key}"); return None

if __name__ == "__main__":
    want = json.load(open(sys.argv[1]))
    got=[c for k,n in want.items() if (c:=fetch(n,k))]
    json.dump(got, open(os.path.join(RAW,"sources.json"),"w"), indent=1, ensure_ascii=False)
    print(f"\n{len(got)}/{len(want)} geladen -> {RAW}")
