"""WHO WINS? #7: same $300K house, credit score 760 vs 620. 1080x1920 @30fps. Indigo -> plum blueprint grid + skyline, score gauges, interest towers."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
TM = json.load(open(os.path.join(HERE, "timings.json")))
TOTAL = TM["total"] + 0.4
NF = int(TOTAL * FPS)
PREVIEW = [float(x) for x in sys.argv[1:]]

F_CAP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_HAND = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"
F_NUM = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_MED = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
_fc = {}
def font(path, size):
    k = (path, max(2, int(size)))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, k[1])
    return _fc[k]

WHITE = (255, 255, 255); INK = (38, 34, 74); BLUE_INK = (40, 80, 200)
YEL = (255, 216, 77); GREEN = (30, 170, 95); RED = (230, 60, 70); GREY = (110, 106, 140)
NORA = (255, 140, 82); THEO = (70, 196, 230); SKIN = (255, 214, 180); SKIN2 = (196, 140, 100)
HAIR_N = (70, 40, 30); HAIR_T = (30, 30, 40)
B10 = (130, 200, 255); B12 = (150, 120, 255); B22 = (255, 120, 150)

def clamp(x): return min(max(x, 0.0), 1.0)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t

SEG = {s["scene"]: s for s in TM["segments"]}
def tok(scene, i): return SEG[scene]["tokens"][i]["start"]
def seg_start(scene): return SEG[scene]["start"]
def scene_at(t):
    cur = TM["segments"][0]
    for s in TM["segments"]:
        if t >= s["start"] - 0.05:
            cur = s
    return cur

# mouth openness from the voice envelope
sr, vv = wavfile.read(os.path.join(HERE, "voice.wav"))
vv = np.abs(vv.astype(np.float32) / 32768)
def mouth_at(t):
    i = int(t * sr); w = int(0.04 * sr)
    if i >= len(vv): return 0.0
    return clamp(vv[max(0, i - w):i + w].mean() / 0.12)
def pop_text(img, xy, s, path, size, fill, scale=1.0, stroke=0, alpha=1.0, anchor_c=True, sfill=(0, 0, 0)):
    if scale <= 0.01 or alpha <= 0.01 or size * scale < 2:
        return
    f = font(path, size * scale)
    pad = 20 + stroke
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    layer = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - l, pad - t), s, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=sfill + (255,))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    x = xy[0] - layer.width / 2 if anchor_c else xy[0] - pad
    img.alpha_composite(layer, (int(x), int(xy[1] - layer.height / 2)))

def tw(s, path, size):
    l, t, r, b = font(path, size).getbbox(s); return r - l

# ---------- characters ----------
def person(img, cx, cy, s, col, who, t, talk=0.0, pose="idle", mood="smile"):
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bob = math.sin(t * 9) * 6 * s * talk
    cy = cy + bob
    sk = SKIN if who == "N" else SKIN2
    # arms (behind body)
    sh_l, sh_r = (cx - 80 * s, cy + 5 * s), (cx + 80 * s, cy + 5 * s)
    def arm(p0, p1, col=col):
        d.line([p0, p1], fill=col, width=max(2, int(38 * s)))
        d.ellipse([p1[0] - 24 * s, p1[1] - 24 * s, p1[0] + 24 * s, p1[1] + 24 * s], fill=sk)
    wv = math.sin(t * 7) * 18 * s
    if pose == "point_up":      # points up at the board
        side = 1 if who == "T" else -1
        arm(sh_r if side > 0 else sh_l, (cx + side * 150 * s, cy - 190 * s + wv * 0.3))
        arm(sh_l if side > 0 else sh_r, (cx - side * 120 * s, cy + 120 * s))
    elif pose == "shrug":
        arm(sh_l, (cx - 175 * s, cy - 70 * s + wv * 0.4)); arm(sh_r, (cx + 175 * s, cy - 70 * s - wv * 0.4))
    elif pose == "cheer":
        arm(sh_l, (cx - 140 * s, cy - 165 * s + wv * 0.5)); arm(sh_r, (cx + 140 * s, cy - 165 * s - wv * 0.5))
    elif pose == "facepalm":
        arm(sh_l, (cx - 120 * s, cy + 120 * s)); arm(sh_r, (cx + 20 * s, cy - 110 * s))
    elif pose == "marker":      # Nora holding a marker towards the board
        side = -1 if who == "N" else 1
        p1 = (cx + side * 160 * s, cy - 150 * s + wv * 0.3)
        arm(sh_l if side < 0 else sh_r, p1)
        d.rounded_rectangle([p1[0] - 9 * s, p1[1] - 60 * s, p1[0] + 9 * s, p1[1] - 10 * s], radius=6 * s, fill=RED)
        arm(sh_r if side < 0 else sh_l, (cx - side * 110 * s, cy + 125 * s))
    else:
        arm(sh_l, (cx - 115 * s, cy + 125 * s)); arm(sh_r, (cx + 115 * s, cy + 125 * s))
    # body
    d.rounded_rectangle([cx - 95 * s, cy - 40 * s, cx + 95 * s, cy + 150 * s], radius=80 * s, fill=col)
    d.rectangle([cx - 95 * s, cy + 90 * s, cx + 95 * s, cy + 150 * s], fill=col)
    if who == "T":   # collar stripe
        d.polygon([(cx - 30 * s, cy - 38 * s), (cx, cy + 5 * s), (cx + 30 * s, cy - 38 * s)], fill=(40, 120, 190))
    # head
    hx, hy, hr = cx, cy - 115 * s, 64 * s
    if who == "N":
        d.ellipse([hx - hr * 1.12, hy - hr * 1.1, hx + hr * 1.12, hy + hr * 0.9], fill=HAIR_N)
        d.ellipse([hx - 30 * s, hy - hr * 1.55, hx + 30 * s, hy - hr * 0.95], fill=HAIR_N)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=sk)
    if who == "T":
        d.chord([hx - hr * 1.02, hy - hr * 1.08, hx + hr * 1.02, hy + hr * 0.5], 180, 360, fill=HAIR_T)
        d.polygon([(hx + 10 * s, hy - hr * 1.0), (hx + 40 * s, hy - hr * 1.32), (hx + 50 * s, hy - hr * 0.9)], fill=HAIR_T)
    else:
        d.chord([hx - hr * 1.05, hy - hr * 1.08, hx + hr * 1.05, hy + hr * 0.3], 190, 350, fill=HAIR_N)
    # eyes
    ey = hy + 6 * s
    blink = 1.5 <= ((t + (0 if who == "N" else 1.7)) % 3.9) < 1.62
    closed = mood == "facepalm"
    for ex in (-22, 22):
        if blink or closed:
            d.line([hx + ex * s - 9 * s, ey, hx + ex * s + 9 * s, ey], fill=(25, 25, 35), width=max(2, int(4 * s)))
        else:
            d.ellipse([hx + ex * s - 7 * s, ey - 9 * s, hx + ex * s + 7 * s, ey + 9 * s], fill=(25, 25, 35))
    if mood == "smug":
        for ex in (-22, 22):
            d.line([hx + (ex - 12) * s, ey - 22 * s, hx + (ex + 12) * s, ey - 16 * s], fill=HAIR_T, width=max(2, int(5 * s)))
    if mood == "worried":
        for ex in (-22, 22):
            sgn = 1 if ex < 0 else -1
            d.line([hx + (ex - 12) * s, ey - 16 * s - sgn * 4 * s, hx + (ex + 12) * s, ey - 16 * s + sgn * 4 * s], fill=(25, 25, 35), width=max(2, int(4 * s)))
        d.ellipse([hx + 52 * s, hy - 30 * s, hx + 66 * s, hy - 8 * s], fill=(120, 200, 255))  # sweat drop
    # mouth
    mo = talk * mouth_at(t)
    my = hy + 30 * s
    if mo > 0.12:
        h = (6 + 18 * mo) * s
        d.ellipse([hx - 15 * s, my - h / 2, hx + 15 * s, my + h / 2], fill=(90, 30, 40))
    elif mood == "worried":
        d.arc([hx - 16 * s, my - 2 * s, hx + 16 * s, my + 18 * s], 200, 340, fill=(25, 25, 35), width=max(2, int(5 * s)))
    else:
        d.arc([hx - 20 * s, my - 16 * s, hx + 20 * s, my + 8 * s], 20, 160, fill=(25, 25, 35), width=max(2, int(5 * s)))
    # soft shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(20, 10, 50, 70))
    img.alpha_composite(sh); img.alpha_composite(lay)
# ---------- background: deep indigo -> plum, faint blueprint grid + night skyline ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((10, 14, 52), np.float32); bot = np.array((66, 20, 84), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    grid = (((xx % 60) < 2) | ((yy % 60) < 2)).astype(np.float32) * 10
    img += grid[..., None] * np.array((0.6, 0.8, 1.4), np.float32)
    # soft glow behind the stage
    r = np.sqrt(((xx - W / 2) / 1.3) ** 2 + ((yy - 620) / 1.0) ** 2)
    img += (np.clip(1 - r / 800, 0, 1) ** 2)[..., None] * np.array((30, 30, 80), np.float32)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    # skyline silhouette behind the characters
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(7); x = 0
    while x < W:
        w = int(rng.integers(70, 150)); h = int(rng.integers(60, 190)); base = 1095
        if rng.random() < 0.5:   # house with roof
            d.rectangle([x, base - h, x + w, base], fill=(26, 18, 64, 255))
            d.polygon([(x - 6, base - h), (x + w / 2, base - h - 50), (x + w + 6, base - h)], fill=(26, 18, 64, 255))
        else:
            d.rectangle([x, base - h - 40, x + w, base], fill=(22, 16, 58, 255))
        for wy in range(base - h + 20, base - 20, 38):
            for wx in range(x + 16, x + w - 20, 34):
                if rng.random() < 0.35:
                    d.rectangle([wx, wy, wx + 14, wy + 18], fill=(255, 210, 120, 70))
        x += w + int(rng.integers(6, 24))
    d.rectangle([0, 1095, W, H], fill=(30, 16, 62, 255))
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 95, 110)
def money(v): return "${:,.0f}".format(v)
def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0

# ---------- score gauge ----------
def score_col(v):
    if v < 640: return (255, 90, 90)
    if v < 700: return (255, 170, 60)
    if v < 740: return (240, 220, 70)
    return (70, 220, 120)
def gauge(img, cx, cy, r, score, name, ncol, glow=0.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([cx - r - 30, cy - r - 70, cx + r + 30, cy + 95], radius=30, fill=(8, 10, 36, 190),
                        outline=ncol + (230,), width=5)
    bands = [(300, 580, (200, 50, 60)), (580, 670, (230, 110, 50)), (670, 740, (220, 190, 50)), (740, 850, (50, 190, 100))]
    for a0, a1, c in bands:
        s0 = 180 + (a0 - 300) / 550 * 180; s1 = 180 + (a1 - 300) / 550 * 180
        d.arc([cx - r, cy - r, cx + r, cy + r], s0, s1, fill=c + (255,), width=26)
    ang = math.radians(180 + (score - 300) / 550 * 180)
    nx, ny = cx + math.cos(ang) * (r - 34), cy + math.sin(ang) * (r - 34)
    d.line([cx, cy, nx, ny], fill=(255, 255, 255, 255), width=9)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 255, 255, 255))
    img.alpha_composite(lay)
    pop_text(img, (cx, cy - r - 38), name + "'S SCORE", F_NUM, 34, ncol, stroke=4, sfill=(10, 10, 30))
    pop_text(img, (cx, cy + 50), str(int(round(score))), F_NUM, 70, score_col(score), scale=1 + 0.12 * glow, stroke=7, sfill=(10, 10, 30))

def rate_tag(img, cx, cy, txt, col, k):
    if k < 0.03: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 150 * k, 40 * k
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=int(20 * k), fill=col + (255,))
    img.alpha_composite(lay)
    pop_text(img, (cx, cy), txt, F_NUM, 44, (15, 15, 35), scale=k)

def house(img, cx, cy, s, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 110 * s, 100 * s
    d.polygon([(cx - w - 20 * s, cy - h * 0.2), (cx, cy - h * 1.25), (cx + w + 20 * s, cy - h * 0.2)], fill=(200, 70, 80))
    d.rectangle([cx - w, cy - h * 0.2, cx + w, cy + h], fill=(250, 236, 210))
    d.rectangle([cx - 24 * s, cy + h * 0.3, cx + 24 * s, cy + h], fill=(120, 70, 50))
    for wx in (-70, 70):
        d.rectangle([cx + (wx - 22) * s, cy + 0 * s, cx + (wx + 22) * s, cy + 40 * s], fill=(255, 214, 90))
    d.rectangle([cx + 50 * s, cy - h * 1.05, cx + 76 * s, cy - h * 0.6], fill=(150, 60, 70))
    img.alpha_composite(lay)
    pop_text(img, (cx, cy + h + 40 * s), "$300K LOAN", F_NUM, 40, GOLD, stroke=5, sfill=(30, 20, 10))
    pop_text(img, (cx, cy - h * 1.25 - 34 * s), "SAME HOUSE", F_NUM, 32, WHITE, stroke=4, sfill=(10, 10, 30))

# ---------- interest towers ----------
TB = 925; TMAX = 175; TW = 92
NI, TI = 347_515, 455_152
def cum_int(r, yrs, P=300_000):
    # cumulative interest paid after yrs years (amortising 30-yr loan), fractional years interpolated
    i = r / 12; pm = P * i / (1 - (1 + i) ** -360); m = yrs * 12
    k = int(m); bal_k = P * (1 + i) ** k - pm * ((1 + i) ** k - 1) / i
    paid = pm * k - (P - bal_k)
    return paid + (m - k) * bal_k * i
def tower(img, cx, val, col, label_k, extra=0.0):
    """val: interest so far; extra: red part on top (Theo's extra vs Nora)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hh = TMAX * val / TI
    d.rounded_rectangle([cx - TW, TB - hh, cx + TW, TB], radius=14, fill=col + (235,))
    for yb in range(int(TB - 30), int(TB - hh), -30):   # stacked-bill stripes
        d.line([cx - TW + 10, yb, cx + TW - 10, yb], fill=(255, 255, 255, 60), width=3)
    if extra > 0:
        eh = TMAX * extra / TI
        d.rounded_rectangle([cx - TW, TB - hh, cx + TW, TB - hh + eh], radius=14, fill=(230, 55, 75, 255))
    img.alpha_composite(lay)
    if label_k > 0.02:
        pop_text(img, (cx, TB - hh - 34), money(val), F_NUM, 46, WHITE, scale=label_k, stroke=6, sfill=(10, 10, 30))
    if extra > 1000:
        eh = TMAX * extra / TI
        pop_text(img, (cx, TB - hh + eh / 2), "+${}K".format(int(extra // 1000)), F_NUM, 36, WHITE, stroke=5, sfill=(90, 0, 20))

NXC, TXC = 282, 797
def stage(img, t, st):
    gauge(img, 190, 470, 120, st.get("ns", 760), "NORA", NORA, st.get("ng", 0.0))
    gauge(img, 890, 470, 120, st.get("ts", 620), "THEO", THEO, st.get("tg", 0.0))
    house(img, 540, 470, 1.0, t)
    rate_tag(img, 190, 605, "6.0% RATE", (120, 235, 160), st.get("nr", 0.0))
    rate_tag(img, 890, 605, "7.5% RATE", (255, 140, 120), st.get("tr", 0.0))
    yrs = st.get("yrs", 30)
    if st.get("towers", 1.0) > 0.02:
        nv, tv = cum_int(0.06, yrs), cum_int(0.075, yrs)
        tower(img, NXC, nv, (230, 130, 70), st.get("lab", 1.0))
        tower(img, TXC, tv, (50, 160, 200), st.get("lab", 1.0), extra=(tv - nv) if st.get("red", 1.0) > 0.5 else 0)
        pop_text(img, (540, 735), "INTEREST", F_NUM, 36, (200, 200, 240), stroke=4, sfill=(10, 10, 30))
        pop_text(img, (540, 775), "PAID", F_NUM, 36, (200, 200, 240), stroke=4, sfill=(10, 10, 30))
        if st.get("year_ctr", False):
            pop_text(img, (540, 830), f"YEAR {int(round(yrs))}", F_NUM, 44, GOLD, stroke=5, sfill=(30, 20, 10))
    if st.get("pm", 0.0) > 0.02:
        k = st["pm"]
        pop_text(img, (190, 665), "$1,799/MO", F_NUM, 40, (255, 200, 150), scale=k, stroke=5, sfill=(10, 10, 30))
        pop_text(img, (890, 665), "$2,098/MO", F_NUM, 40, (150, 225, 255), scale=k, stroke=5, sfill=(10, 10, 30))
        pop_text(img, (540, 890), "+$299/MO", F_NUM, 46, SOFTRED, scale=k, stroke=6, sfill=(40, 0, 10))

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 100), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(40, 10, 70))
    if sub:
        pop_text(img, (W / 2, 205), sub, F_NUM, 46, sub_col, stroke=5, sfill=(20, 10, 50))

FULL = dict(nr=1.0, tr=1.0, pm=1.0)
def sc_hook(img, t):
    headline(img, t, "SAME HOUSE. THEO PAYS +$107K")
    stage(img, t, dict(pm=0.0))
def sc_huh(img, t):
    headline(img, t, "SAME HOUSE. THEO PAYS +$107K")
    stage(img, t, dict(pm=0.0))
def sc_score(img, t):
    headline(img, t, "THE DIFFERENCE: 3 DIGITS", GOLD)
    stage(img, t, dict(pm=0.0, ng=clamp(1 - abs(t - tok("score", 1) - 0.3) / 0.5), nr=kpop(tok("score", 2), t),
                       tg=clamp(1 - abs(t - tok("score", 4) - 0.3) / 0.5), tr=kpop(tok("score", 5), t)))
def sc_only(img, t):
    headline(img, t, "\"ONLY\" 1.5% MORE", SOFTRED)
    stage(img, t, dict(nr=1.0, tr=1.0, pm=0.0))
def sc_month(img, t):
    headline(img, t, "SAME LOAN. 30 YEARS.", GOLD)
    t0 = tok("month", 4); t1 = SEG["month"]["end"] + 0.1
    yrs = 1 + 29 * ease_out((t - t0) / (t1 - t0)) if t > t0 else 1
    stage(img, t, dict(nr=1.0, tr=1.0, pm=kpop(tok("month", 1), t), yrs=yrs, year_ctr=True, lab=1.0))
def sc_fix(img, t):
    headline(img, t, "PAY ON TIME + LOW CARD BALANCES", MINT)
    t0 = seg_start("fix"); t1 = SEG["fix"]["end"]
    ts = 620 + 140 * ease_out((t - tok("fix", 4)) / 0.9) if t > tok("fix", 4) else 620
    stage(img, t, dict(FULL, ts=ts, tg=0.6 if t > tok("fix", 4) else 0.0))
def sc_punch(img, t):
    headline(img, t, "3 DIGITS = 6 DIGITS", SOFTRED)
    stage(img, t, dict(FULL))
    k = kpop(tok("punch", 2), t)
    if k > 0.03:
        d = ImageDraw.Draw(img)
        bx, by = 540, 850
        d.rounded_rectangle([bx - 330 * k, by - 70 * k, bx + 330 * k, by + 70 * k], radius=int(34 * k), fill=WHITE, outline=SOFTRED, width=max(2, int(7 * k)))
        pop_text(img, (bx, by), "620 = -$107,637", F_NUM, 64, (200, 40, 60), scale=k)
def sc_q(img, t):
    headline(img, t, "")
    stage(img, t, dict(FULL))
    k = ease_back((t - seg_start("q")) / 0.35)
    if k > 0.03:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([W / 2 - 440 * k, 620 - 250 * k, W / 2 + 440 * k, 620 + 250 * k], radius=int(40 * k), fill=WHITE, outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 465), "FIX YOUR SCORE", F_NUM, 88, (20, 140, 90), scale=k)
        pop_text(img, (W / 2, 565), "OR", F_NUM, 56, (20, 30, 70), scale=k)
        pop_text(img, (W / 2, 665), "BUY NOW?", F_NUM, 96, (200, 50, 80), scale=k)
        pop_text(img, (W / 2, 775), "TELL US IN THE COMMENTS", F_NUM, 44, (20, 30, 70), scale=k)

SCENES = {"hook": sc_hook, "huh": sc_huh, "score": sc_score, "only": sc_only, "month": sc_month,
          "fix": sc_fix, "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "smile", "point_up", "smile"), "huh": ("shrug", "worried", "idle", "smile"),
         "score": ("idle", "worried", "point_up", "smile"), "only": ("shrug", "smug", "idle", "smile"),
         "month": ("idle", "worried", "marker", "smile"), "fix": ("idle", "smile", "point_up", "smile"),
         "punch": ("facepalm", "worried", "shrug", "smile"), "q": ("idle", "smile", "point_up", "smile"),
         "loop": ("shrug", "worried", "idle", "smile")}
CY = 1215
def crown(img, cx, cy, s, k):
    if k < 0.03: return
    d = ImageDraw.Draw(img)
    hy = cy - 115 * s; yb = hy - 64 * s * 1.5 - 8; w = 62 * s * k; h = 52 * s * k
    pts = [(cx - w, yb), (cx - w, yb - h), (cx - w / 2, yb - h * 0.55), (cx, yb - h * 1.15), (cx + w / 2, yb - h * 0.55), (cx + w, yb - h), (cx + w, yb)]
    d.polygon(pts, fill=GOLD, outline=GOLD_D)
    for px in (-w, 0, w):
        d.ellipse([cx + px - 8 * k, yb - h * (1.15 if px == 0 else 1.0) - 8 * k, cx + px + 8 * k, yb - h * (1.15 if px == 0 else 1.0) + 8 * k], fill=(255, 90, 120))


def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("N", NXC, NORA, np_, nm), ("T", TXC, THEO, tp, tm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.0 if who == spk else 0.95
        cy = CY + (0 if who == spk else 12)
        person(img, cx, cy, sc, col, who, t, talk=talking, pose=pose, mood=mood)
        if who == "N" and s["scene"] in ("month", "fix", "punch", "q"):
            crown(img, cx, cy, sc, kpop(tok("month", 4), t) if s["scene"] == "month" else 1.0)
GROUPS = []
for s in TM["segments"]:
    cur = []
    for tk in s["tokens"]:
        cur.append(tk)
        chars = sum(len(x["text"]) for x in cur)
        if chars >= 11 or tk["text"][-1] in ".?!,:" or len(cur) == 3:
            GROUPS.append((s["spk"], cur)); cur = []
    if cur: GROUPS.append((s["spk"], cur))
_G = []
for i, (spk, grp) in enumerate(GROUPS):
    end = GROUPS[i + 1][1][0]["start"] if i + 1 < len(GROUPS) else grp[-1]["end"] + 0.5
    _G.append((0.0 if i == 0 else grp[0]["start"], min(end, grp[-1]["end"] + 0.6), spk, grp))
GROUPS = _G

CAP_Y = 1450
def draw_captions(img, t):
    for gs, ge, spk, toks in GROUPS:
        if gs <= t < ge: break
    else:
        return
    f = font(F_CAP, 90)
    widths = [f.getbbox(tk["text"], stroke_width=12)[2] - f.getbbox(tk["text"], stroke_width=12)[0] for tk in toks]
    space = 48
    lines, line, lw = [], [], 0
    for i, w_ in enumerate(widths):
        if line and lw + space + w_ > 900:
            lines.append(line); line, lw = [], 0
        lw += (space if line else 0) + w_; line.append(i)
    lines.append(line)
    gk = 1.0 if gs <= 0 else ease_back((t - gs) / 0.18)
    for li, ln in enumerate(lines):
        tw_ = sum(widths[i] for i in ln) + space * (len(ln) - 1)
        x = W / 2 - tw_ / 2; y = CAP_Y + (li - (len(lines) - 1) / 2) * 108
        for i in ln:
            tk = toks[i]
            active = tk["start"] <= t < tk["end"] + 0.05 or (i == len(toks) - 1 and t >= tk["start"])
            col = (60, 230, 120) if ("$" in tk["text"] or "%" in tk["text"]) else (YEL if active else WHITE)
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 90, col, scale=gk * (1.05 if active else 1.0), stroke=12, sfill=(20, 16, 40))
            x += widths[i] + space
def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=GOLD)
    c = (190, 196, 235)
    lines = ["Example rates for illustration (760 vs 620 score); real rates vary.",
             "$300K, 30-yr fixed; principal + interest only, no taxes,",
             "insurance, PMI or fees. Fictional characters.",
             "Illustration only. Not financial advice."]
    for i, ln in enumerate(lines):
        d.text((W / 2, 1600 + i * 33), ln, font=font(F_MED, 26), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    SCENES[s["scene"]](img, t)
    draw_cast(img, t)
    draw_captions(img, t)
    draw_ui(img, t)
    return img.convert("RGB")

if __name__ == "__main__":
    if PREVIEW:
        for tt in PREVIEW:
            frame(tt).save(os.path.join(HERE, f"prev_{tt:05.2f}.png"))
        sys.exit()
    out = os.path.join(HERE, "video_noaudio.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0: print("frame", i, "/", NF, flush=True)
    p.stdin.close(); p.wait()
    print("done", out)
