#!/bin/sh
# Downloads the 1080p source videos used by the EDL (video only) from Bilibili.
set -e
mkdir -p src src2
for id in BV1dwad6cE5G BV1ZP4y1H7BF BV1TyNv6oEHR BV1JsGT6pESA BV1SzM2zDE17 BV1VP4y1k7eP BV1R54y1B7CN BV1Ja41197y4 BV1eB4y197w8; do
  yt-dlp -q --no-playlist -f "bv*[vcodec^=avc1]/bv*" -o "src/$id.%(ext)s" "https://www.bilibili.com/video/$id"
done
for id in BV1gbgCzUEiS BV1c5411t7KD BV1Cg41117HH BV1hs411j7J5; do
  yt-dlp -q --no-playlist -f "bv*[vcodec^=avc1]/bv*" -o "src2/$id.%(ext)s" "https://www.bilibili.com/video/$id"
done
