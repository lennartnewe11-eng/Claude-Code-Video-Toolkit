# Black-and-white loop edits – Hazard, Mbappé, Yamal (+ Neymar)

Three edits in exactly the style of the [Neymar edit](../neymar-jr/): the same reference song segment, beat grid, grade, grain, flash, punch and fade, and the same shot structure. Each is 13.6 s, 16:9, 1080p30, and loops seamlessly.

`engine.py` is the Neymar renderer turned into a shared engine. Each player is a small module with an edit decision list. As a proof that the style is identical, `neymar.py` re-renders the original Neymar edit **bit-identically** (the video MD5 matches `edits/neymar-jr`).

The footage, the reference video and the song are **not** in git (`media/` is ignored).

```bash
./fetch_sources.sh                                                        # all sources -> media/<player>/src
mkdir -p media/audio && ffmpeg -i reference.MP4 -vn -ar 44100 -ac 2 media/audio/ref_audio.wav
python3 engine.py hazard                                                  # -> media/hazard/out/hazard_edit.mp4
python3 engine.py mbappe
python3 engine.py yamal
python3 engine.py neymar                                                  # == edits/neymar-jr output
python3 engine.py yamal --preview                                         # 3 stills per shot
```

## The shared structure

Each player fills the same slots. `G(n) = 0.0022 + 0.4685·n` gives the output time of beat `n`, and the drop is at `n = 13`.

| Beats | Role | Hazard | Mbappé | Yamal |
|---|---|---|---|---|
| 0–5 | intro, wide, slow-mo | ball on the head, Belgium training WC 2018 | juggling (commercial) | warm-up jacket, Camp Nou |
| 5–8 | close-up | head down, training | the look, WC final 2022 | boots + ball close-up |
| 8–12 | face, slow push-in | the stare from the Chelsea bench | face close-up | face close-up |
| 12–13 | ball at the feet | close run with the ball | feet + ball | feet + ball |
| **13** | **drop: white flash** | sprint | close dribble vs Real | close dribble, Estrella board |
| 14–17 | one dribble, 3 punch-ins | vs Liverpool | PSG–Real 2022, the 94' run | vs Real Madrid |
| 17 | emotion | smile | the scream (WC final) | hands on head |
| 18–21 | one cut per beat | dribbles, face, West Ham run | vs Argentina, profile, at Courtois, feet | dribbles, the smile |
| 22 | name from behind | **HAZARD 10** | **MBAPPE 10** | **LAMINE YAMAL 10** |
| 23.3–25 | signature goal, **strike on the cut** | solo vs West Ham 2019 | 2-2 volley, WC final 2022 | curler vs France, EURO 2024 |
| 25–26 | ball in | goal-line camera | net camera | keeper beaten (Lidl board) |
| 26–end | celebration, slow-mo, fades to black | hands behind the ears | arms crossed | celebration |

## Notes

- **Overlays.** Every crop avoids the burned-in overlays: watermarks (bilibili, NT, JogaBy E, 小张), broadcaster bugs, scoreboards and subtitles. The comments in each module say which source has what.
- **Shot boundaries.** Scene detection checked every EDL range for source cuts, and the boundaries were set frame-exactly. One exception: the Mbappé and Yamal "ball in" shots keep the source's own zoom steps.
- **Mbappé volley.** It comes from the wide broadcast camera. The crop zooms in by about 1.6× and runs at 0.55× with motion interpolation, so it is softer than the other shots.
- **Loudness** is −13.9 LUFS integrated, the same as Neymar; true peak is about −3.4 dBFS.
