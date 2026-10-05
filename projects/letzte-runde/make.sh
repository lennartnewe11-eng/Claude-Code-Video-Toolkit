#!/usr/bin/env bash
# Full build: assets → sound mix → picture → mux → cover + preview sheet.
set -euo pipefail
cd "$(dirname "$0")"

[ -d assets/video ] && [ -n "$(ls -A assets/video 2>/dev/null)" ] || ./fetch_assets.sh

python3 audio.py
python3 render.py --out output/picture.mp4

ffmpeg -v error -y -i output/picture.mp4 -i output/mix.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -movflags +faststart -shortest \
  output/letzte-runde_tiktok.mp4

# cover frame for the TikTok "select cover" step and a review contact sheet
ffmpeg -v error -y -ss 12.5 -i output/letzte-runde_tiktok.mp4 -frames:v 1 -q:v 2 output/cover.jpg
ffmpeg -v error -y -i output/letzte-runde_tiktok.mp4 \
  -vf "fps=2,scale=216:384,tile=8x4" -frames:v 1 -q:v 3 output/contact_sheet.jpg

rm -f output/picture.mp4 output/mix.wav
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 output/letzte-runde_tiktok.mp4
