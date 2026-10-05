# TikTok sports clips, built for the viral metrics

Three upload-ready clips, each 9:16, 1080×1920, 30 fps, H.264 with AAC at −14 LUFS and 13–15 s long. Each one targets a different metric:

| Clip | Mechanic | Main lever |
|---|---|---|
| `bolt.py` – **9,58 in Echtzeit** | Bolt's 100 m world record (Berlin 2009) in real time, with a live clock, live km/h and a distance bar | completion rate (the clock creates a "watch to 9.58" pull), rewatches, comments ("wie weit kämst du?") |
| `quiz.py` – **Erkennst du ihn am Jubel?** | 5 pixelated celebrations with a 3-2-1 countdown, then a reveal: Ronaldo, Mbappé, Pogba, Hazard, Vardy | comments ("wie viele hattest du?"), rewatches (people replay to check), 1/5 progress dots |
| `rank.py` – **3 Tore, die eigentlich unmöglich sind** | #1 teased in the first 0.6 s, then #3 Yamal → #2 Hazard → #1 Ronaldo bicycle kick, with a list that fills as each ball goes in | retention (waiting for #1), shares, comments ("welches ist deine Nr. 1?") |

## Common rules

- **The hook is in frame 1.** Large title text and moving footage start immediately. Nothing important sits in TikTok's UI zones: the top 150 px, the right-hand button column, or the caption area below y≈1560.
- **The music is self-made.** Beats, ticks, whooshes, impacts and dings are synthesised in `tk.py`, so the audio track carries no music copyright. You can still add a trending sound in the app on top.
- **Seamless loop.** The last frame flows back into the hook.
- The **data in the Bolt clip** comes from the official 10 m splits, including the 0.146 s reaction time. The speed profile peaks at 12.42 m/s (44.72 km/h) around 60–70 m, and its integral matches the splits within about 0.5 m.

## Pipeline

```bash
./fetch_sources.sh            # all sources (Bilibili, 1080p) + Montserrat Black Italic -> media/
python3 bolt.py               # -> media/bolt/out/bolt_958_echtzeit.mp4   (~3.5 min)
python3 quiz.py               # -> media/quiz/out/jubel_quiz.mp4          (~8 min, motion-interpolated slow-mo)
python3 rank.py               # -> media/rank/out/3_unmoegliche_tore.mp4  (~7 min)
```

Requirements: `ffmpeg`, `python3` with `numpy`, `scipy`, `opencv-python-headless`, `pillow`, `fonttools` and `brotli`, plus `yt-dlp`.

## Captions to post with them

| Clip | Caption | Hashtags |
|---|---|---|
| Bolt | Wie weit wärst du in 9,58 Sekunden gekommen? 👇 | #usainbolt #weltrekord #sprint #leichtathletik #fyp |
| Quiz | Wie viele hast du erkannt? Ehrlich sein 👀 | #fußball #quiz #jubel #ronaldo #fyp |
| Ranking | Welches ist deine Nr. 1? 👇 | #fußball #traumtor #ronaldo #yamal #hazard #fyp |

## Notes

- **Copyright.** The footage is broadcast material, so TikTok may mute or restrict a clip. Check the status right after upload.
- **Burned-in overlays.** Every crop avoids the sources' overlays: the timer box in the Bolt source, bilibili watermarks, broadcaster logos, scoreboards and subtitles.
