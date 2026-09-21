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
MUSIC_GAIN = 0.708        # -3 dB, headroom for the effect layer


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
    for clip, at, out, rate, look, tin, move in edl.TIMELINE:
        if clip not in meta:
            missing.append(clip); continue
        shots.append(dict(clip=clip, at=at, out=out, rate=rate, look=look,
                          tin=tin, move=move, meta=meta[clip]))
    if missing:
        print(f"WARNUNG: nicht gefunden: {missing}", file=sys.stderr)

    # Work in whole frames, not seconds: rounding 66 segments independently
    # is what let the first cut drift away from the soundtrack length.
    target_frames = round(edl.TARGET_DURATION * FPS)
    k = target_frames / (sum(s["out"] for s in shots) * FPS)
    frames = [max(round(s["out"] * FPS * k), 2) for s in shots]

    # hand the rounding remainder to the longest shots, where it is invisible
    diff = target_frames - sum(frames)
    order = sorted(range(len(frames)), key=lambda i: -frames[i])
    i = 0
    while diff:
        j = order[i % len(order)]
        step = 1 if diff > 0 else -1
        if frames[j] + step >= 2:
            frames[j] += step
            diff -= step
        i += 1

    for idx, (s, f) in enumerate(zip(shots, frames)):
        # the opening shot has no predecessor to cross-fade with, so its
        # transition must not buy extra frames - the final fade-in covers it
        tf = round(s["tin"][1] * FPS) if (s["tin"] and idx) else 0
        s["frames"], s["tframes"] = f, tf
        s["out"] = f / FPS
        s["len_frames"] = f + tf            # extra material for the overlap
        s["len"] = s["len_frames"] / FPS
        src = s["meta"]["dur"]
        # a short source cannot feed a fast ramp for the whole shot; slow the
        # ramp down rather than let the segment come up short and drift
        max_rate = (src - 0.05) / s["len"]
        if s["rate"] > max_rate:
            print(f"  {s['clip']}: Tempo {s['rate']}x -> {max_rate:.2f}x "
                  f"(Quelle nur {src:.1f}s)")
            s["rate"] = max_rate
        need = s["len"] * s["rate"]         # source seconds consumed
        start = s["at"] * src
        if start + need > src - 0.05:       # keep the in-point inside the clip
            start = max(0.0, src - need - 0.05)
        s["start"], s["need"] = start, min(need, src - start)

    assert sum(s["frames"] for s in shots) == target_frames
    return shots


def render_segment(args):
    idx, s = args
    dst = SEG / f"{idx:03d}.mp4"
    if dst.exists():
        return dst
    m = s["meta"]
    chain = looks.build_chain(m["w"], m["h"], s["rate"], s["look"], FPS,
                              move=s.get("move"), frames=s["len_frames"])
    flag = "-filter_complex" if chain.startswith("split") else "-vf"
    spec = f"{chain}[vout]" if flag == "-filter_complex" else chain
    # -t belongs on the INPUT side: as an output option it would cut slow
    # motion short, since `need` is shorter than the shot when rate < 1.
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-ss", f"{s['start']:.3f}", "-t", f"{s['need'] + 0.25:.3f}",
           "-i", str(FOOT / (s["clip"] + ".mov")),
           flag, spec]
    if flag == "-filter_complex":
        cmd += ["-map", "[vout]"]
    cmd += ["-an", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-frames:v", str(s["len_frames"]), str(dst)]
    run(cmd)
    got = count_frames(dst)
    if got != s["len_frames"]:
        raise RuntimeError(
            f"{s['clip']}: {got} Frames statt {s['len_frames']} "
            f"(rate={s['rate']:.2f}, Quelle {s['meta']['dur']:.1f}s)")
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


def count_frames(p):
    r = run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames",
             "-of", "default=nw=1:nk=1", str(p)])
    return int(r.stdout.strip())


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
        head = shots[chunks[n][0]]
        kind = head["tin"][0]
        d = head["tframes"] / FPS
        off = max(acc - d, 0.0)
        out = f"[x{n}]"
        graph.append(f"{prev}[{n}:v]xfade=transition={kind}"
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


def sound_design(shots, total, music_path=None):
    """Place the effect layer against the cut AND the music's own shape.

    Levels are not set in absolute terms: sfx.render reads the music under
    each event, so an accent in a quiet passage stays quiet. `over_db` is
    how far the mix should lift at that moment - the reference sits its
    accents around +5 dB, so that is the default here.
    """
    music = sfx.load_mono(music_path) * MUSIC_GAIN if music_path else None

    events, t, cuts = [], 0.0, []
    for i, s in enumerate(shots):
        cuts.append((t, i, s))
        t += s["out"]

    burst_lo, burst_hi = edl.BURST_RANGE
    for t0, i, s in cuts:
        if i in edl.ACT_STARTS and i > 0:
            events.append((t0 - 2.0, "swell", {"dur": 2.0, "over_db": 4.0}))
            events.append((t0, "drop", {"dur": 1.5, "over_db": 6.5}))
        elif burst_lo <= i < burst_hi:
            events.append((t0, "tick", {"dur": 0.13, "over_db": 3.5}))
        elif s["rate"] >= 3.0:
            events.append((t0 - 0.26, "air_whoosh",
                           {"dur": 0.5, "direction": "up", "over_db": 4.5}))
        elif s["rate"] <= 0.6 and s["tin"]:
            events.append((t0 - 1.0, "reverse_air", {"dur": 1.2, "over_db": 3.5}))
        elif s["tin"] and s["tin"][0] in ("fadewhite", "distance", "pixelize"):
            events.append((t0, "soft_thud", {"dur": 0.5, "over_db": 5.5}))

    # the burst is the one place the layer is allowed to lead
    events.append((cuts[burst_lo][0] - 2.2, "swell", {"dur": 2.2, "over_db": 6.0}))

    # lean on the music's own builds, not only on the cut list
    for sw in edl.MUSIC_SWELLS:
        if 2.0 < sw < total - 3.0:
            quiet = edl.MUSIC_BREAKDOWN[0] <= sw <= edl.MUSIC_BREAKDOWN[1]
            events.append((sw - 0.9, "reverse_air",
                           {"dur": 1.0, "over_db": 2.5 if quiet else 4.0}))

    events = [(max(t, 0.0), k, kw) for t, k, kw in events]
    dst = WORK / "sfx.wav"
    sfx.write_wav(dst, sfx.render(events, total, music_mono=music))
    print(f"  Sounddesign: {len(events)} Effekte, gegen die Musik eingepegelt")
    return dst


def mix_audio(sfx_wav, music_path, total, dst):
    """Sum music and effects with headroom, then soft-limit the result.

    Limiting the effect bus on its own would undo the per-event levels, so
    the ceiling is applied here, once, to the finished mix.
    """
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(music_path), "-i", str(sfx_wav),
         "-filter_complex",
         f"[0:a]volume={MUSIC_GAIN:.4f},atrim=0:{total:.3f},asetpts=N/SR/TB[m];"
         f"[1:a]atrim=0:{total:.3f},asetpts=N/SR/TB[s];"
         f"[m][s]amix=inputs=2:duration=longest:normalize=0[sum];"
         f"[sum]alimiter=limit=0.89:level=disabled,"
         f"afade=t=out:st={total - 4.0:.2f}:d=4.0[a]",
         "-map", "[a]", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_s16le", str(dst)])
    return dst


def main():
    shots = resolve()
    print(f"{len(shots)} Shots, Ziel {edl.TARGET_DURATION:.1f}s")

    print("Segmente rendern ...", flush=True)
    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(render_segment, enumerate(shots)))

    chunks = chunk_shots(shots)
    print(f"Fuegen: {len(chunks)} Bloecke, {len(chunks) - 1} weiche Uebergaenge",
          flush=True)
    video = join(shots, chunks)
    total = probe_dur(video)
    want = sum(s["frames"] for s in shots)
    got = count_frames(video)
    if got != want:
        raise RuntimeError(f"Bildspur {got} Frames statt {want}")
    print(f"Bildspur fertig: {total:.2f}s ({got} Frames, exakt)", flush=True)

    music = ROOT / "music_raw.wav"
    if not music.exists():
        music = None
        print("  WARNUNG: music_raw.wav fehlt - nur Effektspur", flush=True)
    audio = sound_design(shots, total, music)
    if music:
        audio = mix_audio(audio, music, total, WORK / "mix.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ac", "2",
         "-shortest", "-movflags", "+faststart", str(OUTPUT)])
    print(f"\nFERTIG: {OUTPUT}  ({OUTPUT.stat().st_size/1e6:.1f} MB, {total:.2f}s)")


if __name__ == "__main__":
    main()
