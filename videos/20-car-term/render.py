"""WHO WINS? #8: same $45K car, 4-yr vs 7-yr loan at 7%. 1080x1920 @30fps. Night road, two-lane loan race, receipts."""
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

# ---------- background: night navy -> violet, stars + perspective road ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((6, 10, 40), np.float32); bot = np.array((58, 18, 92), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    r = np.sqrt(((xx - W / 2) / 1.6) ** 2 + ((yy - 1000) / 0.7) ** 2)
    img += (np.clip(1 - r / 700, 0, 1) ** 2)[..., None] * np.array((60, 30, 90), np.float32)  # horizon glow
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(20)
    for _ in range(90):
        x, y = rng.integers(0, W), rng.integers(230, 980); rr = rng.choice([1, 2, 2, 3])
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, int(rng.integers(50, 160))))
    # hills
    pts = [(0, 1000)] + [(x, 1000 - 60 * math.sin(x / 170) - 30 * math.sin(x / 61 + 1)) for x in range(0, W + 20, 20)] + [(W, 1000)]
    d.polygon(pts, fill=(28, 14, 60, 255))
    d.rectangle([0, 1000, W, H], fill=(24, 12, 50, 255))
    # road in perspective
    d.polygon([(470, 1000), (610, 1000), (W + 260, H), (-260, H)], fill=(40, 36, 70, 255))
    for k in range(9):
        y0 = 1000 + (k / 9) ** 1.6 * 920; y1 = 1000 + ((k + 0.5) / 9) ** 1.6 * 920
        w0 = 3 + 22 * (y0 - 1000) / 920; w1 = 3 + 22 * (y1 - 1000) / 920
        d.polygon([(540 - w0, y0), (540 + w0, y0), (540 + w1, y1), (540 - w1, y1)], fill=(255, 210, 90, 150))
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 95, 110)
def money(v): return "${:,.0f}".format(v)
def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0

P, R = 45_000, 0.07
def pmt(n): i = R / 12; return P * i / (1 - (1 + i) ** -n)
def owed(n, yrs):
    m = min(yrs * 12, n); i = R / 12; p = pmt(n)
    return max(0.0, P * (1 + i) ** m - p * ((1 + i) ** m - 1) / i)

# ---------- loan road ----------
X0, X1 = 120, 980
def yx(y): return X0 + (X1 - X0) * y / 7
LN, LT = 412, 600      # lane centre y for Nora / Theo
def car(img, cx, cy, col, t, moving, smoke=0.0, s=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bob = math.sin(t * 30) * 2 if moving else 0
    cy += bob
    d.rounded_rectangle([cx - 70 * s, cy - 30 * s, cx + 70 * s, cy + 12 * s], radius=int(16 * s), fill=col)
    d.polygon([(cx - 40 * s, cy - 30 * s), (cx - 22 * s, cy - 58 * s), (cx + 26 * s, cy - 58 * s), (cx + 46 * s, cy - 30 * s)], fill=col)
    d.polygon([(cx - 30 * s, cy - 32 * s), (cx - 17 * s, cy - 52 * s), (cx + 0 * s, cy - 52 * s), (cx + 0 * s, cy - 32 * s)], fill=(200, 235, 255))
    d.polygon([(cx + 6 * s, cy - 32 * s), (cx + 6 * s, cy - 52 * s), (cx + 22 * s, cy - 52 * s), (cx + 36 * s, cy - 32 * s)], fill=(200, 235, 255))
    d.ellipse([cx + 58 * s, cy - 22 * s, cx + 72 * s, cy - 10 * s], fill=(255, 240, 150))
    ang = t * 14 if moving else 0
    for wx in (-42, 42):
        x, y = cx + wx * s, cy + 14 * s
        d.ellipse([x - 20 * s, y - 20 * s, x + 20 * s, y + 20 * s], fill=(25, 22, 35))
        d.ellipse([x - 9 * s, y - 9 * s, x + 9 * s, y + 9 * s], fill=(190, 190, 205))
        d.line([x + math.cos(ang) * 16 * s, y + math.sin(ang) * 16 * s, x - math.cos(ang) * 16 * s, y - math.sin(ang) * 16 * s], fill=(120, 120, 140), width=3)
    if smoke > 0.02:
        for k in range(5):
            ph = (t * 0.9 + k / 5) % 1
            r_ = (14 + 34 * ph) * s
            sx, sy = cx - 10 * s + 30 * math.sin(k * 2.1) * ph, cy - 60 * s - 130 * ph
            d.ellipse([sx - r_, sy - r_, sx + r_, sy + r_], fill=(150, 150, 165, int(170 * (1 - ph) * smoke)))
    img.alpha_composite(lay)

def lane(img, y, col, yrs_total, done):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([X0 - 70, y - 44, X1 + 50, y + 44], radius=22, fill=(14, 12, 40, 215), outline=col + (220,), width=4)
    xe = yx(yrs_total)
    for x in range(X0, int(xe), 44):
        d.line([x, y + 26, x + 22, y + 26], fill=(255, 255, 255, 70), width=4)
    # finish line (checkered)
    for r_ in range(8):
        for c_ in range(2):
            fill = (255, 255, 255, 255) if (r_ + c_) % 2 == 0 else (20, 20, 30, 255)
            d.rectangle([xe + c_ * 11, y - 44 + r_ * 11, xe + c_ * 11 + 11, y - 44 + r_ * 11 + 11], fill=fill)
    if done > 0:
        d.rectangle([X0, y + 36, X0 + (xe - X0) * done, y + 42], fill=col + (255,))
    img.alpha_composite(lay)

def stage(img, t, st):
    yrs = st.get("yrs", 0.0)
    for nm, y, col, n, yt in (("NORA", LN, NORA, 48, 4), ("THEO", LT, THEO, 84, 7)):
        lane(img, y, col, yt, min(1, yrs / yt))
        k = st.get("lab", 1.0)
        lbl = f"{nm} · {yt} YRS · {money(pmt(n))}/MO"
        hl = st.get("hl_t", 0.0) if nm == "THEO" else 0.0
        pop_text(img, (X0 - 60, y - 82), lbl, F_NUM, 38, col, scale=1 + 0.08 * hl, stroke=5, sfill=(10, 8, 30), anchor_c=False)
        ow = owed(n, yrs)
        if st.get("owed", False):
            txt = "PAID OFF!" if ow < 1 else "OWES " + money(ow)
            c = MINT if ow < 1 else ((255, 150, 150) if nm == "THEO" and yrs >= 4 else (220, 220, 240))
            if yrs > 0.01:
                pop_text(img, (X1 + 40 - tw(txt, F_NUM, 30) / 2 - 10, y - 82), txt, F_NUM, 30, c, stroke=4, sfill=(10, 8, 30))
        cx = yx(min(yrs, yt)); moving = 0.01 < yrs < yt
        car(img, cx, y + 6, col, t, moving, smoke=st.get("smoke", 0.0) if nm == "THEO" else 0.0, s=0.8)
    for yv in range(8):
        pop_text(img, (yx(yv), 672), f"Y{yv}" if yv else "START", F_MED, 26, (180, 180, 220))
    if st.get("apr", 0.0) > 0.02:
        k = st["apr"]
        pop_text(img, (W / 2, 268), "BOTH: $45K CAR · SAME 7% APR", F_NUM, 36, GOLD, scale=k, stroke=5, sfill=(30, 20, 10))
    if st.get("flag", 0.0) > 0.02:
        k = st["flag"]
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        fx = yx(4) + 6
        d.line([fx, LN - 44, fx, LN - 44 - 120 * k], fill=(240, 240, 240, 255), width=6)
        d.polygon([(fx, LN - 44 - 120 * k), (fx + 90 * k, LN - 44 - 95 * k), (fx, LN - 44 - 70 * k)], fill=MINT + (255,))
        img.alpha_composite(lay)
    if st.get("bill", 0.0) > 0.02:
        receipts(img, st["bill"])

def receipts(img, k):
    for cx, col, lbl, v in ((282, NORA, "NORA'S INTEREST", 6_724), (797, THEO, "THEO'S INTEREST", 12_050)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w, h = 215 * k, 80 * k; cy = 790
        d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=int(18 * k), fill=(250, 248, 240, 255), outline=col + (255,), width=max(2, int(6 * k)))
        for zx in range(int(cx - w), int(cx + w), 20):   # zig-zag receipt edge
            d.polygon([(zx, cy + h), (zx + 10, cy + h + 12 * k), (zx + 20, cy + h)], fill=(250, 248, 240, 255))
        img.alpha_composite(lay)
        pop_text(img, (cx, cy - 38 * k), lbl, F_NUM, 30, (90, 80, 110), scale=k)
        pop_text(img, (cx, cy + 22 * k), money(v), F_NUM, 66, (200, 40, 60) if v > 10_000 else (20, 140, 80), scale=k)

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 100), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(40, 10, 70))
    if sub:
        pop_text(img, (W / 2, 205), sub, F_NUM, 46, sub_col, stroke=5, sfill=(20, 10, 50))

def y4_progress(t):
    t0 = seg_start("year4"); t1 = tok("year4", 2)
    return 4 * ease_out((t - t0) / max(0.3, t1 - t0)) if t > t0 else 0.0
def sc_hook(img, t):
    headline(img, t, "SAME CAR. THEO PAYS +$5,326", SOFTRED)
    stage(img, t, dict(apr=1.0))
def sc_huh(img, t):
    headline(img, t, "THEO: \"$398 LESS A MONTH!\"", (150, 225, 255))
    stage(img, t, dict(apr=1.0, hl_t=0.5 + 0.5 * math.sin(t * 8)))
def sc_term(img, t):
    headline(img, t, "4 YEARS vs 7 YEARS", GOLD)
    stage(img, t, dict(apr=kpop(tok("term", 4), t)))
def sc_year4(img, t):
    headline(img, t, "YEAR 4", GOLD)
    stage(img, t, dict(yrs=y4_progress(t), owed=True, flag=kpop(tok("year4", 2), t)))
def sc_total(img, t):
    headline(img, t, "INTEREST: THEO PAYS +$5,326", SOFTRED)
    t0 = seg_start("total"); t1 = SEG["total"]["end"]
    yrs = 4 + 3 * ease_out((t - t0) / (t1 - t0))
    stage(img, t, dict(yrs=yrs, owed=True, flag=1.0, bill=kpop(tok("total", 2), t)))
def sc_punch(img, t):
    headline(img, t, "PAID OFF... IN YEAR 7", SOFTRED)
    stage(img, t, dict(yrs=7, owed=True, flag=1.0, bill=1.0, smoke=clamp((t - tok("punch", 4)) / 0.4) if t > tok("punch", 4) - 0.3 else 0.0))
def sc_q(img, t):
    headline(img, t, "")
    stage(img, t, dict(yrs=7, owed=True, flag=1.0, bill=1.0, smoke=1.0))
    k = ease_back((t - seg_start("q")) / 0.35)
    if k > 0.03:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([W / 2 - 440 * k, 600 - 240 * k, W / 2 + 440 * k, 600 + 240 * k], radius=int(40 * k), fill=WHITE, outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 455), "4 YEARS", F_NUM, 96, (220, 110, 40), scale=k)
        pop_text(img, (W / 2, 550), "OR", F_NUM, 56, (20, 30, 70), scale=k)
        pop_text(img, (W / 2, 645), "7 YEARS?", F_NUM, 96, (30, 130, 180), scale=k)
        pop_text(img, (W / 2, 755), "TELL US IN THE COMMENTS", F_NUM, 44, (20, 30, 70), scale=k)

SCENES = {"hook": sc_hook, "huh": sc_huh, "term": sc_term, "year4": sc_year4, "total": sc_total,
          "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "smile", "point_up", "smile"), "huh": ("cheer", "smug", "idle", "smile"),
         "term": ("idle", "smile", "point_up", "smile"), "year4": ("idle", "worried", "cheer", "smile"),
         "total": ("shrug", "worried", "point_up", "smile"), "punch": ("facepalm", "worried", "shrug", "smile"),
         "q": ("idle", "smile", "point_up", "smile"), "loop": ("shrug", "worried", "idle", "smile")}
CY = 1215
NXC, TXC = 282, 797

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
        if who == "N" and s["scene"] in ("year4", "total", "punch", "q"):
            crown(img, cx, cy, sc, kpop(tok("year4", 2), t) if s["scene"] == "year4" else 1.0)
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
    lines = ["Source: Edmunds Q3 2026 - avg new-car APR 7%; 25.5% of new loans 84+ mo.",
             "$45K financed, 7% APR on both loans, monthly payments; no fees,",
             "taxes or insurance. Longer loans often get higher rates.",
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
