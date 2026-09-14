#!/usr/bin/env python3
"""Render-Engine: EDL -> 9:16-Video auf schwarzem Grund.

Jeder Shot wird einzeln gerendert (eigener ffmpeg-Aufruf), danach concat.
Das haelt den Filtergraph klein, macht Fehler lokalisierbar und erlaubt
pro Shot eine eigene Effektkette.

Zeitraster: BEAT = 0.3715s (161.5 BPM). Schnittpunkte werden aus der
absoluten Zeit auf den naechsten Frame gerundet -- so bleibt der Fehler
unter einer halben Frame und summiert sich nicht auf.
"""
import json, os, subprocess, sys, math, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from looks import W, H, FPS, SUPER, BANDS, GRADES, band_rect, zoom_expr, pan_expr

BEAT = 0.3715
SRC_DIR = os.path.join(PROJ, "assets", "source")
OUT_DIR = os.path.join(PROJ, "build", "shots")

def src_path(key):
    p = os.path.join(SRC_DIR, key + ".mp4")
    if not os.path.exists(p):
        raise FileNotFoundError(f"Quelle fehlt: {p}")
    return p

def probe_dur(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",p],capture_output=True,text=True).stdout.strip())

# ------------------------------------------------------------ Effektkette ---
def post_fx(fx, dur):
    """Effekte NACH der Skalierung auf Bandgroesse."""
    f = []
    if "rgbhit" in fx:      # Chromatic Aberration als Schlag auf dem Schnitt
        f.append(f"rgbashift=rh=-9:bh=9:rv=3:bv=-3:enable='lt(t,0.075)'")
    if "rgbsplit" in fx:    # durchgehend, subtil
        f.append("rgbashift=rh=-3:bh=3")
    if "invert" in fx:
        f.append("negate=enable='lt(t,0.05)'")
    if "blurhit" in fx:
        f.append("gblur=sigma=14:enable='lt(t,0.07)'")
    if "grain" in fx:
        f.append("noise=alls=9:allf=t+u")
    if "grain_heavy" in fx:
        f.append("noise=alls=20:allf=t+u")
    if "vignette" in fx:
        f.append("vignette=angle=PI/5")
    if "flash" in fx:       # weisser Anschnitt
        f.append("eq=brightness='if(lt(t,0.05),0.9*(1-t/0.05),0)':eval=frame")
    if "dip" in fx:         # schwarzer Anschnitt
        f.append("eq=brightness='if(lt(t,0.06),-1.0*(1-t/0.06),0)':eval=frame")
    return f

def band_anim_overlay(fx, dur, bw, bh):
    """Animiertes Band: das Format selbst faehrt auf oder zu.

    drawbox scheidet aus -- es wertet w/h nur einmal beim Filter-Init aus.
    overlay wertet x/y dagegen pro Frame aus, also schieben wir zwei schwarze
    Balken ueber das Bild. Rueckgabe: (Anzahl Zusatzeingaenge, Graph-Bauer).
    """
    half = bh // 2
    ops = []
    if "open" in fx:
        p = "min(1,t/0.18)"
        ops.append((f"0-{half}*{p}", f"{half}+{half}*{p}"))
    if "close" in fx:
        st = max(0.01, dur - 0.20)
        p = f"min(1,max(0,(t-{st:.3f})/0.20))"
        ops.append((f"0-{half}*(1-{p})", f"{half}+{half}*(1-{p})"))
    return half, ops

def _mask_cond(mask, dur, bw, bh, sc):
    """Maskenbedingung fuer eine Ebene. sc=1 fuer Luma, 2 fuer Chroma (yuv420p
    hat halbe Chroma-Aufloesung, also muessen alle Koordinaten halbiert werden)."""
    cx, cy = (bw // 2) // sc, (bh // 2) // sc
    r = (int(math.hypot(bw, bh) / 2) + 8) // sc
    w, h = bw // sc, bh // sc
    if mask == "circle_in":
        return f"lt(hypot(X-{cx},Y-{cy}),{r}*min(1,T/0.22))"
    if mask == "circle_out":
        st = max(0.01, dur - 0.22)
        return f"lt(hypot(X-{cx},Y-{cy}),{r}*(1-min(1,max(0,(T-{st:.3f})/0.22))))"
    if mask == "wipe_r":  return f"lt(X,{w}*min(1,T/0.18))"
    if mask == "wipe_l":  return f"gt(X,{w}*(1-min(1,T/0.18)))"
    if mask == "wipe_d":  return f"lt(Y,{h}*min(1,T/0.18))"
    if mask == "diag":    return f"lt(X+Y,{w+h}*min(1,T/0.20))"
    if mask == "bars":    return f"lt(mod(X,{max(2,w//6)}),{max(2,w//6)}*min(1,T/0.22))"
    return None

def mask_filter(mask, dur, bw, bh):
    """Animierte Maske. Statt Alpha zu setzen (das spaeter von format=yuv420p
    verworfen wuerde) wird ausserhalb der Maske direkt Schwarz gemalt --
    der Hintergrund ist ohnehin schwarz."""
    if not mask: return []
    cl = _mask_cond(mask, dur, bw, bh, 1)
    cc = _mask_cond(mask, dur, bw, bh, 2)
    if not cl: return []
    return [f"geq=lum='if({cl},lum(X,Y),0)'"
            f":cb='if({cc},cb(X,Y),128)'"
            f":cr='if({cc},cr(X,Y),128)'"]

# ----------------------------------------------------------- Shot-Rendering --
def render_shot(shot, idx, nframes, dst):
    dur = nframes / FPS
    band = shot.get("band", "wide")
    bx, by, bw, bh = band_rect(band, shot.get("y"), shot.get("x"))
    fx    = shot.get("fx", [])
    grade = GRADES[shot.get("grade", "neutral")]
    speed = float(shot.get("speed", 1.0))
    mask  = shot.get("mask")

    # --- Platzhalter fuer noch fehlendes Material --------------------------
    if shot.get("src") == "SLOT":
        col = shot.get("slot_color", "0x121212")
        vf = (f"color=c={col}:s={bw}x{bh}:r={FPS}:d={dur:.4f},"
              f"drawbox=x=0:y=0:w={bw}:h={bh}:color=0x3A3A3A:t=3,"
              f"pad={W}:{H}:{bx}:{by}:black,setsar=1,format=yuv420p")
        cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y",
               "-f","lavfi","-i",f"nullsrc=s=16x16:r={FPS}:d={dur:.4f}",
               "-filter_complex",vf.replace(f"color=c={col}",f"color=c={col}",1),
               "-frames:v",str(nframes),"-c:v","libx264","-crf","14",
               "-pix_fmt","yuv420p","-r",str(FPS),dst]
        # einfacher: direkt lavfi color als Quelle
        cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y",
               "-f","lavfi","-i",f"color=c={col}:s={bw}x{bh}:r={FPS}",
               "-vf",f"drawbox=x=0:y=0:w={bw}:h={bh}:color=0x3A3A3A:t=3,"
                     f"pad={W}:{H}:{bx}:{by}:black,setsar=1,format=yuv420p",
               "-frames:v",str(nframes),"-c:v","libx264","-crf","14",
               "-preset","veryfast","-r",str(FPS),dst]
        subprocess.run(cmd,check=True,capture_output=True)
        return

    # --- echtes Quellmaterial ---------------------------------------------
    src = src_path(shot["src"])
    ss  = float(shot.get("src_in", 0.0))
    need = dur * speed + 0.30            # etwas Reserve fuer fps-Konvertierung
    sdur = probe_dur(src)
    if ss + need > sdur:
        ss = max(0.0, sdur - need)

    sw, sh = bw * SUPER, bh * SUPER
    chain = [f"fps={FPS}"]
    # Vorab-Beschnitt, z.B. um UI-Reste aus einem Bildschirmmitschnitt zu entfernen
    if shot.get("pre_crop"):
        chain.append(f"crop={shot['pre_crop']}")
    if speed != 1.0:
        chain.append(f"setpts=PTS/{speed}")
    chain.append(f"scale={sw}:{sh}:force_original_aspect_ratio=increase:flags=bicubic")
    chain.append(f"crop={sw}:{sh}")
    if grade: chain.append(grade)
    boost = float(shot.get("boost", 1.0))
    if boost != 1.0:
        chain.append(f"eq=gamma={boost:.3f}")

    z = zoom_expr(fx, dur)
    px, py = pan_expr(fx, dur, "x"), pan_expr(fx, dur, "y")
    chain.append(
        f"zoompan=z='{z}':d=1:s={bw}x{bh}:fps={FPS}"
        f":x='iw/2-(iw/zoom/2)+({px})*{SUPER}'"
        f":y='ih/2-(ih/zoom/2)+({py})*{SUPER}'")
    chain.append(f"setpts=N/{FPS}/TB")   # PTS nach zoompan neu aufbauen
    chain += post_fx(fx, dur)
    chain += mask_filter(mask, dur, bw, bh)

    half, band_ops = band_anim_overlay(fx, dur, bw, bh)
    extra_in, graph = [], ""
    if band_ops:
        graph += "[0:v]" + ",".join(chain) + "[v0];"
        extra_in = ["-f","lavfi","-i",f"color=black:s={bw}x{half}:r={FPS}"]
        cur = "v0"
        for j,(ytop,ybot) in enumerate(band_ops):
            graph += f"[1:v]split=2[bt{j}][bb{j}];"
            graph += f"[{cur}][bt{j}]overlay=x=0:y='{ytop}':shortest=1[o{j}a];"
            graph += f"[o{j}a][bb{j}]overlay=x=0:y='{ybot}':shortest=1[o{j}b];"
            cur = f"o{j}b"
        graph += f"[{cur}]pad={W}:{H}:{bx}:{by}:black,setsar=1,format=yuv420p[out]"
    else:
        graph = ("[0:v]" + ",".join(chain) +
                 f",pad={W}:{H}:{bx}:{by}:black,setsar=1,format=yuv420p[out]")

    cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y",
           "-ss",f"{ss:.4f}","-i",src] + extra_in + [
           "-filter_complex",graph,"-map","[out]",
           "-frames:v",str(nframes),
           "-an","-c:v","libx264","-crf","14","-preset","medium",
           "-pix_fmt","yuv420p","-r",str(FPS),dst]
    r = subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode != 0:
        print(f"  !! Shot {idx} ({shot.get('note','')}) FEHLER:\n{r.stderr[-1200:]}")
        raise SystemExit(1)

# ------------------------------------------------------------------ Main ----
def main(edl_path, out_name, audio=None, audio_offset=0.0):
    edl = json.load(open(edl_path))
    shots = edl["shots"]
    os.makedirs(OUT_DIR, exist_ok=True)

    # Frame-genaue Grenzen aus absoluter Zeit
    bounds = []
    for s in shots:
        bounds.append(round(s["beat_in"] * BEAT * FPS))
    end_beat = shots[-1]["beat_in"] + shots[-1]["beats"]
    bounds.append(round(end_beat * BEAT * FPS))

    print(f"{len(shots)} Shots, {bounds[-1]} Frames = {bounds[-1]/FPS:.3f}s @ {FPS}fps")
    files = []
    for i, s in enumerate(shots):
        n = bounds[i+1] - bounds[i]
        dst = os.path.join(OUT_DIR, f"{out_name}_{i:03d}.mp4")
        print(f"  [{i:02d}] b{s['beat_in']:>5.1f}+{s['beats']:<4.1f} {n:>4}f "
              f"{s.get('band','wide'):9s} {str(s.get('src'))[:16]:16s} {s.get('note','')[:40]}")
        render_shot(s, i, n, dst)
        files.append(dst)

    lst = os.path.join(OUT_DIR, f"{out_name}_concat.txt")
    with open(lst,"w") as f:
        for p in files: f.write(f"file '{p}'\n")
    silent = os.path.join(PROJ,"build",f"{out_name}_silent.mp4")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","concat","-safe","0","-i",lst,"-c","copy",silent],check=True)
    print(f"-> {silent}")
    return silent, bounds[-1]/FPS

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
