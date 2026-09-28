# Messi — Karriere-Edit (16:9)

86 s, 1920×1080, 50 fps. Ganze Karriere von Rosario bis MetLife 2026; große
Niederlagen und große Erfolge stehen gegeneinander. Geschnitten nach den
Regeln aus `erkenntnisse.md` (Raster aus absoluter Zeit, Splice-Regel,
Zweierpuls mit Einzelbeat-Trauben und Vierer-Atempausen, seltene laute
Effekte, Grades tragen den Umschlag).

## Dramaturgie

| Ausgabe-Beats | Song-Beats | Teil | Inhalt | Grade |
|---|---|---|---|---|
| 0–16 | 16–32 | Intro | Kindheit, La Masia, erstes Tor 2005 | faded, 4:3 |
| 16–64 | 32–80 | Drop | Barça: Getafe 07, Rom 09, Wembley 11, Boateng/Bilbao 15, Bernabéu 17 | warm |
| 64–96 | 96–128 | ohne Hi-Hats | 2014 Maracanã, 2016 MetLife, Anfield 19, Abschied 21 | cold / bleak |
| 96–128 | 480–512 | Build | Copa 2021, Saudi-Arabien 22, Finale 22 bis Montiels Elfmeter | warm → bleak |
| 128–192 | 512–576 | Refrain | Weltmeister; Diptychen 2014 ↔ 2022; Vermächtnis-Wand | warm |
| 192–231 | 608–647 | Outro | MetLife 2026, Diptychon 2016 ↔ 2026, Triptychon, Abgang | cold / bleak |

Drei Musik-Splices (80→96, 128→480, 576→608), alle `(b − a) % 4 == 0`.
Programmierter Aussetzer: die zwei Beats vor dem Refrain ist die Musik stumm,
man hört nur das Stadion bei Montiels Elfmeter — der Jubel landet exakt auf
dem ersten Refrain-Beat (aus der Segmentstruktur gerechnet, `audio.py`).

**Gegenüberstellung statt Erklärung:** 2014 Golden Ball (Hand vor dem Mund) |
2022 Golden Ball (Arme hoch). 2014 der Gang an der Siegerehrung vorbei | 2022
der Kuss auf den Pokal. 2016 MetLife | 2026 MetLife. Am Ende alle drei
Begegnungen mit dem Pokal als Triptychon.

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # build/messi_edit_master.mp4
python3 review.py 0-21 build/rv.jpg                # framegenaue Durchsicht
python3 shotliste.py > SHOTLISTE.md
python3 deliver.py --mb 48                         # Master + Lieferfassung, Sync-Prüfung
```

`media/` (Footage, Song, Fonts) liegt nicht im Repo.

| Datei | Aufgabe |
|---|---|
| `beatmap.py` | Beat-Tracking mit zeitvariablem Tempo, Takt-Eins-Index |
| `timeline.py` | Song-Segmente → Ausgabe-Beats → Frames (`kf(k) = round(T(k)·fps)`) |
| `audio.py` | Musikbett mit Splices, Aussetzer, Stadionton |
| `edl.py` | alle Shots in Ausgabe-Beats |
| `render.py` | Bänder, Grades, FX, Grid-Anordnungen, Labels; Chunks je Shot |
| `review.py`, `contact.py` | Kontrollbögen aus den gerenderten Chunks |
| `fetch.py` | Quellen (Archive-Items, Zeitstempel) |
| `deliver.py` | Master (CRF) und Lieferfassung (2-Pass auf Zielgröße), Prüfung am fertigen File |

## Neu gemessen

- **Das Tempo ist nicht konstant.** Der Track beginnt bei 161,5 BPM (wie in
  `erkenntnisse.md`), zieht aber auf ~169 BPM an. Ein starres 0,3715-s-Raster
  läge nach einer Minute mehrere Beats daneben. Deshalb eine echte Beat-Map;
  die Regel „Grenzen aus absoluter Zeit“ bleibt, nur die Zeiten kommen aus der
  Messung. Onsets liegen über alle Splices auf ±12 ms.
- **Kontaktbögen per `fps`-Filter beschriften falsch.** Das erste Werkzeug lag
  0,5–0,75 s daneben; 20 In-Punkte zeigten dadurch Vorgänger-Szenen. Seitdem
  werden Frames per Index gezogen und jeder Shot aus dem gerenderten Chunk
  geprüft (`review.py`).
- **Der Vorlauf fehlte im Bild.** Beat 0 liegt 0,4 s nach Songbeginn; gerendert
  wurde erst ab Beat 0, das Bild lief also 20 Frames vor der Musik. Aufgefallen
  nur, weil die Framezahl des Masters gegen die Erwartung geprüft wurde. Jetzt
  verlangt `render.check()` lückenlose Abdeckung ab Frame 0, und `deliver.py`
  misst den Sync am fertigen File (Weißblitz im Bild gegen Jubel im Ton am
  Refrain-Einsatz).
