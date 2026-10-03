#!/usr/bin/env python3
"""Paul Pogba beat-synced edit on Stromae – "Alors on danse" (16:9, 1920x1080, 30 fps).

Every "danse" lands on a 2-bar downbeat; each one gets a goal or a dance.
"""
import subprocess, sys, math, os, json
import numpy as np
import cv2

# Media lives outside git (copyrighted footage + music). Default: ./media next to this script.
ROOT = os.environ.get("POGBA_MEDIA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "media"))
SRC = {k: f"{ROOT}/src/{v}.mp4" for k, v in
       {"P": "peak", "W": "wcfinal", "U": "udinese", "D": "dance_show", "E": "euro2020"}.items()}
SONG = f"{ROOT}/audio/song.wav"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else f"{ROOT}/out/pogba_edit.mp4"
PREVIEW = "--preview" in sys.argv

W, H, FPS = 1920, 1080, 30

# Beat grid measured from the kick drum: 118.02 BPM
BEAT = 0.5084
def B(k):
    return 55.0105 + BEAT * k

K_START, K_DROP, K_END = 5, 13, 49   # "Alors on sort pour oublier…" -> drop on "danse" -> 11 bars total
T0, T_END = B(K_START), B(K_END)

# crop windows (x, y, w, h) per source – keep clear of logos, tickers, subtitles, letterbox
CROP = {
    "P": (0, 135, 1440, 810),      # 4:3 source, bilibili watermark top-left
    "W": (100, 134, 1036, 583),    # CCTV5 logo, scoreboard + sponsor tag on top
    "U": (100, 40, 1600, 900),     # burned-in subs bottom, logo bottom-right
    "D": (170, 96, 939, 528),      # letterboxed 2.42:1 inside 720p
    "E": (266, 175, 1387, 780),    # title/ticker on top, subs bottom
}
BAILLY = (40, 96, 939, 528)

# EDL: (beat_in, beat_out, src, src_in, src_out, crop|None, extras)
EDL = [
    # BUILD – "Alors on sort pour oublier tous les problèmes, alors on…"
    (5, 7,   "D", 8.20, 9.25,    None, {"pushin": 0.05}),     # tunnel, World Cup trophy, sparklers
    (7, 9,   "D", 18.30, 19.30,  None, {"pushin": 0.05}),     # arms spread in the smoke
    (9, 11,  "U", 86.00, 87.00,  None, {"pushin": 0.06}),     # the stare (Juve)
    (11, 13, "P", 132.02, 132.64, None, {"interp": True}),     # Napoli volley: ball drops… slow-mo
    # DROP – "DANSE": contact on the downbeat
    (13, 15, "P", 132.64, 133.80, None, {}),                   # …volley, top corner
    (15, 17, "P", 141.08, 141.72, None, {"interp": True}),     # Juve arms spread, slow-mo
    (17, 19, "P", 84.30, 85.30,  (0, 200, 1440, 810), {}),    # skill vs Leeds (below scoreboard)
    (19, 21, "W", 76.00, 76.98,  None, {}),                    # World Cup final 2018: the shot
    # "DANSE" 2 – ball in the net, arms spread
    (21, 23, "W", 86.40, 87.40,  None, {}),
    (23, 27, "W", 88.55, 90.58,  None, {}),
    (27, 29, "D", 21.20, 22.20,  None, {}),                    # smoke dab
    # "DANSE" 3 – dance block, cut every 2 beats
    (29, 31, "D", 161.30, 162.32, BAILLY, {}),                 # Bailly x Pogba
    (31, 33, "D", 88.00, 89.00,  (200, 96, 939, 528), {}),                    # Old Trafford night dance
    (33, 35, "D", 57.20, 58.20,  (300, 96, 939, 528), {}),                    # Lingard x Pogba
    (35, 37, "D", 46.10, 47.10,  None, {}),                    # point
    # "DANSE" 4 – swagger
    (37, 39, "P", 153.10, 154.10, None, {}),                   # Swansea celebration
    (39, 41, "E", 249.80, 250.80, None, {}),                   # "POGBA 6" – EURO 2020 screamer
    (41, 43, "E", 256.30, 257.30, None, {}),                   # France pile-on
    (43, 45, "P", 130.76, 131.25, None, {"interp": True}),     # Juve gesture, slow-mo
    # "DANSE" 5 – final pose, slow push-in, cut on the bar line (loops into the intro)
    (45, 49, "P", 156.00, 157.30, None, {"interp": True, "pushin": 0.10}),
]


def fidx(t):
    return int(round((t - T0) * FPS))


N_TOTAL = fidx(T_END)
DANSE = [B(k) for k in (13, 21, 29, 37, 45)]
CUTS = sorted({B(s[0]) for s in EDL} - set(DANSE) - {T0})
PULSE = [B(k) for k in range(30, 37) if B(k) not in CUTS]          # beat bounce during the dance block
FLASH = {B(13): 0.9, B(21): 0.6, B(29): 0.5, B(37): 0.45, B(45): 0.6}
SHAKE = {B(13): 26, B(21): 14, B(45): 10}


def shot_frames(seg):
    k0, k1, src, a, b, crop, ex = seg
    s0, s1 = B(k0), B(k1)
    n = fidx(s1) - fidx(s0)
    speed = (b - a) / (s1 - s0)
    x, y, w, h = crop or CROP[src]
    vf = [f"crop={w}:{h}:{x}:{y}", f"scale={W}:{H}:flags=lanczos",
          f"setpts=(PTS-STARTPTS)/{speed:.6f}"]
    if ex.get("interp") and speed < 0.95:
        vf.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    else:
        vf.append(f"fps={FPS}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{(b - a) + 0.6:.3f}",
           "-i", SRC[src], "-an", "-vf", ",".join(vf), "-frames:v", str(n),
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8)
    got = len(frames) // (W * H * 3)
    out = list(frames[: got * W * H * 3].reshape(got, H, W, 3))
    if not out:
        raise RuntimeError(f"no frames decoded for {seg}")
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


def loudnorm_filter(dur, target=-14.0, tp=-1.0):
    """Two-pass EBU R128: measure the song segment, then apply linear gain to hit TikTok's -14 LUFS."""
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{T0:.3f}", "-t", f"{dur:.3f}", "-i", SONG,
                            "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    return (f"loudnorm=I={target}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}")


def main():
    rng = np.random.default_rng(6)
    punch = [(fidx(t), 0.10) for t in DANSE] + [(fidx(t), 0.045) for t in CUTS] + \
            [(fidx(t), 0.03) for t in PULSE]
    flash_ev = [(fidx(t), a) for t, a in FLASH.items()]
    shake_ev = [(fidx(t), a) for t, a in SHAKE.items()]
    rgb_ev = [(fidx(t), 14) for t in DANSE] + [(fidx(t), 6) for t in CUTS]

    enc = None
    if not PREVIEW:
        os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
        dur = N_TOTAL / FPS
        enc = subprocess.Popen([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-ss", f"{T0:.3f}", "-t", f"{dur:.3f}", "-i", SONG,
            "-filter_complex",
            "[0:v]eq=contrast=1.08:saturation=1.18:gamma=0.98,unsharp=5:5:0.6:5:5:0.0,"
            "vignette=angle=PI/5.5,format=yuv420p[v];"
            f"[1:a]{loudnorm_filter(dur)},aresample=44100,"
            f"afade=t=in:st=0:d=0.01,afade=t=out:st={dur - 0.04:.3f}:d=0.04[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level", "4.2",
            "-g", "30", "-bf", "2", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "320k", "-ar", "44100",
            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    else:
        os.makedirs(f"{ROOT}/out", exist_ok=True)

    f_global = 0
    for i, seg in enumerate(EDL):
        frames, speed = shot_frames(seg)
        n = len(frames)
        print((i, seg[0], seg[1], round(B(seg[0]), 3), seg[2], seg[3], seg[4], round(speed, 3), n), flush=True)
        for k, fr in enumerate(frames):
            f = f_global + k
            z = 1.0 + env(f, punch, 3.0)
            if "pushin" in seg[6]:
                z *= 1.0 + seg[6]["pushin"] * (k / max(1, n - 1))
            sh = env(f, shake_ev, 4.0)
            dx = dy = 0.0
            if sh > 0.8:
                dx, dy = rng.uniform(-sh, sh), rng.uniform(-sh, sh)
                z += sh / 900.0
            img = zoom_shift(fr, z, dx, dy)
            c = env(f, rgb_ev, 2.5)
            if c > 0.8:
                s = int(round(c))
                b_, g_, r_ = cv2.split(img)
                img = cv2.merge([np.roll(b_, -s, axis=1), g_, np.roll(r_, s, axis=1)])
            fl = min(1.0, env(f, flash_ev, 2.4))
            if fl > 0.01:
                img = cv2.addWeighted(img, 1 - fl, np.full_like(img, 255), fl, 0)
            if PREVIEW:
                if k in (0, n // 2, n - 1):
                    cv2.imwrite(f"{ROOT}/out/prev_{i:02d}_{k:03d}.jpg", cv2.resize(img, (384, 216)))
            else:
                enc.stdin.write(img.tobytes())
        f_global += n
    if enc:
        enc.stdin.close()
        enc.wait()
    print("total frames", f_global, "expected", N_TOTAL, "duration", round(f_global / FPS, 3))


if __name__ == "__main__":
    main()
