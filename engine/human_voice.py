"""Turn the owner's raw narration into voice.wav + timings.json (same format as tts.py), so render.py/mix.py work unchanged.

usage: python3 engine/human_voice.py <recording(any format)> <video_folder>
  - cleans audio with ffmpeg (high-pass, denoise, de-ess, gentle compression, loudness)
  - splits on pauses, transcribes each chunk offline (engine/asr.py), and matches chunks to the script's paragraphs
    (script.py SEGMENTS, in order). Retakes: when a paragraph was read more than once, the LAST good take is kept.
  - word timings: spread over the voiced parts of each paragraph by phoneme length (same method as tts.py)
  - writes voice.wav (24 kHz), timings.json, and voice_report.json (per-paragraph match score + transcript)
  - exits with code 3 and lists paragraph numbers if any paragraph is missing / unclear (score < MIN_SCORE)
The end-card segment (scene 'endcard') gets no narration: captions only, over music."""
import json, os, re, subprocess, sys, difflib
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import asr  # noqa: E402

SR = 24000
MIN_SCORE = 0.45
# note: ffmpeg deesser after highpass produced NaNs in testing -> use a gentle static EQ dip on sibilance instead
CLEAN = ("highpass=f=75,lowpass=f=12000,afftdn=nf=-28:tn=1,equalizer=f=6500:t=q:w=1.4:g=-4,"
         "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200:makeup=2,loudnorm=I=-16:TP=-2:LRA=9")

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def num_words(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + num_words(n % 100))
    for div, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")):
        if n >= div: return num_words(n // div) + " " + name + ("" if n % div == 0 else " " + num_words(n % div))
def norm(text):
    t = text.lower().replace("%", " percent ").replace("$", " ").replace("-", " ")
    t = re.sub(r"(\d),(\d)", r"\1\2", t)
    t = re.sub(r"(\d+)\.(\d+)", lambda m: num_words(m.group(1)) + " point " + " ".join(ONES[int(c)] for c in m.group(2)), t)
    t = re.sub(r"\d+", lambda m: " " + num_words(m.group(0)) + " ", t)
    t = re.sub(r"[^a-z' ]", " ", t)
    words = [w for w in t.split() if w not in ("and", "a", "the", "dollars", "dollar", "uh", "um")]
    return words
def sim(a, b):
    if not a or not b: return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()

def load_any(path):
    """-> (clean float32 @24k, raw float32 @16k)"""
    def ff(af, sr):
        cmd = ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr)] + (["-af", af] if af else []) + ["-f", "f32le", "-"]
        return np.nan_to_num(np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy())
    return ff(CLEAN, SR), ff(None, 16000)

def voiced_mask(a, sr, hop=0.02):
    n = int(sr * hop); fr = len(a) // n
    e = np.sqrt((a[:fr * n].reshape(fr, n) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(e)
    floor = np.percentile(db, 10); peak = np.percentile(db, 95)
    thr = floor + max(6, (peak - floor) * 0.30)
    m = db > thr
    # close tiny gaps (<120 ms) and drop blips (<80 ms)
    k = int(0.12 / hop)
    idx = np.where(m)[0]
    for i0, i1 in zip(idx[:-1], idx[1:]):
        if 1 < i1 - i0 <= k: m[i0:i1] = True
    out = m.copy(); i = 0
    while i < len(m):
        if m[i]:
            j = i
            while j < len(m) and m[j]: j += 1
            if j - i < int(0.08 / hop): out[i:j] = False
            i = j
        else: i += 1
    return out, hop

def chunks_from(mask, hop, min_gap=0.42):
    segs = []; i = 0; n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while True:
                while j < n and mask[j]: j += 1
                g = j
                while g < n and not mask[g]: g += 1
                if g < n and (g - j) * hop < min_gap: j = g; continue
                break
            segs.append([i * hop, j * hop]); i = j
        else: i += 1
    return [s for s in segs if s[1] - s[0] > 0.25]

def match(paras, chunk_words, max_span=5):
    """DP: assign each paragraph a span of consecutive chunks, in order; chunks may be skipped (retakes/false starts).
    Ties prefer later spans (= last take)."""
    P, C = len(paras), len(chunk_words)
    NEG = -1e9
    best = np.full((P + 1, C + 2), NEG); choice = {}
    best[P, :] = 0.0
    for i in range(P - 1, -1, -1):
        for j in range(C, -1, -1):
            # option: skip chunk j (small penalty)
            cand = (best[i, j + 1] - 0.03, None) if j < C else (NEG, None)
            for a in [j]:
                for b in range(a, min(C, a + max_span)):
                    words = sum((chunk_words[k] for k in range(a, b + 1)), [])
                    s = sim(paras[i], words)
                    v = s + best[i + 1, b + 1]
                    if v > cand[0] + 1e-9: cand = (v, (a, b, s))
            best[i, j] = cand[0]; choice[(i, j)] = cand[1]
    # walk
    out = []; i = j = 0
    while i < P:
        c = choice.get((i, j))
        if c is None:
            if j >= C: out.append(None); i += 1; continue
            j += 1; continue
        # prefer a later take of the same paragraph if it scores at least as well
        a, b, s = c
        out.append((a, b, s)); i += 1; j = b + 1
    return out

def main(rec, folder):
    sys.path.insert(0, folder)
    from script import SEGMENTS
    import tts as T  # the video's tts.py (phonemizer + tokens())
    clean24, raw16 = load_any(rec)
    mask, hop = voiced_mask(raw16, 16000)
    chunks = chunks_from(mask, hop)
    print(f"{len(chunks)} spoken chunks in {len(raw16) / 16000:.1f}s of audio", flush=True)
    chunk_txt = []
    for k, (s, e) in enumerate(chunks):
        a = raw16[int(max(0, s - 0.15) * 16000):int((e + 0.15) * 16000)]
        txt = asr.transcribe(a) if e - s < 28 else " ".join(asr.transcribe(a[i:i + 16000 * 25]) for i in range(0, len(a), 16000 * 25))
        chunk_txt.append(txt); print(f"  chunk {k:3d} {s:7.2f}-{e:7.2f}  {txt[:80]}", flush=True)
    segs = [s for s in SEGMENTS if s["scene"] != "endcard"]
    paras = [norm(T.spoken(s["text"])) for s in segs]
    assign = match(paras, [norm(t) for t in chunk_txt])
    # -------- re-run matching preferring last takes: for each paragraph, look for a later chunk span (before next para) scoring >= s-0.05
    final = []
    for i, c in enumerate(assign):
        if c is None: final.append(None); continue
        a, b, s = c
        nxt = next((x[0] for x in assign[i + 1:] if x), len(chunks))
        best = c
        for a2 in range(b + 1, nxt):
            for b2 in range(a2, min(nxt, a2 + 5)):
                s2 = sim(paras[i], sum((norm(chunk_txt[k]) for k in range(a2, b2 + 1)), []))
                if s2 >= s - 0.05 and s2 >= MIN_SCORE: best = (a2, b2, s2)
        final.append(best)
    report = []; bad = []
    for i, (sg, c) in enumerate(zip(segs, final)):
        sc = c[2] if c else 0.0
        report.append({"n": i + 1, "id": sg["id"], "score": round(sc, 2), "chunks": c[:2] if c else None,
                       "heard": " / ".join(chunk_txt[k] for k in range(c[0], c[1] + 1)) if c else ""})
        if sc < MIN_SCORE: bad.append(i + 1)
    json.dump(report, open(os.path.join(folder, "voice_report.json"), "w"), indent=1)
    if bad:
        print("UNCLEAR/MISSING PARAGRAPHS:", bad); sys.exit(3)
    # -------- assemble voice.wav + timings
    out = [np.zeros(int(0.15 * SR), np.float32)]; t = 0.15; timings = []
    for sg, (a, b, sc) in zip(segs, final):
        s0, e0 = chunks[a][0] - 0.06, chunks[b][1] + 0.12
        piece = clean24[int(s0 * SR):int(e0 * SR)].copy()
        # shorten long internal silences to 0.45 s
        pm, ph = voiced_mask(resample_poly(piece, 16000, SR), 16000)
        keep = np.ones(len(piece), bool); i = 0
        while i < len(pm):
            if not pm[i]:
                j = i
                while j < len(pm) and not pm[j]: j += 1
                if (j - i) * ph > 0.6 and i > 0 and j < len(pm):
                    cut0 = int((i * ph + 0.22) * SR); cut1 = int((j * ph - 0.22) * SR); keep[cut0:cut1] = False
                i = j
            else: i += 1
        piece = piece[keep]
        fade = int(0.01 * SR); piece[:fade] *= np.linspace(0, 1, fade); piece[-fade:] *= np.linspace(1, 0, fade)
        dur = len(piece) / SR
        # voiced timeline inside the piece -> map word weights onto voiced time only
        vm, vh = voiced_mask(resample_poly(piece, 16000, SR), 16000)
        vt = np.where(vm)[0] * vh
        if len(vt) < 5: vt = np.linspace(0, dur, 50)
        toks = T.tokens(sg["text"])
        ws = [max(2, len(T.phonemize(sp).replace(" ", ""))) for _, sp in toks]
        cw = np.concatenate([[0], np.cumsum(ws)]) / sum(ws)
        def at(f): return float(vt[min(len(vt) - 1, int(f * (len(vt) - 1)))])
        tk = [{"text": cap, "start": round(t + at(cw[k]), 3), "end": round(t + at(cw[k + 1]) + vh, 3)} for k, (cap, _) in enumerate(toks)]
        timings.append({"id": sg["id"], "scene": sg["scene"], "start": round(t, 3), "end": round(t + dur, 3), "tokens": tk})
        out += [piece, np.zeros(int(sg["pause"] * SR), np.float32)]; t += dur + sg["pause"]
    for sg in SEGMENTS:
        if sg["scene"] == "endcard":
            toks = T.tokens(sg["text"]); d = 5.0 / len(toks)
            timings.append({"id": sg["id"], "scene": "endcard", "start": round(t, 3), "end": round(t + 5.0, 3),
                            "tokens": [{"text": c, "start": round(t + k * d, 3), "end": round(t + (k + 1) * d, 3)} for k, (c, _) in enumerate(toks)]})
            out.append(np.zeros(int((5.0 + sg["pause"]) * SR), np.float32)); t += 5.0 + sg["pause"]
    audio = np.concatenate(out); audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
    wavfile.write(os.path.join(folder, "voice.wav"), SR, (audio * 32767).astype(np.int16))
    json.dump({"total": len(audio) / SR, "segments": timings, "narrator": "owner"}, open(os.path.join(folder, "timings.json"), "w"), indent=1)
    print("OK total %.1fs, lowest paragraph score %.2f" % (len(audio) / SR, min(r["score"] for r in report)))

if __name__ == "__main__":
    main(sys.argv[1], os.path.abspath(sys.argv[2]))
