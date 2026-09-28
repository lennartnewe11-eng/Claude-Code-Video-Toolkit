# Erkenntnisse

[`stil.md`](stil.md) hält fest, **wie** geschnitten wird. Hier steht, **warum** —
was sich beim Bauen von Akt 1 als tragfähig erwiesen hat, was schiefging und was
davon für Akt 2 und 3 gilt. Die Fehler stehen mit drin, weil die Regel ohne den
Fehler nur eine Behauptung ist.

Alle Zahlen aus dem gebauten Akt 1: 59 Shots, 116 Beats, 43,09 s.

---

## 1. Schnitt

### Das Raster ist die Grundlage, nicht das Ziel

Der Track läuft auf 161,5 BPM, ein Beat sind 0,3715 s. Über 493 Beats gemessen
streut das Raster um 9,8 ms — der Song läuft also wirklich gleichmäßig, man darf
sich darauf verlassen.

Zwei Dinge, die daraus folgen:

**Schnittgrenzen aus absoluter Zeit rechnen, nie aufaddieren.**
`round(beat × 0,3715 × 60)` je Grenze. So bleibt der Fehler unter einer halben
Frame und summiert sich über 116 Beats nicht auf. Wer Shot-Längen addiert,
driftet — am Anfang unmerklich, am Ende hörbar.

**Splice-Regel: `(b − a) % 4 == 0`.** Ein Sprung von Beat *a* nach *b* bleibt nur
dann rhythmisch nahtlos, wenn die Taktphase erhalten bleibt. Der ganze
Musikschnitt in Akt 1 ist ein einziger Sprung (Beat 119 → 295), und er trägt,
weil 176 durch 4 teilbar ist. Das ist keine Feinheit: liegt der Sprung daneben,
klingt es nach Fehler, egal wie gut die Bilder passen.

### Ein Beat ist keine Leseeinheit

**Das ist die wichtigste Erkenntnis der Sitzung.**

Ein Beat sind 0,3715 s, zwei Beats 0,74 s. Für einen Akzent reicht das. Für eine
Beobachtung — zwei Leute auf einer Bank, jeder ins Telefon vertieft — reicht es
nicht. Auf den Beat geschnitten blieb von den stärksten Clips nichts hängen: man
sah, dass etwas da war, aber nicht was.

Die naheliegende Lösung wäre gewesen, langsamer zu schneiden. Die hätte das
Tempo zerstört, das den ganzen Akt trägt.

### Bewegung statt Schnitt

Die tragfähige Lösung war, **Rhythmus und Schnitt zu entkoppeln**:

> Die Clips laufen durchgehend weiter. Auf jedem Beat springt nur ihre Position
> und Größe in eine neue Anordnung. Den Takt trägt die Bewegung, nicht der
> Schnitt.

Sechs Szenen gleichzeitig, jede mehrere Sekunden lesbar, und trotzdem passiert
auf jedem Beat sichtbar etwas. Jeder Clip hat dabei seine eigene Zeit, die ab
seinem ersten Auftritt durchläuft — er friert nicht ein, wenn er das Feld
wechselt.

Das verallgemeinert sich: **wenn Material mehr Zeit braucht als der Takt
hergibt, ändere nicht die Schnittfrequenz, sondern was auf dem Beat passiert.**
Position, Größe, Anordnung, Maske — alles außer dem Schnitt kann den Takt
tragen.

### Schnittlängen sind selbst ein Rhythmus

| Länge | Anzahl | Funktion |
|-------|-------:|----------|
| 2 Beats | 37 | der Normalfall |
| 1 Beat | 18 | Akzent, Stakkato |
| 4 Beats | 3 | Luft holen |
| 12 Beats | 1 | der Schluss |

Nicht gleichmäßig, aber auch nicht beliebig: ein Grundpuls aus Zweierschnitten,
Einzelbeats in Trauben (Shots 21–26 sind sechs am Stück), Viererschnitte als
Atempausen. Unter einen Beat geht nichts.

### Wann das Band stehen bleibt

Die Regel ist: das Formatband wechselt auf jedem Schnitt. In Akt 1 wird sie
genau einmal gebrochen — Shots 41–49, neun Mal `portrait`.

Ich hatte diese Stelle zuerst falsch erinnert und dem Scroll-Block zugeschrieben.
Ein Blick in die EDL zeigte: es ist der Größenvergleich. Und das ist der bessere
Grund. **Der Vergleich funktioniert nur, weil der Rahmen sich nicht rührt und
allein das Gerät wächst.** Ein Bandwechsel dazwischen würde genau die
Größenänderung kaschieren, um die es geht.

Daraus die allgemeine Fassung: **das Band steht still, wenn der Inhalt die
Veränderung trägt. Sonst wechselt es.**

(Nebenbei: nicht aus dem Gedächtnis über den eigenen Schnitt reden. Die EDL
weiß es genauer.)

### Die Häufigkeit ist der Stil

| | | | |
|---|--:|---|--:|
| `punch` | 26 | `zoom_in` | 4 |
| `grain` | 20 | `drift` | 3 |
| `thump` | 15 | `push` | 2 |
| `grain_heavy` | 9 | `open`/`close`/`dip`/`flash` | je 1 |
| `rgbhit` | 7 | ohne `fx` | 8 Shots |

Das ist kein Nebenbefund, sondern die Signatur: **ein paar Werkzeuge ständig,
die auffälligen fast nie.** `rgbhit` wirkt, weil es sieben Mal vorkommt. Auf
jedem zweiten Shot wäre es kein Akzent mehr, sondern ein Filter.

Dasselbe bei den Vektornetzen: 7 von 59 Shots, und zwar zusammenhängend in
einer Passage (Bett → Hand → Brille → Auge). Über das ganze Video verteilt wäre
aus der Behauptung „hier misst dich jemand aus“ Tapete geworden.

Beim Bauen hieß das zweimal: Dinge wieder herausnehmen, die für sich genommen
gut aussahen.

### Beat-gebunden konstruieren statt timen

Die Netzknoten werden aus dem Bild selbst gewonnen — stärkster Gradient je
Rasterzelle — und auf jedem Beat neu gesetzt. Dadurch sitzt das Neuzeichnen
**per Konstruktion** auf der Musik; es gibt nichts von Hand zu timen und nichts,
was verrutschen kann.

Generell: wo eine Größe aus dem Beatindex ausgerechnet werden kann, ist sie
richtig und bleibt richtig, auch wenn der Akt später wächst. Der programmierte
Aussetzer im Musikbett rechnet aus demselben Grund aus der Aktstruktur statt aus
einer festen Sekundenzahl.

### Ein Akt muss nicht knallen

Akt 1 endet mit der Choreographie: das Tempo bleibt, die Schnitte hören auf.
Das ist die Brücke in den Vibe Shift — ein Ende, das nicht zumacht, sondern
übergibt.

---

## 2. Freistellen

Drei Fehler, jeder mit einer Regel dahinter.

**Sprenkel blähen den Kasten auf.** u2net lässt Restpunkte im Bild stehen. Ein
bloßes `getbbox()` fängt jeden davon ein: bei `u_klippe` kam 786 × 860 heraus,
während die Figur 199 × 516 groß war. Beim Einpassen wurde sie damit auf rund
60 % skaliert. → Maske erst erodieren (`MinFilter`), dann messen.

**Pro Frame messen lässt die Figur pulsieren.** Die Ränder schwanken von Bild zu
Bild um Dutzende Pixel; croppt man einzeln und skaliert auf Feldhöhe, atmet die
Figur. → Einmal über den Clip messen. Dabei Ausreißer-Frames verwerfen, sonst
reicht ein einziges schlechtes Bild, um den Kasten für den ganzen Clip
aufzuziehen.

**Die Höhe bestimmt den Maßstab, nicht der Ausschnitt.** Sonst füllt eine
Einzelfigur ihr Feld, während eine Zweiergruppe daneben winzig wird. Gruppen
dürfen breiter werden als ihr Feld (bis 3,2 ×) und werden notfalls in den Rahmen
geschoben statt beschnitten.

**Und zur Anordnung:** im 9:16 ist eine Reihe auf einer Standlinie in der
Bildmitte die schlechteste aller Lösungen — oben und unten bleibt je ein Viertel
leer, in der Mitte überlappt alles. Die Figuren über die volle Höhe streuen.

---

## 3. Ausliefern

Weniger Schnitt, aber es hat Zeit gekostet — deshalb festgehalten.

**Eine Zielgröße trifft man nicht mit CRF.** CRF hält die Qualität konstant und
lässt die Größe laufen. Bei einem festen Budget ist die Bitrate das vorzugebende
Maß: zwei Durchgänge auf die Zielgröße.

**Grenzen kennen, bevor man encodiert.** Das Artefakt liefert 15 MB je Datei und
64 MB je Version aus. Die Downloadfassung liegt deshalb byteweise in drei
Stücken, die der Browser wieder zusammensetzt — byteweise geteilt und byteweise
gefügt ergibt dieselbe Datei, über SHA-256 geprüft.

**Zahlen gehören dorthin, wo sie entstehen.** Größen in der HTML-Seite fest
eingetragen waren nach dem nächsten Export veraltet, und die Längenprüfung im
Browser schlug an. Jetzt schreibt `deliver.py` einen Index, die Seite baut ihre
Zeilen daraus.

**Lokal getestet ist nicht veröffentlicht getestet.** Der lokale Test lief gegen
die aktuellen Dateien und war grün — veröffentlicht lagen noch die aus dem
vorigen Export, und zwei von drei Downloads wären gescheitert. Gegen die echte
Dateiliste prüfen, nicht gegen die Arbeitskopie.

---

## 4. Das Muster hinter den Fehlern

Fast alles, was in dieser Sitzung schiefging, hatte dieselbe Form: **eine
plausible Annahme, die niemand nachgemessen hat.**

- Der Alpha-Kasten umschließt schon die Figur → tat er nicht.
- Die Ansichtsfassung ist die veröffentlichte Datei → war sie nicht.
- Ein Download-Link lädt herunter → im Artefakt nicht.
- Der Block mit festem Band war der Scroll-Teil → war der Größenvergleich.

Was geholfen hat, war jeweils dasselbe: **hinsehen statt annehmen.** Contact
Sheet rendern und anschauen. Die EDL auszählen. Die Prüfsumme vergleichen. Die
Datei im Browser wirklich klicken.

Deshalb auch: die Shotliste wird inzwischen aus der EDL erzeugt
(`build/shotliste.py`). Von Hand gepflegt stand sie auf 49 Shots und 34,18 s,
während der Schnitt längst bei 59 Shots und 43,09 s war. Eine Doku, die driften
kann, driftet.

---

## 5. Was für Akt 2 und 3 gilt

1. Raster und Splice-Regel bleiben. Jeder Aktübergang muss `% 4 == 0` erfüllen.
2. Zweierschnitte als Puls, Einzelbeats in Trauben, Vierer als Atempause.
3. Band wechselt auf jedem Schnitt — außer wo der Inhalt die Veränderung trägt.
4. Die Effektkurve halten: die auffälligen Werkzeuge bleiben selten. Akt 2 und 3
   haben eigene Grades (`cold`, `bleak`, `warm`), die in Akt 1 fast ungenutzt
   sind — die tragen den Umschlag, nicht neue Effekte.
5. Wo Material Zeit braucht, Bewegung auf den Beat legen statt langsamer zu
   schneiden.
6. Vor dem Übernehmen einer Entscheidung: nachsehen, nicht erinnern.
