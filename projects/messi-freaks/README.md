# Messi — auf „Freaks“ (16:9, für TikTok)

2:24, 1920×1080, 50 fps. Das Messi-Edit (`../messi-edit`, v3) neu geschnitten auf
„Freaks“ von Surf Curse: gleiche Storyline, im Wesentlichen dieselben Clips,
dasselbe Schnitt-Vokabular (Bänder, Grades, FX, Gesichter-Reihe), gleiches Format.

## Für TikTok

Das Video ist so gebaut, dass der Song aus der TikTok-Bibliothek darunterpasst:

- **Start bei 0:00.** Der erste Gitarrenanschlag liegt im Video bei 0,06 s, also
  praktisch auf dem ersten Frame. In TikTok den Originalton auf 0 und „Freaks“
  ab dem Anfang wählen.
- **Nur der Song**, kein Stadionton, keine Absenkung (anders als im Messi-Edit):
  was in der Datei zu hören ist, ist genau das, was auf TikTok läuft.
- Geschnitten auf die hochgeladene Aufnahme (2:22 Musik). Die Studioversion ist
  mit 2:27 angegeben; ist die TikTok-Version eine andere (schneller/langsamer),
  laufen Bild und Musik auseinander.

## Dramaturgie

Der Song läuft **an einem Stück**. Ausgabe-Beat k = Achtel des Songs.

| Ausgabe-Beats | Zeit | Song | Inhalt | Grade |
|---|---|---|---|---|
| 0–56 | 0:00–0:19 | Intro (Gitarre) | Rosario, La Masia, erstes Profitor mit Ronaldinho | faded |
| 56–120 | 0:19–0:40 | Strophe 1 | Barça: Getafe, Rom, Wembley, Ballon d'Or, Iran-Tor 2014, Bayern, Bilbao, Bernabéu, Paris | warm |
| 120–176 | 0:40–0:59 | Refrain 1 | Niederlagen: Elfmeter und Tränen 2016, Anfield 2019; die Copa 2021; Abschied aus Barcelona; Saudi-Arabien 2022 | cold / bleak |
| 176–240 | 0:59–1:20 | Zwischenteil | **WM-Finale 2014 ↔ 2022**, ruhig: Tunnel, Einlauf, Hymne, Anpfiff | cold ↔ warm |
| 240–296 | 1:20–1:39 | Strophe 2 | 2014 ↔ 2022 im Spiel, Wechsel wird schneller; Montiels Elfmeter **auf dem zweiten Refrain im Netz** | cold ↔ warm |
| 296–352 | 1:39–1:58 | Refrain 2 | Weltmeister: Golden Ball und Pokal 2014 ↔ 2022, Bisht, Pokal, Vermächtnis-Wand | warm |
| 352–380 | 1:58–2:07 | Outro | MetLife 2026 | cold / bleak |
| 380–416 | 2:07–2:19 | Outro | **Gesichter über die Jahre**: Baby → 2026 | mono |
| Coda | 2:19–2:24 | Ausklang | Abgang in den Tunnel, Titel | bleak |

**2014 ↔ 2022.** Harte Schnitte hin und her, nie beide gleichzeitig: 2014 immer
im Scope-Band und kalt, 2022 immer im Vollbild und warm. Der Wechsel wird
schneller: Achter im ruhigen Zwischenteil, Vierer, Zweier, eine Einer-Traube,
dann bei Montiels Anlauf der Split, in dem 2022 die 2014er Hälfte aus dem Bild
schiebt.

**Was gegenüber v3 neu ist** (der Song ist 40 s länger): die Kindheit im Intro
(Rosario, La Masia, erstes Tor), das Iran-Tor 2014, der Ballon d'Or in
Großaufnahme, die Copa 2021 und Saudi-Arabien 2022 zwischen den Niederlagen,
und im Finale mehr Momente beider Spiele (Messis Elfmeter 2022, Mbappé,
Götze, Messi nach dem Freistoß).

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # Chunks je Shot
python3 review.py 0-37 build/rv.jpg                # framegenaue Durchsicht
python3 stillcheck.py 0-137                        # kein Standbild am Shot-Anfang
python3 deliver.py --name messi_freaks_1080p.mp4   # Master + Lieferfassung (28,5 MB)
python3 shotliste.py > SHOTLISTE.md
```

`media/` (Footage, Song, Fonts) liegt nicht im Repo; es ist dasselbe Material
wie im Messi-Edit plus `src/iran14.ts` und `cuts/c21_lift.mp4`.

## Nachgemessen

- **Achtel statt Viertel.** „Freaks“ läuft auf ~89,6 BPM; ein Viertel (0,67 s)
  ist doppelt so lang wie ein Beat im Messi-Song. Die Gitarre schlägt Achtel
  (0,334 s), und die sind fast genau so lang wie der alte Beat (0,37 s). Auf
  Achteln geschnitten bleiben Zweierschnitte, Einer-Trauben und Vierer-Pausen
  dieselben. Das Tempo schwankt leicht (88–91 BPM, Band ohne Klick), deshalb
  eine echte Beat-Map, Rest-Jitter 8 ms.
- **Takt-Eins** aus Akkord- und Basswechseln: beide liegen je Takt auf dem
  Wechsel von der vierten auf die erste Zählzeit, die Eins fällt auf den ersten
  Anschlag.
- **Abschnitte** aus Text (Transkription) und Pegel: Gesang setzt in Takt 7 ein,
  „I'm just a freak“ in Takt 15 und 37, das ruhige „My head is…“ ab Takt 22.
- **Reaktionsvideo.** Die Copa-2016-Szenen stammen aus einem Reaktionsvideo; in
  r16_cry ist der Reagierende zwischen 5,5–12 s und 15,5–18,5 s bildfüllend. Die
  In-Punkte liegen nur in den Messi-Abschnitten, die Einblendung unten rechts ist
  jeweils weggezoomt.
- **Standbild am Shot-Anfang** behoben wie im Neymar-Edit (`-fps_mode
  passthrough`); `stillcheck.py` prüft jeden Shot.
