import numpy as np, json, librosa
y, sr = librosa.load('song.mp3', sr=22050, mono=True)
hop=512
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop, units='frames', tightness=400)
bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
d = np.diff(bt)
print('tempo', tempo, 'median ibi', np.median(d), 'std', d.std(), 'min', d.min(), 'max', d.max())
# fit linear grid
n = np.arange(len(bt))
A = np.vstack([n, np.ones_like(n)]).T
k, b = np.linalg.lstsq(A, bt, rcond=None)[0]
res = bt - (k*n+b)
print('grid period', k, 'offset', b, 'resid max', np.abs(res).max(), 'resid std', res.std())
# low-freq (kick) strength at each beat
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
low = S[(f>30)&(f<120)].sum(0)
lowd = np.maximum(0, np.diff(low, prepend=low[0]))
kick = np.array([lowd[max(0,x-2):x+3].max() for x in beats])
for ph in range(4):
    print('phase', ph, kick[ph::4].mean())
json.dump({'period':k,'offset':b,'beats':bt.tolist()}, open('grid.json','w'))
