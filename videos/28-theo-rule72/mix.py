"""THEO EXPLAINS #11 mix: voice + station shuffle bed (Cmaj7-Am7-Dm7-G7, 112 bpm, train-chug shaker) + flap clatter / whistle / rail clack SFX into mix.wav (48 kHz stereo)."""
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
rng = np.random.default_rng(27)

# ---- music: Cmaj7 - Am7 - Dm7 - G7, 112 bpm: soft pad, plucked keys, walking bass, 16th shaker chug ----
bpm = 112; beat = 60 / bpm; bar = 4 * beat
def hz(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[48, 52, 55, 59], [45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 53]]
roots = [36, 33, 38, 31]
pad = np.zeros(N, np.float32); keys = np.zeros(N, np.float32); bass = np.zeros(N, np.float32); rim = np.zeros(N, np.float32)
nbars = int(N / SR / bar) + 1
for b in range(nbars):
    ch = chords[b % 4]; s0 = int(b * bar * SR); s1 = min(N, int((b + 1) * bar * SR))
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.3)
    for m in ch:
        pad[s0:s1] += env * np.sin(2 * np.pi * hz(m) * tt) / 4
    for k in (0, 0.75, 1.5, 2, 2.75, 3.5):          # syncopated plucks
        ps = s0 + int(k * beat * SR)
        if ps >= N: continue
        L = min(int(0.45 * SR), N - ps); t2 = np.arange(L) / SR
        m = ch[int(k * 4) % 4] + 12
        f = hz(m)
        keys[ps:ps + L] += (np.sin(2 * np.pi * f * t2) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t2)) * np.exp(-t2 * 9) * 0.55
    for k, off in ((0, 0), (1, 4), (2, 7), (3, 9)):     # walking bass
        ps = s0 + int(k * beat * SR)
        if ps >= N: continue
        L = min(int(0.4 * SR), N - ps); t2 = np.arange(L) / SR
        bass[ps:ps + L] += np.sin(2 * np.pi * hz(roots[b % 4] + off) * t2) * np.exp(-t2 * 5)
    for k in [i / 4 for i in range(16)]:          # train-chug shaker (accent on beats)
        ps = s0 + int(k * beat * SR)
        if ps >= N: continue
        L = min(int(0.03 * SR), N - ps)
        rim[ps:ps + L] += (0.6 if k % 1 == 0 else 0.3) * rng.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / SR * 200)
sos = butter(2, 2800, "low", fs=SR, output="sos")
music = sosfilt(sos, pad * 0.45 + keys * 0.4) + bass * 0.35 + rim * 0.12
music /= np.abs(music).max()

envv = np.abs(voice)
k = int(0.15 * SR); envv = np.convolve(envv, np.ones(k) / k, mode="same")
duck = 1 - 0.55 * np.clip(envv / 0.05, 0, 1)
music = music * duck * 0.16
music *= np.minimum(1, t / 0.3) * np.minimum(1, (t[-1] - t) / 0.25)

# ---- sfx ----
sfx = np.zeros(N, np.float32)
def whoosh(at, dur=0.35, g=0.12):
    s = int(max(0, at - dur * 0.7) * SR); L = min(int(dur * SR), N - s)
    n = rng.standard_normal(L).astype(np.float32); tt = np.arange(L) / L
    lo = butter(2, 1800, "low", fs=SR, output="sos"); hi = butter(2, 300, "high", fs=SR, output="sos")
    sfx[s:s + L] += sosfilt(hi, sosfilt(lo, n)) * np.sin(np.pi * tt) ** 2 * g * 3
def pop(at, f0=900, g=0.22):
    s = int(at * SR); L = min(int(0.12 * SR), N - s); tt = np.arange(L) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt * 40))
    sfx[s:s + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 35) * g
def boom(at, g=0.5):
    s = int(at * SR); L = min(int(0.6 * SR), N - s); tt = np.arange(L) / SR
    f = 40 + 90 * np.exp(-tt * 18)
    sfx[s:s + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6) * g
def ding(at, f0=1320, g=0.16):                     # station bell
    s = int(at * SR); L = min(int(0.9 * SR), N - s); tt = np.arange(L) / SR
    sfx[s:s + L] += (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2.76 * tt)) * np.exp(-tt * 5) * g
def chime(at, f0=1318, g=0.13):                   # arrival chime
    for j, ff in enumerate((f0, f0 * 1.26, f0 * 1.5)):
        ding(at + j * 0.06, ff, g * 0.7)
def roll(at, dur, g):                               # crunchy snow roll
    s = int(at * SR); L = min(int(dur * SR), N - s)
    if L <= 0: return
    n = rng.standard_normal(L).astype(np.float32); tt = np.arange(L) / SR
    lo = butter(2, 900, "low", fs=SR, output="sos")
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt)
    sfx[s:s + L] += sosfilt(lo, n) * am * np.minimum(1, tt / 0.1) * np.minimum(1, (dur - tt) / 0.3) * g * 3
def slide(at, f0, f1, dur=1.0, g=0.07):            # motor rising/falling
    st = int(at * SR); L = min(int(dur * SR), N - st); tt = np.arange(L) / SR
    f = f0 + (f1 - f0) * (tt / dur)
    sfx[st:st + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * g * np.minimum(1, tt / 0.05) * np.minimum(1, (dur - tt) / 0.2)

def whistle(at, g=0.07):                            # two-tone train whistle
    st = int(at * SR); L = min(int(0.7 * SR), N - st); tt = np.arange(L) / SR
    env = np.minimum(1, tt / 0.05) * np.minimum(1, (0.7 - tt) / 0.2)
    sfx[st:st + L] += (np.sin(2 * np.pi * 587 * tt) + np.sin(2 * np.pi * 740 * tt) + 0.4 * np.sin(2 * np.pi * 880 * tt)) * env * g
def clatter(at, n=8, g=0.08):                       # split-flap board clatter
    for j in range(n):
        st = int((at + j * 0.035) * SR); L = min(int(0.02 * SR), N - st)
        if L <= 0: continue
        sfx[st:st + L] += rng.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / SR * 300) * g * 3
def clack(at, dur, g=0.12):                         # rail clack while the train moves
    k = 0.0
    while k < dur:
        pop(at + k, 180, g); k += 0.18

for s in TM["segments"][1:]:
    whoosh(s["start"]); clatter(s["start"] + 0.05)
seg = {s["scene"]: s for s in TM["segments"]}
tk = lambda sc, i: seg[sc]["tokens"][i]["start"]
boom(0.05, 0.25); clatter(0.05, 10)
whistle(tk("hook", 4))
pop(tk("no", 2), 900, 0.18); ding(tk("no", 3), 1320, 0.12)
clack(tk("no", 6), 0.7); ding(tk("no", 6) + 0.7, 1568, 0.12)
clack(tk("ladder", 2) - 0.1, 0.5); ding(tk("ladder", 2) + 0.4, 1568, 0.1)
clack(tk("ladder", 4) - 0.1, 0.5); ding(tk("ladder", 4) + 0.4, 1760, 0.1)
clack(tk("big", 1) - 0.1, 1.4, 0.14); whistle(tk("big", 3), 0.06); chime(tk("big", 3) + 0.1, 1568)
pop(tk("punch", 2), 1300); boom(tk("punch", 5) + 0.15, 0.35)
pop(seg["fix"]["start"] + 0.1, 800); ding(tk("fix", 2), 1320, 0.1)
pop(seg["q"]["start"], 1200); pop(tk("q", 4), 1500)
whistle(seg["loop"]["start"] + 0.1, 0.05)
mix = voice * 1.0 + music + sfx
mix /= max(1.0, np.abs(mix).max() / 0.95)
st = np.stack([mix, mix], 1)
wavfile.write(os.path.join(HERE, "mix.wav"), SR, (st * 32767).astype(np.int16))
print("mix ok", round(N / SR, 2))
