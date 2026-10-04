#!/usr/bin/env bash
# Downloads the sources used by render.py into ./media/src (public Bilibili uploads, 1080p;
# YouTube blocks datacenter IPs). Bilibili rate-limits: keep it sequential.
# The music comes from the reference video: media/audio/ref_audio.wav (see README).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p media/src media/audio

dl() {  # dl <bilibili av id> <name>
  yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" \
    -o "media/src/$2.%(ext)s" "https://www.bilibili.com/video/av$1"
  sleep 5
}

dl 948811450       rare        # "Neymar JR ● RARE CLIPS ● SCENEPACK" – UCL warm-up juggling
dl 41712216        skills1819  # Neymar 18/19 skills – feet/ball close-ups, face close-up
dl 117256533187967 scene8k     # scenepack – vs Real Madrid 2018, vs Bayern, profile at the Bernabéu
dl 744797460       faces       # face compilation – hands on face, "NEYMAR JR 10"
dl 207001101       uclpsg      # UEFA "Neymar at PSG in the UCL" – free kick vs Red Star 2018, celebration

echo "Now extract the reference audio, e.g.:"
echo "  ffmpeg -i <reference>.mp4 -vn -ar 44100 -ac 2 media/audio/ref_audio.wav"
