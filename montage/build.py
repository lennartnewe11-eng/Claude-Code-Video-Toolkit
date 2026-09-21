#!/usr/bin/env python3
"""Render the edit decision list into the finished 16:9 film."""
import json, subprocess, sys, shutil
import numpy as np
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
MUSIC_GAIN = 0.708        # -3 dB, headroom for the other layers
AMB_GAIN   = 0.10         # -20 dB: the clips' own sound as texture, not a track


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed:\n{' '.join(map(str,cmd))}\n{r.stderr[-1500:]}")
    return r


def resolve():
    """Turn the EDL into concrete in-points and render lengths.

    Cut positions are accumulated in BEATS and converted to frames once,
    at the end. Converting each shot on its own and adding the results up
    lets rounding drift, and the cuts then walk off the beat.
    """
    meta = {Path(c["name"]).stem: c
            for c in json.loads((ROOT/"analysis/manifest.json").read_text())}
    shots, missing = [], []
    for clip, at, beats, rate, look, tin, move, amb in edl.TIMELINE:
        if clip not in meta:
            missing.append(clip); continue
        shots.append(dict(clip=clip, at=at, beats=beats, rate=rate, look=look,
                          tin=tin, move=move, amb=amb, meta=meta[clip]))
    if missing:
        print(f"WARNUNG: nicht gefunden: {missing}", file=sys.stderr)

    target_frames = round(edl.TARGET_DURATION * FPS)
    # The detected grid starts at GRID_OFFSET, not at zero. The film has to
    # start at zero, so the opening shot absorbs the offset and every cut
    # after it lands on a beat.
    pos, cum = [0.0], 0.0
    for s in shots:
        cum += s["beats"]
        pos.append(edl.GRID_OFFSET + cum * edl.BEAT)
    # No scaling. Stretching the grid to land exactly on the end walks every
    # cut off the beat - 0.1% over two and a half minutes is several frames.
    # The grid is left alone and the closing shot takes up the remainder,
    # where it is under the fade to black anyway.
    fpos = [round(p * FPS) for p in pos]
    fpos = [min(f, target_frames) for f in fpos]
    fpos[-1] = target_frames
    for i in range(1, len(fpos)):                 # no zero-length shot
        if fpos[i] <= fpos[i - 1]:
            fpos[i] = fpos[i - 1] + 2
    if fpos[-1] != target_frames:                 # keep the total exact
        fpos[-1] = max(fpos[-2] + 2, target_frames)

    for i, s in enumerate(shots):
        f = fpos[i + 1] - fpos[i]
        tf = round(s["tin"][1] * FPS) if (s["tin"] and i) else 0
        s["frames"], s["tframes"] = f, tf
        s["at_frame"] = fpos[i]
        s["out"] = f / FPS
        s["len_frames"] = f + tf
        s["len"] = s["len_frames"] / FPS

        src = s["meta"]["dur"]
        head = max(0.5, s["len"] * s["rate"] * 0.20)
        max_rate = max((src - head) / s["len"], 0.05)
        if s["rate"] > max_rate:
            print(f"  {s['clip']}: Tempo {s['rate']}x -> {max_rate:.2f}x "
                  f"(Quelle nur {src:.1f}s)")
            s["rate"] = max_rate
        need = s["len"] * s["rate"]
        st = s["at"] * src
        if st + need + head > src:
            st = max(0.0, src - need - head)
        s["start"], s["need"] = st, need
        s["head"] = min(head, max(src - st - need, 0.0))

    assert sum(s["frames"] for s in shots) == target_frames
    return shots


def render_segment(args):
    idx, s = args
    dst = SEG / f"{idx:03d}.mp4"
    if dst.exists():
        return dst
    m = s["meta"]
    # the move ramps over the SOURCE frames it will actually see
    src_frames = max(int(round(s["need"] * (m["fps"] or FPS))), 2)
    chain = looks.build_chain(m["w"], m["h"], s["rate"], s["look"], FPS,
                              move=s.get("move"), src_frames=src_frames)
    flag = "-filter_complex" if chain.startswith("split") else "-vf"
    spec = f"{chain}[vout]" if flag == "-filter_complex" else chain
    # -t belongs on the INPUT side: as an output option it would cut slow
    # motion short, since `need` is shorter than the shot when rate < 1.
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-ss", f"{s['start']:.3f}", "-t", f"{s['need'] + s['head']:.3f}",
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
    # not named `run`: that is the module-level ffmpeg helper, and shadowing
    # it here breaks the call above this line
    tail = frozen_tail(dst)
    allowed = int(1 / s["rate"]) + 2 if s["rate"] < 1 else 2
    if tail > allowed:
        raise RuntimeError(
            f"{s['clip']}: Standbild am Ende - {tail} gleiche Frames "
            f"(erlaubt {allowed} bei Tempo {s['rate']:.2f}x)")
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


def frozen_tail(path, look=16, size=(64, 36)):
    """How many identical frames the segment ends on.

    Slow motion repeats frames by design, so the caller compares this
    against what its rate implies; what this catches is a source that ran
    out and left the fps filter holding one frame.
    """
    w, h = size
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-sseof", "-2", "-i", str(path),
         "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
        capture_output=True)
    buf = r.stdout
    n = len(buf) // (w * h)
    if n < 2:
        return 0
    frames = [buf[i * w * h:(i + 1) * w * h] for i in range(max(n - look, 0), n)]
    same = 1
    for a, b in zip(reversed(frames), reversed(frames[:-1])):
        if a == b:
            same += 1
        else:
            break
    return same


def count_frames(p):
    r = run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames",
             "-of", "default=nw=1:nk=1", str(p)])
    return int(r.stdout.strip())


def probe_dur(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(p)])
    return float(r.stdout.strip())


def join(shots, chunks, want_frames):
    parts = [concat(c, WORK / f"chunk{n:02d}.mp4") for n, c in enumerate(chunks)]
    if len(parts) == 1:
        return parts[0]

    # Offsets are accumulated in FRAMES. Adding them up in float seconds
    # across a chain of cross-fades drifts, and one frame of drift is
    # enough to miss the soundtrack length.
    lens = [count_frames(p) for p in parts]

    inputs, graph, acc, prev = [], [], lens[0], "[0:v]"
    for n in range(1, len(parts)):
        head = shots[chunks[n][0]]
        kind, df = head["tin"][0], head["tframes"]
        off = max(acc - df, 0) / FPS
        out = f"[x{n}]"
        graph.append(f"{prev}[{n}:v]xfade=transition={kind}"
                     f":duration={df / FPS:.4f}:offset={off:.4f}{out}")
        acc += lens[n] - df
        prev = out
    for p in parts:
        inputs += ["-i", str(p)]

    total = want_frames / FPS
    graph.append(f"{prev}fade=t=in:st=0:d=1.6,fade=t=out:st={total-3.0:.2f}:d=3.0[v]")
    dst = WORK / "video_only.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(graph), "-map", "[v]",
         # -frames:v pins the result: xfade can still land a frame either
         # side of the arithmetic, and the length has to be exact
         "-frames:v", str(want_frames),
         "-c:v", "libx264", "-crf", "18", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(dst)])
    return dst


def _atempo_chain(rate):
    """atempo only accepts 0.5-2.0 per stage, so decompose the rate."""
    parts, r = [], float(rate)
    while r < 0.5:
        parts.append(0.5); r /= 0.5
    while r > 2.0:
        parts.append(2.0); r /= 2.0
    parts.append(r)
    return ",".join(f"atempo={x:.6f}" for x in parts)


def ambience(shots, total, dst):
    """The clips' own sound, quietly, under the music.

    Only the shots flagged for it, and only as texture: waves, a train, a
    room. Each piece is speed-matched to its shot, faded at both ends so a
    cut never clicks, and the whole bus is set well below the music.
    """
    flagged = [(i, s) for i, s in enumerate(shots)
               if s.get("amb") and s["meta"].get("audio")]
    if not flagged:
        return None

    bus = np.zeros(int(sfx.SR * total) + sfx.SR, dtype=np.float64)
    tmp = WORK / "amb"; tmp.mkdir(exist_ok=True)
    used = 0
    for i, s in flagged:
        piece = tmp / f"{i:03d}.wav"
        if not piece.exists():
            try:
                run(["ffmpeg", "-y", "-loglevel", "error",
                     "-ss", f"{s['start']:.3f}", "-t", f"{s['need']:.3f}",
                     "-i", str(FOOT / (s["clip"] + ".mov")),
                     "-vn", "-af", _atempo_chain(s["rate"]),
                     "-ac", "1", "-ar", str(sfx.SR),
                     "-c:a", "pcm_s16le", str(piece)])
            except RuntimeError:
                continue
        a = sfx.load_mono(piece)
        if a.size < 400:
            continue
        want = int(s["out"] * sfx.SR)
        a = a[:want] if a.size >= want else np.pad(a, (0, want - a.size))
        # fade both ends; a hard edge on room tone reads as a click
        f = min(int(0.08 * sfx.SR), a.size // 3)
        if f > 1:
            a[:f] *= np.linspace(0, 1, f)
            a[-f:] *= np.linspace(1, 0, f)
        start = int(s["at_frame"] / FPS * sfx.SR)
        end = min(start + a.size, bus.size)
        if end > start:
            bus[start:end] += a[:end - start]
            used += 1

    peak = np.max(np.abs(bus))
    if peak < 1e-6:
        return None
    sfx.write_wav(dst, np.stack([bus, bus], axis=1))
    print(f"  Originalton: {used} Shots als leise Ebene")
    return dst


def sound_design(shots, total, music_path=None):
    """A quiet click layer: a steady pulse over the opening, then sparse.

    The opening runs clicks on a fixed beat interval so they read as a
    rhythm rather than as scattered accents. After that the layer thins
    out to act changes and the staccato passage only.
    """
    music = sfx.load_mono(music_path) * MUSIC_GAIN if music_path else None

    events, t, cuts = [], 0.0, []
    for i, s in enumerate(shots):
        cuts.append((t, i, s))
        t += s["out"]

    # steady pulse over the opening
    lo, hi, every = edl.OPENING_PULSE
    step = edl.BEAT * every
    k = 0
    while True:
        tp = edl.GRID_OFFSET + lo + k * step
        if tp > hi:
            break
        # a light accent every fourth click gives the pulse a bar feel
        strong = (k % 4 == 0)
        events.append((tp, "tick", {"dur": 0.12 if strong else 0.09,
                                    "over_db": 2.2 if strong else 1.4}))
        k += 1

    burst_lo, burst_hi = edl.BURST_RANGE
    for t0, i, s in cuts:
        if i in edl.ACT_STARTS and i > 0:
            events.append((t0, "tick", {"dur": 0.14, "over_db": 2.4}))
            events.append((t0 - 0.9, "reverse_air", {"dur": 1.0, "over_db": 1.2}))
        elif burst_lo <= i < burst_hi and (i - burst_lo) % 2 == 0:
            events.append((t0, "tick", {"dur": 0.09, "over_db": 1.8}))

    events = [e for e in events if 0.3 < e[0] < total - 9.0]
    events = sorted((max(t, 0.0), k, kw) for t, k, kw in events)
    dst = WORK / "sfx.wav"
    sfx.write_wav(dst, sfx.render(events, total, music_mono=music,
                                  ceiling_over_bed=4.0))
    print(f"  Sounddesign: {len(events)} Klicks, davon {k} als Puls im Vorspann")
    return dst


def mix_audio(sfx_wav, music_path, total, dst, amb_wav=None):
    """Sum music, the clips' own sound and the click layer, then limit once.

    Levels: the music carries the film, the ambience sits well under it as
    texture, the clicks only mark. Limiting any single bus on its own would
    undo the per-event levels, so the ceiling is applied here, to the sum.
    """
    inputs = ["-i", str(music_path), "-i", str(sfx_wav)]
    chain = (f"[0:a]volume={MUSIC_GAIN:.4f},atrim=0:{total:.3f},"
             f"asetpts=N/SR/TB[m];"
             f"[1:a]atrim=0:{total:.3f},asetpts=N/SR/TB[s];")
    mixin = "[m][s]"
    n = 2
    if amb_wav:
        inputs += ["-i", str(amb_wav)]
        # ducked under the music and rolled off top and bottom, so it reads
        # as room rather than as a second soundtrack
        chain += (f"[2:a]volume={AMB_GAIN:.4f},highpass=f=120,lowpass=f=9000,"
                  f"atrim=0:{total:.3f},asetpts=N/SR/TB[a];")
        mixin = "[m][s][a]"
        n = 3
    chain += (f"{mixin}amix=inputs={n}:duration=longest:normalize=0[sum];"
              f"[sum]alimiter=limit=0.89:level=disabled,"
              f"afade=t=out:st={total - 4.0:.2f}:d=4.0[out]")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", chain, "-map", "[out]", "-ac", "2",
         "-ar", "48000", "-c:a", "pcm_s16le", str(dst)])
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
    want = sum(s["frames"] for s in shots)
    video = join(shots, chunks, want)
    total = probe_dur(video)
    got = count_frames(video)
    if got != want:
        raise RuntimeError(f"Bildspur {got} Frames statt {want}")
    print(f"Bildspur fertig: {total:.2f}s ({got} Frames, exakt)", flush=True)

    music = ROOT / "music_raw.wav"
    if not music.exists():
        music = None
        print("  WARNUNG: music_raw.wav fehlt - nur Effektspur", flush=True)
    audio = sound_design(shots, total, music)
    amb = ambience(shots, total, WORK / "amb.wav")
    if music:
        audio = mix_audio(audio, music, total, WORK / "mix.wav", amb)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ac", "2",
         "-shortest", "-movflags", "+faststart", str(OUTPUT)])
    print(f"\nFERTIG: {OUTPUT}  ({OUTPUT.stat().st_size/1e6:.1f} MB, {total:.2f}s)")


if __name__ == "__main__":
    main()
