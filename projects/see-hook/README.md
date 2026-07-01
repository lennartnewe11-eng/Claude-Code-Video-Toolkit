# "See" — Video-Hook

Cinematische ~30-Sekunden-Hook zum Thema *Wie entsteht ein See?* — Stock- und
eigenes Footage, synchronisiert zum deutschen Voiceover, unter einem eigenen
Song, mit warmem (dezentem) Röhrenfernseher-Grade und modernen gelben Untertiteln.

**Output:** [`out/see_hook_16x9.mp4`](out/see_hook_16x9.mp4) — 1920×1080, 30 fps, ~30.3 s
(komprimiert: `see_hook_1080p_web.mp4` ~13 MB, `see_hook_web.mp4` 720p ~4 MB)

Aktueller Build: **`scripts/build_hook_v3.py`** (v1/v2 archiviert).

## Aufbau der Hook

| Zeit (T) | Bild | Ton / Text |
|----------|------|------------|
| 0.0–6.0 | Vögel überm See (eigenes Footage) | nur Song |
| ~6.75 | Vögel laufen weiter | VO startet: „Das ist ein See." |
| ~8.6 | **Überblendung** in den Bergsee (Pexels) | „…das ist auch ein See." |
| 11.6 | **Leerer Stausee** (Vertiefung ohne Wasser) | „Aber das … kein See." |
| 14.3 | Tal aus der Luft | „drei Orte … 2 km …" |
| 18.0 | **Mr. Bean #1** (Feld) | „…voneinander entfernt sind" |
| 20.2 | Wolken über Bergen | „…gleichen Witterungsbedingungen…" |
| 24.2 | **Mr. Bean #2** | „Wie kann das sein?" |
| 25.7 | See **fährt animiert** aus Vollbild in kleinen Rahmen auf Weiß | Outro: schwarzes, quer über den Screen animiertes **„Seen oder geseen werden"** |
| 28.6 | Schluss-See mit Fahrrädern (eigenes Footage) | „Wie entsteht eigentlich ein See?" |

## Intro (separate ~12 s, kommt zwischen Hook und Hauptteil)

**Output:** [`out/intro.mp4`](out/intro.mp4) — Build: `scripts/make_intro.py`

- Hintergrund: das hochgeladene Feld-Video, weichgezeichnet + hell gewaschen
  und leicht warm gegradet.
- Vordergrund: die Bleistift-Zeichnung wird **Strich für Strich** aufgebaut —
  Reveal entlang einer geodätischen „Zeichen-Reihenfolge" (der Stift läuft von
  der Vase an den Stängeln hoch zu den Blüten). Umgesetzt in Python
  (numpy/Pillow BFS über die Alpha-Maske → PNG-Sequenz → Overlay).
- Unten rechts in Helvetica: „eine Past.Present.Future. Produktion".

## Look & Stil

- **Format:** 16:9 (1920×1080).
- **Grade:** warmer Röhrenfernseher, aber **dezent** — reduzierte Farbtemperatur
  (5200 K, mix 0.65), leichte Scanlines, milde Röhren-Wölbung, Bloom, dezente
  chromatische Aberration, Vignette, analoges Rauschen.
- **Untertitel:** **modern, klein, gelb, ohne schwarze Umrandung** — stattdessen
  weicher **Leucht-/Glow-Effekt** (libass `\blur`), als Overlay über dem Grade
  (bricht den Retro-Look auf). Kein Karaoke, phrasenweise mit Fade.
- **Outro:** das See-Video **animiert** aus Vollbild in einen zentrierten Rahmen
  auf weißem Grund (zeitbasierter `scale`), darüber das Wortspiel
  **„Seen oder geseen werden"** in **schwarz**, wortweise kreativ über den
  ganzen Screen (auch übers Video) animiert — bricht bewusst mit dem Untertitel-Format.
- **Ton:** eigener Song unter dem ganzen Clip (Intro laut, unter dem VO
  geduckt), Voiceover on top, Limiter gegen Clipping.

## Neu bauen

```bash
# 1. Pexels-Footage holen (einmalig)
PEXELS_KEY=xxxxx python3 scripts/fetch_footage.py

# 2. Hook rendern (v3). Cached Zwischenschritte werden übersprungen;
#    FORCE=1 erzwingt kompletten Rebuild.
python3 scripts/build_hook_v3.py
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
