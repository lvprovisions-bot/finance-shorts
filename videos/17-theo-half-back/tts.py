"""Synthesize the script with Kokoro (ONNX) + espeak-ng phonemes.
Writes voice.wav (24 kHz) and timings.json (per caption token start/end)."""
import json, re, subprocess, sys, os
import numpy as np, onnxruntime as ort
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script import SEGMENTS, VOICES, SPEED

T = os.path.join(os.path.dirname(os.path.dirname(HERE)), ".tools")  # built by setup.sh
ESPEAK = os.path.join(T, "espeak/bin/espeak-ng")
VOCAB = json.load(open(os.path.join(T, "kokoro-onnx/src/kokoro_onnx/config.json")))["vocab"]
SR = 24000
sess = ort.InferenceSession(os.path.join(T, "kokoro-v1.0.int8.onnx"))
voices = np.load(os.path.join(T, "voices-v1.0.bin"))
env = dict(os.environ, ESPEAK_DATA_PATH=os.path.join(T, "espeak/share/espeak-ng-data"))


def ipa(text):
    out = subprocess.run([ESPEAK, "-q", "--ipa", "-v", "en-us", text],
                         capture_output=True, text=True, env=env).stdout
    return " ".join(out.split())


def phonemize(text):
    # keep punctuation like phonemizer(preserve_punctuation=True)
    parts = re.split(r"([,.?!;:]+|\.\.\.)", text)
    res = ""
    for p in parts:
        if not p.strip():
            continue
        if re.fullmatch(r"[,.?!;:.]+", p.strip()):
            res = res.rstrip() + p.strip()[-1] + " "
        else:
            res += ipa(p) + " "
    return "".join(c for c in res.strip() if c in VOCAB)


def synth(phon, voice):
    ids = [VOCAB[c] for c in phon]
    style = voices[voice][len(ids)]
    audio = sess.run(None, {"tokens": np.array([[0, *ids, 0]], dtype=np.int64),
                            "style": style.astype(np.float32),
                            "speed": np.array([SPEED], dtype=np.float32)})[0]
    return audio.reshape(-1)


def trim(a, thr=0.008):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(0.02 * SR)); e = min(len(a), idx[-1] + int(0.05 * SR))
    return a[s:e]


chunks, timings, t = [], [], 0.05
chunks.append(np.zeros(int(0.05 * SR), np.float32))
for scene, spk, toks, pause in SEGMENTS:
    text = " ".join(sp for _, sp in toks)
    phon = phonemize(text)
    a = trim(synth(phon, VOICES[spk]))
    dur = len(a) / SR
    # distribute token times by phoneme length (+ weight for trailing punctuation)
    weights = []
    for _, sp in toks:
        p = phonemize(sp)
        w = len(p.replace(" ", "")) + (3 if re.search(r"[.?!]$", sp) else 1 if sp.endswith(",") else 0)
        weights.append(max(w, 2))
    W = sum(weights); cur = t
    seg = {"scene": scene, "spk": spk, "start": t, "end": t + dur, "tokens": []}
    for (cap, sp), w in zip(toks, weights):
        d = dur * w / W
        seg["tokens"].append({"text": cap, "start": round(cur, 3), "end": round(cur + d, 3)})
        cur += d
    timings.append(seg)
    chunks.append(a); chunks.append(np.zeros(int(pause * SR), np.float32))
    t += dur + pause
    print(f"{scene:7s} {dur:5.2f}s  {phon[:70]}")

audio = np.concatenate(chunks)
audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
wavfile.write(os.path.join(HERE, "voice.wav"), SR, (audio * 32767).astype(np.int16))
json.dump({"total": len(audio) / SR, "segments": timings}, open(os.path.join(HERE, "timings.json"), "w"), indent=1)
print("TOTAL", round(len(audio) / SR, 2), "s")
