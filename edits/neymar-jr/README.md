# Neymar Jr – black-and-white edit modelled on a reference TikTok (16:9)

A 13.6 s, 1080p30 edit that loops seamlessly. It was built from a reference video the user supplied: a screen recording of a Neymar TikTok edit. The edit reuses the reference's song segment and rebuilds its structure, look and cut rhythm shot by shot from fresh Neymar footage.

The footage, the reference and the song are **not** in git (`media/` is ignored). This folder holds only the pipeline to rebuild the edit.

## How the reference is built

The screen recording is 886×1920. Its 16:9 video sits at `crop=886:498:0:536`, between the TikTok UI elements. A contact sheet, scene detection and audio analysis give the following:

| Feature | Reference |
|---|---|
| Format | 16:9, **completely black and white**, crushed blacks, hard contrast |
| Song | A vocal intro ("*I don't call my phone, make me feel right…*") with a pause at 1.4 s, then the drop at 6.07 s. 128 BPM, one 13.64 s loop |
| Intro (no drums) | Long, calm shots: warm-up juggling (wide), then feet and ball close-up, then a face close-up with the ball |
| Drop | **White flash**, then **one cut per beat**, alternating CL dribbles with face close-ups (hands on face, profile) |
| Climax | "NEYMAR JR 10" from behind, then a **free kick vs Red Star** (Gazprom boards), ball in, team celebration |
| Ending | The celebration fades to black, followed by about 0.6 s of black, then the loop restarts at the warm-up |

## How this edit maps onto it

| Song time | Beats | Shot | Source |
|---|---|---|---|
| 0.00–2.33 | intro | UCL warm-up juggling, slow-mo 0.75× | `rare` 38.9 s |
| 2.33–3.77 | | feet and ball close-up | `skills1819` 242.4 s |
| 3.77–5.63 | | face close-up, slow-mo with push-in | `skills1819` 444.8 s |
| 5.63–6.10 | | ball at the feet | `skills1819` 679.8 s |
| **6.10** | **drop** | **white flash** + feet close-up | `skills1819` 603.9 s |
| 6.57–7.97 | 1 cut/beat | dribble vs Real Madrid (Bernabéu 2018), 3 crops that push in | `scene8k` 11.3 s |
| 7.97 | | hands on face | `faces` 79.1 s |
| 8.43 | | dribble vs Bayern, CHAMPIONS LEAGUE board | `scene8k` 13.2 s |
| 8.90 | | profile in the Bernabéu crowd | `scene8k` 22.6 s |
| 9.37–10.30 | | two close dribbles | `skills1819` 342.4 / 456.0 s |
| 10.30 | | **NEYMAR JR 10** from behind | `faces` 77.9 s |
| 10.93 | | **free kick vs Red Star 2018** (Gazprom); the strike lands on the cut | `uclpsg` 31.1 s |
| 11.70 | | ball in, keeper beaten | `uclpsg` 32.5 s |
| 12.17–13.64 | | crossed-arms celebration in slow-mo, fading to black | `uclpsg` 105.2 s |

The beat grid is `G(n) = 0.0022 + 0.4685·n` in output time, with the drop at `n = 13`. The audio is the reference's own track from 0.9753 s (its first sample) for 13.638 s, up to where the next loop starts. That makes the export loop seamlessly.

## Pipeline

```bash
./fetch_sources.sh
ffmpeg -i reference.MP4 -vn -ar 44100 -ac 2 media/audio/ref_audio.wav
python3 render.py media/out/neymar_edit.mp4    # ~4 min on 4 cores
python3 render.py --preview                    # 3 stills per shot
```

## Look

- **Black and white:** luma only, with an S-curve LUT that crushes the blacks (−6 %) and pushes up the highlights, plus a strong vignette.
- **Film grain:** 4 pre-baked, slightly blurred noise plates. Random grain per frame made the file 84 MB; this keeps the texture at 17.7 MB.
- **Effects:** the drop gets a full white flash and a 10 % zoom punch. Each cut gets a 5 % punch, and the ball going in gets a light flash. The last shot fades from beat 27 to 27.8 and stays black until the loop restarts.
- **Crops:** they push in a little and leave out the sources' watermarks: JYDN, ALLFOOTBALL, Ney-magic, bilibili, the UEFA bug and the subtitles.
- **Audio:** two-pass `loudnorm` with a linear gain brings it to −14 LUFS; true peak is about −3.4 dBFS.
- **Export:** H.264 High, CRF 18, AAC 256k.
