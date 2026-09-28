# Stil

Was diesen Edit ausmacht — festgehalten, damit Akt 2 und 3 dieselbe Sprache
sprechen und nicht neu erfunden werden müssen. Alle Zahlen sind aus dem
gebauten Akt 1 gemessen (59 Shots, 116 Beats, 43,09 s), nicht geschätzt.

---

## 1. Der Grundsatz

**Der schwarze 1080×1920-Rahmen steht still. Das Bild darin nicht.**

Jeder Clip sitzt in einem eigenen Seitenverhältnis-Band auf schwarzem Grund.
Dadurch wirkt es, als wechsle das Format des Videos selbst — obwohl nie etwas
am Rahmen passiert. Das ist keine Deko, das ist die Grammatik: Schwarz ist
Bildfläche, nicht Hintergrund.

Daraus folgt alles Weitere. Ein Effekt, der den Rahmen anfasst (Ganzbild-Wackeln,
Rahmen-Transitions, Letterbox-Animationen über den ganzen Frame), bricht die
Illusion und gehört nicht in dieses Video.

## 2. Das Raster

| | |
|---|---|
| Beat | **0,3715 s** (161,5 BPM) |
| Takt | 4 Beats = 1,4861 s |
| Schnittgrenze | `round(beat × 0,3715 × 60)` — absolut gerechnet, nie aufaddiert |

Schnittpunkte werden immer aus der **absoluten** Beat-Zeit auf den nächsten
Frame gerundet. So bleibt der Fehler unter einer halben Frame und summiert sich
über 116 Beats nicht auf. Wer Shot-Längen addiert, driftet.

**Splice-Regel:** ein Sprung von Beat *a* nach *b* bleibt rhythmisch nahtlos,
wenn `(b − a) % 4 == 0`. Nur so bleibt die Taktphase erhalten. Das ist der
ganze Trick hinter dem einen Musikschnitt in `music_bed.py`.

**Shot-Längen** in Akt 1:

| Länge | Anzahl | Funktion |
|-------|--------|----------|
| 2 Beats | 37 | der Normalfall |
| 1 Beat | 18 | Akzent, Stakkato |
| 4 Beats | 3 | Luft holen |
| 12 Beats | 1 | der Schluss (Choreographie statt Schnitt) |

Unter 1 Beat wird nicht geschnitten. Was kürzer ist als ein Beat, liest niemand.

## 3. Bänder

`strip` 3:1 · `slab` 4:1 · `cinema` 2.39:1 · `wide` 16:9 · `classic` 4:3 ·
`square` 1:1 · `half` 9:8 · `portrait` 3:4 · `full` 9:16 · `tv` 4:3 klein ·
`mini` 4:3 sehr klein

Verteilung in Akt 1: `portrait` 10 · `cinema` 9 · `wide` 9 · `classic` 8 ·
`square` 7 · `full` 6 · `tv` 5 · `strip` 3 · `mini` 1 · `slab` 1.

**Regel: das Band wechselt auf jedem Schnitt.** In Akt 1 steht nur an einer
einzigen Stelle dasselbe Band mehrfach hintereinander — Shot 41–49, der
Größenvergleich, neun Mal `portrait`. Und zwar notwendig: der Vergleich
funktioniert überhaupt nur, wenn der Rahmen sich *nicht* rührt und allein das
Gerät wächst. Ein Bandwechsel dazwischen würde genau die Größenänderung
kaschieren, um die es geht.

Das ist der allgemeine Fall: das Band steht still, wenn der Inhalt die
Veränderung trägt. Sonst wechselt es.

Zuordnung, die sich bewährt hat:

- `classic`, `tv`, `mini` — Archivmaterial. `tv` und `mini` lassen das Bild
  klein und verloren im Schwarz stehen; das ist die Distanz-Geste.
- `cinema`, `strip`, `slab` — Horizonte, Augen, Hände. Alles, was breit und
  flach gelesen wird.
- `portrait`, `full` — Körper, Telefone, Hochkant-Material. `full` ist randlos
  und damit die stärkste Karte; sechs Mal in Akt 1.
- `square`, `wide` — der Normalfall dazwischen.

`fx: ["open"]` / `["close"]` fährt das Band selbst auf oder zu. Je ein Mal
in Akt 1 — mehr verträgt es nicht.

## 4. Grades

Sieben Grades in `looks.py`, in Akt 1 benutzt: `neutral` 16 · `punchy` 15 ·
`archive` 14 · `bw` 13 · `cold` 1.

- `archive` — warm, angehobene Schwarzwerte, leicht ausgeblichen. Für alles
  Historische.
- `punchy` — kontrastreich, gesättigt. Aufbruch, Raketen, Werbung.
- `bw` — hartes Schwarzweiß. **Für die eigenen Clips**, die schon monochrom
  sind: `bleak` und `cold` legen eine Blaufärbung auf bereits entsättigtes
  Material und lassen es kaputt aussehen.
- `cold`, `bleak`, `warm` — für Akt 2 und 3 reserviert (Vibe Shift, tiefster
  Punkt, Auflösung). In Akt 1 hat `cold` genau einen Auftritt.

Über **jedem** Shot liegen Vignette und feines Korn
(`vignette=angle=PI/6,noise=alls=4:allf=t`). Das bindet Archivmaterial,
Stock und Selbstgebautes zu einem Bild zusammen. Es sitzt bewusst im
Einzelshot und nicht als globaler Pass — global verdoppelt `noise` die
Encodezeit und treibt den Master auf 35 Mbit/s.

## 5. Bewegung

Zoom und Versatz kommen aus Ausdrücken, nicht aus Keyframes:

| fx | Wirkung |
|----|---------|
| `punch` | `1 + 0.085·e^(−t/0.11)` — kurzer Stoß, nach ~0,2 s vorbei |
| `thump` | `1 + 0.16·e^(−t/0.07)` — härter, noch kürzer |
| `zoom_in` / `zoom_out` | 10 % über die Shotlänge |
| `push` | 22 % über die Shotlänge |
| `shake` | gedämpfte Schwingung, `e^(−t/0.16)` |
| `drift`, `sway` | langsamer Versatz bzw. Pendeln |

`punch` und `thump` sind die eigentlichen Beat-Akzente: sie klingen exponentiell
ab und sind **vor** dem nächsten Beat verschwunden. Eine Bewegung, die bis in
den nächsten Shot läuft, verwischt das Raster.

Häufigkeit in Akt 1: `punch` 26 · `grain` 20 · `thump` 15 · `grain_heavy` 9 ·
`rgbhit` 7 · `zoom_in` 4 · `drift` 3 · `push` 2 · je ein Mal `open`, `close`,
`dip`, `flash`. Acht Shots haben gar kein `fx`.

**Diese Kurve ist der Stil.** Ein paar Werkzeuge ständig, die auffälligen fast
nie. Wenn `rgbhit` auf jedem zweiten Shot liegt, ist es kein Akzent mehr.

## 6. Vektornetze

Cyanfarbene Wireframes (`CYAN = 56,232,222`) über dem Material, dazu technische
Pseudo-Annotationen (`Δ42ms`, `TRK-17`) und Momente, in denen nur noch die
Linien auf Schwarz stehen (`_solo`).

Die Knoten werden aus dem Bild selbst gewonnen — stärkster Gradient je
Rasterzelle — und **auf jedem Beat neu gesetzt**. Dadurch sitzt das Neuzeichnen
per Konstruktion auf der Musik; nichts muss von Hand getimt werden. Knotenzahl
richtet sich nach dem Bandformat (26/18/12 bei Raster 7/6/5), Linien als dunkler
4px-Unterzug plus 2px Cyan darüber, damit sie auf hellem Material stehen bleiben.

**Sparsam einsetzen.** In Akt 1 tragen 7 von 59 Shots ein Netz, und zwar
zusammenhängend in einer Passage (Bett → Hand → Brille → Auge). Das Netz ist
die Behauptung „hier misst dich jemand aus“ — über das ganze Video verteilt
wird sie zur Tapete.

## 7. Freisteller und Choreographie

Das Problem am Schluss: gute Beobachtungsclips brauchen mehr als 0,74 s, um
gelesen zu werden — auf den Beat geschnitten versteht man sie nicht.

Die Lösung heißt nicht „länger schneiden“, sondern: **die Clips laufen
durchgehend weiter, nur ihre Position springt auf dem Beat.** Den Takt trägt
die Bewegung, nicht der Schnitt. Jeder Clip hat seine eigene Zeit, die ab
seinem ersten Auftritt durchläuft (`collage.py`).

Dazu zwei Beats, auf denen die Umgebung wegfällt und nur die freigestellten
Menschen mit ihren Geräten auf Schwarz übrig bleiben (rembg/u2net).

Regeln für die Freisteller, jede aus einem Fehler gelernt:

- **Die Figuren verteilen sich über die volle Höhe.** Eine Reihe auf einer
  Standlinie in der Bildmitte lässt im 9:16 oben und unten je ein Viertel leer
  und drängt alles in die Mitte.
- **Auf die Figur beschneiden, nicht auf den Rahmen.** Sonst skaliert man vor
  allem leeren Raum und die Figur wird winzig.
- **Sprenkel vorher weg.** u2net lässt Restpunkte im Bild stehen; ein bloßes
  `getbbox()` fängt jeden davon ein und liefert fast den ganzen Rahmen zurück.
  `figure_bbox()` erodiert die Maske erst (`MinFilter`), dann misst sie.
- **Ein fester Kasten pro Clip, nicht pro Frame.** Sonst pulsiert die Figur in
  der Größe. `clip_figure_box()` misst über den Clip, wirft Ausreißer-Frames
  weg und vereinigt den Rest.
- **Die Höhe bestimmt den Maßstab**, Gruppen dürfen breiter werden (bis 3,2×
  der Feldbreite) und werden notfalls in den Rahmen geschoben statt beschnitten.

## 8. Farbe

Das Bild ist schwarz, grau und entsättigt. Es gibt genau zwei Farben:

| | |
|---|---|
| Cyan `56,232,222` | die Vektornetze |
| Rot `200,52,26` | der Akzent — Konturen, Maßbalken, Ansichtsseite |

Rot kam aus einem Fehler: die Kontur des iPhone 1 im Größenvergleich war weiß
auf hellem Grund und damit unsichtbar. Es ist die einzige gesättigte Farbe im
ganzen Video und bleibt dadurch eine Aussage.

## 9. Typo

ASS/libass, Inter Medium. Kein `drawtext` — der ffmpeg-Build hier hat den
Filter nicht, und ASS ist ohnehin das bessere Werkzeug. Text wird erst beim
Zusammenbau eingebrannt (`assemble.py` mit `.ass`-Datei), nicht in die Shots.

Im fertigen Akt 1 steht **kein** Text. Die `.ass` trug nur die Platzhalter
„DEIN CLIP HIER“ für offene Slots; die sind alle gefüllt, also wird sie nicht
mehr eingebrannt und der Zusammenbau bleibt ein reiner Kopiervorgang. Wenn
Typo dazukommt, dann als Aussage auf einem Beat — nicht als Untertitel.

## 10. Was nicht

- **Keine Blenden.** Es wird geschnitten. `dip` und `flash` sind Akzente auf
  einem Beat, keine Übergänge.
- **Kein Effekt ohne Grund im Bild.** Ein `thump` sitzt auf einem Schlag, ein
  Netz auf einem Körperteil, ein Bandwechsel auf einem Themenwechsel.
- **Nichts am Rahmen.** Siehe Grundsatz.
- **Keine Farbe außer den beiden.**
- **Kein Material, das der Aussage widerspricht.** In Akt 1 aussortiert:
  *America in Turmoil* (1967), ein Film der rechtsextremen *Liberty Lobby* —
  unbrauchbar in einem Video gegen Spaltung, egal wie gut die Bilder sind.
  Begründung in `docs/akt1_shotliste.md`.

## 11. Dramaturgie

Der Song gibt die Aktstruktur vor, nicht umgekehrt. Sein erster Breakdown
(Bass fällt um 8 dB ab) ist der Vibe Shift, sein originaler Drop ist der
Umschlag in Akt 3. Details und Zeiten in der [README](../README.md).

| Akt | Haltung | Grades |
|-----|---------|--------|
| 1 — Aufbruch | Versprechen, Tempo, Aufbruch | `punchy`, `archive`, `bw` |
| 2 — Vibe Shift | Vereinzelung, Bass weg | `cold`, `bleak` |
| 3 — Zusammenrücken | Auflösung | `warm` |

Akt 1 endet nicht mit einem Knall, sondern mit der Choreographie: das Tempo
bleibt, die Schnitte hören auf. Das ist die Brücke in den Vibe Shift.
