"""THEO EXPLAINS #8: monthly rate vs APR. 1080x1920 @30fps. Pastel rose sunburst, giant holographic credit card as the stage, magnifying glass, bill tower, rent receipt. Theo left / Nora right."""
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



# ---------- palette (episode 8: pastel rose sunburst, giant holographic credit card as the stage) ----------
C_GREEN = (34, 160, 90); CORAL = (255, 96, 110); PLUM = (70, 26, 70); PAPER = (255, 252, 240)
L_Y = (255, 226, 92); L_P = (255, 150, 170); L_G = (120, 240, 160); L_B = (170, 215, 255)
CARD_A = np.array((46, 28, 110), np.float32); CARD_B = np.array((150, 30, 120), np.float32)
CX0, CY0, CX1, CY1 = 55, 275, 1025, 860

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    img = np.ones((H, W, 3), np.float32) * np.array((255, 226, 226), np.float32)
    ang = np.arctan2(yy - 560.0, xx - 540.0)
    rays = (np.floor((ang + math.pi) / (math.pi / 11)).astype(int) % 2 == 0)[..., None]
    img = np.where(rays, img * 0.94 + np.array((255, 190, 170)) * 0.06, img)
    img = img * (1 - 0.06 * (yy / H)[..., None])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

def make_card():
    w, h = CX1 - CX0, CY1 - CY0
    y, x = np.mgrid[0:h, 0:w]
    f = ((x / w * 0.65 + y / h * 0.35))[..., None]
    a = CARD_A * (1 - f) + CARD_B * f
    a = np.dstack([np.clip(a, 0, 255), np.full((h, w), 255.0)]).astype(np.uint8)
    im = Image.fromarray(a, "RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=44, fill=255)
    im.putalpha(m)
    return im, m
CARD, CARD_M = make_card()

def txt(img, xy, s, size, fill=WHITE, scale=1.0, path=None, alpha=1.0):
    pop_text(img, xy, s, path or F_NUM, size, fill, scale=scale, alpha=alpha)

def card(img, t, title=None, chip=True):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([CX0 + 10, CY0 + 18, CX1 + 10, CY1 + 22], radius=44, fill=(120, 40, 70, 70))
    img.alpha_composite(sh)
    c = CARD.copy()
    # moving hologram sheen
    sheen = Image.new("RGBA", c.size, (0, 0, 0, 0))
    sx = (t * 170) % 1500 - 300
    ImageDraw.Draw(sheen).polygon([(sx, 0), (sx + 130, 0), (sx - 90, CY1 - CY0), (sx - 220, CY1 - CY0)], fill=(255, 255, 255, 18))
    c.alpha_composite(sheen)
    c.putalpha(CARD_M)
    img.alpha_composite(c, (CX0, CY0))
    d = ImageDraw.Draw(img)
    if chip:
        d.rounded_rectangle([105, 325, 205, 395], radius=14, fill=(240, 200, 100))
        d.line([(105, 360), (205, 360)], fill=(170, 130, 50), width=4); d.line([(155, 325), (155, 395)], fill=(170, 130, 50), width=4)
    if title:
        txt(img, (W / 2 + (60 if chip else 0), 360), title, 48, L_Y)

def money(v): return f"${v:,.0f}"

def bd_hook(img, t):
    card(img, t, "THEO'S CREDIT CARD")
    k = 1 + 0.03 * math.sin(t * 5)
    txt(img, (W / 2, 505), "ONLY 2%!", 158, L_Y, scale=k)
    txt(img, (W / 2, 650), "$5,000 x 2% = $100 A YEAR?", 58, WHITE)
    txt(img, (W / 2, 730), "*per month", 26, (210, 190, 230))

def bd_no(img, t):
    card(img, t, "THEO'S CREDIT CARD")
    txt(img, (W / 2, 505), "ONLY 2%!", 158, L_Y, alpha=0.35)
    txt(img, (W / 2, 650), "$5,000 x 2% = $100 A YEAR?", 58, WHITE, alpha=0.35)
    # magnifying glass slides over the small print
    k = ease_out((t - seg_start("no") - 0.1) / 0.6)
    lx, ly = lerp(1250, 540, k), lerp(760, 560, k); R = 215
    d = ImageDraw.Draw(img)
    d.line([(lx + R * 0.72, ly + R * 0.72), (lx + R * 1.25, ly + R * 1.05)], fill=(120, 70, 40), width=38)
    d.ellipse([lx - R - 14, ly - R - 14, lx + R + 14, ly + R + 14], fill=(60, 60, 80))
    d.ellipse([lx - R, ly - R, lx + R, ly + R], fill=PAPER)
    pz = ease_back((t - seg_start("no") - 0.55) / 0.3)
    txt(img, (lx, ly - 60), "*2%", 120, (220, 40, 60), scale=pz)
    txt(img, (lx, ly + 65), "PER MONTH", 62, PLUM, scale=pz)

def bill(d, x, y, w, h, c=(60, 190, 110)):
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=5, fill=c, outline=(20, 110, 60), width=3)
    d.ellipse([x - h * .36, y - h * .36, x + h * .36, y + h * .36], fill=(190, 240, 200))

def bd_math(img, t):
    card(img, t, "A YEAR OF 2%", chip=True)
    d = ImageDraw.Draw(img)
    base = 760
    # Theo's guess: one bill
    bill(d, 215, base - 13, 200, 24)
    txt(img, (215, 660), "$100", 74, L_P); txt(img, (215, 600), "THEO'S GUESS", 34, WHITE)
    # reality: 12 bills pile up
    s0, s1 = tok("math", 0), tok("math", 3) + 0.25
    n = int(clamp((t - s0) / (s1 - s0)) * 12 + 0.999)
    for i in range(n):
        drop = 1 - ease_out((t - (s0 + (s1 - s0) * i / 12)) / 0.18)
        bill(d, 540, base - 13 - i * 26 - drop * 60, 240, 24)
    txt(img, (830, 470), "THE REAL BILL", 34, WHITE)
    txt(img, (830, 540), money(n * 100), 92, L_G, scale=ease_back((t - s0) / 0.25))
    txt(img, (830, 620), f"{n} MONTH" + ("S" if n != 1 else ""), 40, L_Y)

def bd_apr(img, t):
    card(img, t, "THE REAL NUMBER")
    txt(img, (W / 2, 470), "2% x 12 MONTHS", 84, WHITE)
    k = ease_back((t - tok("apr", 2) + 0.1) / 0.35)
    txt(img, (W / 2, 610), "= 24% APR", 132, L_Y, scale=k)
    txt(img, (W / 2, 722), "US average: 22.36% (Fed G.19, Aug 2026)", 32, L_B, alpha=clamp(k))

def bd_owe(img, t):
    card(img, t, "AFTER PAYING ALL YEAR")
    k1 = ease_back((t - tok("owe", 1)) / 0.35)
    txt(img, (290, 450), "YOU PAID", 42, WHITE, scale=k1); txt(img, (290, 535), "$1,200", 92, L_G, scale=k1)
    k2 = ease_back((t - tok("owe", 3) + 0.05) / 0.35)
    txt(img, (790, 450), "YOU OWE", 42, WHITE, scale=k2); txt(img, (790, 535), "$5,000", 104, (255, 110, 120), scale=k2)
    k3 = ease_out((t - tok("owe", 5)) / 0.3)
    if k3 > 0:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([130, 625, 950, 685], radius=30, outline=WHITE, width=5)
        d.rounded_rectangle([140, 635, 158, 675], radius=8, fill=L_G)
        txt(img, (W / 2, 655), "DEBT PAID DOWN: $0", 40, WHITE, alpha=k3)

def bd_punch(img, t):
    card(img, t, None, chip=False)
    k = ease_back((t - seg_start("punch")) / 0.3)
    if k < 0.05: return
    lay = Image.new("RGBA", (760, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, 759, 459], radius=20, fill=PAPER)
    d.rectangle([0, 96, 759, 100], fill=(200, 190, 170))
    pop_text(lay, (380, 52), "RENT RECEIPT", F_NUM, 60, PLUM)
    pop_text(lay, (380, 165), "PROPERTY:", F_MED, 38, GREY)
    pop_text(lay, (380, 228), "MONEY YOU ALREADY SPENT", F_NUM, 48, PLUM)
    pop_text(lay, (380, 310), "$100 / MONTH", F_NUM, 72, (220, 40, 60))
    pop_text(lay, (380, 400), "UNTIL IT'S PAID OFF", F_MED, 38, GREY)
    lay = lay.resize((max(2, int(760 * k)), max(2, int(460 * k)))).rotate(-2.5, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(520 - lay.height / 2)))

def bd_q(img, t):
    card(img, t, "YOUR TURN")
    s0 = seg_start("q")
    txt(img, (W / 2, 475), "YOUR CARD'S APR?", 92, WHITE)
    d = ImageDraw.Draw(img)
    for i, (lab, col) in enumerate([("UNDER 20%", C_GREEN), ("20%+", CORAL), ("NO IDEA", (120, 90, 220))]):
        x = 215 + i * 325; y = 610
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([x - 150 * k, y - 52 * k, x + 150 * k, y + 52 * k], radius=30 * k, outline=WHITE, width=3, fill=col)
        pop_text(img, (x, y), lab, F_NUM, 38 * k, WHITE)
    if t > tok("q", 3) - 0.1:
        txt(img, (W / 2, 725), "GO CHECK. TELL US BELOW", 50, L_Y, scale=ease_back((t - tok("q", 3) + 0.1) / 0.3))

BOARDS = {"hook": bd_hook, "no": bd_no, "math": bd_math, "apr": bd_apr, "owe": bd_owe,
          "punch": bd_punch, "q": bd_q, "loop": bd_hook}
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "worried", "point_up", "smile"),
         "math": ("idle", "worried", "point_up", "smile"), "apr": ("facepalm", "worried", "point_up", "smile"),
         "owe": ("shrug", "worried", "point_up", "smile"), "punch": ("shrug", "worried", "facepalm", "facepalm"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("cheer", "smug", "idle", "worried")}

TX, NX, CY = 280, 800, 1065

def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("T", TX, THEO, tp, tm), ("N", NX, NORA, np_, nm)):
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
    lab1, lab2 = "THEO EXPLAINS #8", "APR"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=PLUM)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=PLUM)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=PLUM, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (110, 40, 80)
    d.text((W / 2, 1530), "Illustration: $5,000 balance, 2% a month, interest paid monthly, no fees.", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1568), "Simplified: real cards charge daily and require minimums. Not financial advice.", font=font(F_MED, 26), fill=c, anchor="mm")

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
