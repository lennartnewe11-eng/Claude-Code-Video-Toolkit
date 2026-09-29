#!/usr/bin/env python3
"""Footage aus dem Internet Archive holen (YouTube blockt dieses Rechenzentrum).

Kurze Dateien werden ganz geladen; aus kompletten Spielübertragungen wird per
HTTP-Range nur das benötigte Segment gezogen (-ss vor -i). PAL-Quellen mit
anamorphen Pixeln (720x576, 352x288) werden dabei auf quadratische Pixel
gebracht, Halbbilder aufgelöst. Die WM 2014 kommt aus dem Weltbild (720p50, ohne
Kommentar), nicht aus Senderaufzeichnungen.

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
    ('src/best.mp4', 'MesutOzil', 'Mesut_Ozil.mp4'),
    ('src/cr1112.avi', 'CristianoRonaldoAllGoals2011-12', 'CristianoRonaldoAllGoals2011-12.avi'),
    ('src/ars_ludo16.mp4', 'Arsenal60Ludogorets', 'Arsenal 6-0 Ludogorets.mp4'),
    ('src/ars_mu15.mp4', 'MOTD2_201903', 'MOTD2-阿森纳对曼联.mp4'),
    ('src/ars_swa16.mp4', 'arsenal-3-2-swansea-city-motd-highlights-saturday-15th-october-2016',
     'Arsenal 3-2 Swansea City - MOTD Highlights (Saturday 15th October 2016).mp4'),
    ('src/ars_whu16.mp4', 'west-ham-united-1-5-arsenal-motd-highlights-saturday-3rd-december-2016',
     'West Ham United 1-5 Arsenal - MOTD Highlights (Saturday 3rd December 2016).mp4'),
]

RMB = ('realmadridbayern2012', 'Real Madrid Bayern 1er tiempo.mp4')
BRM = ('bayernrealmadrid2012', 'Bayern Real Madrid 2do tiempo.mp4')
ARG = ('alemania-argentina-vignolo', 'Alemania Argentina Vignolo.mp4')
WC14 = 'FIFAWorldCup2014AllGamesHDFEEDENINT720pUploadedByKarimHassan'      # Weltbild, 720p50
ALG = (WC14, 'Game 54 - Round of 16 - G1 vs H2 - 720p - HD FEED - Papai.mkv')
FIN = (WC14, 'Game 64 - Final - 720p - HD Feed - Papai.mkv')
FAC = ('arsenal-fc-vs-aston-villa-final-fa-cup-2014-2015-partido-completofull-match',
       'FA_Cup_Final_2015_FC_Arsenal_vs_Aston_Villa_201505.mp4')
A13 = ('arsenal-end-of-season-review-2013-14', 'Arsenal - End of Season Review 2013-14.mp4')
KOR = ('alemania-vs-corea-del-sur-fase-de-grupos-copa-mundial-de-futbol-2018-partido-com', 'korger2018ES.mp4')

HD = "scale='min(1920,iw)':-2:flags=lanczos"
PAL169 = 'yadif=1,scale=1024:576,setsar=1'           # 720x576 anamorph 16:9, Halbbilder

# (Ziel, Quelle, Start s, Dauer s, Filter)   Zeiten per Kontaktbogen gesucht
CUTS = [
    ('rmb12_20', RMB, 1190, 150, HD),        # Özils Pass, Ronaldo 2:0
    ('brm12_oz', BRM, 430, 190, HD),         # Özils 1:1 in München, Jubel, Nahaufnahmen
    ('arg10', ARG, 90, 80, 'null'),          # WM 2010, Hymne
    ('arg10_40', ARG, 5690, 110, 'null'),    # WM 2010, Özils Vorlage zum 4:0
    ('alg14hd', ALG, 11290, 110, 'null'),    # WM 2014, Özils 2:1 gegen Algerien, Jubel mit Schürrle
    ('wc14_cer2', FIN, 13920, 130, 'null'),  # WM-Finale 2014, Özil mit dem Pokal
    ('fac15', FAC, 3220, 45, 'null'),        # FA-Cup-Finale 2015, Jubel mit Bellerín
    ('a13_sign', A13, 1486, 130, PAL169),    # Vorstellung bei Arsenal 2013, Fotoshooting
    ('a13_nap0', A13, 2030, 40, PAL169),     # Arsenal - Napoli 2013, Özils Volley
    ('kor18', KOR, 168, 34, 'null'),         # WM 2018, Hymne
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
