"""WHO WINS? #4 (UK): Lifetime ISA price cap. 1080x1920 @30fps. Plum-dusk gradient + rooftop skyline, ISA cards, price-cap ruler, bonus-vs-charge bars."""
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
    elif pose == "keys":        # holds up house keys
        side = 1 if who == "N" else -1
        p1 = (cx + side * 150 * s, cy - 175 * s + wv * 0.3)
        arm(sh_r if side > 0 else sh_l, p1)
        d.ellipse([p1[0] - 22 * s, p1[1] - 78 * s, p1[0] + 22 * s, p1[1] - 34 * s], outline=(255, 196, 46), width=max(2, int(9 * s)))
        d.line([p1[0], p1[1] - 34 * s, p1[0], p1[1] + 30 * s], fill=(255, 196, 46), width=max(2, int(10 * s)))
        d.line([p1[0], p1[1] + 14 * s, p1[0] + 18 * s, p1[1] + 14 * s], fill=(255, 196, 46), width=max(2, int(8 * s)))
        arm(sh_l if side > 0 else sh_r, (cx - side * 115 * s, cy + 125 * s))
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
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(60, 40, 120, 50))
    img.alpha_composite(sh); img.alpha_composite(lay)
# ---------- background: plum dusk gradient + rooftop skyline with lit windows ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((78, 22, 74), np.float32); bot = np.array((18, 12, 46), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - 520) * 1.2) ** 2) / 760
    img += (np.clip(1 - d, 0, 1) ** 2)[..., None] * np.array((60, 26, 60), np.float32)
    rng = np.random.default_rng(9)
    for _ in range(90):
        x, y = rng.integers(0, W), rng.integers(0, 900)
        img[y:y + 3, x:x + 3] += 60 * rng.random()
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    x = -20
    while x < W:
        w = int(rng.integers(90, 160)); hgt = int(rng.integers(140, 330)); base = 1290
        col = (40, 20, 62, 255)
        dd.rectangle([x, base - hgt, x + w, base], fill=col)
        dd.polygon([(x - 8, base - hgt), (x + w / 2, base - hgt - int(rng.integers(45, 85))), (x + w + 8, base - hgt)], fill=col)
        for wy in range(base - hgt + 25, base - 30, 55):
            for wx in range(x + 18, x + w - 30, 42):
                if rng.random() < 0.35:
                    dd.rectangle([wx, wy, wx + 18, wy + 24], fill=(255, 200, 110, 120))
        x += w + int(rng.integers(6, 26))
    dd.rectangle([0, 1290, W, H], fill=(24, 14, 44, 255))
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); PINK = (255, 110, 170); LAV = (205, 180, 230)
CARD = (255, 248, 252); CARD_INK = (60, 24, 70)
def gbp(v): return "£{:,.0f}".format(v)

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 185), "WHO WINS?", F_NUM, 128, YEL, scale=pulse, stroke=10, sfill=(60, 16, 60))
    if sub:
        pop_text(img, (W / 2, 290), sub, F_NUM, 48, sub_col)

CX = {"T": 290, "N": 790}; CW = 420; CY0, CY1 = 350, 750
def card(img, who, lines, glow=0.0):
    cx = CX[who]; x0, x1 = cx - CW / 2, cx + CW / 2
    d = ImageDraw.Draw(img)
    if glow > 0.01:
        for r in range(5, 0, -1):
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(lay).rounded_rectangle([x0 - r * 7, CY0 - r * 7, x1 + r * 7, CY1 + r * 7], radius=40 + r * 7, fill=GOLD + (int(16 * glow),))
            img.alpha_composite(lay)
    d.rounded_rectangle([x0, CY0, x1, CY1], radius=36, fill=CARD)
    col = THEO if who == "T" else NORA
    d.rounded_rectangle([x0, CY0, x1, CY0 + 82], radius=36, fill=col)
    d.rectangle([x0, CY0 + 50, x1, CY0 + 82], fill=col)
    pop_text(img, (cx, CY0 + 42), ("THEO'S" if who == "T" else "NORA'S") + " LIFETIME ISA", F_NUM, 32, WHITE)
    for (y, s, size, colr, k) in lines:
        pop_text(img, (cx, y), s, F_NUM, size, colr, scale=k)

def sc_hook(img, t):
    s = scene_at(t)["scene"]
    if s == "hook2" and t > tok("hook2", 1) - 0.1:
        headline(img, t, "SAME £20,000 IN. DIFFERENT £ OUT?", GOLD)
    elif s == "how":
        headline(img, t, "SAME ACCOUNT. SAME SAVINGS.", GOLD)
    else:
        headline(img, t, "SAME £20,000 SAVED")
    for who in ("T", "N"):
        L = [(CY0 + 140, "PAID IN", 34, GREY, 1.0), (CY0 + 205, "£20,000", 78, CARD_INK, 1.0)]
        if s in ("hook2", "how"):
            i = 3 if who == "T" else 1
            if t > tok("hook2", i) - 0.1:
                k = ease_back((t - tok("hook2", i) + 0.1) / 0.35)
                L += [(CY0 + 290, "GOT BACK", 34, GREY, k), (CY0 + 355, "£18,750" if who == "T" else "£25,000", 78, RED if who == "T" else GREEN, k)]
        card(img, who, L, glow=1.0 if (who == "N" and s in ("hook2", "how") and t > tok("hook2", 1)) else 0)
    if s == "how":
        k = ease_back((t - seg_start("how")) / 0.35)
        pop_text(img, (CX["T"], CY1 + 45), "−£1,250 vs paid in!", F_NUM, 40, WHITE, scale=k, stroke=8, sfill=RED)

def stack_state(t):
    s = scene_at(t)["scene"]
    if s == "rew":
        a = tok("rew", 3)
        yrs = 5 * ease_out((t - a) / (seg_start("bonus") - a)) if t > a else 0
        return yrs, 0
    if s == "bonus":
        a = tok("bonus", 2)
        return 5, (5 * ease_out((t - a) / 1.6) if t > a - 0.05 else 0)
    return 5, 5

def sc_stack(img, t):
    s = scene_at(t)["scene"]
    yrs, byrs = stack_state(t)
    if s == "rew": headline(img, t, f"£4,000 A YEAR · YEAR {min(5, int(yrs) + (1 if yrs > 0 else 0)) if yrs < 5 else 5} OF 5")
    elif s == "bonus": headline(img, t, "+25% GOVERNMENT BONUS", GOLD)
    else: headline(img, t, "5 YEARS LATER: £25,000 EACH", GREEN)
    for who in ("T", "N"):
        cx = CX[who]; col = THEO if who == "T" else NORA
        val = 4000 * yrs + 1000 * byrs
        card(img, who, [(CY0 + 122, gbp(round(val / 50) * 50), 64, GREEN if byrs > 0 else CARD_INK, 1.0)])
        d = ImageDraw.Draw(img)
        bw, bh, by = 260, 36, CY1 - 20
        for y in range(5):
            fy = clamp(yrs - y)
            if fy <= 0: break
            y1 = by - y * (bh + 8); y0 = y1 - bh * ease_back(fy)
            d.rounded_rectangle([cx - bw / 2, y0, cx + bw / 2 - 70, y1], radius=10, fill=col)
            d.text((cx - 35, (y0 + y1) / 2), "£4K", font=font(F_NUM, 24), fill=WHITE, anchor="mm")
            fb = clamp(byrs - y)
            if fb > 0.02:
                bx0 = cx + bw / 2 - 62
                d.rounded_rectangle([bx0, y1 - bh * ease_back(fb), bx0 + 62, y1], radius=10, fill=GOLD)
                d.text((bx0 + 31, y1 - bh / 2), "+£1K", font=font(F_NUM, 22), fill=(120, 70, 0), anchor="mm")
    if s == "bonus" and t > tok("bonus", 2) - 0.1:
        k = ease_back((t - tok("bonus", 2) + 0.1) / 0.35)
        pop_text(img, (W / 2, 330 + 30), "", F_NUM, 40, GOLD, scale=k)

# ---------- price ruler ----------
RX0, RX1, RY = 110, 970, 650
PMIN, PMAX = 250000, 550000
def px(p): return RX0 + (RX1 - RX0) * (p - PMIN) / (PMAX - PMIN)
def house(img, x, base, s, col, k, label, lab_col):
    if k < 0.03: return
    d = ImageDraw.Draw(img); s = s * k
    w, h = 120 * s, 90 * s
    d.rectangle([x - w / 2, base - h, x + w / 2, base], fill=col)
    d.polygon([(x - w / 2 - 18 * s, base - h), (x, base - h - 70 * s), (x + w / 2 + 18 * s, base - h)], fill=(255, 250, 255))
    d.rectangle([x - 16 * s, base - 50 * s, x + 16 * s, base], fill=(70, 30, 70))
    pop_text(img, (x, base - h - 105 * s), label, F_NUM, 40, lab_col, scale=k, stroke=6, sfill=(40, 14, 50))

def sc_ruler(img, t):
    s = scene_at(t)["scene"]
    subs = {"nora": ("NORA: FIRST FLAT", WHITE), "theo": ("THEO: DREAM FLAT", WHITE),
            "limit": ("FIRST-HOME LIMIT: £450,000", GOLD), "so": ("£30,000 OVER THE LIMIT", (255, 120, 120))}
    headline(img, t, *subs[s])
    d = ImageDraw.Draw(img)
    lim_k = 0
    if s in ("limit", "so"):
        lim_k = 1.0 if s == "so" else ease_out((t - tok("limit", 1) + 0.1) / 0.5)
    if lim_k > 0.02:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle([px(450000), 380, px(450000) + (RX1 + 20 - px(450000)) * lim_k, RY], fill=(230, 60, 70, 70))
        img.alpha_composite(lay)
    d.line([(RX0, RY), (RX1, RY)], fill=WHITE, width=8)
    for p in range(250000, 550001, 50000):
        d.line([(px(p), RY - 14), (px(p), RY + 14)], fill=WHITE, width=5)
        pop_text(img, (px(p), RY + 48), f"£{p // 1000}K", F_MED, 30, LAV)
    if lim_k > 0.02:
        x = px(450000)
        d.line([(x, RY - 270 * lim_k), (x, RY + 20)], fill=RED, width=10)
        pop_text(img, (x, RY - 300), "LIMIT", F_NUM, 40, WHITE, scale=lim_k, stroke=8, sfill=RED)
    kN = 1.0 if s != "nora" else (ease_back((t - tok("nora", 3) + 0.1) / 0.4) if t > tok("nora", 3) - 0.1 else 0)
    house(img, px(320000), RY - 10, 1.0, NORA, kN, "£320K ✓" if False else "£320K", GREEN)
    if kN > 0.5 and (s != "nora" or t > tok("nora", 4) - 0.1):
        kb = 1.0 if s != "nora" else ease_back((t - tok("nora", 4) + 0.1) / 0.35)
        pop_text(img, (px(320000), RY - 255), "BONUS KEPT", F_NUM, 34, GOLD, scale=kb)
    if s != "nora":
        kT = 1.0 if s != "theo" else (ease_back((t - tok("theo", 3) + 0.1) / 0.4) if t > tok("theo", 3) - 0.1 else 0)
        house(img, px(480000), RY - 10, 1.0, THEO, kT, "£480K", (255, 120, 120) if s in ("limit", "so") else WHITE)
    if s == "so" and t > tok("so", 1) - 0.1:
        k = ease_out((t - tok("so", 1) + 0.1) / 0.4)
        y = RY + 90; xa, xb = px(450000), px(450000) + (px(480000) - px(450000)) * k
        d.line([(xa, y), (xb, y)], fill=GOLD, width=7)
        d.line([(xa, y - 14), (xa, y + 14)], fill=GOLD, width=7)
        if k > 0.95:
            d.line([(xb, y - 14), (xb, y + 14)], fill=GOLD, width=7)
            pop_text(img, ((xa + xb) / 2 + 70, y + 2), "+£30K", F_NUM, 36, GOLD)

# ---------- bonus vs charge ----------
BX0, BMAX = 120, 840
def sc_charge(img, t):
    s = scene_at(t)["scene"]
    subs = {"charge": ("OVER THE CAP = 25% CHARGE", (255, 120, 120)), "fair": ("25% IN, 25% OUT... FAIR?", WHITE),
            "maths": ("25% OF A BIGGER POT", GOLD), "punch": ("THEO: −£1,250 vs PAID IN", (255, 120, 120))}
    headline(img, t, *subs[s])
    d = ImageDraw.Draw(img)
    # Theo's pot bar
    y0, y1 = 390, 480
    pop_text(img, (BX0, y0 - 28), "THEO'S POT  £25,000", F_NUM, 34, WHITE, anchor_c=False)
    full = BMAX - BX0 + 120
    split = s != "charge" or t > tok("charge", 2) - 0.1
    ks = 1.0 if s != "charge" else (ease_out((t - tok("charge", 2) + 0.1) / 0.5) if split else 0)
    xs = BX0 + full * 0.75
    d.rounded_rectangle([BX0, y0, xs, y1], radius=16, fill=THEO)
    d.text(((BX0 + xs) / 2, (y0 + y1) / 2), "£18,750 KEPT" if ks > 0.5 else "£25,000", font=font(F_NUM, 40), fill=WHITE, anchor="mm")
    off = 40 * ks
    d.rounded_rectangle([xs + 6 + off, y0 + off * 0.3, BX0 + full + off, y1 + off * 0.3], radius=16, fill=RED if ks > 0.05 else THEO)
    if ks > 0.3:
        d.text(((xs + BX0 + full) / 2 + off + 3, (y0 + y1) / 2 + off * 0.3), "−25%", font=font(F_NUM, 36), fill=WHITE, anchor="mm")
    # comparison bars (scale: £6,250 -> BMAX-BX0 px)
    if s in ("maths", "punch"):
        sc = (BMAX - BX0) / 6250
        kb = 1.0 if s == "punch" else (ease_out((t - tok("maths", 4) + 0.1) / 0.5) if t > tok("maths", 4) - 0.1 else 0)
        kc = 1.0 if s == "punch" else (ease_out((t - tok("maths", 3) + 0.1) / 0.5) if t > tok("maths", 3) - 0.1 else 0)
        yb, yc = 585, 705
        if kc > 0.02:
            pop_text(img, (BX0, yc - 50), "CHARGE (25% of £25,000)", F_MED, 30, LAV, anchor_c=False)
            d.rounded_rectangle([BX0, yc - 30, BX0 + 6250 * sc * kc, yc + 30], radius=14, fill=RED)
            d.text((BX0 + 16, yc), "−£6,250", font=font(F_NUM, 38), fill=WHITE, anchor="lm")
        if kb > 0.02:
            pop_text(img, (BX0, yb - 50), "BONUS HE GOT (25% of £20,000)", F_MED, 30, LAV, anchor_c=False)
            d.rounded_rectangle([BX0, yb - 30, BX0 + 5000 * sc * kb, yb + 30], radius=14, fill=GOLD)
            d.text((BX0 + 16, yb), "+£5,000", font=font(F_NUM, 38), fill=(110, 60, 0), anchor="lm")
        if s == "punch":
            k = ease_back((t - seg_start("punch")) / 0.4)
            xa, xb = BX0 + 5000 * sc, BX0 + 6250 * sc
            dash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(dash).rectangle([xa, yb - 30, xb, yc + 30], outline=(255, 255, 255, 230), width=5)
            img.alpha_composite(dash)
            pop_text(img, (xb + 105, (yb + yc) / 2), "−£1,250", F_NUM, 44, WHITE, scale=k, stroke=8, sfill=RED)

def sc_lesson(img, t):
    s = scene_at(t)["scene"]
    headline(img, t, "")
    d = ImageDraw.Draw(img)
    s0 = seg_start(s)
    k = ease_back((t - s0) / 0.35)
    if k < 0.03: return
    d.rounded_rectangle([W / 2 - 440 * k, 545 - 220 * k, W / 2 + 440 * k, 545 + 220 * k], radius=40 * k, fill=CARD, outline=GOLD, width=max(2, int(10 * k)))
    if s == "lesson":
        pop_text(img, (W / 2, 385), "LIFETIME ISA HOME RULES", F_NUM, 50, CARD_INK, scale=k)
        for i, ln in enumerate(["First home only, £450,000 max", "Bought with a mortgage", "12+ months after first payment",
                                "Otherwise: 25% charge"]):
            pop_text(img, (W / 2, 470 + i * 72), ln, F_MED, 44, RED if i == 3 else (70, 40, 90), scale=k)
    else:
        pop_text(img, (W / 2, 415), "WOULD YOU HAVE", F_NUM, 66, CARD_INK, scale=k)
        pop_text(img, (W / 2, 505), "SPOTTED THE", F_NUM, 66, CARD_INK, scale=k)
        pop_text(img, (W / 2, 610), "£450K LIMIT?", F_NUM, 96, (215, 60, 120), scale=k)
        pop_text(img, (W / 2, 705), "NORA OR THEO? TELL US", F_NUM, 44, (70, 40, 90), scale=k)

SCENES = {"hook": sc_hook, "hook2": sc_hook, "how": sc_hook, "rew": sc_stack, "bonus": sc_stack, "pot": sc_stack,
          "nora": sc_ruler, "theo": sc_ruler, "limit": sc_ruler, "so": sc_ruler,
          "charge": sc_charge, "fair": sc_charge, "maths": sc_charge, "punch": sc_charge,
          "lesson": sc_lesson, "q": sc_lesson, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "smile", "idle", "smile"), "hook2": ("idle", "worried", "cheer", "smile"),
         "how": ("shrug", "worried", "idle", "smile"), "rew": ("idle", "smile", "point_up", "smile"),
         "bonus": ("cheer", "smug", "idle", "smile"), "pot": ("idle", "smile", "point_up", "smile"),
         "nora": ("idle", "smile", "keys", "smile"), "theo": ("cheer", "smug", "idle", "smile"),
         "limit": ("idle", "worried", "point_up", "smile"), "so": ("shrug", "smug", "idle", "smile"),
         "charge": ("idle", "worried", "point_up", "smile"), "fair": ("shrug", "smug", "idle", "smile"),
         "maths": ("idle", "worried", "point_up", "smile"), "punch": ("facepalm", "worried", "idle", "smile"),
         "lesson": ("idle", "worried", "point_up", "smile"), "q": ("idle", "smile", "point_up", "smile"),
         "loop": ("idle", "smile", "idle", "smile")}
CROWN_SCENES = ("nora", "theo", "limit", "so", "charge", "fair", "maths", "punch", "lesson", "q")

TX, NX, CY = 300, 780, 1085
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
    for who, cx, col, pose, mood in (("T", TX, THEO, tp, tm), ("N", NX, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.17 if who == spk else 1.09
        cy = CY + (0 if who == spk else 14)
        person(img, cx, cy, sc, col, who, t, talk=talking, pose=pose, mood=mood)
        if who == "N" and s["scene"] in CROWN_SCENES:
            k = 1.0 if s["scene"] != "nora" else (ease_back((t - tok("nora", 4)) / 0.4) if t > tok("nora", 4) else 0)
            crown(img, cx, cy, sc, k)


# ---------- captions ----------
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

CAP_Y = 1365
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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=PINK)
    c = (200, 180, 220)
    for i, ln in enumerate(["Illustration: both pay £4,000/yr for 5 yrs; cash only, interest & returns ignored.",
                            "Lifetime ISA rules per GOV.UK (Oct 2026): 25% bonus, max £1,000/yr; first home",
                            "£450,000 or less, with a mortgage, 12+ months after first payment; other",
                            "withdrawals pay a 25% charge. Rules may change. Not financial advice."]):
        d.text((W / 2, 1545 + 33 * i), ln, font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1690), "Source: GOV.UK", font=font(F_MED, 26), fill=c, anchor="mm")

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
