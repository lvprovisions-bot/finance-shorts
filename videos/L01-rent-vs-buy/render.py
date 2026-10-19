"""Render L01 rent-vs-buy long-form: 1920x1080 @30fps, frames piped to ffmpeg.
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

# ---------------- model series ----------------
def series(**kw):
    r = model_run(**kw)
    return [0] + [x["owner_nw"] for x in r["rows"]], [0] + [x["renter_nw"] for x in r["rows"]]
BASE_N, BASE_T = series()
R24_N, R24_T = series(rent=2400)
R6_N, R6_T = series(rent=2400, rate=0.06)
UP = MP["price"] * (MP["down"] + MP["close"])
SPEND_T = [0] + [round(UP * (1 + 0.07 / 12) ** (12 * y) - (UP * (1 + 0.07 / 12) ** (12 * y) - UP) * 0.15) for y in range(1, 31)]
BASE_N[0] = BASE_T[0] = R24_N[0] = R24_T[0] = R6_N[0] = R6_T[0] = SPEND_T[0] = None
MODES = {"base": (BASE_N, BASE_T), "spend": (BASE_N, SPEND_T), "rent2400": (R24_N, R24_T), "rent2400r6": (R6_N, R6_T)}

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

# ---------------- scenes ----------------
NX, TX = 430, 1490  # Nora left, Theo right

def sc_hook(c):
    d = c.d; t = c.t
    k1 = c.rv(1); k2 = c.rv(2)
    house(d, NX - 120, 560, 1.0); apartment(d, TX + 130, 590, 0.95)
    person(d, NX + 110, 640, 0.95, NORA, "N", t); person(d, TX - 110, 640, 0.95, THEO, "T", t + 1.3)
    text(d, (NX, 840), "NORA BUYS", font(F_BLK, 56), NORA); text(d, (TX, 840), "THEO RENTS", font(F_BLK, 56), THEO)
    text(d, (W / 2, 120), "SAME SALARY. SAME CITY.", font(F_BLK, 72), WHITE)
    pulse = 1 + 0.03 * math.sin(t * 5)
    text(d, (W / 2, 225), "WHO'S RICHER IN 30 YEARS?", font(F_BLK, int(88 * pulse)), YEL, stroke=4)
    rrect(d, (W / 2 - 70, 480, W / 2 + 70, 620), 70, fill=PANEL2); text(d, (W / 2, 550), "VS", font(F_BLK, 70), WHITE)
    if k1 >= 0:
        kk = ease_back(k1 / 0.4)
        ptext(c, (W / 2, 700), "+$536,000", F_BLK, 76, GREEN, kk)
        ptext(c, (W / 2, 760), "for one of them", F_MED, 34, GREY, kk)
    if k2 >= 0:
        kk = ease_back(k2 / 0.4)
        if kk > 0.05:
            pill(d, W / 2, 330, "...AND THE ANSWER FLIPS", font(F_BLK, int(40 * kk)), (20, 20, 20), YEL)

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
    text(d, (W / 2, 150), "THE SETUP: REAL, CURRENT NUMBERS", font(F_BLK, 54), WHITE)
    if c.rv(1) >= 0: stat_card(c, 440, 470, c.rv(1), "$417,500", "Nora's home (median price)", "Source: NAR, Sep 2026", NORA)
    if c.rv(2) >= 0: stat_card(c, 960, 470, c.rv(2), "7.40%", "30-year fixed mortgage", "Source: Freddie Mac, Oct 2026", YEL)
    if c.rv(3) >= 0: stat_card(c, 1480, 470, c.rv(3), "$1,962", "Theo's rent / month (typical)", "Source: Zillow, Jul 2026", THEO)
    person(d, 120, 760, 0.55, NORA, "N", c.t); person(d, W - 120, 760, 0.55, THEO, "T", c.t + 2)

def sc_rule(c):
    d = c.d
    card(d, (260, 170, 1660, 820), PANEL)
    text(d, (W / 2, 250), "THE RULE THAT MAKES IT FAIR", font(F_BLK, 60), YEL)
    rows = [(1, "Both spend the SAME on housing every month", WHITE),
            (2, "Whoever's cheaper invests the gap at 7% a year", GREEN),
            (3, "7% is below the stock market's long-run average", GREY)]
    for k, s, col in rows:
        if c.rv(k) >= 0:
            a = ease_out(c.rv(k) / 0.35); y = 330 + k * 95
            text(d, (360 + (1 - a) * 60, y), "•", font(F_BLK, 60), col, anchor="lm")
            text(d, (410 + (1 - a) * 60, y), s, font(F_BLD, 46), col, anchor="lm")
    if c.rv(4) >= 0:
        a = ease_back(c.rv(4) / 0.4)
        if a > 0.05:
            f = font(F_BLD, int(36 * a))
            pill(d, 690, 720, "Homes +4%/yr  (US avg 4.4%, FHFA)", f, WHITE, PANEL2, outline=NORA)
            pill(d, 1330, 720, "Rents +3%/yr", f, WHITE, PANEL2, outline=THEO)

def bar_stack(d, x, ybase, w, parts, scale, label_side="r"):
    y = ybase
    for val, col, lab, prog in parts:
        h = val * scale * clamp(prog)
        if h < 1: continue
        d.rectangle([x, y - h, x + w, y], fill=col)
        if prog > 0.8:
            tx = x + w + 30 if label_side == "r" else x - 30
            text(d, (tx, y - h / 2), lab, font(F_BLD, 38), col, anchor="lm" if label_side == "r" else "rm")
        y -= h
    return y

def sc_upfront(c):
    d = c.d
    text(d, (W / 2, 120), "DAY ONE: CASH NEEDED TO BUY", font(F_BLK, 56), WHITE)
    house(d, 260, 520, 0.85); person(d, 470, 640, 0.75, NORA, "N", c.t)
    sc = 520 / 96025; x = 640; yb = 860
    parts = [(83500, NORA, "Down payment (20%)  $83,500", ease_out(c.rv(1) / 0.6) if c.rv(1) >= 0 else 0),
             (12525, RED, "Closing costs (~3%)  $12,525", ease_out(c.rv(2) / 0.6) if c.rv(2) >= 0 else 0)]
    top = bar_stack(d, x, yb, 170, parts, sc)
    if c.rv(3) >= 0:
        k = ease_back(c.rv(3) / 0.4); ptext(c, (x + 85, top - 60), "$96,025", F_BLK, 80, YEL, k)
    if c.rv(4) >= 0:
        k = ease_out(c.rv(4) / 0.8)
        person(d, 1500, 640, 0.75, THEO, "T", c.t)
        jar(d, 1730, 560, 0.85, 0.55 * k, "INVESTED")
        ptext(c, (1730, 300), "$96,025", F_BLK, 64, GREEN, ease_back(c.rv(4) / 0.4))
        if k > 0.1:
            ax = lerp(900, 1560, k)
            d.line([(900, 330), (ax, 330)], fill=GREEN, width=10)
            d.polygon([(ax, 310), (ax + 30, 330), (ax, 350)], fill=GREEN)
            text(d, (1230, 290), "Theo invests the same cash", font(F_BLD, 34), GREEN)

def sc_mortgage(c):
    d = c.d
    text(d, (W / 2, 130), "NORA'S MORTGAGE PAYMENT", font(F_BLK, 56), WHITE)
    text(d, (W / 2, 230), "$2,313 / month", font(F_BLK, 96), NORA)
    x0, x1, y0, y1 = 210, 1710, 400, 560
    rrect(d, (x0, y0, x1, y1), 30, fill=PANEL2)
    fi = 2060 / 2313; xm = x0 + (x1 - x0) * fi
    if c.rv(1) >= 0:
        k = ease_out(c.rv(1) / 0.7); xe = lerp(x0, xm, k)
        rrect(d, (x0, y0, max(x0 + 60, xe), y1), 30, fill=RED)
        if k > 0.7:
            text(d, ((x0 + xm) / 2, (y0 + y1) / 2), "INTEREST TO THE BANK  $2,060", font(F_BLK, 50), WHITE)
    if c.rv(2) >= 0:
        k = ease_out(c.rv(2) / 0.5)
        d.rectangle([xm, y0, lerp(xm, x1, k), y1], fill=GREEN)
        if k > 0.6:
            text(d, ((xm + x1) / 2, y1 + 60), "$253", font(F_BLK, 54), GREEN)
            text(d, ((xm + x1) / 2, y1 + 115), "pays off loan", font(F_BLD, 30), GREEN)
        if c.rv(2) > 1.0 and c.cur()["id"] == "c10":
            k2 = ease_back((c.t - c.cur()["start"]) / 0.4)
            ptext(c, (W / 2 - 120, 780), "89% INTEREST", F_BLK, 110, RED, k2, stroke=3)
    text(d, (W / 2, 330), "First payment, where the money actually goes:", font(F_MED, 34), GREY)

def receipt(c, x, y, w, rows, total, col, title, kt):
    d = c.d
    n = len(rows); h = 180 + 70 * n
    card(d, (x, y, x + w, y + h), (240, 238, 230))
    text(d, (x + w / 2, y + 55), title, font(F_BLK, 40), (30, 30, 40))
    for i, (lab, val, k) in enumerate(rows):
        if k < 0: continue
        a = ease_out(k / 0.3); yy = y + 120 + i * 70
        text(d, (x + 40 + (1 - a) * 30, yy), lab, font(F_BLD, 36), (40, 40, 50), anchor="lm")
        text(d, (x + w - 40, yy), val, font(F_BLK, 38), (40, 40, 50), anchor="rm")
    d.line([(x + 30, y + h - 75), (x + w - 30, y + h - 75)], fill=(160, 160, 160), width=3)
    if kt >= 0:
        k = ease_back(kt / 0.4)
        text(d, (x + 40, y + h - 38), "TOTAL / MONTH", font(F_BLK, 32), (40, 40, 50), anchor="lm")
        ptext(c, (x + w - 120, y + h - 38), total, F_BLK, 46, col, k)

def sc_monthly(c):
    d = c.d
    text(d, (W / 2, 95), "THE REAL MONTHLY COST", font(F_BLK, 54), WHITE)
    rows = [("Mortgage", "$2,313", c.rv(0)), ("Property tax", "$313", c.rv(1)), ("Insurance", "$234", c.rv(2)), ("Maintenance (1%/yr)", "$348", c.rv(3))]
    receipt(c, 170, 170, 640, rows, "$3,208", (220, 90, 40), "NORA", c.rv(4))
    if c.rv(5) >= 0:
        rows2 = [("Rent", "$1,962", c.rv(5)), ("Renter's insurance", "$15", c.rv(5) - 0.4)]
        receipt(c, 1110, 170, 640, rows2, "$1,977", (20, 130, 170), "THEO", c.rv(5) - 0.8)
    if c.rv(6) >= 0:
        k = ease_back(c.rv(6) / 0.45)
        rrect(d, (W / 2 - 330 * k, 690, W / 2 + 330 * k, 840), 40, fill=PANEL2, outline=GREEN, width=4)
        ptext(c, (W / 2, 745), "GAP: $1,231 / MONTH", F_BLK, 54, GREEN, k)
        ptext(c, (W / 2, 805), "Theo invests all of it", F_BLD, 32, WHITE, k)

def sc_rentup(c):
    d = c.d
    text(d, (W / 2, 110), "RENT RISES. A FIXED MORTGAGE DOESN'T.", font(F_BLK, 54), WHITE)
    L, R, T, B = 230, 1690, 220, 800; mx = 5000
    d.line([(L, B), (R, B)], fill=LINE, width=4)
    for v in (1000, 2000, 3000, 4000, 5000):
        y = B - (B - T) * v / mx; d.line([(L, y), (R, y)], fill=(30, 38, 58), width=2)
        text(d, (L - 20, y), "${:,}".format(v), font(F_MED, 26), DIMT, anchor="rm")
    grow = ease_out(c.since() / 2.0); n = 30; bw = (R - L) / n
    for i in range(n):
        if i / n > grow: break
        rent = 1962 * 1.03 ** i; h = (B - T) * rent / mx
        d.rectangle([L + i * bw + 6, B - h, L + (i + 1) * bw - 6, B], fill=THEO)
        if i in (0, 9, 29): text(d, (L + (i + 0.5) * bw, B + 32), f"yr {i + 1}", font(F_MED, 26), GREY)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4)
        ptext(c, (L + 9.5 * bw, B - (B - T) * 2560 / mx - 60), "$2,560", F_BLK, 44, THEO, k)
        ptext(c, (L + 27.5 * bw, B - (B - T) * 4624 / mx - 50), "$4,624", F_BLK, 52, THEO, k)
    if c.rv(2) >= 0:
        k = ease_out(c.rv(2) / 0.8); y = B - (B - T) * 2313 / mx
        d.line([(L, y), (lerp(L, R, k), y)], fill=NORA, width=12)
        if k > 0.6:
            pill(d, 1180, y + 70, "Nora's mortgage: $2,313 for all 30 years", font(F_BLD, 34), (20, 20, 20), NORA)

def sc_lever(c):
    d = c.d
    text(d, (W / 2, 110), "BUYING'S SECRET WEAPON: LEVERAGE", font(F_BLK, 56), WHITE)
    house(d, 480, 520, 1.6)
    text(d, (480, 780), "$417,500 home", font(F_BLD, 40), WHITE)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4)
        ptext(c, (480, 240), "+4%  =  +$16,700", F_BLK, 64, GREEN, k)
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        if k > 0.05:
            card(d, (1050, 300 - 20 * k, 1700, 660), PANEL, outline=NORA)
            ptext(c, (1375, 380), "Her cash in: $96,025", F_BLD, 40, WHITE, k)
            ptext(c, (1375, 470), "Gain: $16,700", F_BLD, 40, GREEN, k)
            ptext(c, (1375, 580), "≈ 17% on her cash", F_BLK, 66, YEL, k)
    if c.rv(3) >= 0:
        k = ease_back(c.rv(3) / 0.4)
        ptext(c, (1375, 760), "...but losses are leveraged too", F_BLD, 40, RED, k)

def sc_score(c):
    d = c.d
    cur = c.cur(); y = cur["show"].get("y", 1)
    # find previous year shown for animation
    ys = [s["show"].get("y", 1) for s in c.run["segs"] if s["start"] <= c.t + 0.05]
    prev_y = ys[-2] if len(ys) > 1 and ys[-2] != y else y
    a = ease_io((c.t - cur["start"]) / 0.9) if prev_y != y else 1
    yy = lerp(prev_y, y, a)
    def val(arr, yv):
        i = int(math.floor(yv)); f = yv - i
        lo = arr[i] if arr[i] is not None else 0; hi = arr[min(30, i + 1)] if i < 30 else lo
        return lo + (hi - lo) * f
    n, th = val(BASE_N, yy), val(BASE_T, yy)
    text(d, (W / 2, 110), "SCOREBOARD", font(F_BLK, 60), YEL)
    text(d, (W / 2, 180), "What each would walk away with: after selling costs, the loan and tax", font(F_MED, 32), GREY)
    rrect(d, (W / 2 - 170, 240, W / 2 + 170, 330), 45, fill=PANEL2)
    text(d, (W / 2, 285), f"YEAR {int(round(yy))}", font(F_BLK, 56), WHITE)
    L, R = 420, 1700; mx = 400000
    for i, (nm, v, col, who) in enumerate([("NORA (buys)", n, NORA, "N"), ("THEO (rents)", th, THEO, "T")]):
        yc = 470 + i * 190
        person(d, 200, yc + 40, 0.5, col, who, c.t + i)
        rrect(d, (L, yc - 55, R, yc + 55), 30, fill=PANEL)
        if c.rv(1) >= 0:
            w = (R - L) * clamp(v / mx) * ease_out(c.rv(1) / 0.8)
            rrect(d, (L, yc - 55, L + max(60, w), yc + 55), 30, fill=col)
            text(d, (L + max(60, w) + 25, yc), kfmt(round(v, -3)), font(F_BLK, 54), WHITE, anchor="lm")
        text(d, (L + 20, yc - 85), nm, font(F_BLD, 30), col, anchor="lm")
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        ptext(c, (W / 2, 860), "Can Nora catch up?", F_BLK, 62, YEL, k)

def sc_where(c):
    d = c.d
    text(d, (W / 2, 100), "30 YEARS OF MONEY YOU NEVER GET BACK", font(F_BLK, 54), WHITE)
    B = 860; sc = 640 / 1120116; x = 520; w = 300
    parts = [(498517, RED, "Interest  $499K", 1), (214575, (255, 160, 70), "Property tax  $215K", 2),
             (133592, (230, 120, 200), "Insurance  $134K", 3), (238417, (150, 130, 255), "Maintenance  $238K", 4)]
    y = B
    for v, col, lab, k in parts:
        if c.rv(k) < 0: continue
        h = v * sc * ease_out(c.rv(k) / 0.5)
        d.rectangle([x, y - h, x + w, y], fill=col)
        if c.rv(k) > 0.35: text(d, (x - 30, y - h / 2), lab, font(F_BLD, 36), col, anchor="rm")
        y -= h
    text(d, (x + w / 2, B + 40), "NORA (owning)", font(F_BLD, 34), NORA)
    if c.rv(5) >= 0:
        k = ease_back(c.rv(5) / 0.4); ptext(c, (x + w / 2, y - 55), "$1.09M", F_BLK, 70, YEL, k)
    if c.rv(6) >= 0:
        x2 = 1150; h = 1120116 * sc * ease_out(c.rv(6) / 0.7)
        d.rectangle([x2, B - h, x2 + w, B], fill=THEO)
        text(d, (x2 + w / 2, B + 40), "THEO (rent paid)", font(F_BLD, 34), THEO)
        if c.rv(6) > 0.6:
            ptext(c, (x2 + w / 2, B - h - 55), "$1.12M", F_BLK, 70, YEL, ease_back((c.rv(6) - 0.6) / 0.4))
        if c.cur()["id"] == "w8":
            k = ease_back((c.t - c.cur()["start"]) / 0.4)
            ptext(c, (1660, 470), "ALMOST", F_BLK, 64, WHITE, k)
            ptext(c, (1660, 545), "THE SAME", F_BLK, 64, WHITE, k)

CH_L, CH_R, CH_T, CH_B = 260, 1500, 200, 800
def sc_chart(c):
    d = c.d; mode = None
    for s in c.run["segs"]:
        if s["start"] <= c.t + 0.05 and s["show"].get("mode"): mode = s["show"]["mode"]
    mode = mode or c.run["mode"] or "base"
    Ns, Ts = MODES[mode]
    titles = {"base": "NET WORTH OVER 30 YEARS", "spend": "IF THEO SPENDS THE GAP", "rent2400": "WITH A FAIR RENT ($2,400)", "rent2400r6": "FAIR RENT + 6% MORTGAGE"}
    text(d, (W / 2 - 60, 110), titles[mode], font(F_BLK, 54), WHITE)
    mx = 2000000
    for v in (500000, 1000000, 1500000, 2000000):
        y = CH_B - (CH_B - CH_T) * v / mx; d.line([(CH_L, y), (CH_R, y)], fill=(30, 38, 58), width=2)
        text(d, (CH_L - 20, y), kfmt(v), font(F_MED, 26), DIMT, anchor="rm")
    d.line([(CH_L, CH_B), (CH_R, CH_B)], fill=LINE, width=4)
    for yr in (0, 5, 10, 15, 20, 25, 30):
        x = CH_L + (CH_R - CH_L) * yr / 30; text(d, (x, CH_B + 32), f"{yr}", font(F_MED, 26), GREY)
    text(d, (CH_L + (CH_R - CH_L) / 2, CH_B + 70), "years", font(F_MED, 26), DIMT)
    # mode-change re-draw animation
    mstart = c.run["start"]
    for s in c.run["segs"]:
        if s["start"] <= c.t + 0.05 and s["show"].get("mode") == mode: mstart = s["start"]; break
    yrs = 1 + 29 * ease_io((c.t - mstart) / 2.6)
    def pts(arr):
        out = []
        for i in range(1, 31):
            if i > yrs + 1e-6:
                lo = arr[i - 1] if arr[i - 1] is not None else arr[i]; f = yrs - (i - 1)
                out.append((CH_L + (CH_R - CH_L) * yrs / 30, CH_B - (CH_B - CH_T) * (lo + (arr[i] - lo) * f) / mx)); break
            out.append((CH_L + (CH_R - CH_L) * i / 30, CH_B - (CH_B - CH_T) * arr[i] / mx))
        return out
    pn, pt = pts(Ns), pts(Ts)
    if len(pt) > 1: d.line(pt, fill=THEO, width=10, joint="curve")
    if len(pn) > 1: d.line(pn, fill=NORA, width=10, joint="curve")
    for p, col in ((pn[-1], NORA), (pt[-1], THEO)):
        d.ellipse([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14], fill=col)
    # crossover marker
    if mode in ("rent2400", "rent2400r6"):
        cy = next(i for i in range(1, 31) if Ns[i] > Ts[i])
        if yrs >= cy:
            x = CH_L + (CH_R - CH_L) * cy / 30
            d.line([(x, CH_T), (x, CH_B)], fill=YEL, width=3)
            pill(d, x, CH_T - 10, f"Nora overtakes: year {cy}", font(F_BLD, 28), (20, 20, 20), YEL)
    # right-side labels
    done = yrs > 29.5
    nv, tv = Ns[30], Ts[30]
    lab_n = kfmt(round(Ns[min(30, int(yrs))], -3)); lab_t = kfmt(round(Ts[min(30, int(yrs))], -3))
    if done: lab_n, lab_t = kfmt(round(nv, -3)), kfmt(round(tv, -3))
    win = "N" if nv > tv else "T"
    for i, (nm, lab, col, who) in enumerate([("NORA", lab_n, NORA, "N"), ("THEO", lab_t, THEO, "T")]):
        y0 = 300 + i * 260
        card(d, (1560, y0, 1860, y0 + 220), PANEL, outline=col if (done and win == who) else None)
        text(d, (1710, y0 + 50), nm, font(F_BLK, 40), col)
        text(d, (1710, y0 + 130), lab, font(F_BLK, 58), WHITE)
        if done and win == who:
            pill(d, 1710, y0 + 195, "WINS", font(F_BLK, 28), (20, 20, 20), YEL)
    if mode == "base" and c.cur()["id"] == "t2":
        ptext(c, (900, 260), "Nora's house: $1.35M, paid off", F_BLD, 40, NORA, ease_back((c.t - c.cur()["start"]) / 0.4))
    if mode == "rent2400" and c.cur()["id"] == "y8":
        k = ease_back((c.t - c.cur()["start"]) / 0.4)
        if k > 0.05:
            card(d, (520, 260, 1240, 470), PANEL2, outline=YEL)
            ptext(c, (880, 315), "SELL AFTER 5 YEARS?", F_BLK, 44, YEL, k)
            ptext(c, (880, 400), "Theo $181K  vs  Nora $162K", F_BLK, 44, WHITE, k)

def sc_twist(c):
    d = c.d; n = c.run["show"].get("n", 1)
    k = ease_back(c.since() / 0.45)
    if k > 0.05:
        pill(d, W / 2, 200, f"TWIST #{n}", font(F_BLK, int(80 * k)), (20, 20, 20), YEL, padx=50)
    lines = {1: [(0, "Theo only wins if he invests"), (0, "EVERY spare dollar, EVERY month"), (0, "for 360 months in a row.")],
             2: [(0, "\"Typical rent\" includes small apartments."), (1, "Nora bought a whole house."), (2, "A similar house might rent for $2,400.")]}[n]
    for i, (st, s) in enumerate(lines):
        if c.rv(st) < 0: continue
        a = ease_out((c.rv(st) - (0.25 * i if n == 1 else 0)) / 0.4)
        if a <= 0: continue
        col = YEL if (n == 1 and i == 1) or (n == 2 and i == 2) else WHITE
        text(d, (W / 2, 420 + i * 120 + (1 - a) * 30), s, font(F_BLK, 62), mix(BG, col, a))
    if n == 1:
        person(d, 1700, 760, 0.6, THEO, "T", c.t)
    else:
        house(d, 250, 760, 0.6); apartment(d, 1680, 780, 0.55)

def sc_ptr(c):
    d = c.d
    text(d, (W / 2, 110), "THE 30-SECOND TEST: PRICE-TO-RENT RATIO", font(F_BLK, 54), WHITE)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4)
        if k > 0.05:
            card(d, (460, 190, 1460, 330), PANEL2)
            ptext(c, (W / 2, 260), "HOME PRICE  ÷  (MONTHLY RENT × 12)", F_BLK, 50, YEL, k)
    if c.rv(2) >= 0:
        k = ease_out(c.rv(2) / 0.4)
        text(d, (W / 2, 410), "$417,500 ÷ ($1,962 × 12)  =  17.7", font(F_BLK, 58), mix(BG, WHITE, k))
    if c.rv(3) >= 0:
        k = ease_out(c.rv(3) / 0.4)
        text(d, (W / 2, 500), "$417,500 ÷ ($2,400 × 12)  =  14.5", font(F_BLK, 58), mix(BG, WHITE, k))
    if c.rv(4) >= 0:
        k = ease_out(c.rv(4) / 0.6)
        L, R, y = 260, 1660, 700; lo, hi = 8, 28
        def X(v): return L + (R - L) * (v - lo) / (hi - lo)
        zones = [(lo, 15, GREEN, "BUYING TENDS TO WIN"), (15, 20, YEL, "IT DEPENDS"), (20, hi, THEO, "RENTING TENDS TO WIN")]
        for a, b, col, lab in zones:
            x0, x1 = X(a), X(min(b, lo + (hi - lo) * k))
            if x1 > x0:
                d.rectangle([x0, y - 40, x1, y + 40], fill=col)
                if k > 0.9: text(d, ((X(a) + X(b)) / 2, y + 85), lab, font(F_BLD, 32), col)
        if k > 0.9:
            for v in (15, 20):
                d.line([(X(v), y - 40), (X(v), y + 40)], fill=BG, width=4)
                text(d, (X(v), y + 130), str(v), font(F_BLK, 30), GREY)
            for v, lab, dx in ((17.7, "17.7", 40), (14.5, "14.5", -40)):
                d.polygon([(X(v) - 18, y - 70), (X(v) + 18, y - 70), (X(v), y - 42)], fill=WHITE)
                text(d, (X(v) + dx, y - 110), lab, font(F_BLK, 44), WHITE)
            text(d, (W / 2, y + 185), "A rule of thumb, not a law", font(F_MED, 28), GREY)

def sc_check(c):
    d = c.d
    text(d, (W / 2, 110), "SO WHO WINS? IT DEPENDS ON 4 THINGS", font(F_BLK, 56), YEL)
    items = ["Your price-to-rent ratio", "How long you'll stay (sellers now stay ~11 years, NAR)",
             "Would you REALLY invest the gap every month?", "The non-money stuff: stability, freedom, a home that's yours"]
    for i, s in enumerate(items):
        k = c.rv(i + 1)
        if k < 0: continue
        a = ease_back(k / 0.35); y = 260 + i * 140
        rrect(d, (240, y - 50, 1680, y + 50), 30, fill=PANEL)
        if a > 0.05:
            d.ellipse([280 - 30 * a, y - 30 * a, 280 + 30 * a, y + 30 * a], fill=GREEN)
            text(d, (280, y), str(i + 1), font(F_BLK, int(36 * a)), (10, 30, 20))
        text(d, (340, y), s, font(F_BLD, 42), WHITE, anchor="lm")

def sc_outro(c):
    d = c.d; t = c.t
    house(d, NX - 120, 560, 1.0); apartment(d, TX + 130, 590, 0.95)
    person(d, NX + 110, 640, 0.95, NORA, "N", t); person(d, TX - 110, 640, 0.95, THEO, "T", t + 1.3)
    text(d, (NX, 840), "TEAM NORA", font(F_BLK, 56), NORA); text(d, (TX, 840), "TEAM THEO", font(F_BLK, 56), THEO)
    rrect(d, (W / 2 - 70, 480, W / 2 + 70, 620), 70, fill=PANEL2); text(d, (W / 2, 550), "OR", font(F_BLK, 64), WHITE)
    if c.run["show"].get("st") == 2 or c.cur()["id"] == "w9":
        k = ease_back(c.since() / 0.4)
        ptext(c, (W / 2, 150), "PAUSE: WHO DO YOU THINK WINS?", F_BLK, 80, YEL, k, stroke=4)
        ptext(c, (W / 2, 250), "Comment  NORA  or  THEO  ↓", F_BLD, 44, WHITE, k)
    elif c.rv(1) >= 0:
        text(d, (W / 2, 120), "SAME SALARY. SAME CITY.", font(F_BLK, 72), WHITE)
        text(d, (W / 2, 225), "WHO'S RICHER IN 30 YEARS?", font(F_BLK, 88), YEL, stroke=4)
    else:
        k = ease_back(c.since() / 0.4)
        ptext(c, (W / 2, 150), "WHICH TEAM ARE YOU?", F_BLK, 88, YEL, k, stroke=4)
        ptext(c, (W / 2, 250), "Tell me in the comments  ↓", F_BLD, 44, WHITE, k)


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

SCENES = {"endcard": sc_endcard, "hook": sc_hook, "setup": sc_setup, "rule": sc_rule, "upfront": sc_upfront, "mortgage": sc_mortgage,
          "monthly": sc_monthly, "rentup": sc_rentup, "lever": sc_lever, "score": sc_score, "where": sc_where,
          "chart": sc_chart, "twist": sc_twist, "ptr": sc_ptr, "check": sc_check, "outro": sc_outro}

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
SC_BG = {"hook": "navy", "setup": "navy", "rule": "navy", "upfront": "warm", "mortgage": "warm", "monthly": "warm",
         "rentup": "teal", "lever": "warm", "score": "navy", "where": "warm", "chart": "navy", "twist": "gold",
         "ptr": "teal", "check": "navy", "outro": "navy", "endcard": "navy"}

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

NUM_SCENES = {"setup", "rule", "upfront", "mortgage", "monthly", "rentup", "lever", "score", "where", "chart", "ptr"}
def draw_ui(img, t, run):
    d = ImageDraw.Draw(img)
    ch = chapter_at(t)
    if ch and run["scene"] != "endcard": pill(d, 40, 48, ch.upper(), font(F_BLD, 26), WHITE, (255, 255, 255, 0) if False else PANEL2, padx=22, h=50, anchor_left=True)
    # progress bar with chapter ticks
    d.rectangle([0, H - 8, W, H], fill=(30, 36, 54)); d.rectangle([0, H - 8, W * t / TOTAL, H], fill=YEL)
    for st, _ in CHAPS: d.rectangle([W * st / TOTAL - 2, H - 8, W * st / TOTAL + 2, H], fill=BG)
    if run["scene"] in NUM_SCENES or run["show"].get("small"):
        text(d, (W / 2, 1030), "Illustration only: assumes homes +4%/yr, rents +3%/yr, investments 7%/yr; real results vary. Not financial advice.",
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
