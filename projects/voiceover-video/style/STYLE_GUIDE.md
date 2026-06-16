# Style Guide — "Warum Amerika seine Züge verlor"

**Richtung:** Editorial Kinetic Collage (Referenz: `style_code.zip` — Prof-G / Scott-Galloway-Look)
**Format:** 16:9 · 1920×1080 (Master 4K möglich) · 30 fps · Sprache: Deutsch
**Zwei Modi:**
1. **Hook** — *ausschließlich* schnell geschnittenes Archivmaterial, footage-forward, minimale Typo.
2. **Erklärender Part** — kinetische Editorial-Typografie + Collage im Referenz-Stil.

---

## 0. Analyse der Referenz (`ScreenRecording … _1.mp4`, 30 s, 60 fps)

Beobachteter Stil ("Prof G"-Editorial):
- **Heller Cream-Hintergrund** statt dunkel; warme Papieranmutung, feines Korn.
- **Gemischte Typografie in EINER Zeile:** neutrale Grotesk-Sans für Verbindungswörter + **fette Sans** für Keywords + *kursive High-Contrast-Serife* für Betonung + **RIESIGE Display-Serife in Caps** für das Schlüsselwort (z. B. „SOCIAL SECURITY", „BIGGEST"). Wort-für-Wort-Reveal.
- **Witzige Text-Edits:** Durchstreichen + Ersetzen (~~my~~ his age).
- **S/W-Freisteller** (Personen, z. B. Galloway) + **3D-Props** (fallende Geldscheine, Münztürme) als Collage rechts.
- **Collage-Schnipsel:** Karo-/Millimeterpapier, Tan- und Sage-Blöcke, leicht rotiert.
- **Editorial-Marks:** dünne Fadenkreuze (+), Eckwinkel (⌐ ¬), Tickmarks — in Olivgrün; technische Layout-Ästhetik.
- **Kursive Rand-Labels mit Pfeil:** „daylight robbery →", „train robbery →"; Namens-Label mit handgezeichnetem Bogen-Pfeil („scott galloway").
- **Media-Cards:** Archiv-/Stockclips als gerahmte Karten mit Schatten, leicht gedreht/geschichtet, von Marks umrahmt.
- **Segmentierte Fortschrittsleiste** oben rechts (kleine Quadrate) = Kapitel-Indikator.
- **Footage-Grade:** leicht entsättigt, warm an die Cream-Palette angeglichen.

---

## 1. Farbsystem (aus Referenz gesampelt)

| Token | Hex | Einsatz |
|-------|-----|---------|
| `--paper` | `#EFEDE1` | Haupt-Hintergrund (Cream) |
| `--paper-2` | `#E6E3D2` | dunkleres Cream / Cards |
| `--tan` | `#D4CFBB` | Beige-Blöcke |
| `--sage` | `#505B4B` | Oliv — Marks, Blöcke, aktive Segmente |
| `--sage-2` | `#7C876E` | helleres Sage |
| `--ink` | `#141312` | Text (Near-Black) |
| `--ink-2` | `#4A4843` | Sekundärtext / Labels |

Prinzip: **warmes Cream + Schwarz + Oliv.** Farbe extrem sparsam; Wirkung kommt aus Typo-Kontrast und Collage, nicht aus Farbe.

## 2. Typografie

- **Display/Serife:** **Fraunces** (Variable, roman + italic) — High-Contrast-Didone. Für Caps-Schlüsselwörter & kursive Betonung. Lokal: `style/assets/fonts/Fraunces*.ttf`.
- **Grotesk/Sans:** **Inter** — neutral, für Verbindungswörter & Bold-Keywords.
- **Mischsatz-Regel:** pro Aussage 1 Schlüsselwort als Display-Serif-Caps; 1–2 Wörter kursiv-serif (Betonung); Rest Sans (regular + bold gemischt). Nicht überladen.
- **Rand-Labels:** Fraunces *italic*, klein, mit `→`/Bogen-Pfeil.

## 3. Komponenten

- **Kinetic-Type-Block** — gemischte Zeile, Wort-für-Wort animiert.
- **Text-Edit** — Strike-through + Ersatz für Pointen.
- **S/W-Freisteller** — Person/Objekt freigestellt, Duoton, vor Collage-Schnipsel; Namens-Label mit Bogen-Pfeil.
- **Media-Card** — Clip als gerahmte, leicht gedrehte Karte mit Schatten; Tag unten; Fadenkreuze/Eckwinkel rundherum; oft eine zweite Karte „peekend" am Rand.
- **3D-Prop / Collage-Objekt** — Geld, Münzen, Schiene/Highway als getiltete Blöcke.
- **Editorial-Marks** — `+` Fadenkreuze, Eckwinkel, Tickmarks (Oliv).
- **Segbar** — Kapitel-Fortschritt oben rechts.
- **Quellen-Beleg** unten links (Pflicht bei Zahlen/Archiv) · **Chapter-Tag** unten rechts (intern).

## 4. Hook — Sonderregel (Wunsch des Auftraggebers)

- **Ausschließlich echtes, schnell geschnittenes Archivmaterial.** Keine Stat-Cards.
- Rapid Montage: Shinkansen, TGV, China-HSR, dann verfallende US-Bahn/leere Bahnhöfe.
- Schnitte hart auf den Beat / auf VO-Pausen (`analysis/voiceover_pauses.txt`).
- Footage warm an Cream gegradet; **minimale** Overlays: ein großes kursiv-serifes Stat-Wort (z. B. *320 km/h*), kleines Location-Label, „→"-Randlabel, Segbar.
- Übergang zum erklärenden Part: harter Cut auf Cream-Bühne.

## 5. Footage- & Material-Beschaffung (lizenzkonform)

- **Archiv/Public Domain:** Library of Congress, Internet Archive (Prelinger), Wikimedia Commons.
- **Stock (frei):** Pexels, Pixabay, Coverr.
- **Freisteller:** S/W, sauber maskiert; Personen aus PD-/CC-Quellen.
- **Karten/Daten:** Natural Earth, OpenRailwayMap.
- Pro Asset: Quelle + Lizenz in `assets/footage/SOURCES.md`.

## 6. Sounddesign

- Score: zurückhaltend, treibend; Hook & Fazit lauter, unter Sprache Ducking (−12 dB).
- SFX: Tick/Type-Pops bei Wort-Reveals, Whoosh bei Card-/Mark-Einblendung, Schienen/Zug-Layer in Kapitel-Intros, „Cash"-Sounds bei Geld-Props. Sammlung: `assets/sfx/`.
- VO-Master sauber (−17,8 dB mean). Mix: VO −3 dB peak.

## 7. Motion (Umsetzung in Remotion)

- Wort-für-Wort-Reveal (kurzer Y-Offset + Fade), Display-Wort mit leichtem Scale-Pop.
- 3D-Props fallen/tumbeln hinein; Cards sliden + leichte Rotation; Marks „snappen".
- Routen/Charts (falls genutzt) zeichnen sich; Zahlen zählen hoch.
- Tempo schnell, an die Sprache geschnitten; pro Aussage ein visueller Beat.

---

### Style-Frames (Editorial — aktueller Stand)
In `style/frames/out/`:
1. `frame_e1_hook.png` — Hook: full-bleed Archiv (320 km/h) · footage-forward
2. `frame_e2_explainer.png` — Kinetic Type + Collage-Props (Highway vs. Schiene)
3. `frame_e3_card.png` — Media-Card mit Registration-Marks (Metroliner)
4. `frame_e4_cutout.png` — S/W-Freisteller + Strike-Edit (Eisenhower)

Render: `node style/frames/render.mjs`  · alte dunkle Variante: `node style/frames/render.mjs frame_01_hook frame_02_chart frame_03_archival`

> Vorherige Richtung (dunkel, Wendover/Vox) liegt noch als `frame_0x_*.html` vor, ist aber **verworfen**.
