"""WHO WINS? #11: same $350K mortgage, +$200/mo extra vs bill only. 1080x1920 @30fps. Midnight-teal suburb: interest bars + balance chart."""
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
        side = -1 if who == "T" else 1
        arm(sh_r if side > 0 else sh_l, (cx + side * 150 * s, cy - 190 * s + wv * 0.3))
        arm(sh_l if side > 0 else sh_r, (cx - side * 120 * s, cy + 120 * s))
    elif pose == "shrug":
        arm(sh_l, (cx - 175 * s, cy - 70 * s + wv * 0.4)); arm(sh_r, (cx + 175 * s, cy - 70 * s - wv * 0.4))
    elif pose == "cheer":
        arm(sh_l, (cx - 140 * s, cy - 165 * s + wv * 0.5)); arm(sh_r, (cx + 140 * s, cy - 165 * s - wv * 0.5))
    elif pose == "facepalm":
        arm(sh_l, (cx - 120 * s, cy + 120 * s)); arm(sh_r, (cx + 20 * s, cy - 110 * s))
    elif pose == "marker":      # Nora holding a marker towards the board
        side = 1 if who == "N" else -1
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

# ---------- background: midnight-teal suburb, crescent moon, two identical houses, picket fence ----------
sys.path.insert(0, HERE)
from script import amort
PMT, MT, IT, HT = amort(0)
_, MN, IN, HN = amort(200)
SAVED = IT - IN

yy, xx = np.mgrid[0:H, 0:W]
GROUND = 1060
def house(d, cx, base, s, body, roof, lit=True):
    w, h = 150 * s, 120 * s
    d.rectangle([cx - w, base - h, cx + w, base], fill=body)
    d.polygon([(cx - w - 24 * s, base - h), (cx, base - h - 110 * s), (cx + w + 24 * s, base - h)], fill=roof)
    d.rectangle([cx + 60 * s, base - h - 95 * s, cx + 90 * s, base - h - 40 * s], fill=roof)   # chimney
    win = (255, 214, 120, 255) if lit else (60, 70, 110, 255)
    for wx in (-95, 45):
        d.rectangle([cx + wx * s, base - h + 25 * s, cx + (wx + 50) * s, base - h + 70 * s], fill=win)
    d.rectangle([cx - 20 * s, base - 70 * s, cx + 20 * s, base], fill=(40, 30, 50, 255))

def make_bg():
    top = np.array((6, 22, 44), np.float32); bot = np.array((14, 70, 92), np.float32)
    f = np.clip(yy / GROUND, 0, 1)[..., None] ** 1.3
    img = top * (1 - f) + bot * f
    r = np.sqrt((xx - 150) ** 2 + (yy - 250) ** 2)
    img += (np.clip(1 - r / 420, 0, 1) ** 2)[..., None] * np.array((40, 70, 70), np.float32)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(26)
    for _ in range(70):
        x, y = rng.integers(0, W), rng.integers(0, 900); r_ = int(rng.integers(1, 3))
        d.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(220, 255, 250, int(rng.integers(60, 180))))
    # crescent moon (top-left, behind the headline glow)
    d.ellipse([90, 190, 210, 310], fill=(235, 250, 220, 120))
    d.ellipse([122, 178, 242, 298], fill=(0, 0, 0, 0))
    # far rooftops silhouette
    x = 0
    while x < W:
        w_ = int(rng.integers(90, 160)); h_ = int(rng.integers(40, 110))
        d.rectangle([x, GROUND - 110 - h_, x + w_, GROUND - 100], fill=(10, 40, 60, 255))
        d.polygon([(x - 10, GROUND - 110 - h_), (x + w_ / 2, GROUND - 160 - h_), (x + w_ + 10, GROUND - 110 - h_)], fill=(10, 40, 60, 255))
        if rng.random() < 0.6:
            wx = x + int(rng.integers(15, max(16, w_ - 30)))
            d.rectangle([wx, GROUND - 90 - h_, wx + 16, GROUND - 74 - h_], fill=(255, 210, 120, 140))
        x += w_ + int(rng.integers(5, 30))
    # lawn
    d.rectangle([0, GROUND - 100, W, H], fill=(16, 58, 58, 255))
    for j in range(0, 12):
        y = GROUND - 100 + (j / 11) ** 1.6 * (H - GROUND + 100)
        d.line([0, y, W, y], fill=(12, 48, 50, 255), width=2)
    # picket fence
    for x in range(-10, W, 46):
        d.polygon([(x, GROUND - 30), (x + 16, GROUND - 52), (x + 32, GROUND - 30), (x + 32, GROUND + 30), (x, GROUND + 30)], fill=(200, 225, 220, 70))
    d.rectangle([0, GROUND - 14, W, GROUND - 4], fill=(200, 225, 220, 70))
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (90, 240, 170); SOFTRED = (255, 96, 104)
CORAL = (255, 128, 110); CARD = (8, 30, 46); LINE = (90, 190, 190)
def money(v): return "${:,.0f}".format(v)
def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0
NXC, TXC = 282, 797     # Nora left, Theo right

def card(img, box, fill=CARD, outline=LINE, alpha=230):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(box, radius=30, fill=fill + (alpha,), outline=outline + (255,), width=5)
    img.alpha_composite(lay)

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 96), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(4, 30, 40))
    if sub:
        pop_text(img, (W / 2, 205), sub, F_NUM, 48, sub_col, stroke=5, sfill=(4, 20, 30))

def two_houses(img, t, y=560, s=1.0, theo_sign=None, nora_sign=None):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    house(d, NXC, y, s, (240, 236, 220, 255), (210, 90, 70, 255))
    house(d, TXC, y, s, (240, 236, 220, 255), (210, 90, 70, 255))
    img.alpha_composite(lay)
    for cx, sg in ((NXC, nora_sign), (TXC, theo_sign)):
        if sg:
            txt, col, k = sg
            if k > 0.05:
                pop_text(img, (cx, y + 70), txt, F_NUM, 50, col, scale=k, stroke=6, sfill=(4, 20, 30))

def sc_hook(img, t):
    headline(img, t, "SAME MORTGAGE. ONE PAYS $200 EXTRA.", WHITE)
    two_houses(img, t, y=470, s=0.85)
    pop_text(img, (NXC, 300), "+$200/mo", F_NUM, 64, MINT, stroke=6, sfill=(4, 20, 30))
    pop_text(img, (TXC, 300), "+$0", F_NUM, 64, (200, 220, 230), stroke=6, sfill=(4, 20, 30))
    pop_text(img, (W / 2, 690), "$108K SAVED", F_NUM, 150, MINT, scale=1 + 0.02 * math.sin(t * 6), stroke=9, sfill=(4, 30, 30))
    pop_text(img, (W / 2, 830), "+ 6 YEARS SOONER", F_NUM, 66, YEL, stroke=6, sfill=(4, 20, 30))

def sc_huh(img, t):
    headline(img, t, "THEO: \"$200? THAT'S NOTHING.\"", (150, 225, 255))
    k = 1 + 0.03 * math.sin(t * 8)
    pop_text(img, (W / 2, 470), "$200", F_NUM, 260, WHITE, scale=k, stroke=10, sfill=(4, 20, 30))
    pop_text(img, (W / 2, 650), "A MONTH", F_NUM, 80, (150, 225, 255), stroke=6, sfill=(4, 20, 30))

def sc_same(img, t):
    headline(img, t, "SAME LOAN FOR BOTH", GOLD)
    tiles = [("LOAN", "$350,000", tok("same", 0)), ("FIXED FOR", "30 YEARS", tok("same", 1)),
             ("EXAMPLE RATE", "6.5%", tok("same", 2))]
    for i, (a, b_, t0) in enumerate(tiles):
        k = kpop(t0, t)
        if k < 0.05: continue
        y = 330 + i * 175
        card(img, [W / 2 - 400 * k, y - 75 * k, W / 2 + 400 * k, y + 75 * k])
        pop_text(img, (W / 2 - 360 * k, y), a, F_NUM, 44, (170, 220, 220), scale=k, anchor_c=False)
        pop_text(img, (W / 2 + 360 * k - tw(b_, F_NUM, 84) * k / 2, y), b_, F_NUM, 84, GOLD if i == 2 else WHITE, scale=k)
    k = kpop(tok("same", 2) + 0.5, t)
    if k > 0.05:
        pop_text(img, (W / 2, 860), f"BILL: {money(PMT)}/mo", F_NUM, 62, WHITE, scale=k, stroke=6, sfill=(4, 20, 30))

def bars(img, t, kt, kn, show_n_label=True):
    """interest bars: Theo vs Nora (height ~ interest)"""
    d = ImageDraw.Draw(img)
    base, top = 860, 430; Hm = base - top
    card(img, [60, 250, 1020, 905])
    d = ImageDraw.Draw(img)
    for cx, v, k, col, nm in ((TXC, IT, kt, CORAL, "THEO"), (NXC, IN, kn, MINT, "NORA")):
        if k <= 0.01: continue
        h = Hm * v / IT * k
        d.rounded_rectangle([cx - 140, base - h, cx + 140, base], radius=18, fill=col)
        pop_text(img, (cx, base - h - 50), money(v * k), F_NUM, 72, col, stroke=6, sfill=(4, 20, 30))
        pop_text(img, (cx, base - 40), nm, F_NUM, 50, (10, 30, 40), scale=min(1, k * 2))
    pop_text(img, (W / 2, 286), "TOTAL INTEREST PAID", F_NUM, 46, (170, 220, 220))

def sc_theo(img, t):
    headline(img, t, "THEO PAYS EXACTLY THE BILL", CORAL)
    kt = ease_out((t - seg_start("theo") - 0.2) / 1.6)
    bars(img, t, kt, 0)

def sc_nora(img, t):
    headline(img, t, "NORA: +$200 → STRAIGHT TO THE BALANCE", MINT)
    kn = ease_out((t - seg_start("nora") - 0.2) / 1.4)
    bars(img, t, 1.0, kn)
    k = kpop(tok("nora", 3), t)
    if k > 0.05:
        pop_text(img, (W / 2, 470), f"-{money(SAVED)}", F_NUM, 70, YEL, scale=k, stroke=6, sfill=(4, 20, 30))

# balance-over-time area chart
CX0, CX1, CY0, CY1 = 120, 980, 330, 820
def chart(img, t, prog, show_gap=0.0):
    card(img, [50, 250, 1030, 905])
    d = ImageDraw.Draw(img)
    pop_text(img, (W / 2, 286), "MORTGAGE LEFT TO PAY", F_NUM, 46, (170, 220, 220))
    for yr in (0, 10, 20, 30):
        x = CX0 + (CX1 - CX0) * yr / 30
        d.line([x, CY0, x, CY1], fill=(40, 80, 90), width=2)
        pop_text(img, (x, CY1 + 40), f"YR {yr}", F_MED, 30, (150, 200, 200))
    d.line([CX0, CY1, CX1, CY1], fill=(150, 200, 200), width=4)
    m_end = int(360 * prog)
    for hist, col, w in ((HT, CORAL, 10), (HN, MINT, 10)):
        pts = []
        for m in range(0, min(m_end, len(hist) - 1) + 1, 3):
            pts.append((CX0 + (CX1 - CX0) * m / 360, CY1 - (CY1 - CY0) * hist[m] / 350000))
        if m_end >= len(hist) - 1:
            pts.append((CX0 + (CX1 - CX0) * (len(hist) - 1) / 360, CY1))
        if len(pts) > 1:
            d.line(pts, fill=col, width=w, joint="curve")
            d.ellipse([pts[-1][0] - 14, pts[-1][1] - 14, pts[-1][0] + 14, pts[-1][1] + 14], fill=col)
    pop_text(img, (CX0 + 60, CY0 - 18), "$350K", F_MED, 34, (150, 200, 200))
    xn = CX0 + (CX1 - CX0) * MN / 360; xt = CX1
    if m_end >= MN:
        k = kpop(seg_start("nora") + 0.0, t) if t < seg_start("me") else 1.0
        pop_text(img, (xn - 190, CY1 - 90), "PAID OFF!", F_NUM, 46, MINT, stroke=5, sfill=(4, 20, 30))
        pop_text(img, (xn - 190, CY1 - 44), "23 YRS 10 MO", F_MED, 32, MINT, stroke=4, sfill=(4, 20, 30))
    if show_gap > 0.03:
        y = CY0 + 90
        d.line([xn, y, xn + (xt - xn) * show_gap, y], fill=YEL, width=8)
        d.line([xn, y - 22, xn, y + 22], fill=YEL, width=8)
        if show_gap > 0.95: d.line([xt, y - 22, xt, y + 22], fill=YEL, width=8)
        pop_text(img, ((xn + xt) / 2 - 50, y - 60), "+6 YEARS", F_NUM, 64, YEL, scale=show_gap, stroke=6, sfill=(4, 20, 30))

def sc_me(img, t):
    headline(img, t, "THEO: \"AND ME?\"", (150, 225, 255))
    chart(img, t, MN / 360)

def nora_prog(t):
    t0 = tok("nora", 3); t1 = SEG["nora"]["end"]
    return clamp((t - t0 + 0.3) / max(0.5, t1 - t0 + 0.2)) * MN / 360

def sc_nora2(img, t):
    sc_nora(img, t)

def sc_more(img, t):
    headline(img, t, "SAME HOUSE. 6 MORE YEARS OF BILLS.", CORAL)
    p = MN / 360 + (1 - MN / 360) * ease_out((t - seg_start("more")) / 1.0)
    chart(img, t, p, show_gap=ease_out((t - seg_start("more") - 0.3) / 0.8))

def sc_punch(img, t):
    headline(img, t, f"NORA KEEPS {money(SAVED)}", MINT)
    k = kpop(tok("punch", 2), t)
    # retirement-home sign over Theo's side, paid-off house for Nora
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    house(d, NXC, 640, 0.95, (240, 236, 220, 255), (210, 90, 70, 255))
    img.alpha_composite(lay)
    pop_text(img, (NXC, 340), "PAID OFF", F_NUM, 64, MINT, stroke=6, sfill=(4, 20, 30))
    if k > 0.05:
        d = ImageDraw.Draw(img)
        d.rectangle([TXC - 10, 700 - 330 * k, TXC + 10, 860], fill=(120, 90, 70))
        d.rounded_rectangle([TXC - 230 * k, 420 - 120 * k, TXC + 230 * k, 420 + 120 * k], radius=int(26 * k), fill=(236, 226, 196), outline=(140, 100, 70), width=max(2, int(8 * k)))
        pop_text(img, (TXC, 420 - 55 * k), "SUNSET", F_NUM, 60, (130, 70, 60), scale=k)
        pop_text(img, (TXC, 420 + 15 * k), "RETIREMENT", F_NUM, 50, (60, 60, 80), scale=k)
        pop_text(img, (TXC, 420 + 70 * k), "HOME", F_NUM, 50, (60, 60, 80), scale=k)
        pop_text(img, (TXC, 640), "PAYMENT DUE", F_NUM, 50, SOFTRED, scale=k, stroke=5, sfill=(4, 20, 30))

def sc_q(img, t):
    headline(img, t, "")
    k = ease_back((t - seg_start("q")) / 0.35)
    if k > 0.03:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([W / 2 - 460 * k, 560 - 280 * k, W / 2 + 460 * k, 560 + 280 * k], radius=int(40 * k), fill=WHITE, outline=MINT, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 560 - 190 * k), "YOUR $200:", F_NUM, 70, (20, 40, 60), scale=k)
        pop_text(img, (W / 2, 560 - 60 * k), "PAY EXTRA", F_NUM, 104, (20, 150, 100), scale=k)
        pop_text(img, (W / 2, 560 + 50 * k), "OR INVEST IT?", F_NUM, 92, (220, 80, 70), scale=k)
        pop_text(img, (W / 2, 560 + 180 * k), "TELL US IN THE COMMENTS", F_NUM, 46, (20, 40, 60), scale=k)

def sc_nora_full(img, t):
    # bars first, then the chart once Nora says "Done in..."
    if t < tok("nora", 3) - 0.1:
        sc_nora(img, t)
    else:
        headline(img, t, "NORA: DONE IN UNDER 24 YEARS", MINT)
        chart(img, t, nora_prog(t))

SCENES = {"hook": sc_hook, "huh": sc_huh, "same": sc_same, "theo": sc_theo, "nora": sc_nora_full, "me": sc_me,
          "more": sc_more, "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "worried", "point_up", "smile"), "huh": ("shrug", "smug", "idle", "smile"),
         "same": ("idle", "smile", "point_up", "smile"), "theo": ("idle", "smug", "marker", "smile"),
         "nora": ("idle", "smile", "point_up", "smile"), "me": ("shrug", "worried", "idle", "smile"),
         "more": ("idle", "worried", "point_up", "smile"), "punch": ("facepalm", "worried", "cheer", "smile"),
         "q": ("idle", "smile", "point_up", "smile"), "loop": ("shrug", "worried", "idle", "smile")}
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
        if who == "N" and s["scene"] in ("punch", "q"):
            crown(img, cx, cy, sc, kpop(seg_start("punch"), t) if s["scene"] == "punch" else 1.0)

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
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 90, col, scale=gk * (1.05 if active else 1.0), stroke=12, sfill=(4, 18, 26))
            x += widths[i] + space
def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=GOLD)
    band = Image.new('RGBA', (W, 160), (2, 18, 26, 175)); img.alpha_composite(band, (0, 1572)); d = ImageDraw.Draw(img)
    c = (190, 196, 235)
    lines = ["$350K 30-yr fixed at an EXAMPLE 6.5% rate. Principal + interest only",
             "(no taxes/insurance). Nora's extra $200/mo goes to principal; assumes",
             "no prepayment penalty. Investing the $200 instead may also make sense.",
             "Fictional characters. Illustration only. Not financial advice."]
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
