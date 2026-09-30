"""Render a beat-synced edit (9:16 or 16:9) from an EDL, clips in parallel.

EDL (edl.json):
{
  "bpm": 120, "grid0": 0.2555,           # first downbeat in edit time
  "clips": [
    {"src": "src/x.mp4", "in": 12.3, "beats": 4, "speed": 1.0,
     "cx": 0.5 | [[t_rel, x], ...],       # subject centre x (0..1 of source width), keyframed in clip seconds
     "cy": 0.5, "h": 1.0,                  # subject centre y, extra zoom (crop height as fraction of the usable band)
     "xlim": [0, 1], "ylim": [0, 1],       # overlay-free rectangle of the source (burnt-in subs, logos, scoreboards)
     "delogo": [[x, y, w, h], ...],        # small watermarks to paint out (ffmpeg delogo), normalised
     "clone": [[x, y, w, h, dx, dy], ...], # clone-stamp a watermark with the patch offset by (dx, dy), feathered
     "fit": false,                         # show the whole source on a blurred fill (e.g. square source in 16:9)
     "track": [x, y, w, h],                # optional: bbox of the subject in the first frame -> CSRT tracking for cx
     "fx": ["punch", "flash", "shake", "bw", "fadein", "fadeout", "zoomin", "zoomout"],
     "title": {...},                       # optional title card (see title_layer)
     "interp": true                        # motion-interpolated slow motion (default when speed < 1)
    }, ...]
}
The crop is the largest W:H window inside xlim x ylim (divided by h and any zoom effect), centred as close to
(cx, cy) as the rectangle allows. Clip i starts where clip i-1 ended; boundaries snap to the beat grid in frames.

usage: render.py edl.json out.mp4 [--size 1080x1920] [--override overrides.json] [--jobs 4] [--segdir segs]
overrides.json maps clip index -> dict merged over that clip (used for the 16:9 safe rectangles).
"""
import json, subprocess, sys, os, hashlib, argparse
from multiprocessing import Pool
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


def decode(path, t0, dur, rate, interp, crop=None, delogo=()):
    """BGR frames sampled at `rate` fps from source time t0 for `dur` seconds (optionally pre-cropped to x,y,w,h)."""
    sw, sh, sfps = probe(path)
    vf = []
    for (lx, ly, lw, lh) in delogo:
        x = max(2, int(lx * sw)); y = max(2, int(ly * sh))
        w = min(sw - x - 2, int(lw * sw)); h = min(sh - y - 2, int(lh * sh))
        vf.append(f"delogo=x={x}:y={y}:w={w}:h={h}")
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


def clone_patches(frames, rects, SW, SH, ox, oy):
    """Cover watermarks with a feathered copy of nearby background (same frame), in source-normalised coords."""
    if not rects:
        return frames
    fh, fw = frames[0].shape[:2]
    ops = []
    for (x, y, w, h, dx, dy) in rects:
        x0 = int(x * SW) - ox; y0 = int(y * SH) - oy; x1 = x0 + int(w * SW); y1 = y0 + int(h * SH)
        sx, sy = int(dx * SW), int(dy * SH)
        x0, y0 = max(x0, 0, -sx), max(y0, 0, -sy)
        x1, y1 = min(x1, fw, fw - sx), min(y1, fh, fh - sy)
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        m = np.zeros((y1 - y0, x1 - x0), np.float32)
        e = max(3, int(0.12 * min(x1 - x0, y1 - y0)))
        m[e:-e, e:-e] = 1
        m = cv2.GaussianBlur(m, (0, 0), e / 2)[..., None]
        m = np.clip(m * 1.6, 0, 1)
        ops.append((x0, y0, x1, y1, sx, sy, m))
    out = []
    for f in frames:
        f = f.copy()
        for (x0, y0, x1, y1, sx, sy, m) in ops:
            d = f[y0:y1, x0:x1].astype(np.float32)
            p = f[y0 + sy:y1 + sy, x0 + sx:x1 + sx].astype(np.float32)
            f[y0:y1, x0:x1] = (d * (1 - m) + p * m).astype(np.uint8)
        out.append(f)
    return out


def ease_out(a):
    return 1 - (1 - a) ** 3


def fit_frame(f):
    """Whole source frame centred on a blurred, darkened fill of the output size."""
    sh, sw = f.shape[:2]
    s = max(W / sw, H / sh)
    bg = cv2.resize(f, (int(sw * s / 8) + 1, int(sh * s / 8) + 1), interpolation=cv2.INTER_AREA)
    bg = cv2.GaussianBlur(bg, (0, 0), 6)
    bg = cv2.resize(bg, (int(sw * s) + 1, int(sh * s) + 1), interpolation=cv2.INTER_LINEAR)
    y0 = (bg.shape[0] - H) // 2; x0 = (bg.shape[1] - W) // 2
    bg = (bg[y0:y0 + H, x0:x0 + W].astype(np.float32) * 0.45).astype(np.uint8)
    s2 = min(W / sw, H / sh)
    fw, fh = int(round(sw * s2)), int(round(sh * s2))
    fg = cv2.resize(f, (fw, fh), interpolation=cv2.INTER_CUBIC)
    xo = (W - fw) // 2; yo = (H - fh) // 2
    bg[yo:yo + fh, xo:xo + fw] = fg
    return bg


def render_clip(c, dur, write, rng):
    speed = c.get("speed", 1.0)
    rate = FPS / speed
    n_out = int(round(dur * FPS))
    SW, SH, sfps = probe(c["src"])
    interp = c.get("interp", speed < 0.99)
    fit = c.get("fit", False)
    xlo, xhi = c.get("xlim", [0, 1]); ylo, yhi = c.get("ylim", [0, 1])
    band_w = (xhi - xlo) * SW; band_h = (yhi - ylo) * SH
    ch_base = min(band_h, band_w * H / W) * c.get("h", 1.0)
    crop = None
    if interp and rate > sfps * 1.05 and "track" not in c and not fit:
        kf = c.get("cx", 0.5)
        xs = [v for _, v in kf] if isinstance(kf, list) else [kf]
        cw_max = ch_base * W / H
        xa = max(int(xlo * SW), int(min(xs) * SW - cw_max / 2 - 40)) // 2 * 2
        xb = min(int(xhi * SW), int(max(xs) * SW + cw_max / 2 + 40))
        if xb - xa < cw_max + 4:
            xa = max(0, int(xlo * SW)) // 2 * 2; xb = int(xhi * SW)
        ya = int(ylo * SH) // 2 * 2; yb = int(yhi * SH)
        crop = (xa, ya, (xb - xa) // 2 * 2, (yb - ya) // 2 * 2)
    frames, sw, sh = decode(c["src"], c["in"], dur * speed, rate, interp, crop, c.get("delogo", ()))
    if not frames:
        raise RuntimeError(f"no frames from {c['src']} @ {c['in']}")
    while len(frames) < n_out:
        frames.append(frames[-1])
    frames = frames[:n_out]
    frames = clone_patches(frames, c.get("clone", []), SW, SH, *((crop[0], crop[1]) if crop else (0, 0)))
    if fit:
        frames = [fit_frame(f) for f in frames]
        SW, SH, sw, sh = W, H, W, H
        xlo, xhi, ylo, yhi = 0, 1, 0, 1
        ch_base = H * c.get("h", 1.0)
    ox, oy = (crop[0], crop[1]) if crop else (0, 0)
    # allowed window in source pixels: overlay-free rectangle intersected with the decoded area
    bx0 = max(xlo * SW, ox); bx1 = min(xhi * SW, ox + sw)
    by0 = max(ylo * SH, oy); by1 = min(yhi * SH, oy + sh)
    tx = ty = None
    if "track" in c:
        tx, ty = track_path(frames, c["track"], SW, SH)
    fx = set(c.get("fx", []))
    shake = np.zeros((n_out, 2))
    if "shake" in fx:
        for i in range(min(n_out, 10)):
            amp = 18 * (1 - i / 10)
            shake[i] = rng.uniform(-amp, amp, 2)
    t_rgb = t_a = None
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
        cx = (tx[i] + c.get("dx", 0)) if tx is not None and not fit else (0.5 if fit else interp_kf(c.get("cx", 0.5), t))
        cy = interp_kf(c.get("cy", (ylo + yhi) / 2), t) if ty is None or "cy" in c or fit else ty[i]
        if fit:
            cy = 0.5
        px = cx * SW + shake[i][0] * SW / 1920
        py = cy * SH + shake[i][1] * SH / 1080
        x0 = min(max(px - cw / 2, bx0), bx1 - cw) - ox
        y0 = min(max(py - ch / 2, by0), by1 - ch) - oy
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
            if t_rgb is None:
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
        write(out)
    return n_out


def _segment(job):
    idx, c, dur, path = job
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "10",
                            "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n = render_clip(c, dur, lambda fr: enc.stdin.write(fr.tobytes()), np.random.default_rng(7 + idx))
    enc.stdin.close(); enc.wait()
    return idx, n


def main():
    global W, H
    ap = argparse.ArgumentParser()
    ap.add_argument("edl"); ap.add_argument("out")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--override")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--segdir", default="segs")
    a = ap.parse_args()
    W, H = (int(v) for v in a.size.split("x"))
    edl = json.load(open(a.edl))
    ovr = json.load(open(a.override)) if a.override else {}
    beat = 60.0 / edl["bpm"]
    os.makedirs(a.segdir, exist_ok=True)
    jobs, segs = [], []
    t = 0.0; edge = edl["grid0"]
    for idx, c in enumerate(edl["clips"]):
        c = dict(c, **ovr.get(str(idx), {}))
        end = edge + c["beats"] * beat
        dur = (int(round(end * FPS)) - int(round(t * FPS))) / FPS
        key = hashlib.sha1(json.dumps([c, dur, W, H], sort_keys=True).encode()).hexdigest()[:16]
        path = os.path.join(a.segdir, f"seg{idx:02d}_{key}.mp4")
        segs.append(path)
        if not os.path.exists(path):
            jobs.append((idx, c, dur, path))
        t = end; edge = end
    # longest (slow-motion) clips first so the pool stays busy
    jobs.sort(key=lambda j: -(j[1].get("speed", 1) < 0.99) * j[2])
    with Pool(a.jobs) as pool:
        for idx, n in pool.imap_unordered(_segment, jobs):
            print(f"clip {idx:2d} done ({n} frames)", flush=True)
    lst = os.path.join(a.segdir, "list.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{os.path.abspath(p)}'\n" for p in segs)
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf", GRADE,
                           "-c:v", "libx264", "-preset", os.environ.get("PRESET", "medium"),
                           "-crf", os.environ.get("CRF", "14"), "-pix_fmt", "yuv420p", a.out])
    print("wrote", a.out)


if __name__ == "__main__":
    main()
