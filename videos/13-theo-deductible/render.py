"""THEO EXPLAINS #3: Insurance deductibles. 1080x1920 @30fps. Pastel peach + bokeh dots, paper flipchart on an easel, Theo left / Nora right, cartoon car."""
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



# ---------- palette (episode 3: peach + paper flipchart, marker inks) ----------
PAPER = (253, 252, 247); RULE = (214, 226, 240); CLIP = (70, 74, 92); EASEL = (176, 120, 78); EASEL2 = (138, 90, 56)
M_NAVY = (34, 52, 110); M_RED = (222, 56, 64); M_GREEN = (22, 150, 90); M_TEAL = (20, 140, 170); M_ORG = (240, 130, 40)
CAR = (255, 92, 92); CAR2 = (190, 50, 60); GLASS = (190, 225, 250)

# ---------- background: pastel peach with soft bokeh dots ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((255, 232, 214), np.float32); bot = np.array((255, 210, 190), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    rng = np.random.default_rng(11)
    for _ in range(26):
        cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 130)
        dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        img += (np.clip(1 - dd, 0, 1) ** 0.6)[..., None] * np.array((6, 4, 2), np.float32) * 1.6
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - 1050) * 1.2) ** 2) / 800
    img += (np.clip(1 - d, 0, 1) ** 2)[..., None] * 10
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

def marker(img, xy, s, size, fill, scale=1.0, path=None):
    pop_text(img, xy, s, path or F_HAND, size, fill, scale=scale)

# ---------- flipchart on an easel ----------
BX0, BY0, BX1, BY1 = 80, 300, 1000, 790
def board(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # easel legs behind the paper
    d.line([(W / 2, BY0 - 30), (W / 2, BY1 + 260)], fill=EASEL2, width=26)
    d.line([(BX0 + 120, BY0), (BX0 + 30, BY1 + 330)], fill=EASEL, width=30)
    d.line([(BX1 - 120, BY0), (BX1 - 30, BY1 + 330)], fill=EASEL, width=30)
    d.rounded_rectangle([BX0 + 12, BY0 + 16, BX1 + 12, BY1 + 16], radius=10, fill=(150, 80, 50, 50))
    d.rectangle([BX0, BY0, BX1, BY1], fill=PAPER)
    for y in range(BY0 + 70, BY1 - 10, 58):
        d.line([(BX0 + 20, y), (BX1 - 20, y)], fill=RULE, width=2)
    d.line([(BX0 + 70, BY0 + 40), (BX0 + 70, BY1 - 6)], fill=(250, 200, 200), width=3)  # margin line
    # curled page corner
    d.polygon([(BX1, BY1 - 70), (BX1 - 70, BY1), (BX1, BY1)], fill=(255, 220, 200))
    d.polygon([(BX1 - 70, BY1), (BX1, BY1 - 70), (BX1 - 58, BY1 - 58)], fill=(235, 232, 225))
    d.rounded_rectangle([BX0 - 25, BY0 - 34, BX1 + 25, BY0 + 18], radius=14, fill=CLIP)  # clip bar
    for x in (BX0 + 160, BX1 - 160):
        d.ellipse([x - 12, BY0 - 20, x + 12, BY0 + 4], fill=(150, 156, 175))
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

def car(img, cx, cy, s, dent=False, scratch=False, t=0.0):
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def R(x0, y0, x1, y1): return [cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s]
    d.rounded_rectangle(R(-200, -10, 200, 70), radius=max(1, 34 * s), fill=CAR, outline=CAR2, width=max(2, int(5 * s)))
    d.polygon([(cx - 120 * s, cy - 8 * s), (cx - 70 * s, cy - 85 * s), (cx + 80 * s, cy - 85 * s), (cx + 135 * s, cy - 8 * s)], fill=CAR, outline=CAR2)
    d.polygon([(cx - 95 * s, cy - 14 * s), (cx - 58 * s, cy - 70 * s), (cx - 2 * s, cy - 70 * s), (cx - 2 * s, cy - 14 * s)], fill=GLASS)
    d.polygon([(cx + 12 * s, cy - 14 * s), (cx + 12 * s, cy - 70 * s), (cx + 70 * s, cy - 70 * s), (cx + 108 * s, cy - 14 * s)], fill=GLASS)
    for wx in (-115, 115):
        d.ellipse(R(wx - 44, 30, wx + 44, 118), fill=(40, 40, 52)); d.ellipse(R(wx - 20, 54, wx + 20, 94), fill=(190, 190, 200))
    d.ellipse(R(176, 4, 198, 26), fill=(255, 236, 140))
    if dent:   # crumpled front bumper
        d.polygon([(cx + 170 * s, cy - 6 * s), (cx + 205 * s, cy + 18 * s), (cx + 182 * s, cy + 34 * s), (cx + 210 * s, cy + 56 * s), (cx + 168 * s, cy + 70 * s)], fill=(170, 40, 50))
    if scratch:
        pts = [(cx + (-150 + i * 30) * s, cy + (22 + (12 if i % 2 else -6)) * s) for i in range(9)]
        d.line(pts, fill=(255, 255, 255), width=max(2, int(6 * s)))
    img.alpha_composite(lay)

def split_bar(img, y, total, you, k, scale_max=1500, thresh=None):
    """horizontal claim bar: red 'you pay' part then teal 'insurance' part, width ~ amount."""
    d = ImageDraw.Draw(img)
    x0, x1 = 160, 920
    px = lambda v: x0 + (x1 - x0) * v / scale_max
    shown = total * ease_out(k)
    yv = min(shown, you)
    d.rounded_rectangle([x0, y - 50, px(total), y + 50], radius=16, outline=(200, 200, 210), width=4)
    if yv > 1:
        d.rounded_rectangle([x0, y - 50, px(yv), y + 50], radius=16, fill=M_RED)
    if shown > you + 1:
        d.rounded_rectangle([px(you) - 16, y - 50, px(shown), y + 50], radius=16, fill=M_TEAL)
        d.rectangle([px(you), y - 50, px(you) + 2, y + 50], fill=PAPER)
    if thresh is not None:
        tx = px(thresh)
        for yy_ in range(int(y - 80), int(y + 80), 22):
            d.line([(tx, yy_), (tx, yy_ + 12)], fill=M_NAVY, width=5)
    return px

def hook_board(img, t):
    marker(img, (W / 2, 385), "$1,000 DEDUCTIBLE", 86, M_NAVY, path=F_NUM)
    marker(img, (W / 2, 520), "=", 90, M_NAVY, path=F_NUM)
    marker(img, (W / 2, 650), "$1,000 OFF MY TAXES!", 70, M_GREEN, path=F_NUM)

def bd_hook(img, t): hook_board(img, t)

def bd_no(img, t):
    hook_board(img, t)
    s0 = seg_start("no"); ts = tok("no", 1)
    k = ease_out((t - s0) / 0.3)
    if k > 0.05:
        ImageDraw.Draw(img).line([(130, 662), (130 + 820 * k, 636)], fill=M_RED, width=16)
    if t > ts - 0.1:
        stamp(img, W / 2, 520, 0.6 * ease_back((t - ts + 0.1) / 0.3), "NOT A TAX BREAK", M_RED, angle=-7, back=(255, 255, 255))

def bd_what(img, t):
    marker(img, (W / 2, 370), "DEDUCTIBLE =", 64, M_NAVY, path=F_NUM)
    ts = tok("what", 1)
    if t > ts - 0.1:
        k = ease_back((t - ts + 0.1) / 0.3)
        marker(img, (W / 2, 480), "WHAT YOU PAY FIRST", 66, M_RED, scale=k)
    tb = tok("what", 3)
    if t > tb - 0.1:
        k = ease_out((t - tb + 0.1) / 0.3)
        marker(img, (W / 2, 590), "THEN insurance pays", 56, M_TEAL, scale=k)
        marker(img, (W / 2, 680), "(per claim, up to your limit)", 38, (120, 120, 140), scale=k)

def bd_pole(img, t):
    s0 = seg_start("pole")
    marker(img, (W / 2, 370), "THE POLE INCIDENT", 60, M_NAVY, path=F_NUM)
    k = ease_back((t - s0) / 0.35)
    d = ImageDraw.Draw(img)
    d.rectangle([765, 430, 805, 740], fill=(150, 150, 165)); d.rectangle([755, 420, 815, 440], fill=(120, 120, 135))
    hit = t > tok("pole", 2)
    car(img, 520 + (40 if hit else 0) * k, 640, 1.0 * k, dent=hit)
    if hit:
        marker(img, (700, 480), "CRUNCH!", 58, M_ORG, scale=ease_back((t - tok("pole", 2)) / 0.25), path=F_NUM)

def bd_repair(img, t):
    s0 = seg_start("repair")
    marker(img, (W / 2, 370), "$1,500 REPAIR", 76, M_NAVY, path=F_NUM)
    t0, t1 = tok("repair", 2), tok("repair", 4) + 0.4
    k = clamp((t - t0) / (t1 - t0))
    if t > t0 - 0.1:
        px = split_bar(img, 520, 1500, 1000, k, thresh=1000)
        if 1500 * ease_out(k) >= 1000:
            marker(img, ((160 + px(1000)) / 2, 520), "YOU $1,000", 48, WHITE, path=F_NUM)
        if t > tok("repair", 5) - 0.1:
            marker(img, ((px(1000) + px(1500)) / 2, 520), "$500", 48, WHITE, path=F_NUM)
            marker(img, ((px(1000) + px(1500)) / 2, 625), "INSURER", 38, M_TEAL, path=F_NUM)
        marker(img, (px(1000), 625), "deductible line", 34, M_NAVY) if t < tok("repair", 5) - 0.1 else None
    else:
        car(img, W / 2, 560, 1.0, dent=True)

def bd_scratch(img, t):
    s0 = seg_start("scratch")
    marker(img, (W / 2, 370), "$600 SCRATCH", 76, M_NAVY, path=F_NUM)
    car(img, W / 2, 590, 1.1 * ease_back((t - s0) / 0.35), scratch=t > tok("scratch", 1))

def bd_zero(img, t):
    marker(img, (W / 2, 370), "$600 SCRATCH", 76, M_NAVY, path=F_NUM)
    s0 = seg_start("zero")
    k = clamp((t - s0) / 0.6)
    px = split_bar(img, 510, 600, 1000, k, thresh=1000)
    marker(img, ((160 + px(600)) / 2, 510), "YOU $600", 46, WHITE, path=F_NUM)
    marker(img, (805, 490), "$1,000", 44, M_NAVY, path=F_NUM)
    marker(img, (805, 535), "deductible", 32, M_NAVY)
    tz = tok("zero", 2)
    if t > tz - 0.1:
        k2 = ease_back((t - tz + 0.1) / 0.3)
        marker(img, (W / 2, 650), "INSURANCE PAYS $0", 70, M_TEAL, scale=k2, path=F_NUM)
        marker(img, (W / 2, 730), "under the deductible = all yours", 36, (120, 120, 140), scale=k2)

def bd_tip(img, t):
    s0 = seg_start("tip")
    rows = [(s0, "HIGHER DEDUCTIBLE", M_RED, True), (tok("tip", 2), "CHEAPER PREMIUM", M_GREEN, False)]
    d = ImageDraw.Draw(img)
    for i, (ts, lab, col, up) in enumerate(rows):
        if t < ts - 0.1: continue
        k = ease_back((t - ts + 0.1) / 0.3)
        y = 395 + i * 125
        marker(img, (560, y), lab, 64, col, scale=k, path=F_NUM)
        ax = 175
        if k > 0.5:
            if up:
                d.polygon([(ax, y - 42), (ax - 32, y + 4), (ax + 32, y + 4)], fill=col); d.rectangle([ax - 12, y, ax + 12, y + 38], fill=col)
            else:
                d.polygon([(ax, y + 42), (ax - 32, y - 4), (ax + 32, y - 4)], fill=col); d.rectangle([ax - 12, y - 38, ax + 12, y], fill=col)
    tk_ = tok("tip", 4)
    if t > tk_ - 0.1:
        k = ease_back((t - tk_ + 0.1) / 0.3)
        d.rounded_rectangle([W / 2 - 330 * k, 630 - 70 * k, W / 2 + 330 * k, 630 + 70 * k], radius=30 * k, outline=M_NAVY, width=max(2, int(7 * k)))
        marker(img, (W / 2, 630), "KEEP IT SAVED", 66, M_NAVY, scale=k, path=F_NUM)

def bd_punch(img, t):
    marker(img, (W / 2, 370), "THEO'S NEW WORD:", 56, M_NAVY)
    ts = tok("punch", 1)
    if t > ts - 0.1:
        k = ease_back((t - ts + 0.1) / 0.35)
        marker(img, (W / 2, 520), "DEDUCT-", 110, M_ORG, scale=k, path=F_NUM)
    if t > tok("punch", 2) - 0.1:
        k = ease_back((t - tok("punch", 2) + 0.1) / 0.35)
        marker(img, (W / 2, 660), "FROM-ME-IBLE", 100, M_RED, scale=k, path=F_NUM)
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate([(150, 450), (930, 450), (150, 720), (930, 720)]):
        r = 22 + 6 * math.sin(t * 8 + i)
        pts = [(x + r * math.cos(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45),
                y + r * math.sin(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45)) for a in range(10)]
        d.polygon(pts, fill=(255, 190, 40))

def bd_q(img, t):
    s0 = seg_start("q")
    marker(img, (W / 2, 370), "WHAT'S YOUR DEDUCTIBLE?", 58, M_NAVY, path=F_NUM)
    d = ImageDraw.Draw(img)
    opts = [("$500", M_GREEN), ("$1,000", M_TEAL), ("$2,000+", M_RED)]
    for i, (lab, col) in enumerate(opts):
        x = 255 + i * 285; y = 520
        k = ease_back((t - s0 - 0.12 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([x - 125 * k, y - 70 * k, x + 125 * k, y + 70 * k], radius=24 * k, outline=col, width=max(2, int(8 * k)))
        marker(img, (x, y), lab, 52, col, scale=k, path=F_NUM)
    if t > tok("q", 3) - 0.1:
        marker(img, (W / 2, 680), "TELL US BELOW", 70, M_ORG, scale=ease_back((t - tok("q", 3) + 0.1) / 0.3), path=F_NUM)

BOARDS = {"hook": bd_hook, "no": bd_no, "what": bd_what, "pole": bd_pole, "repair": bd_repair, "scratch": bd_scratch,
          "zero": bd_zero, "tip": bd_tip, "punch": bd_punch, "q": bd_q, "loop": lambda img, t: hook_board(img, t)}
# per-scene staging: (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "smile", "marker", "smile"),
         "what": ("idle", "worried", "point_up", "smile"), "pole": ("shrug", "worried", "idle", "smile"),
         "repair": ("idle", "worried", "marker", "smile"), "scratch": ("point_up", "worried", "idle", "smile"),
         "zero": ("facepalm", "worried", "marker", "smile"), "tip": ("idle", "smile", "point_up", "smile"),
         "punch": ("cheer", "smug", "facepalm", "facepalm"), "q": ("idle", "smile", "shrug", "smile"),
         "loop": ("point_up", "smug", "idle", "worried")}

TX, NX, CY = 290, 790, 1040
def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("N", NX, NORA, np_, nm), ("T", TX, THEO, tp, tm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.40 if who == spk else 1.28
        person(img, cx, CY + (0 if who == spk else 18) - (30 if who == "T" else 0), sc, col, who, t, talk=talking, pose=pose, mood=mood)

def keys(img, x, y, t):
    # Theo's car keys dangling from his hand area (small recurring prop)
    d = ImageDraw.Draw(img)
    sw = math.sin(t * 3) * 6
    d.ellipse([x - 18 + sw, y - 18, x + 18 + sw, y + 18], outline=(120, 120, 135), width=6)
    d.rounded_rectangle([x - 14 + sw, y + 14, x + 14 + sw, y + 60], radius=8, fill=CAR2)
    d.rectangle([x + 4 + sw, y + 58, x + 10 + sw, y + 90], fill=(200, 200, 210))
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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=(240, 110, 80))
    lab1, lab2 = "THEO EXPLAINS #3", "DEDUCTIBLES"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=M_NAVY)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=M_NAVY)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=INK, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (120, 62, 40)
    d.text((W / 2, 1515), "Illustration: US personal car policy, collision cover, $1,000 deductible per claim.", font=font(F_MED, 25), fill=c, anchor="mm")
    d.text((W / 2, 1550), "Repair costs are made-up examples. Real policies and premiums vary.", font=font(F_MED, 25), fill=c, anchor="mm")
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
