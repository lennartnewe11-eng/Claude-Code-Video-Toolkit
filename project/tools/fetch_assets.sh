#!/usr/bin/env bash
# Re-download all hook media into project/remotion/public (footage + audio).
# Media is gitignored, so run this after a fresh checkout to rebuild the hook.
# Requires: project/tools/secrets.env with FREESOUND_API_KEY (for SFX).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
FFMPEG="project/tools/ffmpeg"
FOOT="project/remotion/public/footage"
AUD="project/remotion/public/audio"
SRC="$(mktemp -d)"
mkdir -p "$FOOT" "$AUD"

commons(){ python3 project/tools/commons_fetch.py get "$1" "$2"; }

echo "==> Footage: photos (final)"
commons "File:Grand Junction Amtrak station platforms and sign.jpg" "$FOOT/usa-break.jpg"
commons "File:Lower Manhattan, New York skyline from Liberty Island 2021.jpg" "$FOOT/richest.jpg"
commons "File:Lower Manhattan from Jersey City November 2014 panorama 2.jpg" "$FOOT/economy.jpg"
commons "File:East and West Shaking hands at the laying of last rail Union Pacific Railroad - Restoration.jpg" "$FOOT/best-network.jpg"
commons "File:Abandoned railway - geograph.org.uk - 3920844.jpg" "$FOOT/squandered.jpg"

echo "==> Footage: video clips (download + trim to 1080p mp4)"
commons "File:Shinkansen N700 Series Bullet Train Tokyo Station by Don Ramey Logan.webm" "$SRC/shinkansen.webm"
commons "File:CRH entering Yuyao Station 201907141725.webm" "$SRC/china.webm"
commons "File:France TGV high speed trains.webm" "$SRC/tgv.webm"
VF="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1"
enc(){ "$FFMPEG" -v error -ss "$2" -t "$3" -i "$SRC/$1" -vf "$VF" -an -r 30 \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p "$FOOT/$4" -y; }
enc shinkansen.webm 5   5 japan.mp4
enc china.webm      20  5 china.mp4
enc tgv.webm        116 5 tgv.mp4

echo "==> Audio: music bed (Incompetech, CC-BY)"
curl -sSL -m 90 -A "usa-train-video/1.0" -o "$AUD/musicBed.mp3" \
  "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Crypto.mp3"

echo "==> Audio: SFX (Freesound, CC0)"
# shellcheck disable=SC1091
source project/tools/secrets.env
python3 project/tools/freesound_fetch.py get 812689 "$AUD/whoosh.mp3"
python3 project/tools/freesound_fetch.py get 749465 "$AUD/impact.mp3"
python3 project/tools/freesound_fetch.py get 334525 "$AUD/riser.mp3"

echo "==> Voiceover"
if [ -f project/footage/0615_2.mov ]; then
  "$FFMPEG" -v error -i project/footage/0615_2.mov -vn -c:a aac -b:a 192k "$AUD/vo.m4a" -y
  echo "    vo.m4a extracted"
else
  echo "    NOTE: project/footage/0615_2.mov missing (user upload) — vo.m4a not regenerated"
fi

rm -rf "$SRC"
echo "==> Done. Render with: cd project/remotion && npx remotion render Hook out/hook-full.mp4"
