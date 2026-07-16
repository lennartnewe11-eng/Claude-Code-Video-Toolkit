#!/usr/bin/env python3
"""
Voice-Over Pipeline (ElevenLabs)

Nimmt ein Skript (Text) + optional eine Sprachprobe (Audio) und erzeugt ein
Voice-Over. Mit --sample wird die Stimme geklont (Instant Voice Cloning, ab
Starter-Plan), mit --voice-id wird eine bestehende/vorgefertigte Stimme genutzt.

Beispiele:
    # Stimme klonen und Skript vertonen
    python voiceover.py --script script.txt --sample samples/meine_stimme.mp3 \
        --voice-name "Meine Stimme" --output output/voiceover.mp3

    # Mit bereits geklonter/vorhandener Stimme
    python voiceover.py --script script.txt --voice-id <VOICE_ID> \
        --output output/voiceover.mp3

    # Verfuegbare Stimmen anzeigen
    python voiceover.py --list-voices

    # Nur Chunking pruefen, keine API-Calls (kostet nichts)
    python voiceover.py --script script.txt --dry-run

Der API-Key wird aus der Umgebungsvariable ELEVENLABS_API_KEY oder aus einer
.env-Datei neben diesem Skript gelesen (Zeile: ELEVENLABS_API_KEY=...).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

API_BASE = "https://api.elevenlabs.io/v1"
SCRIPT_DIR = Path(__file__).resolve().parent


# --------------------------------------------------------------------------- #
# Konfiguration / Auth
# --------------------------------------------------------------------------- #
def load_api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        env_file = SCRIPT_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("ELEVENLABS_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        sys.exit(
            "FEHLER: Kein API-Key gefunden.\n"
            "  -> Setze ELEVENLABS_API_KEY oder lege voice-over/.env mit\n"
            "     ELEVENLABS_API_KEY=sk_... an."
        )
    return key


def api_headers(api_key: str, extra: dict | None = None) -> dict:
    h = {"xi-api-key": api_key}
    if extra:
        h.update(extra)
    return h


# --------------------------------------------------------------------------- #
# Account / Stimmen
# --------------------------------------------------------------------------- #
def get_subscription(api_key: str) -> dict:
    r = requests.get(
        f"{API_BASE}/user/subscription", headers=api_headers(api_key), timeout=30
    )
    r.raise_for_status()
    return r.json()


def list_voices(api_key: str) -> list[dict]:
    r = requests.get(f"{API_BASE}/voices", headers=api_headers(api_key), timeout=30)
    r.raise_for_status()
    return r.json().get("voices", [])


def create_voice_clone(
    api_key: str, name: str, sample_paths: list[Path], description: str | None
) -> str:
    """Instant Voice Cloning. Braucht mindestens den Starter-Plan."""
    files = []
    open_handles = []
    try:
        for p in sample_paths:
            fh = open(p, "rb")
            open_handles.append(fh)
            files.append(("files", (p.name, fh, "application/octet-stream")))
        data = {"name": name}
        if description:
            data["description"] = description
        r = requests.post(
            f"{API_BASE}/voices/add",
            headers=api_headers(api_key),
            data=data,
            files=files,
            timeout=300,
        )
    finally:
        for fh in open_handles:
            fh.close()

    if r.status_code != 200:
        raise RuntimeError(
            f"Voice-Cloning fehlgeschlagen (HTTP {r.status_code}): {r.text}\n"
            "Hinweis: Instant Voice Cloning ist erst ab dem Starter-Plan verfuegbar."
        )
    return r.json()["voice_id"]


# --------------------------------------------------------------------------- #
# Text -> Chunks
# --------------------------------------------------------------------------- #
def split_text(text: str, max_chars: int = 2000) -> list[str]:
    """Teilt Text an Satzgrenzen in Chunks <= max_chars auf."""
    text = re.sub(r"[ \t]+", " ", text.strip())
    # Absaetze respektieren, aber innerhalb nach Saetzen splitten
    raw_sentences = re.split(r"(?<=[.!?…])\s+|\n{2,}", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    chunks: list[str] = []
    current = ""
    for s in sentences:
        if len(s) > max_chars:
            # Sehr langer Satz: hart an Wortgrenzen zerlegen
            if current:
                chunks.append(current)
                current = ""
            words = s.split(" ")
            piece = ""
            for w in words:
                if len(piece) + len(w) + 1 <= max_chars:
                    piece = (piece + " " + w).strip()
                else:
                    chunks.append(piece)
                    piece = w
            if piece:
                current = piece
            continue

        if not current:
            current = s
        elif len(current) + len(s) + 1 <= max_chars:
            current = current + " " + s
        else:
            chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    return chunks


# --------------------------------------------------------------------------- #
# TTS
# --------------------------------------------------------------------------- #
def synthesize_chunk(
    api_key: str,
    voice_id: str,
    text: str,
    model_id: str,
    voice_settings: dict,
    out_path: Path,
    output_format: str,
    previous_text: str | None = None,
    next_text: str | None = None,
) -> None:
    body = {"text": text, "model_id": model_id, "voice_settings": voice_settings}
    if previous_text:
        body["previous_text"] = previous_text
    if next_text:
        body["next_text"] = next_text

    r = requests.post(
        f"{API_BASE}/text-to-speech/{voice_id}",
        headers=api_headers(
            api_key, {"Content-Type": "application/json", "Accept": "audio/mpeg"}
        ),
        params={"output_format": output_format},
        json=body,
        timeout=300,
    )
    if r.status_code != 200:
        raise RuntimeError(f"TTS fehlgeschlagen (HTTP {r.status_code}): {r.text}")
    out_path.write_bytes(r.content)


# --------------------------------------------------------------------------- #
# Audio zusammenfuegen
# --------------------------------------------------------------------------- #
def find_ffmpeg() -> str | None:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def concat_audio(parts: list[Path], out_path: Path) -> str:
    """Fuegt MP3-Teile zusammen. Nutzt ffmpeg (sauber) oder faellt auf
    Roh-Byte-Concat zurueck. Gibt die verwendete Methode zurueck."""
    if len(parts) == 1:
        shutil.copyfile(parts[0], out_path)
        return "single"

    ff = find_ffmpeg()
    if ff:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as lf:
            for p in parts:
                lf.write(f"file '{p.resolve()}'\n")
            list_path = lf.name
        try:
            subprocess.run(
                [ff, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
                 "-c", "copy", str(out_path)],
                check=True,
                capture_output=True,
            )
            return "ffmpeg"
        finally:
            os.unlink(list_path)
    else:
        with open(out_path, "wb") as out:
            for p in parts:
                out.write(p.read_bytes())
        return "raw-concat"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def build_voice_settings(args) -> dict:
    return {
        "stability": args.stability,
        "similarity_boost": args.similarity,
        "style": args.style,
        "use_speaker_boost": not args.no_speaker_boost,
        "speed": args.speed,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Voice-Over aus Skript + (optional) geklonter Stimme erzeugen.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--script", help="Pfad zur Skript-Textdatei (.txt).")
    ap.add_argument("--output", default="output/voiceover.mp3",
                    help="Ziel-Audiodatei (Default: output/voiceover.mp3).")

    voice = ap.add_mutually_exclusive_group()
    voice.add_argument("--sample", action="append", metavar="AUDIO",
                       help="Sprachprobe(n) zum Klonen. Mehrfach angebbar.")
    voice.add_argument("--voice-id", help="ID einer vorhandenen/vorgefertigten Stimme.")

    ap.add_argument("--voice-name", default="Meine Stimme",
                    help="Name fuer die geklonte Stimme.")
    ap.add_argument("--voice-description", help="Beschreibung der geklonten Stimme.")

    ap.add_argument("--model", default="eleven_multilingual_v2",
                    help="TTS-Modell (Default: eleven_multilingual_v2, gut fuer Deutsch).")
    ap.add_argument("--output-format", default="mp3_44100_128",
                    help="Audio-Format (Default: mp3_44100_128, free-tier-tauglich).")
    ap.add_argument("--max-chars", type=int, default=2000,
                    help="Max. Zeichen pro TTS-Request (Default: 2000).")

    # Voice settings
    ap.add_argument("--stability", type=float, default=0.5)
    ap.add_argument("--similarity", type=float, default=0.75)
    ap.add_argument("--style", type=float, default=0.0)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--no-speaker-boost", action="store_true")

    # Utility
    ap.add_argument("--list-voices", action="store_true",
                    help="Verfuegbare Stimmen anzeigen und beenden.")
    ap.add_argument("--check", action="store_true",
                    help="Account/Plan pruefen und beenden.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur Chunking anzeigen, keine API-Calls (kostet nichts).")

    args = ap.parse_args()

    # Dry-run braucht keinen Key
    if args.dry_run:
        if not args.script:
            sys.exit("FEHLER: --dry-run braucht --script.")
        text = Path(args.script).read_text(encoding="utf-8")
        chunks = split_text(text, args.max_chars)
        total = sum(len(c) for c in chunks)
        print(f"Skript: {len(text)} Zeichen -> {len(chunks)} Chunk(s), "
              f"{total} Zeichen an TTS.")
        for i, c in enumerate(chunks, 1):
            preview = c[:70].replace("\n", " ")
            print(f"  [{i:>2}] {len(c):>4} Zeichen | {preview}...")
        return

    api_key = load_api_key()

    if args.check:
        sub = get_subscription(api_key)
        print(f"Tier: {sub['tier']}")
        print(f"Zeichen: {sub['character_count']}/{sub['character_limit']}")
        print(f"Instant Voice Cloning: {sub['can_use_instant_voice_cloning']}")
        print(f"Professional Cloning:  {sub['can_use_professional_voice_cloning']}")
        return

    if args.list_voices:
        for v in list_voices(api_key):
            print(f"{v['voice_id']}  {v['name']:<24} ({v.get('category', '?')})")
        return

    if not args.script:
        sys.exit("FEHLER: --script wird benoetigt (oder nutze --list-voices/--check).")

    # Stimme bestimmen
    if args.sample:
        sample_paths = [Path(s) for s in args.sample]
        for p in sample_paths:
            if not p.exists():
                sys.exit(f"FEHLER: Sprachprobe nicht gefunden: {p}")
        print(f"Klone Stimme aus {len(sample_paths)} Datei(en) ...")
        voice_id = create_voice_clone(
            api_key, args.voice_name, sample_paths, args.voice_description
        )
        print(f"  -> Voice-ID: {voice_id}")
    elif args.voice_id:
        voice_id = args.voice_id
    else:
        sys.exit("FEHLER: Entweder --sample (klonen) oder --voice-id angeben.")

    # Skript vertonen
    text = Path(args.script).read_text(encoding="utf-8")
    chunks = split_text(text, args.max_chars)
    settings = build_voice_settings(args)
    print(f"Skript: {len(text)} Zeichen -> {len(chunks)} Chunk(s).")

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = SCRIPT_DIR / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        parts: list[Path] = []
        for i, chunk in enumerate(chunks):
            part = Path(tmp) / f"part_{i:03d}.mp3"
            prev_text = chunks[i - 1] if i > 0 else None
            next_text = chunks[i + 1] if i < len(chunks) - 1 else None
            print(f"  TTS Chunk {i + 1}/{len(chunks)} ({len(chunk)} Zeichen) ...")
            synthesize_chunk(
                api_key, voice_id, chunk, args.model, settings, part,
                args.output_format, prev_text, next_text,
            )
            parts.append(part)

        method = concat_audio(parts, out_path)

    size_kb = out_path.stat().st_size / 1024
    print(f"\nFertig: {out_path}  ({size_kb:.0f} KB, zusammengefuegt via {method})")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Ausgabe wurde abgeschnitten (z. B. via `| head`) – kein Fehler.
        try:
            sys.stdout.close()
        except Exception:
            pass
    except KeyboardInterrupt:
        sys.exit(130)
