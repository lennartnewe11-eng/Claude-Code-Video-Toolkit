# Messi — auf „Freaks“ (16:9, TikTok-Fassung)

0:59, 1920×1080, 50 fps. Messi auf „Freaks“ von Surf Curse, gekürzt für TikTok:
der Song läuft von 0:00 bis zum Ende des ersten Refrains, das Video endet auf
einer Takt-Eins und läuft in der TikTok-Schleife sauber ins Intro-Riff zurück.

Gegenüber der langen Fassung (2:24, Commit `7e6a660`): kürzer, weniger
Füllmaterial (Kindheit, Zeremonien, Gesichter-Reihe sind raus), dafür mehr
**Spielszenen, die man versteht**: jede läuft vom Antritt bis ins Netz, in
HD-Quellen (1080p, Barça-Szenen 720p) und nie über einen Schnitt oder eine
Blende in der Quelle hinweg. Neu sind die WM-2022-Spiele gegen Mexiko und
Kroatien aus den offiziellen FIFA-Highlights.

## Für TikTok

- **Start bei 0:00.** Der erste Gitarrenanschlag liegt im Video bei 0,06 s. In
  TikTok den Originalton auf 0 und „Freaks“ ab dem Anfang wählen; TikTok
  schneidet den Song selbst auf die Videolänge.
- **Nur der Song** in der Datei, kein Stadionton: was man hört, ist genau das,
  was auf TikTok läuft.
- Geschnitten auf die hochgeladene Aufnahme. Ist die TikTok-Version eine andere
  (schneller/langsamer), laufen Bild und Musik auseinander.

## Dramaturgie

Ausgabe-Beat k = Achtel des Songs (0,334 s).

| Beats | Zeit | Song | Inhalt | Grade |
|---|---|---|---|---|
| 0–56 | 0:00–0:19 | Intro (Gitarre) | **Barça, vier Solos**: Getafe 2007 (Mittellinie bis Netz), Bayern 2015 (Boateng fällt, Lupfer über Neuer), Bilbao 2015 (durch vier Mann), Bernabéu 2017 (Siegtor, Trikot) | warm |
| 56–97 | 0:19–0:33 | Strophe 1 | **WM 2014**: Schlenzer gegen Iran; im Finale Messis Chance vorbei, Götzes Tor, Messi am Pokal vorbei | neutral → cold |
| 97–113 | 0:33–0:38 | „I can't cover up my face“ | Copa 2016 nach dem verschossenen Elfmeter, Anfield 2019 | bleak |
| 113–120 | 0:38–0:40 | „Don't cry“ | Abschied aus Barcelona 2021 | bleak |
| 120–148 | 0:40–0:50 | Refrain 1 | **WM 2022**: Mexiko (Annahme, Schuss aus 25 m, Netz, Schrei), Kroatien (Messi gegen Gvardiol, Álvarez trifft) | warm |
| 148–176 | 0:50–0:59 | Refrain 1 | **Finale**: Martínez' Fuß in der 123. Minute, Montiels Elfmeter — **im Netz auf dem vierten „I'm just a freak“** —, Messi, der Pokal | warm |

**Knackig, aber lesbar.** Längere Szenen (Getafe, Bilbao) werden auf dem Beat in
Ausschnitte zerlegt (`RUN` in `edl.py`): die Quelle läuft ohne Sprung weiter, nur
Band und Zoom springen. So bleibt der Takt im Schnitt, ohne die Szene zu
zerhacken. Schnelle Läufe laufen mit 1,25–1,5×, sonst Echtzeit.

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # Chunks je Shot
python3 review.py 0-29 build/rv.jpg                # framegenaue Durchsicht
python3 stillcheck.py 0-29                         # kein Standbild am Shot-Anfang
python3 deliver.py --name messi_freaks_tiktok_1080p.mp4
python3 shotliste.py > SHOTLISTE.md
```

`media/` (Footage, Song, Fonts) liegt nicht im Repo.

## Nachgemessen

- **Achtel statt Viertel.** „Freaks“ läuft auf ~89,6 BPM; die Gitarre schlägt
  Achtel (0,334 s). Das Tempo schwankt leicht (88–91 BPM, Band ohne Klick),
  deshalb eine echte Beat-Map, Rest-Jitter 8 ms.
- **Schluss auf der Eins.** Bei k 176 (58,80 s) setzt im Song der Zwischenteil
  ein; das Video hört davor auf (80 ms Ausblende nur gegen das Knacken). Montiels
  Ball ist bei k 160 im Netz (53,50 s), `deliver.py` prüft Blitz und Anschlag am
  fertigen File auf denselben Frame.
- **Blenden in den Highlights.** Die FIFA-Highlights wechseln die Kamera oft per
  Überblendung statt per Schnitt; die Szenenerkennung findet die nicht. Die
  In-Punkte sind deshalb per Kontaktbogen (0,1–0,25 s Raster) und
  Frame-Differenzen gesetzt: Mexiko 79,3 (Annahme bis Schuss, Nahaufnahme) und
  76,3 (hinter dem Tor) liegen je zwischen zwei Blenden.
- **Reaktionsvideo 2016.** In `r16_cry` steht das Messi-Bild ab 4,3 s still (das
  Video pausiert dort); verwendet wird nur 2,6–4,27 s, die Einblendung unten
  rechts ist weggezoomt.
- **Standbild am Shot-Anfang** behoben wie im Neymar-Edit (`-fps_mode
  passthrough`); `stillcheck.py` prüft jeden Shot.
