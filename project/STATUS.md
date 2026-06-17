# Projektstatus — USA-Zug-Video

## Was vorliegt
- **Audio/Quelle:** `0615_2.mov` (3840×2160, **Bild durchgehend schwarz**, nur Tonspur), 14:42 / 882 s.
  → Liegt als Upload vor, **nicht** im Repo (Binär). Vor dem Schnitt in `project/footage/` kopieren.
- **Transkript:** WhisperX, 230 Segmente mit Wort-Timing. Aufbereitet als:
  - `transcript.srt` — frame-genaue Untertitel/Cue-Punkte
  - `script_timed.txt` — lesbares Skript mit Timecodes
- **Plan:** `CUT_AND_ANIMATION_PLAN.md` — Hook + 7 Kapitel, jedes Segment mit Footage-Suchbegriff & Animationsidee.

## Netzwerk-Befund

### Session 2026-06-17 (a) — Policy „Vertraute Quellen"
Erlaubte **nur** Entwickler-Paketquellen (github.com, pypi.org, npm), KEINE Medien-/Stock-Seiten
(YouTube, Wikimedia, Pexels, Pixabay, archive.org → `host_not_allowed`). ffmpeg installierbar,
Footage-Download nicht möglich.

### Session 2026-06-17 (b) — Policy umgestellt ✅ Medienquellen offen
Nach der Umstellung sind die Medienquellen jetzt erreichbar (getestet):

| Quelle | Status |
|---|---|
| github.com, pypi.org | ✅ |
| YouTube | ✅ erreichbar, **aber** „Sign in to confirm you're not a bot" (Anti-Bot bei Rechenzentrums-IP) → nur mit Cookies nutzbar |
| Wikimedia Commons / upload.wikimedia | ✅ **end-to-end getestet** (API-Suche + 2,2 MB JPEG-Download) |
| archive.org, Vimeo | ✅ erreichbar |
| Pexels, Pixabay | ✅ erreichbar (Server liefert 403 ohne API-Key/Browser → API-Key nötig) |

**Empfohlene Footage-Quellen** (lizenzkonform, ohne Bot-Hürde): **Wikimedia Commons** (CC) und
**archive.org**. Pexels/Pixabay nur mit API-Key. YouTube nur mit Browser-Cookies.

### TLS-Proxy-Hinweis (wichtig für yt-dlp)
Das Environment leitet HTTPS über einen **TLS-inspizierenden Proxy** (envoy, self-signed CA).
`curl` und Python-`urllib` vertrauen ihm über das System-Bundle; **yt-dlp** nutzt jedoch sein
eigenes `certifi` und scheiterte mit `CERTIFICATE_VERIFY_FAILED`. **Fix ist in `setup.sh`
eingebaut** (Proxy-CA wird beim Session-Start an certifi angehängt) — läuft automatisch.

## Nächster Schritt
Netzwerk steht. Jetzt kann echtes Material geladen werden — z. B. Hook-Footage gemäß
`CUT_AND_ANIMATION_PLAN.md`. Vor dem Schnitt `0615_2.mov` nach `project/footage/` kopieren
(Upload, nicht im Repo).

Tools installieren sich automatisch beim Session-Start (`.claude/settings.json` → `project/tools/setup.sh`).
