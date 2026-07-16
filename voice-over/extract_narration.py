#!/usr/bin/env python3
"""
Extrahiert aus einem Skript-PDF nur die zu sprechenden Erzaehler-Passagen.

Nimmt alle Zeilen, die mit "ERZÄHLER:" (auch "ERZÄHLER (Schluss):") beginnen,
inkl. ihrer Fortsetzungszeilen, und ueberspringt Regie/Struktur (Abschnitts-
ueberschriften, GRAFIK-Hinweise, WAHRSCHEINLICHKEIT/Timing, Quellen-Fusszeile).
Bereinigt typische PDF-Extraktionsartefakte (zerissene Zeilen, "V or" -> "Vor").

Nutzung:
    python extract_narration.py skript.pdf --out narration.txt
    python extract_narration.py skript.pdf --out narration.txt --speaker ERZÄHLER
"""

import argparse
import re
import sys
from pathlib import Path

import fitz  # pymupdf


def pdf_to_text(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def is_structural(s: str) -> bool:
    if re.match(r"^\d+\.\s+[A-ZÄÖÜ„]", s):          # "2. SZENARIO ..."
        return True
    if s.startswith("GRAFIK"):
        return True
    if "WAHRSCHEINLICHKEIT" in s:  # nur echte Regie-Zeile; blosser "—" ist Satzzeichen
        return True
    if re.match(r"^\(?\d+:\d+", s):                  # "7:00)" / "(4:00–"
        return True
    if " · " in s or s.startswith('for Everything'):  # Quellen-Fusszeile
        return True
    return False


def clean(text: str) -> str:
    # "V or..." -> "Vor...", "V olks" -> "Volks", "V ier" -> "Vier"
    text = re.sub(r"\bV ([a-zäöü])", r"V\1", text)
    # fehlendes Leerzeichen nach Doppelpunkt: "Berufen:verhält" -> "Berufen: verhält"
    text = re.sub(r"([a-zäöüß]):([A-Za-zÄÖÜ])", r"\1: \2", text)
    # Mehrfach-Whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract(text: str, speaker: str) -> list[str]:
    marker = re.compile(rf"^{re.escape(speaker)}\s*(\([^)]*\))?\s*:\s*(.*)$")
    blocks: list[list[str]] = []
    cur: list[str] | None = None
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        m = marker.match(s)
        if m:
            if cur is not None:
                blocks.append(cur)
            cur = [m.group(2)] if m.group(2) else []
        elif cur is not None:
            if is_structural(s):
                blocks.append(cur)
                cur = None
            else:
                cur.append(s)
    if cur is not None:
        blocks.append(cur)

    paras = [clean(" ".join(b)) for b in blocks]
    return [p for p in paras if p]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="Pfad zum Skript-PDF")
    ap.add_argument("--speaker", default="ERZÄHLER",
                    help="Sprecher-Marker (Default: ERZÄHLER)")
    ap.add_argument("--out", default="narration.txt", help="Ziel-Textdatei")
    args = ap.parse_args()

    text = pdf_to_text(args.pdf)
    paras = extract(text, args.speaker)
    if not paras:
        sys.exit(f"Keine '{args.speaker}'-Passagen gefunden.")

    out = "\n\n".join(paras) + "\n"
    Path(args.out).write_text(out, encoding="utf-8")
    print(f"{len(paras)} Passagen, {sum(len(p) for p in paras)} Zeichen -> {args.out}")


if __name__ == "__main__":
    main()
