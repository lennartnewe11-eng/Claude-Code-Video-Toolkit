# Jamie Vardy – beat-synced football edit (16:9)

A ~23 s TikTok-style edit: iconic Vardy goals, match scenes first, and the corner-flag slide at Bramall Lane. The cut starts on the lyric "Destroy it all", and every hard cut or impact lands on a hit of the song.

The footage and the music are copyrighted, so they are **not** in git (`media/` is ignored). This folder holds only the pipeline to rebuild the edit.

## Pipeline

```bash
./fetch_sources.sh                                   # 2 source compilations -> media/src (Bilibili, 1080p)
ffmpeg -i song.mp3 -ar 44100 -ac 2 media/audio/song.wav
python3 analyze_song.py media/audio/song.wav         # lyric timestamps, silence gaps, tempo
python3 render.py media/out/vardy_edit.mp4           # full render (~5 min on 4 cores)
python3 render.py --preview                          # writes 2 stills per shot to media/out/ to check crops
```

Requirements: `ffmpeg` (with `minterpolate`, `vignette`, `unsharp`), `python3`, `numpy`, `opencv-python-headless`, `librosa`, `yt-dlp`. `faster-whisper` is optional and only used for the lyric timestamps.

## Music analysis

| | |
|---|---|
| Tempo | ~86.85 BPM half-time phonk, bar = 2.763 s |
| "Destroy it all" | music re-enters at **1.906 s** after the silence that follows "Promise me just one thing". The edit starts here |
| Bar hits | 2.648 · 5.408 · 8.172 · 10.935 · 13.699 · 16.463 · 19.221 · 21.985 (each comes right after a ~0.1 s full-band silence) |
| Sub-hits per bar | +0.518 · +0.691 · +1.036 · +1.727 (808) · +2.072 · +2.245 · +2.418 s |
| End | 24.614 s, where the next silence starts. The last 3 frames are black, so the edit loops cleanly back into "Destroy it all" |

## Edit decision list (song time)

| Song time | Shot | Source | Sync point |
|---|---|---|---|
| 1.906–3.166 | **Corner flag hook**, red-seat angle | top10 3.9–5.2 | flag snaps on "ALL" (H1) |
| 3.166–5.408 | Liverpool 2016: slow-mo as the ball drops | top10 139.4–140.83 (0.64×, motion-interpolated) | volley contact on H2 |
| 5.408–7.135 | Ball flight, then Mignolet beaten | top10 140.83–141.35, 143.15–144.55 | |
| 7.135–8.172 | Vardy's walk-off | top10 137.6–138.7 | |
| 8.172–10.935 | **11 in a row** vs Man Utd 2015: finish, run, scream | celebs 74.0–79.0 | ball in net on H3+0.5 |
| 10.935–13.699 | **Drop**: Spurs volley, Man Utd 2021, Villa pen, Sunderland, Villa, Arsenal scream | mixed | one cut per sub-hit |
| 13.699–16.463 | Sheffield Utd 90th-minute winner | top10 27.3–30.1 | ball in net on the 808 |
| 16.463–19.221 | Run to the corner, slide | top10 30.4–33.05 (crop pans left onto the flag) | **flag impact on H7** |
| 19.221–21.985 | Rainbow flag flying (slow-mo), back up, yellow card | top10 33.05–36.15 | |
| 21.985–24.700 | "VARDY 9", arms spread, slow push-in, cut to black | celebs 79.4–82.1 | |

## Look

- **Crops** remove the burned-in Chinese subtitles, the uploader watermark, the scoreboard and the LCFC TV bug. The top10 crop is 1458×820 from y=112; the celebs crop is 1664×936. Both are scaled to 1920×1080 with lanczos and sharpened with `unsharp`.
- **On every bar hit:** a zoom punch (+10 %), a short RGB split, and a white flash, strongest on the two flag impacts and the drop. The flag impacts also get camera shake.
- **Sub-hits** get a small zoom punch (+4.5 %).
- **Grade:** contrast 1.07, saturation 1.16, slight vignette.
- **Export:** H.264 High, 1080p30, CRF 16, AAC 320k, `+faststart`. Loudness is about −14 LUFS integrated, which matches the TikTok target.
