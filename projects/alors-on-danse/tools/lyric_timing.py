"""Build lyric_timing.json: onset/duration (song seconds) of every sung word the
edit shows on screen.

Inputs (from the analysis step, not in the repo):
  words.json        faster-whisper large-v3 word timestamps on the Demucs vocal stem
  seg_words.json    the same on short clips where the full pass skipped repeats
  vocal_onsets.json librosa onsets of the vocal stem
The Demucs stems carry a 25 ms MP3 encoder delay, removed here. Whisper word
starts run ~0.1 s early, so each start is snapped to the first vocal onset in a
small window around it. Only the displayed fragments are stored.

usage: python3 lyric_timing.py ANALYSIS_DIR ../beats.json ../lyric_timing.json
"""
import json
import sys

import numpy as np

adir, beats_path, out_path = sys.argv[1:4]
STEM_DELAY = 0.025
W = json.load(open(f"{adir}/words.json"))
SEG = json.load(open(f"{adir}/seg_words.json"))
ON = np.array(json.load(open(f"{adir}/vocal_onsets.json"))["onsets"]) - STEM_DELAY
BT = json.load(open(beats_path))["beats"]
bar = lambda k: BT[3 + 4 * k]

words = [(w["w"].strip(" ,.").lower(), w["s"] - STEM_DELAY, w["e"] - STEM_DELAY) for w in W]
for seg in SEG.values():  # already delay-corrected
    words += [(w.strip(" ,.").lower(), s, e) for w, s, e, p in seg]


def snap(est, lo=-0.12, hi=0.25):
    c = ON[(ON >= est + lo) & (ON <= est + hi)]
    return round(float(c.min()), 3) if len(c) else round(est + 0.04, 3)


def find(text, near, tol=1.5):
    """Whisper start of `text` closest to `near`."""
    c = [(abs(s - near), s, e) for w, s, e in words if w == text and abs(s - near) < tol]
    if not c:
        raise SystemExit(f"'{text}' not found near {near}")
    return min(c)[1:]


def seq(*items):
    """[(display text, whisper word, approx time)] -> words with snapped onsets + durations."""
    out = []
    for disp, key, near in items:
        if ">" in key:  # a displayed fragment spanning several sung words
            k1, k2 = key.split(">")
            s, _ = find(k1, near)
            _, e = find(k2, near + 0.2)
        else:
            s, e = find(key, near)
        out.append({"text": disp, "t": snap(s), "e": round(e, 3), "raw": s})
    # two quick words can snap onto the same onset: keep the later one on the
    # onset and move the earlier back to its own (bias-corrected) whisper start
    for i in range(len(out) - 1, 0, -1):
        a, b = out[i - 1], out[i]
        if a["t"] > b["t"] - 0.1:
            a["t"] = round(min(a["t"], a["raw"] + 0.04, b["t"] - 0.1), 3)
    for w in out:
        w.pop("raw")
    for a, b in zip(out, out[1:]):
        a["d"] = round(min(0.7, max(0.12, b["t"] - a["t"])), 3)
    out[-1]["d"] = round(min(0.6, max(0.2, out[-1].pop("e") - out[-1]["t"])), 3)
    for w in out:
        w.pop("e", None)
    return out


def hook(k, words3=("Alors", "on", "danse")):
    """'a-lors on DANSE' lands on the grid: danse on the downbeat of bar k."""
    d = bar(k)
    beat = BT[3 + 4 * k] - BT[2 + 4 * k]
    t_danse = snap(d - 0.02, -0.1, 0.15)
    t_on = snap(t_danse - beat, -0.12, 0.12)
    # "a-lors" starts 0.3-0.4 s before "on": the last vocal onset in that gap
    # (earlier onsets still belong to the previous line)
    c = ON[(ON >= t_on - 0.55) & (ON <= t_on - 0.2)]
    t_alors = round(float(c.max()), 3) if len(c) else round(t_on - 0.33, 3)
    ws = [{"text": words3[0], "t": t_alors}, {"text": words3[1], "t": t_on},
          {"text": words3[2], "t": t_danse}]
    ws[0]["d"] = round(t_on - t_alors, 3)
    ws[1]["d"] = round(t_danse - t_on, 3)
    ws[2]["d"] = 0.55
    return ws


L = {}
L["hook_intro"] = [hook(8), hook(10)]
L["verse"] = [
    seq(("qui dit", "qui>dit", 28.8), ("Études", "études", 29.8), ("dit", "dit", 30.4), ("travail", "travail", 30.6)),
    seq(("te dit", "te>dit", 32.4), ("les thunes", "les>thunes", 32.7)),
    seq(("qui dit", "qui>dit", 33.4), ("Argent", "argent", 33.9), ("dit", "dit", 34.5), ("dépenses", "dépenses", 34.7)),
    seq(("qui dit", "qui>dit", 35.5), ("Crédit", "crédit", 35.9), ("dit", "dit", 36.6), ("créances", "créances", 36.8)),
    seq(("qui dit", "qui>dit", 37.6), ("Dette", "dette", 38.0), ("te dit", "te>dit", 38.6), ("huissier", "huissier", 38.9)),
    seq(("qui dit", "qui>dit", 41.6), ("Amour", "amour", 42.0), ("dit", "dit", 42.7), ("les gosses", "les>gosses", 42.8)),
    seq(("dit", "dit", 43.6), ("Toujours", "toujours", 43.8), ("et dit", "et>dit", 44.3), ("divorce", "divorce", 44.9)),
    seq(("qui dit", "qui>dit", 45.7), ("Proches", "proche", 46.1), ("te dit", "te>dit", 46.8), ("deuils", "deuil", 47.1)),
    seq(("qui dit", "qui>dit", 49.6), ("Crise", "christ", 50.1), ("dit", "dit", 52.5), ("tiers-monde", "tiers>-monde", 52.9)),
    seq(("qui dit", "qui>dit", 53.6), ("Fatigue", "fatigue", 54.2), ("dit", "dit", 54.8), ("réveil", "réveil", 55.0)),
    seq(("Alors", "alors", 57.6), ("on", "on", 58.0), ("sort", "sort", 58.3)),
]
L["chorus1"] = [hook(k) for k in range(28, 43, 2)] + [
    seq(("Alors", "alors", 93.1), ("on", "on", 93.5), ("danse", "danse", 93.95))]
L["fini"] = seq(("c'est", "c", 95.5), ("fini", "fini", 95.8))
L["verse2"] = [
    seq(("les problèmes", "les>problèmes", 103.8)),
    seq(("la musique", "la>musique", 105.8)),
    seq(("encore", "encore", 115.5), ("plus fort", "plus>fort", 115.9)),
]
L["chante"] = [
    seq(("Alors", "alors", 117.8), ("on", "on", 118.1), ("chante", "chante", 118.3)),
    seq(("Alors", "alors", 125.56), ("on", "on", 126.0), ("chante", "chante", 126.5)),
    seq(("Alors", "alors", 133.07), ("on", "on", 134.1), ("chante", "chante", 134.64)),
    seq(("Alors", "alors", 141.16), ("on", "on", 142.28), ("chante", "chante", 142.76)),
]
L["la"] = []
for w, s, e in sorted(words, key=lambda x: x[1]):
    if w == "la" and (119.0 <= s <= 124.0 or 127.0 <= s <= 130.5):
        t = snap(s, -0.08, 0.15)
        if not L["la"] or t - L["la"][-1]["t"] >= 0.25:   # drop double detections
            L["la"].append({"text": "la", "t": t, "d": 0.2})
L["predrop"] = seq(("quand", "quand", 147.9), ("c'est", "c", 148.4), ("fini", "fini", 148.7))
# after the silence (149.7-150.3) "alors on danse" comes back, danse on the drop
L["drop2"] = hook(72)
L["chorus2"] = [hook(k) for k in range(74, 87, 2)]
L["encore"] = [seq(("encore", "encore", t)) for t in (183.2, 191.4, 199.5, 207.6, 215.8)]
# the Alors of the hooks can be sung short: clamp its write-on
for grp in ("hook_intro", "chorus1", "chorus2"):
    for ph in L[grp]:
        ph[0]["d"] = round(min(ph[0]["d"], 0.6), 3)
json.dump(L, open(out_path, "w"), ensure_ascii=False, indent=1)
print("wrote", out_path)
for k, v in L.items():
    first = v[0] if isinstance(v[0], dict) else v[0][0]
    print(f"{k:11s} {len(v):2d}  first: {first['text']}@{first['t']}")
