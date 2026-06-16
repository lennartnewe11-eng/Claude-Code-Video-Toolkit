#!/usr/bin/env bash
# Extracts mono 16kHz audio (for STT) from the source video.
# Usage: bash scripts/extract_audio.sh /path/to/source.mov
set -euo pipefail
SRC="${1:?provide path to source .mov/.mp4}"
OUT_DIR="$(cd "$(dirname "$0")/.." && pwd)/assets"
mkdir -p "$OUT_DIR"
ffmpeg -y -i "$SRC" -ac 1 -ar 16000 "$OUT_DIR/voiceover.wav" -loglevel error
echo "Wrote $OUT_DIR/voiceover.wav"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$SRC"
