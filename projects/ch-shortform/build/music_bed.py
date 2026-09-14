#!/usr/bin/env python3
"""Baut das Musikbett: ein Splice, damit der Breakdown des Tracks
genau auf den Vibe Shift des Skripts faellt.

Der Track laeuft durchgehend auf einem Raster (161.5 BPM, beat=0.3715s,
offset=0.0474s, std ueber 493 beats = 9.8ms). Ein Schnitt von Rasterpunkt a
nach Rasterpunkt b bleibt rhythmisch nahtlos, solange (b-a) % 4 == 0 --
dann bleibt auch die Taktphase erhalten.
"""
import json, subprocess, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SRC  = "/root/.claude/uploads/fbc32e5c-a9f9-58cd-90f3-b3c31c377e20/f83e78bf-converted_1789402615979.mp3"

BEAT   = 0.3715
OFFSET = 0.0474
BAR    = BEAT * 4

def bt(n):        # Zeit des Beats n im Originaltrack
    return OFFSET + n * BEAT

# --- Splice-Punkte (Beat-Indizes im Original) --------------------------------
N_START   = 3      # 1.1619s  erster hoerbarer Downbeat
N_CUT     = 95     # Ende Akt 1 (23 Takte)
N_BREAK   = 295    # 109.6455s Breakdown beginnt (Bass faellt weg)
N_END     = 395    # 146.7899s Ende

ACTS = [
    # name,            beat_from, beat_to
    ("act1_aufbruch",  N_START,  N_CUT),    # 23 Takte
    ("act2_3_shift",   N_BREAK,  N_END),    # 25 Takte (8 Breakdown + 17 Drop)
]

# --- Programmierte Aussetzer (Video-Zeit, Sekunden) --------------------------
# Skript: "letztes bild leere Spielplaetze. Ohne Hintergrund Musik kurze Stille"
def _mutes():
    """Ein Takt Stille direkt vor dem Drop-in. Wird aus der Aktstruktur
    berechnet, damit es stimmt, waehrend Akt 1 weiter waechst."""
    act1 = (N_CUT - N_START) * BEAT           # Laenge Akt 1
    drop = act1 + 8 * BAR                     # Akt 2 = 8 Takte Breakdown
    return [(round(drop - BAR, 4), round(drop, 4))]

MUTES = _mutes()

def main():
    out_dir = os.path.join(PROJ, "assets", "audio")
    os.makedirs(out_dir, exist_ok=True)

    parts, vt, marks = [], 0.0, []
    for name, a, b in ACTS:
        t0, t1 = bt(a), bt(b)
        parts.append((t0, t1 - t0))
        marks.append({"act": name, "video_in": round(vt, 4),
                      "video_out": round(vt + (t1 - t0), 4),
                      "src_in": round(t0, 4), "src_out": round(t1, 4),
                      "bars": round((b - a) / 4, 2)})
        vt += t1 - t0

    total = vt
    # (b-a) % 4 Kontrolle
    assert (N_BREAK - N_CUT) % 4 == 0, "Splice zerstoert die Taktphase"

    # ffmpeg: zwei Segmente schneiden, concat, Mutes als volume-Automation
    vol = "".join(f",volume=enable='between(t,{m0},{m1})':volume=0" for m0, m1 in MUTES)
    # 6ms Mikro-Blende an der Splice-Kante -> kein Klick, Laenge bleibt exakt
    F = 0.006
    fc = ""
    for i, (ss, d) in enumerate(parts):
        fc += (f"[0:a]atrim=start={ss}:duration={d},asetpts=PTS-STARTPTS,"
               f"afade=t=in:st=0:d={F},afade=t=out:st={d-F:.6f}:d={F}[a{i}];")
    fc += "".join(f"[a{i}]" for i in range(len(parts)))
    fc += f"concat=n={len(parts)}:v=0:a=1[cat];"
    fc += f"[cat]afade=t=out:st={total-0.9:.4f}:d=0.9{vol},loudnorm=I=-14:TP=-1.0:LRA=11[out]"

    dst = os.path.join(out_dir, "music_bed.wav")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", SRC,
           "-filter_complex", fc, "-map", "[out]",
           "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst]
    subprocess.run(cmd, check=True)

    grid = {
        "bpm": 161.5, "beat": BEAT, "bar": BAR,
        "total_duration": round(total, 4),
        "n_beats": round(total / BEAT),
        "n_bars": round(total / BAR, 2),
        "acts": marks,
        "mutes": MUTES,
        # Video-Beatraster startet bei 0 und laeuft durch (Splice ist rasterfest)
        "video_beats": [round(i * BEAT, 4) for i in range(int(total / BEAT) + 1)],
        "video_downbeats": [round(i * BAR, 4) for i in range(int(total / BAR) + 1)],
        "source": os.path.basename(SRC),
    }
    json.dump(grid, open(os.path.join(PROJ, "analysis", "timeline_grid.json"), "w"), indent=1)

    print(f"music bed -> {dst}")
    print(f"Gesamt {total:.3f}s  |  {grid['n_beats']} beats  |  {grid['n_bars']} Takte")
    for m in marks:
        print(f"  {m['act']:16s} video {m['video_in']:7.3f} -> {m['video_out']:7.3f}  "
              f"({m['bars']:5.1f} Takte)  src {m['src_in']:8.3f}-{m['src_out']:8.3f}")
    print(f"  Aussetzer: {MUTES}")

if __name__ == "__main__":
    main()
