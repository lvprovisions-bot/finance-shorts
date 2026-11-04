"""WHO WINS? #10: same $30K 401(k), rollover vs cash-out. 1080x1920 @30fps. Dusk harbour: coin tower vs sinking jet ski."""
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

# ---------- background: dusk harbour, moon + stars, sea with ripples, wooden pier ----------
yy, xx = np.mgrid[0:H, 0:W]
HORIZON, DECK = 730, 1085
def make_bg():
    top = np.array((12, 10, 66), np.float32); bot = np.array((96, 34, 120), np.float32)
    f = np.clip(yy / HORIZON, 0, 1)[..., None]
    img = top * (1 - f) + bot * f
    r = np.sqrt((xx - 900) ** 2 + (yy - 330) ** 2)
    img += (np.clip(1 - r / 520, 0, 1) ** 2)[..., None] * np.array((60, 50, 90), np.float32)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(24)
    for _ in range(90):
        x, y = rng.integers(0, W), rng.integers(0, HORIZON - 80); r_ = int(rng.integers(1, 4))
        d.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(255, 255, 255, int(rng.integers(70, 200))))
    # distant hills + town lights
    pts = [(0, HORIZON)]
    for i in range(0, 12):
        pts.append((i * 100, HORIZON - 26 - 26 * abs(math.sin(i * 1.4))))
    pts.append((W, HORIZON)); d.polygon(pts, fill=(34, 18, 78, 255))
    for i in range(26):
        x = rng.integers(0, W); y = HORIZON - rng.integers(4, 24)
        d.rectangle([x, y, x + 4, y + 4], fill=(255, 216, 120, 220))
    # sea
    for y in range(HORIZON, DECK):
        k = (y - HORIZON) / (DECK - HORIZON)
        c = (int(lerp(38, 16, k)), int(lerp(30, 40, k)), int(lerp(120, 96, k)))
        d.line([0, y, W, y], fill=c + (255,))
    for _ in range(70):
        y = rng.integers(HORIZON + 6, DECK - 8); x = rng.integers(0, W); L = int(20 + 90 * (y - HORIZON) / 355)
        d.line([x, y, x + L, y], fill=(120, 130, 220, 70), width=2)
    # pier deck
    d.rectangle([0, DECK, W, H], fill=(52, 30, 70, 255))
    for j in range(0, 11):
        y = DECK + (j / 10) ** 1.5 * (H - DECK)
        d.line([0, y, W, y], fill=(34, 18, 52, 255), width=3)
    d.rectangle([0, DECK - 8, W, DECK + 6], fill=(92, 58, 96, 255))
    for x in (60, 1020):
        d.rounded_rectangle([x - 16, DECK - 62, x + 16, DECK + 20], radius=8, fill=(84, 50, 86, 255))
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 85, 100)
CARD = (20, 16, 62); LINE = (130, 125, 200)
def money(v): return "${:,.0f}".format(v)
def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0
NXC, TXC = 282, 797     # Nora left, Theo right
P0, FV = 30000, 30000 * 1.07 ** 30

def card(img, box, fill=CARD, outline=LINE, alpha=225):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(box, radius=30, fill=fill + (alpha,), outline=outline + (255,), width=5)
    img.alpha_composite(lay)

# coin tower standing in the sea; height proportional to the money
TOWER_BASE, TOWER_MAX = 900, 515   # 228K = 515 px
def tower(img, cx, v, label=True):
    d = ImageDraw.Draw(img)
    h = TOWER_MAX * v / FV
    cw = 118; ch = 30
    y = TOWER_BASE
    d.ellipse([cx - cw - 30, TOWER_BASE - 18, cx + cw + 30, TOWER_BASE + 26], fill=(14, 12, 60))
    i = 0
    while y > TOWER_BASE - h:
        c = GOLD if i % 2 else (240, 176, 32)
        d.rectangle([cx - cw, y - ch, cx + cw, y], fill=c)
        d.ellipse([cx - cw, y - 9, cx + cw, y + 9], fill=c)
        d.ellipse([cx - cw, y - ch - 9, cx + cw, y - ch + 9], fill=(255, 222, 110), outline=GOLD_D)
        y -= ch; i += 1
    if label:
        pop_text(img, (cx, y - 58), money(v), F_NUM, 76, MINT, stroke=6, sfill=(16, 10, 50))

def jetski(img, cx, wy, s=1.0, sink=0.0, t=0.0, rust=0.0):
    """Jet ski floating on water line wy; sink 0..1 slides it under."""
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bob = math.sin(t * 3.5) * 6
    tilt = sink * 26
    dy = bob + sink * 190
    def P(x, y):
        a = math.radians(tilt); x2 = x * math.cos(a) - y * math.sin(a); y2 = x * math.sin(a) + y * math.cos(a)
        return (cx + x2 * s, wy + dy + y2 * s)
    hull = (40, 200, 240) if rust < 0.5 else (120, 150, 160)
    stripe = (255, 90, 110) if rust < 0.5 else (150, 110, 110)
    d.polygon([P(-150, -58), P(90, -78), P(185, -34), P(120, 28), P(-135, 28)], fill=hull + (255,))     # short, tall hull
    d.polygon([P(-145, -30), P(130, -46), P(160, -24), P(-140, -8)], fill=stripe + (255,))
    d.rounded_rectangle([P(-120, -108)[0], P(-120, -108)[1], P(-20, -70)[0] + 10, P(-20, -70)[1]], radius=int(16 * s), fill=(30, 26, 60, 255))  # saddle
    d.line([P(30, -74), P(52, -152)], fill=(30, 26, 60, 255), width=max(2, int(18 * s)))      # steering post
    d.line([P(18, -158), P(92, -148)], fill=(30, 26, 60, 255), width=max(2, int(16 * s)))     # handlebars
    d.polygon([P(70, -84), P(120, -60), P(70, -60)], fill=(170, 230, 255, 255))               # windscreen
    # water mask: nothing shows below the water line
    arr = np.array(lay); arr[int(wy + 18):, :, 3] = 0
    lay = Image.fromarray(arr)
    img.alpha_composite(lay)
    d2 = ImageDraw.Draw(img)
    for i in range(-3, 4):
        x = cx + i * 66 * s
        d2.arc([x - 40, wy + 6, x + 40, wy + 30], 200, 340, fill=(180, 200, 255), width=4)

def bubbles(img, cx, wy, k, t):
    if k <= 0.01 or k >= 1: return
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for i in range(12):
        x = cx + rng.integers(-150, 150); ph = rng.random()
        y = wy + 16 - ((t * 110 + ph * 90) % 90)
        r_ = rng.integers(5, 14)
        d.ellipse([x - r_, y - r_, x + r_, y + r_], outline=(210, 230, 255), width=3)

def jar(img, cx, cy, s, col, name):
    """401(k) jar with coins"""
    if s < 0.05: return
    d = ImageDraw.Draw(img)
    w_, h_ = 165 * s, 175 * s
    d.rounded_rectangle([cx - w_, cy - h_, cx + w_, cy + h_], radius=int(44 * s), fill=(38, 40, 110), outline=(200, 210, 255), width=max(2, int(7 * s)))
    d.rounded_rectangle([cx - w_ * 0.72, cy - h_ - 26 * s, cx + w_ * 0.72, cy - h_ + 10 * s], radius=int(12 * s), fill=col)
    for i in range(5):
        y = cy + h_ - 34 * s - i * 34 * s
        d.rounded_rectangle([cx - w_ + 26 * s, y - 15 * s, cx + w_ - 26 * s, y + 15 * s], radius=int(14 * s), fill=GOLD if i % 2 else (240, 176, 32))
    pop_text(img, (cx, cy - h_ * 0.62), "401(k)", F_NUM, 60, WHITE, scale=s)
    pop_text(img, (cx, cy + h_ * 0.42), "$30K", F_NUM, 92, WHITE, scale=s, stroke=8, sfill=(40, 24, 70))
    pop_text(img, (cx, cy - h_ - 62 * s), name, F_NUM, 44, col, scale=s, stroke=4, sfill=(16, 10, 50))

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 96), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(40, 10, 70))
    if sub:
        pop_text(img, (W / 2, 205), sub, F_NUM, 48, sub_col, stroke=5, sfill=(20, 10, 50))

def arrow_down(img, cx, y, s=1.0, col=WHITE):
    d = ImageDraw.Draw(img)
    d.polygon([(cx - 28*s, y), (cx + 28*s, y), (cx + 28*s, y + 40*s), (cx + 62*s, y + 40*s), (cx, y + 94*s), (cx - 62*s, y + 40*s), (cx - 28*s, y + 40*s)], fill=col)

def sc_hook(img, t):
    headline(img, t, "SAME $30K 401(k). ONE CASHED OUT.", WHITE)
    pop_text(img, (W / 2, 330), "CASHED OUT $30K", F_NUM, 100, YEL, stroke=7, sfill=(16, 10, 50))
    arrow_down(img, W / 2, 398 + 8 * math.sin(t * 7))
    pop_text(img, (W / 2, 610), "-$228K", F_NUM, 220, SOFTRED, scale=1 + 0.02 * math.sin(t * 6), stroke=9, sfill=(30, 8, 40))
    pop_text(img, (W / 2, 790), "BY AGE 65", F_NUM, 56, WHITE, stroke=5, sfill=(16, 10, 50))

def sc_huh(img, t):
    headline(img, t, "THEO: \"IT'S MY MONEY!\"", (150, 225, 255))
    k = 1 + 0.03 * math.sin(t * 8)
    pop_text(img, (W / 2, 480), "$30,000", F_NUM, 210, MINT, scale=k, stroke=9, sfill=(10, 40, 40))
    pop_text(img, (W / 2, 640), "CASH! RIGHT NOW!", F_NUM, 72, WHITE, stroke=5, sfill=(16, 10, 50))

def sc_same(img, t):
    headline(img, t, "SAME JOB CHANGE", GOLD)
    k = kpop(seg_start("same"), t)
    jar(img, NXC, 590, 1.0 * k, NORA, "NORA, 35")
    jar(img, TXC, 590, 1.0 * k, THEO, "THEO, 35")

def sc_choice(img, t):
    headline(img, t, "SAME MONEY. TWO CHOICES.", GOLD)
    k1 = kpop(tok("choice", 1), t); k2 = kpop(tok("choice", 4), t)
    for cx, k, col, top, lines, big, bc in ((NXC, k1, NORA, "NORA", ("ROLLOVER", "TO NEW PLAN"), "TAX $0", MINT),
                                            (TXC, k2, THEO, "THEO", ("CASH OUT", "SPEND IT"), "TAX NOW", SOFTRED)):
        if k < 0.05: continue
        w_, h_ = 245 * k, 300 * k; cy = 580
        card(img, [cx - w_, cy - h_, cx + w_, cy + h_], outline=col)
        pop_text(img, (cx, cy - 225 * k), top, F_NUM, 58, col, scale=k)
        pop_text(img, (cx, cy - 110 * k), lines[0], F_NUM, 66, WHITE, scale=k)
        pop_text(img, (cx, cy - 35 * k), lines[1], F_NUM, 44, (205, 205, 240), scale=k)
        pop_text(img, (cx, cy + 130 * k), big, F_NUM, 82, bc, scale=k)

def sc_cut(img, t):
    headline(img, t, "THEO'S $30,000 PAYOUT", SOFTRED)
    d = ImageDraw.Draw(img)
    x0, x1 = 70, 1010; y0 = 280; bw = x1 - x0
    k1 = clamp((t - tok("cut", 1)) / 0.4); k2 = clamp((t - tok("cut", 3)) / 0.4)
    card(img, [x0 - 24, y0 - 26, x1 + 24, 800])
    d = ImageDraw.Draw(img)
    pct_left = 1 - 0.10 * k1 - 0.22 * k2
    d.rounded_rectangle([x0, y0, x1, y0 + 96], radius=16, fill=(50, 44, 100))
    d.rounded_rectangle([x0, y0, x0 + bw * pct_left, y0 + 96], radius=16, fill=MINT)
    if k1 > 0:
        d.rectangle([x0 + bw * pct_left, y0, x0 + bw * (pct_left + 0.10 * k1), y0 + 96], fill=(255, 150, 60))
    if k2 > 0:
        d.rectangle([x0 + bw * (pct_left + 0.10 * k1), y0, x0 + bw * (pct_left + 0.10 * k1 + 0.22 * k2), y0 + 96], fill=SOFTRED)
    left = 30000 - 3000 * k1 - 6600 * k2
    pop_text(img, (x0 + bw * pct_left / 2, y0 + 49), money(left), F_NUM, 66, (12, 40, 40))
    rows = [(tok("cut", 0), "10% IRS PENALTY", "-$3,000", (255, 170, 90)), (tok("cut", 3), "INCOME TAX (22%)", "-$6,600", SOFTRED)]
    for i, (t0, a, b_, c) in enumerate(rows):
        k = kpop(t0, t)
        if k < 0.05: continue
        y = y0 + 180 + i * 104
        pop_text(img, (x0 + 10, y), a, F_NUM, 50, WHITE, scale=k, anchor_c=False)
        pop_text(img, (x1 - 10 - tw(b_, F_NUM, 66) / 2, y), b_, F_NUM, 66, c, scale=k)
    k = kpop(tok("cut", 5), t)
    if k > 0.05:
        d = ImageDraw.Draw(img)
        d.line([x0, y0 + 368, x1, y0 + 368], fill=LINE, width=4)
        pop_text(img, (x0 + 10, y0 + 430), "THEO GETS", F_NUM, 56, WHITE, scale=k, anchor_c=False)
        pop_text(img, (x1 - 10 - tw("$20,400", F_NUM, 96) / 2, y0 + 430), "$20,400", F_NUM, 96, MINT, scale=k)

def sc_ski(img, t):
    headline(img, t, "THEO: \"STILL A JET SKI!\"", (150, 225, 255))
    k = kpop(tok("ski", 1), t)
    pop_text(img, (W / 2, 420), "$20,400", F_NUM, 150, MINT, stroke=7, sfill=(10, 40, 40))
    jetski(img, W / 2, 800, 1.5 * k, t=t)

def grow_v(t):
    t0 = seg_start("grow"); t1 = tok("grow", 4)
    p = clamp((t - t0) / max(0.3, t1 - t0))
    return p * 30, P0 * 1.07 ** (p * 30)

def sc_grow(img, t):
    yr, v = grow_v(t)
    headline(img, t, f"YEAR {int(yr)} · AGE {35 + int(yr)}", GOLD)
    tower(img, NXC, v)
    jetski(img, TXC, 860, 1.0, t=t, rust=yr / 30)
    if t > tok("grow", 5) - 0.1:
        pop_text(img, (TXC, 560), "?", F_NUM, 220, YEL, scale=kpop(tok("grow", 5), t), stroke=8, sfill=(40, 10, 70))

def sc_punch(img, t):
    headline(img, t, "$228K vs A SUNKEN JET SKI", SOFTRED)
    tower(img, NXC, FV)
    k = clamp((t - tok("punch", 1) + 0.25) / 1.0)
    jetski(img, TXC, 860, 1.0, sink=k, t=t, rust=1)
    bubbles(img, TXC, 860, k, t)
    pop_text(img, (TXC, 560), "$0", F_NUM, 200, SOFTRED, scale=kpop(tok("punch", 1), t), stroke=8, sfill=(30, 8, 40))

def sc_q(img, t):
    headline(img, t, "")
    tower(img, NXC, FV, label=True)
    k = ease_back((t - seg_start("q")) / 0.35)
    if k > 0.03:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([W / 2 - 450 * k, 530 - 260 * k, W / 2 + 450 * k, 530 + 260 * k], radius=int(40 * k), fill=WHITE, outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 530 - 170 * k), "WOULD YOU", F_NUM, 76, (20, 30, 70), scale=k)
        pop_text(img, (W / 2, 530 - 10 * k), "CASH OUT?", F_NUM, 130, (205, 40, 60), scale=k)
        pop_text(img, (W / 2, 530 + 150 * k), "TELL US IN THE COMMENTS", F_NUM, 50, (20, 30, 70), scale=k)

SCENES = {"hook": sc_hook, "huh": sc_huh, "same": sc_same, "choice": sc_choice, "cut": sc_cut, "ski": sc_ski,
          "grow": sc_grow, "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "worried", "point_up", "smile"), "huh": ("cheer", "smug", "idle", "smile"),
         "same": ("idle", "smile", "point_up", "smile"), "choice": ("point_up", "smug", "point_up", "smile"),
         "cut": ("idle", "worried", "marker", "smile"), "ski": ("cheer", "smug", "shrug", "smile"),
         "grow": ("idle", "smile", "cheer", "smile"), "punch": ("facepalm", "worried", "shrug", "smile"),
         "q": ("idle", "smile", "point_up", "smile"), "loop": ("facepalm", "worried", "idle", "smile")}
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
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 90, col, scale=gk * (1.05 if active else 1.0), stroke=12, sfill=(20, 16, 40))
            x += widths[i] + space
def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=GOLD)
    band = Image.new('RGBA', (W, 160), (12, 8, 30, 170)); img.alpha_composite(band, (0, 1572)); d = ImageDraw.Draw(img)
    c = (190, 196, 235)
    lines = ["Age 35 to 65, 7%/yr assumed (not guaranteed), no new deposits, before tax at 65.",
             "Theo: 10% IRS early-withdrawal penalty + 22% federal bracket; state tax extra.",
             "Direct rollover isn't taxed now. Some penalty exceptions exist. Source: IRS.",
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
