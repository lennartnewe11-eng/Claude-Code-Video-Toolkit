#!/usr/bin/env bash
# Downloads every source used by bolt.py / quiz.py / rank.py into ./media (public Bilibili uploads,
# 1080p – YouTube blocks datacenter IPs) plus the caption font. Sequential: Bilibili rate-limits.
set -euo pipefail
cd "$(dirname "$0")"
dl() {  # dl <dir> <bilibili av id> <name>
  mkdir -p "media/$1/src"
  [ -f "media/$1/src/$3.mp4" ] && return
  yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" -o "media/$1/src/$3.%(ext)s" \
    "https://www.bilibili.com/video/av$2"
  sleep 5
}
link() { mkdir -p "media/$1/src"; ln -sfn "../../$2/src/$3.mp4" "media/$1/src/$4.mp4"; }

# Clip 1 – Bolt 9.58 (Berlin 2009)
dl bolt 946565323       timer      # continuous real-time camera of the final (source has its own timer box, cropped out)
dl bolt 114985921481787 race164    # "9.58 Berlin 2009" feature – stadium clock 9.58, arms-up celebration
# Shared football sources
dl _fb  770307957       bicycle    # Ronaldo bicycle kick vs Juventus 2018, every angle
dl _fb  313224796       siu        # SIU compilation
dl _fb  479222393       wcgoals    # Mbappé World Cup goals (arms-crossed celebration)
dl _fb  114080891277195 peak       # Pogba compilation (Man Utd celebration)
dl _fb  600305254       westham    # Chelsea–West Ham 2019 broadcast (Hazard celebration)
dl _fb  216851398       hztop10    # Hazard Chelsea top-10 (West Ham solo)
dl _fb  259118829       vdtop10    # Vardy top-10 (corner flag, Sheffield Utd)
dl _fb  115112455178309 pure       # Yamal compilation (EURO 2024 goal vs France)
dl _fb  1456185188      eurofra    # EURO 2024 Spain–France (celebration)
# Clip 2 – quiz
link quiz _fb siu siu; link quiz _fb wcgoals mbappe; link quiz _fb peak pogba
link quiz _fb westham hazard; link quiz _fb vdtop10 vardy
# Clip 3 – ranking
link rank _fb pure yamal_pure; link rank _fb eurofra yamal_wide; link rank _fb hztop10 hazard
link rank _fb westham hazard_wh; link rank _fb bicycle cr7

# Caption font: Montserrat Black Italic (SIL OFL), latin subset
python3 - <<'PY'
import re, urllib.request
from fontTools.ttLib import TTFont
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
css = urllib.request.urlopen(urllib.request.Request(
    "https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@1,900&display=swap", headers=ua)).read().decode()
url = re.search(r"url\((https://fonts\.gstatic\.com[^)]+)\)", css[css.index("/* latin */"):]).group(1)
open("media/mb.woff2", "wb").write(urllib.request.urlopen(url).read())
f = TTFont("media/mb.woff2"); f.flavor = None; f.save("media/Montserrat-BlackItalic.ttf")
PY
