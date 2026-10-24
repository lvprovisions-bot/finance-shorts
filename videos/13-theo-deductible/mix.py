"""THEO EXPLAINS #3 mix: voice + soft synth music bed + whooshes/pops into mix.wav (48 kHz stereo)."""
import json, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
sr0, v = wavfile.read(os.path.join(HERE, "voice.wav"))
v = resample_poly(v.astype(np.float32) / 32768, SR, sr0)
TM = json.load(open(os.path.join(HERE, "timings.json")))
N = int((TM["total"] + 0.4) * SR)
voice = np.zeros(N, np.float32); voice[:len(v)] = v[:N]
t = np.arange(N) / SR
rng = np.random.default_rng(7)

# ---- music: Am7 - Fmaj7 - C - G, 96 bpm, warm pad + soft pluck + kick ----
bpm = 112; beat = 60 / bpm; bar = 4 * beat
def hz(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[53, 57, 60, 64], [55, 59, 62, 65], [50, 57, 60, 65], [52, 55, 60, 64]]
pad = np.zeros(N, np.float32); pluck = np.zeros(N, np.float32); kick = np.zeros(N, np.float32)
nbars = int(N / SR / bar) + 1
for b in range(nbars):
    ch = chords[b % 4]; s0 = int(b * bar * SR); s1 = min(N, int((b + 1) * bar * SR))
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.4)
    for m in ch:
        f = hz(m)
        pad[s0:s1] += env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.3) + 0.15 * np.sin(2 * np.pi * f * 1.003 * tt)) / 4
    # arpeggio plucks on 8th notes
    for k in range(8):
        ps = s0 + int(k * beat / 2 * SR)
        if ps >= N: break
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
        L = min(int(0.5 * SR), N - ps); tt2 = np.arange(L) / SR
        pluck[ps:ps + L] += np.sin(2 * np.pi * hz(m) * tt2) * np.exp(-tt2 * 9) * 0.5
    # kick on 1 and 3
    for k in (0, 2):
        ps = s0 + int(k * beat * SR)
        if ps >= N: break
        L = min(int(0.3 * SR), N - ps); tt2 = np.arange(L) / SR
        f = 50 + 70 * np.exp(-tt2 * 30)
        kick[ps:ps + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt2 * 12)
sos = butter(2, 2500, "low", fs=SR, output="sos")
music = sosfilt(sos, pad * 0.5 + pluck * 0.35) + kick * 0.45
music /= np.abs(music).max()

# duck music under the voice
envv = np.abs(voice)
k = int(0.15 * SR); envv = np.convolve(envv, np.ones(k) / k, mode="same")
duck = 1 - 0.55 * np.clip(envv / 0.05, 0, 1)
music = music * duck * 0.16
fade = np.minimum(1, t / 0.3) * np.minimum(1, (t[-1] - t) / 0.25)
music *= fade

# ---- sfx ----
sfx = np.zeros(N, np.float32)
def whoosh(at, dur=0.35, g=0.18):
    s = int(max(0, at - dur * 0.7) * SR); L = min(int(dur * SR), N - s)
    n = rng.standard_normal(L).astype(np.float32)
    tt = np.arange(L) / L
    env = np.sin(np.pi * tt) ** 2
    lo = butter(2, 1800, "low", fs=SR, output="sos"); hi = butter(2, 300, "high", fs=SR, output="sos")
    sfx[s:s + L] += sosfilt(hi, sosfilt(lo, n)) * env * g * 3
def pop(at, f0=900, g=0.22):
    s = int(at * SR); L = min(int(0.12 * SR), N - s); tt = np.arange(L) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt * 40))
    sfx[s:s + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 35) * g
def boom(at, g=0.5):
    s = int(at * SR); L = min(int(0.6 * SR), N - s); tt = np.arange(L) / SR
    f = 40 + 90 * np.exp(-tt * 18)
    sfx[s:s + L] += (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6)) * g

prev = None
for s in TM["segments"]:
    if prev is not None:
        whoosh(s["start"], g=0.12)
    prev = s["scene"]
seg = {s["scene"]: s for s in TM["segments"]}
tk = lambda sc, i: seg[sc]["tokens"][i]["start"]
boom(0.05, 0.25)
boom(tk("no", 1), 0.35); pop(tk("no", 1), 500, 0.3)
pop(tk("what", 1), 1000); pop(tk("what", 3), 1200)
boom(tk("pole", 2), 0.45)
pop(tk("repair", 3), 700); pop(tk("repair", 5), 1300)
pop(tk("scratch", 1), 1600, 0.15)
pop(tk("zero", 2), 500, 0.3)
pop(seg["tip"]["start"], 1000); pop(tk("tip", 2), 1200); pop(tk("tip", 4), 1400)
pop(tk("punch", 1), 1400); pop(tk("punch", 2), 1600)
pop(seg["q"]["start"], 1200)

mix = voice * 1.0 + music + sfx
mix /= max(1.0, np.abs(mix).max() / 0.95)
st = np.stack([mix, mix], 1)
wavfile.write(os.path.join(HERE, "mix.wav"), SR, (st * 32767).astype(np.int16))
print("mix ok", round(N / SR, 2))
