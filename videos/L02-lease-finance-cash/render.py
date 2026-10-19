"""Render L02 lease-vs-finance-vs-cash long-form: 1920x1080 @30fps, frames piped to ffmpeg.
python3 render.py            -> video_noaudio.mp4
python3 render.py 1.0 20.5   -> prev_*.png at those times
python3 render.py --sweep N  -> render every Nth frame without encoding (exception check)"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import SEGMENTS
from model import run as model_run, P as MP

W, H, FPS = 1920, 1080, 30
TM = json.load(open(os.environ.get("TIMINGS", os.path.join(HERE, "timings.json"))))
TOTAL = TM["total"] + 0.5
NF = int(TOTAL * FPS)

F_CAP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_BLK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_BLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_MED = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
_fc = {}
def font(path, size):
    k = (path, max(2, int(round(size))))
    if k not in _fc: _fc[k] = ImageFont.truetype(path, k[1])
    return _fc[k]

BG = (10, 14, 26); PANEL = (22, 28, 46); PANEL2 = (32, 40, 62); LINE = (60, 70, 96)
WHITE = (255, 255, 255); YEL = (255, 216, 77); GREEN = (52, 211, 120); RED = (255, 92, 92)
GREY = (150, 160, 178); DIMT = (110, 120, 140)
NORA = (255, 140, 82); THEO = (70, 196, 230); SKIN = (255, 214, 180); SKIN2 = (196, 140, 100)

def clamp(x): return min(max(x, 0.0), 1.0)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))
def money(v): return "${:,.0f}".format(v)
def kfmt(v): return "${:,.0f}K".format(v / 1000) if v < 1e6 else "${:.2f}M".format(v / 1e6)

# ---------------- runs (consecutive segments of one scene) ----------------
SHOW = {s["id"]: s for s in SEGMENTS}
SEGS = TM["segments"]
for s in SEGS: s["show"] = SHOW[s["id"]]["show"]
RUNS = []
for s in SEGS:
    md = s["show"].get("mode")
    if RUNS and RUNS[-1]["scene"] == s["scene"] and not (md and md != RUNS[-1]["mode"]) and not s["show"].get("n") and not (s["scene"] == "pc"):
        RUNS[-1]["segs"].append(s)
    elif RUNS and RUNS[-1]["scene"] == s["scene"] == "twist" and s["show"].get("n") == RUNS[-1]["show"].get("n"):
        RUNS[-1]["segs"].append(s)
    else:
        RUNS.append({"scene": s["scene"], "segs": [s], "start": s["start"], "mode": md or (RUNS[-1]["mode"] if RUNS and RUNS[-1]["scene"] == s["scene"] else None), "show": dict(s["show"])})
for r in RUNS:
    r["reveal"] = {}; merged = {}
    for s in r["segs"]:
        merged.update(s["show"]); st = s["show"].get("st", 0)
        for k in range(0, st + 1):
            r["reveal"].setdefault(k, s["start"])
    r["show"] = merged; r["end"] = r["segs"][-1]["end"]
CHAPS = []
for s in SEGS:
    c = s["show"].get("chap")
    if c and (not CHAPS or CHAPS[-1][1] != c): CHAPS.append((s["start"], c))

def run_at(t):
    cur = RUNS[0]
    for r in RUNS:
        if t >= r["start"] - 0.05: cur = r
    return cur
def seg_at(t):
    cur = SEGS[0]
    for s in SEGS:
        if t >= s["start"] - 0.05: cur = s
    return cur
def chapter_at(t):
    cur = None
    for st, c in CHAPS:
        if t >= st - 0.05: cur = c
    return cur

class Ctx:
    def __init__(self, img, t, run):
        self.img = img; self.d = ImageDraw.Draw(img); self.t = t; self.run = run
    def rv(self, k):  # reveal progress (seconds since stage k began, or -1)
        s = self.run["reveal"].get(k)
        return -1 if s is None or self.t < s - 0.05 else self.t - s + 0.05
    def since(self): return self.t - self.run["start"]
    def seg(self, sid):
        for s in self.run["segs"]:
            if s["id"] == sid: return s
    def cur(self): return seg_at(self.t)

# ---------------- drawing helpers ----------------
def text(d, xy, s, f, fill, anchor="mm", stroke=0, sfill=(0, 0, 0)):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)
def ptext(c, xy, s, path, size, fill, k=1.0, anchor="mm", stroke=0):
    """text that pops in with scale k (0..~1.1)."""
    if k <= 0.02 or size * k < 3: return
    text(c.d, xy, s, font(path, size * k), fill, anchor, stroke)
def rrect(d, box, r, fill=None, outline=None, width=0):
    x0, y0, x1, y1 = box
    if x1 - x0 < 2 or y1 - y0 < 2: return
    d.rounded_rectangle([x0, y0, x1, y1], radius=min(r, (x1 - x0) / 2, (y1 - y0) / 2), fill=fill, outline=outline, width=width)
def pill(d, cx, cy, s, f, fg, bg, padx=26, h=None, outline=None, anchor_left=False):
    l, tp, r, b = f.getbbox(s); w = r - l + padx * 2; h = h or (b - tp + 26)
    x0 = cx if anchor_left else cx - w / 2
    rrect(d, (x0, cy - h / 2, x0 + w, cy + h / 2), h / 2, fill=bg, outline=outline, width=3 if outline else 0)
    text(d, (x0 + w / 2, cy), s, f, fg)
    return w

def person(d, cx, cy, s, col, who="N", blink_t=0.0, wave=0.0):
    """flat cartoon person; cy = feet baseline-ish center of body. s=scale."""
    if s < 0.05: return
    # body
    rrect(d, (cx - 95 * s, cy - 40 * s, cx + 95 * s, cy + 150 * s), 80 * s, fill=col)
    d.rectangle([cx - 95 * s, cy + 90 * s, cx + 95 * s, cy + 150 * s], fill=col)
    # neck + head
    hx, hy, hr = cx, cy - 115 * s, 64 * s
    if who == "N":  # hair behind + bun
        d.ellipse([hx - hr * 1.12, hy - hr * 1.1, hx + hr * 1.12, hy + hr * 0.9], fill=(70, 40, 30))
        d.ellipse([hx - 30 * s, hy - hr * 1.55, hx + 30 * s, hy - hr * 0.95], fill=(70, 40, 30))
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=SKIN if who == "N" else SKIN2)
    if who == "T":  # short hair cap
        d.chord([hx - hr * 1.02, hy - hr * 1.08, hx + hr * 1.02, hy + hr * 0.5], 180, 360, fill=(30, 30, 40))
    else:
        d.chord([hx - hr * 1.05, hy - hr * 1.08, hx + hr * 1.05, hy + hr * 0.3], 190, 350, fill=(70, 40, 30))
    # eyes
    ey = hy + 6 * s; eh = 9 * s * (0.15 if 1.5 <= (blink_t % 3.7) < 1.62 else 1)
    for ex in (-22, 22):
        d.ellipse([hx + ex * s - 7 * s, ey - eh, hx + ex * s + 7 * s, ey + eh], fill=(25, 25, 35))
    d.arc([hx - 20 * s, hy + 14 * s, hx + 20 * s, hy + 38 * s], 20, 160, fill=(25, 25, 35), width=max(2, int(5 * s)))

def house(d, cx, cy, s, col=NORA, roof=(200, 90, 60)):
    if s < 0.05: return
    d.polygon([(cx - 150 * s, cy - 30 * s), (cx, cy - 150 * s), (cx + 150 * s, cy - 30 * s)], fill=roof)
    d.rectangle([cx - 120 * s, cy - 32 * s, cx + 120 * s, cy + 110 * s], fill=(245, 236, 222))
    d.rectangle([cx - 25 * s, cy + 30 * s, cx + 25 * s, cy + 110 * s], fill=col)
    for dx in (-80, 50):
        d.rectangle([cx + dx * s, cy, cx + (dx + 34) * s, cy + 34 * s], fill=(120, 190, 240))
    d.rectangle([cx + 70 * s, cy - 120 * s, cx + 100 * s, cy - 70 * s], fill=roof)

def apartment(d, cx, cy, s, col=THEO):
    if s < 0.05: return
    rrect(d, (cx - 105 * s, cy - 200 * s, cx + 105 * s, cy + 110 * s), 10 * s, fill=(60, 78, 110))
    for row in range(5):
        for colm in range(3):
            x = cx - 75 * s + colm * 56 * s; y = cy - 175 * s + row * 52 * s
            lit = (row * 3 + colm) % 4 != 1
            d.rectangle([x, y, x + 34 * s, y + 32 * s], fill=(255, 226, 140) if lit else (40, 52, 76))
    d.rectangle([cx - 22 * s, cy + 50 * s, cx + 22 * s, cy + 110 * s], fill=col)

def card(d, box, fill=PANEL, outline=None):
    rrect(d, box, 28, fill=fill, outline=outline, width=3 if outline else 0)

def jar(d, cx, cy, s, fill_frac, label=None):
    if s < 0.05: return
    w, h = 120 * s, 170 * s
    rrect(d, (cx - w, cy - h, cx + w, cy + h), 30 * s, fill=(30, 42, 64), outline=(120, 140, 170), width=max(2, int(5 * s)))
    fh = (2 * h - 20 * s) * clamp(fill_frac)
    if fh > 4: rrect(d, (cx - w + 10 * s, cy + h - 10 * s - fh, cx + w - 10 * s, cy + h - 10 * s), 22 * s, fill=GREEN)
    d.rectangle([cx - w * 0.7, cy - h - 24 * s, cx + w * 0.7, cy - h + 4 * s], fill=(120, 140, 170))
    if label: text(d, (cx, cy + h + 40 * s), label, font(F_BLD, 34 * s), GREEN)

# ---------------- L02 data (from model.py) ----------------
BASE = model_run()
R0 = model_run(apr=0.0001); R10 = model_run(apr=0.10)
ROWS = {r["y"]: r for r in BASE["rows"]}
MAX = (150, 110, 240)   # Max: purple
CASH_C, FIN_C, LEASE_C = NORA, MAX, THEO

def car(d, cx, cy, s, col, shine=True):
    if s < 0.05: return
    d.polygon([(cx - 105 * s, cy - 18 * s), (cx - 62 * s, cy - 80 * s), (cx + 58 * s, cy - 80 * s), (cx + 110 * s, cy - 18 * s)], fill=col)
    d.polygon([(cx - 80 * s, cy - 22 * s), (cx - 52 * s, cy - 68 * s), (cx - 4 * s, cy - 68 * s), (cx - 4 * s, cy - 22 * s)], fill=(180, 220, 250))
    d.polygon([(cx + 6 * s, cy - 22 * s), (cx + 6 * s, cy - 68 * s), (cx + 50 * s, cy - 68 * s), (cx + 84 * s, cy - 22 * s)], fill=(180, 220, 250))
    rrect(d, (cx - 175 * s, cy - 26 * s, cx + 175 * s, cy + 48 * s), 26 * s, fill=col)
    for dx in (-100, 100):
        d.ellipse([cx + (dx - 38) * s, cy + 14 * s, cx + (dx + 38) * s, cy + 90 * s], fill=(25, 25, 32))
        d.ellipse([cx + (dx - 16) * s, cy + 36 * s, cx + (dx + 16) * s, cy + 68 * s], fill=(150, 155, 165))
    d.rectangle([cx + 150 * s, cy - 8 * s, cx + 172 * s, cy + 6 * s], fill=(255, 236, 160))

def person3(d, cx, cy, s, col, who, t):
    person(d, cx, cy, s, col, "N" if who == "N" else "T", t)
    if who == "M":  # Max: cap
        hx, hy = cx, cy - 115 * s
        d.chord([hx - 68 * s, hy - 80 * s, hx + 68 * s, hy + 10 * s], 180, 360, fill=(60, 40, 120))
        d.rectangle([hx - 10 * s, hy - 40 * s, hx + 95 * s, hy - 28 * s], fill=(60, 40, 120))

TRIO = [("NORA", "pays cash", CASH_C, "N"), ("MAX", "finances", FIN_C, "M"), ("THEO", "leases", LEASE_C, "T")]
XS = [380, 960, 1540]

def sc_hook(c):
    d = c.d; t = c.t
    text(d, (W / 2, 110), "SAME $50K CAR. THREE WAYS TO PAY.", font(F_BLK, 66), WHITE)
    pulse = 1 + 0.03 * math.sin(t * 5)
    text(d, (W / 2, 205), "WHO'S RICHEST AFTER 9 YEARS?", font(F_BLK, int(80 * pulse)), YEL, stroke=4)
    for (nm, how, col, who), x in zip(TRIO, XS):
        person3(d, x - 110, 640, 0.8, col, who, t + x)
        car(d, x + 95, 700, 0.62, col)
        text(d, (x, 830), nm, font(F_BLK, 54), col); text(d, (x, 880), how, font(F_BLD, 34), WHITE)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4)
        if k > 0.05: pill(d, XS[2], 300, "-$56,000", font(F_BLK, int(46 * k)), WHITE, RED)
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        if k > 0.05: pill(d, XS[0], 300, "didn't win?!", font(F_BLK, int(40 * k)), (20, 20, 20), YEL)

def stat_card(c, x, y, k, big, label, src, col):
    d = c.d; kk = ease_back(k / 0.45)
    if kk < 0.05: return
    w, h = 470 * kk, 300 * kk
    card(d, (x - w / 2, y - h / 2, x + w / 2, y + h / 2), PANEL, outline=col)
    text(d, (x, y - 50 * kk), big, font(F_BLK, 84 * kk), col)
    text(d, (x, y + 40 * kk), label, font(F_BLD, 32 * kk), WHITE)
    text(d, (x, y + 95 * kk), src, font(F_MED, 24 * kk), GREY)

def sc_setup(c):
    d = c.d
    text(d, (W / 2, 150), "THE SETUP: REAL NUMBERS, OCTOBER 2026", font(F_BLK, 54), WHITE)
    if c.rv(1) >= 0: stat_card(c, 440, 470, c.rv(1), "$50,562", "Average new car price", "Source: Kelley Blue Book, Sep 2026", YEL)
    if c.rv(2) >= 0: stat_card(c, 960, 470, c.rv(2), "7.0%", "Average new car loan APR", "Source: Edmunds, Q3 2026", MAX)
    if c.rv(3) >= 0: stat_card(c, 1480, 470, c.rv(3), "-41.8%", "Value lost in 5 years", "Source: iSeeCars 2026 study", RED)

def sc_rule(c):
    d = c.d
    card(d, (260, 170, 1660, 820), PANEL)
    text(d, (W / 2, 250), "THE RULE THAT MAKES IT FAIR", font(F_BLK, 60), YEL)
    rows = [(0, "All three start with $50,562 in cash", WHITE), (1, "Same monthly car budget: $767", WHITE), (1, "Anything not spent on the car is invested at 7%/yr", GREEN)]
    for i, (k, s, col) in enumerate(rows):
        if c.rv(k) >= 0:
            a = ease_out((c.rv(k) - 0.3 * (i if k == 1 else 0)) / 0.35)
            if a <= 0: continue
            y = 400 + i * 110
            text(d, (360 + (1 - a) * 60, y), "•", font(F_BLK, 60), col, anchor="lm")
            text(d, (410 + (1 - a) * 60, y), s, font(F_BLD, 46), mix(PANEL, col, a), anchor="lm")
    for (nm, how, col, who), x in zip(TRIO, (560, 960, 1360)):
        person3(d, x, 760, 0.38, col, who, c.t + x)

def big_person_scene(c, who, title, lines):
    d = c.d; nm, how, col, wh = next(x for x in TRIO if x[3] == who)
    k = ease_back(c.since() / 0.45)
    person3(d, 380, 560, 1.25 * k, col, wh, c.t)
    car(d, 380, 820, 0.9 * k, col)
    text(d, (1150, 150), title, font(F_BLK, 64), col)
    for i, (st, s, colr, size) in enumerate(lines):
        if c.rv(st) < 0: continue
        a = ease_out(c.rv(st) / 0.35)
        text(d, (760 + (1 - a) * 40, 300 + i * 110), s, font(F_BLK if size > 50 else F_BLD, size), mix(BG, colr, a), anchor="lm")

def sc_nora(c):
    big_person_scene(c, "N", "NORA PAYS CASH", [(0, "Pays $50,562 up front", WHITE, 52), (0, "No loan. No interest.", GREEN, 46),
                                                (1, "Invests her whole $767/month", GREEN, 46), (1, "car budget instead", GREEN, 46)])

def sc_max(c):
    big_person_scene(c, "M", "MAX FINANCES", [(0, "$5,554 down (US average)", WHITE, 50), (0, "Invests the rest of his cash", GREEN, 44),
                                              (1, "6-year loan at 7%", WHITE, 50), (1, "$767 / month", MAX, 72), (2, "Interest paid: $10,241", RED, 50)])

def sc_theo(c):
    big_person_scene(c, "T", "THEO LEASES", [(0, "Rents the car for 3 years,", WHITE, 46), (0, "then swaps for a new one", WHITE, 46),
                                             (1, "Pays for the value it loses", GREY, 40), (1, "+ a finance charge", GREY, 40),
                                             (2, "≈ $773 / month + $4,000 each lease", THEO, 50), (3, "Same as the loan payment!", YEL, 54)])

def sc_loanlen(c):
    d = c.d
    text(d, (W / 2, 120), "LONGER LOANS: LOWER PAYMENT, MORE INTEREST", font(F_BLK, 54), WHITE)
    text(d, (W / 2, 190), "1 in 4 new car loans is now 7 years or longer (Edmunds, Q3 2026)", font(F_MED, 32), GREY)
    rows = [("5 years", 891, 8465, 2), ("6 years", 767, 10241, 0), ("7 years", 679, 12052, 1)]
    for i, (lab, pay, intr, st) in enumerate(rows):
        if c.rv(st) < 0: continue
        a = ease_out(c.rv(st) / 0.6); y = 330 + i * 170
        text(d, (330, y), lab, font(F_BLK, 48), WHITE, anchor="rm")
        rrect(d, (370, y - 50, 370 + 560 * pay / 900 * a, y - 6), 18, fill=MAX)
        rrect(d, (370, y + 6, 370 + 560 * intr / 12500 * a, y + 50), 18, fill=RED)
        if a > 0.8:
            text(d, (390 + 560 * pay / 900, y - 28), f"${pay}/mo", font(F_BLD, 36), WHITE, anchor="lm")
            text(d, (390 + 560 * intr / 12500, y + 28), f"${intr:,} interest", font(F_BLD, 36), RED, anchor="lm")
    if c.rv(3) >= 0:
        k = ease_back(c.rv(3) / 0.4)
        if k > 0.05:
            card(d, (1180, 360, 1760, 640), PANEL2, outline=YEL)
            ptext(c, (1470, 450), "Longer loans", F_BLK, 54, WHITE, k)
            ptext(c, (1470, 530), "FEEL cheaper.", F_BLK, 54, YEL, k)
            ptext(c, (1470, 600), "You just pay for longer.", F_BLD, 34, GREY, k)

def sc_depr(c):
    d = c.d
    text(d, (W / 2, 110), "THE SILENT COST: DEPRECIATION", font(F_BLK, 58), WHITE)
    L, R, T, B = 280, 1500, 220, 800
    vals = [50562] + [ROWS[y]["car"] for y in range(1, 10)]
    d.line([(L, B), (R, B)], fill=LINE, width=4)
    for v in (10000, 20000, 30000, 40000, 50000):
        y = B - (B - T) * v / 52000; d.line([(L, y), (R, y)], fill=(30, 38, 58), width=2)
        text(d, (L - 20, y), "${:,}".format(v), font(F_MED, 26), DIMT, anchor="rm")
    grow = ease_out(c.since() / 2.5); n = len(vals); bw = (R - L) / n
    for i, v in enumerate(vals):
        if i / n > grow: break
        h = (B - T) * v / 52000
        d.rectangle([L + i * bw + 10, B - h, L + (i + 1) * bw - 10, B], fill=mix(GREEN, RED, i / 9))
        text(d, (L + (i + 0.5) * bw, B + 32), "new" if i == 0 else f"yr {i}", font(F_MED, 26), GREY)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4); x = L + 1.5 * bw
        ptext(c, (x, B - (B - T) * vals[1] / 52000 - 50), "-20%", F_BLK, 50, RED, k)
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        ptext(c, (L + 5.5 * bw, B - (B - T) * vals[5] / 52000 - 50), "-42%", F_BLK, 50, RED, k)
        ptext(c, (L + 9.5 * bw, B - (B - T) * vals[9] / 52000 - 50), "$24K", F_BLK, 50, WHITE, k)
    if c.rv(3) >= 0:
        k = ease_back(c.rv(3) / 0.4)
        if k > 0.05: pill(d, 1180, 300, "Theo pays for this inside every lease payment", font(F_BLD, int(32 * k)), (20, 20, 20), THEO)

def sc_score(c):
    d = c.d
    cur = c.cur(); y = cur["show"].get("y", 1)
    ys = [s["show"].get("y", 1) for s in c.run["segs"] if s["start"] <= c.t + 0.05]
    prev_y = ys[-2] if len(ys) > 1 and ys[-2] != y else y
    a = ease_io((c.t - cur["start"]) / 0.9) if prev_y != y else 1
    yy = lerp(prev_y, y, a)
    def val(key, yv):
        i = int(math.floor(yv)); f = yv - i
        lo = ROWS[max(1, i)][key]; hi = ROWS[min(9, i + 1)][key] if i < 9 else lo
        return lo + (hi - lo) * f
    text(d, (W / 2, 100), "SCOREBOARD", font(F_BLK, 60), YEL)
    text(d, (W / 2, 165), "Car value + investments - any loan left", font(F_MED, 32), GREY)
    rrect(d, (W / 2 - 170, 210, W / 2 + 170, 300), 45, fill=PANEL2)
    text(d, (W / 2, 255), f"YEAR {int(round(yy))}", font(F_BLK, 56), WHITE)
    L, R = 430, 1650; mx = 140000
    for i, ((nm, how, col, who), key) in enumerate(zip(TRIO, ("cash", "fin", "lease"))):
        v = val(key, yy); yc = 410 + i * 175
        person3(d, 210, yc + 40, 0.45, col, who, c.t + i)
        rrect(d, (L, yc - 50, R, yc + 50), 30, fill=PANEL)
        if c.rv(1) >= 0:
            w = (R - L) * min(1, v / mx) * ease_out(c.rv(1) / 0.8)
            rrect(d, (L, yc - 50, L + max(60, w), yc + 50), 30, fill=col)
            text(d, (L + max(60, w) + 25, yc), kfmt(round(v, -2)), font(F_BLK, 50), WHITE, anchor="lm")
        text(d, (L + 20, yc - 78), f"{nm} ({how})", font(F_BLD, 28), col, anchor="lm")
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        if k > 0.05:
            pill(d, 1340, 870, "GAP: $56,000", font(F_BLK, int(44 * k)), WHITE, RED)
            pill(d, 650, 870, "NORA = MAX ?!", font(F_BLK, int(44 * k)), (20, 20, 20), YEL)

def sc_twist(c):
    d = c.d; n = c.run["show"].get("n", 1)
    k = ease_back(c.since() / 0.45)
    if k > 0.05: pill(d, W / 2, 190, f"TWIST #{n}", font(F_BLK, int(80 * k)), (20, 20, 20), YEL, padx=50)
    lines = {1: [(0, "Paying cash didn't beat the loan.", WHITE), (1, "Loan cost 7%  =  investments earned 7%", WHITE),
                 (2, "Loan rate < what your money earns: FINANCE", GREEN), (2, "Loan rate > what your money earns: CASH", NORA)],
             2: [(0, "Theo isn't stupid.", WHITE), (1, "Brand-new car the whole time.", WHITE), (1, "Always under warranty. No big repairs.", WHITE),
                 (2, "$56K = the price of always driving new", YEL)]}[n]
    for i, (st, s, col) in enumerate(lines):
        if c.rv(st) < 0: continue
        a = ease_out(c.rv(st) / 0.4)
        text(d, (W / 2, 380 + i * 115 + (1 - a) * 30), s, font(F_BLK, 56), mix(BG, col, a))

def sc_rates(c):
    d = c.d
    text(d, (W / 2, 130), "IT ALL DEPENDS ON YOUR LOAN RATE", font(F_BLK, 58), WHITE)
    for i, (st, title, run_, col) in enumerate([(0, "0% DEALER DEAL", R0, GREEN), (1, "10% LOAN", R10, RED)]):
        if c.rv(st) < 0: continue
        k = ease_back(c.rv(st) / 0.45)
        if k < 0.05: continue
        x = 560 + i * 800; f9 = run_["rows"][-1]
        card(d, (x - 330, 260, x + 330, 760), PANEL, outline=col)
        ptext(c, (x, 330), title, F_BLK, 54, col, k)
        ptext(c, (x, 450), f"Max (finance)  {kfmt(round(f9['fin'], -2))}", F_BLD, 42, MAX, k)
        ptext(c, (x, 540), f"Nora (cash)  {kfmt(round(f9['cash'], -2))}", F_BLD, 42, NORA, k)
        diff = f9["fin"] - f9["cash"]
        ptext(c, (x, 670), ("FINANCE wins +" if diff > 0 else "CASH wins +") + kfmt(round(abs(diff), -2)), F_BLK, 46, YEL, k)

def sc_bill(c):
    d = c.d
    text(d, (W / 2, 110), "WHAT 9 YEARS OF DRIVING REALLY COST", font(F_BLK, 56), WHITE)
    B = 820; sc = 560 / 96000
    stacks = [(1, "THEO", LEASE_C, [(95442, LEASE_C, "Lease payments + fees $95.4K")]),
              (2, "MAX", FIN_C, [(26593, (255, 150, 70), "Value lost $26.6K"), (10241, RED, "Interest $10.2K"), (6000, (200, 120, 220), "Repairs $6K")]),
              (3, "NORA", CASH_C, [(26593, (255, 150, 70), "Value lost $26.6K"), (6000, (200, 120, 220), "Repairs $6K")])]
    for i, (st, nm, col, parts) in enumerate(stacks):
        if c.rv(st) < 0: continue
        x = 330 + i * 560; y = B; a = ease_out(c.rv(st) / 0.7)
        for v, pc, lab in parts:
            h = v * sc * a; d.rectangle([x - 110, y - h, x + 110, y], fill=pc)
            if a > 0.9 and nm != "THEO": text(d, (x + 130, y - h / 2), lab, font(F_BLD, 30), pc, anchor="lm")
            y -= h
        text(d, (x, B + 40), nm, font(F_BLK, 44), col)
        if nm == "NORA" and c.rv(3) > 0.6:
            pill(d, x, y - 60, "+ lost investment growth", font(F_BLD, 28), (20, 20, 20), YEL)
        if nm == "MAX" and a > 0.9: text(d, (x, y - 40), "$42.8K", font(F_BLK, 46), WHITE)
        if nm == "THEO" and a > 0.9:
            text(d, (x, y - 40), "$95.4K lease + fees", font(F_BLK, 40), WHITE)
            text(d, (x, (y + B) / 2), "No car", font(F_BLK, 40), (15, 30, 40)); text(d, (x, (y + B) / 2 + 50), "at the end", font(F_BLD, 30), (15, 30, 40))

def checklist(c, title, items, col=GREEN, warn=False):
    d = c.d
    text(d, (W / 2, 120), title, font(F_BLK, 56), YEL)
    for i, (st, s) in enumerate(items):
        k = c.rv(st)
        if k < 0: continue
        a = ease_back(k / 0.35); y = 280 + i * 140
        rrect(d, (220, y - 52, 1700, y + 52), 30, fill=PANEL)
        if a > 0.05:
            d.ellipse([270 - 32 * a, y - 32 * a, 270 + 32 * a, y + 32 * a], fill=RED if (warn and i > 0) else col)
            text(d, (270, y), "!" if (warn and i > 0) else str(i + 1), font(F_BLK, int(36 * a)), (15, 20, 25))
        text(d, (330, y), s, font(F_BLD, 40), WHITE, anchor="lm")

def sc_lease_ok(c):
    checklist(c, "WHEN LEASING CAN MAKE SENSE (AND THE TRAPS)",
              [(0, "Cheap manufacturer lease deals, swapping every few years, low miles"),
               (1, "Mileage caps, often ~10-12K miles a year, with fees for every mile over"),
               (2, "Wear-and-tear charges at hand-back"), (2, "Ending a lease early can be very expensive")], warn=True)

def sc_tips(c):
    checklist(c, "3 HABITS THAT SAVE REAL MONEY",
              [(1, "Get a bank or credit union loan quote first (1% lower = ~$1,500 saved)"),
               (2, "Keep your car longer: the big value drop is early"),
               (3, "Negotiate the car's price, not the monthly payment")])

def sc_check(c):
    checklist(c, "LEASE, FINANCE OR CASH? THE 30-SECOND VERSION",
              [(1, "Keep cars a long time? Owning usually wins"),
               (2, "Loan rate vs what your money earns decides cash or finance"),
               (3, "Love a new car every few years? Leasing can be fair, at a price")])

def sc_outro(c):
    d = c.d; t = c.t
    for (nm, how, col, who), x in zip(TRIO, XS):
        person3(d, x - 110, 640, 0.8, col, who, t + x); car(d, x + 95, 700, 0.62, col)
        text(d, (x, 830), nm, font(F_BLK, 54), col); text(d, (x, 880), how, font(F_BLD, 34), WHITE)
    if c.rv(1) >= 0:
        text(d, (W / 2, 110), "SAME $50K CAR. THREE WAYS TO PAY.", font(F_BLK, 66), WHITE)
        text(d, (W / 2, 205), "WHO'S RICHEST AFTER 9 YEARS?", font(F_BLK, 80), YEL, stroke=4)
    else:
        k = ease_back(c.since() / 0.4)
        ptext(c, (W / 2, 140), "ARE YOU A NORA, A MAX OR A THEO?", F_BLK, 74, YEL, k, stroke=4)
        ptext(c, (W / 2, 235), "Tell me in the comments  ↓", F_BLD, 44, WHITE, k)
ROOT = os.path.dirname(os.path.dirname(HERE))
_LOGO = Image.open(os.path.join(ROOT, "brand/profile-800.png")).convert("RGB")
_mask = Image.new("L", _LOGO.size, 0); ImageDraw.Draw(_mask).ellipse([0, 0, _LOGO.size[0] - 1, _LOGO.size[1] - 1], fill=255)
_SHORTS = [Image.open(os.path.join(ROOT, "thumbs", f)).convert("RGB") for f in ("06-same-raise.jpg", "01-coffee.jpg")]
def sc_endcard(c):
    d = c.d; k = ease_back(c.since() / 0.5)
    sz = int(320 * k)
    if sz > 10:
        logo = _LOGO.resize((sz, sz), Image.LANCZOS); m = _mask.resize((sz, sz), Image.LANCZOS)
        c.img.paste(logo, (int(520 - sz / 2), int(360 - sz / 2)), m)
    ptext(c, (520, 600), "FINANCE ADVISED", F_BLK, 76, WHITE, k)
    ptext(c, (520, 670), "Money maths in under a minute", F_MED, 36, GREY, k)
    if k > 0.3:
        pill(d, 520, 770, "SUBSCRIBE", font(F_BLK, 44), WHITE, (230, 33, 23), padx=40, h=86)
    for i, im in enumerate(_SHORTS):
        kk = ease_back((c.since() - 0.4 - 0.25 * i) / 0.5)
        if kk < 0.05: continue
        w, h = int(250 * kk), int(444 * kk); x = 1170 + i * 330; y = 470
        rrect(d, (x - w / 2 - 14, y - h / 2 - 14, x + w / 2 + 14, y + h / 2 + 14), 36, fill=(20, 20, 26), outline=(90, 100, 120), width=3)
        c.img.paste(im.resize((w, h), Image.LANCZOS), (int(x - w / 2), int(y - h / 2)))
    kk = ease_back((c.since() - 0.9) / 0.5)
    ptext(c, (1335, 160), "WATCH OUR SHORTS", F_BLK, 64, YEL, kk, stroke=3)
    ptext(c, (1335, 780), "New money maths every day", F_BLD, 36, WHITE, kk)

SCENES = {"endcard": sc_endcard, "hook": sc_hook, "setup": sc_setup, "rule": sc_rule, "nora": sc_nora, "max": sc_max,
          "theo": sc_theo, "loanlen": sc_loanlen, "depr": sc_depr, "score": sc_score, "twist": sc_twist, "rates": sc_rates,
          "bill": sc_bill, "lease_ok": sc_lease_ok, "tips": sc_tips, "check": sc_check, "outro": sc_outro}

# ---------------- background ----------------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg(col):
    dd = np.sqrt(((xx - W / 2) / 1.6) ** 2 + (yy - H * 0.45) ** 2) / 900
    g = np.clip(1 - dd, 0, 1) ** 2
    img = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32)
    img += g[..., None] * np.array(col, np.float32) * 0.22
    grid = ((xx % 80 == 0) | (yy % 80 == 0)).astype(np.float32) * 5
    img += grid[..., None] * (0.3 + 0.7 * g[..., None])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BGS = {"navy": make_bg((70, 90, 200)), "warm": make_bg((220, 110, 60)), "teal": make_bg((40, 170, 190)), "gold": make_bg((200, 160, 40))}
SC_BG = {"hook": "navy", "setup": "navy", "rule": "navy", "nora": "warm", "max": "navy", "theo": "teal", "loanlen": "navy",
         "depr": "warm", "score": "navy", "twist": "gold", "rates": "teal", "bill": "warm", "lease_ok": "teal", "tips": "navy",
         "check": "navy", "outro": "navy", "endcard": "navy"}

# ---------------- captions + UI ----------------
GROUPS = []
for s in SEGS:
    cur = []
    for tk in s["tokens"]:
        cur.append(tk)
        chars = sum(len(x["text"]) + 1 for x in cur)
        if chars >= 34 or tk["text"][-1] in ".?!" or (tk["text"][-1] == "," and chars >= 18):
            GROUPS.append(cur); cur = []
    if cur: GROUPS.append(cur)
for i, g_ in enumerate(GROUPS):
    end = GROUPS[i + 1][0]["start"] if i + 1 < len(GROUPS) else g_[-1]["end"] + 0.5
    GROUPS[i] = (g_[0]["start"], min(end, g_[-1]["end"] + 0.5), g_)

def draw_captions(img, t):
    for gs, ge, toks in GROUPS:
        if gs <= t < ge: break
    else: return
    d = ImageDraw.Draw(img); f = font(F_CAP, 50); sp = 16
    ws = [f.getbbox(tk["text"], stroke_width=6)[2] - f.getbbox(tk["text"], stroke_width=6)[0] for tk in toks]
    tw = sum(ws) + sp * (len(ws) - 1); x = W / 2 - tw / 2; y = 960
    for tk, w in zip(toks, ws):
        active = tk["start"] <= t < tk["end"] + 0.05
        col = GREEN if any(ch in tk["text"] for ch in "$%") else (YEL if active else WHITE)
        d.text((x + w / 2, y), tk["text"], font=f, fill=col, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
        x += w + sp

NUM_SCENES = {"setup", "rule", "nora", "max", "theo", "loanlen", "depr", "score", "rates", "bill"}
def draw_ui(img, t, run):
    d = ImageDraw.Draw(img)
    ch = chapter_at(t)
    if ch and run["scene"] != "endcard": pill(d, 40, 48, ch.upper(), font(F_BLD, 26), WHITE, (255, 255, 255, 0) if False else PANEL2, padx=22, h=50, anchor_left=True)
    # progress bar with chapter ticks
    d.rectangle([0, H - 8, W, H], fill=(30, 36, 54)); d.rectangle([0, H - 8, W * t / TOTAL, H], fill=YEL)
    for st, _ in CHAPS: d.rectangle([W * st / TOTAL - 2, H - 8, W * st / TOTAL + 2, H], fill=BG)
    if run["scene"] in NUM_SCENES or run["show"].get("small"):
        text(d, (W / 2, 1030), "Illustration: $50,562 car, 7% loan/72 mo, est. lease (62% residual), investments 7%/yr, $1k/yr repairs from yr 4; taxes & fees ignored. Not financial advice.",
             font(F_MED, 20), (120, 128, 146))

def frame(t):
    run = run_at(t)
    img = BGS[SC_BG.get(run["scene"], "navy")].copy()
    c = Ctx(img, t, run)
    SCENES[run["scene"]](c)
    draw_captions(img, t)
    draw_ui(img, t, run)
    # quick white flash on scene change
    dt = t - run["start"]
    if 0 <= dt < 0.1 and run is not RUNS[0]:
        a = 1 - dt / 0.1
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.15 * a)
    return img

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--sweep":
        step = int(args[1]); bad = 0
        for i in range(0, NF, step):
            try: frame(i / FPS)
            except Exception as e:
                bad += 1; print("ERR", i / FPS, run_at(i / FPS)["scene"], repr(e))
                if bad > 10: break
        print("sweep done", bad); sys.exit()
    if args:
        for tt in args:
            frame(float(tt)).save(os.path.join(HERE, f"prev_{float(tt):07.2f}.png"))
        sys.exit()
    out = os.path.join(HERE, "video_noaudio.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 900 == 0: print("frame", i, "/", NF, flush=True)
    p.stdin.close(); p.wait(); print("done", out)