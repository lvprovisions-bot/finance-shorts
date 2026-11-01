"""THEO EXPLAINS #7: marginal vs effective tax rate. 1080x1920 @30fps. Pastel mint diagonal stripes, green chalkboard, stacked salary bar, chalk pies. Nora left / Theo right."""
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




# ---------- palette (episode 7: pastel mint diagonal stripes, green chalkboard with chalk tray, stacked salary bar) ----------
WOOD = (176, 120, 70); WOOD2 = (140, 92, 52); SLATE = (38, 78, 62); SLATE_D = (32, 66, 53)
CH_W = (240, 242, 232); CH_Y = (255, 232, 120); CH_P = (255, 150, 175); CH_B = (150, 210, 255); CH_G = (150, 235, 160); CH_V = (200, 170, 255)
C_GREEN = (34, 160, 90); C_RED = (220, 50, 60); C_NAVY = (30, 60, 70); CORAL = (255, 112, 96); PAPER = (255, 252, 240)

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    base = np.array((214, 246, 228), np.float32)
    img = np.ones((H, W, 3), np.float32) * base
    st = (((xx + yy) // 60) % 2 == 0)[..., None]
    img = np.where(st, img * 0.955 + np.array((150, 220, 190)) * 0.045, img)
    f = (yy / H)[..., None]
    img = img * (1 - 0.07 * f)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

BX0, BY0, BX1, BY1 = 70, 300, 1010, 850
rng = np.random.default_rng(7)
SMUDGE = [(int(rng.uniform(BX0 + 40, BX1 - 40)), int(rng.uniform(BY0 + 40, BY1 - 40)), int(rng.uniform(30, 90))) for _ in range(14)]

def chalk(img, xy, s, size, fill=CH_W, scale=1.0, path=None, alpha=0.95):
    pop_text(img, xy, s, path or F_HAND, size, fill, scale=scale, alpha=alpha)

def board(img, t, title="THEO'S MATHS"):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([BX0 + 10, BY0 + 16, BX1 + 10, BY1 + 30], radius=18, fill=(40, 110, 80, 60))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=18, fill=WOOD)
    d.rectangle([BX0 + 22, BY0 + 22, BX1 - 22, BY1 - 22], fill=SLATE)
    for x, y, r in SMUDGE:
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=SLATE_D)
    d.rounded_rectangle([BX0 - 10, BY1 - 6, BX1 + 10, BY1 + 22], radius=8, fill=WOOD2)   # chalk tray
    d.rounded_rectangle([BX1 - 200, BY1 - 18, BX1 - 140, BY1 - 4], radius=6, fill=CH_W)
    d.rounded_rectangle([BX1 - 120, BY1 - 18, BX1 - 70, BY1 - 4], radius=6, fill=CH_P)
    img.alpha_composite(lay)
    chalk(img, (W / 2, BY0 + 72), title, 44, CH_Y)
    d = ImageDraw.Draw(img)
    w = tw(title, F_HAND, 44)
    d.line([(W / 2 - w / 2, BY0 + 104), (W / 2 + w / 2, BY0 + 100)], fill=CH_Y, width=4)

def money(v): return f"${v:,.0f}"

def pie(img, cx, cy, r, frac, col, label, s=1.0):
    if s < 0.05: return
    d = ImageDraw.Draw(img); r = r * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CH_W, width=6)
    if frac > 0.003:
        d.pieslice([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], -90, -90 + 360 * frac, fill=col)
    chalk(img, (cx, cy + r + 40 * s), label, 40 * s, CH_W)

def strike(img, x0, y, x1, k, col=CH_P):
    if k <= 0: return
    ImageDraw.Draw(img).line([(x0, y + 8), (lerp(x0, x1, k), y - 8)], fill=col, width=10)

def bd_hook(img, t):
    board(img, t)
    chalk(img, (420, 470), "$80,000 x 22%", 76)
    chalk(img, (420, 600), "= $17,600", 92, CH_P)
    chalk(img, (420, 715), "TAX?!", 60, CH_Y)
    pie(img, 840, 560, 105, 0.22, CH_P, "22% OF ALL?")

# stacked salary bar
BAR_X0, BAR_X1, BAR_Y, BAR_H = 125, 955, 515, 105
SC = (BAR_X1 - BAR_X0) / 80000
SEGS = [(16100, CH_G, "0%", "$0"), (12400, CH_B, "10%", "$1,240"), (38000, CH_V, "12%", "$4,560"), (13500, CH_P, "22%", "$2,970")]
def salary_bar(img, t, shown):
    """shown: list of 4 floats 0..1 (reveal of each coloured slice)"""
    d = ImageDraw.Draw(img)
    d.rectangle([BAR_X0, BAR_Y, BAR_X1, BAR_Y + BAR_H], outline=CH_W, width=5)
    x = BAR_X0
    for (amt, col, rate, tax), k in zip(SEGS, shown):
        w = amt * SC
        if k > 0.1:
            d.rectangle([x + 4, BAR_Y + 4 + BAR_H * (1 - k) * 0.5, x + w - 4, BAR_Y + BAR_H - 4 - BAR_H * (1 - k) * 0.5], fill=col)
            chalk(img, (x + w / 2, BAR_Y + BAR_H / 2), rate, 46, SLATE, scale=ease_back(k), alpha=1.0)
            chalk(img, (x + w / 2, BAR_Y + BAR_H + 42), tax, 40, col, scale=ease_back(k))
        x += w
        d.line([(x, BAR_Y - 6), (x, BAR_Y + BAR_H + 6)], fill=CH_W, width=3)

def tax_counter(img, t, val):
    chalk(img, (W / 2, 738), "TAX SO FAR: " + money(val), 52, CH_Y)

def bd_no(img, t):
    board(img, t, title="WHERE $80K GETS TAXED")
    s0 = seg_start("no")
    k = ease_out((t - tok("no", 1)) / 0.5)
    salary_bar(img, t, [0, 0, 0, k])
    if k > 0.3:
        x = BAR_X1 - 13500 * SC / 2
        d = ImageDraw.Draw(img); bob = math.sin(t * 8) * 8
        d.line([(x, 420 + bob), (x, 470 + bob)], fill=CH_P, width=8)
        d.polygon([(x - 22, 462 + bob), (x + 22, 462 + bob), (x, 494 + bob)], fill=CH_P)
        chalk(img, (x - 190, 440 + bob), "ONLY HERE", 50, CH_P)

def bd_ded(img, t):
    board(img, t, title="WHERE $80K GETS TAXED")
    k = ease_out((t - tok("ded", 1) + 0.1) / 0.5)
    salary_bar(img, t, [k, 0, 0, 1])
    if k > 0.5:
        chalk(img, (BAR_X0 + 16100 * SC / 2 + 40, 448), "TAX-FREE", 46, CH_G, scale=ease_back((t - tok("ded", 3)) / 0.3))
    tax_counter(img, t, 0)

def bd_slices(img, t):
    board(img, t, title="WHERE $80K GETS TAXED")
    k1 = ease_out((t - tok("slices", 0)) / 0.4); k2 = ease_out((t - tok("slices", 1)) / 0.4)
    k3 = ease_out((t - tok("slices", 3) + 0.1) / 0.3)
    salary_bar(img, t, [1, k1, k2, 1])
    if k3 > 0:
        d = ImageDraw.Draw(img); x0 = BAR_X1 - 13500 * SC
        d.rounded_rectangle([x0 - 8, BAR_Y - 14, BAR_X1 + 8, BAR_Y + BAR_H + 14], radius=12, outline=CH_Y, width=int(4 + 4 * k3))
        chalk(img, (x0 - 30, 448), "LAST $13,500", 44, CH_P, scale=ease_back(k3))
    val = 1240 * k1 + 4560 * k2 + 2970 * k3
    tax_counter(img, t, val)

def bd_total(img, t):
    board(img, t, title="THE REAL BILL")
    s0 = seg_start("total")
    chalk(img, (300, 460), "THEO", 44, CH_W)
    chalk(img, (300, 550), "$17,600", 80, CH_P)
    strike(img, 150, 550, 450, ease_out((t - s0) / 0.4))
    chalk(img, (780, 460), "REAL", 44, CH_W)
    k = ease_out((t - tok("total", 1) + 0.1) / 0.8)
    chalk(img, (780, 550), money(8770 * k), 80, CH_G, scale=ease_back((t - tok("total", 1) + 0.1) / 0.3))
    kk = ease_back((t - tok("total", 2)) / 0.35)
    pie(img, 330, 715, 55, 0.22, CH_P, "", s=1.0)
    pie(img, 810, 715, 55, 0.11 * min(1, kk) if kk > 0 else 0, CH_G, "", s=1.0)
    chalk(img, (465, 715), "22%", 48, CH_P)
    chalk(img, (650, 715), "~11%", 48, CH_G, scale=kk)

def bd_punch(img, t):
    board(img, t, title="THEO'S PARTY TOPICS")
    s0 = seg_start("punch")
    items = [("1. MY TAX BILL", True), ("2. MY TAX BILL", True), ("3. ...", False)]
    for i, (txt, cross) in enumerate(items):
        y = 460 + i * 115
        k = ease_back((t - s0 - 0.15 * i) / 0.3)
        chalk(img, (W / 2, y), txt, 64, CH_W if cross else CH_Y, scale=k)
        if cross:
            w = tw(txt, F_HAND, 64)
            strike(img, W / 2 - w / 2, y, W / 2 + w / 2, ease_out((t - tok("punch", 2) - 0.15 * i) / 0.3))
    if t > tok("punch", 4):
        d = ImageDraw.Draw(img)   # party hat on the board
        hx, hy = 860, 700
        d.polygon([(hx - 50, hy + 60), (hx + 50, hy + 60), (hx, hy - 70)], outline=CH_Y, width=6)
        d.ellipse([hx - 14, hy - 90, hx + 14, hy - 62], fill=CH_P)

def bd_q(img, t):
    board(img, t, title="YOUR TURN")
    s0 = seg_start("q")
    chalk(img, (W / 2, 450), "YOUR RATE?", 84, CH_W)
    d = ImageDraw.Draw(img)
    for i, (lab, col) in enumerate([("MY BRACKET", CORAL), ("WAY LESS", C_GREEN)]):
        x = 310 + i * 460; y = 610
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([x - 190 * k, y - 58 * k, x + 190 * k, y + 58 * k], radius=30 * k, fill=col)
        pop_text(img, (x, y), lab, F_NUM, 44 * k, WHITE)
    if t > tok("q", 3) - 0.1:
        chalk(img, (W / 2, 760), "TELL US BELOW", 58, CH_Y, scale=ease_back((t - tok("q", 3) + 0.1) / 0.3))

BOARDS = {"hook": bd_hook, "no": bd_no, "ded": bd_ded, "slices": bd_slices, "total": bd_total,
          "punch": bd_punch, "q": bd_q, "loop": bd_hook}
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "worried", "point_up", "smile"),
         "ded": ("idle", "smile", "point_up", "smile"), "slices": ("idle", "worried", "point_up", "smile"),
         "total": ("cheer", "smile", "point_up", "smile"), "punch": ("shrug", "worried", "facepalm", "facepalm"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("cheer", "smug", "idle", "worried")}

NX, TX, CY = 290, 790, 1065

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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=CORAL)
    lab1, lab2 = "THEO EXPLAINS #7", "TAX RATES"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=C_NAVY)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=C_NAVY)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=C_NAVY, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (40, 90, 70)
    d.text((W / 2, 1530), "Illustration: single filer, $80K salary, IRS 2026 brackets + $16,100 std deduction.", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1568), "Federal income tax only (no state, FICA or credits). Not financial advice.", font=font(F_MED, 26), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
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
