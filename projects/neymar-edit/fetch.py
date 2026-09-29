#!/usr/bin/env python3
"""Footage aus dem Internet Archive holen (YouTube blockt dieses Rechenzentrum).

Kurze Dateien werden ganz geladen; aus den kompletten Spielübertragungen wird per
HTTP-Range nur das benötigte Segment gezogen (-ss vor -i).

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

FULL = [
    ('src/santos_colo.mp4', 'gols-colo-colo-chi-3-x-2-santos-bra-libertadores-2011-globo-hd_202504',
     'Gols - Colo-Colo (CHI) 3 x 2 Santos (BRA) - Libertadores 2011 - Globo HD.mp4'),
    ('src/santos_final11.mp4', 'jogos-historicos-santos-2-x-1-penarol-melhores-momentos-final-libertadores-22-06-2011-720-p-hd',
     'Jogos Históricos _ Santos 2 x 1 Peñarol _ Melhores Momentos _ Final Libertadores _ 22_06_2011(720P_HD).mp4'),
    ('src/london12.mp4', 'youtube-KfjUUrY2CEA',
     'Neymar_Jr_-_Giochi_Olimici_Di_Londra_2012_Hall_Of_Fame_HD_Re-Upload-KfjUUrY2CEA.mp4'),
    ('src/aus13.ts', 'Brazil3VS0AustraliaNeymar1080iBarcelonaHd.blogspot.com',
     'Brazil 3 VS 0 Australia Neymar 1080i barcelona-hd.blogspot.com.ts'),
    ('src/confed13_hl.mp4', 'jogo-histo-rico-brasil-3-x-0-espanha-melhores-momentos-final-copa-das-confederaco-es-2013-720-p-hd',
     'JOGO HISTÓRICO _ BRASIL 3 X 0 ESPANHA _ MELHORES MOMENTOS _ FINAL COPA DAS CONFEDERAÇÕES 2013(720P_HD).mp4'),
    ('src/psg17_end.mp4', '2017.03.08-ucl-r-16-g-2-barcelona-psg-6-2', 'UCL-20170308-R16-G2-Barcelona Ending.mp4'),
    ('src/samba.mp4', 'neymar-jr-samba-dance', 'Neymar Jr Samba Dance.mp4'),
    # Saison 2014/15: Saisonrückblick in zwei Teilen (je ~1,5 GB), Athletic, Sevilla, Pokalfinale
    ('src/b1415_1.mp4', 'barcelona-2014-15', 'Barcelona 2014-15 (1).mp4'),
    ('src/b1415_2.mp4', 'barcelona-2014-15', 'Barcelona 2014-15 (2).mp4'),
    # Champions-League-Finale Berlin 2015, die letzten Minuten bis zum 3:1
    ('src/berlin95.mkv', '4RakiticKora1hd.blogspot.com', "95' Neymar kora-1hd.blogspot.com.mkv"),
]

OLY = ('2016-olympic-games-Rio-Men-football-soccer-all-matchs-in-HD-no-ads-no-commentary',
       '2016_08_20_20_19 - Football (H) - Finale - Brésil v Allemagne.ts')
CRO = ('croatia-vs-brazil-fifa-world-cup-2022', '1 Croatia v Brazil - BBC UHD.mkv')

# (Ziel, Quelle, Start s, Dauer s, Filter, Ton)   Zeiten per Kontaktbogen gesucht
CUTS = [
    ('oly_pre', OLY, 380, 140, 'yadif=0:-1:1,scale=1280:-2', False),
    ('oly_stadium', OLY, 3515, 60, 'yadif=0:-1:1,scale=1280:-2', False),
    ('oly_fk', OLY, 3640, 80, 'yadif=0:-1:1,scale=1280:-2', False),
    ('oly_so', OLY, 9950, 245, 'yadif=0:-1:1,scale=1280:-2', True),
    ('oly_pen', OLY, 10195, 170, 'yadif=0:-1:1,scale=1280:-2', True),   # Ton: Clean Feed für audio.py
    ('oly_medal', OLY, 12380, 180, 'yadif=0:-1:1,scale=1280:-2', False),
    ('cro22', CRO, 8618, 82, 'scale=1920:-2:flags=lanczos', False),
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
    name, (item, fn), t0, dur, vf, sound = e
    p = os.path.join(MEDIA, 'cuts', name + '.mp4')
    if not os.path.exists(p):
        a = ['-c:a', 'aac', '-b:a', '192k'] if sound else ['-an']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-i', url(item, fn), '-t', str(dur),
                        '-vf', vf, '-c:v', 'libx264', '-crf', '14', '-preset', 'veryfast', '-pix_fmt', 'yuv420p']
                       + a + [p], check=True)
    return name


def main():
    if '--list' in sys.argv:
        for out, item, name in FULL:
            print(f'{out:24s} {IA}{item}')
        for name, (item, fn), t0, dur, *_ in CUTS:
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
