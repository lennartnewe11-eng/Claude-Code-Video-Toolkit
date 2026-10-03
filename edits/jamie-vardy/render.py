#!/usr/bin/env python3
"""Jamie Vardy beat-synced edit renderer (16:9, 1920x1080, 30 fps)."""
import subprocess, sys, math, json, os
import numpy as np
import cv2

# Media lives outside git (copyrighted footage + music). Default: ./media next to this script.
ROOT = os.environ.get("VARDY_MEDIA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "media"))
SRC = {"t10": f"{ROOT}/src/top10.mp4", "cel": f"{ROOT}/src/celebs.mp4"}
SONG = f"{ROOT}/audio/song.wav"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else f"{ROOT}/out/vardy_edit.mp4"
PREVIEW = "--preview" in sys.argv

W, H, FPS = 1920, 1080, 30
T0 = 1.906          # "Destroy it all" – music re-enters after the silence
T_END = 24.700      # end inside the silence gap after bar 8 (cut to black)

# Bar downbeats (hit after each silence gap), measured from the song
H1, H2, H3, H4, H5, H6, H7, H8 = 2.648, 5.408, 8.172, 10.935, 13.699, 16.463, 19.221, 21.985
B = 2.7628          # bar length (86.85 BPM, 4 beats)

def sub(h, k):      # sub-hits inside a bar (16th grid offsets of the cowbell/808 pattern)
    return h + {0: 0, 3: 0.518, 4: 0.691, 6: 1.036, 10: 1.727, 12: 2.072, 13: 2.245, 14: 2.418}[k] * (B / 2.7628)

# crop presets: (x, y, w, h) in source pixels – keep clear of burned-in subs / watermarks
def t10(x=231, w=1458, h=820, y=112):
    return (x, y, w, h)
def cel(x=8, y=70, w=1664, h=936):
    return (x, y, w, h)

# EDL: (song_start, song_end, src, src_in, src_out, crop, extra)
# speed = (src_out - src_in) / (song_end - song_start)
EDL = [
    # HOOK – "Destroy it ALL": corner flag destroyed exactly on the hit (impact src 4.65 -> H1)
    (T0,          sub(H1, 3), "t10", 4.65 - (H1 - T0), 4.65 - (H1 - T0) + (sub(H1, 3) - T0), t10(380), {}),
    # Liverpool volley 2016: slow-mo anticipation, strike lands on H2
    (sub(H1, 3),  H2,         "t10", 139.40, 140.83, t10(120), {"interp": True}),
    (H2,          sub(H2, 3), "t10", 140.83, 141.35, t10(120), {}),
    (sub(H2, 3),  sub(H2, 10),"t10", 143.15, 144.55, t10(462), {}),
    (sub(H2, 10), H3,         "t10", 137.62, 138.66, t10(231), {}),
    # 11 in a row – record breaker vs Man United 2015 (ball in net on H3+0.518)
    (H3,          sub(H3, 6), "cel", 74.03, 75.07, cel(254, 134), {}),
    (sub(H3, 6),  sub(H3, 10),"cel", 76.40, 77.09, cel(128, 134), {}),
    (sub(H3, 10), H4,         "cel", 78.22, 78.95, cel(8, 70), {"interp": True}),
    # DROP – quick-fire finishes on every hit
    (H4,          sub(H4, 3), "t10", 96.55, 97.07, t10(300), {}),          # Spurs volley
    (sub(H4, 3),  sub(H4, 6), "t10", 56.15, 56.67, t10(60), {}),           # Man Utd 2021 strike
    (sub(H4, 6),  sub(H4, 10),"cel", 271.05, 271.74, cel(8, 70), {}),     # Villa 2020 penalty strike
    (sub(H4, 10), sub(H4, 12),"t10", 113.55, 113.90, t10(150), {}),        # Sunderland – rounds keeper
    (sub(H4, 12), sub(H4, 14),"t10", 82.90, 83.25, t10(231), {}),          # Villa
    (sub(H4, 14), H5,         "cel", 130.10, 130.45, cel(8, 70), {}),      # Arsenal 2017 scream
    # Sheffield United 90th-minute winner -> ball in net on the 808 (H5+1.727)
    (H5,          sub(H5, 10),"t10", 27.30, 29.03, (150, 160, 1280, 720), {}),
    (sub(H5, 10), H6,         "t10", 29.03, 30.07, t10(231), {}),
    # THE corner flag – run + slide, impact exactly on H7
    (H6,          H7,         "t10", 30.40, 33.05, t10(400), {"panx": (1.5, 2.5, 400, 0)}),
    (H7,          sub(H7, 6), "t10", 33.05, 33.60, t10(0), {"interp": True}),
    (sub(H7, 6),  sub(H7, 10),"t10", 33.70, 34.50, t10(231), {}),
    (sub(H7, 10), H8,         "t10", 35.62, 36.15, t10(150), {"interp": True}),   # yellow card
    # OUTRO – "VARDY 9", arms spread, slow push-in
    (H8,          T_END,      "cel", 79.40, 79.40 + (T_END - H8), cel(8, 70), {"pushin": 0.08}),
]

def fidx(t):
    return int(round((t - T0) * FPS))

N_TOTAL = fidx(T_END)
BLACK_FROM = fidx(24.614)  # music stops -> black

# Effect events (frame index, kind, strength)
BIG_HITS = [H1, H2, H3, H4, H5, H6, H7, H8]
SMALL_HITS = [sub(H4, 3), sub(H4, 6), sub(H4, 10), sub(H4, 12), sub(H4, 14),
              sub(H1, 3), sub(H2, 3), sub(H2, 10), sub(H3, 6), sub(H3, 10),
              sub(H5, 10), sub(H7, 6), sub(H7, 10)]
FLASH = {H1: 0.85, H2: 0.6, H4: 0.75, H7: 0.9, H5: 0.35, H3: 0.35, H6: 0.3, H8: 0.45}
SHAKE = {H1: 26, H7: 30, H4: 14, H2: 10}


def shot_frames(seg):
    s0, s1, src, a, b, crop, ex = seg
    n = fidx(s1) - fidx(s0)
    speed = (b - a) / (s1 - s0)
    x, y, w, h = crop
    if "panx" in ex:
        t_a, t_b, x0, x1 = ex["panx"]
        xexpr = f"'{x0}+({x1}-{x0})*min(1,max(0,(t-{t_a})/({t_b}-{t_a})))'"
    else:
        xexpr = str(x)
    vf = [f"crop={w}:{h}:{xexpr}:{y}",
          f"scale={W}:{H}:flags=lanczos",
          f"setpts=(PTS-STARTPTS)/{speed:.6f}"]
    if ex.get("interp") and speed < 0.95:
        vf.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    else:
        vf.append(f"fps={FPS}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{(b - a) + 0.6:.3f}",
           "-i", SRC[src], "-an", "-vf", ",".join(vf), "-frames:v", str(n),
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8)
    got = len(frames) // (W * H * 3)
    frames = frames[: got * W * H * 3].reshape(got, H, W, 3)
    out = list(frames)
    while len(out) < n:
        out.append(out[-1])
    return out[:n], speed


def env(f, events, tau):
    v = 0.0
    for fe, amp in events:
        if f >= fe:
            v += amp * math.exp(-(f - fe) / tau)
    return v


def zoom_shift(img, z, dx, dy):
    if z <= 1.0001 and abs(dx) < 0.5 and abs(dy) < 0.5:
        return img
    M = np.float32([[z, 0, (1 - z) * W / 2 + dx], [0, z, (1 - z) * H / 2 + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def main():
    rng = np.random.default_rng(9)
    punch_big = [(fidx(t), 0.10) for t in BIG_HITS]
    punch_small = [(fidx(t), 0.045) for t in SMALL_HITS]
    flash_ev = [(fidx(t), a) for t, a in FLASH.items()]
    shake_ev = [(fidx(t), a) for t, a in SHAKE.items()]
    rgb_ev = [(fidx(t), 14) for t in BIG_HITS] + [(fidx(t), 6) for t in SMALL_HITS]

    enc = None
    if not PREVIEW:
        os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
        enc = subprocess.Popen([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-ss", f"{T0:.3f}", "-t", f"{N_TOTAL / FPS:.3f}", "-i", SONG,
            "-filter_complex",
            "[0:v]eq=contrast=1.07:saturation=1.16:gamma=0.98,unsharp=5:5:0.55:5:5:0.0,"
            "vignette=angle=PI/5.5,format=yuv420p[v];"
            f"[1:a]afade=t=in:st=0:d=0.01,afade=t=out:st={N_TOTAL / FPS - 0.03:.3f}:d=0.03[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level", "4.2",
            "-g", "30", "-bf", "2", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "320k", "-ar", "44100",
            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

    f_global = 0
    log = []
    for i, seg in enumerate(EDL):
        frames, speed = shot_frames(seg)
        n = len(frames)
        log.append((i, round(seg[0], 3), round(seg[1], 3), seg[2], seg[3], seg[4], round(speed, 3), n))
        for k, fr in enumerate(frames):
            f = f_global + k
            img = fr
            if f >= BLACK_FROM:
                img = np.zeros_like(fr)
            else:
                z = 1.0 + env(f, punch_big, 3.2) + env(f, punch_small, 2.2)
                if "pushin" in seg[6]:
                    z *= 1.0 + seg[6]["pushin"] * (k / max(1, n - 1))
                sh = env(f, shake_ev, 4.0)
                dx = dy = 0.0
                if sh > 0.8:
                    dx, dy = rng.uniform(-sh, sh), rng.uniform(-sh, sh)
                    z += sh / 900.0
                img = zoom_shift(img, z, dx, dy)
                c = env(f, rgb_ev, 2.5)
                if c > 0.8:
                    s = int(round(c))
                    b_, g_, r_ = cv2.split(img)
                    r_ = np.roll(r_, s, axis=1)
                    b_ = np.roll(b_, -s, axis=1)
                    img = cv2.merge([b_, g_, r_])
                fl = min(1.0, env(f, flash_ev, 2.4))
                if fl > 0.01:
                    img = cv2.addWeighted(img, 1 - fl, np.full_like(img, 255), fl, 0)
            if PREVIEW:
                os.makedirs(f"{ROOT}/out", exist_ok=True)
                if k == 0 or k == n // 2:
                    cv2.imwrite(f"{ROOT}/out/prev_{i:02d}_{k:03d}.jpg", cv2.resize(img, (480, 270)))
            else:
                enc.stdin.write(img.tobytes())
        f_global += n
    if enc:
        enc.stdin.close()
        enc.wait()
    for row in log:
        print(row)
    print("total frames", f_global, "expected", N_TOTAL, "duration", f_global / FPS)


if __name__ == "__main__":
    main()
