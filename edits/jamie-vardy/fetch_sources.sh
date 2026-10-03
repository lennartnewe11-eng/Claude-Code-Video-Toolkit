#!/usr/bin/env bash
# Downloads the two source compilations used by render.py into ./media/src.
# YouTube blocks datacenter IPs ("confirm you're not a bot"), so the edit uses
# public Bilibili re-uploads (1080p). Bilibili rate-limits: keep it sequential.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p media/src media/audio

dl() {  # dl <bilibili av id> <name>
  yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" \
    -o "media/src/$2.%(ext)s" "https://www.bilibili.com/video/av$1"
  sleep 5
}

dl 259118829 top10    # "瓦尔迪经典十佳球" – top-10 goals incl. Liverpool volley + Sheffield Utd corner flag (burned-in CN subs, cropped out)
dl 287243861 celebs   # LCFC "Jamie Vardy's Iconic Celebrations" – clean, incl. 11-in-a-row record vs Man Utd

echo "Now put the song at media/audio/song.wav, e.g.:"
echo "  ffmpeg -i <your-song>.mp3 -ar 44100 -ac 2 media/audio/song.wav"
