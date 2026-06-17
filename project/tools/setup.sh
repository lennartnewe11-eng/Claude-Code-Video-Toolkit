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

echo "==> Installing yt-dlp (for footage download)"
python3 -m pip install --quiet --upgrade yt-dlp >/dev/null 2>&1 || pip install --quiet --upgrade yt-dlp
python3 -m yt_dlp --version 2>/dev/null || yt-dlp --version || true

# The remote environment routes HTTPS through a TLS-inspecting proxy whose CA
# lives in the system bundle (/etc/ssl/certs/ca-certificates.crt). curl and
# Python's urllib honour SSL_CERT_FILE and trust it, but yt-dlp uses its own
# bundled certifi and otherwise fails with CERTIFICATE_VERIFY_FAILED. Append the
# system bundle (incl. proxy CA) to certifi so yt-dlp trusts the proxy too.
echo "==> Patching certifi with the proxy CA (for yt-dlp over the TLS proxy)"
SYS_CA="/etc/ssl/certs/ca-certificates.crt"
CERTIFI="$(python3 -c 'import certifi; print(certifi.where())' 2>/dev/null || true)"
if [ -n "$CERTIFI" ] && [ -f "$CERTIFI" ] && [ -f "$SYS_CA" ]; then
  if ! grep -q "PROXY-CA-APPENDED" "$CERTIFI"; then
    { echo ""; echo "# PROXY-CA-APPENDED (system bundle incl. TLS-inspection CA)"; cat "$SYS_CA"; } >> "$CERTIFI"
    echo "    appended system CA bundle to $CERTIFI"
  else
    echo "    certifi already patched"
  fi
fi

echo "==> Done. Tools in: $HERE"
