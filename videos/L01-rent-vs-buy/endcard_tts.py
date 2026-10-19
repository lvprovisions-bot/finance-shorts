"""Append the end-card line to voice.wav + timings.json without regenerating everything."""
import json, os, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tts
TEXT = "Want money maths in under a minute? Watch our Shorts, there's a new one every day. And subscribe to Finance Advised."
HOLD = 7.0
tm = json.load(open(os.path.join(HERE, "timings.json")))
assert tm["segments"][-1]["id"] != "e1", "already appended"
sr, v = wavfile.read(os.path.join(HERE, "voice.wav")); v = v.astype(np.float32) / 32767
a = tts.trim(tts.synth(tts.phonemize(tts.spoken(TEXT))));
a = a / max(1e-6, np.abs(a).max()) * np.abs(v).max()
t0 = len(v) / sr; dur = len(a) / sr
toks = tts.tokens(TEXT); ws = [max(2, len(tts.phonemize(sp).replace(" ", ""))) for _, sp in toks]; W = sum(ws); cur = t0; tk = []
for (cap, _), k in zip(toks, ws):
    d = dur * k / W; tk.append({"text": cap, "start": round(cur, 3), "end": round(cur + d, 3)}); cur += d
tm["segments"].append({"id": "e1", "scene": "endcard", "start": round(t0, 3), "end": round(t0 + dur, 3), "tokens": tk})
out = np.concatenate([v, a, np.zeros(int(HOLD * sr), np.float32)])
tm["total"] = len(out) / sr
wavfile.write(os.path.join(HERE, "voice.wav"), sr, (out * 32767).astype(np.int16))
json.dump(tm, open(os.path.join(HERE, "timings.json"), "w"), indent=1)
print("appended", round(dur, 2), "total", round(tm["total"], 2))
