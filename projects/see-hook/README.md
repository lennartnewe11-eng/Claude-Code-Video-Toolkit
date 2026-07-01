# "See" — Video-Hook

Cinematische ~29-Sekunden-Hook zum Thema *Wie entsteht ein See?* — Stock- und
eigenes Footage, synchronisiert zum deutschen Voiceover, unter einem eigenen
Song, mit warmem (dezentem) Röhrenfernseher-Grade und modernen gelben Untertiteln.

**Output:** [`out/see_hook_16x9.mp4`](out/see_hook_16x9.mp4) — 1920×1080, 30 fps, ~28.9 s

Aktueller Build: **`scripts/build_hook_v2.py`** (v1 = `scripts/build_hook.py`, archiviert).

## Aufbau der Hook

| Zeit (T) | Bild | Ton / Text |
|----------|------|------------|
| 0.0–6.0 | Vögel überm See (eigenes Footage) | nur Song |
| ~6.75 | Vögel laufen weiter | VO startet: „Das ist ein See." |
| ~8.6 | **Überblendung** in den Bergsee (Pexels) | „…das ist auch ein See." |
| 11.6 | Pfützen-Spiegelung | „Aber das … kein See." |
| 14.3 | Tal aus der Luft | „drei Orte … 2 km …" |
| 18.0 | **Mr. Bean #1** (Feld) | „…voneinander entfernt sind" |
| 20.2 | Wolken über Bergen | „…gleichen Witterungsbedingungen…" |
| 24.2 | **Mr. Bean #2** | „Wie kann das sein?" |
| 25.7 | See schrumpft auf weißen Hintergrund | Outro-Card: **„Seen oder geseen werden"** |

## Look & Stil

- **Format:** 16:9 (1920×1080).
- **Grade:** warmer Röhrenfernseher, aber **dezent** — reduzierte Farbtemperatur
  (5200 K, mix 0.65), leichte Scanlines, milde Röhren-Wölbung, Bloom, dezente
  chromatische Aberration, Vignette, analoges Rauschen.
- **Untertitel:** **modern, crisp, gelb** (Liberation Sans / Helvetica), als
  Overlay **über** dem Grade gerendert — damit brechen sie den Retro-Look
  bewusst auf. Kein Karaoke mehr, phrasenweise mit sanftem Fade.
- **Outro:** cleaner weißer Hintergrund, das See-Video schrumpft in einen
  Rahmen, darüber groß in Helvetica das Wortspiel „Seen oder geseen werden".
- **Ton:** eigener Song unter dem ganzen Clip (Intro laut, unter dem VO
  geduckt), Voiceover on top, Limiter gegen Clipping.

## Neu bauen

```bash
# 1. Pexels-Footage holen (einmalig)
PEXELS_KEY=xxxxx python3 scripts/fetch_footage.py

# 2. Hook rendern (v2). Cached Zwischenschritte werden übersprungen;
#    FORCE=1 erzwingt kompletten Rebuild.
python3 scripts/build_hook_v2.py
```

Voraussetzungen: `ffmpeg` (mit libass + libx264 + fontconfig), `curl`, `python3`.
Hinweis: der genutzte statische ffmpeg-Build hat **kein** `drawtext` (harfbuzz
fehlt) — sämtliche Textelemente laufen daher über **libass** (`ass`-Filter).

## Assets

- `audio/voiceover.wav` — Sprecheraufnahme
- `audio/song.mp3` — Musikbett (eigenes)
- `audio/transcript.json` — WhisperX Word-Transkript (Caption-Timings)
- `user_footage/birds.mp4` — Vögel-Intro · `mrbean.mp4` — Mr. Bean · `lake_bikes.mp4`
- `assets/` — Pexels-Clips (nicht eingecheckt, siehe `fetch_footage.py`)
- `build/` — Zwischenschritte (`captions_v2.ass`, `outro_text.ass`, `main_graded.mp4`, …)
- `CREDITS.md` — Footage-Attribution

## Hinweise

- Mr. Bean und der Song sind vom Nutzer bereitgestellt (Mr. Bean © Tiger
  Aspect/Rowan Atkinson — nur zur nutzerseitigen Verwendung).
- Die Swimming-GIFs aus dem Upload werden aktuell nicht verwendet (Inhalt liegt
  hinter dem 22-s-Hook).
