# Ronaldo & Nani — Manchester United × „Blame“

Edit der besten Tore und Highlights von Cristiano Ronaldo und Nani bei Manchester
United, geschnitten auf „Blame“ (Calvin Harris feat. John Newman). 16:9, 1920×1080,
50 fps, 89,16 s. Fast ausschließlich Spielszenen; Text nur als Namenstitel am Anfang und Abspann.

Die Schnittregeln stammen aus den Erkenntnissen aus Akt 1 (Raster, Leseeinheiten,
Bewegung statt Schnitt, Effektkurve, nachsehen statt erinnern); wie sie hier
angewendet werden, steht unten.

## Quellen

Alle Szenen stammen aus Mitschnitten auf archive.org, keine YouTube-Downloads
(von dort lässt YouTube aus der Cloud-Umgebung keine Videodaten zu):

| Quelle | Inhalt | verwendet für |
|---|---|---|
| CL-Finale 2008 (ITV, 720p) | Vollspiel | Ronaldos Kopfball in Moskau, Jubel |
| CL-VF Roma–United 2008 (MUTV, 1080p) | Vollspiel | Flugkopfball |
| CL-HF Arsenal–United 2009 (ITV, 576p) | Vollspiel | Freistoß aus 40 m, Konter mit Hackentrick |
| PL United–City 2010/11 (Sky, 720p) | Vollspiel | Nanis Tor, Salto, Flanke zu Rooneys Fallrückzieher |
| PL United–Arsenal 2011/12, 2. HZ (576p) | Halbzeit | Nanis Lupfer beim 8:2 |
| Premier League Years 06/07, 07/08, 08/09 (1080p) | Saisonrückblicke | Fulham 2007, Portsmouth-Freistoß, Nani gegen Spurs und Boro, City-Freistoß 2009 |
| Premier League Years 10/11, 11/12 (1080p) | Saisonrückblicke | City 2011 in HD (Nanis Tor, Fallrückzieher), Nanis Jubel beim 8:2 |

`build/archive_sources.txt` nennt die Dateien, `build/segments.txt` die
Ausschnitte. Ganze Spiele werden nie komplett geladen: ffmpeg springt per
HTTP-Range an die Stelle. Die Saisonrückblicke (je 2,7 GB) liegen lokal, weil
`build/ply_index.py` sie einmal ganz durchläuft und die Spiel-Einblendungen
per Texterkennung zu einem Inhaltsverzeichnis macht (`build/ply_index/`).

Senderlogos und Spielstände werden je Quelle weggeschnitten (`CROP` in
`build/edl.py`, gleiche Breite und Höhe, damit 16:9 bleibt). TV-Bauchbinden
lassen sich so nicht entfernen, die Schnitte weichen ihnen aus.

## Auflösung

Wo es eine Szene auch in einem 1080p-Saisonrückblick gibt, kommt sie von dort.
Was nur als 576p/720p-Mitschnitt existiert, rechnet `build/upscale.py` mit
Real-ESRGAN (`realesr-general-x4v3`, BSD-3) auf der CPU hoch: Crop, 4×, dann
flächengemittelt auf 1920×1080. Nur die Bilder, die der Schnitt wirklich liest,
gehen durchs Netz (~8 s je 576p-Bild, ~13 s je 720p-Bild); das Ergebnis
`<key>_ai.mp4` hat dieselbe Zeitachse und wird von `render.py` automatisch
bevorzugt. Die Gewichte liegen in `media/models/` (nicht im Repo).

## Musik

`build/grid.py` misst das Raster statt es anzunehmen: 127,872 BPM, ein Beat =
0,46922 s, Beat 0 bei 0,5614 s. Die Kicks liegen im Mittel 2 ms neben dem Raster
(Streuung 8 ms). Verwendet wird Beat 248 bis 438:

| Beats | Teil | Inhalt |
|---|---|---|
| 248–256 | Build | „RONALDO 7“, „NANI 17“, dann vier Einzelbeats in den Drop |
| 256–288 | Drop 2 | **Ronaldo**: Portsmouth-Freistoß, Arsenal-Freistoß, Roma-Kopfball, Moskau-Kopfball |
| 288–352 | Breakdown | **Nani**, kalter Grade, Zeitlupe: Spurs, Boro, Vorlage zu Rooney, City, Salti |
| 352–368 | Build | Splitscreen 7 gegen 17, Layout springt auf jedem Beat; 366 ist der stille Beat → schwarz |
| 368–432 | Drop 3 | beide im Wechsel, warmer Grade: Arsenal-Konter, Nanis Lupfer, Fulham, City-Freistoß; 396–399 Bass-Pause → vier Gesichter |
| 432–438 | Outro | Ronaldo und Nani, Abblende |

Kein Musikschnitt: der Ausschnitt läuft am Stück bis zum natürlichen Songende.

## Wie die Regeln hier greifen

- **Grenzen aus absoluter Zeit**: `round((beat − 248) × 0,46922 × 50)` je Grenze.
- **Ein Beat ist keine Leseeinheit**: Tore bekommen 4–8 Beats (1,9–3,8 s).
  Einzelbeats nur für Jubel, Skills und die Bass-Pause.
- **Bewegung statt Schnitt**: in langen Tor-Shots trägt `thump` (Zoom-Puls auf
  jedem Beat, stärker auf der Eins) den Takt, der Clip läuft weiter. Im Build 3
  laufen beide Spieler durchgehend, nur das Split-Layout springt.
- **Anker statt In-Point**: `at=(Quellsekunde, Beat)` legt den Schuss auf den
  Kick; eine Geschwindigkeitsrampe (`speed`) bremst erst nach dem Treffer in die
  Zeitlupe, damit das Tor in Echtzeit lesbar bleibt.
- **Effektkurve**: `punch`, `grain` und `thump` ständig; `flash`, `rgbhit` und
  `shake` selten. Den Umschlag tragen die Grades (`base` → `cold` → `warm`).
- **Nachsehen**: `build/contact.py` für Quell-Clips und für den fertigen Schnitt
  (In, Anker, Out je Shot). `SHOTLISTE.md` wird aus der EDL erzeugt.

## Ablauf

```bash
pip install librosa numpy opencv-python-headless pillow   # + ffmpeg, tesseract
pip install torch --index-url https://download.pytorch.org/whl/cpu   # für upscale.py
cp <song>.mp3 media/blame.mp3
python3 build/grid.py media/blame.mp3          # Raster -> build/grid.json
python3 build/cut_segments.py                  # Ausschnitte -> media/src/
python3 build/cuts.py r_pompey                 # Kameraschnitte in einem Clip
python3 build/contact.py src r_pompey 22 34 0.25   # ansehen, Anker setzen
python3 build/upscale.py r_arsfk r_arscounter   # schwache Quellen -> media/src/<key>_ai.mp4
python3 build/render.py --half                 # Vorschau 960x540
python3 build/render.py                        # -> out/edit_video.mp4
python3 build/contact.py edit out/edit_video.mp4   # In / Anker / Out je Shot
python3 build/deliver.py --mb 60               # Song auf dem Raster, 2 Pässe
python3 build/shotliste.py                     # SHOTLISTE.md
```

Die Quellen laufen mit 24–30 fps, der Schnitt mit 50. Zwischenbilder rechnet
`render.py` per optischem Fluss (DIS), das trägt vor allem die Zeitlupen. An
Kameraschnitten fällt es auf das nächste echte Bild zurück.

`media/` und `out/` sind nicht im Repo (Song und Spielszenen).

## Dateien

| Datei | Zweck |
|---|---|
| `build/grid.py` | Beat-Raster aus den Kicks messen -> `grid.json` |
| `build/edl.py` | die Schnittliste: Shots, Anker, Rampen, fx, Texte, Crops |
| `build/render.py` | Bild für Bild rendern (Zwischenbilder, Grades, Zoom-Pulse, Splitscreen, Text) |
| `build/deliver.py` | Song auf dem Raster schneiden, muxen, 2-Pass auf Zielgröße |
| `build/contact.py` | Contact Sheets für Quellen, URLs und den Schnitt |
| `build/cuts.py` | Kameraschnitte in einem Quellclip finden |
| `build/cut_segments.py` | Ausschnitte aus archive.org schneiden |
| `build/ply_index.py` | Saisonrückblicke per Texterkennung indizieren |
| `build/upscale.py` | KI-Hochskalierung (Real-ESRGAN) der genutzten Bilder schwacher Quellen |
| `build/shotliste.py` | `SHOTLISTE.md` aus der EDL |
| `assets/fonts/` | Anton, Bebas Neue, Oswald (OFL) |
