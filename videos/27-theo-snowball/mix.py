"""THEO EXPLAINS #10 mix: voice + winter music-box bed (Ebmaj7-Cm7-Abmaj7-Bb7sus, 92 bpm) + snow-roll/chime SFX into mix.wav (48 kHz stereo)."""
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

# ---- music: Fmaj7 - Dm7 - Gm7 - C7, 102 bpm, elevator-bossa: soft pad, syncopated keys, rim tick, bass ----
bpm = 92; beat = 60 / bpm; bar = 4 * beat
def hz(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[51, 55, 58, 62], [48, 51, 55, 58], [56, 60, 63, 67], [46, 51, 53, 56]]
roots = [39, 36, 44, 34]
pad = np.zeros(N, np.float32); keys = np.zeros(N, np.float32); bass = np.zeros(N, np.float32); rim = np.zeros(N, np.float32)
nbars = int(N / SR / bar) + 1
for b in range(nbars):
    ch = chords[b % 4]; s0 = int(b * bar * SR); s1 = min(N, int((b + 1) * bar * SR))
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.3)
    for m in ch:
        pad[s0:s1] += env * np.sin(2 * np.pi * hz(m) * tt) / 4
    for k in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):       # music-box arpeggio
        ps = s0 + int(k * beat * SR)
        if ps >= N: continue
        L = min(int(0.45 * SR), N - ps); t2 = np.arange(L) / SR
        m = ch[int(k * 2) % 4] + (24 if int(k * 2) % 8 >= 4 else 12)
        f = hz(m)
        keys[ps:ps + L] += (np.sin(2 * np.pi * f * t2) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t2)) * np.exp(-t2 * 6) * 0.6
    for k, off in ((0, 0), (2, 7)):                    # soft half-note bass
        ps = s0 + int(k * beat * SR)
        if ps >= N: continue
        L = min(int(0.4 * SR), N - ps); t2 = np.arange(L) / SR
        bass[ps:ps + L] += np.sin(2 * np.pi * hz(roots[b % 4] + off) * t2) * np.exp(-t2 * 5)
    for k in (1, 3):                               # brush on 2 and 4
        ps = s0 + int(k * beat * SR)
        if ps >= N: continue
        L = min(int(0.03 * SR), N - ps)
        rim[ps:ps + L] += 0.6 * rng.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / SR * 200)
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
def ding(at, f0=1320, g=0.16):                     # elevator arrival bell
    s = int(at * SR); L = min(int(0.9 * SR), N - s); tt = np.arange(L) / SR
    sfx[s:s + L] += (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2.76 * tt)) * np.exp(-tt * 5) * g
def chime(at, f0=1318, g=0.13):                   # sleigh-bell style chime
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

for s in TM["segments"][1:]:
    whoosh(s["start"])
seg = {s["scene"]: s for s in TM["segments"]}
tk = lambda sc, i: seg[sc]["tokens"][i]["start"]
boom(0.05, 0.25)
roll(tk("hook", 3), 2.2, 0.06)                                  # Theo's ball rolls (simple)
pop(tk("hook", 5), 900, 0.18)
slide(tk("no", 2) - 0.1, 300, 700, dur=0.6, g=0.08); chime(tk("no", 2) + 0.35)
slide(seg["y1"]["start"], 600, 250, dur=0.45, g=0.06); pop(tk("y1", 2), 1200, 0.2)
roll(tk("y30", 0), 1.4, 0.09); chime(tk("y30", 3), 1568); pop(tk("y30", 4), 900, 0.18)
pop(tk("why", 2), 1000, 0.2); chime(tk("why", 5), 1760, 0.12)
pop(tk("punch", 2), 1300); boom(tk("punch", 4) + 0.3, 0.35)
pop(seg["fix"]["start"], 800); pop(seg["fix"]["start"] + 0.25, 900); pop(seg["fix"]["start"] + 0.5, 1000)
pop(seg["q"]["start"], 1200); pop(seg["q"]["start"] + 0.15, 1500)
mix = voice * 1.0 + music + sfx
mix /= max(1.0, np.abs(mix).max() / 0.95)
st = np.stack([mix, mix], 1)
wavfile.write(os.path.join(HERE, "mix.wav"), SR, (st * 32767).astype(np.int16))
print("mix ok", round(N / SR, 2))
