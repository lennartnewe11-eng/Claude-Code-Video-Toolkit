#!/bin/sh
# Cut the song to the edit (96.26 s, 120 BPM, first downbeat at 2.2555 s in the original track):
#   intro + verse 1 + pre-chorus 1   (2.00 -> 50.26)
#   -> chorus 2 + breakdown          (122.25 -> 170.26)   seamless: both follow an identical pre-chorus bar
# then a 3.5 s fade-out under the closing title.
set -e
SONG=${1:-song.mp3}
ffmpeg -v error -y -i "$SONG" -filter_complex \
  "[0:a]atrim=2.0:50.2605,asetpts=PTS-STARTPTS[a];[0:a]atrim=122.2505:170.2555,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d=0.01:c1=tri:c2=tri,afade=t=out:st=92.7:d=3.5[out]" \
  -map "[out]" -c:a pcm_s16le audio_edit.wav
