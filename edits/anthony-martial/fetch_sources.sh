#!/usr/bin/env bash
# Downloads the source used by render.py into ./media/src plus the caption font.
# YouTube blocks datacenter IPs ("confirm you're not a bot"), so the edit uses
# a public Bilibili upload of the Premier League's Martial goals compilation (1080p30).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p media/src media/audio media/fonts

yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" \
  -o "media/src/plcomp.%(ext)s" "https://www.bilibili.com/video/av1305175072"

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
