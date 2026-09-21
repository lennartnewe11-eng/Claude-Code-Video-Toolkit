#!/usr/bin/env python3
"""Render the edit decision list into the finished 16:9 film."""
import json, subprocess, sys, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).parent))
import looks, edl, sfx

ROOT   = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
FOOT   = ROOT / "footage"
WORK   = ROOT / "work"; WORK.mkdir(exist_ok=True)
SEG    = WORK / "seg";  SEG.mkdir(exist_ok=True)
OUTPUT = ROOT / "montage_16x9.mp4"
FPS    = 30
XFADE  = {"fade": "fade", "black": "fadeblack", "white": "fadewhite"}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed:\n{' '.join(map(str,cmd))}\n{r.stderr[-1500:]}")
    return r


def resolve():
    """Turn the EDL into concrete in-points and render lengths."""
    meta = {Path(c["name"]).stem: c
            for c in json.loads((ROOT/"analysis/manifest.json").read_text())}
    shots, missing = [], []
    for clip, at, out, rate, look, tin in edl.TIMELINE:
        if clip not in meta:
            missing.append(clip); continue
        shots.append(dict(clip=clip, at=at, out=out, rate=rate, look=look,
                          tin=tin, meta=meta[clip]))
    if missing:
        print(f"WARNUNG: nicht gefunden: {missing}", file=sys.stderr)

    # stretch the visible durations so the film matches the soundtrack exactly
    k = edl.TARGET_DURATION / sum(s["out"] for s in shots)
    for s in shots:
        s["out"] *= k
        tdur = s["tin"][1] if s["tin"] else 0.0
        s["len"] = s["out"] + tdur          # extra material for the overlap
        need = s["len"] * s["rate"]         # source seconds consumed
        src = s["meta"]["dur"]
        start = s["at"] * src
        if start + need > src - 0.05:       # keep the in-point inside the clip
            start = max(0.0, src - need - 0.05)
        s["start"], s["need"] = start, min(need, src - start)
    return shots


def render_segment(args):
    idx, s = args
    dst = SEG / f"{idx:03d}.mp4"
    if dst.exists():
        return dst
    m = s["meta"]
    chain = looks.build_chain(m["w"], m["h"], s["rate"], s["look"], FPS)
    flag = "-filter_complex" if chain.startswith("split") else "-vf"
    spec = f"{chain}[vout]" if flag == "-filter_complex" else chain
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-ss", f"{s['start']:.3f}", "-i", str(FOOT / (s["clip"] + ".mov")),
           "-t", f"{s['need']:.3f}", flag, spec]
    if flag == "-filter_complex":
        cmd += ["-map", "[vout]"]
    cmd += ["-an", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-t", f"{s['len']:.3f}", str(dst)]
    run(cmd)
    return dst


def chunk_shots(shots):
    """Group consecutive hard cuts; a soft transition starts a new chunk."""
    chunks, cur = [], []
    for i, s in enumerate(shots):
        if s["tin"] and cur:
            chunks.append(cur); cur = []
        cur.append(i)
    if cur:
        chunks.append(cur)
    return chunks


def concat(indices, dst):
    lst = WORK / f"concat_{dst.stem}.txt"
    lst.write_text("".join(f"file '{(SEG / f'{i:03d}.mp4').resolve()}'\n" for i in indices))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(dst)])
    return dst


def probe_dur(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(p)])
    return float(r.stdout.strip())


def join(shots, chunks):
    parts = [concat(c, WORK / f"chunk{n:02d}.mp4") for n, c in enumerate(chunks)]
    durs = [probe_dur(p) for p in parts]
    if len(parts) == 1:
        return parts[0]

    inputs, graph, acc, prev = [], [], durs[0], "[0:v]"
    for n in range(1, len(parts)):
        kind, d = shots[chunks[n][0]]["tin"]
        off = max(acc - d, 0.0)
        out = f"[x{n}]"
        graph.append(f"{prev}[{n}:v]xfade=transition={XFADE[kind]}"
                     f":duration={d:.3f}:offset={off:.3f}{out}")
        acc = acc + durs[n] - d
        prev = out
    for p in parts:
        inputs += ["-i", str(p)]

    total = acc
    graph.append(f"{prev}fade=t=in:st=0:d=1.6,fade=t=out:st={total-3.0:.2f}:d=3.0[v]")
    dst = WORK / "video_only.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(graph), "-map", "[v]",
         "-c:v", "libx264", "-crf", "18", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(dst)])
    return dst


def sound_design(shots, total):
    """Place whooshes, impacts and risers against the actual cut points."""
    events, t = [], 0.0
    cuts = []
    for i, s in enumerate(shots):
        cuts.append((t, i, s))
        t += s["out"]

    burst_lo, burst_hi = edl.BURST_RANGE
    for t0, i, s in cuts:
        if i in edl.ACT_STARTS and i > 0:
            events.append((t0 - 2.2, "riser", {"dur": 2.2, "intensity": 0.9}))
            events.append((t0, "sub_drop", {"dur": 2.4, "intensity": 1.0}))
            events.append((t0, "impact", {"dur": 1.3, "intensity": 0.95}))
        elif burst_lo <= i < burst_hi:
            if (i - burst_lo) % 2 == 0:
                events.append((t0, "impact", {"dur": 0.45, "pitch": 88,
                                              "intensity": 0.45}))
        elif s["rate"] >= 3.0:
            events.append((t0 - 0.30, "whoosh", {"dur": 0.55, "direction": "up",
                                                 "intensity": 0.6}))
        elif s["rate"] <= 0.6 and s["tin"]:
            events.append((t0 - 1.1, "reverse_swell", {"dur": 1.4,
                                                       "intensity": 0.45}))
        elif s["tin"] and s["tin"][0] == "white":
            events.append((t0, "impact", {"dur": 0.9, "intensity": 0.8}))

    events.append((cuts[burst_lo][0] - 2.4, "riser", {"dur": 2.4, "intensity": 1.0}))
    events = [(max(t, 0.0), k, kw) for t, k, kw in events]
    dst = WORK / "sfx.wav"
    sfx.write_wav(dst, sfx.render(events, total))
    print(f"  Sounddesign: {len(events)} Effekte platziert")
    return dst


def main():
    shots = resolve()
    print(f"{len(shots)} Shots, Ziel {edl.TARGET_DURATION:.1f}s")

    print("Segmente rendern ...", flush=True)
    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(render_segment, enumerate(shots)))

    chunks = chunk_shots(shots)
    print(f"Fuegen: {len(chunks)} Bloecke, "
          f"{sum(1 for s in shots if s['tin'])} weiche Uebergaenge", flush=True)
    video = join(shots, chunks)
    total = probe_dur(video)
    print(f"Bildspur fertig: {total:.2f}s", flush=True)

    audio = sound_design(shots, total)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ac", "2",
         "-shortest", "-movflags", "+faststart", str(OUTPUT)])
    print(f"\nFERTIG: {OUTPUT}  ({OUTPUT.stat().st_size/1e6:.1f} MB, {total:.2f}s)")


if __name__ == "__main__":
    main()
