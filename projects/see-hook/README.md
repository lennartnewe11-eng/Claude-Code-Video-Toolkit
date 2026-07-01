# "See" — Video-Hook (Röhrenfernseher-Look)

Cinematische ~22-Sekunden-Hook zum Thema *Wie entsteht ein See?*, gebaut aus
Stock-Footage, synchronisiert zum deutschen Voiceover und in einen warmen
Retro-CRT-Look gebracht.

**Output:** [`out/see_hook_16x9.mp4`](out/see_hook_16x9.mp4) — 1920×1080, 30 fps, 22.7 s

## Look & Stil

- **Format:** 16:9 (1920×1080)
- **Grade:** warmer alter Röhrenfernseher — Farbtemperatur ~4600 K, angehobene
  Rot-/gesenkte Blaukurve, Sättigung +, Bloom/Glühen, chromatische Aberration,
  Röhren-Wölbung (`lenscorrection`), Scanlines, Vignette, analoges Rauschen.
- **Untertitel:** gelbe Helvetica (Liberation Sans, metrisch Helvetica-kompatibel),
  **kinetisch word-synced** als Karaoke-Sweep — gesprochenes Wort hell-gelb,
  kommende Wörter gedämpft (Bernstein). Timings aus dem WhisperX-Word-Transkript.

## Schnitt / Shot-Liste (Timeline)

| # | Zeit | Text | Footage |
|---|------|------|---------|
| A | 0.0–2.6 | „Das ist ein See." | Bergsee, Luftaufnahme |
| B | 2.6–5.6 | „auch ein See." | Waldsee, Spiegelung |
| C | 5.6–8.3 | „kein See." | Pfützen-Spiegelung |
| D | 8.3–12.3 | „drei Orte … 2 km" | Tal / Dörfer aus der Luft |
| E | 12.3–15.1 | „gleiche Erhebung" | Hochebene |
| F | 15.1–18.2 | „Witterungsbedingungen" | Wolken über Bergen |
| G | 18.2–19.7 | „Wie kann das sein?" | Nebelsee, düster |
| H | 19.7–22.7 | „sehen und gesehen werden" | See im Sonnenuntergang |

## Neu bauen

```bash
# 1. Footage von Pexels holen (API-Key als Env-Var)
PEXELS_KEY=xxxxx python3 scripts/fetch_footage.py

# 2. Schnitt + Captions + CRT-Grade rendern
python3 scripts/build_hook.py
```

Voraussetzungen: `ffmpeg` (mit libass, libx264, fontconfig), `curl`, `python3`.

## Assets

- `audio/voiceover.wav` — Sprecher-Aufnahme (Original)
- `audio/transcript.json` — WhisperX Word-Level-Transkript (Timings für Captions)
- `assets/` — rohe Pexels-Clips
- `fonts/Anton-Regular.ttf` — optionaler Display-Font (aktuell nutzen die Captions Helvetica/Liberation Sans)
- `build/` — Zwischenschritte (`captions.ass`, `scanlines.png`, `base.mp4`, …)
- `CREDITS.md` — Footage-Attribution (Pexels)

## Hinweise

- Eigenes Footage lässt sich einbinden, indem eine Datei in `assets/` unter dem
  Shot-Namen (`A_lake1_*.mp4` …) abgelegt und im Manifest referenziert wird; der
  Build normalisiert automatisch auf 1080p30.
- Zusätzliche Public-Domain-Quellen (archive.org) sind vorbereitet, wurden aber
  nicht benötigt — Pexels lieferte alle acht Shots in HD.
