"""Render a beat-synced 9:16 edit from an EDL.

EDL (edl.json):
{
  "bpm": 120, "grid0": 0.2555,          # first downbeat in edit time
  "clips": [
    {"src": "src/x.mp4", "in": 12.3, "beats": 4, "speed": 1.0,
     "cx": 0.5 | [[t_rel, x], ...],      # crop centre x (0..1 of source width), t_rel in edit seconds from clip start
     "cy": 0.5, "h": 1.0,                  # crop centre y, crop height as fraction of usable height
     "ylim": [0, 1],                       # usable vertical band of the source (to cut burnt-in subs / letterbox)
     "track": [x, y, w, h],                # optional: normalised bbox of Pogba in first frame -> CSRT tracking for cx
     "fx": ["punch", "flash", "shake", "bw", "fadein", "fadeout", "zoomin"],
     "interp": true                        # motion-interpolate for slow motion
    }, ...]
}
Clip i starts where clip i-1 ended; the first clip starts at edit t=0 and may carry "beats" plus "pre" (seconds before grid0).
"""
import json, subprocess, sys, math, os
import numpy as np, cv2

W, H, FPS = 1080, 1920, 30
# global look: a touch more contrast/saturation, light sharpening, soft vignette
GRADE = "eq=contrast=1.06:saturation=1.12:gamma=0.98,unsharp=5:5:0.55:5:5:0,vignette=angle=PI/5"


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate", "-of", "json", path])
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(n) / float(d)


def decode(path, t0, dur, rate, interp, crop=None):
    """BGR frames sampled at `rate` fps from source time t0 for `dur` seconds (optionally pre-cropped to x,y,w,h)."""
    sw, sh, sfps = probe(path)
    vf = []
    if crop:
        vf.append("crop=%d:%d:%d:%d" % (crop[2], crop[3], crop[0], crop[1]))
        sw, sh = crop[2], crop[3]
    if interp and rate > sfps * 1.05:
        vf.append(f"minterpolate=fps={rate:.4f}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    vf.append(f"fps={rate:.4f}")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0, t0):.3f}", "-i", path, "-t", f"{dur + 0.2:.3f}",
           "-vf", ",".join(vf), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fs = sw * sh * 3
    frames = []
    while True:
        b = p.stdout.read(fs)
        if len(b) < fs:
            break
        frames.append(np.frombuffer(b, np.uint8).reshape(sh, sw, 3))
    p.wait()
    return frames, sw, sh


def interp_kf(kf, t):
    if not isinstance(kf, list):
        return kf
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            a = (t - t0) / max(1e-6, t1 - t0)
            a = a * a * (3 - 2 * a)  # smoothstep between keyframes
            return v0 + (v1 - v0) * a
    return kf[-1][1]


def track_path(frames, box, sw, sh):
    x, y, w, h = box
    bb = (int(x * sw), int(y * sh), int(w * sw), int(h * sh))
    tr = cv2.TrackerCSRT_create()
    scale = 0.5
    sm = lambda f: cv2.resize(f, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    tr.init(sm(frames[0]), tuple(int(v * scale) for v in bb))
    xs = [(bb[0] + bb[2] / 2) / sw]
    ys = [(bb[1] + bb[3] / 2) / sh]
    for f in frames[1:]:
        ok, r = tr.update(sm(f))
        if ok:
            xs.append((r[0] + r[2] / 2) / scale / sw); ys.append((r[1] + r[3] / 2) / scale / sh)
        else:
            xs.append(xs[-1]); ys.append(ys[-1])
    # heavy smoothing so the virtual camera glides
    def smooth(a, k=9):
        a = np.array(a); pad = np.pad(a, (k, k), mode="edge")
        ker = np.ones(2 * k + 1) / (2 * k + 1)
        return np.convolve(pad, ker, mode="valid")
    return smooth(xs), smooth(ys)


def title_layer(spec):
    """Pre-render a centred title (RGBA float arrays) for alpha blending onto frames."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    font = ImageFont.truetype(spec.get("font", "fonts/BebasNeue-Regular.ttf"), spec.get("size", 150))
    sub_font = ImageFont.truetype(spec.get("font", "fonts/BebasNeue-Regular.ttf"), spec.get("sub_size", 54))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def spaced(text, f, y, track):
        widths = [d.textlength(ch, font=f) for ch in text]
        total = sum(widths) + track * (len(text) - 1)
        x = (W - total) / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=f, fill=(255, 255, 255, 255))
            x += w + track
    y = int(spec.get("y", 0.72) * H)
    spaced(spec["text"], font, y, spec.get("track", 14))
    if spec.get("sub"):
        spaced(spec["sub"], sub_font, y + spec.get("size", 150) + 10, 10)
    glow = img.filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); shadow.paste((0, 0, 0, 200), mask=glow.split()[3])
    comp = Image.alpha_composite(shadow, img)
    a = np.asarray(comp).astype(np.float32) / 255.0
    rgb = a[..., :3][..., ::-1] * 255.0  # to BGR
    return rgb, a[..., 3:4]


def ease_out(a):
    return 1 - (1 - a) ** 3


def render_clip(c, t_edit0, dur, enc, rng):
    speed = c.get("speed", 1.0)
    rate = FPS / speed
    n_out = int(round(dur * FPS))
    SW, SH, sfps = probe(c["src"])
    interp = c.get("interp", speed < 0.99)
    ylo, yhi = c.get("ylim", [0, 1])
    crop = None
    if interp and rate > sfps * 1.05 and "track" not in c:
        kf = c.get("cx", 0.5)
        xs = [v for _, v in kf] if isinstance(kf, list) else [kf]
        cw_max = (yhi - ylo) * SH * c.get("h", 1.0) * W / H
        xa = max(0, int(min(xs) * SW - cw_max / 2 - 40)) // 2 * 2
        xb = min(SW, int(max(xs) * SW + cw_max / 2 + 40))
        ya = int(ylo * SH) // 2 * 2
        yb = int(yhi * SH)
        crop = (xa, ya, (xb - xa) // 2 * 2, (yb - ya) // 2 * 2)
    frames, sw, sh = decode(c["src"], c["in"], dur * speed, rate, interp, crop)
    ox, oy = (crop[0], crop[1]) if crop else (0, 0)
    if not frames:
        raise RuntimeError(f"no frames from {c['src']} @ {c['in']}")
    while len(frames) < n_out:
        frames.append(frames[-1])
    frames = frames[:n_out]
    band = (yhi - ylo) * SH
    ch_base = band * c.get("h", 1.0)
    tx = ty = None
    if "track" in c:
        tx, ty = track_path(frames, c["track"], SW, SH)
    fx = set(c.get("fx", []))
    shake = np.zeros((n_out, 2))
    if "shake" in fx:
        for i in range(min(n_out, 10)):
            amp = 18 * (1 - i / 10)
            shake[i] = rng.uniform(-amp, amp, 2)
    for i, f in enumerate(frames):
        t = i / FPS
        z = 1.0
        if "punch" in fx:
            a = min(1, t / 0.35)
            z *= 1.14 - 0.14 * ease_out(a)
        if "zoomin" in fx:
            z *= 1.0 + 0.10 * (t / max(dur, 1e-3))
        if "zoomout" in fx:
            z *= 1.10 - 0.10 * (t / max(dur, 1e-3))
        ch = ch_base / z
        cw = ch * W / H
        if cw > SW:  # source narrower than 9:16 crop
            cw = SW; ch = cw * H / W
        cx = (tx[i] + c.get("dx", 0)) if tx is not None else interp_kf(c.get("cx", 0.5), t)
        cy = interp_kf(c.get("cy", (ylo + yhi) / 2), t) if ty is None or "cy" in c else ty[i]
        px = cx * SW - ox + shake[i][0] * SW / 1920
        py = cy * SH - oy + shake[i][1] * SH / 1080
        x0 = min(max(px - cw / 2, 0), sw - cw)
        y0 = min(max(py - ch / 2, ylo * SH - oy), yhi * SH - oy - ch)
        # sub-pixel accurate crop+scale via affine warp
        sx = W / cw; sy = H / ch
        M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
        out = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        if "bw" in fx:
            g = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
            out = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        k = 1.0
        if "fadein" in fx:
            k *= min(1, t / c.get("fadein_s", 0.6))
        if "fadeout" in fx:
            k *= min(1, (dur - t) / c.get("fadeout_s", 1.5))
        if k < 1:
            out = (out.astype(np.float32) * max(0, k)).astype(np.uint8)
        if "title" in c:
            if i == 0:
                t_rgb, t_a = title_layer(c["title"])
            ts = c["title"].get("start", 0.0)
            ta = min(1.0, max(0.0, (t - ts) / c["title"].get("fade", 0.8)))
            if "fade_out" in c["title"]:
                ta *= min(1.0, max(0.0, (dur - t) / c["title"]["fade_out"]))
            if ta > 0:
                A = t_a * ta
                out = (out.astype(np.float32) * (1 - A) + t_rgb * A).astype(np.uint8)
        if "flash" in fx and t < 0.2:
            a = 0.85 * (1 - t / 0.2)
            out = cv2.addWeighted(out, 1 - a, np.full_like(out, 255), a, 0)
        enc.stdin.write(out.tobytes())
    return n_out


def main(edl_path, out_path, only=None):
    edl = json.load(open(edl_path))
    beat = 60.0 / edl["bpm"]
    grid0 = edl["grid0"]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-vf", GRADE, "-c:v", "libx264", "-preset", os.environ.get("PRESET", "medium"),
                            "-crf", os.environ.get("CRF", "14"),
                            "-pix_fmt", "yuv420p", out_path], stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    # clip boundaries snap to the beat grid in frames
    t = 0.0
    edge = grid0
    total = 0
    for idx, c in enumerate(edl["clips"]):
        end = edge + c["beats"] * beat
        f0 = int(round(t * FPS)); f1 = int(round(end * FPS))
        dur = (f1 - f0) / FPS
        if only is None or idx in only:
            n = render_clip(c, t, dur, enc, rng)
            total += n
            print(f"clip {idx:2d} {t:6.2f}-{end:6.2f} {os.path.basename(c['src'])} in={c['in']}", flush=True)
        t = end; edge = end
    enc.stdin.close(); enc.wait()
    print("frames", total, "dur", total / FPS)


if __name__ == "__main__":
    only = set(int(x) for x in sys.argv[3].split(",")) if len(sys.argv) > 3 else None
    main(sys.argv[1], sys.argv[2], only)
