import sys, json, urllib.request, urllib.parse, http.cookiejar, re, html
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
op.addheaders = [("User-Agent", UA), ("Referer", "https://www.bilibili.com/")]
op.open("https://www.bilibili.com/").read()
for kw in sys.argv[1:]:
    for page in (1, 2):
        url = "https://api.bilibili.com/x/web-interface/search/type?" + urllib.parse.urlencode({"search_type": "video", "keyword": kw, "page": page})
        d = json.loads(op.open(url).read())
        res = (d.get("data") or {}).get("result") or []
        print(f"=== {kw} p{page} code={d.get('code')} n={len(res)}")
        for r in res:
            t = html.unescape(re.sub("<[^>]+>", "", r["title"]))
            print(f"{r['bvid']} | {r['duration']:>6} | {r['play']:>8} | {t[:80]}")
