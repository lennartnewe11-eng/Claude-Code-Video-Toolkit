#!/bin/bash
# Build an adaptive HLS stream (1080p + 720p, fMP4 segments) + poster from the master render.
set -e
IN=${1:?usage: make_hls.sh MASTER.mp4 OUTDIR}; ODIR=${2:?usage: make_hls.sh MASTER.mp4 OUTDIR}

OUT=$ODIR/hls
rm -rf "$OUT"; mkdir -p "$OUT/1080" "$OUT/720"
GOP="-g 120 -keyint_min 120 -sc_threshold 0 -force_key_frames expr:gte(t,n_forced*4)"
enc() { # name scale vbitrate maxrate bufsize
  ffmpeg -v error -y -i "$IN" -vf "scale=$2:flags=lanczos" -c:v libx264 -preset slow -profile:v high \
    -b:v $3 -maxrate $4 -bufsize $5 $GOP -pix_fmt yuv420p \
    -c:a aac -b:a 160k -ar 48000 \
    -f hls -hls_time 4 -hls_playlist_type vod -hls_segment_type fmp4 \
    -hls_fmp4_init_filename init.mp4 -hls_segment_filename "$OUT/$1/seg_%03d.mp4" \
    "$OUT/$1/index.txt"
}
enc 1080 1920:1080 5500k 8000k 11000k &
enc 720 1280:720 2400k 3600k 5000k &
wait
cat > "$OUT/master.txt" <<EOF
#EXTM3U
#EXT-X-VERSION:7
#EXT-X-INDEPENDENT-SEGMENTS
#EXT-X-STREAM-INF:BANDWIDTH=8300000,AVERAGE-BANDWIDTH=5700000,RESOLUTION=1920x1080,FRAME-RATE=30.000,CODECS="avc1.640032,mp4a.40.2"
1080/index.txt
#EXT-X-STREAM-INF:BANDWIDTH=3800000,AVERAGE-BANDWIDTH=2600000,RESOLUTION=1280x720,FRAME-RATE=30.000,CODECS="avc1.64001f,mp4a.40.2"
720/index.txt
EOF
ffmpeg -v error -y -ss 17.2 -i "$IN" -frames:v 1 -vf scale=1280:720 -q:v 4 "$ODIR/poster.jpg"
du -sh "$OUT" "$OUT/1080" "$OUT/720"; ls "$OUT/1080" | wc -l; ls "$OUT/720" | wc -l
ls -la "$ODIR/poster.jpg"
