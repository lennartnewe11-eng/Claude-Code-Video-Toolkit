# Projektstatus — USA-Zug-Video

## Was vorliegt
- **Audio/Quelle:** `0615_2.mov` (3840×2160, **Bild durchgehend schwarz**, nur Tonspur), 14:42 / 882 s.
  → Liegt als Upload vor, **nicht** im Repo (Binär). Vor dem Schnitt in `project/footage/` kopieren.
- **Transkript:** WhisperX, 230 Segmente mit Wort-Timing. Aufbereitet als:
  - `transcript.srt` — frame-genaue Untertitel/Cue-Punkte
  - `script_timed.txt` — lesbares Skript mit Timecodes
- **Plan:** `CUT_AND_ANIMATION_PLAN.md` — Hook + 7 Kapitel, jedes Segment mit Footage-Suchbegriff & Animationsidee.

## Netzwerk-Befund (Session 2026-06-17)
Die Policy **„Vertraute Quellen"** erlaubt **nur Entwickler-Paketquellen**, KEINE Medien-/Stock-Seiten:

| erlaubt ✅ | blockiert ❌ (`host_not_allowed`) |
|---|---|
| github.com, raw/objects.githubusercontent.com | YouTube, googlevideo, ytimg |
| pypi.org, registry.npmjs.org | Wikimedia Commons, upload.wikimedia |
| | Pexels, Pixabay, iStock, Vimeo, archive.org |

**Folge:** ffmpeg ließ sich von GitHub installieren; Footage-Download ist **nicht** möglich.

## Nächster Schritt
**Vor der nächsten Session** in den Environment-Einstellungen auf **„Full network access"**
oder **„Custom allowlist"** umstellen (Domains siehe `CUT_AND_ANIMATION_PLAN.md` /
Chat-Anleitung). Erst dann lässt sich echtes Zug-Material laden.

Tools installieren sich automatisch beim Session-Start (`.claude/settings.json` → `project/tools/setup.sh`).
