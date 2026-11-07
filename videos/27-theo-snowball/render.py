"""THEO EXPLAINS #10: simple vs compound growth. 1080x1920 @30fps. Pastel lilac winter dusk, wide whiteboard with text + chart (line / yearly-interest bars), snowy slope with a growing snowball between Theo (left) and Nora (right)."""
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



# ---------- palette (episode 10: pastel lilac winter dusk, snowy slope, snowball, wide whiteboard with chart) ----------
C_GREEN = (22, 150, 85); CORAL = (235, 72, 84); INK2 = (52, 40, 96); PAPER = (255, 253, 248)
FRAME = (120, 96, 190); FRAME_D = (84, 64, 150)
MARK_B = (40, 80, 200); MARK_R = (215, 45, 60); MARK_G = (20, 140, 80)
SNOW = (246, 244, 255); SNOW_S = (216, 210, 242)

BX0, BY0, BX1, BY1 = 40, 270, 1040, 705   # whiteboard
TX0, TX1 = 70, 520                        # text column
CX0, CX1, CY0, CY1 = 590, 1000, 345, 650  # chart area
BC = (TX0 + TX1) / 2

def hill_y(x): return min(1268, 960 + 0.43 * x)   # snow ramp surface
BALL_X0, BALL_X1 = 365, 615

R = 0.07; P0 = 10000.0
def real_v(y): return P0 * (1 + R) ** y
def theo_v(y): return P0 * (1 + R * y)

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    a = np.zeros((H, W, 3), np.float32)
    k = (yy / 900.0).clip(0, 1)[..., None]
    top = np.array((206, 196, 246), np.float32); bot = np.array((255, 214, 226), np.float32)
    a[:] = top * (1 - k) + bot * k
    im = Image.fromarray(a.astype(np.uint8)).convert("RGB"); d = ImageDraw.Draw(im)
    # far hills
    d.polygon([(0, 760), (180, 700), (420, 745), (700, 690), (1080, 735), (1080, 900), (0, 900)], fill=(226, 220, 250))
    # pines on the far hills
    for px, ph, base in ((60, 120, 800), (980, 150, 790), (1045, 110, 800), (560, 90, 760)):
        for i in range(3):
            w_ = (48 - i * 12) * ph / 120; y0 = base - ph * (0.25 + 0.3 * i)
            d.polygon([(px - w_, y0 + ph * 0.38), (px, y0 - ph * 0.12), (px + w_, y0 + ph * 0.38)], fill=(88, 120, 150))
            d.polygon([(px - w_ * 0.5, y0 + ph * 0.05), (px, y0 - ph * 0.12), (px + w_ * 0.5, y0 + ph * 0.05)], fill=SNOW)
        d.rectangle([px - 7, base - 10, px + 7, base + 6], fill=(110, 80, 70))
    # snow slope + foreground
    d.polygon([(0, 790), (W, 800), (W, H), (0, H)], fill=(236, 232, 252))
    d.line([(0, 790), (W, 800)], fill=SNOW_S, width=4)
    pts = [(x, hill_y(x)) for x in range(0, W + 1, 20)]
    d.polygon(pts + [(W, H), (0, H)], fill=SNOW)
    d.line(pts, fill=SNOW_S, width=6)
    for i in range(14):   # soft drifts
        x = (i * 173) % W; y = 1000 + (i * 97) % 820
        d.ellipse([x - 110, y - 18, x + 110, y + 18], fill=(236, 232, 252))
    return im
BG = make_bg()

FLAKES = [(np.random.default_rng(7).random(3)) for _ in range(1)]
_r = np.random.default_rng(10); FL = _r.random((60, 4))
def snowflakes(img, t):
    d = ImageDraw.Draw(img)
    for fx, fy0, sp, sz in FL:
        y = (fy0 * H + t * (40 + 60 * sp)) % H
        x = fx * W + math.sin(t * 1.3 + fx * 20) * 18
        if BY0 - 8 < y < BY1 + 8 and BX0 - 8 < x < BX1 + 8: continue
        r = 3 + sz * 5
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

def txt(img, xy, s, size, fill=INK2, scale=1.0, path=None, alpha=1.0):
    pop_text(img, xy, s, path or F_NUM, size, fill, scale=scale, alpha=alpha)
def money(v): return f"${v:,.0f}"

def board(img, title=None, col=MARK_B):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([BX0 + 8, BY0 + 12, BX1 + 8, BY1 + 14], radius=18, fill=(170, 150, 210))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=18, fill=FRAME)
    d.rounded_rectangle([BX0 + 12, BY0 + 12, BX1 - 12, BY1 - 12], radius=10, fill=PAPER)
    d.line([(560, BY0 + 34), (560, BY1 - 34)], fill=(225, 222, 236), width=3)
    if title:
        txt(img, (BC, BY0 + 58), title, 42, col)

# ---------- chart (right half of the board) ----------
def cx_(y): return CX0 + 40 + (CX1 - CX0 - 60) * y / 30
def cy_(v, vmax=80000): return CY1 - (CY1 - CY0) * v / vmax
def axes(d, ymax=80000, labels=(0, 40000, 80000), fmt=lambda v: f"${v/1000:.0f}K"):
    d.line([(cx_(0), CY0 - 6), (cx_(0), CY1)], fill=(150, 146, 170), width=4)
    d.line([(cx_(0), CY1), (cx_(30) + 10, CY1)], fill=(150, 146, 170), width=4)
    for v in labels:
        y = cy_(v, ymax)
        d.text((cx_(0) - 10, y), fmt(v), font=font(F_MED, 22), fill=(130, 126, 150), anchor="rm")
    for yr in (0, 10, 20, 30):
        d.text((cx_(yr), CY1 + 22), f"{yr}", font=font(F_MED, 22), fill=(130, 126, 150), anchor="mm")
    d.text((cx_(30), CY1 + 22), "30 YRS", font=font(F_MED, 22), fill=(130, 126, 150), anchor="rm")

def line_chart(img, t, theo_k=1.0, real_k=0.0, area=False, end_labels=True):
    d = ImageDraw.Draw(img)
    axes(d)
    if area and real_k > 0:   # deposit band vs interest
        pts = [(cx_(y), cy_(real_v(y))) for y in np.linspace(0, 30, 61)]
        d.polygon(pts + [(cx_(30), cy_(P0)), (cx_(0), cy_(P0))], fill=(200, 236, 212))
        d.rectangle([cx_(0), cy_(P0), cx_(30), CY1 - 2], fill=(214, 220, 244))
        d.text((cx_(18), cy_(P0 / 2) + 2), "YOUR $10K", font=font(F_NUM, 22), fill=MARK_B, anchor="mm")
        d.text((cx_(21), cy_(24000)), "INTEREST", font=font(F_NUM, 24), fill=MARK_G, anchor="mm")
    if theo_k > 0:   # Theo's straight dashed line
        ye = 30 * theo_k
        n = 24
        for i in range(n):
            a0, a1 = i / n * 30, (i + 0.55) / n * 30
            if a0 > ye: break
            a1 = min(a1, ye)
            d.line([(cx_(a0), cy_(theo_v(a0))), (cx_(a1), cy_(theo_v(a1)))], fill=MARK_B, width=8)
        if end_labels and theo_k >= 1:
            d.text((cx_(30) - 4, cy_(31000) + 30), "$31,000", font=font(F_NUM, 30), fill=MARK_B, anchor="rm")
    if real_k > 0:
        ye = 30 * real_k
        pts = [(cx_(y), cy_(real_v(y))) for y in np.linspace(0, ye, max(2, int(60 * real_k)))]
        d.line(pts, fill=MARK_G, width=10, joint="curve")
        ex, ey = pts[-1]
        d.ellipse([ex - 11, ey - 11, ex + 11, ey + 11], fill=MARK_G)
        if end_labels and real_k >= 1:
            d.text((cx_(30) - 18, cy_(76123) - 4), "$76,123", font=font(F_NUM, 32), fill=MARK_G, anchor="rm")

INTS = [real_v(y) * R for y in range(30)]
def bar_chart(img, t, nshow, hi=None):
    d = ImageDraw.Draw(img)
    axes(d, 5000, (0, 2500, 5000), fmt=lambda v: f"${v:,.0f}")
    bw = (cx_(30) - cx_(0)) / 30
    for i in range(int(nshow)):
        x0 = cx_(i) + 2; v = INTS[i]
        col = MARK_G if i == hi else (170, 214, 186)
        d.rectangle([x0, cy_(v, 5000), x0 + bw - 4, CY1 - 2], fill=col)
    d.text((cx_(15), CY0 - 22), "INTEREST EARNED EACH YEAR", font=font(F_NUM, 22), fill=INK2, anchor="mm")

# ---------- board scenes ----------
def bd_hook(img, t):
    board(img, "THEO'S MATHS")
    k = 1 + 0.03 * math.sin(t * 5)
    txt(img, (BC, 410), "7% x 30 YEARS", 52, MARK_B)
    txt(img, (BC, 485), "= 210%", 70, MARK_B, scale=k)
    txt(img, (BC, 568), "$10,000 >", 48, INK2)
    txt(img, (BC, 640), "$31,000", 84, MARK_B, scale=k)
    line_chart(img, t, 1.0, 0.0)

def bd_no(img, t):
    board(img, "COMPOUNDED", MARK_G)
    kt = clamp((t - tok("no", 2)) / 1.0)
    txt(img, (BC, 400), "THEO: $31,000", 40, (130, 126, 150))
    d = ImageDraw.Draw(img)
    d.line([(BC - 150, 402), (BC + 150, 402)], fill=MARK_R, width=6)
    k = ease_back((t - tok("no", 2) + 0.05) / 0.3)
    txt(img, (BC, 515), "$76,123", 110, MARK_G, scale=k)
    txt(img, (BC, 625), "AFTER 30 YEARS", 36, INK2, alpha=clamp(k))
    line_chart(img, t, 1.0, ease_out(kt))

def bd_y1(img, t):
    board(img, "YEAR ONE", MARK_G)
    txt(img, (BC, 410), "7% OF $10,000", 46, INK2)
    k = ease_back((t - tok("y1", 2) + 0.05) / 0.3)
    txt(img, (BC, 530), "+$700", 120, MARK_G, scale=k)
    bar_chart(img, t, 1, hi=0)

def bd_y30(img, t):
    board(img, "YEAR THIRTY", MARK_G)
    n = 1 + 29 * ease_out((t - tok("y30", 0)) / 1.4)
    txt(img, (BC, 410), "7% OF $71,143", 46, INK2)
    k = ease_back((t - tok("y30", 3) + 0.05) / 0.3)
    txt(img, (BC, 520), "+$4,980", 108, MARK_G, scale=k)
    k2 = ease_back((t - tok("y30", 4)) / 0.3)
    txt(img, (BC, 630), "SAME 7%!", 50, MARK_B, scale=k2)
    bar_chart(img, t, n, hi=29 if n >= 29.5 else None)

def bd_why(img, t):
    board(img, "INTEREST ON INTEREST", MARK_G)
    txt(img, (BC, 400), "YOU PUT IN", 34, INK2)
    txt(img, (BC, 450), "$10,000", 56, MARK_B)
    k = ease_back((t - tok("why", 2)) / 0.3)
    txt(img, (BC, 525), "INTEREST MADE", 34, INK2, scale=k)
    txt(img, (BC, 585), "+$66,123", 72, MARK_G, scale=k)
    line_chart(img, t, 0.0, 1.0, area=True, end_labels=False)

def stamp(img, s, xy, k, col=MARK_R, w=440, h=120, rot=-7, size=56):
    if k <= 0.05: return
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle([4, 4, w - 5, h - 5], radius=16, outline=col, width=9)
    pop_text(lay, (w / 2, h / 2), s, F_NUM, size, col)
    lay = lay.resize((max(2, int(w * k)), max(2, int(h * k)))).rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2)))

def bd_punch(img, t):
    board(img, "THEO'S ERROR", MARK_R)
    txt(img, (BC, 400), "$76,123 - $31,000", 40, INK2)
    k = ease_back((t - tok("punch", 2) + 0.05) / 0.3)
    txt(img, (BC, 505), "$45,123", 110, MARK_G, scale=k)
    txt(img, (BC, 610), "...IN HIS FAVOR", 40, MARK_B, scale=ease_back((t - tok("punch", 3)) / 0.3))
    line_chart(img, t, 1.0, 1.0)
    d = ImageDraw.Draw(img)
    x = cx_(30) + 2
    d.line([(x, cy_(31000) - 8), (x, cy_(76123) + 16)], fill=MARK_R, width=6)
    stamp(img, "BEST MISTAKE EVER", (795, 600), ease_back((t - tok("punch", 4) - 0.1) / 0.25), MARK_R, 400, 90, -6, 38)

def bd_fix(img, t):
    board(img, "THE CATCH", MARK_B)
    s0 = seg_start("fix")
    for i, line in enumerate(("NO WITHDRAWALS", "NO PANIC SELLING", "30 YEARS OF PATIENCE")):
        k = ease_back((t - s0 - 0.25 * i) / 0.3)
        txt(img, (BC, 410 + i * 82), line, 40, (MARK_B, MARK_B, MARK_G)[i], scale=k)
    txt(img, (BC, 640), "Returns vary. Some years are negative.", 24, (120, 116, 140), path=F_HAND)
    line_chart(img, t, 0.0, 1.0)

def bd_q(img, t):
    board(img, "YOUR GUESS?", MARK_B)
    s0 = seg_start("q")
    d = ImageDraw.Draw(img)
    for i, (lab, col) in enumerate([("$31,000", MARK_B), ("$76,123", C_GREEN)]):
        y = 420 + i * 95
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([BC - 190 * k, y - 36 * k, BC + 190 * k, y + 36 * k], radius=36 * k, fill=col)
        pop_text(img, (BC, y), lab, F_NUM, 50 * k, WHITE)
    if t > tok("q", 4) - 0.1:
        txt(img, (BC, 630), "TELL US BELOW", 44, MARK_R, scale=ease_back((t - tok("q", 4) + 0.1) / 0.3))
    line_chart(img, t, 1.0, 1.0)

BOARDS = {"hook": bd_hook, "no": bd_no, "y1": bd_y1, "y30": bd_y30, "why": bd_why, "punch": bd_punch,
          "fix": bd_fix, "q": bd_q, "loop": bd_hook}

# ---------- snowball on the slope ----------
def ball_state(t):
    """returns (year, value, label colour)"""
    if t < seg_start("no"):
        k = ease_out((t - tok("hook", 3)) / 2.2)
        return 30 * k, theo_v(30 * k), MARK_B
    if t < seg_start("y1"):
        k = ease_out((t - tok("no", 2) + 0.05) / 0.6)
        return 30, lerp(31000, real_v(30), k), MARK_G
    if t < seg_start("y30"):
        k = ease_out((t - seg_start("y1")) / 0.45)
        y = lerp(30, 1, k)
        return y, real_v(y), MARK_G
    if t < seg_start("why"):
        k = ease_out((t - tok("y30", 0)) / 1.4)
        y = lerp(1, 30, k)
        return y, real_v(y), MARK_G
    if t < seg_start("loop"):
        return 30, real_v(30), MARK_G
    k = ease_out((t - seg_start("loop")) / 0.6)
    y = lerp(30, 0, k)
    return y, lerp(real_v(30), P0, k), MARK_B

def snowball(img, t):
    yr, v, col = ball_state(t)
    x = lerp(BALL_X0, BALL_X1, yr / 30)
    r = 28 * math.sqrt(v / P0)
    cy = hill_y(x) - r + 6
    d = ImageDraw.Draw(img)
    # track behind the ball
    d.line([(BALL_X0 - 30, hill_y(BALL_X0 - 30) + 2), (x, hill_y(x) + 2)], fill=SNOW_S, width=10)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([x - r * 0.95, hill_y(x) - 4, x + r * 0.95, hill_y(x) + 14], fill=(120, 100, 170, 70))
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, cy - r, x + r, cy + r], fill=(255, 255, 255), outline=(196, 190, 230), width=4)
    d.chord([x - r, cy - r, x + r, cy + r], 20, 160, fill=(228, 224, 248))
    ang = (x - BALL_X0) / max(r, 1)
    for a in (0, 2.1, 4.2):
        px, py = x + math.cos(ang + a) * r * 0.55, cy + math.sin(ang + a) * r * 0.55
        rr = max(2, r * 0.12)
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(210, 204, 240))
    # value tag
    lab = money(v)
    f = font(F_NUM, 36); wl = tw(lab, F_NUM, 36)
    ty = cy - r - 38
    d.rounded_rectangle([x - wl / 2 - 18, ty - 26, x + wl / 2 + 18, ty + 26], radius=26, fill=col)
    d.text((x, ty), lab, font=f, fill=WHITE, anchor="mm")
    d.text((x, ty - 46), f"YEAR {round(yr):d}", font=font(F_NUM, 24), fill=INK2, anchor="mm")
    # yearly interest chips
    s = scene_at(t)["scene"]
    if s == "y1":
        txt(img, (x + 92, cy - 4), "+$700", 36, MARK_G, scale=ease_back((t - tok("y1", 2)) / 0.3))
    if s == "y30" and yr > 29.5:
        txt(img, (x - r - 92, cy + 4), "+$4,980", 36, MARK_G, scale=ease_back((t - tok("y30", 3)) / 0.3))

STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("shrug", "worried", "point_up", "smile"),
         "y1": ("idle", "smile", "marker", "smile"), "y30": ("idle", "worried", "marker", "smile"),
         "why": ("shrug", "worried", "point_up", "smile"), "punch": ("cheer", "smug", "facepalm", "facepalm"),
         "fix": ("idle", "worried", "marker", "smile"), "q": ("idle", "smile", "shrug", "smile"),
         "loop": ("cheer", "smug", "idle", "worried")}

TX_, NX_, CYC = 150, 925, 1090

def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("T", TX_, THEO, tp, tm), ("N", NX_, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.2 if who == spk else 1.12
        person(img, cx, CYC + (0 if who == spk else 10), sc, col, who, t, talk=talking, pose=pose, mood=mood)

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
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 90, col, scale=gk * (1.05 if active else 1.0), stroke=12, sfill=(36, 24, 70))
            x += widths[i] + space

def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=CORAL)
    lab1, lab2 = "THEO EXPLAINS #10", "COMPOUND INTEREST"
    f1 = font(F_NUM, 42)
    w1 = tw(lab1, F_NUM, 42) + 46; w2 = tw(lab2, F_NUM, 42) + 46
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 165, x0 + w1 + 30, 243], radius=39, fill=THEO)
    d.rounded_rectangle([x0 + w1, 165, x0 + total, 243], radius=39, fill=INK2)
    d.rectangle([x0 + w1, 165, x0 + w1 + 30, 243], fill=INK2)
    d.text((x0 + w1 / 2, 204), lab1, font=f1, fill=INK2, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 204), lab2, font=f1, fill=YEL, anchor="mm")
    c = INK2
    d.text((W / 2, 1530), "Example: $10,000 at 7% a year, compounded yearly, 30 years,", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1566), "no fees, taxes or new deposits. Real returns vary and can be", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1602), "negative. Not a forecast. Not financial advice.", font=font(F_MED, 27), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    snowflakes(img, t)
    BOARDS[s["scene"]](img, t)
    draw_cast(img, t)
    snowball(img, t)
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
