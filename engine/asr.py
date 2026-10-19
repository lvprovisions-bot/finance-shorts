"""Tiny offline English ASR (Moonshine tiny, int8 ONNX from sherpa-onnx GitHub release) with onnxruntime.
transcribe(audio_float32_16k) -> text. Model dir: .tools/asr/sherpa-onnx-moonshine-tiny-en-int8 (setup.sh downloads it)."""
import os
import numpy as np, onnxruntime as ort
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, ".tools/asr/sherpa-onnx-moonshine-tiny-en-int8")
_s = {}
def _sess(n):
    if n not in _s:
        o = ort.SessionOptions(); o.intra_op_num_threads = 2
        _s[n] = ort.InferenceSession(os.path.join(MD, n), o)
    return _s[n]
_tok = None
def _tokens():
    global _tok
    if _tok is None:
        _tok = {}
        for line in open(os.path.join(MD, "tokens.txt"), encoding="utf-8"):
            p = line.rstrip("\n").rsplit("\t", 1)
            if len(p) == 2: _tok[int(p[1])] = p[0]
    return _tok
def _detok(ids):
    t = _tokens(); out = bytearray()
    for i in ids:
        s = t.get(i, "")
        if s.startswith("<0x") and s.endswith(">"): out += bytes([int(s[3:-1], 16)])
        elif s in ("<s>", "</s>", "<unk>"): continue
        else: out += s.replace("▁", " ").encode("utf-8")
    return out.decode("utf-8", "ignore").strip()
def transcribe(audio):
    audio = np.asarray(audio, np.float32)[None, :]
    feats = _sess("preprocess.onnx").run(None, {"args_0": audio})[0]
    enc = _sess("encode.int8.onnx").run(None, {"args_0": feats, "args_1": np.array([feats.shape[1]], np.int32)})[0]
    un = _sess("uncached_decode.int8.onnx"); ca = _sess("cached_decode.int8.onnx")
    out = un.run(None, {"args_0": np.array([[1]], np.int32), "args_1": enc, "args_2": np.array([1], np.int32)})
    logits, cache = out[0], out[1:]; ids = []
    maxlen = int(audio.shape[1] / 16000 * 7) + 10
    names = [i.name for i in ca.get_inputs()]
    for step in range(maxlen):
        nxt = int(np.argmax(logits[0, -1]))
        if nxt == 2: break
        ids.append(nxt)
        feed = {"args_0": np.array([[nxt]], np.int32), "args_1": enc, "args_2": np.array([step + 2], np.int32)}
        for n, c in zip(names[3:], cache): feed[n] = c
        out = ca.run(None, feed); logits, cache = out[0], out[1:]
    return _detok(ids)
if __name__ == "__main__":
    import sys
    from scipy.io import wavfile
    sr, a = wavfile.read(sys.argv[1]); a = a.astype(np.float32) / (32768 if a.dtype == np.int16 else 1)
    if a.ndim > 1: a = a.mean(1)
    if sr != 16000:
        from scipy.signal import resample_poly; a = resample_poly(a, 16000, sr)
    print(transcribe(a))
