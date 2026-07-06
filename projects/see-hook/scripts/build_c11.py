#!/usr/bin/env python3
"""Main part - Chunk 11 (VO 214.24 -> ~228.4s): the long, narrow Rinnenseen of
Schleswig-Holstein, carved by meltwater under the glacier.
  beat A  static Swiss-poster of the SH relief (yellow, big Helvetica typo),
          the long narrow Rinnenseen pulsing red-orange  (no camera move)
  beat B  the aesthetic GIF filler inside a 35mm film-camera frame
Captions run over the film beat; the poster carries editorial typography.
"""
import json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
C11=MA/"c11"; FF="ffmpeg"; SCAN=str(BUILD/"scanlines.png")
MAPF=BUILD/"c11_map_f"

VO_START=214.24
SONG_OFFSET=291.14                      # continues the looped song from chunk 10
D_MAP, D_FILM, D_WASH, D_RINNEN = 5.5, 3.5, 3.3, 2.3
TOTAL=D_MAP+D_FILM+D_WASH+D_RINNEN      # 14.6
T_FILM0=D_MAP;              T_FILM1=D_MAP+D_FILM
T_RIN0 =D_MAP+D_FILM+D_WASH; T_RIN1 =TOTAL

GRADE = ("colortemperature=temperature=5200:mix=0.6:pl=1,"
         "eq=contrast=1.04:saturation=1.08:gamma=0.99,"
         "curves=r='0/0 0.5/0.53 1/1':b='0/0 0.5/0.47 1/0.98',rgbashift=rh=2:bh=-2")
CRT_TAIL = ("[pre][sc]blend=all_mode=multiply:all_opacity=0.34:shortest=1[m];"
            "[m]vignette=PI/6,noise=alls=4:allf=t,format=yuv420p[cg]")
# yellow poster: keep the yellow true, a whisper of vignette + grain
MAP_GRADE=("eq=contrast=1.04:saturation=1.06,vignette=PI/16,"
           "noise=alls=3:allf=t,format=yuv420p")

def run(cmd,label=""):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode!=0:
        sys.stderr.write(f"\n### FAIL {label}\n"+p.stderr[-3500:]); raise SystemExit(1)
    return p
def at(t):
    m=int(t//60); t-=m*60; s=int(t); c=int(round((t-s)*100))
    if c==100: s+=1; c=0
    return f"0:{m:02d}:{s:02d}.{c:02d}"
def ass_header(styles):
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"+"\n".join(styles)+"\n\n")

# ---- beat A: SH Swiss-poster + editorial Helvetica typography ----------------
def _poster_ass(a):
    BK="&H00181410"; GY="&H00403830"
    styles=[
      f"Style: Big,Liberation Sans,78,{BK},{BK},&H00FFFFFF,&H90101010,-1,0,0,0,100,100,0,0,1,0.6,0,7,0,0,0,1",
      f"Style: Sub,Liberation Sans,30,{GY},{GY},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
      f"Style: Meta,Liberation Sans,25,{BK},{BK},&H00FFFFFF,&H90101010,-1,0,0,0,100,100,3,0,1,0,0,9,0,0,0,1",
      f"Style: MetaS,Liberation Sans,25,{GY},{GY},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1",
      f"Style: State,Liberation Sans,56,{BK},{BK},&H00FFFFFF,&H90101010,-1,0,0,0,100,100,0,0,1,0,0,1,0,0,0,1",
      f"Style: Fact,Liberation Sans,26,{BK},{BK},&H00FFFFFF,&H90101010,-1,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1",
      f"Style: FactS,Liberation Sans,22,{GY},{GY},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1"]
    E=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    def d(st,en,style,txt): E.append(f"Dialogue: 0,{at(st)},{at(en)},{style},,0,0,0,,{txt}")
    D=D_MAP
    d(0.3,D,"Big",  "{\\pos(72,54)\\fad(220,0)}Rinnenseen")
    d(0.3,D,"Sub",  "{\\pos(76,152)\\fad(260,0)}Schleswig-Holstein · Holsteinische Schweiz")
    d(0.3,D,"Meta", "{\\pos(1848,52)\\fad(220,0)}TUNNELTÄLER")
    d(0.3,D,"MetaS","{\\pos(1848,92)\\fad(260,0)}vom Schmelzwasser gegraben")
    # editorial statement (instead of a running subtitle)
    d(0.5,3.0,"State","{\\an1\\pos(72,1006)\\fad(220,180)}Lange, schmale Seen —")
    d(3.05,D, "State","{\\an1\\pos(72,1006)\\fad(180,220)}wie Kratzer in der Landschaft.")
    # lake data-grid (right column)
    facts=[("Gr. Plöner See","30 km²"),("Selenter See","22 km²"),("Kellersee","5 km²")]
    for k,(nm,ar) in enumerate(facts):
        y=724+k*74
        d(1.3+0.25*k,D,"Fact", f"{{\\pos(1848,{y})\\fad(240,0)}}{nm}")
        d(1.3+0.25*k,D,"FactS",f"{{\\pos(1848,{y+30})\\fad(280,0)}}{ar}")
    a.write_text(ass_header(styles)+"\n".join(E)+"\n")

def beat_map():
    a=BUILD/"c11_mapcap.ass"; _poster_ass(a)
    fc=(f"[0:v]setsar=1,{MAP_GRADE},ass={a.as_posix()}:fontsdir={FONTS.as_posix()}[v]")
    run([FF,"-y","-framerate","30","-i",str(MAPF/"m_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_MAP),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c11_a.mp4")],"map")

# ---- beat B: GIF aesthetic filler inside a 35mm film-camera frame -------------
def beat_film():
    x0,y0,x1,y1=96,168,1824,912; ww,wh=x1-x0,y1-y0
    # loop the gif to cover the window, overlay the film frame, then grade
    fc=(f"[0:v]scale={ww}:{wh}:force_original_aspect_ratio=increase,crop={ww}:{wh},"
        f"fps=30,setsar=1[gif];"
        f"color=c=0x141110:s=1920x1080:r=30[bg];"
        f"[bg][gif]overlay={x0}:{y0}:shortest=0[win];"
        f"[win][1:v]overlay=0:0[fr];"
        f"[fr]{GRADE},vignette=PI/7,noise=alls=5:allf=t,format=yuv420p[v]")
    run([FF,"-y","-stream_loop","-1","-i",str(C11/"img"/"filler.gif"),
         "-loop","1","-i",str(BUILD/"c11_film.png"),
         "-filter_complex",fc,"-map","[v]","-t",str(D_FILM),"-r","30",
         "-c:v","libx264","-preset","medium","-crf","20",str(BUILD/"c11_b.mp4")],"film")

# ---- beat C: Hochdruckreiniger cut-out on white + blue editorial type ---------
def beat_wash():
    nf=int(D_WASH*30)+2; z="min(zoom+0.0005,1.05)"
    fc=(f"[0:v]scale=2304:-1,zoompan=z='{z}':d={nf}:s=1920x1080:fps=30,setsar=1,"
        f"{MAP_GRADE}[v]")
    run([FF,"-y","-loop","1","-i",str(BUILD/"c11_wash.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(D_WASH),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c11_c.mp4")],"wash")

# ---- beat D: real glacial meltwater channels ("Rinnen in die Landschaft") -----
def beat_rinnen():
    nf=int(D_RINNEN*30)+2; z="min(zoom+0.0009,1.10)"
    fc=(f"[0:v]scale=2304:1296:force_original_aspect_ratio=increase,crop=2304:1296,"
        f"zoompan=z='{z}':d={nf}:s=1920x1080:fps=30,setsar=1,{GRADE}[pre];"
        f"[1:v]scale=1920:1080,setsar=1[sc];"+CRT_TAIL+";[cg]copy[v]")
    run([FF,"-y","-loop","1","-i",str(C11/"img"/"rinnen.jpg"),"-loop","1","-i",SCAN,
         "-filter_complex",fc,"-map","[v]","-t",str(D_RINNEN),"-r","30","-c:v","libx264",
         "-preset","medium","-crf","20",str(BUILD/"c11_d.mp4")],"rinnen")

# ---- captions (film beat only) ----------------------------------------------
def write_captions():
    words=[]
    for seg in json.loads((AUD/"main_transcript.json").read_text())["segments"]:
        for w in seg["words"]:
            st=w.get("start")
            if st is None: continue
            rel=st-VO_START
            # captions only over the darker footage beats (GIF film + Rinnen);
            # the poster + the white washer editorial carry their own typography
            if (T_FILM0<=rel<T_FILM1) or (T_RIN0<=rel<T_RIN1):
                words.append(w)
    lines,cur=[],[]
    for w in words:
        cur.append(w)
        if len(cur)>=6 or w["word"].endswith((".","?","!",",",";",":")):
            lines.append(cur); cur=[]
    if cur: lines.append(cur)
    style=("Style: Cap,Liberation Sans,52,&H0000E9F4,&H0000E9F4,&H00101010,&H90101010,"
           "-1,0,0,0,100,100,0.2,0,1,2,2,2,160,160,150,1")
    ev=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i,ln in enumerate(lines):
        s=max(0.0,ln[0]["start"]-VO_START-0.05); e=ln[-1]["end"]-VO_START+0.12
        if i+1<len(lines): e=min(e, lines[i+1][0]["start"]-VO_START-0.03)
        txt="{\\fad(90,90)\\blur7}"+" ".join(w["word"] for w in ln)
        ev.append(f"Dialogue: 0,{at(s)},{at(e)},Cap,,0,0,0,,{txt}")
    (BUILD/"c11_caps.ass").write_text(ass_header([style])+"\n".join(ev)+"\n")

def final():
    write_captions()
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c11_song.wav")],"songbed")
    ass=(BUILD/"c11_caps.ass").as_posix()
    fc=(f"[0:v]ass={ass}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v];"
        f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c11_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c11_song.wav"),"-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",str(TOTAL),"-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"main_chunk11.mp4")],"final")
    print("  ->", OUT/"main_chunk11.mp4")

if __name__=="__main__":
    print("[1/6] poster"); beat_map()
    print("[2/6] film");   beat_film()
    print("[3/6] wash");   beat_wash()
    print("[4/6] rinnen"); beat_rinnen()
    (BUILD/"c11_concat.txt").write_text(
        "\n".join(f"file '{(BUILD/f'{o}.mp4').as_posix()}'"
                  for o in ["c11_a","c11_b","c11_c","c11_d"])+"\n")
    run([FF,"-y","-f","concat","-safe","0","-i",str(BUILD/"c11_concat.txt"),
         "-c","copy",str(BUILD/"c11_full.mp4")],"concat")
    print("[4/4] final"); final()
    print("DONE", round(TOTAL,2),"s")
