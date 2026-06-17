#!/usr/bin/env bash
# Installs the media toolchain for the USA-train video project.
# Safe to re-run. Requires network access to github.com + pypi.org.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing static ffmpeg/ffprobe from GitHub release"
if [ ! -x "$HERE/ffmpeg" ]; then
  TMP="$(mktemp -d)"
  curl -sSL -o "$TMP/ffmpeg.tar.xz" \
    "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
  tar -xf "$TMP/ffmpeg.tar.xz" -C "$TMP"
  BIN="$(find "$TMP" -type d -name bin -path '*ffmpeg*' | head -1)"
  cp "$BIN/ffmpeg" "$BIN/ffprobe" "$HERE/"
  rm -rf "$TMP"
fi
"$HERE/ffmpeg" -version | head -1

echo "==> Installing yt-dlp (for footage download once network policy allows it)"
python3 -m pip install --quiet --upgrade yt-dlp >/dev/null 2>&1 || pip install --quiet --upgrade yt-dlp
python3 -m yt_dlp --version 2>/dev/null || yt-dlp --version || true

echo "==> Done. Tools in: $HERE"
