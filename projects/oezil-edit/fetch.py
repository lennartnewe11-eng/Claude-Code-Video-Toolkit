#!/usr/bin/env python3
"""Footage aus dem Internet Archive holen (YouTube blockt dieses Rechenzentrum).

Kurze Dateien werden ganz geladen; aus kompletten Spielübertragungen wird per
HTTP-Range nur das benötigte Segment gezogen (-ss vor -i). PAL-Quellen mit
anamorphen Pixeln (720x576, 352x288) werden dabei auf quadratische Pixel
gebracht, Halbbilder aufgelöst.

    python3 fetch.py            # lädt nach media/src und media/cuts
    python3 fetch.py --list     # nur die Quellenliste

Der Song ist nicht Teil des Repos: media/audio/song.mp3 (vom Auftraggeber).
Schriften (Oswald, IBM Plex Mono) und Haar-Kaskaden liegen wie in ../neymar-edit
unter media/fonts und media/models.
"""
import os
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'media')
IA = 'https://archive.org/download/'

# (Ziel, Item, Datei im Item)
FULL = [
    ('src/cr1112.avi', 'CristianoRonaldoAllGoals2011-12', 'CristianoRonaldoAllGoals2011-12.avi'),
    ('src/ars_ludo16.mp4', 'Arsenal60Ludogorets', 'Arsenal 6-0 Ludogorets.mp4'),
    ('src/ars_mu15.mp4', 'MOTD2_201903', 'MOTD2-阿森纳对曼联.mp4'),
    ('src/ref_liberace.mp4', 'LiberaceChristmasShow', 'Liberace Christmas Show.mp4'),
    ('src/ref_lauda.mp4', 'RennfahrerlegendeNikiLaudaIstTot', 'Rennfahrerlegende Niki Lauda ist tot.mp4'),
]

RMB = ('realmadridbayern2012', 'Real Madrid Bayern 1er tiempo.mp4')
BRM = ('bayernrealmadrid2012', 'Bayern Real Madrid 2do tiempo.mp4')
ARG = ('alemania-argentina-vignolo', 'Alemania Argentina Vignolo.mp4')
ALG = ('jalkapallon-mm-kisat-porto-alegre-2014-neljannesvaliera-saksa-vs.-algeria',
       'Jalkapallon MM-kisat Porto Alegre 2014 Neljännesvälierä Saksa vs. Algeria.MP4')
FAC = ('arsenal-fc-vs-aston-villa-final-fa-cup-2014-2015-partido-completofull-match',
       'FA_Cup_Final_2015_FC_Arsenal_vs_Aston_Villa_201505.mp4')
A13 = ('arsenal-end-of-season-review-2013-14', 'Arsenal - End of Season Review 2013-14.mp4')
KOR = ('alemania-vs-corea-del-sur-fase-de-grupos-copa-mundial-de-futbol-2018-partido-com', 'korger2018ES.mp4')
KOB = ('youtube-qxJzA2np0BE', 'qxJzA2np0BE.mp4')
JOB = ('mw2007_iphone1000_100.1', 'mw2007_iphone1000_100.1.m4v')
NAC = ('oi43032', '43031.BG_9717.mpg')
WHI = ('oi52540', '52539.WEEKNUMMER262-HRE000275E1.mpg')

HD = "scale='min(1920,iw)':-2:flags=lanczos"
PAL169 = 'yadif=1,scale=1024:576,setsar=1'           # 720x576 anamorph 16:9, Halbbilder
PAL43 = 'scale=768:576,setsar=1'                      # 720x576 anamorph 4:3 (Quelle progressiv)
CIF = 'fps=25,yadif=0:-1:0,scale=384:288,setsar=1'    # Polygoon-Wochenschau, 352x288

# (Ziel, Quelle, Start s, Dauer s, Filter)   Zeiten per Kontaktbogen gesucht
CUTS = [
    ('rmb12_20', RMB, 1190, 150, HD),        # Özils Pass, Ronaldo 2:0
    ('brm12_oz', BRM, 430, 190, HD),         # Özils 1:1 in München, Jubel, Nahaufnahmen
    ('brm12_sub', BRM, 1425, 50, HD),        # Özil geht vom Platz
    ('arg10', ARG, 90, 80, 'null'),          # WM 2010, Hymne
    ('alg14', ALG, 8080, 120, PAL43),        # WM 2014, Özils 2:0 gegen Algerien
    ('fac15', FAC, 3220, 45, 'null'),        # FA-Cup-Finale 2015, Jubel mit Bellerín
    ('a13_sign', A13, 1486, 130, PAL169),    # Vorstellung bei Arsenal 2013
    ('kor18', KOR, 168, 34, 'null'),         # WM 2018, Hymne
    ('ref_kobe', KOB, 5512, 30, HD),         # Kobe Bryant, Wurf gegen Phoenix 2006
    ('ref_jobs', JOB, 2380, 200, HD),        # Macworld 2007, das erste iPhone
    ('ref_nachtwacht', NAC, 0, 151, CIF),    # Polygoon 1976, Rembrandts Nachtwache
    ('ref_whiteman', WHI, 0, 132, CIF),      # Polygoon 1926, Paul Whiteman
]


def url(item, name):
    return IA + item + '/' + urllib.parse.quote(name)


def get_full(e):
    out, item, name = e
    p = os.path.join(MEDIA, out)
    if not os.path.exists(p):
        subprocess.run(['curl', '-sSL', '--retry', '3', '-o', p, url(item, name)], check=True)
    return out


def get_cut(e):
    name, (item, fn), t0, dur, vf = e
    p = os.path.join(MEDIA, 'cuts', name + '.mp4')
    if not os.path.exists(p):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-i', url(item, fn), '-t', str(dur), '-an',
                        '-vf', vf, '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', p],
                       check=True)
    return name


def main():
    if '--list' in sys.argv:
        for out, item, name in FULL:
            print(f'{out:24s} {url(item, name)}')
        for name, (item, fn), t0, dur, _ in CUTS:
            print(f'cuts/{name:19s} {url(item, fn)}  @{t0}s +{dur}s')
        return
    for d in ('src', 'cuts', 'audio', 'fonts', 'models'):
        os.makedirs(os.path.join(MEDIA, d), exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(get_full, FULL):
            print('ok', r)
        for r in ex.map(get_cut, CUTS):
            print('ok', r)


if __name__ == '__main__':
    main()
