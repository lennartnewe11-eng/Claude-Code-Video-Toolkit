# Messi — Karriere-Edit (16:9)

v2: 89,7 s, 1920×1080, 50 fps. Ganze Karriere von Rosario bis MetLife 2026; große
Niederlagen und große Erfolge stehen gegeneinander. Geschnitten nach den Regeln
aus `erkenntnisse.md` (Raster aus absoluter Zeit, Zweierpuls mit
Einzelbeat-Trauben und Vierer-Atempausen, seltene laute Effekte, Grades tragen
den Umschlag, Band steht still, wo der Inhalt die Veränderung trägt).

## Dramaturgie

Der Song läuft **an einem Stück**, Song-Beat 416 bis zum letzten Schlag (647),
ohne Splice. Ausgabe-Beat k = Song-Beat − 416.

| Ausgabe-Beats | Song-Beats | Teil | Inhalt | Grade |
|---|---|---|---|---|
| 0–32 | 416–448 | Breakdown | Rosario, La Masia, Barça 2005–2017 | faded → warm |
| 32–40 | 448–456 | Build | Niederlagen 2016, 2019, 2021 | cold / bleak |
| 40–96 | 456–512 | Build | **Parallelmontage WM-Finale 2014 \| 2022** | cold \| neutral |
| 96–160 | 512–576 | Refrain | Weltmeister; Golden Ball und Pokal 2014 ↔ 2022; Vermächtnis-Wand | warm |
| 160–196 | 576–612 | Refrain | MetLife 2026, 2016 ↔ 2026, Triptychon der drei Pokal-Begegnungen | cold / bleak |
| 196–231 | 612–647 | Outro | **Gesichter über die Jahre**: Baby → 2026 | mono |
| Coda | Ausklang | — | Nachhall, Stadion, Abgang in den Tunnel, Titel | bleak |

**Parallelmontage (k 40–96).** Zwei Finals, Moment für Moment nebeneinander:
Tunnel · Einlauf am Pokal vorbei · Hymne · Messis Chance (vorbei | drin) ·
Reaktion · Gegentor (Götze entscheidet | Mbappé gleicht aus) · letzte Chance
(Freistoß drüber | Martínez hält) · Schlusspfiff | Elfmeterschießen · Messi
allein | Montiel läuft an. Die Clips laufen durch, auf jedem Beat springt nur
die Trennlinie. Sie wandert zu der Seite, die den Moment hat; bei Montiels
Elfmeter schiebt 2022 das Jahr 2014 aus dem Bild.

**Gesichter (k 196–231).** Vierzehn Nahaufnahmen, einmal je Clip vermessen
(`faces.py`), auf gleiche Höhe und gleichen Ort gebracht. Das Band steht
still, nur das Gesicht altert. Jahreszahlen nur dort, wo das Jahr belegt ist
(Spielaufnahmen); die Kindheitsfotos bleiben ohne Zahl.

**Musik.** Vor dem Refrain wird der Song zwei Beats lang abgesenkt, nicht
stumm geschaltet; darüber das Stadion bei Montiels Elfmeter, der Jubel landet
exakt auf Song-Beat 512. Nach dem letzten Schlag: natürlicher Ausklang,
Nachhall aus dem letzten Schlag, leiser Stadion-Teppich (Clean Feed 2014, ohne
Kommentar), Ausblendung — kein harter Stopp mehr.

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # build/messi_edit_master.mp4
python3 review.py 0-21 build/rv.jpg                # framegenaue Durchsicht
python3 shotliste.py > SHOTLISTE.md
python3 deliver.py --name messi_edit_v2_1080p.mp4  # Master + Lieferfassung (28,5 MB), Sync-Prüfung
```

`media/` (Footage, Song, Fonts) liegt nicht im Repo.

| Datei | Aufgabe |
|---|---|
| `beatmap.py` | Beat-Tracking mit zeitvariablem Tempo, Takt-Eins-Index |
| `timeline.py` | Song-Beats → Ausgabe-Beats → Frames (`kf(k) = round(T(k)·fps)`) |
| `audio.py` | Musikbett am Stück, Absenkung vor dem Refrain, Stadionton, Nachhall-Coda |
| `edl.py` | alle Shots in Ausgabe-Beats |
| `faces.py` | Gesicht je Clip vermessen (Median, Ausreißer verworfen), Cache in `build/faces.json` |
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
- **Gesichtserkennung braucht Kontrolle.** Die Haar-Kaskade fand bei 2010 Sepp
  Blatter statt Messi, bei der Copa 2021 einen Mitspieler, bei 2014 einen
  Fotografen. Jede Box wurde deshalb eingezeichnet und angesehen
  (`facecheck`), falsche Quellen ersetzt, drei Gesichter von Hand gesetzt.
- **OpenCV 5 hat die Haar-Kaskaden entfernt.** `faces.py` läuft mit OpenCV
  4.10; `fetch.py` holt die Kaskaden-Dateien aus dessen Wheel.
