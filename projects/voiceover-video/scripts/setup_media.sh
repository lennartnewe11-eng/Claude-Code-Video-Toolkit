#!/usr/bin/env bash
# Resume kit: rebuilds the media tooling after a fresh container.
# Run once after the environment restarts (e.g. after enabling huggingface.co egress).
set -euo pipefail

echo "==> Installing ffmpeg"
sudo apt-get update -qq || true
sudo apt-get install -y -qq ffmpeg

echo "==> Installing faster-whisper"
pip3 install -q faster-whisper

echo "==> Done. Next: place the source .mov, then run:"
echo "    bash scripts/extract_audio.sh /path/to/source.mov"
echo "    python3 scripts/transcribe.py"
