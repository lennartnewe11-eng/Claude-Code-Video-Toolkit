# Voice-Over Pipeline (ElevenLabs)

Skript-Text + Sprachprobe → geklontes Voice-Over. Klont deine Stimme über die
ElevenLabs-API (Instant Voice Cloning) und vertont damit ein Skript zu einer
fertigen Audiodatei. Ohne Sprachprobe lässt sich auch jede vorgefertigte Stimme
nutzen.

## Was die Pipeline macht

1. **Klonen** — legt aus einer Sprachprobe eine geklonte Stimme an (`/voices/add`).
2. **Chunking** — teilt das Skript an Satzgrenzen in API-taugliche Stücke.
3. **TTS** — vertont jeden Chunk mit der geklonten Stimme; `previous_text`/
   `next_text` sorgen für nahtlose Übergänge (Prosodie/Betonung).
4. **Zusammenfügen** — fügt die Teile zu einer Datei zusammen (ffmpeg, mit
   Roh-Concat als Fallback).

## Voraussetzungen

- Python 3.10+
- `pip install -r requirements.txt` (`requests`; `imageio-ffmpeg` liefert ein
  ffmpeg-Binary fürs saubere Zusammenfügen, ohne System-Installation)
- Ein **ElevenLabs-API-Key**
- Für das Klonen: mindestens der **Starter-Plan**. Der **Free-Tier kann kein
  Voice-Cloning** (`can_use_instant_voice_cloning: false`) — normale TTS mit
  vorgefertigten Stimmen geht aber.

## Setup

```bash
cd voice-over
pip install -r requirements.txt

# API-Key hinterlegen (wird von .gitignore ausgeschlossen)
cp .env.example .env
# .env öffnen und ELEVENLABS_API_KEY=sk_... eintragen
```

Alternativ per Umgebungsvariable: `export ELEVENLABS_API_KEY=sk_...`

## Skript-PDF → nur Erzähler-Text

Wenn das Skript ein PDF mit Regie-Anweisungen ist (Abschnitte, `GRAFIK:`,
Timings, mehrere Sprecher), zieht `extract_narration.py` nur die zu sprechenden
Passagen heraus:

```bash
# Standard: alle "ERZÄHLER:"-Passagen (inkl. "ERZÄHLER (Schluss):")
python extract_narration.py skript.pdf --out narration.txt

# Anderer Sprecher-Marker
python extract_narration.py skript.pdf --speaker SPRECHER --out narration.txt
```

Übersprungen werden Abschnittsüberschriften, `GRAFIK:`-Hinweise,
`WAHRSCHEINLICHKEIT`/Timing-Zeilen und die Quellen-Fußzeile. Typische
PDF-Artefakte (zerrissene Zeilen, `V or` → `Vor`) werden bereinigt. Danach
`narration.txt` an `voiceover.py --script` übergeben.

## Nutzung

```bash
# 0) Account/Plan prüfen (klärt, ob Cloning freigeschaltet ist)
python voiceover.py --check

# 1) Chunking testen, ohne API-Calls (kostenlos)
python voiceover.py --script script.txt --dry-run

# 2) Stimme klonen + Skript vertonen  (braucht Starter-Plan)
python voiceover.py \
  --script script.txt \
  --sample samples/meine_stimme.mp3 \
  --voice-name "Meine Stimme" \
  --output output/voiceover.mp3

# 3) Mit vorhandener/vorgefertigter Stimme (auch im Free-Tier)
python voiceover.py --list-voices           # IDs anzeigen
python voiceover.py --script script.txt --voice-id <VOICE_ID> \
  --output output/voiceover.mp3
```

### Wichtige Optionen

| Option | Default | Bedeutung |
|---|---|---|
| `--model` | `eleven_multilingual_v2` | TTS-Modell (gute Deutsch-Qualität). Alternativen: `eleven_turbo_v2_5`, `eleven_flash_v2_5` (schneller/günstiger). |
| `--output-format` | `mp3_44100_128` | Free-tier-tauglich. Höhere Bitraten/PCM brauchen höhere Tarife. |
| `--max-chars` | `2000` | Max. Zeichen pro TTS-Request. |
| `--stability` | `0.5` | Niedriger = ausdrucksstärker/variabler, höher = ruhiger/konstanter. |
| `--similarity` | `0.75` | Nähe zur Originalstimme. |
| `--style` | `0.0` | Stil-Übertreibung (erhöht Latenz). |
| `--speed` | `1.0` | Sprechtempo (0.7–1.2 sinnvoll). |
| `--no-speaker-boost` | aus | Speaker-Boost deaktivieren. |

## Tipps für die Sprachprobe (Cloning)

- **1–5 Minuten** sauberes, gleichmäßiges Audio reichen für Instant Cloning.
- Ruhiger Raum, kein Hall, keine Hintergrundmusik, gleichbleibende Lautstärke.
- So sprechen, wie das Voice-Over klingen soll (Tempo, Energie, Tonfall).
- Mehrere Dateien möglich: `--sample a.mp3 --sample b.mp3`.
- Es muss **deine eigene Stimme** sein; ElevenLabs verlangt für Professional
  Cloning zusätzlich eine Einwilligungs-Verifikation.

## Sicherheit

- Der API-Key gehört **nur** in `.env` (per `.gitignore` ausgeschlossen) oder in
  eine Umgebungsvariable — **niemals** in Code oder Commits.
- `samples/` und `output/` sowie alle Audiodateien sind per `.gitignore`
  ausgeschlossen; private Aufnahmen landen nicht im Repo.
- Wird ein Key versehentlich geteilt: bei ElevenLabs im Dashboard rotieren.
