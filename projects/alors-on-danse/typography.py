"""Lyric typography: one white calligraphic script, synced to the singing.

Every word appears exactly while it is sung: `t` is the sung onset and `d` the
sung duration (song seconds) from lyric_timing.json, measured on the isolated
vocals (tools/lyric_timing.py). The renderer writes each word on over `d`.
Phrases sit in the corners and are cut by the frame edge. Strokes are plain
solid lines: no texture, no ghosted repeats (GHOSTS switches those back on).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

BIG, MID, SMALL = 330, 250, 150
HOLD = 1.3          # seconds a phrase stays after its last word
GAP = 0.06          # a phrase leaves this long before the next one starts
GHOSTS = False      # offset repeats behind key words (read as hatching)

PLACES = {
    "bl": dict(layout="line", anchor="bl", bleed=(0.04, 0.10)),
    "tr": dict(layout="line", anchor="tr", bleed=(0.04, 0.10)),
    "br": dict(layout="line", anchor="br", bleed=(0.04, 0.10)),
    "tl": dict(layout="line", anchor="tl", bleed=(0.04, 0.10)),
    "stack_bl": dict(layout="stack", anchor="bl", bleed=(0.03, 0.06)),
    "stack_tr": dict(layout="stack", anchor="tr", bleed=(0.03, 0.06)),
    "stack_br": dict(layout="stack", anchor="br", bleed=(0.03, 0.06)),
}


def load():
    with open(os.path.join(HERE, "lyric_timing.json")) as f:
        return json.load(f)


def texts():
    L = load()
    T = []

    def phrase(words, where, sizes, layers=None):
        place = PLACES[where]
        step = (0.035, 0.17) if place["anchor"].startswith("t") else (0.035, -0.17)
        ws = []
        for i, w in enumerate(words):
            d = dict(w, size=sizes[i] if i < len(sizes) else sizes[-1])
            if GHOSTS and layers and i < len(layers) and layers[i]:
                d.update(layers=layers[i], step=step)
            ws.append(d)
        T.append(dict(style="script", t0=words[0]["t"], words=ws, **place))

    hook_sizes = (MID, 200, 380)
    hook_layers = (0, 0, 3)

    # intro: the first two "alors on danse"
    phrase(L["hook_intro"][0], "stack_bl", hook_sizes, hook_layers)
    phrase(L["hook_intro"][1], "tr", hook_sizes, hook_layers)

    # verse 1: "qui dit X, dit Y" -- small connectors, big key words, rotating corners
    corners = ["bl", "tr", "br", "tl"]
    for i, ph in enumerate(L["verse"][:-1]):
        sizes = [SMALL if w["text"] in ("qui dit", "dit", "te dit", "et dit") else 300 for w in ph]
        phrase(ph, corners[i % 4], sizes)
    phrase(L["verse"][-1], "bl", (MID, 190, 300))                       # alors on sort

    # chorus 1: every "alors on danse" as it is sung, rotating compositions
    rot = ["stack_bl", "tr", "br", "stack_tr", "bl", "tl", "stack_br", "tr", "bl"]
    for i, ph in enumerate(L["chorus1"]):
        big = i == 0                                                       # the drop
        phrase(ph, rot[i % len(rot)], (300, 220, 460) if big else hook_sizes,
               (0, 0, 4) if big else hook_layers)

    phrase(L["fini"], "tl", (220, 320))                                   # c'est fini
    phrase(L["verse2"][0], "tr", (280,))                                  # les problèmes
    phrase(L["verse2"][1], "bl", (300,))                                  # la musique
    phrase(L["verse2"][2], "br", (220, 340), (0, 2))                      # encore plus fort

    chante = ["tr", "bl", "stack_tr", "bl"]
    for i, ph in enumerate(L["chante"]):
        phrase(ph, chante[i], (MID, 190, 320), (0, 0, 2))

    # "la la la": each sung "la" pops up near a corner
    las = L["la"]
    groups, cur = [], [las[0]]
    for a, b in zip(las, las[1:]):
        if b["t"] - a["t"] > 2.0:
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    for k, g in enumerate(groups):
        T.append(dict(style="scatter", t0=g[0]["t"], seed=3 + 8 * k,
                      items=[dict(w, life=0.9) for w in g], t1=g[-1]["t"] + 0.9))

    phrase(L["predrop"], "bl", (220, 200, 320))                           # quand c'est fini
    phrase(L["drop2"], "stack_bl", (320, 230, 480), (0, 0, 4))            # the drop

    rot2 = ["tr", "stack_br", "tl", "br", "stack_bl", "tr", "bl"]
    for i, ph in enumerate(L["chorus2"]):
        phrase(ph, rot2[i % len(rot2)], hook_sizes, hook_layers)

    for ph, where in zip(L["encore"], ["bl", "tr", "br", "tl", "bl"]):
        phrase(ph, where, (360,), (4,))                                   # encore

    # end times: hold after the last word, leave before the next phrase begins
    T.sort(key=lambda e: e["t0"])
    for a, b in zip(T, T[1:] + [None]):
        if "t1" not in a:
            last = a["words"][-1]
            a["t1"] = last["t"] + last["d"] + HOLD
        if b is not None:
            a["t1"] = min(a["t1"], b["t0"] - GAP)
    return T
