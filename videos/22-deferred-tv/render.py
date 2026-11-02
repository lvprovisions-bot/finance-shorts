"""WHO WINS? #9: same $1,200 TV on a deferred-interest "0%" deal, $100 vs $99 a month. 1080x1920 @30fps. Electronics store + giant TV."""
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

# ---------- background: night electronics store, neon strip, shelves of glowing TVs, checker floor ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((14, 8, 58), np.float32); bot = np.array((84, 16, 88), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    r = np.sqrt(((xx - W / 2) / 1.5) ** 2 + ((yy - 560) / 1.0) ** 2)
    img += (np.clip(1 - r / 760, 0, 1) ** 2)[..., None] * np.array((70, 50, 120), np.float32)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(22)
    # back shelves with small glowing TVs
    for row, y in enumerate((885, 985)):
        d.rectangle([0, y + 62, W, y + 72], fill=(20, 10, 44, 255))
        for k in range(8):
            x = 18 + k * 134 + (row * 60)
            c = [(90, 200, 255), (255, 120, 190), (255, 210, 90), (120, 240, 180)][int(rng.integers(0, 4))]
            d.rounded_rectangle([x, y, x + 112, y + 60], radius=6, fill=(16, 10, 36, 255))
            d.rectangle([x + 6, y + 6, x + 106, y + 54], fill=c + (70,))
    # checker floor
    d.rectangle([0, 1065, W, H], fill=(30, 14, 60, 255))
    for j in range(9):
        y0 = 1065 + (j / 9) ** 1.5 * 860; y1 = 1065 + ((j + 1) / 9) ** 1.5 * 860
        for i in range(-8, 9):
            if (i + j) % 2: continue
            s0 = 40 + 170 * (y0 - 1065) / 860; s1 = 40 + 170 * (y1 - 1065) / 860
            d.polygon([(540 + i * s0, y0), (540 + (i + 1) * s0, y0), (540 + (i + 1) * s1, y1), (540 + i * s1, y1)], fill=(44, 22, 82, 255))
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 85, 100)
SCR = (70, 288, 1010, 812)   # TV screen rect
SW = SCR[2] - SCR[0]; SCX = (SCR[0] + SCR[2]) / 2
def money(v): return "${:,.0f}".format(v)
def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0

def make_tv():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([430, 840, 650, 880], fill=(20, 18, 34, 255))
    d.rounded_rectangle([340, 872, 740, 896], radius=10, fill=(32, 28, 52, 255))
    d.rounded_rectangle([40, 258, 1040, 846], radius=26, fill=(12, 12, 22, 255), outline=(95, 90, 135, 255), width=5)
    scr = np.zeros((SCR[3] - SCR[1], SW, 3), np.float32)
    fy = np.linspace(0, 1, SCR[3] - SCR[1])[:, None, None]
    scr += np.array((10, 20, 58), np.float32) * (1 - fy) + np.array((30, 12, 66), np.float32) * fy
    scr[::4] *= 0.9   # scanlines
    s_img = Image.fromarray(np.clip(scr, 0, 255).astype(np.uint8)).convert("RGBA")
    lay.alpha_composite(s_img, (SCR[0], SCR[1]))
    return lay
TV = make_tv()

# balances
def nbal(m): return max(0, 1200 - 100 * m)
def tbal(m): return 1200 - 99 * m
INT = [(1200 - 99 * m) * 0.30 / 12 for m in range(12)]

def month_now(t):
    t0 = seg_start("pay"); t1 = tok("m12", 2)
    return 12 * clamp((t - t0) / (t1 - t0)) if t > t0 else 0.0

def bar(img, y, label, col, bal, payoff=None, wig=0.0):
    x0, x1 = SCR[0] + 40, SCR[2] - 40
    d = ImageDraw.Draw(img)
    pop_text(img, (x0, y - 46), label, F_NUM, 40, col, anchor_c=False)
    d.rounded_rectangle([x0, y, x1, y + 62], radius=18, fill=(38, 34, 70), outline=(120, 115, 170), width=3)
    fw = (x1 - x0 - 8) * bal / 1200
    if bal > 0:
        ww = max(fw, 34)
        d.rounded_rectangle([x0 + 4 + wig, y + 4, x0 + 4 + wig + ww, y + 58], radius=14, fill=col)
    txt = payoff if payoff else money(bal)
    c = MINT if bal == 0 else (WHITE if not payoff else SOFTRED)
    pop_text(img, (x1 - 6 - tw(txt, F_NUM, 46) / 2, y - 42), txt, F_NUM, 46, c)

def calendar(img, y, m, col=GOLD):
    d = ImageDraw.Draw(img)
    n = 12; g = 8; x0 = SCR[0] + 40; w = (SW - 80 - g * (n - 1)) / n
    for i in range(n):
        x = x0 + i * (w + g); on = i < int(m)
        d.rounded_rectangle([x, y, x + w, y + 54], radius=9, fill=col if on else (42, 38, 76))
        pop_text(img, (x + w / 2, y + 27), str(i + 1), F_NUM, 26, (30, 24, 50) if on else (130, 125, 170))

def payments(img, t, freeze=False, wig=0.0):
    m = 12 if freeze else int(month_now(t))
    cm = 12 if freeze else month_now(t)
    pop_text(img, (SCX, SCR[1] + 44), f"MONTH {min(m, 12)} OF 12" if m else "12-MONTH DEAL", F_NUM, 44, GOLD)
    calendar(img, SCR[1] + 82, cm)
    n, th = nbal(m), tbal(m)
    bar(img, SCR[1] + 225, "NORA · $100/MO", NORA, n, payoff="PAID OFF!" if n == 0 else None)
    bar(img, SCR[1] + 390, "THEO · $99/MO", THEO, th, payoff="$12 LEFT" if m >= 12 else None, wig=wig)

def tag(img, cx, cy, s, txt, size=86):
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w_, h_ = 300 * s, 110 * s
    d.polygon([(cx - w_ - 60 * s, cy), (cx - w_, cy - h_), (cx + w_, cy - h_), (cx + w_, cy + h_), (cx - w_, cy + h_)], fill=YEL + (255,))
    d.ellipse([cx - w_ - 18 * s, cy - 14 * s, cx - w_ + 10 * s, cy + 14 * s], fill=(30, 20, 60, 255))
    img.alpha_composite(lay)
    pop_text(img, (cx + 10 * s, cy), txt, F_NUM, size, (40, 24, 70), scale=s)

def small_print(img, t):
    """paper contract with a highlighter sweep + magnifier on the key line"""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = SCR[0] + 50, SCR[1] + 26, SCR[2] - 50, SCR[3] - 26
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(248, 246, 236))
    pop_text(img, ((x0 + x1) / 2, y0 + 44), "STORE CARD AGREEMENT", F_NUM, 36, (70, 66, 90))
    rng = np.random.default_rng(5)
    for i in range(13):
        ly = y0 + 90 + i * 28
        if 4 <= i <= 7: continue
        d.line([x0 + 30, ly, x1 - 30 - int(rng.integers(0, 180)), ly], fill=(190, 188, 200), width=8)
    k = clamp((t - tok("catch", 1)) / 0.5)
    ky = y0 + 240
    txt = "*NO INTEREST ONLY IF PAID IN FULL"
    w_ = tw(txt, F_NUM, 42)
    d.rectangle([SCX - w_ / 2 - 12, ky - 34, SCX - w_ / 2 - 12 + (w_ + 24) * k, ky + 34], fill=(255, 232, 90))
    pop_text(img, (SCX, ky), txt, F_NUM, 42, (40, 30, 60))

def backcharge(img, t):
    d = ImageDraw.Draw(img)
    t0 = tok("catch", 5); t1 = SEG["catch"]["end"]
    prog = clamp((t - t0) / max(0.2, t1 - t0))
    n = int(12 * prog + 0.999) if t > t0 else 0
    pop_text(img, (SCX, SCR[1] + 50), "BACK-CHARGED FROM MONTH 1", F_NUM, 46, SOFTRED)
    g = 10; cols = 6; w_ = (SW - 70 - g * (cols - 1)) / cols; x0 = SCR[0] + 35
    for i in range(12):
        c, r_ = i % cols, i // cols
        x = x0 + c * (w_ + g); y = SCR[1] + 100 + r_ * 112
        on = i < n
        d.rounded_rectangle([x, y, x + w_, y + 100], radius=12, fill=(200, 40, 60) if on else (42, 38, 76))
        pop_text(img, (x + w_ / 2, y + 26), f"M{i + 1}", F_NUM, 26, WHITE if on else (130, 125, 170))
        if on:
            pop_text(img, (x + w_ / 2, y + 66), f"${INT[i]:.2f}", F_NUM, 32, WHITE)
    cum = sum(INT[:n])
    pop_text(img, (SCX, SCR[1] + 425), "THEO OWES EXTRA", F_NUM, 36, (220, 215, 245))
    pop_text(img, (SCX, SCR[1] + 480), money(cum), F_NUM, 72, SOFTRED)

def receipts(img, k):
    for cx, col, lbl, v, c2, tot in ((SCX - 240, THEO, "THEO'S INTEREST", 197, (205, 40, 60), "TV: $1,397"),
                                     (SCX + 240, NORA, "NORA'S INTEREST", 0, (20, 140, 80), "TV: $1,200")):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w_, h_ = 218 * k, 180 * k; cy = SCR[1] + 270
        d.rectangle([cx - w_, cy - h_, cx + w_, cy + h_], fill=(250, 248, 240, 255))
        for zx in range(int(cx - w_), int(cx + w_), 20):
            d.polygon([(zx, cy + h_), (zx + 10, cy + h_ + 13 * k), (zx + 20, cy + h_)], fill=(250, 248, 240, 255))
        d.rectangle([cx - w_, cy - h_, cx + w_, cy - h_ + 14 * k], fill=col + (255,))
        img.alpha_composite(lay)
        pop_text(img, (cx, cy - 110 * k), lbl, F_NUM, 32, (90, 80, 110), scale=k)
        pop_text(img, (cx, cy - 20 * k), money(v), F_NUM, 104, c2, scale=k)
        pop_text(img, (cx, cy + 90 * k), tot, F_NUM, 44, (60, 54, 80), scale=k)

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 96), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(40, 10, 70))
    if sub:
        pop_text(img, (W / 2, 205), sub, F_NUM, 48, sub_col, stroke=5, sfill=(20, 10, 50))

def sc_hook(img, t):
    headline(img, t, "SAME TV. SAME \"0%\" DEAL.", WHITE)
    pop_text(img, (SCX, SCR[1] + 112), "$12 SHORT", F_NUM, 128, YEL)
    d = ImageDraw.Draw(img)
    ay = SCR[1] + 205 + 8 * math.sin(t * 7)
    d.polygon([(SCX - 26, ay), (SCX + 26, ay), (SCX + 26, ay + 36), (SCX + 58, ay + 36), (SCX, ay + 86), (SCX - 58, ay + 36), (SCX - 26, ay + 36)], fill=WHITE)
    pop_text(img, (SCX, SCR[1] + 395), "+$197", F_NUM, 196, SOFTRED, scale=1 + 0.02 * math.sin(t * 6))
def sc_huh(img, t):
    headline(img, t, "THEO: \"IT SAID 0%!\"", (150, 225, 255))
    pop_text(img, (SCX, SCR[1] + 215), "0%", F_NUM, 300, MINT, scale=1 + 0.03 * math.sin(t * 8))
    pop_text(img, (SCX, SCR[1] + 445), "FOR 12 MONTHS*", F_NUM, 72, WHITE)
def sc_deal(img, t):
    headline(img, t, "SAME TV. SAME DEAL.", GOLD)
    tag(img, SCX + 20, SCR[1] + 150, kpop(tok("deal", 1), t), "$1,200 TV", 92)
    k = kpop(tok("deal", 3), t)
    pop_text(img, (SCX, SCR[1] + 335), "NO INTEREST", F_NUM, 92, MINT, scale=k)
    pop_text(img, (SCX, SCR[1] + 440), "FOR 12 MONTHS*", F_NUM, 72, WHITE, scale=k)
def sc_pay(img, t):
    headline(img, t, "$100 vs $99 A MONTH", GOLD)
    payments(img, t)
def sc_m12(img, t):
    headline(img, t, "MONTH 12", GOLD)
    payments(img, t)
def sc_only(img, t):
    headline(img, t, "THEO: \"ONLY $12!\"", (150, 225, 255))
    payments(img, t, freeze=True, wig=4 * math.sin(t * 30))
def sc_catch(img, t):
    headline(img, t, "THE SMALL PRINT", SOFTRED)
    if t < tok("catch", 3) - 0.05:
        small_print(img, t)
    else:
        backcharge(img, t)
def sc_total(img, t):
    headline(img, t, "INTEREST: $197 vs $0", SOFTRED)
    receipts(img, ease_back((t - seg_start("total") + 0.1) / 0.35))
def sc_punch(img, t):
    headline(img, t, "HE \"SAVED\" $1 A MONTH", SOFTRED)
    receipts(img, 1.0)
def sc_q(img, t):
    headline(img, t, "")
    receipts(img, 1.0)
    k = ease_back((t - seg_start("q")) / 0.35)
    if k > 0.03:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([W / 2 - 440 * k, 550 - 250 * k, W / 2 + 440 * k, 550 + 250 * k], radius=int(40 * k), fill=WHITE, outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 395), "WOULD YOU TRUST", F_NUM, 70, (20, 30, 70), scale=k)
        pop_text(img, (W / 2, 535), "\"0%\"?", F_NUM, 170, (205, 40, 60), scale=k)
        pop_text(img, (W / 2, 695), "TELL US IN THE COMMENTS", F_NUM, 46, (20, 30, 70), scale=k)

SCENES = {"hook": sc_hook, "huh": sc_huh, "deal": sc_deal, "pay": sc_pay, "m12": sc_m12, "only": sc_only,
          "catch": sc_catch, "total": sc_total, "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "worried", "point_up", "smile"), "huh": ("cheer", "smug", "idle", "smile"),
         "deal": ("idle", "smile", "point_up", "smile"), "pay": ("point_up", "smug", "point_up", "smile"),
         "m12": ("idle", "smile", "cheer", "smile"), "only": ("shrug", "smug", "idle", "smile"),
         "catch": ("idle", "worried", "marker", "smile"), "total": ("shrug", "worried", "point_up", "smile"),
         "punch": ("facepalm", "worried", "shrug", "smile"), "q": ("idle", "smile", "point_up", "smile"),
         "loop": ("facepalm", "worried", "idle", "smile")}
CY = 1215
TXC, NXC = 282, 797

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
    for who, cx, col, pose, mood in (("T", TXC, THEO, tp, tm), ("N", NXC, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.0 if who == spk else 0.95
        cy = CY + (0 if who == spk else 12)
        person(img, cx, cy, sc, col, who, t, talk=talking, pose=pose, mood=mood)
        if who == "N" and s["scene"] in ("total", "punch", "q"):
            crown(img, cx, cy, sc, kpop(seg_start("total"), t) if s["scene"] == "total" else 1.0)

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
    lines = ["Deferred-interest store card at 30% APR (Bankrate 2025 avg: 30.14%).",
             "Interest on each month's balance, no compounding; bills can be higher.",
             "True 0% APR offers don't back-charge. Source on the catch: CFPB.",
             "Fictional characters. Illustration only. Not financial advice."]
    for i, ln in enumerate(lines):
        d.text((W / 2, 1600 + i * 33), ln, font=font(F_MED, 26), fill=c, anchor="mm")


def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    img.alpha_composite(TV)
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
