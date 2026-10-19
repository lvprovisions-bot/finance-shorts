"""Long-form mix: voice + gentle synth bed (two alternating progressions) + soft whoosh on scene changes."""
import json, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
sr0, v = wavfile.read(os.path.join(HERE, "voice.wav"))
v = resample_poly(v.astype(np.float32) / 32768, SR, sr0)
TM = json.load(open(os.path.join(HERE, "timings.json")))
N = int((TM["total"] + 0.5) * SR)
voice = np.zeros(N, np.float32); voice[:min(len(v), N)] = v[:N]
t = np.arange(N) / SR; rng = np.random.default_rng(11)
bpm = 88; beat = 60 / bpm; bar = 4 * beat
def hz(m): return 440 * 2 ** ((m - 69) / 12)
progA = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 48, 57, 60], [48, 55, 60, 64]]   # Dm Bb F C
progB = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [48, 55, 60, 64]]   # Am F G C
pad = np.zeros(N, np.float32); pl = np.zeros(N, np.float32); kick = np.zeros(N, np.float32); hat = np.zeros(N, np.float32)
nb = int(N / SR / bar) + 1
for b in range(nb):
    prog = progA if (b // 16) % 2 == 0 else progB; ch = prog[b % 4]
    s0 = int(b * bar * SR); s1 = min(N, int((b + 1) * bar * SR))
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR; env = np.minimum(1, tt / 0.5) * np.minimum(1, (bar - tt) / 0.5)
    for m in ch:
        f = hz(m); pad[s0:s1] += env * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt + 0.4)) / 4
    for k in range(8):
        ps = s0 + int(k * beat / 2 * SR)
        if ps >= N or (k % 2 and b % 2): continue
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12; L = min(int(0.45 * SR), N - ps); t2 = np.arange(L) / SR
        pl[ps:ps + L] += np.sin(2 * np.pi * hz(m) * t2) * np.exp(-t2 * 8) * 0.45
    for k in (0, 2):
        ps = s0 + int(k * beat * SR)
        if ps >= N: break
        L = min(int(0.3 * SR), N - ps); t2 = np.arange(L) / SR; f = 48 + 60 * np.exp(-t2 * 30)
        kick[ps:ps + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t2 * 12)
    for k in range(4):
        ps = s0 + int((k + 0.5) * beat * SR)
        if ps >= N: break
        L = min(int(0.05 * SR), N - ps); hat[ps:ps + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 90) * 0.15
hp = butter(2, 6000, "high", fs=SR, output="sos"); hat = sosfilt(hp, hat)
music = sosfilt(butter(2, 2200, "low", fs=SR, output="sos"), pad * 0.5 + pl * 0.3) + kick * 0.35 + hat
music /= np.abs(music).max()
envv = np.convolve(np.abs(voice), np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
music = music * (1 - 0.6 * np.clip(envv / 0.04, 0, 1)) * 0.13
music *= np.minimum(1, t / 0.4) * np.minimum(1, (t[-1] - t) / 1.5)
sfx = np.zeros(N, np.float32)
def whoosh(at, dur=0.4, g=0.12):
    s = int(max(0, at - dur * 0.7) * SR); L = min(int(dur * SR), N - s)
    if L <= 0: return
    n = rng.standard_normal(L).astype(np.float32); env = np.sin(np.pi * np.arange(L) / L) ** 2
    sfx[s:s + L] += sosfilt(butter(2, 300, "high", fs=SR, output="sos"), sosfilt(butter(2, 1600, "low", fs=SR, output="sos"), n)) * env * g * 3
prev = None
for s in TM["segments"]:
    if s["scene"] != prev and prev is not None: whoosh(s["start"])
    prev = s["scene"]
mix = voice + music + sfx; mix /= max(1.0, np.abs(mix).max() / 0.95)
wavfile.write(os.path.join(HERE, "mix.wav"), SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print("mix ok", round(N / SR, 1))
