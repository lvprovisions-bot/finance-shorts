"""MONEY MYTHS: TRUE OR FALSE? #1 - carrying a credit card balance. 1080x1920 @30fps.
Teal/cyan + white: quiz card with myth in quotes, TRUE/FALSE buttons, green/red split screen, interest counter
+ credit-score gauge, MOSTLY FALSE stamp. One-off character: Uncle Ray."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
TM = json.load(open(os.path.join(HERE, "timings.json")))
TOTAL = TM["total"] + 0.4
NF = int(TOTAL * FPS)
PREVIEW = [float(x) for x in sys.argv[1:]]

F_CAP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_QUOTE = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"
F_NUM = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_MED = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
_fc = {}
def font(path, size):
    k = (path, max(2, int(size)))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, k[1])
    return _fc[k]

WHITE = (255, 255, 255); INK = (8, 62, 74); CYAN = (60, 225, 235); TEAL = (0, 150, 160)
YEL = (255, 216, 77); GREEN = (40, 200, 110); RED = (235, 70, 80); MIST = (190, 235, 240)
RAY = (176, 70, 98); SKIN_R = (232, 182, 140); HAIR_R = (205, 205, 210)

def clamp(x): return min(max(x, 0.0), 1.0)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

SEG = {s["scene"]: s for s in TM["segments"]}
def tok(scene, i): return SEG[scene]["tokens"][i]["start"]
def seg_start(scene): return SEG[scene]["start"]
def scene_at(t):
    cur = TM["segments"][0]
    for s in TM["segments"]:
        if t >= s["start"] - 0.05:
            cur = s
    return cur
def appear(scene, i, t, dur=0.35, lead=0.1):
    """0..1 pop-in starting at token i of scene (1.0 once past this scene)."""
    a = tok(scene, i) - lead
    return 0.0 if t < a else ease_back((t - a) / dur)

sr, vv = wavfile.read(os.path.join(HERE, "voice.wav"))
vv = np.abs(vv.astype(np.float32) / 32768)
def mouth_at(t):
    i = int(t * sr); w = int(0.04 * sr)
    if i >= len(vv): return 0.0
    return clamp(vv[max(0, i - w):i + w].mean() / 0.12)

def pop_text(img, xy, s, path, size, fill, scale=1.0, stroke=0, alpha=1.0, anchor_c=True, sfill=(0, 0, 0), angle=0):
    if scale <= 0.01 or alpha <= 0.01 or size * scale < 2:
        return
    f = font(path, size * scale)
    pad = 20 + stroke
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    layer = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - l, pad - t), s, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=sfill + (255,))
    if angle:
        layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    x = xy[0] - layer.width / 2 if anchor_c else xy[0] - pad
    img.alpha_composite(layer, (int(x), int(xy[1] - layer.height / 2)))

# ---------- background: deep teal -> cyan glow with faint dot grid + question marks ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((0, 88, 104), np.float32); bot = np.array((3, 30, 48), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - 560) * 1.1) ** 2) / 820
    img += (np.clip(1 - d, 0, 1) ** 2)[..., None] * np.array((10, 70, 70), np.float32)
    dots = ((xx % 54) < 5) & ((yy % 54) < 5)
    img[dots] += 18
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rng = np.random.default_rng(4)
    for _ in range(14):
        x, y = int(rng.integers(30, W - 30)), int(rng.integers(120, 1300))
        ImageDraw.Draw(lay).text((x, y), "?", font=font(F_NUM, int(rng.integers(50, 110))), fill=(120, 230, 240, 26), anchor="mm")
    im.alpha_composite(lay)
    return im.convert("RGB")
BG = make_bg()

def badge(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W / 2 - 230, 70, W / 2 + 230, 140], radius=35, fill=(2, 40, 52), outline=CYAN, width=4)
    d.text((W / 2, 105), "MONEY MYTHS #1", font=font(F_NUM, 40), fill=CYAN, anchor="mm")

def check(d, cx, cy, s, col, width=None):
    w = width or max(2, int(14 * s))
    d.line([(cx - 28 * s, cy), (cx - 8 * s, cy + 22 * s), (cx + 30 * s, cy - 24 * s)], fill=col, width=w, joint="curve")
def cross(d, cx, cy, s, col, width=None):
    w = width or max(2, int(14 * s))
    d.line([(cx - 24 * s, cy - 24 * s), (cx + 24 * s, cy + 24 * s)], fill=col, width=w)
    d.line([(cx - 24 * s, cy + 24 * s), (cx + 24 * s, cy - 24 * s)], fill=col, width=w)

# ---------- quiz card (hook / tf / loop / verdict / q) ----------
CX0, CX1, CY0, CY1 = 90, 990, 185, 600
def quiz_card(img, t, mode):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([CX0 + 10, CY0 + 14, CX1 + 10, CY1 + 14], radius=44, fill=(0, 30, 40))
    d.rounded_rectangle([CX0, CY0, CX1, CY1], radius=44, fill=WHITE)
    d.rounded_rectangle([CX0, CY0, CX1, CY0 + 70], radius=44, fill=TEAL)
    d.rectangle([CX0, CY0 + 40, CX1, CY0 + 70], fill=TEAL)
    d.text((W / 2, CY0 + 36), "THE MYTH", font=font(F_NUM, 34), fill=WHITE, anchor="mm")
    if mode == "q":
        pop_text(img, (W / 2, 330), "WHO TOLD YOU", F_NUM, 80, INK)
        pop_text(img, (W / 2, 425), "THIS ONE?", F_NUM, 96, TEAL)
        k = appear("q", 2, t)
        pop_text(img, (W / 2, 530), "COMMENT BELOW", F_NUM, 50, RED, scale=k)
        if k > 0.3:
            ay = 575 + 8 * math.sin(t * 8)
            d.polygon([(W / 2 - 22, ay - 6), (W / 2 + 22, ay - 6), (W / 2, ay + 16)], fill=RED)
        return
    for i, ln in enumerate(["“Carrying a balance", "builds your", "credit score.”"]):
        pop_text(img, (W / 2, 320 + i * 90), ln, F_QUOTE, 72, INK)
    # TRUE / FALSE buttons
    by = 690
    sel = None
    if mode == "verdict":
        sel = "F"
    for key, x, col, lab in (("T", 300, GREEN, "TRUE"), ("F", 780, RED, "FALSE")):
        wob = 1 + 0.03 * math.sin(t * 6 + (0 if key == "T" else 1.5)) if mode in ("hook", "tf", "loop") else 1
        dim = sel is not None and sel != key
        c = tuple(int(v * 0.45 + 40) for v in col) if dim else col
        w2, h2 = 200 * wob, 62 * wob
        d.rounded_rectangle([x - w2, by - h2 + 8, x + w2, by + h2 + 8], radius=30, fill=tuple(int(v * 0.6) for v in c))
        d.rounded_rectangle([x - w2, by - h2, x + w2, by + h2], radius=30, fill=c)
        (check if key == "T" else cross)(d, x - 120 * wob, by, 1.0 * wob, WHITE)
        d.text((x + 30, by), lab, font=font(F_NUM, int(58 * wob)), fill=WHITE, anchor="mm")
    if mode != "verdict":
        pop_text(img, (W / 2, 805), "TRUE OR FALSE?", F_NUM, 78, YEL, stroke=8, sfill=(2, 40, 52),
                 scale=1 + 0.04 * math.sin(t * 5))
    if mode == "verdict":
        k = appear("verdict", 1, t, dur=0.3)
        if k > 0.02:
            veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(veil).rounded_rectangle([CX0, CY0 + 70, CX1, CY1], radius=44, fill=(255, 255, 255, int(205 * clamp(k))))
            img.alpha_composite(veil)
            sc = 1 + 1.2 * (1 - clamp((t - tok("verdict", 1) + 0.1) / 0.25))
            stamp = Image.new("RGBA", (760, 230), (0, 0, 0, 0)); sd = ImageDraw.Draw(stamp)
            sd.rounded_rectangle([10, 10, 750, 220], radius=26, outline=RED + (235,), width=14)
            sd.text((380, 115), "MOSTLY FALSE", font=font(F_NUM, 86), fill=RED + (235,), anchor="mm")
            stamp = stamp.resize((max(2, int(760 * sc)), max(2, int(230 * sc)))).rotate(-9, expand=True, resample=Image.BICUBIC)
            if clamp(k) < 1:
                stamp.putalpha(stamp.getchannel("A").point(lambda v: int(v * clamp(k))))
            img.alpha_composite(stamp, (int(W / 2 - stamp.width / 2), int(400 - stamp.height / 2)))
        k2 = appear("verdict", 3, t)
        if k2 > 0.02:
            d2 = ImageDraw.Draw(img)
            d2.rounded_rectangle([90, 775, 990, 900], radius=30, fill=(2, 40, 52), outline=CYAN, width=4)
            pop_text(img, (W / 2, 808), "IT DEPENDS ON:", F_MED, 34, CYAN, scale=k2)
            pop_text(img, (W / 2, 860), "PAYING THE FULL STATEMENT ON TIME", F_NUM, 40, WHITE, scale=k2)

# ---------- split screen (true / false) ----------
def panel(img, x0, x1, col, title, icon, items, kp):
    if kp < 0.02: return
    d = ImageDraw.Draw(img)
    y0, y1 = 200, 860
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([x0, y0 + (1 - kp) * 60, x1, y1], radius=36, fill=col + (int(235 * clamp(kp)),))
    img.alpha_composite(lay)
    cx = (x0 + x1) / 2
    d.ellipse([cx - 62, y0 + 40, cx + 62, y0 + 164], fill=WHITE)
    icon(d, cx, y0 + 102, 1.4, col, width=20)
    pop_text(img, (cx, y0 + 215), title, F_NUM, 64, WHITE, scale=kp)
    for i, (lines, k) in enumerate(items):
        if k < 0.02: continue
        yb = y0 + 330 + i * 190
        d.rounded_rectangle([x0 + 24, yb - 10, x1 - 24, yb + 150], radius=24, fill=WHITE)
        for j, (s, c, sz) in enumerate(lines):
            pop_text(img, (cx, yb + 40 + j * 62), s, F_NUM, sz, c, scale=k)

def sc_split(img, t):
    s = scene_at(t)["scene"]
    kT = 1.0 if s != "true" else appear("true", 0, t)
    items_t = [([("USING", INK, 44), ("THE CARD", INK, 44)], 1.0 if s != "true" else appear("true", 1, t)),
               ([("PAYING", INK, 44), ("ON TIME", GREEN, 44)], 1.0 if s != "true" else appear("true", 3, t))]
    panel(img, 50, 525, GREEN, "TRUE", check, items_t, kT)
    kF = 0.0 if s == "true" else appear("false", 0, t)
    items_f = [([("SCORE SEES", INK, 42), ("STATEMENT $", RED, 44)], appear("false", 2, t) if s == "false" else 1.0),
               ([("PAID IN FULL?", INK, 42), ("STILL COUNTS", GREEN, 44)], appear("false", 5, t) if s == "false" else 1.0)]
    panel(img, 555, 1030, RED, "MYTH", cross, items_f, kF)
    if s == "true" and t > tok("true", 4) - 0.1:
        k = appear("true", 4, t)
        pop_text(img, (W / 2, 900), "THAT PART IS TRUE", F_NUM, 46, YEL, scale=k, stroke=7, sfill=(2, 40, 52))
    if s == "false" and t > tok("false", 0) - 0.1:
        pop_text(img, (W / 2, 900), "BUT CARRYING A BALANCE?", F_NUM, 46, YEL, stroke=7, sfill=(2, 40, 52))

# ---------- cost: interest counter + score gauge ----------
def gauge(img, cx, cy, r, val, k):
    """credit score gauge 300..850, needle at val."""
    d = ImageDraw.Draw(img)
    cols = [(235, 70, 80), (250, 140, 60), (250, 210, 60), (150, 210, 80), (40, 200, 110)]
    for i, c in enumerate(cols):
        a0 = 180 + i * 36; a1 = a0 + 34
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=c, width=int(38 * k) or 2)
    ang = math.radians(180 + 180 * (val - 300) / 550)
    wob = 0.03 * math.sin(t_glob * 13) * k
    ang += wob
    d.line([(cx, cy), (cx + (r - 50) * math.cos(ang), cy + (r - 50) * math.sin(ang))], fill=WHITE, width=12)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=WHITE)
    pop_text(img, (cx, cy + 55), f"{val}", F_NUM, 56, WHITE)
    pop_text(img, (cx - r + 10, cy + 38), "300", F_MED, 26, MIST)
    pop_text(img, (cx + r - 10, cy + 38), "850", F_MED, 26, MIST)

t_glob = 0.0
def sc_cost(img, t):
    s = scene_at(t)["scene"]
    d = ImageDraw.Draw(img)
    # left: credit card with $1,000 balance
    k = 1.0 if s != "cost" else appear("cost", 0, t)
    if k > 0.02:
        lay = Image.new("RGBA", (520, 330), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([0, 0, 519, 329], radius=34, fill=(14, 120, 140, 255))
        ld.rounded_rectangle([0, 0, 519, 329], radius=34, outline=CYAN + (255,), width=5)
        ld.rectangle([0, 60, 519, 110], fill=(2, 40, 52, 255))
        ld.rounded_rectangle([40, 140, 110, 190], radius=10, fill=(255, 210, 90, 255))
        ld.text((40, 230), "BALANCE KEPT", font=font(F_MED, 30), fill=MIST + (255,))
        ld.text((40, 290), "$1,000", font=font(F_NUM, 64), fill=WHITE + (255,), anchor="lm")
        lay = lay.rotate(-6, expand=True, resample=Image.BICUBIC)
        sc = clamp(k) * 0.4 + 0.6 if k < 1 else 1.0
        lay = lay.resize((max(2, int(lay.width * sc)), max(2, int(lay.height * sc))))
        img.alpha_composite(lay, (int(300 - lay.width / 2), int(360 - lay.height / 2)))
    if s == "cost" and t > tok("cost", 3) - 0.1 or s != "cost":
        ka = 1.0 if s != "cost" else appear("cost", 3, t)
        pop_text(img, (300, 560), "22.15% APR", F_NUM, 50, YEL, scale=ka, stroke=6, sfill=(2, 40, 52))
        pop_text(img, (300, 610), "avg for cards charging interest", F_MED, 24, MIST, scale=ka)
    # counter
    a = tok("cost", 4) - 0.1
    if t > a:
        v = 222 if s != "cost" else 222 * ease_out((t - a) / 1.6)
        d.rounded_rectangle([90, 660, 510, 860], radius=30, fill=(60, 12, 24), outline=RED, width=5)
        pop_text(img, (300, 705), "INTEREST PAID / YEAR", F_MED, 28, (255, 170, 170))
        pop_text(img, (300, 790), f"${v:,.0f}", F_NUM, 104, RED)
    # right: score gauge
    pop_text(img, (790, 300), "YOUR SCORE", F_NUM, 44, WHITE)
    gauge(img, 790, 560, 220, 720, 1.0)
    if s == "zero":
        kz = appear("zero", 1, t)
        pop_text(img, (790, 760), "+0 POINTS", F_NUM, 72, YEL, scale=kz, stroke=8, sfill=(2, 40, 52))
        pop_text(img, (790, 830), "from paying interest", F_MED, 30, MIST, scale=kz)
    elif s == "cost":
        pop_text(img, (790, 760), "...", F_NUM, 72, MIST)

# ---------- Uncle Ray ----------
def ray(img, cx, cy, s, t, talk=0.0, pose="idle", mood="smile"):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bob = math.sin(t * 9) * 6 * s * talk
    cy = cy + bob
    sh_l, sh_r = (cx - 85 * s, cy + 5 * s), (cx + 85 * s, cy + 5 * s)
    def arm(p0, p1):
        d.line([p0, p1], fill=RAY, width=max(2, int(40 * s)))
        d.ellipse([p1[0] - 24 * s, p1[1] - 24 * s, p1[0] + 24 * s, p1[1] + 24 * s], fill=SKIN_R)
    wv = math.sin(t * 7) * 16 * s
    if pose == "finger":   # wagging finger up, lecturing
        arm(sh_r, (cx + 150 * s, cy - 170 * s + wv * 0.6))
        d.rounded_rectangle([cx + 142 * s, cy - 245 * s + wv * 0.6, cx + 158 * s, cy - 185 * s + wv * 0.6], radius=8 * s, fill=SKIN_R)
        arm(sh_l, (cx - 120 * s, cy + 125 * s))
    elif pose == "shrug":
        arm(sh_l, (cx - 175 * s, cy - 70 * s + wv * 0.4)); arm(sh_r, (cx + 175 * s, cy - 70 * s - wv * 0.4))
    elif pose == "card":   # holds up a credit card
        p1 = (cx + 150 * s, cy - 150 * s + wv * 0.3)
        arm(sh_r, p1)
        d.rounded_rectangle([p1[0] - 10 * s, p1[1] - 95 * s, p1[0] + 110 * s, p1[1] - 15 * s], radius=10 * s, fill=CYAN, outline=WHITE, width=max(2, int(4 * s)))
        d.rectangle([p1[0] + 5 * s, p1[1] - 70 * s, p1[0] + 30 * s, p1[1] - 52 * s], fill=YEL)
        arm(sh_l, (cx - 120 * s, cy + 125 * s))
    else:
        arm(sh_l, (cx - 115 * s, cy + 125 * s)); arm(sh_r, (cx + 115 * s, cy + 125 * s))
    # cardigan body with buttons + collar
    d.rounded_rectangle([cx - 100 * s, cy - 40 * s, cx + 100 * s, cy + 150 * s], radius=70 * s, fill=RAY)
    d.rectangle([cx - 100 * s, cy + 90 * s, cx + 100 * s, cy + 150 * s], fill=RAY)
    d.polygon([(cx - 26 * s, cy - 38 * s), (cx, cy + 40 * s), (cx + 26 * s, cy - 38 * s)], fill=(240, 240, 235))
    for by in (60, 95, 130):
        d.ellipse([cx - 6 * s, cy + by * s - 6 * s, cx + 6 * s, cy + by * s + 6 * s], fill=(250, 220, 120))
    # head (bald top, grey sides, glasses, moustache)
    hx, hy, hr = cx, cy - 115 * s, 66 * s
    d.ellipse([hx - hr * 1.08, hy - hr * 0.5, hx - hr * 0.55, hy + hr * 0.35], fill=HAIR_R)
    d.ellipse([hx + hr * 0.55, hy - hr * 0.5, hx + hr * 1.08, hy + hr * 0.35], fill=HAIR_R)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=SKIN_R)
    d.arc([hx - 30 * s, hy - 55 * s, hx + 10 * s, hy - 35 * s], 200, 330, fill=(250, 220, 190), width=max(2, int(4 * s)))
    ey = hy + 2 * s
    blink = 1.1 <= (t % 4.3) < 1.22
    for ex in (-24, 24):
        d.ellipse([hx + ex * s - 20 * s, ey - 18 * s, hx + ex * s + 20 * s, ey + 18 * s], outline=(40, 40, 50), width=max(2, int(5 * s)))
        if blink:
            d.line([hx + ex * s - 8 * s, ey, hx + ex * s + 8 * s, ey], fill=(25, 25, 35), width=max(2, int(4 * s)))
        else:
            d.ellipse([hx + ex * s - 6 * s, ey - 8 * s, hx + ex * s + 6 * s, ey + 8 * s], fill=(25, 25, 35))
    d.line([hx - 4 * s, ey, hx + 4 * s, ey], fill=(40, 40, 50), width=max(2, int(5 * s)))
    if mood == "oops":
        for ex in (-24, 24):
            sgn = 1 if ex < 0 else -1
            d.line([hx + (ex - 14) * s, ey - 26 * s - sgn * 5 * s, hx + (ex + 14) * s, ey - 26 * s + sgn * 5 * s], fill=(90, 90, 100), width=max(2, int(5 * s)))
        d.ellipse([hx + 54 * s, hy - 36 * s, hx + 68 * s, hy - 12 * s], fill=(120, 210, 255))
    else:
        for ex in (-24, 24):
            d.line([hx + (ex - 14) * s, ey - 28 * s, hx + (ex + 14) * s, ey - 30 * s], fill=(150, 150, 160), width=max(2, int(6 * s)))
    my = hy + 36 * s
    mo = talk * mouth_at(t)
    if mo > 0.12:
        h = (6 + 18 * mo) * s
        d.ellipse([hx - 14 * s, my - h / 2 + 4 * s, hx + 14 * s, my + h / 2 + 4 * s], fill=(90, 30, 40))
    elif mood == "oops":
        d.arc([hx - 16 * s, my, hx + 16 * s, my + 20 * s], 200, 340, fill=(25, 25, 35), width=max(2, int(5 * s)))
    else:
        d.arc([hx - 18 * s, my - 12 * s, hx + 18 * s, my + 12 * s], 20, 160, fill=(25, 25, 35), width=max(2, int(5 * s)))
    d.chord([hx - 34 * s, my - 22 * s, hx + 34 * s, my + 6 * s], 180, 360, fill=HAIR_R)  # moustache
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([cx - 125 * s, cy + 140 * s - bob, cx + 125 * s, cy + 172 * s - bob], fill=(0, 20, 30, 70))
    img.alpha_composite(shadow); img.alpha_composite(lay)

# per-scene: (ray x, ray scale, pose, mood)
RAY_STAGE = {"hook": (250, 1.05, "finger", "smile"), "tf": (250, 1.0, "card", "smile"), "true": (230, 0.95, "idle", "smile"),
             "false": (230, 0.95, "shrug", "oops"), "cost": (230, 0.95, "idle", "oops"), "zero": (230, 0.95, "shrug", "oops"),
             "verdict": (230, 0.95, "shrug", "oops"), "q": (230, 0.95, "idle", "smile"), "loop": (250, 1.05, "finger", "smile")}
def draw_ray(img, t):
    s = scene_at(t)
    x, sc, pose, mood = RAY_STAGE[s["scene"]]
    talking = 1.0 if (s["spk"] == "R" and s["start"] - 0.05 <= t <= s["end"] + 0.05) else 0.0
    ray(img, x, 1100, sc, t, talk=talking, pose=pose, mood=mood)
    # name tag on hook
    if s["scene"] in ("hook", "loop"):
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x + 150, 1150, x + 430, 1215], radius=30, fill=WHITE)
        d.text((x + 290, 1182), "UNCLE RAY", font=font(F_NUM, 34), fill=RAY, anchor="mm")
    # host mic icon on the right when narrator speaks
    if s["spk"] == "N":
        d = ImageDraw.Draw(img)
        mx, my = 900, 1110 + 5 * math.sin(t * 4)
        d.rounded_rectangle([mx - 34, my - 90, mx + 34, my + 10], radius=34, fill=CYAN)
        for yy_ in range(-70, 0, 18):
            d.line([(mx - 24, my + yy_), (mx + 24, my + yy_)], fill=TEAL, width=4)
        d.arc([mx - 55, my - 50, mx + 55, my + 40], 0, 180, fill=WHITE, width=8)
        d.line([(mx, my + 40), (mx, my + 85)], fill=WHITE, width=8)
        d.line([(mx - 35, my + 85), (mx + 35, my + 85)], fill=WHITE, width=8)
        lv = mouth_at(t)
        for i in range(3):
            if lv > 0.15 + i * 0.25:
                d.arc([mx - 90 - i * 28, my - 110 - i * 28, mx + 90 + i * 28, my + 30 + i * 28], 300, 345, fill=WHITE, width=6)

def sc_quiz(img, t):
    s = scene_at(t)["scene"]
    quiz_card(img, t, "q" if s == "q" else ("verdict" if s == "verdict" else "hook"))

SCENES = {"hook": sc_quiz, "tf": sc_quiz, "loop": sc_quiz, "true": sc_split, "false": sc_split,
          "cost": sc_cost, "zero": sc_cost, "verdict": sc_quiz, "q": sc_quiz}

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

CAP_Y = 1375
def draw_captions(img, t):
    for gs, ge, spk, toks in GROUPS:
        if gs <= t < ge: break
    else:
        return
    f = font(F_CAP, 92)
    widths = [f.getbbox(tk["text"], stroke_width=12)[2] - f.getbbox(tk["text"], stroke_width=12)[0] for tk in toks]
    space = 44
    lines, line, lw = [], [], 0
    for i, w_ in enumerate(widths):
        if line and lw + space + w_ > 940:
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
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 92, col, scale=gk * (1.05 if active else 1.0), stroke=12, sfill=(2, 26, 34))
            x += widths[i] + space

def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=CYAN)
    c = (170, 215, 222)
    for i, ln in enumerate(["Illustration: $1,000 balance kept all year at 22.15% APR (Fed G.19, Q2 2026 avg",
                            "for card accounts charged interest), interest paid monthly. Scores vary by",
                            "model & lender. Sources: myFICO, Federal Reserve. Not financial advice."]):
        d.text((W / 2, 1560 + 33 * i), ln, font=font(F_MED, 26), fill=c, anchor="mm")

def frame(t):
    global t_glob
    t_glob = t
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    badge(img, t)
    SCENES[s["scene"]](img, t)
    draw_ray(img, t)
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
