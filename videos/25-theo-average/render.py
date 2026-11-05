"""THEO EXPLAINS #9: average vs actual return. 1080x1920 @30fps. Pastel aqua art-deco hotel lobby, whiteboard + front desk on the left, tall brass elevator shaft on the right whose floors are dollar values. Nora left / Theo right."""
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



# ---------- palette (episode 9: pastel aqua art-deco hotel lobby, whiteboard + front desk, brass elevator shaft whose floors are dollars) ----------
C_GREEN = (22, 150, 85); CORAL = (235, 72, 84); TEAL_INK = (16, 74, 84); PAPER = (255, 253, 245)
BRASS = (205, 160, 70); BRASS_D = (140, 100, 36); BRASS_L = (240, 208, 130); WOOD = (120, 72, 48); SHAFT = (24, 44, 66); LED = (255, 212, 80)
MARK_B = (32, 70, 170); MARK_R = (215, 45, 60); MARK_G = (20, 140, 80)

SX0, SX1 = 610, 990      # shaft
HDR0, HDR1 = 275, 372    # LED header
SY0, SY1 = 372, 1292
BX0, BY0, BX1, BY1 = 50, 275, 590, 715  # whiteboard
DESK_Y = 1190

def fy(v):  # dollars -> floor y
    return 1240 - (v - 8000) * 0.085

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    img = np.ones((H, W, 3), np.float32) * np.array((196, 236, 232), np.float32)
    im = Image.fromarray(img.astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(im)
    # art-deco fan wallpaper
    R = 90
    for row in range(0, 16):
        for col in range(-1, 8):
            cx = col * 2 * R + (R if row % 2 else 0); cy = row * R + 60
            for r, c in ((R, (182, 226, 224)), (R * 0.72, (196, 236, 232)), (R * 0.46, (182, 226, 224)), (R * 0.2, (196, 236, 232))):
                d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=c)
    # marble floor + skirting
    FL = 1262
    d.rectangle([0, FL, W, H], fill=(244, 238, 222))
    for row in range(0, 8):
        for col in range(0, 12):
            if (row + col) % 2 == 0:
                x0 = col * 90; y0 = FL + 8 + row * 90
                d.rectangle([x0, y0, x0 + 90, y0 + 90], fill=(226, 234, 226))
    d.rectangle([0, FL - 10, W, FL + 8], fill=BRASS_D)
    return im
BG = make_bg()

def make_shaft():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([SX0 + 10, HDR0 + 14, SX1 + 14, SY1 + 8], radius=26, fill=(30, 70, 80, 60))
    d.rounded_rectangle([SX0 - 12, HDR0 - 12, SX1 + 12, SY1 + 6], radius=26, fill=BRASS)
    d.rounded_rectangle([SX0 - 4, HDR0 - 4, SX1 + 4, SY1], radius=20, fill=BRASS_D)
    d.rectangle([SX0, SY0, SX1, SY1 - 4], fill=SHAFT)
    # guide rails + cables backdrop
    for x in (760, 980):
        d.rectangle([x - 3, SY0, x + 3, SY1 - 4], fill=(46, 72, 98))
    # floors every $2,000
    for v in (8000, 10000, 12000, 14000, 16000):
        y = fy(v)
        d.rectangle([SX0, y, SX1, y + 7], fill=BRASS)
        s = f"${v:,.0f}"
        d.text((SX0 + 14, y - 8), s, font=font(F_NUM, 30), fill=(190, 212, 230) if v != 10000 else LED, anchor="ls")
    d.rectangle([SX0 + 14, fy(10000) + 16, SX0 + 134, fy(10000) + 50], fill=LED)
    d.text((SX0 + 74, fy(10000) + 33), "START", font=font(F_NUM, 26), fill=SHAFT, anchor="mm")
    # LED header
    d.rounded_rectangle([SX0, HDR0, SX1, HDR1 - 4], radius=16, fill=(16, 20, 34))
    return lay
SHAFT_L = make_shaft()

def make_desk():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([18, DESK_Y, 590, 1300], radius=10, fill=WOOD)
    for x in range(40, 590, 68):
        d.rounded_rectangle([x, DESK_Y + 30, x + 50, 1286], radius=6, fill=(138, 86, 58))
    d.rounded_rectangle([6, DESK_Y - 16, 602, DESK_Y + 14], radius=10, fill=BRASS)
    # brass bell
    d.pieslice([505, DESK_Y - 60, 570, DESK_Y + 2], 180, 360, fill=BRASS_L)
    d.ellipse([532, DESK_Y - 72, 544, DESK_Y - 58], fill=BRASS_L)
    d.rectangle([498, DESK_Y - 30, 577, DESK_Y - 22], fill=BRASS_D)
    return lay
DESK = make_desk()

def txt(img, xy, s, size, fill=TEAL_INK, scale=1.0, path=None, alpha=1.0):
    pop_text(img, xy, s, path or F_NUM, size, fill, scale=scale, alpha=alpha)

def money(v): return f"${v:,.0f}"

def board(img, title=None, col=MARK_B):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([BX0 + 8, BY0 + 12, BX1 + 8, BY1 + 14], radius=16, fill=(150, 196, 196))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=16, fill=BRASS)
    d.rounded_rectangle([BX0 + 12, BY0 + 12, BX1 - 12, BY1 - 12], radius=8, fill=PAPER)
    if title:
        txt(img, ((BX0 + BX1) / 2, BY0 + 58), title, 42, col)
BC = (BX0 + BX1) / 2

# value of the elevator at time t (10k -> Theo's 12.1k dream -> real ride)
def val_at(t):
    if t < seg_start("no"):                       # Theo's dream ride up
        return lerp(10000, 12100, ease_out((t - tok("hook", 4)) / 1.6))
    if t < seg_start("up"):                       # the statement: drop
        k = ease_out((t - tok("no", 3) + 0.1) / 0.5)
        return lerp(12100, 9600, k)
    if t < seg_start("down"):                     # year one: reset to start, go to 16k
        k0 = clamp((t - seg_start("up")) / 0.25)
        k = ease_out((t - tok("up", 1)) / 1.0)
        return lerp(lerp(9600, 10000, k0), 16000, k)
    if t < seg_start("q"):                        # year two: down to 9.6k and stay
        return lerp(16000, 9600, ease_out((t - tok("down", 1)) / 1.0))
    if t < seg_start("loop"):
        return 9600
    return lerp(9600, 10000, ease_out((t - seg_start("loop")) / 0.5))

def shaft(img, t):
    s = scene_at(t)["scene"]
    img.alpha_composite(SHAFT_L)
    d = ImageDraw.Draw(img)
    v = val_at(t)
    # Theo's promised floor (dashed green) during hook / no / loop
    if s in ("hook", "no", "loop"):
        y = fy(12100)
        d.rectangle([SX0 + 8, fy(12000) - 34, SX0 + 140, fy(12000) - 1], fill=SHAFT)  # hide the $12,000 label under Theo's dream floor
        for x in range(SX0 + 6, SX1 - 6, 34):
            d.rectangle([x, y, x + 20, y + 6], fill=(90, 230, 150))
        d.text((SX0 + 36, y - 10), "$12,100", font=font(F_NUM, 28), fill=(90, 230, 150), anchor="ls")
    # the car
    cy_ = fy(v)
    cx0, cx1, ch = 762, 974, 170
    top = cy_ - ch
    # cable
    d.rectangle([(cx0 + cx1) / 2 - 3, SY0, (cx0 + cx1) / 2 + 3, top], fill=(120, 140, 160))
    d.rounded_rectangle([cx0 - 6, top - 6, cx1 + 6, cy_ + 2], radius=12, fill=BRASS_L)
    d.rounded_rectangle([cx0 + 4, top + 4, cx1 - 4, cy_ - 4], radius=8, fill=(255, 238, 200))
    mood = "smug" if s in ("hook", "loop") else "worried"
    pose = "cheer" if s in ("hook", "loop") else "shrug"
    # mini Theo riding
    person(img, (cx0 + cx1) / 2, cy_ - 72, 0.46, THEO, "T", t, talk=0.0, pose=pose, mood=mood)
    d = ImageDraw.Draw(img)
    d.rectangle([cx0 - 6, cy_ - 22, cx1 + 6, cy_ + 2], fill=BRASS)
    # LED counter
    col = LED
    if s not in ("hook", "loop") and v < 10000: col = (255, 90, 90)
    if s in ("up",) and v > 10000: col = (100, 240, 150)
    d.text(((SX0 + SX1) / 2, (HDR0 + HDR1) / 2 - 2), money(round(v / 10) * 10), font=font(F_NUM, 74), fill=col, anchor="mm")
    # direction pills next to the car
    if s == "up":
        k = ease_back((t - tok("up", 1) + 0.05) / 0.3)
        if k > 0.05:
            txt(img, (690, 645), "+60%", 50, (100, 240, 150), scale=k)
    if s == "down":
        k = ease_back((t - tok("down", 1) + 0.05) / 0.3)
        if k > 0.05:
            txt(img, (690, 815), "-40%", 50, (255, 110, 120), scale=k)
    if s == "why":
        top = fy(9600) - 178
        k1 = ease_back((t - tok("why", 1) + 0.05) / 0.3)
        if k1 > 0.05:
            d.line([(778, top), (778, fy(16000) + 30)], fill=(100, 240, 150), width=10)
            d.polygon([(758, fy(16000) + 34), (798, fy(16000) + 34), (778, fy(16000) + 6)], fill=(100, 240, 150))
            d.rounded_rectangle([800, 665, 950, 715], radius=14, fill=SHAFT)
            txt(img, (875, 690), "+$6,000", 34, (100, 240, 150), scale=k1)
        k2 = ease_back((t - tok("why", 3) + 0.05) / 0.3)
        if k2 > 0.05:
            d.line([(960, fy(16000) + 10), (960, top - 28)], fill=(255, 110, 120), width=10)
            d.polygon([(940, top - 30), (980, top - 30), (960, top - 2)], fill=(255, 110, 120))
            d.rounded_rectangle([800, 780, 950, 830], radius=14, fill=SHAFT)
            txt(img, (875, 805), "-$6,400", 34, (255, 110, 120), scale=k2)

def bd_hook(img, t):
    board(img, "THEO'S MATHS")
    k = 1 + 0.03 * math.sin(t * 5)
    txt(img, (BC, 415), "10% A YEAR!", 66, MARK_B, scale=k)
    txt(img, (BC, 505), "2 YEARS LATER:", 40, TEAL_INK)
    txt(img, (BC, 600), "$12,100", 112, MARK_G, scale=k)
    txt(img, (BC, 682), "(he hasn't looked)", 28, (120, 130, 140), path=F_HAND)

def bd_no(img, t):
    board(img, "THE STATEMENT", MARK_R)
    s0 = seg_start("no")
    txt(img, (BC, 415), "THEO'S GUESS: $12,100", 36, (120, 130, 140))
    d = ImageDraw.Draw(img)
    d.line([(112, 415), (528, 415)], fill=MARK_R, width=6)
    k = ease_back((t - tok("no", 3) + 0.08) / 0.3)
    txt(img, (BC, 520), "$9,600", 118, MARK_R, scale=k)
    txt(img, (BC, 640), "BALANCE, END OF YEAR 2", 32, TEAL_INK, alpha=clamp(k))

def bd_up(img, t):
    board(img, "YEAR ONE", MARK_G)
    k = ease_back((t - tok("up", 1)) / 0.3)
    txt(img, (BC, 400), "$10,000", 64, TEAL_INK)
    txt(img, (BC, 490), "+60%", 96, MARK_G, scale=k)
    k2 = ease_back((t - tok("up", 2) + 0.05) / 0.3)
    txt(img, (BC, 610), "= $16,000", 80, MARK_G, scale=k2)

def bd_down(img, t):
    board(img, "YEAR TWO", MARK_R)
    k = ease_back((t - tok("down", 1)) / 0.3)
    txt(img, (BC, 400), "$16,000", 64, TEAL_INK)
    txt(img, (BC, 490), "-40%", 96, MARK_R, scale=k)
    k2 = ease_back((t - tok("down", 2) + 0.05) / 0.3)
    txt(img, (BC, 610), "= $9,600", 84, MARK_R, scale=k2)

def bd_avg(img, t):
    board(img, "TWO DIFFERENT NUMBERS")
    txt(img, (BC, 385), "(+60% - 40%) / 2", 50, TEAL_INK)
    k1 = ease_back((t - tok("avg", 1)) / 0.3)
    txt(img, (BC, 460), "AVERAGE +10%", 66, MARK_G, scale=k1)
    k2 = ease_back((t - tok("avg", 4)) / 0.3)
    txt(img, (BC, 555), "$10,000 > $9,600", 54, TEAL_INK, scale=k2)
    txt(img, (BC, 640), "MONEY -$400", 76, MARK_R, scale=k2)

def bd_why(img, t):
    board(img, "WHY IT'S NOT EVEN", MARK_B)
    k1 = ease_back((t - tok("why", 1) + 0.05) / 0.3)
    txt(img, (BC, 385), "60% of $10,000", 40, TEAL_INK, scale=k1)
    txt(img, (BC, 440), "+$6,000", 66, MARK_G, scale=k1)
    k2 = ease_back((t - tok("why", 3) + 0.05) / 0.3)
    txt(img, (BC, 512), "40% of $16,000", 40, TEAL_INK, scale=k2)
    txt(img, (BC, 567), "-$6,400", 66, MARK_R, scale=k2)
    k3 = ease_back((t - tok("why", 5)) / 0.3)
    d = ImageDraw.Draw(img)
    if k3 > 0.05:
        d.rounded_rectangle([BX0 + 40, 618, BX1 - 40, 688], radius=30, fill=MARK_R)
        txt(img, (BC, 652), "REAL: -2% A YEAR", 40, WHITE, scale=k3)

def bd_punch(img, t):
    board(img, None)
    k = ease_back((t - seg_start("punch")) / 0.3)
    if k < 0.05: return
    txt(img, (BC, 330), "RENT DUE: THIS MONTH", 34, TEAL_INK, scale=k)
    txt(img, (BC, 400), "PAYING WITH:", 40, (120, 130, 140), scale=k)
    txt(img, (BC, 490), "1 AVERAGE", 80, MARK_B, scale=k)
    if t > tok("punch", 4) + 0.1:
        ks = ease_back((t - tok("punch", 4) - 0.1) / 0.25)
        if ks > 0.05:
            lay = Image.new("RGBA", (470, 130), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            dl.rounded_rectangle([4, 4, 465, 125], radius=16, outline=MARK_R, width=10)
            pop_text(lay, (235, 65), "REJECTED", F_NUM, 80, MARK_R)
            lay = lay.resize((max(2, int(470 * ks)), max(2, int(130 * ks)))).rotate(-7, expand=True, resample=Image.BICUBIC)
            img.alpha_composite(lay, (int(BC - lay.width / 2), int(615 - lay.height / 2)))

def bd_q(img, t):
    board(img, "YOUR TURN", MARK_B)
    s0 = seg_start("q")
    txt(img, (BC, 388), "WHAT DO YOU CHECK?", 38, TEAL_INK)
    d = ImageDraw.Draw(img)
    for i, (lab, col) in enumerate([("DOLLARS", C_GREEN), ("PERCENTAGES", MARK_B), ("NEITHER", CORAL)]):
        y = 455 + i * 62
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([BC - 220 * k, y - 28 * k, BC + 220 * k, y + 28 * k], radius=28 * k, fill=col)
        pop_text(img, (BC, y), lab, F_NUM, 36 * k, WHITE)
    if t > tok("q", 5) - 0.1:
        txt(img, (BC, 655), "TELL US BELOW", 40, MARK_R, scale=ease_back((t - tok("q", 5) + 0.1) / 0.3))

BOARDS = {"hook": bd_hook, "no": bd_no, "up": bd_up, "down": bd_down, "avg": bd_avg, "why": bd_why,
          "punch": bd_punch, "q": bd_q, "loop": bd_hook}
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "worried", "point_up", "smile"),
         "up": ("cheer", "smile", "marker", "smile"), "down": ("idle", "worried", "marker", "smile"),
         "avg": ("facepalm", "worried", "marker", "smile"), "why": ("shrug", "worried", "point_up", "smile"),
         "punch": ("shrug", "worried", "facepalm", "facepalm"), "q": ("idle", "smile", "shrug", "smile"),
         "loop": ("cheer", "smug", "idle", "worried")}

NX, TX, CY = 150, 445, 1010

def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("N", NX, NORA, np_, nm), ("T", TX, THEO, tp, tm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.22 if who == spk else 1.14
        person(img, cx, CY + (0 if who == spk else 12), sc, col, who, t, talk=talking, pose=pose, mood=mood)
    img.alpha_composite(DESK)

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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=CORAL)
    lab1, lab2 = "THEO EXPLAINS #9", "AVERAGE RETURNS"
    f1 = font(F_NUM, 44)
    w1 = tw(lab1, F_NUM, 44) + 50; w2 = tw(lab2, F_NUM, 44) + 50
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 165, x0 + w1 + 30, 245], radius=40, fill=THEO)
    d.rounded_rectangle([x0 + w1, 165, x0 + total, 245], radius=40, fill=TEAL_INK)
    d.rectangle([x0 + w1, 165, x0 + w1 + 30, 245], fill=TEAL_INK)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=TEAL_INK, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = TEAL_INK
    d.text((W / 2, 1520), "Illustration: made-up fund, $10,000, +60% then -40%, no fees or taxes.", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1558), "Past swings don't predict returns. Not financial advice.", font=font(F_MED, 27), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    shaft(img, t)
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
