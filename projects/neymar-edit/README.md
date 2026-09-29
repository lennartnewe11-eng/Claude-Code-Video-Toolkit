# Neymar — OUSADIA E ALEGRIA (16:9)

2:17, 1920×1080, 50 fps. Ein Skill-Edit mit einer Storyline, die genau eine
Emotion bedient: **Freude**. Sie wird gespielt, angehalten und bricht mit dem
letzten Elfmeter im Maracanã 2016 als Freudentränen wieder aus. Die Maschine
(Renderer, Timeline, Prüfwerkzeuge) stammt aus `../messi-edit`.

## Storyline

Der Song läuft **an einem Stück**, Song-Beat 152 bis zum letzten Schlag (432).
Ausgabe-Beat k = Song-Beat − 152.

| Ausgabe-Beats | Song-Abschnitt | Kapitel | Inhalt | Grade |
|---|---|---|---|---|
| 0–60 | Strophe 2, Pre-Chorus | GINGA | Santos 2011 (Solotor um den Torwart), London 2012, Confed Cup 2013 | faded → warm |
| 60–96 | Pre-Chorus | SHOW | Barça, PSG, Seleção; Hochkant-Quellen im Portrait-Band | warm |
| 96–104 | Loch | Atem | ein Profil in Zeitlupe | mono |
| 104–136 | Drop 2 | Skills | Kroatien 2022, Dribbling-Trauben, Freistoß im Olympia-Finale | warm |
| 136–200 | Breakdown | DRUCK | Maracanã bei Nacht, Elfmeterschießen, Hand aufs Herz, Blick nach oben | bleak / mono |
| 200–216 | Build | ANLAUF | Neymar legt den Ball hin; Band zieht sich zusammen | mono |
| 216–244 | Drop 3 | ALEGRIA | **Ball im Netz genau auf dem Drop**, Freudentränen | warm |
| 244–248 | Loch | Tränen | ein Bild, still | mono |
| 248–280 | Finale | Gold | Medaille, Samba, jedes Lachen noch einmal | warm |
| Coda | Ausklang | — | Medaille in Zeitlupe, Titel | warm |

**Der Treffer.** Der Schuss läuft in Zeitlupe; die Quellzeit ist so gerechnet,
dass der Ball exakt auf Song-Beat 368 (Drop 3) im Netz ist (`audio.SYNC`).
Darunter der Clean Feed aus dem Maracanã ohne Kommentar: vier Beats lang die
angespannte Stille, dann der Jubel auf dem Drop.

**Farbe als Dramaturgie.** Alles bis zum Freistoß ist warm. Das Elfmeterschießen
entsättigt sich bis zu Schwarzweiß; in dem Moment, in dem der Ball im Netz
ist, kommt die Farbe mit einem Weißblitz zurück.

## Bauen

```bash
python3 fetch.py                                   # Footage aus dem Internet Archive
python3 beatmap.py media/audio/song.mp3 build/beatmap.json
python3 audio.py                                   # build/music.wav
python3 render.py                                  # Chunks je Shot
python3 review.py 0-24 build/rv.jpg                # framegenaue Durchsicht
python3 deliver.py --name neymar_edit_1080p.mp4    # Master + Lieferfassung (28,5 MB)
python3 shotliste.py > SHOTLISTE.md
```

## Nachgemessen

- **Tempo konstant.** Anders als beim Messi-Song: 127,87 BPM über die ganze
  Länge (Fensterstreuung < 0,1 %), also ein starres Raster, per Least-Squares
  auf die Onsets gefittet (Jitter 9 ms).
- **Nicht jede „Neymar"-Quelle zeigt Neymar.** Ein Item namens „Neymar" war ein
  indischer Spielfilm mit einem Hund dieses Namens; das Dribbling in den
  Santos-Highlights, das zuerst im Schnitt war, stammt vom Colo-Colo-Spieler
  mit der 11. Beides nur durch Hinsehen gefunden, beides ersetzt.
