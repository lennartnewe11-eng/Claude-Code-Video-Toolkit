#!/usr/bin/env bash
# Full build: assets → prep (footage/photos/audio cuts) → sound mix → HyperFrames render
# → finishing pass + mux → cover & contact sheet.
set -euo pipefail
cd "$(dirname "$0")"

[ -s assets/nasa/hq194.mp4 ] || ./fetch_assets.sh

# HyperFrames CLI (npm) + a headless Chromium; override HF / CHROME if yours live elsewhere
HF=${HF:-"npx --yes hyperframes@0.8.134"}
CHROME=${CHROME:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}
[ -x "$CHROME" ] && export PRODUCER_HEADLESS_SHELL_PATH="$CHROME" HYPERFRAMES_BROWSER_PATH="$CHROME"
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1

python3 prep.py
python3 audio.py
mkdir -p build output
(cd hf && $HF lint && $HF render --fps 30 --quality high --crf 12 -o ../build/picture_hf.mp4)
python3 post.py build/picture_hf.mp4 build/mix.wav output/eagle-has-landed_tiktok.mp4

ffmpeg -v error -y -ss 17.6 -i output/eagle-has-landed_tiktok.mp4 -frames:v 1 -q:v 2 output/cover.jpg
ffmpeg -v error -y -i output/eagle-has-landed_tiktok.mp4 \
  -vf "fps=2,scale=216:384,tile=7x6" -frames:v 1 -q:v 3 output/contact_sheet.jpg
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 output/eagle-has-landed_tiktok.mp4
