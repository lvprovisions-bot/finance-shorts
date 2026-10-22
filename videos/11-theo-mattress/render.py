"""THEO EXPLAINS #2: Inflation (mattress money). 1080x1920 @30fps. Pastel mint, slate chalkboard, Nora left / Theo right, mattress prop."""
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
        side = 1 if cx < W / 2 else -1
        arm(sh_r if side > 0 else sh_l, (cx + side * 150 * s, cy - 190 * s + wv * 0.3))
        arm(sh_l if side > 0 else sh_r, (cx - side * 120 * s, cy + 120 * s))
    elif pose == "shrug":
        arm(sh_l, (cx - 175 * s, cy - 70 * s + wv * 0.4)); arm(sh_r, (cx + 175 * s, cy - 70 * s - wv * 0.4))
    elif pose == "cheer":
        arm(sh_l, (cx - 140 * s, cy - 165 * s + wv * 0.5)); arm(sh_r, (cx + 140 * s, cy - 165 * s - wv * 0.5))
    elif pose == "facepalm":
        arm(sh_l, (cx - 120 * s, cy + 120 * s)); arm(sh_r, (cx + 20 * s, cy - 110 * s))
    elif pose == "marker":      # Nora holding a marker towards the board
        side = 1 if cx < W / 2 else -1
        p1 = (cx + side * 160 * s, cy - 150 * s + wv * 0.3)
        arm(sh_r if side > 0 else sh_l, p1)
        d.rounded_rectangle([p1[0] - 9 * s, p1[1] - 60 * s, p1[0] + 9 * s, p1[1] - 10 * s], radius=6 * s, fill=RED)
        arm(sh_l if side > 0 else sh_r, (cx - side * 110 * s, cy + 125 * s))
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
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(30, 90, 70, 50))
    img.alpha_composite(sh); img.alpha_composite(lay)


# ---------- palette (episode 2: mint + slate chalkboard) ----------
CH_W = (242, 242, 232); CH_Y = (255, 226, 110); CH_P = (255, 130, 150); CH_G = (130, 232, 160); CH_B = (140, 205, 255)
SLATE = (40, 56, 54); WOOD = (160, 108, 62); WOOD2 = (120, 78, 42)
BILL = (120, 190, 120); BILL2 = (70, 140, 80)

# ---------- background: pastel mint with soft diagonal stripes ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((226, 248, 236), np.float32); bot = np.array((200, 238, 220), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    stripes = (((xx + yy) // 70) % 2 == 0).astype(np.float32)
    img -= stripes[..., None] * 6
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - 1050) * 1.2) ** 2) / 800
    img += (np.clip(1 - d, 0, 1) ** 2)[..., None] * 12
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

# chalk grain: a fixed noise mask multiplied into chalk text alpha
_rng = np.random.default_rng(3)
GRAIN = Image.fromarray((np.clip(_rng.random((H, W)) * 1.4, 0.55, 1.0) * 255).astype(np.uint8))

def chalk(img, xy, s, size, fill, scale=1.0, path=None):
    path = path or F_HAND
    if scale <= 0.01 or size * scale < 2:
        return
    f = font(path, size * scale)
    l, t, r, b = f.getbbox(s)
    pad = 10
    w_, h_ = r - l + pad * 2, b - t + pad * 2
    layer = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - l, pad - t), s, font=f, fill=fill + (255,))
    x, y = int(xy[0] - w_ / 2), int(xy[1] - h_ / 2)
    gx, gy = max(0, min(W - w_, x)), max(0, min(H - h_, y))
    if w_ <= W and h_ <= H:
        g_ = GRAIN.crop((gx, gy, gx + w_, gy + h_))
        a_ = Image.fromarray((np.asarray(layer.getchannel("A"), np.float32) * np.asarray(g_, np.float32) / 255).astype(np.uint8))
        layer.putalpha(a_)
    img.alpha_composite(layer, (x, y))

# ---------- chalkboard ----------
BX0, BY0, BX1, BY1 = 60, 285, 1020, 775
def board(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([BX0 + 10, BY0 + 14, BX1 + 10, BY1 + 14], radius=22, fill=(20, 70, 50, 55))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=22, fill=WOOD)
    d.rounded_rectangle([BX0 + 22, BY0 + 22, BX1 - 22, BY1 - 22], radius=10, fill=SLATE)
    d.rectangle([BX0 + 100, BY1 - 6, BX1 - 100, BY1 + 12], fill=WOOD2)  # chalk tray
    d.rounded_rectangle([BX0 + 150, BY1 - 14, BX0 + 215, BY1 - 2], radius=5, fill=(250, 250, 245))
    d.rounded_rectangle([BX0 + 240, BY1 - 14, BX0 + 300, BY1 - 2], radius=5, fill=CH_Y)
    sm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sm)
    for i in range(6):  # faint eraser smudges
        x = 150 + i * 150; y = 360 + (i % 3) * 120
        sd.ellipse([x - 90, y - 30, x + 90, y + 30], fill=(255, 255, 255, 9))
    lay.alpha_composite(sm)
    img.alpha_composite(lay)

def stamp(img, cx, cy, s, text, col, angle=-12, back=None):
    if s < 0.03: return
    f = font(F_NUM, 120 * s); l, t, r, b = f.getbbox(text)
    w, h = r - l + 70 * s, b - t + 50 * s
    lay = Image.new("RGBA", (int(w + 40), int(h + 40)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=20 * s, fill=back + (255,) if back else None, outline=col + (255,), width=max(2, int(12 * s)))
    d.text((20 + w / 2, 20 + h / 2), text, font=f, fill=col + (255,), anchor="mm")
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def bill(img, cx, cy, s, label=None, ghost=False):
    """a cartoon banknote, s = scale (1.0 = 520x250)."""
    if s < 0.03: return
    w, h = 520 * s, 250 * s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if ghost:
        for k in range(0, int(2 * (w + h)), 28):  # dashed outline
            pass
        d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=max(1, 18 * s), outline=CH_W + (150,), width=4)
        img.alpha_composite(lay); return
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=max(1, 18 * s), fill=BILL + (255,), outline=BILL2 + (255,), width=max(2, int(8 * s)))
    d.rounded_rectangle([cx - w / 2 + 22 * s, cy - h / 2 + 22 * s, cx + w / 2 - 22 * s, cy + h / 2 - 22 * s], radius=max(1, 12 * s), outline=(230, 250, 230, 255), width=max(2, int(4 * s)))
    d.ellipse([cx - 80 * s, cy - 80 * s, cx + 80 * s, cy + 80 * s], fill=(200, 240, 200, 255), outline=BILL2 + (255,), width=max(2, int(5 * s)))
    img.alpha_composite(lay)
    if label:
        pop_text(img, (cx, cy), label, F_NUM, 92 * s, (30, 90, 40))
    else:
        pop_text(img, (cx, cy), "$", F_NUM, 110 * s, (30, 90, 40))

def hook_board(img, t):
    chalk(img, (W / 2, 375), "$10,000", 130, CH_G, path=F_NUM)
    chalk(img, (W / 2, 520), "IN THE MATTRESS", 66, CH_W)
    chalk(img, (W / 2, 640), "= SAFE FOREVER!", 78, CH_Y)

def bd_hook(img, t):
    hook_board(img, t)

def bd_no(img, t):
    hook_board(img, t)
    s0 = seg_start("no"); ts = tok("no", 1)
    k = ease_out((t - s0) / 0.3)
    if k > 0.05:  # chalk strike through "SAFE FOREVER"
        ImageDraw.Draw(img).line([(250, 645), (250 + 590 * k, 630)], fill=CH_P, width=14)
    if t > ts - 0.1:
        stamp(img, W / 2, 470, 0.72 * ease_back((t - ts + 0.1) / 0.3), "SHRINKING", RED, angle=-8, back=(255, 255, 255))

def bd_still(img, t):
    s0 = seg_start("still")
    bill(img, W / 2, 500, 1.15 * ease_back((t - s0) / 0.35), "$10,000")
    chalk(img, (W / 2, 690), "the number never changes...", 46, CH_W, scale=ease_out((t - tok("still", 1)) / 0.3) if t > tok("still", 1) else 0)

def bd_year(img, t):
    chalk(img, (W / 2, 350), "LAST 12 MONTHS", 50, CH_W)
    ts = tok("year", 1)
    if t > ts - 0.1:
        k = ease_back((t - ts + 0.1) / 0.3)
        chalk(img, (W / 2 + 40, 440), "PRICES +3.7%", 84, CH_P, scale=k)
        d = ImageDraw.Draw(img)  # up arrow
        ax, ay = 205, 440
        if k > 0.3:
            d.polygon([(ax, ay - 46 * k), (ax - 34 * k, ay + 4), (ax + 34 * k, ay + 4)], fill=CH_P)
            d.rectangle([ax - 13 * k, ay, ax + 13 * k, ay + 42 * k], fill=CH_P)
    tb = tok("year", 3)
    if t > tb - 0.1:
        k = ease_out((t - tb + 0.1) / 0.3)
        chalk(img, (W / 2, 545), "$10,000 NOW BUYS WHAT", 52, CH_W, scale=k)
    tn = tok("year", 4)
    if t > tn:
        k = ease_back((t - tn) / 0.35)
        chalk(img, (W / 2, 640), "$9,643", 108, CH_Y, scale=k, path=F_NUM)
        chalk(img, (W / 2, 728), "BOUGHT A YEAR AGO  (BLS CPI, SEP 2026)", 30, CH_B, scale=k)

def bd_ten(img, t):
    t0, t1 = tok("ten", 2), tok("ten", 5) + 0.3
    u = clamp((t - t0) / (t1 - t0))
    yrs = 10 * ease_out(u) if u < 1 else 10.0
    yd = int(yrs + 1e-6)
    val = 10000 / 1.03 ** yd
    chalk(img, (W / 2, 340), "AT 3% A YEAR", 48, CH_W)
    s = math.sqrt(val / 10000)
    bill(img, 330, 515, 0.82, ghost=True)
    bill(img, 330, 515, 0.82 * s)
    chalk(img, (330, 650), f"YEAR {yd}", 44, CH_W)
    shown = int(round(val))
    chalk(img, (760, 470), "BUYS LIKE", 44, CH_W)
    chalk(img, (760, 560), f"${shown:,}", 104, CH_Y if u < 1 else CH_G, path=F_NUM)
    chalk(img, (760, 645), "TODAY", 44, CH_W)
    # mini timeline
    d = ImageDraw.Draw(img)
    x0, x1, yl = 140, 940, 715
    d.line([(x0, yl), (x1, yl)], fill=(200, 210, 200), width=4)
    d.line([(x0, yl), (x0 + (x1 - x0) * yrs / 10, yl)], fill=CH_Y, width=8)
    for i in range(11):
        x = x0 + (x1 - x0) * i / 10
        d.ellipse([x - 6, yl - 6, x + 6, yl + 6], fill=CH_Y if i <= yrs + 0.01 else (200, 210, 200))

def bd_thief(img, t):
    s0 = seg_start("thief")
    chalk(img, (W / 2, 350), "INFLATION QUIETLY TOOK", 52, CH_W)
    ts = tok("thief", 1)
    if t > ts - 0.1:
        stamp(img, W / 2, 500, 1.0 * ease_back((t - ts + 0.1) / 0.35), "-$2,559", RED, angle=-4, back=(255, 255, 255))
    d = ImageDraw.Draw(img)  # tiptoe footprints across the board
    n = int(clamp((t - s0) / 2.2) * 8)
    for i in range(n):
        x = 160 + i * 105; y = 680 + (12 if i % 2 else -12)
        d.ellipse([x - 16, y - 24, x + 16, y + 20], fill=(210, 215, 205))
        for j in range(3):
            d.ellipse([x - 16 + j * 12, y - 40, x - 8 + j * 12, y - 30], fill=(210, 215, 205))

def bd_power(img, t):
    s0 = seg_start("power")
    chalk(img, (W / 2, 350), "CASH KEEPS ITS...", 52, CH_W)
    rows = [(s0, "NUMBER", "$10,000", CH_G, True), (tok("power", 2), "POWER", "$7,441", CH_P, False)]
    for i, (ts, a, b, c, ok) in enumerate(rows):
        if t < ts - 0.1: continue
        k = ease_back((t - ts + 0.1) / 0.3)
        y = 470 + i * 150
        chalk(img, (300, y), a, 70, CH_W, scale=k)
        chalk(img, (690, y), b, 84, c, scale=k, path=F_NUM)
        d = ImageDraw.Draw(img); x = 900
        if k > 0.6:
            if ok:
                d.line([(x - 26, y), (x - 6, y + 24), (x + 32, y - 28)], fill=CH_G, width=12)
            else:
                d.line([(x - 26, y - 26), (x + 26, y + 26)], fill=CH_P, width=12); d.line([(x + 26, y - 26), (x - 26, y + 26)], fill=CH_P, width=12)

def bd_punch(img, t):
    s0 = seg_start("punch")
    chalk(img, (W / 2, 350), "THEO'S FIX:", 56, CH_W)
    ts = tok("punch", 2)
    if t > ts - 0.1:
        k = ease_back((t - ts + 0.1) / 0.35)
        mattress(img, W / 2, 545, 1.6 * k, cash=True)
        chalk(img, (W / 2, 700), "BIGGER MATTRESS", 72, CH_Y, scale=k)
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate([(170, 360), (910, 360), (150, 600), (930, 600)]):
        r = 22 + 6 * math.sin(t * 8 + i)
        pts = [(x + r * math.cos(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45),
                y + r * math.sin(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45)) for a in range(10)]
        d.polygon(pts, fill=CH_Y)

def bd_q(img, t):
    s0 = seg_start("q")
    chalk(img, (W / 2, 350), "WHERE DOES YOUR CASH SLEEP?", 50, CH_W)
    d = ImageDraw.Draw(img)
    opts = [("MATTRESS", CH_P), ("BANK", CH_B), ("INVESTED", CH_G)]
    for i, (lab, col) in enumerate(opts):
        x = 225 + i * 315; y = 520
        k = ease_back((t - s0 - 0.12 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([x - 140 * k, y - 75 * k, x + 140 * k, y + 75 * k], radius=24 * k, outline=col, width=max(2, int(8 * k)))
        chalk(img, (x, y), lab, 40, col, scale=k)
    if t > tok("q", 3) - 0.1:
        chalk(img, (W / 2, 690), "TELL US BELOW", 64, CH_Y, scale=ease_back((t - tok("q", 3) + 0.1) / 0.3), path=F_NUM)

# ---------- mattress prop ----------
def mattress(img, cx, cy, s, cash=True):
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 300 * s, 80 * s
    if cash:  # bills poking out of the top seam
        for i, dx in enumerate((-90, -30, 40, 100)):
            ang = (-14, 8, -6, 16)[i]
            b = Image.new("RGBA", (int(110 * s) + 4, int(55 * s) + 4), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
            bd.rounded_rectangle([2, 2, 110 * s, 55 * s], radius=max(1, 6 * s), fill=BILL + (255,), outline=BILL2 + (255,), width=max(1, int(3 * s)))
            bd.ellipse([55 * s - 12 * s, 28 * s - 12 * s, 55 * s + 12 * s, 28 * s + 12 * s], outline=BILL2 + (255,), width=max(1, int(2 * s)))
            b = b.rotate(ang, expand=True, resample=Image.BICUBIC)
            lay.alpha_composite(b, (int(cx + dx * s - b.width / 2), int(cy - h / 2 - b.height * 0.55)))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=max(1, 30 * s), fill=(250, 245, 235, 255), outline=(150, 140, 170, 255), width=max(2, int(5 * s)))
    for i in range(1, 6):  # quilting stitches
        x = cx - w / 2 + w * i / 6
        d.ellipse([x - 5 * s, cy - 5 * s, x + 5 * s, cy + 5 * s], fill=(170, 160, 200, 255))
    d.line([cx - w / 2 + 20 * s, cy - h / 2 + 14 * s, cx + w / 2 - 20 * s, cy - h / 2 + 14 * s], fill=(200, 190, 220, 255), width=max(1, int(3 * s)))
    img.alpha_composite(lay)

BOARDS = {"hook": bd_hook, "no": bd_no, "still": bd_still, "year": bd_year, "ten": bd_ten, "thief": bd_thief,
          "power": bd_power, "punch": bd_punch, "q": bd_q, "loop": lambda img, t: hook_board(img, t)}
# per-scene staging: (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "smile", "marker", "smile"),
         "still": ("point_up", "smug", "idle", "smile"), "year": ("idle", "worried", "marker", "smile"),
         "ten": ("idle", "worried", "point_up", "smile"), "thief": ("shrug", "worried", "idle", "smile"),
         "power": ("idle", "worried", "marker", "smile"), "punch": ("cheer", "smug", "facepalm", "facepalm"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("cheer", "smug", "idle", "worried")}

NX, TX, CY = 290, 790, 1035
def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("T", TX, THEO, tp, tm), ("N", NX, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.40 if who == spk else 1.28
        person(img, cx, CY + (0 if who == spk else 18) - (30 if who == "T" else 0), sc, col, who, t, talk=talking, pose=pose, mood=mood)
    mattress_front(img, t)

def mattress_front(img, t):
    # front edge of the mattress drawn over Theo's legs so he looks like he stands behind it
    mattress(img, TX + 10, CY + 200, 1.0, cash=True)

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

CAP_Y = 1385
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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=(30, 170, 130))
    lab1, lab2 = "THEO EXPLAINS #2", "INFLATION"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=SLATE)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=SLATE)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=INK, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (40, 95, 75)
    d.text((W / 2, 1515), "Illustration: $10,000 cash earning 0%. 10-year view assumes 3% inflation a year.", font=font(F_MED, 25), fill=c, anchor="mm")
    d.text((W / 2, 1550), "Last-year figure: US CPI-U +3.7%, 12 months to Sep 2026 (Source: BLS).", font=font(F_MED, 25), fill=c, anchor="mm")
    d.text((W / 2, 1585), "Not financial advice.", font=font(F_MED, 25), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    board(img)
    BOARDS[s["scene"]](img, t)
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
