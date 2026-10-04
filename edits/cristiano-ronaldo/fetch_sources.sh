#!/usr/bin/env bash
# Downloads the source clips + caption font used by render.py into ./media.
# YouTube blocks datacenter IPs ("confirm you're not a bot"), so the edit uses
# public Bilibili uploads. Bilibili rate-limits: keep it sequential.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p media/src media/audio media/fonts

dl() {  # dl <bilibili av id> <name>
  yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" \
    -o "media/src/$2.%(ext)s" "https://www.bilibili.com/video/av$1"
  sleep 5
}

dl 770307957       bicycle   # UCL 2018 Juventus–Real: bicycle kick, every angle, Zidane, hand on heart, smile
dl 115529301955222 iconic    # iconic moments (beard celebration vs Spain 2018)
dl 605731774       young     # young Ronaldo – WM 2006 close-up + scream vs France
dl 427255894       mom       # Portugal–Switzerland 2022: Dolores in tears in the stands
dl 816317048       calma     # Camp Nou 2012 "calma" celebration
dl 313224796       siu       # SIU compilation (run/jump Juve, landing Real, Ballon d'Or, trophy kiss)
dl 928377952       mom2013   # Ballon d'Or 2013 speech (tears)
dl 115109133289538 portugal  # Portugal national team close-ups

# Caption font: Montserrat Black Italic (SIL OFL), latin subset from Google Fonts
python3 - <<'PY'
import re, urllib.request
from fontTools.ttLib import TTFont
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
css = urllib.request.urlopen(urllib.request.Request(
    "https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@1,900&display=swap", headers=ua)).read().decode()
latin = css[css.index("/* latin */"):]
url = re.search(r"url\((https://fonts\.gstatic\.com[^)]+)\)", latin).group(1)
open("media/fonts/mb.woff2", "wb").write(urllib.request.urlopen(url).read())
f = TTFont("media/fonts/mb.woff2"); f.flavor = None; f.save("media/fonts/Montserrat-BlackItalic.ttf")
PY

echo "Now put the song at media/audio/song.wav, e.g.:"
echo "  ffmpeg -i <your-song>.mp3 -ar 44100 -ac 2 media/audio/song.wav"
