# Footage Credits

## Pexels (Pexels License — free to use, attribution appreciated)

- **"Das ist ein See" → "auch ein See" (Bergsee)** — AP Vibes · https://www.pexels.com/video/aerial-view-of-a-lake-and-mountains-in-the-distance-27671894/
- **"kein See" (leerer Stausee / Vertiefung ohne Wasser)** — Philipp Kappler · https://www.pexels.com/video/drone-view-of-dry-cracked-earth-and-empty-reservoir-37533724/
- **3 Orte / Landschaft** — Serg Alesenko · https://www.pexels.com/video/village-near-forest-on-hills-12418239/
- **Witterung / Wolken** — Yaroslav Shuraev · https://www.pexels.com/video/video-of-a-sky-and-mountains-8025546/
- **Outro-See (Schrumpf-Animation)** — Tom Fisk · https://www.pexels.com/video/a-view-of-the-water-from-a-boat-28043352/

Nicht mehr verwendet (v1/v2): Pfütze (Özgür Sürmeli), Waldsee (Everett Bumstead),
Hochebene (Serg Alesenko), Nebelsee (Matthias Groeneveld).

## Wikimedia Commons (Hauptteil Chunk 2 — Collage-Polaroids)

Frei lizenzierte Bilder (960px-Thumbs), gezogen via `scripts/fetch_commons.py`:

- **Landschaft-BG** — *View from Foggy Peak to Craigieburn Range, New Zealand* · CC BY-SA 4.0
- **See (Luft)** — *Lake Willoughby, October 2021* · CC BY-SA 4.0
- **Bergsee** — *Gurudongmar Lake, Sikkim* · CC BY-SA 4.0
- **Teich** — *Small pond in Waterlea Meadow* · CC BY-SA 2.0
- **Trockenes Becken** — *California Drought Dry Lakebed 2009* · Public Domain
- **Pfütze** — *Reflection in puddle of rain water, Rotterdam* · CC BY-SA 4.0
- **Wasser-Ripples** — *2006-01-14 Surface waves* · CC BY-SA 3.0
- **Bach** — *Black Forest — Stream* · CC BY 2.0
- (für spätere Sieb-Szene vorgehalten: *Soil Texture Samples* CC BY 2.0, *Gravel/Sand Pit* CC BY-SA 2.0)

Cartoon-Eimer (Chunk 2) selbst generiert: `scripts/gen_buckets.py`.

## Nutzer-Footage (vom Auftraggeber bereitgestellt)

- **Regen-Video** (Hauptteil Chunk 2, „in den Regen stellen") — `main_assets/c2/rain.mp4`
- **Baum-/Wolken-Video** (Hauptteil Chunk 3, Lückenfüller) — `main_assets/c3/tree.mp4`
- **Töpfer-/Ton-Video** (Hauptteil Chunk 4, Aufsicht auf drehenden Ton) — `main_assets/c4_clay.mp4`
- **Cartoon-Park, Höhle, Wasserstrom, Gegenlicht-See, Wiese, „See"-Wort-Animation**
  (Hauptteil Chunk 1) — `main_assets/*`

Referenzbilder vom Nutzer (nur als Stil-Vorlage, nicht im Video):
`main_assets/c3/ref_hockney.jpg` (David Hockney „joiner"-Collage),
`main_assets/c3/ref_red_type.jpg` (rotes Plakat-Typo-Design).
Chunk-3-Grafiken selbst generiert: `scripts/gen_hockney.py` (Joiner, aktuell
zurückgestellt), `scripts/gen_sieve.py` (Sand/Kies-Querschnitt, 2 Schichten),
rote Typo in `scripts/build_c3.py`.
S/W-Foto im roten Frame — *Waves sand shadows* (Wikimedia Commons) →
`main_assets/c3/bw.jpg`.

Chunk-4-Vergleichsfotos (Wikimedia Commons): *Nilnag Lake* (See) und
*Cracked dry mud* (staubtrockene Senke) → `main_assets/c4/see.jpg`, `dry.jpg`.
Ton-Querschnitt selbst generiert: `scripts/gen_clay.py`.
Hinweis: der Song (~2:12) wird ab Chunk 4 geloopt, da der Hauptteil länger läuft.

- **Vögel-Intro** & **Schluss-See mit Fahrrädern** — `user_footage/birds.mp4`, `user_footage/lake_bikes.mp4`
- **Mr. Bean** (2×) — `user_footage/mrbean.mp4` · © Tiger Aspect / Rowan Atkinson, nur nutzerseitige Verwendung
- **Song** — `audio/song.mp3` · **Voiceover** — `audio/voiceover.wav`
  (der Song läuft durchgängig; vor „Aber jetzt mal wirklich" nur sehr leise gemischt)

## Hauptteil Chunk 5 (Grundwasser)

- **Mine-Shaft-Descent-Footage** — Archive.org `p-5100006-3` (Public Domain) → `main_assets/c5/mine.mp4` (nicht eingecheckt, re-fetchbar)
- **Wasser-GIF, Spiegel-PNG, Referenzen (blue.jpg, Hand)** — vom Nutzer → `main_assets/c5/`
- **Wikimedia Commons** (Collage/Spiegel-Fill): *Flowing artesian well*, *Suwannee soil water table*, *Ripple and reflections*, *Dramatic clouds Xiyuping* → `main_assets/c5/img/`

## Hauptteil Chunk 6 (Grundwasser II)

- **Sediment-/Unterwasser-Video, Landschafts-GIF, Grain-Figur-GIF** — vom Nutzer → `main_assets/c6/`
- **Inspo-Referenzen** (Editorial-Layouts) → `main_assets/c6/ref_insp1..4.jpg`
- **Wikimedia Commons** (Kaskade): *Carrière Princeville Nord*, *Drina canyon*, *Great Blue Hole Belize* → `main_assets/c6/img/`

## Hauptteil Chunk 7 (Übergang Eiszeit)

- **Wikimedia Commons**: *Bylot Island Glacier* (Eiszeit-Reveal), *Crevasses glacier blue ice* (Eis), *Abandoned slate workings Prince of Wales* (die Löcher) → main_assets/c7/img/

## Hauptteil Chunk 8 (Eiszeit / Becken)

- **Europa-Reliefkarte (Nutzer, Photoroom-Cutout)** fuer die Gletscher-Karten-Animation -> main_assets/c8/img/europe.png
- **Wikimedia Commons**: Bergbau/Sand/Kies (Aside), *Lake Constance/Chiemsee/Kloster Bernried* (Seen-Grid) -> main_assets/c8/img/
- **Echte Gletscher-Textur** fuer den Becken-Querschnitt: *Argentina - Mt Tronador Ascent - 49 - walls of ice* (Wikimedia Commons, CC BY-SA) -> main_assets/c8/img/glaciertex.jpg (greyscale, kontrastverstaerkt in die Animation gesampelt)
- Karten-Eis-Animation und Gletscher-Becken-Querschnitt selbst generiert: scripts/gen_c8.py
- Stil-Referenzen (Nutzer): warme Collage (ref_lakes.jpg), Gelaende-Block (ref_block.jpg). Becken-Querschnitt jetzt grainy S/W; Seen-Grid warm gegradet (Anton-Font).

## Hauptteil Chunk 9 (Fussabdruck / Tiefe / Geschiebemergel)

- **Nutzer-Referenzen** (Zip): Zungen-Foto (Wortwitz Gletscher-ZUNGE) auf Gelb, Editorial-Waveform-Layout, Collage-Stil -> main_assets/c9/ref/ (ref_a/b/c.jpg)
- **Gletscher-Front-Video** (echtes Kalben) aus derselben Referenz -> main_assets/c9/ref/ref_vid.mp4
- **Riss-Ton-Foto** fuer den Geschiebemergel-Liner: wiederverwendet main_assets/c4/dry.jpg (Cracked dry mud, Wikimedia Commons)
- Editorial-Canvas (graue VO-Tonspur + Playhead, Tiefen-Skala mit Koelner-Dom-Vergleich, Geschiebemergel-Mulde + Wasser, 2-in-1-Badge) selbst generiert: scripts/gen_c9.py
- Hinweis: In diesem Part bewusst KEINE gelben Glow-Captions (unlesbar auf Gelb/Weiss; Referenz traegt keine Caption-Leiste) -- die Tonspur repraesentiert die Sprache.

## Hauptteil Chunk 10 (Toteis / runde Loecher / Seenplatte-Karte)

- **Eisblock-Foto** (Nutzer-Referenz) -> main_assets/c10/img/iceblock_orig.jpg; Hero = echtes Foto full-frame (Photoroom-Cutout iceblock.png nur noch in die Formations-Animation gesampelt)
- **Formations-Animation**: Toteis-Querschnitt (Eisblock -> Geroell -> Schmelze -> Einsturz -> rundes Wasserloch) mit editorialer Typografie (Kicker "TOTEIS · DEAD ICE", Anton-Phasentitel 01-04, "SCHRITT"-Ghostzahl, Fortschritts-Punkte) -> scripts/gen_c10.py
- **Relief-Karte** (Nutzer, schattiertes 3D-Rendering MV) -> main_assets/c10/img/relief_mv.jpg; in scripts/gen_c10.py::map_prep aufbereitet: B/W-Hillshade, Alamy-Wasserzeichen entfernt (halbtransparent-weisse, entsaettigte Pixel erkannt + per Diffusion mit Relieftextur aufgefuellt, fetter Mittel-Schriftzug flachgelegt), Fussleiste weggeschnitten. Seen = nur echte cyanfarbene Blobs (B-R>18). (Frueherer Karten-Entwurf map_mv_bb.jpg zurueckgestellt.)
- **Karten-Look = Swiss/Editorial-Poster** (Nutzer-Referenz: Spitzer "Far South", CCNY): gelber Grund (247,233,25), graues Relief, weisses Breiten-/Laengengrad-Gitter (baked, faehrt mit), Seen als pulsierender rot-oranger Akzent. Editorial-Typo (Liberation Sans/Helvetica-Grotesk) statt Laufschrift: Masthead "Toteisloecher / Mecklenburgische Seenplatte", Meta "EISZEIT-ERBE · vor ~15.000 Jahren", aufbauende Statements + See-Daten-Raster (Mueritz 117/Plauer 38/Koelpin 20/Fleesen 11 km²). Captions laufen nur noch ueber Hero+Formation. -> scripts/build_c10.py::_map_ass, scripts/gen_c10.py::map_frames
- **Animations-Referenz** (Nutzer, GIF) -> main_assets/c10/ref/anim_ref.gif (nur Stil-Vorlage)
- Caption-Korrektur: ASR-Verhoerer "sagte" -> "sank" ("sank der Boden ... ein")
