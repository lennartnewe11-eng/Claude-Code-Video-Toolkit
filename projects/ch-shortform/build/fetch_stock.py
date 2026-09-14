#!/usr/bin/env python3
"""Sucht und laedt Clips von mixkit und coverr (freie Stock-Portale mit
direkten Dateilinks). Pexels liefert in dieser Sitzung nur 401, YouTube
blockt den Download mit einer Bot-Pruefung -- diese beiden gehen."""
import os, re, subprocess, sys, json, time

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST  = os.path.join(PROJ, "assets", "stock")
UA   = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/141 Safari/537.36"

def page(url):
    r = subprocess.run(["curl","-sSL","--max-time","90","-A",UA,url],
                       capture_output=True, text=True)
    return r.stdout

def mixkit(query, limit=8):
    html = page(f"https://mixkit.co/free-stock-video/{query}/")
    urls = re.findall(r'https://assets\.mixkit\.co/[^"?\s]*?-720\.mp4', html)
    seen, out = set(), []
    for u in urls:
        k = u.rsplit("/",1)[1]
        if k in seen: continue
        seen.add(k); out.append(u)
        if len(out) >= limit: break
    return out

def coverr(query, limit=8):
    html = page(f"https://coverr.co/s?q={query}")
    urls = re.findall(r'https://cdn[^"\s]*coverr\.co/videos/[^"\s]*?/1080p\.mp4', html)
    seen, out = set(), []
    for u in urls:
        if "ai-generation" in u: continue          # KI-Clips ueberspringen
        k = u.split("/videos/")[1].split("/")[0]
        if k in seen: continue
        seen.add(k); out.append(u)
        if len(out) >= limit: break
    return out

def grab(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 80_000: return True
    r = subprocess.run(["curl","-sSL","--max-time","300","-A",UA,"-o",dst,url])
    return r.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 80_000

def main(spec_path):
    os.makedirs(DST, exist_ok=True)
    spec = json.load(open(spec_path))
    got = []
    for group, queries in spec.items():
        n = 0
        for q in queries:
            for src, fn in (("mx", mixkit), ("cv", coverr)):
                try: urls = fn(q)
                except Exception as e: print(f"  [err] {src}:{q} {e}"); continue
                for u in urls:
                    key = f"{group}_{src}{n:02d}"
                    dst = os.path.join(DST, key + ".mp4")
                    if grab(u, dst):
                        got.append({"key":key,"file":dst,"query":q,"source":src,"url":u})
                        n += 1
                    if n >= 10: break
                if n >= 10: break
                time.sleep(0.4)
            if n >= 10: break
        print(f"  {group:14s} {n} Clips")
    json.dump(got, open(os.path.join(DST,"stock.json"),"w"), indent=1)
    print(f"\n{len(got)} Clips -> {DST}")

if __name__ == "__main__":
    main(sys.argv[1])
