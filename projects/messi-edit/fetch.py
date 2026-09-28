#!/usr/bin/env python3
"""Footage aus dem Internet Archive holen.

Kurze Dateien werden ganz geladen. Aus kompletten Spielübertragungen (bis 86 GB)
wird per HTTP-Range nur das benötigte Segment gezogen und als Zwischencodec
abgelegt (-ss vor -i: ffmpeg springt im Remote-Stream, lädt nur Bruchteile).

    python3 fetch.py            # lädt nach media/src und media/cuts
    python3 fetch.py --list     # nur die Quellenliste

Der Song ist nicht Teil des Repos: media/audio/song.mp3 (vom Auftraggeber).
"""
import os
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'media')
IA = 'https://archive.org/download/'

# (Zieldatei, Item, Datei im Item)
FULL = [
    ('src/first_goal05.mp4', 'messi-mix-videos', 'El primer gol de Messi (01 05 2005).mp4'),
    ('src/bilbao15.mp4', 'messi-mix-videos',
     'Lionel Messi Amazing Solo Goal vs Bilbao 30-05-2015 - Bilbao vs Barcelona 0-1.mp4'),
    ('src/lamasia.mp4', 'messi-mix-videos', 'Young Lionel Messi At La Masia - FC Barcelona More Than A Club HD.mp4'),
    ('src/ballondor09_11.mp4', 'messi-mix-videos', "Lionel Messi - FIFA Ballon D'Or 2009 - 2010 - 2011.mp4"),
    ('src/getafe07.mkv', 'ClassicAmazingGoalFromMessiVsGetafe1080iHDBarcelonaHd.blogspot.com',
     'Classic Amazing Goal From Messi Vs Getafe 1080iHD barcelona-hd.blogspot.com.mkv'),
    ('src/wembley11.mkv', '12MessiUCLFinalBarcelonaManchesterUnited28052011',
     '12_Messi_UCL_Final_Barcelona_Manchester-United_28-05-2011.mkv'),
    ('src/psg17_end.mp4', '2017.03.08-ucl-r-16-g-2-barcelona-psg-6-2', 'UCL-20170308-R16-G2-Barcelona Ending.mp4'),
    ('src/final22_hl.mp4', 'the-greatest-final-ever-argentina-v-france-fifa-world-cup-qatar-2022-highlights',
     'THE GREATEST FINAL EVER - Argentina v France - FIFA World Cup Qatar 2022 Highlights.mp4'),
    ('src/ucl09_2h.mp4', 'EcondHalfOfBarcelona2-0ManchesterUnited--FinalUcl2008-2009',
     'SecondHalfOfBarcelona2-0ManchesterUnited--FinalUcl2008-2009.mp4'),
]

W14 = ('wc-2014-final-germany-vs-argentina-1080p-satfeed-422', 'FIFA.WC2014.Final.Ger-Arg.1080i.H264_422.HDFEED.ts')
W22 = ('2022_argentina_france', 'FIFA.WC2022.Final.Argentina-France.mkv')
W26 = ('spain-vs-argentina-fwc-2026-final-bbc-uhd', 'Spain vs Argentina - FWC 2026 Final - BBC UHD.mkv')
C21a = ('argentinavsbrasil2021', 'Argentina vs Brasil (3).mp4')
C21b = ('argentinavsbrasil2021', 'Argentina vs Brasil (4).mp4')
N21 = ('nos-news-2021-08-08', 'NOS-Journaal-NPO-12021-08-0820-00.ts')
ANF = ('liverpoolvsbarcelona2019', 'Liverpool vs Barcelona (2).mp4')
SAU = ('argentinavsarabia2022', 'Argentina vs Arabia (2).mp4')
R16 = ('argentino-reacciona-a-la-final-de-copa-ame-rica-centenario-contra-chile-2016.-sigue-doliendo',
       'ARGENTINO REACCIONA A LA FINAL DE COPA AMÉRICA CENTENARIO CONTRA CHILE (2016). ¿SIGUE DOLIENDO¿.mp4')
B15 = ('barcelona-vs-bayern-munich-ida-semifinal-champions-league-2014-15-partido-comple',
       'Barcelona.Vs.Bayern.Munich.Full.Match.HD720p.akoam.com_33096141455.mp4')
M17 = ('2017.04.23-la-liga-j-33-madrid-vs-barca', '2017.04.23 - (LaLiga J33) - Madrid vs Barça.mkv')

# (Zieldatei, Quelle, Start s, Dauer s, Filter)   Zeiten per Kontaktbogen gesucht
CUTS = [
    ('c14_alone', W14, 12768, 14, 'yadif=1'), ('c14_golden', W14, 13012, 16, 'yadif=1'),
    ('c14_walk', W14, 13048, 14, 'yadif=1'), ('c14_pitch', W14, 13084, 30, 'yadif=1'),
    ('c14_ref', W14, 11795, 12, 'yadif=1'),
    ('c22_kiss', W22, 12336, 18, 'null'), ('c22_gball', W22, 12364, 18, 'null'),
    ('c22_bisht', W22, 13028, 22, 'null'), ('c22_trophy', W22, 13064, 20, 'null'),
    ('c22_lift', W22, 13090, 28, 'null'),
    ('c26_medal', W26, 16484, 12, 'null'), ('c26_trophy', W26, 16562, 28, 'null'),
    ('c26_back', W26, 16600, 14, 'null'), ('c26_tears', W26, 16612, 26, 'null'),
    ('c26_spain', W26, 17030, 40, 'null'),
    ('c21_pile', C21a, 3136, 16, 'null'), ('c21_smile', C21b, 224, 14, 'null'),
    ('c21_raise', C21b, 292, 40, 'null'),
    ('n21_cry_a', N21, 570, 8, 'yadif=1'), ('n21_cry_b', N21, 592, 12, 'yadif=1'),
    ('anf19', ANF, 3028, 14, 'null'), ('sau22', SAU, 2744, 12, 'null'),
    ('r16_pen', R16, 1126, 18, 'null'), ('r16_cry', R16, 1158, 32, 'null'), ('r16_after', R16, 1200, 30, 'null'),
    ('b15_drib', B15, 4846, 32, 'null'), ('m17_celeb', M17, 6172, 18, 'null'),
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
                        '-vf', f"{vf},scale='min(1920,iw)':-2:flags=lanczos", '-c:v', 'libx264', '-crf', '14',
                        '-preset', 'veryfast', '-pix_fmt', 'yuv420p', p], check=True)
    return name


def main():
    if '--list' in sys.argv:
        for out, item, name in FULL:
            print(f'{out:28s} {url(item, name)}')
        for name, (item, fn), t0, dur, _ in CUTS:
            print(f'cuts/{name:23s} {url(item, fn)}  @{t0}s +{dur}s')
        return
    for d in ('src', 'cuts', 'audio', 'fonts'):
        os.makedirs(os.path.join(MEDIA, d), exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(get_full, FULL):
            print('ok', r)
        for r in ex.map(get_cut, CUTS):
            print('ok', r)


if __name__ == '__main__':
    main()
