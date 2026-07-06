#!/usr/bin/env python3
"""Main part - Chunk 12 (VO 228.84 -> ~242.84s): the Deutschlandkarte payoff.
One editorial map beat: Germany relief on the Swiss-poster yellow, gentle camera
moves, the two lake CLUSTERS (North Seenplatte / South Alpenvorland) revealing in
sync with the VO while the middle stays empty. Big prominent editorial typography
carries the narration (no running subtitles).
"""
import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD, OUT, MA, AUD, FONTS = (ROOT/"build", ROOT/"out", ROOT/"main_assets",
                              ROOT/"audio", ROOT/"fonts")
FF="ffmpeg"; MAPF=BUILD/"c12_map_f"

VO_START=228.84
SONG_OFFSET=305.74                      # continues the looped song from chunk 11
TOTAL=14.0
ORGA="&H001A3AE8"                       # red-orange in ASS BGR (ties to the dots)

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

def _ass(a):
    BK="&H00181410"; GY="&H00403830"
    styles=[
      f"Style: Mast,Anton,128,{BK},{BK},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
      f"Style: Sub,Liberation Sans,33,{GY},{GY},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
      f"Style: Meta,Liberation Sans,26,{BK},{BK},&H00FFFFFF,&H90101010,-1,0,0,0,100,100,3,0,1,0,0,9,0,0,0,1",
      f"Style: MetaS,Liberation Sans,26,{GY},{GY},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1",
      f"Style: Big,Anton,104,{ORGA},{ORGA},&H00FFFFFF,&H90101010,0,0,0,0,100,100,0,0,1,0,0,1,0,0,0,1",
      f"Style: Tag,Liberation Sans,28,{BK},{BK},&H00FFFFFF,&H90101010,-1,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1",
      f"Style: TagS,Liberation Sans,24,{GY},{GY},&H00FFFFFF,&H90101010,0,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1"]
    E=["[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    def d(st,en,style,txt): E.append(f"Dialogue: 0,{at(st)},{at(en)},{style},,0,0,0,,{txt}")
    D=TOTAL
    # masthead + meta (persistent)
    d(0.4,D,"Mast","{\\pos(70,34)\\fad(300,0)}DEUTSCHLAND")
    d(0.4,D,"Sub", "{\\pos(78,196)\\fad(340,0)}Wo die Seen liegen \\N– und wo nicht")
    d(0.4,D,"Meta","{\\pos(1848,50)\\fad(300,0)}SEENVERTEILUNG")
    d(0.4,D,"MetaS","{\\pos(1848,88)\\fad(340,0)}folgt dem Eis")
    # big region labels (lower-left), swapping with the narration
    d(4.3,7.05,"Big","{\\an1\\pos(70,1016)\\fad(220,150)}IM NORDEN")
    d(7.1,11.45,"Big","{\\an1\\pos(70,1016)\\fad(180,150)}IM SÜDEN")
    d(11.5,D,  "Big","{\\an1\\pos(70,1016)\\fad(180,220)}DIE MITTE: FAST LEER")
    # right-side tags, timed
    d(4.7,7.05,"Tag", "{\\pos(1848,150)\\fad(200,120)}Mecklenburgische Seenplatte")
    d(4.7,7.05,"TagS","{\\pos(1848,186)\\fad(220,120)}Norden · Eiszeit-Tiefland")
    d(7.3,11.45,"Tag", "{\\pos(1848,150)\\fad(200,120)}Alpenvorland · Bodensee")
    d(7.3,11.45,"TagS","{\\pos(1848,186)\\fad(220,120)}Süden · Alpengletscher")
    d(10.0,D,"TagS","{\\pos(1848,980)\\fad(240,0)}genau dort, wo das Eis lag")
    a.write_text(ass_header(styles)+"\n".join(E)+"\n")

def beat():
    a=BUILD/"c12_cap.ass"; _ass(a)
    fc=(f"[0:v]setsar=1,{MAP_GRADE},ass={a.as_posix()}:fontsdir={FONTS.as_posix()},"
        f"fade=t=in:d=0.4,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[v]")
    run([FF,"-y","-framerate","30","-i",str(MAPF/"m_%04d.png"),"-filter_complex",fc,
         "-map","[v]","-t",str(TOTAL),"-r","30","-c:v","libx264","-preset","medium",
         "-crf","20",str(BUILD/"c12_full.mp4")],"beat")

def final():
    run([FF,"-y","-stream_loop","4","-i",str(AUD/"song.mp3"),
         "-af",f"atrim={SONG_OFFSET}:{SONG_OFFSET+TOTAL},asetpts=PTS-STARTPTS",
         "-t",str(TOTAL),str(BUILD/"c12_song.wav")],"songbed")
    fc=(f"[1:a]atrim={VO_START}:{VO_START+TOTAL},asetpts=PTS-STARTPTS,volume=1.15,asplit=2[vo1][vo2];"
        f"[2:a]volume=0.85[song];"
        f"[song][vo2]sidechaincompress=threshold=0.04:ratio=7:attack=12:release=320:makeup=1[sd];"
        f"[sd][vo1]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]")
    run([FF,"-y","-i",str(BUILD/"c12_full.mp4"),"-i",str(AUD/"main_vo.wav"),
         "-i",str(BUILD/"c12_song.wav"),"-filter_complex",fc,"-map","0:v","-map","[a]",
         "-t",str(TOTAL),"-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",
         str(OUT/"main_chunk12.mp4")],"final")
    print("  ->", OUT/"main_chunk12.mp4")

if __name__=="__main__":
    print("[1/2] beat"); beat()
    print("[2/2] final"); final()
    print("DONE", round(TOTAL,2),"s")
