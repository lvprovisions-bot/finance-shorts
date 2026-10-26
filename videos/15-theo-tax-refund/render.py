"""THEO EXPLAINS #4: Tax refunds. 1080x1920 @30fps. Pastel sky + clouds, marquee lightbox sign with chasing bulbs, Nora left / Theo right, refund cheque, month calendar, IRS piggy bank."""
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



# ---------- palette (episode 4: pastel sky + clouds, marquee lightbox sign with bulbs) ----------
FRAME_C = (36, 40, 62); PANEL = (255, 253, 244); BULB_ON = (255, 214, 90); BULB_OFF = (210, 190, 140)
M_NAVY = (34, 52, 110); M_RED = (222, 56, 64); M_GREEN = (22, 150, 90); M_TEAL = (20, 140, 170); M_ORG = (240, 130, 40)
M_PINK = (240, 120, 160); CHEQUE = (226, 246, 232); CHEQUE_L = (150, 200, 170)

# ---------- background: pastel sky blue with soft clouds ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((196, 228, 255), np.float32); bot = np.array((232, 244, 255), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    rng = np.random.default_rng(4)
    for _ in range(9):
        cx, cy = rng.uniform(-100, W + 100), rng.uniform(80, 1800)
        for j in range(5):
            bx, by, r = cx + (j - 2) * 70 + rng.uniform(-20, 20), cy + rng.uniform(-30, 20), rng.uniform(55, 95)
            dd = np.sqrt(((xx - bx) / 1.3) ** 2 + (yy - by) ** 2) / r
            img += (np.clip(1 - dd, 0, 1) ** 0.35)[..., None] * (np.array((255, 255, 255), np.float32) - img) * 0.55
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

def marker(img, xy, s, size, fill, scale=1.0, path=None):
    pop_text(img, xy, s, path or F_NUM, size, fill, scale=scale)

# ---------- marquee lightbox sign ----------
BX0, BY0, BX1, BY1 = 70, 300, 1010, 800
def board(img, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([BX0 + 14, BY0 + 18, BX1 + 14, BY1 + 18], radius=40, fill=(60, 90, 140, 60))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=40, fill=FRAME_C)
    d.rounded_rectangle([BX0 + 46, BY0 + 46, BX1 - 46, BY1 - 46], radius=18, fill=PANEL)
    # bulbs around the frame, chasing
    pts = []
    n_top = 15; n_side = 8
    for i in range(n_top):
        x = BX0 + 40 + i * (BX1 - BX0 - 80) / (n_top - 1); pts += [(x, BY0 + 23)]
    for i in range(1, n_side):
        y = BY0 + 23 + i * (BY1 - BY0 - 46) / n_side; pts += [(BX1 - 23, y)]
    for i in range(n_top - 1, -1, -1):
        x = BX0 + 40 + i * (BX1 - BX0 - 80) / (n_top - 1); pts += [(x, BY1 - 23)]
    for i in range(n_side - 1, 0, -1):
        y = BY0 + 23 + i * (BY1 - BY0 - 46) / n_side; pts += [(BX0 + 23, y)]
    ph = int(t * 8)
    for i, (x, y) in enumerate(pts):
        on = (i + ph) % 3 != 0
        c = BULB_ON if on else BULB_OFF
        if on: d.ellipse([x - 17, y - 17, x + 17, y + 17], fill=(255, 230, 140, 90))
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=c)
    img.alpha_composite(lay)

def stamp(img, cx, cy, s, text, col, angle=-12, back=None, size=120):
    if s < 0.03: return
    f = font(F_NUM, size * s); l, t, r, b = f.getbbox(text)
    w, h = r - l + 70 * s, b - t + 50 * s
    lay = Image.new("RGBA", (int(w + 40), int(h + 40)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=20 * s, fill=back + (255,) if back else None, outline=col + (255,), width=max(2, int(12 * s)))
    d.text((20 + w / 2, 20 + h / 2), text, font=f, fill=col + (255,), anchor="mm")
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def cheque(img, cx, cy, s, t, label="BONUS?!"):
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def R(x0, y0, x1, y1): return [cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s]
    d.rounded_rectangle(R(-380, -175, 380, 175), radius=max(1, 22 * s), fill=CHEQUE, outline=CHEQUE_L, width=max(2, int(6 * s)))
    for k in range(6):
        d.line([cx - 370 * s, cy + (-140 + k * 9) * s, cx + 370 * s, cy + (-140 + k * 9) * s], fill=(205, 232, 214), width=max(1, int(2 * s)))
    img.alpha_composite(lay)
    pop_text(img, (cx - 210 * s, cy - 95 * s), "TAX REFUND", F_NUM, 44 * s, M_NAVY)
    pop_text(img, (cx, cy + 15 * s), "$3,273", F_NUM, 150 * s, M_GREEN)
    d = ImageDraw.Draw(img)
    d.line([cx - 330 * s, cy + 120 * s, cx + 330 * s, cy + 120 * s], fill=(120, 150, 130), width=max(1, int(3 * s)))
    pop_text(img, (cx + 150 * s, cy + 147 * s), "to Theo · memo: " + label, F_HAND, 30 * s, M_PINK)

MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
def calendar(img, t, k_fill, show_amt=True, top=375):
    d = ImageDraw.Draw(img)
    cw, ch, gx, gy = 196, 108, 18, 16
    x0 = W / 2 - (4 * cw + 3 * gx) / 2
    filled = int(k_fill * 12 + 1e-6)
    for i, m in enumerate(MONTHS):
        r, c = divmod(i, 4)
        x, y = x0 + c * (cw + gx), top + r * (ch + gy)
        on = i < filled
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=16, fill=(255, 236, 236) if on else (240, 240, 246), outline=M_RED if on else (200, 200, 214), width=4)
        d.rectangle([x + 4, y + 4, x + cw - 4, y + 34], fill=M_RED if on else (200, 200, 214))
        pop_text(img, (x + cw / 2, y + 19), m, F_NUM, 24, WHITE)
        if on and show_amt:
            pop_text(img, (x + cw / 2, y + 70), "-$273", F_NUM, 40, M_RED)
    return x0

def bd_hook(img, t):
    cheque(img, W / 2, 545, 1.0, t)
    stamp(img, 790, 395, 0.5, "BONUS!", M_ORG, angle=10, back=(255, 255, 255))

def bd_no(img, t):
    cheque(img, W / 2, 545, 1.0, t, label="your own money")
    ts = tok("no", 2)
    if t > ts - 0.1:
        stamp(img, W / 2, 560, 0.55 * ease_back((t - ts + 0.1) / 0.3), "YOUR OWN MONEY", M_RED, angle=-8, back=(255, 255, 255))

def bd_over(img, t):
    s0 = seg_start("over"); te = tok("over", 2) + 0.5
    calendar(img, t, clamp((t - s0) / (te - s0)), show_amt=False, top=370)
    if t > tok("over", 1) - 0.1:
        k = ease_back((t - tok("over", 1) + 0.1) / 0.3)
        stamp(img, W / 2, 500, 0.6 * k, "OVERPAID", M_RED, angle=-5, back=(255, 255, 255))
    if t > tok("over", 5) - 0.15:
        k = ease_back((t - tok("over", 5) + 0.15) / 0.3)
        stamp(img, W / 2, 640, 0.45 * k, "...SENT BACK IN SPRING", M_TEAL, angle=-4, back=(255, 255, 255))

def bd_ask(img, t):
    marker(img, (W / 2, 450), "$3,273", 120, M_GREEN)
    marker(img, (W / 2, 590), "÷ 12 MONTHS = ?", 80, M_NAVY)

def bd_month(img, t):
    s0 = seg_start("month")
    calendar(img, t, clamp((t - s0) / 1.4), show_amt=True, top=330)
    tz = tok("month", 5)
    if t > tz - 0.1:
        stamp(img, W / 2, 545, 0.62 * ease_back((t - tz + 0.1) / 0.3), "INTEREST: $0", M_NAVY, angle=-6, back=(255, 255, 255))

def bd_loan(img, t):
    s0 = seg_start("loan")
    d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.3)
    marker(img, (W / 2, 385), "LOAN AGREEMENT", 64, M_NAVY, scale=k)
    rows = [("LENDER:", "THEO"), ("BORROWER:", "THE IRS"), ("AMOUNT:", "$3,273"), ("INTEREST:", "0%")]
    for i, (a, b) in enumerate(rows):
        if t < s0 + 0.2 + 0.18 * i: continue
        y = 470 + i * 66
        pop_text(img, (180, y), a, F_MED, 46, (100, 106, 130), anchor_c=False)
        pop_text(img, (520, y), b, F_NUM, 50, M_RED if b == "0%" else (M_GREEN if "$" in b else M_NAVY), anchor_c=False)
        d.line([(510, y + 32), (880, y + 32)], fill=(210, 210, 222), width=3)

def bd_tip(img, t):
    s0 = seg_start("tip"); d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.3)
    # little W-4 form card
    if k > 0.05:
        x, y = 200, 520
        d.rounded_rectangle([x - 110 * k, y - 140 * k, x + 110 * k, y + 140 * k], radius=14 * k, fill=WHITE, outline=M_NAVY, width=max(2, int(5 * k)))
        pop_text(img, (x, y - 90 * k), "W-4", F_NUM, 70 * k, M_NAVY)
        for j in range(4):
            d.line([x - 80 * k, y + (-20 + j * 40) * k, x + 80 * k, y + (-20 + j * 40) * k], fill=(200, 200, 214), width=max(1, int(4 * k)))
        if t > tok("tip", 1):
            d.line([x - 70 * k, y + 20 * k, x - 35 * k, y + 55 * k, x + 70 * k, y - 50 * k], fill=M_GREEN, width=max(2, int(12 * k)))
    # paycheck bars grow
    tb = tok("tip", 2)
    if t > tb - 0.1:
        kk = ease_out((t - tb + 0.1) / 0.8)
        pop_text(img, (650, 395), "EACH PAYCHECK", F_NUM, 50, M_NAVY)
        for j, (lab, base, col) in enumerate([("BEFORE", 300, (170, 176, 200)), ("AFTER", 300 + 120 * kk, M_GREEN)]):
            y = 500 + j * 130
            pop_text(img, (400, y), lab, F_MED, 34, (90, 96, 120), anchor_c=False)
            d.rounded_rectangle([540, y - 38, 540 + base, y + 38], radius=14, fill=col)
        if kk > 0.7:
            pop_text(img, (720, 720), "(and a smaller refund)", F_HAND, 32, (110, 116, 140))

def piggy(img, cx, cy, s, t):
    if s < 0.05: return
    d = ImageDraw.Draw(img)
    def R(x0, y0, x1, y1): return [cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s]
    pk, pk2 = (255, 160, 190), (225, 110, 150)
    for lx in (-110, -40, 50, 120):
        d.rounded_rectangle(R(lx - 22, 80, lx + 22, 150), radius=max(1, 10 * s), fill=pk2)
    d.ellipse(R(-200, -130, 200, 130), fill=pk)
    d.polygon([(cx - 120 * s, cy - 100 * s), (cx - 70 * s, cy - 190 * s), (cx - 30 * s, cy - 115 * s)], fill=pk2)
    d.ellipse(R(170, -40, 250, 40), fill=pk2); d.ellipse(R(190, -12, 205, 8), fill=(120, 50, 80)); d.ellipse(R(215, -12, 230, 8), fill=(120, 50, 80))
    d.ellipse(R(100, -60, 122, -38), fill=(30, 30, 40))
    d.rounded_rectangle(R(-60, -132, 40, -116), radius=max(1, 6 * s), fill=(120, 50, 80))
    pop_text(img, (cx - 20 * s, cy + 10 * s), "IRS", F_NUM, 80 * s, WHITE)
    # coins dropping into the slot
    for i in range(3):
        ph = ((t * 1.6) + i / 3) % 1
        y = cy - 330 * s + ph * 200 * s
        if ph < 0.9:
            d.ellipse([cx - 10 * s - 34 * s, y - 34 * s, cx - 10 * s + 34 * s, y + 34 * s], fill=(255, 205, 60), outline=(210, 150, 30), width=max(1, int(5 * s)))

def bd_punch(img, t):
    s0 = seg_start("punch")
    ts = tok("punch", 2)
    if t < ts - 0.1:
        marker(img, (W / 2, 470), "BONUS", 130, M_GREEN)
        if t > tok("punch", 1) - 0.2:
            k = ease_out((t - tok("punch", 1) + 0.2) / 0.3)
            ImageDraw.Draw(img).line([(250, 520), (250 + 580 * k, 420)], fill=M_RED, width=18)
        marker(img, (W / 2, 640), "?", 90, M_NAVY)
    else:
        piggy(img, W / 2 + 10, 600, 0.9 * ease_back((t - ts + 0.1) / 0.35), t)

def bd_q(img, t):
    s0 = seg_start("q")
    marker(img, (W / 2, 385), "THIS YEAR, DID YOU...", 56, M_NAVY)
    d = ImageDraw.Draw(img)
    opts = [("REFUND", M_GREEN), ("OWE", M_RED)]
    for i, (lab, col) in enumerate(opts):
        x = 330 + i * 420; y = 540
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([x - 170 * k, y - 80 * k, x + 170 * k, y + 80 * k], radius=40 * k, fill=col)
        pop_text(img, (x, y), lab, F_NUM, 64 * k, WHITE)
    if t > tok("q", 3) - 0.1:
        marker(img, (W / 2, 690), "TELL US BELOW 👇".replace(" 👇", ""), 64, M_ORG, scale=ease_back((t - tok("q", 3) + 0.1) / 0.3))

BOARDS = {"hook": bd_hook, "no": bd_no, "over": bd_over, "ask": bd_ask, "month": bd_month, "loan": bd_loan,
          "tip": bd_tip, "punch": bd_punch, "q": bd_q, "loop": bd_hook}
# per-scene staging: (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "smile", "point_up", "smile"),
         "over": ("idle", "worried", "marker", "smile"), "ask": ("shrug", "worried", "idle", "smile"),
         "month": ("idle", "worried", "point_up", "smile"), "loan": ("facepalm", "worried", "idle", "smile"),
         "tip": ("idle", "smile", "marker", "smile"), "punch": ("shrug", "worried", "facepalm", "facepalm"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("cheer", "smug", "idle", "worried")}

TX, NX, CY = 790, 290, 1040

def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("N", NX, NORA, np_, nm), ("T", TX, THEO, tp, tm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.40 if who == spk else 1.28
        person(img, cx, CY + (0 if who == spk else 18) - (30 if who == "T" else 0), sc, col, who, t, talk=talking, pose=pose, mood=mood)

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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=(90, 150, 240))
    lab1, lab2 = "THEO EXPLAINS #4", "TAX REFUNDS"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=M_NAVY)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=M_NAVY)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=INK, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (40, 60, 110)
    d.text((W / 2, 1515), "$3,273 = average 2026 US refund (IRS filing season stats, to 1 May 2026).", font=font(F_MED, 25), fill=c, anchor="mm")
    d.text((W / 2, 1550), "Illustration: assumes all of it was tax over-withheld; some refunds include credits.", font=font(F_MED, 25), fill=c, anchor="mm")
    d.text((W / 2, 1585), "Not financial advice.", font=font(F_MED, 25), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    board(img, t)
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
