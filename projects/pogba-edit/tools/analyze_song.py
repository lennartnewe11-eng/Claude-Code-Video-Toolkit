import librosa, numpy as np, json
y, sr = librosa.load('song.mp3', sr=22050, mono=True)
dur = len(y)/sr
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
print('dur', dur, 'tempo', tempo, 'nbeats', len(beats))
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
rms = librosa.feature.rms(y=y)[0]
t = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
# per-2s energy
for s in range(0, int(dur), 2):
    m = (t>=s)&(t<s+2)
    e = rms[m].mean()
    # low-frequency energy
    print(f"{s:4d}s {'#'*int(e*200):<60} {e:.3f}")
np.save('beats.npy', beats)
# bass band energy for kicks
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
bass = S[freqs<150].sum(axis=0)
np.save('bass.npy', bass)
np.save('onset.npy', onset_env)
json.dump({'tempo': float(np.atleast_1d(tempo)[0]), 'beats': beats.tolist()}, open('beats.json','w'))
