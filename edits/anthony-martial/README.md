# Anthony Martial (Man Utd) – 16:9 TikTok edit on the song's opening hook

A 14.2 s, 1080p30 edit that loops seamlessly. It uses the same German rap track as the [Ronaldo edit](../cristiano-ronaldo/), but this time its opening hook ("*Bin auf Cartier, nicht auf Ray-Ban …*"). Almost every shot is match footage: goals, solo runs and the celebrations straight after them.

The footage, the song and the font binary are **not** in git (`media/` is ignored). This folder holds only the pipeline to rebuild the edit.

## Pipeline

```bash
./fetch_sources.sh                          # PL "every Martial goal" compilation (Bilibili, 1080p30) + font -> media/
ffmpeg -i song.mp3 -ar 44100 -ac 2 media/audio/song.wav
python3 render.py media/out/martial_edit.mp4   # ~5 min on 4 cores
python3 render.py --preview                    # 3 stills per shot to check crops
```

The beat grid and lyric timestamps come from `../cristiano-ronaldo/analyze_song.py`, since it is the same song.

## Which part of the song, and why

The opening hook runs twice. The second pass covers **14.70 → 28.92 s**, 4 bars at 135 BPM, and it is the one used here.

| | First pass, 0.5–14.7 s | Second pass, 14.7–28.9 s (used) |
|---|---|---|
| Lyric | "Bin auf Cartier …" | the same |
| Drums | straight | **drop-out** at 22.25–24.03 s ("Ich bin Selfmade, 100%") |
| Ending | kick roll into the downbeat | kick roll into the downbeat |

Two reasons for the second pass:

- **It has the drop-out.** Of all the beginnings of the song, this is the only one with a built-in tension-and-release moment.
- **It loops seamlessly.** It starts on the downbeat right after a kick roll and ends exactly on the next roll, the same way the song itself goes. The lyric "Bin auf Cartier" opens it too, so TikTok's auto-replay is musically invisible.

## Built for TikTok metrics

| Metric | What the edit does |
|---|---|
| **Hook rate (0–2 s)** | Frame 1 is already the run on his debut vs Liverpool, with the caption **"DEBÜT MIT 19. GEGEN LIVERPOOL."** (debut at 19, against Liverpool) for context and curiosity. The first strike lands at 1.3 s. |
| **Retention** | Each bar is one goal told in three shots (run, strike on the kick, ball in or celebration), so there is a payoff every 3.6 s. |
| **Mid-point spike** | In bar 3 the drums drop out: the Fulham solo runs in slow-mo (0.48×, motion-interpolated) and the **strike lands exactly when the kick returns**, with a flash and shake. |
| **Completion & rewatch** | 14.2 s total. The last bar speeds up (a goal, then three one-beat flashes on the kick roll) and ends on Martial's look, which loops straight back into the debut run. |

## Edit decision list

All shots come from `plcomp.mp4`. `B(k) = 32.030 + 0.4444·k` (song time); the edit covers `B(-39)` to `B(-7)`.

| Beats | Song | Shot | Source time |
|---|---|---|---|
| −39 → −36 | "Bin auf Cartier" | **Debut vs Liverpool 2015**: run past Clyne, strike on the kick (with caption) | 17.59–18.92 |
| −36 → −34 | | ball in, behind-the-line angle | 19.48–20.37 |
| −34 → −31 | | corner-flag celebration jump | 9.40–10.73 |
| −31 → −28 | "Mach kein Rückzug" | **Stoke 2016**: solo, strike on the kick | 202.59–203.92 |
| −28 → −26 | | ball into the far corner | 204.62–205.51 |
| −26 → −23 | | arms-wide celebration | 206.05–207.38 |
| −23 → −22 | "Ich bin Selfmade" | **Fulham 2019**: turn | 51.00–51.44 |
| −22 → −18 | *(drums drop out)* | dribble in slow-mo (0.48×), **strike on the kick return** | 51.44–52.30 |
| −18 → −15 | | keeper beaten (slow-mo), then net-cam | 52.30–53.46 |
| −15 → −12 | "Hab nur Augen für Geld" | **Cardiff 2018**: solo, strike on the kick | 28.09–29.42 |
| −12 → −10 | | ball in, behind-the-goal angle | 30.15–31.04 |
| −10 / −9 / −8 | kick roll | Norwich 2019 ball in · Southampton 2020 strike · Martial's look, which loops to the start | 136.0 · 40.05 · 32.25 |

## Notes

- **Crops.** The source has a Premier League lion (top right) and a bilibili watermark (bottom right) burned in. `safe_window()` pushes every 16:9 crop window out of both areas automatically. Crops run between 1.11× and 1.32× zoom, and keyframes follow the action.
- **Hidden cuts.** Scene detection flags something every 0.2 s inside some shots. These are duplicated frames from the source's 25 → 30 fps conversion, not cuts. I checked every shot visually.
- **Look.** Impacts (net, drop-out return) get a 10–12 % zoom punch, a flash, an RGB split and shake. Cuts get a 4.5 % punch, each roll beat a 6 % punch, and the snares a 2 % bounce. Grade: contrast 1.08, saturation 1.15, unsharp mask, vignette.
- **Audio.** It starts 10 ms before the downbeat so the kick transient is intact, and has 5 ms anti-click fades. Two-pass `loudnorm` with a linear gain brings it to −14 LUFS; true peak is about −3.6 dBFS.
- **Export.** H.264 High, CRF 16, AAC 320k. For uploads under 30 MB, re-encode with CRF 17, which gives about 26 MB.
