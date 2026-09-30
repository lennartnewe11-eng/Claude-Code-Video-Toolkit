# Paul Pogba Edit (9:16)

A 1:36 beat-synced vertical edit (1080×1920, 30 fps) of prime Pogba (Juventus 2012–16, Man United 2016–19, France 2018), cut to a French track at 120 BPM. This folder holds the scripts and the edit decision list (EDL). The footage and the song are not committed.

## Structure (song time → edit)

| Edit | Music | Content |
|---|---|---|
| 0:00–0:08 | Intro | Anthem close-ups (WC 2018 semi-final and final), slow motion |
| 0:08–0:20 | Verse: "…le bout du tunnel" | Smile (Juve), tunnel walk, Etihad walkout, POGBA 6 |
| 0:20–0:30 | Verse B | Skills: vs Bayern, USA, Inter, Verona, chest-and-volley |
| 0:32–0:48 | Pre-chorus: "graver ton image…" | Slow-motion stares, then the WC final goal replay. The ball hits the net on the drop |
| 0:48–1:20 | Chorus | Final celebration, Udinese volley, Napoli volley, City brace, Europa League final goal, arms crossed, hand to ear, trophy dance |
| 1:20–1:36 | Breakdown: "j'sais pas si je t'aime" | Finger to the sky, calm celebration, back view, eyes closed, title card |

Audio: intro + verse 1 + pre-chorus 1 are spliced into chorus 2 + breakdown. Both chorus entries follow identical bars (mel correlation 0.99), so the splice is inaudible (`build_audio.sh`).

## Pipeline

```sh
./download_sources.sh             # 13 Bilibili sources, 1080p, video only
./build_audio.sh song.mp3         # -> audio_edit.wav (96.26 s)
python3 make_edl.py               # -> edl.json (37 clips on the beat grid)
python3 render.py edl.json video.mp4
ffmpeg -i video.mp4 -i audio_edit.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest out.mp4
```

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
- `analyze_song.py`, `beat_grid.py`: tempo, downbeats and section boundaries

Requirements: ffmpeg, yt-dlp, Python with numpy, opencv-contrib-python-headless, pillow and librosa, plus `fonts/BebasNeue-Regular.ttf` (Google Fonts, OFL).

## Sources

All clips come from public Bilibili uploads of broadcast footage: FIFA / CCTV, Premier League, Serie A, UEFA and Manchester United's official channel. The rights stay with the respective rights holders. This edit is a personal fan edit.
