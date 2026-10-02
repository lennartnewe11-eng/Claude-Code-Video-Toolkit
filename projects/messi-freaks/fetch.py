#!/usr/bin/env python3
"""Footage aus dem Internet Archive holen (nur, was edl.py verwendet).

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
    ('src/getafe07.mkv', 'ClassicAmazingGoalFromMessiVsGetafe1080iHDBarcelonaHd.blogspot.com',
     'Classic Amazing Goal From Messi Vs Getafe 1080iHD barcelona-hd.blogspot.com.mkv'),
    ('src/bilbao15.mp4', 'messi-mix-videos',
     'Lionel Messi Amazing Solo Goal vs Bilbao 30-05-2015 - Bilbao vs Barcelona 0-1.mp4'),
    ('src/iran14.ts', 'messi-mix-videos', 'Messi - Argentina (1) - (0) Iran.ts'),
    ('src/final22_hl.mp4', 'the-greatest-final-ever-argentina-v-france-fifa-world-cup-qatar-2022-highlights',
     'THE GREATEST FINAL EVER - Argentina v France - FIFA World Cup Qatar 2022 Highlights.mp4'),
    # WM 2022, offizielle FIFA-Highlights (1080p50)
    ('src/wc22_mex.webm', 'argentina-v-mexico', 'Argentina v Mexico.webm'),
    ('src/wc22_cro.webm', 'argentina-v-croatia', 'Argentina v Croatia.webm'),
]

W14 = ('wc-2014-final-germany-vs-argentina-1080p-satfeed-422', 'FIFA.WC2014.Final.Ger-Arg.1080i.H264_422.HDFEED.ts')
W22 = ('2022_argentina_france', 'FIFA.WC2022.Final.Argentina-France.mkv')
N21 = ('nos-news-2021-08-08', 'NOS-Journaal-NPO-12021-08-0820-00.ts')
ANF = ('liverpoolvsbarcelona2019', 'Liverpool vs Barcelona (2).mp4')
R16 = ('argentino-reacciona-a-la-final-de-copa-ame-rica-centenario-contra-chile-2016.-sigue-doliendo',
       'ARGENTINO REACCIONA A LA FINAL DE COPA AMÉRICA CENTENARIO CONTRA CHILE (2016). ¿SIGUE DOLIENDO¿.mp4')
B15 = ('barcelona-vs-bayern-munich-ida-semifinal-champions-league-2014-15-partido-comple',
       'Barcelona.Vs.Bayern.Munich.Full.Match.HD720p.akoam.com_33096141455.mp4')
M17 = ('2017.04.23-la-liga-j-33-madrid-vs-barca', '2017.04.23 - (LaLiga J33) - Madrid vs Barça.mkv')

# (Zieldatei, Quelle, Start s, Dauer s, Filter)   Zeiten per Kontaktbogen gesucht
CUTS = [
    ('b15_drib', B15, 4846, 32, 'null'),
    ('m17_goal', M17, 6116, 14, 'null'), ('m17_celeb', M17, 6172, 18, 'null'),
    ('w14_chance', W14, 6370, 36, 'yadif=1'), ('w14_goetze', W14, 11376, 26, 'yadif=1'),
    ('c14_walk', W14, 13048, 14, 'yadif=1'),
    ('r16_pen', R16, 1126, 18, 'null'), ('r16_cry', R16, 1158, 32, 'null'),
    ('anf19', ANF, 3028, 14, 'null'),
    ('n21_cry_b', N21, 592, 12, 'yadif=1'),
    ('c22_lift', W22, 13090, 28, 'null'),
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
                        '-vf', vf if vf.startswith('scale') else f"{vf},scale='min(1920,iw)':-2:flags=lanczos", '-c:v', 'libx264', '-crf', '14',
                        '-preset', 'veryfast', '-pix_fmt', 'yuv420p', p], check=True)
    return name


def get_cascades():
    """Haar-Kaskaden für faces.py (OpenCV 5 liefert sie nicht mehr mit): aus dem 4.10-Wheel."""
    import glob
    import tempfile
    import zipfile
    dst = os.path.join(MEDIA, 'models')
    os.makedirs(dst, exist_ok=True)
    if glob.glob(os.path.join(dst, 'haarcascade_frontalface_default.xml')):
        return
    tmp = tempfile.mkdtemp()
    subprocess.run([sys.executable, '-m', 'pip', 'download', '--no-deps', 'opencv-python-headless==4.10.0.84',
                    '-d', tmp], check=True)
    z = zipfile.ZipFile(glob.glob(os.path.join(tmp, '*.whl'))[0])
    for n in z.namelist():
        if n.endswith(('frontalface_default.xml', 'frontalface_alt2.xml')):
            open(os.path.join(dst, os.path.basename(n)), 'wb').write(z.read(n))


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
    get_cascades()


if __name__ == '__main__':
    main()
