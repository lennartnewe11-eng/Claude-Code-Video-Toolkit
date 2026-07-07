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

## Hauptteil Chunk 11 (Rinnenseen / Schleswig-Holstein)

- **SH-Reliefkarte** (Nutzer) -> main_assets/c11/img/sh_relief.png; in scripts/gen_c11.py::sh_poster_prep zum STATISCHEN Swiss-Poster aufbereitet: gelber Grund, graues B/W-Hillshade, weisses Gradnetz; Strassen/Fluesse/Beschriftung per Klassifikation + Diffusion entfernt. Original-Ausrichtung (Ostsee = Osten/rechts; Nutzer: Beschriftung egal, nicht spiegeln). Rinnenseen = sizable inland-Blaublobs -> pulsierender rot-oranger Akzent. Grosse Helvetica-Typo (Masthead "Rinnenseen", Meta "TUNNELTAELER", Statements + See-Daten Gr. Ploener 30/Selenter 22/Kellersee 5 km²). KEINE Kamerafahrt.
- **Aesthetischer Filler = GIF** (Nutzer) -> main_assets/c11/img/filler.gif, gezeigt im 35mm-Film-Kamera-Look: prozeduraler Filmstreifen (Perforation, Bildnummern 14/14A, Tick-Lineal, Light-Leaks) in scripts/gen_c11.py::film_frame, GIF spielt im Fenster, warm gegradet.
- **Film-Look-Referenz** (Nutzer) -> main_assets/c11/img/glencoe_film.jpg (35mm-Negativ eines Gletschertals; nur Stil-Vorlage fuer den Filmrahmen, nicht als Inhalt gezeigt)
- **Hochdruckreiniger** (Nutzer-Cutout, Kaercher HD 7/16-4 MXA Produktbild) -> main_assets/c11/img/washer.png; bei "Hochdruckreiniger" auf weissem Grund mit grosser blauer Editorial-Typo HINTER und VOR dem Bild ("HOCHDRUCK" / "REINIGER") -> scripts/gen_c11.py::washer_hero
- **"Rinnen in die Landschaft" = glaziofluviale Schmelzwasser-Rinnen (Luftbild)** -> main_assets/c11/img/rinnen.jpg · *Glaciofluvial* von Mike Beauregard (Nunavut, Kanada), **CC BY 2.0**, Wikimedia Commons; warm gegradet mit Push-in
- Captions (gelber Glow) laufen nur ueber die dunkleren Footage-Beats (GIF-Film + Rinnen); Poster + weisse Hochdruckreiniger-Editorial tragen eigene Typo. Fix: blauer Glow (versehentliche BGR-Outline-Farbe) an der Poster-Schrift entfernt. -> scripts/build_c11.py

## Hauptteil Chunk 12 (Deutschlandkarte - Payoff: Seen folgen dem Eis)

- **Deutschland-Reliefkarte** (Nutzer, RGBA-Schummerung) -> main_assets/c12/img/de_relief.png; in scripts/gen_c12.py zum Swiss-Poster aufbereitet (gelber Grund, graues B/W-Hillshade, weisses Gradnetz).
- Die Karte hat KEINE eingezeichneten Seen -> die beiden See-Ballungen werden als rot-orange Punkt-Cluster gezeigt: NORDEN (Schleswig-Holstein + Mecklenburgische Seenplatte + Havelland) und SUEDEN (Alpenvorland inkl. Bodensee); die Mitte bleibt leer. Cluster enthuellen synchron zum VO (Norden@233.3, Sueden@236.2, Mitte@240.5).
- Kleine Kamerafahrten (sanfter Push-in + leichte N->S->weit-Drift) in scripts/gen_c12.py::_cam.
- Grosse prominente Editorial-Typo (Anton-Masthead "DEUTSCHLAND", rot-orange "IM NORDEN"/"IM SUEDEN"/"DIE MITTE: FAST LEER", Meta "SEENVERTEILUNG folgt dem Eis", getaktete Tags). ASS-Farben in korrektem BGR. -> scripts/build_c12.py
- Keine Laufschrift; die Typo traegt die Erzaehlung.

## Hauptteil Chunk 13 (Eifel-Vulkanismus / Maare - "nicht nur das Eis")

- **Vulkanvideo** (Nutzer) -> main_assets/c13/img/volcano.mp4; Himmel per Helligkeit/Blau-Key ausgeschnitten und auf Weiss gelegt, VOLLE BREITE am unteren Bildrand; darum herum gelayerte gelbe Editorial-Typo (MAGMA hinter dem Kegel, EIFEL als Outline davor, Kicker "NICHT NUR DAS EIS"). Sky-Key + Komposition in scripts/gen_c13.py::volcano_frames.
- **Dauner-Maare-Luftbild** (Nutzer) -> main_assets/c13/img/maar.jpg; die drei kreisrunden Maar-Seen mit rot-orangen Ringen hervorgehoben, warm gegradet, sanfter Push-in, Typo "MAARE / kreisrunde Krater · voll Wasser / Vulkaneifel". -> scripts/build_c13.py::beat_maar
- Editorial-Typo traegt den Part; keine Laufschrift.

## Hauptteil Chunk 14 (Altarme + Tagebau Hambach - "die anderen Seemacher, und wir")

- **Referenz-Collage** (Nutzer, altarme.zip) -> main_assets/c14/img/ref.jpg; Vorlage fuer den Layout-Look: grosses freigestelltes Motiv sweept rechts durch den kuehlen Editorial-Grund, kleine Bodytext-Spalte in den linken Negativraum genestet, Spiel mit EBENEN (Geistwort hinter dem Cutout, Masthead/Body auf dem Grund, rot-orange Annotation davor).
- **Fluss-Cutout / Altarme** (Nutzer-Cutout, RGBA, gerissene Kanten) -> main_assets/c14/img/river.png; als Hero rechts platziert; Geistwort "SCHLINGEN" HINTER dem Cutout, Masthead "ALTARME" + gesetzte Bodytext-Definition + Fussnote "Altarm - Oxbow - Bras mort" links, rot-orange handgezeichnete Ringmarkierung ("hier schnuert sich der Bogen ab") VOR dem Fluss, dann Pivot "der fleissigste Seebauer der Gegenwart - WIR SELBST." (SELBST. in Gelb). -> scripts/gen_c14.py::river_frames
- **Tagebau-Hambach-Zeitraffer** (Nutzer, Satelliten-Timelapse mit Jahreszahlen) -> main_assets/c14/img/tagebau.mp4; in einem gerissenen Fenster rechts (Jahreslabels bleiben sichtbar), Geistwort "LAUSITZ" dahinter, links "TAGEBAU WIRD SEE" + Body + rot-orange "laeuft voll -> neuer See" + gelbe Punchwoerter "RIESIG. BRANDNEU.". -> scripts/gen_c14.py::tagebau_frames
- Schlichter WEISSER Editorial-Grund (nur ein Hauch neutrales Korn, keine Vignette/Scanline). Ringmarkierung sitzt schraeg rechts oben und umkreist die zwei tatsaechlich abgeschnuerten Altarme (Wasserblobs per Helligkeit/Saettigung detektiert), Label 'abgeschnuerte Boegen: zwei Altarme' im rechten Weissraum. Typo in die Frames gebacken, keine Laufschrift. -> scripts/build_c14.py

## Hauptteil Chunk 15 (DIE BEDINGUNG - Collage-Rebuild + Verlandungs-Auftakt, 2 Teile)

- **Teil 1 (0-12s):** die universelle Formel als Cutaway-Collage. Das Erdreich ist ein echter BODEN-QUERSCHNITT (Nutzer, soil.jpg) als Textur - die Grube ist in die Schichten geschnitten (tiefer = aeltere Straten). Darin ein echter 3-DIMENSIONALER CUTAWAY-SEE: das ANIMIERTE (generierte) Wasser ist der QUERSCHNITT (der verborgene Unterwasser-Teil, eine blaue Schale, die in die Bodenschichten reicht - das was man normalerweise nicht sieht); das BOOT-VIDEO (Nutzer, lakewater.mp4, ruhiger See mit Ruderboot) ist die Wasser-OBERFLAECHE, in die Ellipse gelegt; und die freigestellte VEGETATION (Nutzer, veg.png; Himmel + offenes Wasser gekeyt) ist NICHT gerade, sondern GEKRUEMMT um den fernen Ellipsenrand gelegt - ihre Rundung suggeriert Tiefe und umschliesst den Platz fuer das Boot-Video. Gras-Fransen auf der Oberflaeche. Editorial-Gleichung 1 EIN BECKEN + 2 GENUG WASSER = EIN SEE (gelb), sonst -> '„TROCKENE SENKE"' (rot) mit Rissen. -> scripts/gen_c15.py
- **Break open (~12s):** der Frame bricht auf - das WASSER-VIDEO (Nutzer, water.mp4) schiebt sich per xfade=smoothup hoch; darueber die FRAU (Nutzer, woman.mp4), heller Hintergrund per lumakey entfernt, mit geringer Sichtbarkeit (aa=0.30) eingeblendet, so dass nur ihre Silhouette geistert.
- **Teil 2 (12-16.5s):** Wasser + Frau, jetzt mit den GELBEN Glow-Untertiteln zurueck (Cap-Style &H0000E9F4, blur7) fuer 'Eine Sache solltest du wissen ... Kein See bleibt fuer immer!' -> scripts/build_c15.py
- VO 272.94->289.44, Song-Offset 349.84. Ersetzt den frueheren rein-generierten c15-Entwurf.

## Hauptteil Chunk 16 - DAS FINALE (VO 289.44 -> 313.90, Videoende)

- **Beat A - Verlandung:** nebliger Daemmerungssee (Nutzer, lake.mp4) mit gelben Glow-Untertiteln - "Von allen Seiten rieselt Sand, Laub und Schlamm hinein, vom Ufer her wuchern Schilf und Pflanzen nach innen."
- **Beat B - See -> Sumpf -> Wiese:** grosse Editorial-Progression SEE -> SUMPF -> WIESE (Anton, weiss mit Glow), baut sich zur VO auf ("aus dem See wird ein Sumpf ... eine Wiese").
- **Beat C - der Schluss:** die PUSTEBLUME (Nutzer, pusteblume.mp4) als Symbol der Vergaenglichkeit, dann Voegel im Sonnenaufgang (Nutzer, birds.mp4). Die poetischen Schlusszeilen ("nichts Ewiges - nur ein kurzer nasser Moment ... wir haben das Glueck, ihn erleben zu duerfen") als VERSTREUTE, leuchtende Titel-Woerter durcheinander ueber dem Bild - nach Nutzer-Referenz (ref_title.jpg, Titel-Sequenz-Look) in Wellen (NICHTS/EWIGES -> NUR EIN KURZER NASSER MOMENT -> GESCHICHTE EINER LANDSCHAFT -> WIR HABEN DAS GLUECK ERLEBEN ZU DUERFEN).
- Footage per xfade verbunden, einheitlicher Film-Grade + Vignette + Korn; Schlussblende auf Schwarz. Song-Offset 366.34. -> scripts/build_c16.py

## Gesamtschnitt (main_full) - das ganze Video am Stueck

- Alle 16 Chunks (main_chunk1..16) per concat-Demuxer BILD-only aneinandergeschnitten (Stream-Copy, kein Requalitaetsverlust an den Schnitten) -> build/master/master_v.mp4 (~317 s).
- Tonspur KOMPLETT NEU durchgehend unterlegt statt der Clip-Audios: eine einzige VO-Spur (main_vo.wav, ab 0 - Chunk 1 startet bei VO 0, die Chunks sind lueckenlos aneinandergereiht) + EIN durchgehend geloopter Musik-Bett (song.mp3), unter die Stimme geduckt (sidechaincompress). Dadurch keine Audio-Spruenge und keine mitten im Satz beginnenden/endenden Uebergaenge. VO per apad bis Videoende verlaengert (Musik traegt den ~3 s Finale-Tail), sanfte Ein-/Ausblende. -> scripts/build_master.py
- Ausgaben: out/main_full.mp4 (Bild-Copy, volle Qualitaet ~201 MB), out/main_full_1080p.mp4 (crf23 ~118 MB), out/main_full_720p.mp4 (~24 MB Vorschau).
