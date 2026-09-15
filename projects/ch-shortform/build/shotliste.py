#!/usr/bin/env python3
"""Schreibt die Shot-Tabelle in docs/akt1_shotliste.md aus der EDL neu.

Die Tabelle von Hand zu pflegen geht schief, sobald sich die Schnittliste
aendert -- der Text stand zuletzt auf 49 Shots, waehrend die EDL 59 hatte.
Kopf und Tabelle stehen deshalb zwischen Markern und werden erzeugt; die
Prosa drumherum (Aufbau, Quellen, Rechte) bleibt unberuehrt.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BEAT = 0.3715

BEGIN, END       = "<!-- shots:begin -->", "<!-- shots:end -->"
KBEGIN, KEND     = "<!-- kopf:begin -->", "<!-- kopf:end -->"

def table(shots):
    out = ["| # | Beat | Dauer | Format | Quelle | In | Grade | Effekte / Maske | Inhalt |",
           "|--:|-----:|------:|--------|--------|---:|-------|-----------------|--------|"]
    for i, s in enumerate(shots):
        fx = " ".join(s.get("fx", [])) or "—"
        if s.get("mask"):
            fx += f" · mask:{s['mask']}"
        si = s.get("src_in")
        # Standbilder haben keinen Einstiegspunkt
        sin = "—" if si is None else f"{si:.1f}s"
        out.append(f"| {i} | {s['beat_in']} | {s['beats']*BEAT:.2f}s | `{s.get('band','wide')}` | "
                   f"{s.get('src')} | {sin} | {s.get('grade','neutral')} | {fx} | {s.get('note','')} |")
    return "\n".join(out)

def main(edl_path=None, doc=None):
    edl_path = edl_path or os.path.join(PROJ, "edl", "act1.json")
    doc = doc or os.path.join(PROJ, "docs", "akt1_shotliste.md")
    shots = json.load(open(edl_path))["shots"]
    beats = shots[-1]["beat_in"] + shots[-1]["beats"]
    head = (f"{beats//4} Takte · {beats} Beats · {beats*BEAT:.2f} s · "
            f"1080×1920 @ 60 fps · 161,5 BPM (Beat = 0,3715 s) · {len(shots)} Shots")

    md = open(doc).read()
    a, b = md.index(KBEGIN), md.index(KEND)
    md = md[:a] + KBEGIN + "\n" + head + "\n" + md[b:]
    a, b = md.index(BEGIN), md.index(END)
    md = md[:a] + BEGIN + "\n\n" + table(shots) + "\n\n" + md[b:]
    open(doc, "w").write(md)
    print(f"{len(shots)} Shots, {beats} Beats ({beats*BEAT:.2f}s) -> {doc}")

if __name__ == "__main__":
    main(*sys.argv[1:])
