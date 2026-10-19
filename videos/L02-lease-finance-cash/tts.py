"""Kokoro TTS for long-form. Supports {CAPTION|spoken} tokens. Writes voice.wav + timings.json."""
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
    ids = [VOCAB[c] for c in phon]; assert len(ids) < 505, (len(ids), phon[:60])
    a = sess.run(None, {"tokens": np.array([[0, *ids, 0]], dtype=np.int64), "style": voices[VOICE][len(ids)].astype(np.float32),
                        "speed": np.array([SPEED], dtype=np.float32)})[0]
    return a.reshape(-1)
def trim(a, thr=0.008):
    idx = np.where(np.abs(a) > thr)[0]
    return a if len(idx) == 0 else a[max(0, idx[0] - int(0.02 * SR)):min(len(a), idx[-1] + int(0.06 * SR))]
def tokens(text):
    """-> list of (caption, spoken)."""
    out = []
    for m in re.finditer(r"\{([^|}]*)\|([^}]*)\}([.,?!:;]*)|(\S+)", text):
        if m.group(4): out.append((m.group(4), m.group(4)))
        else: out.append((m.group(1) + m.group(3), m.group(2) + m.group(3)))
    return out
def spoken(text): return " ".join(sp for _, sp in tokens(text))
if __name__ == "__main__":
    chunks = [np.zeros(int(0.12 * SR), np.float32)]; t = 0.12; out = []
    for s in SEGMENTS:
        toks = tokens(s["text"]); phon = phonemize(spoken(s["text"])); a = trim(synth(phon)); dur = len(a) / SR
        ws = [max(2, len(phonemize(sp).replace(" ", "")) + (3 if re.search(r"[.?!]$", sp) else 1 if re.search(r"[,:;]$", sp) else 0)) for _, sp in toks]
        W = sum(ws); cur = t; tk = []
        for (cap, _), k in zip(toks, ws):
            d = dur * k / W; tk.append({"text": cap, "start": round(cur, 3), "end": round(cur + d, 3)}); cur += d
        out.append({"id": s["id"], "scene": s["scene"], "start": round(t, 3), "end": round(t + dur, 3), "tokens": tk})
        chunks += [a, np.zeros(int(s["pause"] * SR), np.float32)]; t += dur + s["pause"]
        print(f'{s["id"]:4s} {dur:5.2f}s {len(phon)}', flush=True)
    audio = np.concatenate(chunks); audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
    wavfile.write(os.path.join(HERE, "voice.wav"), SR, (audio * 32767).astype(np.int16))
    json.dump({"total": len(audio) / SR, "segments": out}, open(os.path.join(HERE, "timings.json"), "w"), indent=1)
    print("TOTAL", round(len(audio) / SR, 2))
