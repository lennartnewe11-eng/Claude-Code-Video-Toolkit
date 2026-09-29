# Mesut Özil — CLASSIC (16:9)

2:12, 1920×1080, 50 fps. Ein Edit über die Klasse des Spielers: der Pass, der
erste Kontakt, der Freistoß, der Lupfer. **v2 zeigt ausschließlich Özil**:
seine Tore, seine Vorlagen, seinen Jubel, sein Gesicht. Die Maschine
(Renderer, Timeline, Prüfwerkzeuge) stammt aus `../neymar-edit`.

## Idee

Der Song beginnt mit einem Ansager aus der Schallplattenzeit: „And now for my
next number, I'd like to return to the classics … perhaps the most famous
classic in all the world of music“, und jede Strophe endet auf „Classic“. Das
Edit beantwortet die Frage, wer der Klassiker ist. Auf „my next number“
dreht sich Özil in Schwarzweiß mit der 11 auf dem Rücken weg, auf „the most
famous classic“ steht er 2010 bei der Hymne.

Der Song läuft **an einem Stück**, vom ersten bis zum letzten Schlag.
Ausgabe-Beat k = Song-Beat.

| Ausgabe-Beats | Song-Abschnitt | Kapitel | Inhalt | Grade |
|---|---|---|---|---|
| 0–48 | Intro, Ansager | Classics | ÖZIL 11 von hinten, Jubel, Trikotdruck, Hymne 2010; auf „Classic, classic, classic“ drei Jubel | mono → warm |
| 48–112 | Strophe 1 | REAL MADRID | Tor gegen Atlético 2010 (Ronaldo umarmt ihn), 1:1 in München 2012, Pass auf Ronaldo zum 2:0 gegen Bayern, Pass zum Siegtor im Camp Nou 2012 | warm |
| 112–144 | Break (Streicher) | — | Ronaldo feiert mit der 10; Özils Freistoßtor und sein Knierutscher | neutral → warm |
| 144–208 | Strophe 2 | DEUTSCHLAND | Tor gegen Ghana 2010, Vorlage zum 4:0 gegen Argentinien, Tor gegen Belgien 2011, Tor gegen Algerien 2014 (Netzkamera), mit Schürrle, der WM-Pokal | warm |
| 208–240 | Break („Meine Damen …“) | ARSENAL | Vorstellung 2013, Fotoshooting; auf „Liebling“ sein Jubel an der Eckfahne | warm |
| 240–304 | Strophe 3 | ARSENAL | Volley gegen Napoli 2013, Tor gegen United 2015, FA-Cup-Sieg, Hattrick gegen Ludogorets 2016 (Torwart umkurvt, Lupfer), mit Sánchez, ÖZIL 11 | warm |
| 304–344 | Outro | Gesichter | 2010, 2012, 2013, 2014 (mit dem Pokal), 2016, 2018: dasselbe Gesicht, älter werdend | mono |
| Coda | — | — | Titel | mono |

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # Chunks je Shot
python3 review.py 0-17 build/rv.jpg                # framegenaue Durchsicht
python3 stillcheck.py 0-46                         # kein Standbild am Shot-Anfang
python3 deliver.py --name oezil_edit_v2_1080p.mp4  # Master + Lieferfassung (28,5 MB)
python3 shotliste.py > SHOTLISTE.md
```

## Nachgemessen

- **Tempo konstant**: 162,00 BPM in allen drei Strophen, gerappt auf halber
  Zeit (eine Zeile = 8 Beats). Die Bass-Einsätze der Strophen liegen exakt auf
  Beat 48, 144 und 240; `beatmap.py` prüft das bei jedem Lauf.
- **WM 2014 aus dem Weltbild**: Algerien-Achtelfinale und Finale samt
  Siegerehrung liegen im Internet Archive als 720p50-Feed ohne Kommentar; aus
  dem 4,5-Stunden-Mitschnitt des Finales wurden nur die 130 Sekunden mit Özil
  und dem Pokal per HTTP-Range gezogen.
- **Fremde Einblendungen**: Der Fan-Schnitt „Top 5 Goals“ trägt links unten ein
  Gesichts-Logo, die Ronaldo-Sammlung eine arabische Laufschrift, die
  West-Ham-Highlights einen QR-Code. Alle drei werden per focus/zoom aus dem
  Bildausschnitt geschoben (`LOGO`, `QR` in `edl.py`).
- **Nicht jede Szene zeigt, wen man erwartet.** Der Sunderland-Ausschnitt im
  Arsenal-Saisonrückblick, als Özils Debüt geführt, zeigt Tore von Giroud und
  Ramsey; der vermeintliche Özil-Jubel gegen Argentinien 2010 zeigt Klose.
  Beides ist raus. Die Gesichter 2012 (Profil) und 2014 (hinter dem Pokal)
  findet die Haar-Kaskade nicht: Position von Hand gesetzt.
- **Formate**: Die PAL-Quellen (Saisonrückblick 13/14) haben nicht-quadratische
  Pixel; ohne Korrektur wären die Gesichter um 42 % gestaucht.
