# Cristiano Ronaldo – vertical TikTok edit, built for watch time (9:16)

A 20.6 s edit in 1080×1920. The brief was to pick the player most likely to get maximum attention on TikTok and to structure the edit for maximum watch time.

The footage, the song and the font binary are **not** in git (`media/` is ignored). This folder holds only the pipeline to rebuild the edit.

## Why Ronaldo

- **Reach.** He is the most-followed athlete on every platform and the largest football fandom on TikTok. "CR7 edits" is its own genre, so the edit gets reach from the start.
- **The lyrics tell his story.** "*Viele, die mir heut die Hand schütteln, meinten, du ver… deine Zeit*" is the doubter line (many who shake my hand today said I was wasting my time). "*Ich lass heute meine Kunst sprechen*" (I let my art speak today) goes over his most famous goal. "*kleine Hater am Platzen vor Neid*" (little haters bursting with envy) goes over the "calma" gesture at Camp Nou. "*Ich erfülle Mamas Wunschzettel, bevor Mama geht mit der Zeit*" (I fulfil Mum's wish list before Mum goes with time) goes over his mother Dolores in tears. The comments write themselves.
- **One event per drum drop.** The song has two drum drop-outs. The first is the a-cappella intro, which ends on the bicycle kick. The second carries the SIU run and lands it on the bass return.

## Watch-time structure

| Time | Song | Picture | Purpose |
|---|---|---|---|
| 0.0 s | a-cappella "Viele, die mir heut die Hand schütteln…" | 21-year-old Ronaldo (World Cup 2006) in close-up, then screaming, with the **lyric as a caption** | Hook in frame 1: a face, text to read, and an open question |
| 2.7 s | **drop** | **Bicycle kick vs Juventus, contact on the 808**, ball in the net, celebration, Zidane, hand on heart | Payoff early, before the swipe-away window closes |
| 7.1 s | "…meine Kunst sprechen, kleine Hater…" | beard stroke vs Spain, the stare, **"calma" at Camp Nou** | Attitude and comment bait |
| 10.7 s | **"Ich erfülle Mamas Wunschzettel, bevor Mama geht mit der Zeit"** (captioned) | Ronaldo points to the stands, **Dolores in tears**, Ballon d'Or 2013 tears | Emotional peak, which drives shares and saves |
| 13.3 s | drums drop out | SIU run in slow-mo (back view, "RONALDO 7") | Suspense, so the viewer waits for the release |
| 15.6 s | **bass returns** | **SIU landing** with a flash and shake | Second payoff |
| 16.4 s | "lass kein Pisser in mein Kreis rein" | screams, laughter, Ballon d'Or kiss, trophy kiss | Fast cuts, one per beat |
| 18.9 s → loop | "…rein" | slow-mo smile of the adult Ronaldo | The end flows into the start: adult smile, then the 21-year-old. Same face, 12 years apart. **Seamless loop**, so replays count |

Other choices aimed at watch time:

- **Length.** 20.6 s, short enough for a high completion rate and long enough that loops add real watch time.
- **Cut rhythm.** A cut every 2 beats (0.89 s) is the base rate. Single beats (0.44 s) are used in the trophy run. The longest shots are the a-cappella hook and the SIU suspense.
- **Captions.** They only cover lines I could confirm (see below). They sit at 60 % of the height, outside TikTok's UI zones at the bottom and right, and pop in.
- **Format.** 9:16 full screen with no bars. The 9:16 window follows Ronaldo inside each 16:9 source through keyframes (`cx`).

## Pipeline

```bash
./fetch_sources.sh                                   # 8 Bilibili sources + Montserrat Black Italic -> media/
ffmpeg -i song.mp3 -ar 44100 -ac 2 media/audio/song.wav
python3 analyze_song.py media/audio/song.wav         # lyrics, 135 BPM grid, drum drop-outs
python3 render.py media/out/cr7_edit.mp4             # full render (~6 min on 4 cores)
python3 render.py --preview                          # 3 stills per shot (9:16) to check the tracking crops
```

Requirements: `ffmpeg`, `python3`, `numpy`, `opencv-python-headless`, `pillow`, `fonttools` + `brotli` (font conversion), `librosa`, `yt-dlp`. `faster-whisper` is optional and only used for the lyrics.

## Notes

- **Lyrics.** Three Whisper models (`small`, `medium`, `large-v3`) all heard "du **vergoldest** deine Zeit". "Vergeudest" (wasting) would make more sense, so that half of the line is **not** captioned. The Mama line is consistent across all three models and is captioned.
- **Beat grid.** `B(k) = 32.030 + 0.4444·k` (135 BPM). Drop 1 is `B(1)`. The drop-out runs from `B(27)` to `B(29)`, and the bass returns at `B(30)`. The edit runs from `B(-5)` to 50.40 s, which is the end of the word "rein".
- **Crops.** Every source is first normalised to 1920×1080 (including the anamorphic 1440×1080 clip), then a 9:16 window is cut out with sub-pixel interpolated keyframes. The crops leave out the Paramount+, GOLAZO, bilibili, FIFA TV and LaLiga logos, the scoreboards and the burned-in subtitles. Two exceptions: a faint "Ronaldo-Sui" watermark remains visible in the Camp Nou shot, and the 2006 close-ups have their black bars cropped away.
- **Slow motion.** Real slow-mo with `minterpolate` is used only on the bicycle kick and the final smile. The SIU run plays at 0.84× without interpolation, to avoid ghosting.
- **Look.** On each drop: a 12 % zoom punch, a white flash, an RGB split and shake. Each cut gets a 4.5 % punch, and each kick a 2.5 % bounce. Grade: contrast 1.08, saturation 1.15, unsharp mask, vignette.
- **Audio.** Two-pass `loudnorm` with a linear gain to −14 LUFS, which matches the TikTok target. True peak is about −2.7 dBFS.
- **Export.** H.264 High, 1080×1920, 30 fps, CRF 17, AAC 320k.
