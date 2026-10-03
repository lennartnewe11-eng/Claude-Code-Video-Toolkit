#!/usr/bin/env bash
# Downloads the source clips used by render.py into ./media/src.
# YouTube blocks datacenter IPs ("confirm you're not a bot"), so the edit uses
# public Bilibili uploads. Bilibili rate-limits: keep it sequential.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p media/src media/audio

dl() {  # dl <bilibili av id> <name>
  yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" \
    -o "media/src/$2.%(ext)s" "https://www.bilibili.com/video/av$1"
  sleep 5
}

dl 114080891277195 peak        # "博格巴巅峰时期有多强" – Juve/Man Utd goals + celebrations (4:3 1080p)
dl 596714974       wcfinal     # World Cup final 2018 highlights (CCTV5, 720p)
dl 889997809       udinese     # Juve vs Udinese 2013 volley + "the stare"
dl 98805857        dance_show  # "博格巴舞蹈秀" – dances, smoke tunnel with the World Cup trophy (720p, letterboxed)
dl 612599656       euro2020    # France vs Switzerland EURO 2020 (only the close-up + celebration are used)

echo "Now put the song at media/audio/song.wav, e.g.:"
echo "  ffmpeg -i <your-song>.mp3 -ar 44100 -ac 2 media/audio/song.wav"
