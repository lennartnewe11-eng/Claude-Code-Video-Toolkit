#!/usr/bin/env bash
# Downloads every asset the edit uses. All files are from Mixkit (free license,
# no attribution required: https://mixkit.co/license/) and Google Fonts (OFL).
# Raw assets are not committed – only the finished edit is.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets/video assets/music assets/sfx assets/fonts

# footage: try 4K first, fall back to 1080p
VIDEOS="4596 40255 40265 40266 40948 40955 40958 40961 40963 40964 40966 40969 40970 40971 40973 40974"
for id in $VIDEOS; do
  [ -s "assets/video/$id.mp4" ] && continue
  for q in 2160 1080; do
    if curl -fsSL -o "assets/video/$id.mp4" "https://assets.mixkit.co/videos/$id/$id-$q.mp4"; then
      echo "video $id ($q)"; break
    fi
  done
done

# music: "Sparta" (Mixkit #370)
[ -s assets/music/370.mp3 ] || curl -fsSL -o assets/music/370.mp3 "https://assets.mixkit.co/music/370/370.mp3"

# sound effects
SFX="2299 1492 2050 2155 2165 2164 2056 1088 498 2103 2051 2053 2143 1143 490 2054 788 462 1490 458"
for id in $SFX; do
  [ -s "assets/sfx/$id.mp3" ] || curl -fsSL -o "assets/sfx/$id.mp3" \
    "https://assets.mixkit.co/active_storage/sfx/$id/$id-preview.mp3"
done

# fonts (SIL Open Font License)
GF=https://raw.githubusercontent.com/google/fonts/main/ofl
[ -s assets/fonts/Anton-Regular.ttf ] || curl -fsSL -o assets/fonts/Anton-Regular.ttf "$GF/anton/Anton-Regular.ttf"
for w in Black ExtraBold SemiBold; do
  f="BarlowCondensed-$w.ttf"
  [ -s "assets/fonts/$f" ] || curl -fsSL -o "assets/fonts/$f" "$GF/barlowcondensed/$f"
done
echo "assets ready"
