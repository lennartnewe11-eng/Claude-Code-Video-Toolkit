# Paul Pogba Edit (9:16 + 16:9)

A 1:36 beat-synced edit in two formats, vertical 1080×1920 and landscape 1920×1080 (30 fps), of prime Pogba (Juventus 2012–16, Man United 2016–19, France 2018), cut to a French track at 120 BPM. This folder holds the scripts and the edit decision list (EDL). The footage and the song are not committed.

## Structure (song time → edit)

| Edit | Music | Content |
|---|---|---|
| 0:00–0:08 | Intro | Anthem close-ups (WC 2018 semi-final and final), slow motion |
| 0:08–0:20 | Verse: "…le bout du tunnel" | Smile (Juve), tunnel walk, Etihad walkout, POGBA 6 |
| 0:20–0:30 | Verse B | Skills: vs Bayern, USA, Inter, Verona, chest-and-volley |
| 0:32–0:48 | Pre-chorus: "graver ton image…" | Slow-motion stares, then the WC final goal replay. The ball hits the net on the drop |
| 0:48–1:20 | Chorus | Final celebration, Udinese volley, Napoli volley, both arms to the sky, Etihad celebration and header, Europa League final goal, arms crossed, hand to ear, trophy dance |
| 1:20–1:36 | Breakdown: "j'sais pas si je t'aime" | Finger to the sky, calm celebration, back view, eyes closed, title card |

Audio: intro + verse 1 + pre-chorus 1 are spliced into chorus 2 + breakdown. Both chorus entries follow identical bars (mel correlation 0.99), so the splice is inaudible (`build_audio.sh`).

## Pipeline

```sh
./download_sources.sh             # 13 Bilibili sources, 1080p, video only
./build_audio.sh song.mp3         # -> audio_edit.wav (96.26 s)
python3 make_edl.py               # -> edl.json (37 clips on the beat grid)
python3 render.py edl.json v916.mp4 --size 1080x1920 --override overrides_9x16.json
python3 render.py edl.json v169.mp4 --size 1920x1080 --override overrides_16x9.json
ffmpeg -i v169.mp4 -i audio_edit.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest out.mp4
```

Both formats use the same EDL: same clips, in-points and cuts. The override files only change what the wider frame
needs:
- `ylim`/`xlim`: a per-clip "clean rectangle" that keeps uploader watermarks, broadcaster bugs, scoreboards,
  burnt-in subtitles and letterbox bars out of the frame
- `fit`: shows the two square (1080×1080) sources on a blurred fill instead of cropping heads or feet
- `clone`: a feathered clone stamp for watermarks over blurred background (available, currently unused)

The renderer renders clips in parallel into cached segments (a clip only re-renders when its settings change), then
concatenates them and applies the grade in the final encode.

`render.py` renders each clip for a whole number of beats. For each clip it:
- crops a 9:16 window whose centre follows keyframes (`cx`), picked by eye from frame strips so Pogba stays centred
- uses `ylim` to crop out burnt-in subtitles and uploader logos
- applies motion-interpolated slow motion (`minterpolate`, run on a pre-cropped strip for speed)
- adds beat effects (`punch` zoom, `flash`, `shake`, `zoomin`, fades)

A light grade (contrast, saturation, sharpen, vignette) and the closing title in Bebas Neue are then applied over the whole edit.

Tools used for clip selection (`tools/`):
- `bilibili_search.py`: search Bilibili
- `contact_sheet.py`: scene-detect a source and write one thumbnail per shot
- `frame_strip.py`: frame strips with a 10 % grid for choosing crop positions
- `review_sheet.py`: sample every clip of a rendered edit for QA
- `overlay_sheet.py`: full source frames with a grid, to map logos and subtitles for the 16:9 clean rectangles
- `letterbox_check.py`: find burnt-in black bars in the sources
- `analyze_song.py`, `beat_grid.py`: tempo, downbeats and section boundaries

Requirements: ffmpeg, yt-dlp, Python with numpy, opencv-contrib-python-headless, pillow and librosa, plus `fonts/BebasNeue-Regular.ttf` (Google Fonts, OFL).

## Sources

All clips come from public Bilibili uploads of broadcast footage: FIFA / CCTV, Premier League, Serie A, UEFA and Manchester United's official channel. The rights stay with the respective rights holders. This edit is a personal fan edit.
