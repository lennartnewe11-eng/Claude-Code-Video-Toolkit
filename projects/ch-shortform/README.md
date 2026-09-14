# c.h. Shortform — 9:16 Edit

Beatsynchroner Edit auf schwarzem Grund. Jeder Clip sitzt in einem eigenen
Seitenverhältnis-Band, der 1080×1920-Rahmen bleibt stehen — dadurch wirkt es,
als wechsle das Format des Videos selbst.

**Status: Akt 1 gebaut** (34,18 s, 49 Shots). Akt 2 und 3 sind geplant, aber noch nicht gerendert.

## Musik

`Deceptacon` — Le Tigre. 161,5 BPM, Beat = 0,3715 s (Raster über 493 Beats
gemessen, Streuung 9,8 ms — der Track läuft also wirklich auf einem festen Raster).

Der Song hat zwei echte Breakdowns, in denen der Bass wegfällt (−8 dB auf
−17,5 dB): bei 110,0 s und 160,4 s. Das Musikbett nutzt den ersten davon als
Vibe Shift und braucht dafür genau **einen** Schnitt:

| Akt | Video | Musik (Original) | Takte | Funktion |
|-----|-------|------------------|-------|----------|
| 1 — Aufbruch | 0 – 34,18 s | 1,16 – 35,34 s | 23 | volle Energie |
| 2 — Vibe Shift | 34,18 – 46,07 s | 109,65 – 121,53 s | 8 | Bass weg |
| 3 — Zusammenrücken | 46,07 – 71,33 s | 121,53 – 146,79 s | 17 | Drop, Bass zurück |

Der Schnitt bei 34,18 s springt von Beat 95 auf Beat 295. Beide liegen auf dem
Raster und (295−95) ist durch 4 teilbar — damit bleibt die Taktphase erhalten
und der Übergang ist rhythmisch nahtlos. Akt 2→3 ist gar kein Schnitt, das ist
der originale Drop des Songs.

Programmierter Aussetzer: **44,58 – 46,07 s** komplett stumm (ein Takt vor dem
Drop) — für „leere Spielplätze, ohne Hintergrundmusik kurze Stille“ aus dem Skript.
`music_bed.py` rechnet das aus der Aktstruktur aus, es bleibt also richtig,
während Akt 1 weiter wächst.

> Der Track ist für diesen Test nicht lizenziert. Für eine Veröffentlichung
> braucht es eine Sync-Lizenz oder einen anderen Song.

## Pipeline

```bash
python3 build/fetch_sources.py          # NASA + Prelinger
python3 build/fetch_extra.py            # Wikimedia Commons, Werbespots, Nutzerclip
python3 build/phones.py                 # Größenvergleich-Grafiken erzeugen
python3 build/music_bed.py              # Musikbett mit Splice und Aussetzer
python3 build/render.py edl/act1.json act1   # Shots einzeln rendern
python3 build/qc.py     edl/act1.json act1   # Helligkeit je Shot prüfen
python3 build/assemble.py act1 build/act1_slots.ass   # concat + Korn + Musik
```

| Datei | Zweck |
|-------|-------|
| `build/looks.py` | Formatbänder, Grades, Zoom-/Schüttel-Ausdrücke |
| `build/render.py` | EDL → einzelne Shots (ein ffmpeg-Aufruf pro Shot) |
| `build/captions.py` | ASS-Typo (libass; `drawtext` fehlt in diesem ffmpeg-Build) |
| `build/qc.py` | misst Helligkeit **innerhalb des Bands**, nicht über den ganzen Rahmen |
| `build/phones.py` | erzeugt den Größenvergleich (alle Geräte auf demselben Mittelpunkt) |
| `edl/act1.json` | die eigentliche Schnittliste |
| `docs/akt1_shotliste.md` | Shotliste, offene Slots, Quellennachweis |

## Formatbänder

`strip` 3:1 · `slab` 4:1 · `cinema` 2.39:1 · `wide` 16:9 · `classic` 4:3 ·
`square` 1:1 · `half` 9:8 · `portrait` 3:4 · `full` 9:16 · `tv` 4:3 klein ·
`mini` 4:3 sehr klein

`fx: ["open"]` bzw. `["close"]` lässt das Band selbst auf- oder zufahren.

## Eigene Clips einsetzen

In `edl/act1.json` beim betreffenden Shot `"src"` auf den Dateinamen setzen
(ohne Endung). Bewegtbild kommt aus `assets/source/*.mp4`, generierte
Standbilder aus `assets/generated/*.png` — bei Standbildern entfällt `src_in`:

```json
{"beat_in":52, "beats":2, "src":"mein_clip", "src_in":3.4,
 "band":"wide", "grade":"punchy", "fx":["punch","rgbhit"]}
```

Dann `render.py` und `assemble.py` erneut laufen lassen. Die Beatstruktur bleibt,
solange `beat_in` und `beats` unverändert sind.

## Quellen

Gemischt: gemeinfrei (NASA, Prelinger, Kongressansprache), CC BY / CC BY-SA
(Mauerfall, Reagan — Namensnennung nötig) und Werbespots ohne Lizenzangabe
(GTE, Nokia — Rechte bei den Markeninhabern). Vollständige Aufstellung in
`docs/akt1_shotliste.md` und `assets/source/CREDITS.json`.

Ausdrücklich **nicht** verwendet: `America in Turmoil` (1967), ein Film der
rechtsextremen *Liberty Lobby*. Details in der Shotliste.
