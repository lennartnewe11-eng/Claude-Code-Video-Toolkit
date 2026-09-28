#!/usr/bin/env python3
"""Chunks + Musik -> Master und Lieferfassung, danach Prüfung am fertigen File.

    python3 deliver.py [--mb 48]

- Master: CRF 17 (Qualität konstant, Größe egal).
- Lieferfassung: Zielgröße trifft man nicht mit CRF, also zwei Durchgänge auf Bitrate.
- Prüfung am Ergebnis, nicht an der Arbeitskopie: Framezahl, Dauer, und Bild/Ton-Sync
  am Refrain-Einsatz (Weißblitz im Bild vs. Stadion-Jubel im Ton müssen auf
  demselben Frame liegen). Schreibt build/deliver.json.
"""
import argparse
import hashlib
import json
import os
import subprocess

import numpy as np

import audio
import render
import timeline as tl

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')


def concat_list():
    shots = render.resolve()
    assert render.check(shots)
    lst = os.path.join(render.CHUNKS, 'list.txt')
    with open(lst, 'w') as fh:
        for s in shots:
            fh.write(f"file 'shot_{s['i']:03d}.mp4'\n")
    return lst


def encode_master(lst, music, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', music,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out], check=True)


def encode_delivery(lst, music, out, mb):
    a_kbps = 192
    v_kbps = int(mb * 8 * 1000 * 0.97 / tl.TOTAL - a_kbps)
    common = ['-f', 'concat', '-safe', '0', '-i', lst, '-map', '0:v', '-c:v', 'libx264', '-preset', 'slow',
              '-tune', 'grain', '-b:v', f'{v_kbps}k', '-maxrate', f'{int(v_kbps * 1.8)}k',
              '-bufsize', f'{v_kbps * 3}k', '-pix_fmt', 'yuv420p', '-profile:v', 'high']
    log = os.path.join(BUILD, 'x264pass')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + common + ['-pass', '1', '-passlogfile', log, '-an',
                                                              '-f', 'null', '-'], check=True, cwd=BUILD)
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + common[:6] + ['-i', music] + common[6:] +
                   ['-map', '1:a', '-c:a', 'aac', '-b:a', f'{a_kbps}k', '-pass', '2', '-passlogfile', log,
                    '-movflags', '+faststart', out], check=True, cwd=BUILD)
    return v_kbps


def verify(path):
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                                            'stream=codec_type,nb_read_frames,duration', '-of', 'json', path]))
    v = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    a = [s for s in j['streams'] if s['codec_type'] == 'audio'][0]
    frames = int(v['nb_read_frames'])
    # Bild: Helligkeitssprung um den Refrain-Einsatz
    t_hit = tl.kt(audio.CHORUS_K)
    t0 = t_hit - 0.5
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-ss', f'{t0:.3f}', '-i', path, '-t', '1.0', '-vf',
                          'scale=96:54,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    lum = np.frombuffer(raw, np.uint8).reshape(-1, 54 * 96).mean(1)
    f_vid = int(np.argmax(np.diff(lum))) + 1
    t_vid = t0 + f_vid / tl.FPS
    # Ton: Hüllkurvensprung des Jubels
    pcm = subprocess.run(['ffmpeg', '-v', 'quiet', '-ss', f'{t0:.3f}', '-i', path, '-t', '1.0', '-vn', '-ac', '1',
                          '-ar', '8000', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.abs(np.frombuffer(pcm, np.float32))
    env = np.convolve(x, np.ones(80) / 80, 'same')
    t_aud = t0 + int(np.argmax(np.diff(env[::40]))) * 40 / 8000
    return dict(frames=frames, frames_expected=tl.NFRAMES, v_dur=float(v['duration']), a_dur=float(a['duration']),
                chorus_t=round(t_hit, 3), flash_t=round(t_vid, 3), roar_t=round(t_aud, 3),
                av_offset_ms=round((t_vid - t_aud) * 1000, 1))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mb', type=float, default=48)
    ap.add_argument('--no-master', action='store_true')
    a = ap.parse_args()
    lst = concat_list()
    music = os.path.join(BUILD, 'music.wav')
    master = os.path.join(BUILD, 'messi_edit_master.mp4')
    out = os.path.join(BUILD, 'messi_edit_1080p.mp4')
    if not a.no_master:
        encode_master(lst, music, master)
    vk = encode_delivery(lst, music, out, a.mb)
    idx = {}
    for p in ([master] if not a.no_master else []) + [out]:
        info = verify(p)
        info.update(size_mb=round(os.path.getsize(p) / 1e6, 2), sha256=sha(p))
        idx[os.path.basename(p)] = info
        print(os.path.basename(p), json.dumps(info))
    idx['delivery_video_kbps'] = vk
    json.dump(idx, open(os.path.join(BUILD, 'deliver.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
