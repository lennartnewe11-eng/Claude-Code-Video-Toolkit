#!/usr/bin/env bash
# Downloads every source the edit uses. Raw assets are not committed.
#   NASA (public domain, https://www.nasa.gov/nasa-brand-center/images-and-media/):
#     HQ-194 "Eagle Has Landed: The Flight of Apollo 11" (1969), Apollo 11 25th-anniversary B-roll,
#     air-to-ground audio releases, Hasselblad photographs.
#   Mixkit (free license, https://mixkit.co/license/): music #464, #587 and sound effects.
#   Google Fonts (SIL OFL): Barlow Condensed, JetBrains Mono.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets/nasa assets/music assets/sfx assets/fonts
IMG=https://images-assets.nasa.gov

get() { [ -s "$2" ] || curl -fsSL -o "$2" "$1"; }

HQ=KSC-19690716-MH-NAS01-0001-The_Flight_of_Apollo_11_The_Eagle_Has_Landed_HS_from_Film_JSC-DVC_1928
get "$IMG/video/$HQ/$HQ~orig.mp4" assets/nasa/hq194.mp4
BR=KSC-19690716-MH-NAS01-0001-Apollo_11_Historical_Footage_and_Broll-DVC_1560
[ -s assets/nasa/broll_mocr.mp4 ] || ffmpeg -v error -y -ss 1255 -i "$IMG/video/$BR/$BR~orig.mp4" -t 65 -c copy assets/nasa/broll_mocr.mp4

for f in 569462main_eagle_has_landed 590333main_ringtone_eagleHasLanded_extended; do
  get "https://www.nasa.gov/wp-content/uploads/2015/01/$f.mp3" "assets/nasa/$f.mp3"
done

# photographs: resolve the original-resolution file through the NASA Image API
for id in as11-37-5437 6901000 as11-44-6552 as11-44-6642 as11-40-5903 as11-40-5878; do
  [ -s "assets/nasa/$id.jpg" ] && continue
  url=$(curl -fsSL "https://images-api.nasa.gov/asset/$id" | python3 -c "
import sys, json
h = [x['href'] for x in json.load(sys.stdin)['collection']['items']]
print(([x for x in h if '~orig' in x] or [x for x in h if '~large' in x])[0].replace('http:', 'https:'))")
  curl -fsSL -o "assets/nasa/$id.jpg" "$url"
done

for id in 464 587; do get "https://assets.mixkit.co/music/$id/$id.mp3" "assets/music/$id.mp3"; done
for id in 2299 1492 1490 490 498 788 1143; do
  get "https://assets.mixkit.co/active_storage/sfx/$id/$id-preview.mp3" "assets/sfx/$id.mp3"
done

GF=https://raw.githubusercontent.com/google/fonts/main/ofl
for w in Black ExtraBold SemiBold; do get "$GF/barlowcondensed/BarlowCondensed-$w.ttf" "assets/fonts/BarlowCondensed-$w.ttf"; done
get "$GF/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf" assets/fonts/JetBrainsMono.ttf
mkdir -p hf/assets/fonts && cp assets/fonts/*.ttf hf/assets/fonts/
echo "assets ready"
