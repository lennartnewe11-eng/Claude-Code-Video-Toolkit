# Ronaldo & Nani — Manchester United × „Blame“

Edit der besten Tore und Highlights von Cristiano Ronaldo und Nani bei Manchester
United, geschnitten auf „Blame“ (Calvin Harris feat. John Newman). 16:9, 1920×1080,
50 fps, 89,16 s. Fast ausschließlich Spielszenen, Text nur als kleine Torangabe.

Die Schnittregeln stammen aus den Erkenntnissen aus Akt 1 (Raster, Leseeinheiten,
Bewegung statt Schnitt, Effektkurve, nachsehen statt erinnern); wie sie hier
angewendet werden, steht unten.

## Status

Die Pipeline steht und ist gegen synthetische Testclips geprüft (Timing, Anker,
Ton-Sync). **Es fehlt noch das Spielmaterial**: YouTube lässt aus der
Cloud-Umgebung keine Videodaten zu (403), deshalb gibt es `build/fetch.sh` für
einen normalen Rechner. Die Quell-Zeitpunkte in `build/edl.py` sind Platzhalter,
bis jeder Clip auf einem Contact Sheet angesehen wurde.

## Musik

`build/grid.py` misst das Raster statt es anzunehmen: 127,872 BPM, ein Beat =
0,46922 s, Beat 0 bei 0,5614 s. Die Kicks liegen im Mittel 2 ms neben dem Raster
(Streuung 8 ms). Verwendet wird Beat 248 bis 438:

| Beats | Teil | Inhalt |
|---|---|---|
| 248–256 | Build | Intro, Einzelbeats in den Drop |
| 256–288 | Drop 2 | **Ronaldo**: Porto, Arsenal-Freistoß, Portsmouth-Freistoß, Roma, Moskau |
| 288–352 | Breakdown | **Nani**, kalter Grade, Zeitlupe, 8-Beat-Einheiten |
| 352–368 | Build | Splitscreen Ronaldo \| Nani, Layout springt auf jedem Beat; 366 ist der stille Beat → schwarz |
| 368–432 | Drop 3 | beide im Wechsel, warmer Grade; 396–399 Bass-Pause → vier Einzelbeats |
| 432–438 | Outro | letztes Bild, Abblende |

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
pip install librosa numpy opencv-python-headless pillow yt-dlp   # + ffmpeg
cp <song>.mp3 media/blame.mp3
./build/fetch.sh                          # Quellen → media/src/ (auf einem normalen Rechner)
python3 build/grid.py media/blame.mp3     # Raster → build/grid.json
python3 build/contact.py src r_porto 0 12 0.25   # Clip ansehen, Anker setzen
python3 build/render.py                   # → out/edit_video.mp4 (--half, --from/--to für Vorschau)
python3 build/contact.py edit out/edit_video.mp4
python3 build/deliver.py --mb 60          # Ton auf dem Raster, 2-Pass → out/ronaldo_nani_blame.mp4
python3 build/shotliste.py                # SHOTLISTE.md
```

`media/` und `out/` sind nicht im Repo (Song und Spielszenen).

## Dateien

| Datei | Zweck |
|---|---|
| `build/grid.py` | Beat-Raster aus den Kicks messen → `grid.json` |
| `build/edl.py` | die Schnittliste: Shots, Anker, Rampen, fx, Texte |
| `build/render.py` | Bild für Bild rendern (Grades, Zoom-Pulse, Splitscreen, Text) |
| `build/deliver.py` | Song auf dem Raster schneiden, muxen, 2-Pass auf Zielgröße |
| `build/contact.py` | Contact Sheets für Quellen und Schnitt |
| `build/shotliste.py` | `SHOTLISTE.md` aus der EDL |
| `build/sources.txt`, `build/fetch.sh` | Quellen-Liste und Download |
| `assets/fonts/` | Anton, Bebas Neue, Oswald (OFL) |
