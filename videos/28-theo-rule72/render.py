"""THEO EXPLAINS #11: the Rule of 72. 1080x1920 @30fps. Pastel mint train station: split-flap departure board with the key numbers, a 0-72 year rail line with doubling stops and a little train carrying the balance, Theo (left) and Nora (right) on the platform."""
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
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(150, 80, 50, 50))
    img.alpha_composite(sh); img.alpha_composite(lay)



# ---------- palette (episode 11: pastel mint train station, navy split-flap board, rail timeline) ----------
NAVY = (26, 34, 62); NAVY2 = (40, 52, 90); FLAP = (255, 196, 64); FWHITE = (240, 244, 255)
FGREEN = (100, 230, 150); FRED = (255, 100, 100); FBLUE = (120, 190, 255)
TEAL_D = (34, 120, 112); INK2 = (30, 52, 66); CORAL = (240, 96, 90)
C_GREEN = (22, 150, 85)

BX0, BY0, BX1, BY1 = 40, 270, 1040, 685   # departure board
BC = W / 2
RX0, RX1, RY = 95, 985, 795                # rail: year 0 -> 72
R = 0.07; P0 = 10000.0
DBL = math.log(2) / math.log(1 + R)        # 10.2448 years
def val(y): return P0 * (1 + R) ** y
def rx(y): return RX0 + (RX1 - RX0) * y / 72

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    a = np.zeros((H, W, 3), np.float32)
    k = (yy / 860.0).clip(0, 1)[..., None]
    top = np.array((196, 238, 222), np.float32); bot = np.array((236, 250, 240), np.float32)
    a[:] = top * (1 - k) + bot * k
    im = Image.fromarray(a.astype(np.uint8)).convert("RGB"); d = ImageDraw.Draw(im)
    # arched glass roof ribs
    for i in range(-3, 4):
        cx = W / 2 + i * 330
        d.arc([cx - 360, -160, cx + 360, 560], 180, 360, fill=(170, 220, 205), width=10)
    for x in range(0, W, 90):
        d.line([(x, 0), (x, 250)], fill=(182, 228, 212), width=3)
    # iron pillars
    for px in (20, 1060):
        d.rectangle([px - 16, 0, px + 16, 870], fill=(120, 170, 160))
    # track bed behind the rail line
    d.rectangle([0, 760, W, 850], fill=(214, 236, 226))
    # platform floor (warm peach) + yellow safety line
    fk = ((yy - 850) / 1070.0).clip(0, 1)[..., None]
    fl = np.array((255, 232, 210), np.float32) * (1 - fk) + np.array((255, 214, 190), np.float32) * fk
    arr = np.array(im).astype(np.float32); arr[850:] = fl[850:]
    im = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(im)
    d.rectangle([0, 850, W, 866], fill=(255, 206, 70))
    for x in range(0, W, 60):
        d.rectangle([x, 851, x + 30, 865], fill=(240, 186, 50))
    for y0 in range(940, H, 150):   # floor tiles
        d.line([(0, y0), (W, y0)], fill=(244, 210, 186), width=3)
    return im
BG = make_bg()

def money(v): return f"${v:,.0f}"
def short(v):
    if v >= 1e6: return f"${v/1e6:.2f}M"
    return f"${v/1000:.0f}K"

def board(img, title, col=FLAP):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([BX0 + 8, BY0 + 12, BX1 + 8, BY1 + 14], radius=18, fill=(150, 200, 186))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=18, fill=TEAL_D)
    d.rounded_rectangle([BX0 + 14, BY0 + 14, BX1 - 14, BY1 - 14], radius=10, fill=NAVY)
    # hanging rods
    for x in (200, 880):
        d.rectangle([x - 5, BY0 - 30, x + 5, BY0], fill=(110, 150, 140))
    d.rectangle([BX0 + 14, BY0 + 14, BX1 - 14, BY0 + 92], fill=NAVY2)
    pop_text(img, (BC, BY0 + 54), title, F_NUM, 44, col)

def flap(img, y, s, col=FWHITE, size=56, k=1.0, x=None, width=None):
    """split-flap style row: tile + text + seam line"""
    if k <= 0.03: return
    f = font(F_NUM, size)
    tw_ = tw(s, F_NUM, size)
    wdt = width or tw_ + 60
    xc = x or BC
    hh = size * 0.78 * k
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([xc - wdt / 2, y - hh, xc + wdt / 2, y + hh], radius=10, fill=(16, 22, 44))
    pop_text(img, (xc, y), s, F_NUM, size, col, scale=min(1.0, 0.6 + 0.4 * k), alpha=clamp(k))
    d = ImageDraw.Draw(img)
    d.line([(xc - wdt / 2 + 4, y + 1), (xc + wdt / 2 - 4, y + 1)], fill=(10, 14, 30), width=3)

def kin(t, at, dur=0.28): return ease_back((t - at) / dur)

def stamp(img, s, xy, k, col=FRED, w=440, h=110, rot=-7, size=50):
    if k <= 0.05: return
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle([4, 4, w - 5, h - 5], radius=16, outline=col, width=9)
    pop_text(lay, (w / 2, h / 2), s, F_NUM, size, col)
    lay = lay.resize((max(2, int(w * k)), max(2, int(h * k)))).rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2)))

# ---------- board scenes ----------
def bd_hook(img, t):
    board(img, "THEO'S TICKET")
    blink = 0.65 + 0.35 * (math.sin(t * 8) > -0.3)
    rows = [("FROM  $10,000", FWHITE), ("TO    $20,000", FWHITE), ("AT    7% A YEAR", FBLUE)]
    for i, (s, c) in enumerate(rows):
        flap(img, 400 + i * 78, s, c, 48, width=700)
    flap(img, 620, "TIME  72 YEARS", FLAP if blink > 0.8 else (220, 160, 50), 60, width=760)

def bd_no(img, t):
    board(img, "THE RULE OF 72", FGREEN)
    flap(img, 395, "THEO: 72 YEARS", (150, 160, 190), 40, width=520)
    d = ImageDraw.Draw(img)
    if t > tok("no", 2):
        d.line([(BC - 230, 397), (BC + 230, 397)], fill=FRED, width=7)
    flap(img, 510, "72 ÷ 7 ≈ 10", FLAP, 92, k=kin(t, tok("no", 3)), width=760)
    flap(img, 625, "YEARS TO DOUBLE", FGREEN, 48, k=kin(t, tok("no", 6)), width=640)

def bd_ladder(img, t):
    board(img, "DOUBLING STOPS", FGREEN)
    rows = [("~10 YRS", "$20,000", 0), ("~20 YRS", "$40,000", 2), ("~31 YRS", "$80,000", 4)]
    for i, (a, b, ti) in enumerate(rows):
        k = kin(t, tok("ladder", ti) - 0.05) if i else 1.0
        y = 400 + i * 105
        flap(img, y, a, FWHITE, 52, k=k, x=340, width=380)
        flap(img, y, b, FGREEN, 60, k=k, x=740, width=420)

def bd_big(img, t):
    board(img, "YEAR 72", FGREEN)
    s0 = tok("big", 1)
    n = int(clamp((t - s0 + 0.1) / 1.2) * 7)
    d = ImageDraw.Draw(img)
    for i in range(7):     # seven doubling chips
        x = BC + (i - 3) * 118
        on = i < n
        d.rounded_rectangle([x - 50, 352, x + 50, 422], radius=12, fill=(60, 150, 100) if on else (36, 46, 80))
        pop_text(img, (x, 387), "x2", F_NUM, 40, FWHITE if on else (90, 100, 140))
    flap(img, 500, "7 DOUBLINGS", FWHITE, 46, k=kin(t, tok("big", 2) - 0.1), width=520)
    flap(img, 612, "$1,305,065", FGREEN, 96, k=kin(t, tok("big", 3)), width=780)

def bd_punch(img, t):
    board(img, "THE RULE OF 72", FLAP)
    flap(img, 405, "72 ÷ YOUR RATE", FWHITE, 62, width=720)
    flap(img, 515, "= YEARS TO DOUBLE", FGREEN, 52, width=720)
    stamp(img, "NOT A DEADLINE", (BC, 622), kin(t, tok("punch", 5), 0.25), FRED, 560, 100, -4, 52)

def bd_fix(img, t):
    board(img, "TRY ANOTHER RATE", FLAP)
    flap(img, 405, "7%   72 ÷ 7  ≈ 10 YRS", (150, 160, 190), 46, width=820)
    k = kin(t, seg_start("fix") + 0.1)
    flap(img, 505, "6%   72 ÷ 6  = 12 YRS", FLAP, 50, k=k, width=820)
    pop_text(img, (BC, 610), "A quick estimate. Real returns vary.", F_HAND, 34, (170, 180, 210), alpha=clamp(k))

def bd_q(img, t):
    board(img, "YOUR RATE?", FLAP)
    blink = (math.sin(t * 7) > 0)
    flap(img, 440, "72 ÷ ___ = ?", FLAP if blink else FWHITE, 92, width=700)
    flap(img, 590, "TELL US BELOW", FGREEN, 58, k=kin(t, tok("q", 4) - 0.05), width=620)

BOARDS = {"hook": bd_hook, "no": bd_no, "ladder": bd_ladder, "big": bd_big, "punch": bd_punch,
          "fix": bd_fix, "q": bd_q, "loop": bd_hook}

# ---------- rail line + train ----------
def train_year(t):
    s = scene_at(t)["scene"]
    if s == "hook":
        return 0.0
    if s == "no":
        return DBL * ease_out((t - tok("no", 6)) / 0.7)
    if s == "ladder":
        y = DBL
        if t >= tok("ladder", 2) - 0.1: y = lerp(DBL, 2 * DBL, ease_out((t - tok("ladder", 2) + 0.1) / 0.5))
        if t >= tok("ladder", 4) - 0.1: y = lerp(2 * DBL, 3 * DBL, ease_out((t - tok("ladder", 4) + 0.1) / 0.5))
        return y
    if s == "big":
        return lerp(3 * DBL, 72, ease_out((t - tok("big", 1) + 0.1) / 1.4))
    if s == "loop":
        return lerp(72, 0, ease_out((t - seg_start("loop")) / 0.5))
    return 72.0

def rail(img, t):
    d = ImageDraw.Draw(img)
    yr = train_year(t)
    s = scene_at(t)["scene"]
    # sleepers + rails
    for x in range(RX0 - 40, RX1 + 50, 26):
        d.rectangle([x, RY - 6, x + 12, RY + 18], fill=(170, 140, 120))
    d.line([(RX0 - 50, RY), (RX1 + 60, RY)], fill=(110, 120, 130), width=6)
    d.line([(RX0 - 50, RY + 12), (RX1 + 60, RY + 12)], fill=(110, 120, 130), width=6)
    # year ticks
    for y, lab in ((0, "YR 0"), (72, "YR 72")):
        d.text((rx(y), RY + 40), lab, font=font(F_NUM, 24), fill=INK2, anchor="mm")
    # doubling stops
    for kk in range(1, 8):
        y = kk * DBL; x = rx(y)
        passed = yr >= y - 0.05
        d.ellipse([x - 11, RY - 5, x + 11, RY + 17], fill=C_GREEN if passed else (190, 205, 200), outline=WHITE, width=3)
        if passed and s not in ("hook",) and 1 <= kk <= 6:
            d.text((x, RY + 40), short(P0 * 2 ** kk), font=font(F_NUM, 24), fill=C_GREEN, anchor="mm")
    # Theo's imagined ride: one stop at year 72
    if s in ("hook", "loop"):
        k = ease_out((t - (0.3 if s == "hook" else seg_start("loop"))) / 0.8)
        x1 = lerp(rx(0) + 70, rx(72), k)
        for x in range(int(rx(0) + 70), int(x1), 34):
            d.line([(x, RY - 34), (x + 18, RY - 34)], fill=(40, 80, 200), width=6)
        if k > 0.9:
            d.rounded_rectangle([rx(72) - 74, RY - 70, rx(72) + 20, RY - 36], radius=16, fill=(40, 80, 200))
            d.text((rx(72) - 27, RY - 53), "$20K?", font=font(F_NUM, 26), fill=WHITE, anchor="mm")
    # train
    x = rx(yr)
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dt = ImageDraw.Draw(tl)
    bx0, bx1, by0, by1 = x - 62, x + 30, RY - 50, RY - 4
    dt.rounded_rectangle([bx0, by0, bx1, by1], radius=12, fill=CORAL)
    dt.rounded_rectangle([bx1 - 6, by0 + 12, bx1 + 30, by1], radius=10, fill=(220, 70, 70))
    dt.rectangle([bx0 + 12, by0 - 18, bx0 + 28, by0], fill=NAVY)
    for wx in (bx0 + 18, bx0 + 50):
        dt.rounded_rectangle([wx - 10, by0 + 9, wx + 10, by0 + 25], radius=4, fill=(220, 245, 255))
    for wx in (bx0 + 16, bx0 + 48, bx1 + 12):
        dt.ellipse([wx - 10, by1 - 8, wx + 10, by1 + 12], fill=NAVY)
    img.alpha_composite(tl)
    d = ImageDraw.Draw(img)
    v = val(yr)
    lab = money(round(v, -1) if yr > 0 else v) if yr < 71.99 else "$1,305,065"
    wl = tw(lab, F_NUM, 32)
    tx = min(max(x - 16, wl / 2 + 30), W - wl / 2 - 30)
    ty = RY - 88
    d.rounded_rectangle([tx - wl / 2 - 16, ty - 24, tx + wl / 2 + 16, ty + 24], radius=24, fill=C_GREEN if yr > 0.5 else (40, 80, 200))
    d.text((tx, ty), lab, font=font(F_NUM, 32), fill=WHITE, anchor="mm")

STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("shrug", "worried", "point_up", "smile"),
         "ladder": ("idle", "smile", "marker", "smile"), "big": ("cheer", "smile", "point_up", "smile"),
         "punch": ("shrug", "worried", "facepalm", "facepalm"), "fix": ("idle", "smile", "marker", "smile"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("cheer", "smug", "idle", "worried")}

TX_, NX_, CYC = 160, 920, 1100

def ticket(img, t):
    """Theo's paper ticket in the hook/loop"""
    s = scene_at(t)["scene"]
    if s not in ("hook", "loop"): return
    lay = Image.new("RGBA", (230, 120), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle([4, 4, 226, 116], radius=12, fill=(255, 250, 230), outline=(200, 170, 120), width=4)
    dl.text((115, 36), "ADMIT ONE", font=font(F_MED, 22), fill=(150, 120, 80), anchor="mm")
    dl.text((115, 80), "72 YRS", font=font(F_NUM, 40), fill=(40, 80, 200), anchor="mm")
    lay = lay.rotate(12 + 4 * math.sin(t * 4), expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(TX_ + 120), int(CYC - 300)))

def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("T", TX_, THEO, tp, tm), ("N", NX_, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.2 if who == spk else 1.12
        person(img, cx, CYC + (0 if who == spk else 10), sc, col, who, t, talk=talking, pose=pose, mood=mood)
    ticket(img, t)
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

CAP_Y = 1395
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
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 90, col, scale=gk * (1.05 if active else 1.0), stroke=12, sfill=(20, 40, 52))
            x += widths[i] + space

def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=CORAL)
    lab1, lab2 = "THEO EXPLAINS #11", "RULE OF 72"
    f1 = font(F_NUM, 42)
    w1 = tw(lab1, F_NUM, 42) + 46; w2 = tw(lab2, F_NUM, 42) + 46
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 165, x0 + w1 + 30, 243], radius=39, fill=THEO)
    d.rounded_rectangle([x0 + w1, 165, x0 + total, 243], radius=39, fill=INK2)
    d.rectangle([x0 + w1, 165, x0 + w1 + 30, 243], fill=INK2)
    d.text((x0 + w1 / 2, 204), lab1, font=f1, fill=INK2, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 204), lab2, font=f1, fill=YEL, anchor="mm")
    c = INK2
    d.text((W / 2, 1530), "Example: $10,000 at 7% a year, compounded yearly. Rule of 72", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1566), "is an estimate. No fees, taxes or deposits. Returns vary and can", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1602), "be negative. Not a forecast. Not financial advice.", font=font(F_MED, 27), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    BOARDS[s["scene"]](img, t)
    rail(img, t)
    draw_cast(img, t)
    draw_captions(img, t)
    draw_ui(img, t)
    return img.convert("RGB")

if __name__ == "__main__":
    if PREVIEW:
        for tt in PREVIEW:
            frame(tt).save(os.path.join(HERE, f"prev_{tt:05.2f}.png"))
        sys.exit()
    out = os.path.join(HERE, "video_noaudio.tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0: print("frame", i, "/", NF, flush=True)
    p.stdin.close(); rc = p.wait()
    if rc == 0:
        os.replace(out, os.path.join(HERE, "video_noaudio.mp4"))
    print("done", rc)
