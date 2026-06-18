#!/usr/bin/env bash
# Concatenate all rendered parts into one film (Hook -> Ch1 -> Ch2) + loudnorm.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../remotion"
FF=../tools/ffmpeg
CLIPS="hook-full p1ev p2ev p3ev p4ev p5ev p6ev c2p1 c2p2 c2p3 c2p4 c2p5"
inputs=""; maps=""; n=0
for c in $CLIPS; do inputs="$inputs -i out/$c.mp4"; maps="$maps[$n:v][$n:a]"; n=$((n+1)); done
$FF -v error $inputs -filter_complex \
"${maps}concat=n=${n}:v=1:a=1[cv][ca];[cv]scale=1920:1080:in_range=full:out_range=tv,format=yuv420p[v];[ca]loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
-map "[v]" -map "[a]" -r 30 -c:v libx264 -profile:v high -level 4.0 -crf 20 -preset medium -color_range tv \
-movflags +faststart -c:a aac -b:a 192k out/FILM.mp4 -y
echo "wrote out/FILM.mp4"
