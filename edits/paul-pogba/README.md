# Paul Pogba – beat-synced football edit on "Alors on danse" (16:9)

A 22.4 s TikTok-style edit in the style of the [Jamie Vardy edit](../jamie-vardy/). It shows Pogba's goals and his dances. Every **"danse"** in the chorus lands on a 2-bar downbeat, and each one gets a goal or a celebration.

The footage and the music are copyrighted, so they are **not** in git (`media/` is ignored). This folder holds only the pipeline to rebuild the edit.

## Pipeline

```bash
./fetch_sources.sh                                   # 5 source videos -> media/src (Bilibili)
ffmpeg -i song.mp3 -ar 44100 -ac 2 media/audio/song.wav
python3 analyze_song.py media/audio/song.wav         # tempo, kick-aligned beat grid, where "danse" lands
python3 render.py media/out/pogba_edit.mp4           # full render (~5 min on 4 cores)
python3 render.py --preview                          # 3 stills per shot in media/out/ to check crops
```

Requirements: `ffmpeg`, `python3`, `numpy`, `opencv-python-headless`, `librosa`, `yt-dlp`. `faster-whisper` is optional and only used for the lyric timestamps.

## Music analysis

| | |
|---|---|
| Tempo | 118.02 BPM, so one beat is 0.5084 s and one bar is 2.034 s |
| Beat grid | `B(k) = 55.0105 + 0.5084·k`, snapped to the kick drum (the onset envelope sits about 22 ms late) |
| Start | `B(5)` = 57.55 s, the bar line one beat before "Alors on sort pour oublier tous les problèmes" |
| Drop | `B(13)` = 61.62 s, on the first "Alors on **danse**" |
| "danse" hits | `B(13) · B(21) · B(29) · B(37) · B(45)`, one every 2 bars |
| End | `B(49)` = 79.92 s. That makes exactly 11 bars, so the TikTok loop restarts on the beat |

## Edit decision list

| Beats | Song | Shot | Source |
|---|---|---|---|
| 5–13 | build-up | smoke tunnel with the World Cup trophy, arms spread in the smoke, the stare (Juve), the volley vs Napoli in slow-mo as the ball drops | dance_show, udinese, peak |
| **13** | **DANSE** (drop) | **contact on the drop**: Napoli volley into the top corner | peak 132.64 |
| 15–21 | | Juve arms spread (slow-mo), skill vs Leeds, the shot in the **2018 World Cup final** | peak, wcfinal |
| **21** | **DANSE** | ball in the net (net-cam), then 4 beats of the arms-spread celebration, then the smoke dab | wcfinal, dance_show |
| **29** | **DANSE** | dance block, one cut every 2 beats with a bounce on every beat: Bailly × Pogba, Old Trafford night dance, Lingard × Pogba, point | dance_show |
| **37** | **DANSE** | Swansea celebration, "POGBA 6" close-up (EURO 2020 screamer vs Switzerland), France pile-on, Juve gesture (slow-mo) | peak, euro2020 |
| **45–49** | **DANSE** | "can't hear you" pose, slow push-in, hard cut on the bar line | peak 156.0 |

## Look

- **Crops** remove every logo, ticker, scoreboard, subtitle and letterbox bar. `dance_show` is letterboxed at 2.42:1 inside 720p, so those shots are cropped to 939×528 and scaled up about 2×, which makes them noticeably softer than the 1080p shots.
- **On every "danse":** a 10 % zoom punch, a white flash and an RGB split. The drop also gets camera shake.
- **Other cuts** get a 4.5 % punch. During the dance block every beat adds a 3 % bounce.
- **Grade:** contrast 1.08, saturation 1.18, unsharp mask, vignette.
- **Audio:** two-pass `loudnorm` with a linear gain to −14 LUFS integrated, which matches the TikTok target. True peak is about −2.6 dBFS.
- **Export:** H.264 High, 1080p30, CRF 16, AAC 320k, `+faststart`.
