"""Kokoro TTS for long-form: per-segment synth, per-word timings. Writes voice.wav + timings.json."""
import json, re, subprocess, sys, os
import numpy as np, onnxruntime as ort
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import SEGMENTS, VOICE, SPEED, LANG
T = os.path.join(os.path.dirname(os.path.dirname(HERE)), ".tools")
ESPEAK = os.path.join(T, "espeak/bin/espeak-ng")
VOCAB = json.load(open(os.path.join(T, "kokoro-onnx/src/kokoro_onnx/config.json")))["vocab"]
SR = 24000
sess = ort.InferenceSession(os.path.join(T, "kokoro-v1.0.int8.onnx"))
voices = np.load(os.path.join(T, "voices-v1.0.bin"))
env = dict(os.environ, ESPEAK_DATA_PATH=os.path.join(T, "espeak/share/espeak-ng-data"))
def ipa(text):
    out = subprocess.run([ESPEAK, "-q", "--ipa", "-v", LANG, text], capture_output=True, text=True, env=env).stdout
    return " ".join(out.split())
def phonemize(text):
    parts = re.split(r"([,.?!;:]+)", text); res = ""
    for p in parts:
        if not p.strip(): continue
        if re.fullmatch(r"[,.?!;:]+", p.strip()): res = res.rstrip() + p.strip()[-1] + " "
        else: res += ipa(p) + " "
    return "".join(c for c in res.strip() if c in VOCAB)
def synth(phon):
    ids = [VOCAB[c] for c in phon]; assert len(ids) < 500, len(ids)
    style = voices[VOICE][len(ids)]
    a = sess.run(None, {"tokens": np.array([[0, *ids, 0]], dtype=np.int64), "style": style.astype(np.float32),
                        "speed": np.array([SPEED], dtype=np.float32)})[0]
    return a.reshape(-1)
def trim(a, thr=0.008):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(0.02 * SR)):min(len(a), idx[-1] + int(0.06 * SR))]
chunks = [np.zeros(int(0.15 * SR), np.float32)]; t = 0.15; out = []
for s in SEGMENTS:
    phon = phonemize(s["text"]); a = trim(synth(phon)); dur = len(a) / SR
    words = s["text"].split()
    ws = [max(2, len(phonemize(w).replace(" ", "")) + (3 if re.search(r"[.?!]$", w) else 1 if w.endswith(",") or w.endswith(":") else 0)) for w in words]
    W = sum(ws); cur = t; toks = []
    for w, k in zip(words, ws):
        d = dur * k / W; toks.append({"text": w, "start": round(cur, 3), "end": round(cur + d, 3)}); cur += d
    out.append({"id": s["id"], "scene": s["scene"], "start": round(t, 3), "end": round(t + dur, 3), "tokens": toks})
    chunks += [a, np.zeros(int(s["pause"] * SR), np.float32)]; t += dur + s["pause"]
    print(f'{s["id"]:4s} {dur:5.2f}s', flush=True)
audio = np.concatenate(chunks); audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
wavfile.write(os.path.join(HERE, "voice.wav"), SR, (audio * 32767).astype(np.int16))
json.dump({"total": len(audio) / SR, "segments": out}, open(os.path.join(HERE, "timings.json"), "w"), indent=1)
print("TOTAL", round(len(audio) / SR, 2))
