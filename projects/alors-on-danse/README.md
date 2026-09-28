# Alors on danse — travel edit

A 16:9 (1920×1080, 30 fps) beat-synced edit of a summer trip, cut to
*Alors on danse* (Stromae). Every cut, zoom punch, flash and text hit sits on
the song's beat grid.

## Pipeline

1. **Audio**: the song's audio track is taken from a screen recording of the
   music video (only the audio is used). Beats and downbeats are detected with
   [madmom](https://github.com/CPJKU/madmom) (RNN + DBN, 4/4, ~117.6 bpm) and
   stored in `beats.json`. Lyric line timing was read from the video's
   subtitles (OCR) to place the French lyric fragments.
2. **Timeline** (`timeline.py`): shots are placed in beats, grouped by trip leg
   and played in travel order (Praha → Wien → Budapest → Alps/Bled → train to
   Croatia → Kvarner coast → Istria → last leg), with the song sections:

   | bars | song | picture |
   |---|---|---|
   | 0–3 | intro | B&W birds over Praha, letterbox, title |
   | 4–11 | riff + "alors on danse" ×4 | Praha day → evening |
   | 12–27 | verse 1 ("qui dit … dit …") | Praha at dawn → train → Wien; lyric keywords (ARGENT on the money clip, FATIGUE/RÉVEIL on the sleeping photos + 6:17 clock) |
   | 28–43 | drop 1 / chorus | Wien → Budapest |
   | 44–55 | "c'est fini", break, verse 2 | train into the Alps → Bled |
   | 56–69 | "la la la" / build | train to Croatia → Kvarner coast |
   | 70–71 | pre-drop silence | the pier dive in slow motion, frozen in B&W |
   | 72–86 | drop 2 / chorus | splash → Croatian coast, Istria |
   | 87–95 | breakdown ("encore") | golden hour → night alleys |
   | 96–105 | final chorus + outro | last leg, recap strobe, fade to B&W |
3. **Engine** (`engine.py`, `render.py`): decodes each shot with ffmpeg at
   2304×1296, then per frame: camera move (zoom/punch/beat bounce/shake/
   rotation), colour look (cine, warm, night, dream, vivid, B&W), typography,
   chromatic split, white flashes/blinks, vignette, grain, letterbox, fades.
   The render is split into chunks rendered in parallel and concatenated;
   the song is muxed (+5 dB, limited, faded).

Fonts (OFL): Anton, Instrument Serif, Space Mono — in `fonts/`.

## Render

```bash
pip install numpy opencv-python-headless pillow
python3 render.py --media "/path/to/video projekt" \
    --song "/path/to/video projekt/allors on dance, track" \
    --out alors_on_danse.mp4 --jobs 4
# quick preview: --scale 0.5 --preset veryfast --crf 23
```

The media folder is the shared Google Drive folder (`IMG_*.mov`, `IMG_*.jpeg`,
the two portrait clips and the song recording); it is not part of the repo.
