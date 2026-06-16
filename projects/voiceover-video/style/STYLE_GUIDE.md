# Style Guide — "Warum Amerika seine Züge verlor"

**Richtung:** Sachlich-datengetrieben (Referenzen: Wendover Productions, Vox)
**Format:** 16:9 · 1920×1080 (Master in 4K möglich) · 30 fps
**Sprache:** Deutsch · Tonalität: ruhig, autoritär-erklärend, faktenstark

---

## 1. Farbsystem

| Token | Hex | Einsatz |
|-------|-----|---------|
| `--bg` | `#14171C` | Grundfläche (Charcoal) |
| `--bg-2` | `#1B1F26` | Panels, Karten, Pills |
| `--line` | `#2A2F38` | Hairlines, Grid, Achsen |
| `--ink` | `#FFFFFF` | Primärtext |
| `--ink-2` | `#A2A9B4` | Sekundärtext |
| `--ink-3` | `#6B727C` | Captions, Quellen |
| `--accent` | `#FFD23F` | **Signatur-Gelb** — Key-Zahlen, Betonung |
| `--usa` | `#FF5A4D` | Negativ / Niedergang / USA |
| `--rail` | `#38D996` | Positiv / Erfolg (Japan, EU, China) |
| `--blue` | `#5B8DEF` | Neutrale Datenreihe |

Prinzip: **dunkle Bühne, eine Signaturfarbe (Gelb) für Betonung**, Rot/Grün nur semantisch (Niedergang vs. Erfolg). Nie mehr als 2 Akzente pro Frame.

## 2. Typografie

- **Schrift:** Inter (Variable). Lokal unter `style/assets/fonts/Inter.ttf`.
- **Zahlen:** Tabellenziffern (`font-feature-settings: 'tnum'`) — Stats stehen sauber untereinander.
- Headline 64–92 px / 800 · Subtitle 28–32 px / 500 · Kicker 26 px / 700, `letter-spacing .28em`, uppercase, gelb.
- Negatives Tracking (−.02em) bei großen Headlines.

## 3. Bausteine (Komponenten)

- **Kicker** — gelber Balken + Kapitel-Label oben links.
- **Stat-Card** — Panel mit farbigem Seitenbalken (grün/rot), Land, große Zahl, Subtext. Für Vergleiche (Hook, Fazit).
- **Daten-Chart** — dunkler Grund, gestrichelte Gridlines, eine kräftige Linie + Verlaufs-Fläche, Annotation-Pills an Wendepunkten. Für Kosten, Netzlänge, Zeitreihen.
- **Lower-Third** — Jahr (groß, gelb) + Titel + ein Satz Kontext + Akzentbalken. Über Archiv-B-Roll.
- **Map-Inset** — kleine Karte oben rechts, abstrahierte Landmasse + gestrichelte Route + Stadt-Punkte. Für Strecken (Transkontinental, NEC, Brightline).
- **Quellen-Beleg** — klein unten links; **Pflicht** bei jeder Zahl und jedem Archivclip.
- **Chapter-Tag** — Timecode + Kapitel unten rechts (nur intern/Arbeitsversion).

## 4. Footage-Behandlung (Archivmaterial)

- Leichter Color-Grade auf die Palette: warme Lichter, abgesenkte Schwarzwerte (`#14171C`-Floor).
- Dezente Vignette + sehr feines Korn; optional minimaler Scanline-Hauch bei echtem Archiv.
- **Immer** Quelle einblenden (Library of Congress, Prelinger Archive, Periscope Film etc.).
- Ken-Burns (langsamer Push-in 3–6 %) auf Standbildern.
- Balance Ziel: **~50 % Archiv / 50 % Grafik**.

## 5. Motion (für die Umsetzung in Remotion)

- Zahlen **zählen hoch** (count-up) statt hart zu erscheinen.
- Charts **wachsen** von links (stroke-dashoffset / clip).
- Karten-Routen **zeichnen sich** (dashed line draw-on).
- Übergänge: kurze Cuts auf Sprechpausen (siehe `analysis/voiceover_pauses.txt`), gelegentlich Whip/Match-Cut.
- Tempo: ruhig, aber nie statisch — pro Aussage ein visueller Beat.

## 6. Sounddesign

- **Score:** zurückhaltendes, treibendes Doku-Bett (tief, perkussiv), lauter im Hook/Fazit, leiser unter Sprache (Ducking −12 dB).
- **SFX:** UI-Ticks bei Zahlen/Chart-Beats, Whoosh bei Kartenübergängen, dezenter „Schienen/Zug"-Layer in Kapitel-Intros. Sammlung unter `assets/sfx/`.
- VO-Master bereits sauber (−17,8 dB mean). Mix: VO −3 dB peak, Musik darunter.

## 7. Quellen für echtes Material (lizenzkonform)

- **Archiv/Public Domain:** Library of Congress, Internet Archive (Prelinger), Wikimedia Commons.
- **Stock (frei):** Pexels, Pixabay, Coverr.
- **Karten/Daten:** Natural Earth, OpenRailwayMap, eigene Charts.
- Pro Asset: Quelle + Lizenz in `assets/footage/SOURCES.md` dokumentieren.

---

### Style-Frames
Gerenderte Beispiele in `style/frames/out/`:
1. `frame_01_hook.png` — Hook: Länder-Vergleich (Stat-Cards)
2. `frame_02_chart.png` — California HSR Kostenexplosion (Daten-Chart)
3. `frame_03_archival.png` — 1869 Transkontinental (Archiv + Lower-Third + Map-Inset)

Neu rendern: `node style/frames/render.mjs`
