"""AI upscaling for the low-resolution sources (576p / 720p broadcasts).

Real-ESRGAN "realesr-general-x4v3" (SRVGGNetCompact, BSD-3, xinntao/Real-ESRGAN),
run on CPU. Only the source frames the edit actually uses are upscaled; the
output is a drop-in replacement clip <key>_ai.mp4 with the same frame rate and
timeline, already cropped (broadcast graphics) and at 1920x1080, so the
renderer reads it like any other source.

    python3 build/upscale.py r_arsfk [r_arscounter ...]
    python3 build/upscale.py --test r_arsfk 47.0     # one frame, before/after
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

import edl
import render

MODEL = render.MEDIA / "models" / "realesr-general-x4v3.pth"
W, H = 1920, 1080
torch.set_num_threads(4)


class SRVGGNetCompact(nn.Module):
    """Same layer layout as Real-ESRGAN's SRVGGNetCompact, so its weights load."""

    def __init__(self, num_feat=64, num_conv=32, upscale=4):
        super().__init__()
        self.upscale = upscale
        body = [nn.Conv2d(3, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)]
        for _ in range(num_conv):
            body += [nn.Conv2d(num_feat, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)]
        body.append(nn.Conv2d(num_feat, 3 * upscale * upscale, 3, 1, 1))
        self.body = nn.ModuleList(body)
        self.upsampler = nn.PixelShuffle(upscale)

    def forward(self, x):
        out = x
        for layer in self.body:
            out = layer(out)
        return self.upsampler(out) + F.interpolate(x, scale_factor=self.upscale, mode="nearest")


_net = None


def net():
    global _net
    if _net is None:
        _net = SRVGGNetCompact()
        sd = torch.load(MODEL, map_location="cpu", weights_only=True)
        _net.load_state_dict(sd.get("params_ema", sd.get("params", sd)))
        _net.eval()
    return _net


@torch.inference_mode()
def sr(rgb):
    """uint8 RGB HxWx3 -> 4x upscaled uint8 RGB."""
    x = torch.from_numpy(rgb).permute(2, 0, 1).float().unsqueeze(0) / 255.0
    y = net()(x).clamp(0, 1)
    return (y[0].permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)


def to_out(rgb, crop):
    """Crop the broadcast graphics away, AI-upscale, area-downscale to 1920x1080."""
    h, w = rgb.shape[:2]
    if crop:
        x0, y0, x1, y1 = crop
        rgb = rgb[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    big = sr(np.ascontiguousarray(rgb))
    # cover-fit 16:9 then area resample (keeps the detail, kills the 4x ringing)
    bh, bw = big.shape[:2]
    s = max(W / bw, H / bh)
    big = cv2.resize(big, (round(bw * s), round(bh * s)), interpolation=cv2.INTER_AREA)
    oy, ox = (big.shape[0] - H) // 2, (big.shape[1] - W) // 2
    return big[oy:oy + H, ox:ox + W]


def used_windows(key):
    """Source time windows (s) that the edit reads from this clip."""
    win = []
    for s in edl.shots():
        for p in (s.get("panels") or ([s] if s.get("src") else [])):
            if p["src"] == key:
                ts = render.source_times(p, s["b0"], s["b1"])
                win.append((float(ts.min()) - 0.15, float(ts.max()) + 0.15))
    win.sort()
    merged = []
    for a, b in win:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def frames(path, w, h):
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        buf = proc.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)


def upscale_clip(key):
    p = render.probe(key, ai=False)
    crop = edl.CROP.get(key)
    wins = used_windows(key)
    dst = p["path"].with_name(f"{key}_ai.mp4")
    tmp = dst.with_name(f"{key}_ai.part.mp4")  # renamed when complete, so render.py never reads half a file
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=r_frame_rate", "-of", "csv=p=0", str(p["path"])],
                          capture_output=True, text=True).stdout.strip()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", rate, "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "12",
                            "-g", "12", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    n_ai = n = 0
    t0 = time.time()
    for i, f in enumerate(frames(p["path"], p["w"], p["h"])):
        t = i / p["fps"]
        if any(a <= t <= b for a, b in wins):
            out = to_out(f, crop)
            n_ai += 1
        else:  # outside the edit: plain lanczos, nobody sees it
            g = f
            if crop:
                h, w = f.shape[:2]
                x0, y0, x1, y1 = crop
                g = f[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
            out = cv2.resize(g, (W, H), interpolation=cv2.INTER_LANCZOS4)
        enc.stdin.write(np.ascontiguousarray(out).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    tmp.replace(dst)
    print(f"{key}: {n} frames, {n_ai} AI-upscaled in {time.time() - t0:.0f}s -> {dst.name}  windows {wins}")


def test(key, t):
    p = render.probe(key, ai=False)
    r = render.Reader(key, t, t + 0.2, p["w"], p["h"])
    f = r.get(t).copy()
    r.close()
    crop = edl.CROP.get(key)
    t1 = time.time()
    a = to_out(f, crop)
    dt = time.time() - t1
    h, w = f.shape[:2]
    x0, y0, x1, y1 = crop or (0, 0, 1, 1)
    b = cv2.resize(f[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)], (W, H), interpolation=cv2.INTER_LANCZOS4)
    # same 640x360 detail crop from both, side by side
    cy, cx = H // 2 - 180, W // 2 - 320
    side = np.concatenate([b[cy:cy + 360, cx:cx + 640], a[cy:cy + 360, cx:cx + 640]], axis=1)
    out = render.OUT / "sheets" / f"upscale_{key}.png"
    cv2.imwrite(str(out), cv2.cvtColor(side, cv2.COLOR_RGB2BGR))
    print(f"{key} @ {t}s: {w}x{h} -> AI {dt:.1f}s/frame; left lanczos, right AI -> {out}")


if __name__ == "__main__":
    if sys.argv[1] == "--test":
        test(sys.argv[2], float(sys.argv[3]))
    else:
        for k in sys.argv[1:]:
            upscale_clip(k)
