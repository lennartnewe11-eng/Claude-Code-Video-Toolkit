#!/usr/bin/env bash
# Downloads every source used by the four EDLs into ./media/<player>/src (public Bilibili uploads;
# YouTube blocks datacenter IPs). Bilibili rate-limits: keep it sequential.
# The music is the audio track of the reference TikTok: media/audio/ref_audio.wav (see README).
set -euo pipefail
cd "$(dirname "$0")"

dl() {  # dl <player> <bilibili av id> <name>
  mkdir -p "media/$1/src"
  yt-dlp -f "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]" \
    -o "media/$1/src/$3.%(ext)s" "https://www.bilibili.com/video/av$2"
  sleep 5
}

# Eden Hazard
dl hazard 34446054        comp1819   # "Eden Hazard – Out Of This World" 18/19 (letterboxed) – WC 2018 training, bench close-ups
dl hazard 216851398       top10      # Chelsea top-10 goals – Liverpool dribbles, HAZARD 10, West Ham solo (close camera)
dl hazard 600305254       westham    # West Ham 2019 broadcast (pillarboxed) – hands-behind-the-ears celebration
# Kylian Mbappé
dl mbappe 93373475        hd60       # 60 fps commercial footage – juggling, face close-up
dl mbappe 117366222688766 night4k    # World Cup final 2022 cinematic – the look, the scream, MBAPPE 10
dl mbappe 812092144       rmcinema   # PSG–Real Madrid 2022 cinematic – 94' run, close dribbles
dl mbappe 113583933495572 wcfinal22  # World Cup final 2022 – 2-2 volley + net camera
dl mbappe 479222393       wcgoals    # all 12 World Cup goals – MBAPPE 10 back, arms crossed
# Lamine Yamal
dl yamal 116304509934583  y2026      # Yamal 2026 compilation – warm-up, close-ups, dribbles, LAMINE YAMAL 10
dl yamal 115112455178309  pure       # "纯享亚马尔" – EURO 2024 goal vs France, hands on head, smile
dl yamal 1456185188       eurofra    # EURO 2024 Spain–France – celebration
# Neymar Jr (to prove engine.py reproduces edits/neymar-jr bit-identically)
dl neymar 948811450       rare
dl neymar 41712216        skills1819
dl neymar 117256533187967 scene8k
dl neymar 744797460       faces
dl neymar 207001101       uclpsg

echo "Now extract the reference audio, e.g.:"
echo "  mkdir -p media/audio && ffmpeg -i <reference>.MP4 -vn -ar 44100 -ac 2 media/audio/ref_audio.wav"
