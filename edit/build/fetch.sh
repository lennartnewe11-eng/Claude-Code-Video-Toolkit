#!/bin/bash
# Lädt alle Quellen aus build/sources.txt nach media/src/<key>.mp4 (max. 1080p, nur Bild).
# Gedacht für einen normalen Rechner mit yt-dlp und ffmpeg; nacheinander, mit Pause,
# damit YouTube nicht drosselt.
set -u
cd "$(dirname "$0")/.."
mkdir -p media/src
grep -v '^#' build/sources.txt | while read -r key id _; do
  [ -z "$key" ] && continue
  [ -s "media/src/$key.mp4" ] && { echo "vorhanden  $key"; continue; }
  if yt-dlp --no-warnings -q -f "bv*[height<=1080][ext=mp4]/bv*[height<=1080]" \
       --remux-video mp4 -o "media/src/$key.%(ext)s" "https://www.youtube.com/watch?v=$id"; then
    echo "ok         $key"
  else
    echo "FEHLER     $key ($id)"
  fi
  sleep 3
done
