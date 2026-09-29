# Mesut Özil — CLASSIC (16:9)

2:12, 1920×1080, 50 fps. Ein Edit über die Klasse des Spielers: der Pass, der
erste Kontakt, der Lupfer. Die Maschine (Renderer, Timeline, Prüfwerkzeuge)
stammt aus `../neymar-edit`.

## Idee

Der Song beginnt mit einem Ansager aus der Schallplattenzeit: „I'd like to
return to the classics … perhaps the most famous classic in all the world of
music“, und jede Strophe endet auf „Classic“. Das Edit beantwortet die Frage,
wer der Klassiker ist: Liberace am Flügel wird zu Özil bei der Hymne 2010, im
selben Schwarzweiß-Fenster.

Der Song läuft **an einem Stück**, vom ersten bis zum letzten Schlag.
Ausgabe-Beat k = Song-Beat.

| Ausgabe-Beats | Song-Abschnitt | Kapitel | Inhalt | Grade |
|---|---|---|---|---|
| 0–48 | Intro, Ansager | Classics | Liberace (1950er), dann Özil 2010; auf „Classic, classic, classic“ drei Jubel | mono → warm |
| 48–112 | Strophe 1 | REAL MADRID | sein 1:1 in München 2012, Ronaldo umarmt ihn; sein Pass auf Ronaldo zum 2:0 gegen Bayern | warm |
| 112–144 | Break (Streicher) | — | Özil geht vom Platz, Zeitlupe | neutral |
| 144–208 | Strophe 2 | DEUTSCHLAND | WM 2014, sein Tor gegen Algerien; Einschübe auf die Textzeilen | warm |
| 208–240 | Break („Meine Damen …“) | — | Wochenschau 1926, dann Özils Vorstellung bei Arsenal | mono → warm |
| 240–304 | Strophe 3 | ARSENAL | Tor gegen United, FA-Cup-Sieg, Hattrick gegen Ludogorets (Torwart umkurvt, Lupfer) | warm |
| 304–344 | Outro | Gesichter | 2010, 2012, 2013, 2014, 2016, 2018: dasselbe Gesicht, älter werdend | mono |
| Coda | — | — | Titel | mono |

## Geschichtliche Referenzen aus dem Text

Die Wortzeiten stammen aus einer Transkription (faster-whisper large-v3), in
Beats umgerechnet. Der Einschub sitzt jeweils auf dem Wort und ist kurz genug,
dass der Fußball die Erzählung bleibt.

| Zeile | Beat | Bild |
|---|---|---|
| „return to the classics“ | 0–31 | Liberace am Flügel, 1950er |
| „brennt dir deine Fresse, Niki Lauda“ | 169,5 | Laudas brennender Ferrari, Nürburgring 1976 |
| „es wie Kobe Bryant trifft“ | 194 | Kobes Wurf gegen Phoenix, 2006 |
| „reden hinter meinem Rücken“ | 202 | Özils Rücken, ÖZIL 10 |
| „für Sie singt ihr erklärter Liebling“ | 216 | Polygoon-Wochenschau 1926, Paul Whiteman |
| „dein Album ist ein Selfie“ | 265,5 | Özil beim Fotoshooting |
| „unser Album ist ein Rembrandt“ | 269,5 | die Nachtwache nach der Restaurierung, 1976 |
| „Internet-Hype wie ne Apple Keynote“ | 299,5 | das erste iPhone, Macworld 2007 |
| „eine ganze Reihe eindrucksvoller Aufnahmen“ | 304–344 | die Gesichter-Reihe |

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # Chunks je Shot
python3 review.py 0-17 build/rv.jpg                # framegenaue Durchsicht
python3 stillcheck.py 0-50                         # kein Standbild am Shot-Anfang
python3 deliver.py --name oezil_edit_1080p.mp4     # Master + Lieferfassung (28,5 MB)
python3 shotliste.py > SHOTLISTE.md
```

## Nachgemessen

- **Tempo konstant**: 162,00 BPM in allen drei Strophen, gerappt auf halber
  Zeit (eine Zeile = 8 Beats). Die Bass-Einsätze der Strophen liegen exakt auf
  Beat 48, 144 und 240; `beatmap.py` prüft das bei jedem Lauf.
- **Nicht jede Szene zeigt, wen man erwartet.** Der Sunderland-Ausschnitt im
  Arsenal-Saisonrückblick, als Özils Debüt geführt, zeigt Tore von Giroud und
  Ramsey; er ist wieder raus. Das Gesicht 2012 ist im Profil, die Haar-Kaskade
  findet es nicht: Position von Hand gesetzt.
- **Formate**: Die PAL-Quellen (Saisonrückblick 13/14, finnische WM-Übertragung
  2014, Polygoon-Wochenschauen) haben nicht-quadratische Pixel; ohne Korrektur
  wären die Gesichter um 7 bis 42 % gestaucht.
