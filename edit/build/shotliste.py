"""SHOTLISTE.md from the EDL -- generated, so it cannot drift from the cut.

    python3 build/shotliste.py
"""
from collections import Counter
from pathlib import Path

import edl
import render


def main():
    shots = edl.shots()
    rows = ["| # | Beats | Länge | Zeit | Quelle | Anker | fx | Text |", "|--:|---|--:|---|---|---|---|---|"]
    lengths, fx = Counter(), Counter()
    for i, s in enumerate(shots):
        n = s["b1"] - s["b0"]
        lengths[n] += 1
        for f in s.get("fx", ()):
            fx[f] += 1
        if not s.get("fx"):
            fx["(ohne)"] += 1
        t = (render.tb(s["b0"]) - render.tb(edl.B0))
        src = s.get("src") or ("split: " + " + ".join(p["src"] for p in s["panels"]) if "panels" in s else "schwarz")
        at = s.get("at")
        anchor = f"{at[0]:g}s → {at[1]:g}" if at else ""
        text = s.get("label") or s.get("title") or s.get("end") or ""
        rows.append(f"| {i} | {s['b0']}–{s['b1']} | {n:g} | {t:5.2f}s | `{src}` | {anchor} | "
                    f"{' '.join(s.get('fx', ()))} {s.get('grade', '')} | {text.replace('|', ' ')} |")
    total = render.fb(edl.B_END) / render.FPS
    md = [f"# Shotliste", "",
          f"Aus `build/edl.py` erzeugt (`python3 build/shotliste.py`). "
          f"{len(shots)} Shots, {edl.B_END - edl.B0} Beats, {total:.2f} s.", "",
          *rows, "", "## Schnittlängen", "", "| Beats | Anzahl |", "|--:|--:|",
          *[f"| {k:g} | {v} |" for k, v in sorted(lengths.items())], "",
          "## Effekte", "", "| fx | Shots |", "|---|--:|",
          *[f"| `{k}` | {v} |" for k, v in fx.most_common()], ""]
    dst = Path(__file__).resolve().parent.parent / "SHOTLISTE.md"
    dst.write_text("\n".join(md))
    print("wrote", dst)


if __name__ == "__main__":
    main()
