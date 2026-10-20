"""THEO EXPLAINS #1: Tax brackets. 1080x1920 @30fps. Light lavender pastel, whiteboard prop, Theo & Nora large."""
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

# ---------- background: lavender pastel with soft dots ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((236, 230, 255), np.float32); bot = np.array((214, 206, 250), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - 560) * 0.9) ** 2) / 900
    img += (np.clip(1 - d, 0, 1) ** 2)[..., None] * 14
    dots = ((xx % 60 < 6) & (yy % 60 < 6)).astype(np.float32)
    img -= dots[..., None] * 10
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

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
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(60, 40, 120, 50))
    img.alpha_composite(sh); img.alpha_composite(lay)

# ---------- whiteboard ----------
BX0, BY0, BX1, BY1 = 70, 290, 1010, 770
def board(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([BX0 + 8, BY0 + 12, BX1 + 8, BY1 + 12], radius=26, fill=(60, 40, 120, 45))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=26, fill=(250, 250, 255), outline=(150, 150, 175), width=10)
    d.rectangle([BX0 + 120, BY1 + 2, BX1 - 120, BY1 + 18], fill=(170, 170, 190))  # marker tray
    d.rounded_rectangle([BX0 + 160, BY1 - 2, BX0 + 240, BY1 + 12], radius=6, fill=RED)
    d.rounded_rectangle([BX0 + 260, BY1 - 2, BX0 + 340, BY1 + 12], radius=6, fill=BLUE_INK)
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

def hook_board(img, t, k=1.0):
    pop_text(img, (W / 2, 365), "MY RAISE: +$2,000", F_HAND, 70, BLUE_INK, scale=k)
    pop_text(img, (W / 2, 470), "= 22% BRACKET", F_HAND, 90, RED, scale=k)
    pop_text(img, (W / 2, 585), "= TAXED MORE?!", F_HAND, 84, INK, scale=k)

def bd_hook(img, t):
    hook_board(img, t)
    th = tok("hook", 1)
    if t > th - 0.05:
        stamp(img, 790, 700, 0.5 * ease_back((t - th + 0.05) / 0.3), "NO THANKS", RED, angle=10)

def bd_tmath(img, t):
    lines = [(tok("tmath", 0), "$50,000 × 12% = $6,000", BLUE_INK, 395),
             (tok("tmath", 2), "$52,000 × 22% = $11,440", BLUE_INK, 500)]
    for ts, s, c, y in lines:
        if t > ts - 0.1:
            pop_text(img, (W / 2, y), s, F_HAND, 68, c, scale=ease_back((t - ts + 0.1) / 0.3))
    ts = tok("tmath", 4)
    if t > ts - 0.1:
        k = ease_back((t - ts + 0.1) / 0.3)
        pop_text(img, (W / 2, 640), "TAX +$5,440?!", F_HAND, 100, RED, scale=k)

def bd_no(img, t):
    s0 = seg_start("no")
    bd_tmath(img, 99)
    k = ease_back((t - s0) / 0.3)
    d = ImageDraw.Draw(img)
    w = int(22 * k) if k > 0.05 else 0
    if w:
        d.line([(BX0 + 90, BY0 + 70), (BX0 + 90 + (BX1 - BX0 - 180) * min(1, k), BY0 + 70 + (BY1 - BY0 - 140) * min(1, k))], fill=RED, width=w)
        d.line([(BX1 - 90, BY0 + 70), (BX1 - 90 - (BX1 - BX0 - 180) * min(1, k), BY0 + 70 + (BY1 - BY0 - 140) * min(1, k))], fill=RED, width=w)
    tw_ = tok("no", 2)
    if t > tw_ - 0.1:
        stamp(img, W / 2, 530, 0.9 * ease_back((t - tw_ + 0.1) / 0.3), "WRONG", RED, angle=-8, back=(255, 255, 255))

BUCKETS = [  # (rate, amount in it, fill fraction, colour, label)
    ("10%", 12400, 1.0, B10, "$12,400"), ("12%", 38000, 1.0, B12, "$38,000"), ("22%", 1600, 0.12, B22, "$1,600")]
def bucket(img, cx, top, wdt, hgt, frac, col, rate, label, k):
    if k < 0.03: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bot = top + hgt; inset = wdt * 0.12
    poly = [(cx - wdt / 2, top), (cx + wdt / 2, top), (cx + wdt / 2 - inset, bot), (cx - wdt / 2 + inset, bot)]
    d.polygon(poly, fill=(235, 235, 245, 255))
    if frac > 0:
        fy = bot - hgt * frac
        fi = inset * (bot - fy) / hgt
        d.polygon([(cx - wdt / 2 + fi, fy), (cx + wdt / 2 - fi, fy), (cx + wdt / 2 - inset, bot), (cx - wdt / 2 + inset, bot)], fill=col + (255,))
    d.line(poly + [poly[0]], fill=INK + (255,), width=7)
    d.arc([cx - wdt / 2 + 10, top - 70, cx + wdt / 2 - 10, top + 40], 200, 340, fill=INK + (255,), width=6)  # handle
    img.alpha_composite(lay)
    pop_text(img, (cx, top + hgt * 0.42), rate, F_NUM, 64, INK if frac < 0.6 else WHITE, stroke=0)
    pop_text(img, (cx, bot + 42), label, F_HAND, 46, INK)

def bd_bkt(img, t):
    pop_text(img, (W / 2, 340), "THEO'S $52,000", F_HAND, 58, BLUE_INK)
    starts = [tok("bkt", 2), tok("bkt", 5), tok("bkt", 8)]
    for i, ((rate, amt, frac, col, lab), ts) in enumerate(zip(BUCKETS, starts)):
        cx = 245 + i * 295
        k = ease_back((t - seg_start("bkt")) / 0.35)
        f = frac * ease_out((t - ts) / 0.8) if t > ts else 0
        bucket(img, cx, 470, 210, 175, f, col, rate, lab if t > ts else "", k)
    if t > tok("bkt", 8) - 0.1:
        k = ease_out((t - tok("bkt", 8) + 0.1) / 0.4)
        pass

def bd_raise(img, t):
    s0 = seg_start("raise")
    pop_text(img, (W / 2, 360), "THE $2,000 RAISE", F_HAND, 62, BLUE_INK)
    L, R, y0, y1 = 140, 940, 440, 560
    d = ImageDraw.Draw(img)
    k = ease_out((t - s0) / 0.5)
    d.rounded_rectangle([L, y0, L + (R - L) * k, y1], radius=26, fill=(200, 200, 215))
    tt, tk_ = tok("raise", 2), tok("raise", 4)
    xs = L + (R - L) * 0.8
    if t > tt - 0.1:
        u = ease_out((t - tt + 0.1) / 0.4)
        d.rounded_rectangle([L, y0, L + (xs - L) * u, y1], radius=26, fill=GREEN)
        d.rounded_rectangle([xs + 8, y0, xs + 8 + (R - xs - 8) * u, y1], radius=26, fill=RED)
        if u > 0.95:
            pop_text(img, ((L + xs) / 2, (y0 + y1) / 2), "KEEP", F_NUM, 56, WHITE)
            pop_text(img, ((xs + R) / 2 + 4, (y0 + y1) / 2), "TAX", F_NUM, 40, WHITE)
            pop_text(img, ((xs + R) / 2 + 4, y1 + 60), "$400", F_NUM, 64, RED, scale=ease_back((t - tok("raise", 3) + 0.1) / 0.3) if t > tok("raise", 3) - 0.1 else 0)
    if t > tk_ - 0.1:
        pop_text(img, ((L + xs) / 2, y1 + 70), "+$1,600", F_NUM, 104, GREEN, scale=ease_back((t - tk_ + 0.1) / 0.35))
    pop_text(img, ((xs + R) / 2 - 20, 700), "(not +$5,440)", F_HAND, 32, GREY)

def bd_turn(img, t):
    pop_text(img, (W / 2, 420), "RAISE = MORE", F_HAND, 100, GREEN)
    pop_text(img, (W / 2, 545), "TAKE-HOME PAY", F_HAND, 84, GREEN)
    if scene_at(t)["scene"] == "never":
        pop_text(img, (W / 2, 670), "(brackets alone can't stop that)", F_HAND, 42, GREY,
                 scale=ease_out((t - seg_start("never")) / 0.3))

def bd_punch(img, t):
    s0 = seg_start("punch")
    pop_text(img, (W / 2, 370), "THEO'S NEW PLAN:", F_HAND, 60, BLUE_INK)
    pop_text(img, (W / 2, 495), "ASK FOR", F_HAND, 92, INK)
    if t > tok("punch", 1) - 0.1:
        pop_text(img, (W / 2, 625), "2 RAISES", F_HAND, 110, RED, scale=ease_back((t - tok("punch", 1) + 0.1) / 0.3))
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate([(170, 370), (910, 380), (180, 690), (900, 690)]):
        r = 22 + 6 * math.sin(t * 8 + i)
        pts = [(x + r * math.cos(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45),
                y + r * math.sin(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45)) for a in range(10)]
        d.polygon(pts, fill=YEL, outline=(200, 150, 0))

def bd_q(img, t):
    s0 = seg_start("q")
    pop_text(img, (W / 2, 370), "WHICH DID YOU THINK?", F_HAND, 58, BLUE_INK)
    d = ImageDraw.Draw(img)
    for i, (lab, col, sub) in enumerate([("THEO'S WAY", THEO, "all taxed at 22%"), ("NORA'S WAY", NORA, "only the top slice")]):
        x = 300 + i * 480; y = 545
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        d.rounded_rectangle([x - 210 * k, y - 100 * k, x + 210 * k, y + 100 * k], radius=30 * k, fill=col, outline=INK, width=max(1, int(6 * k)))
        pop_text(img, (x, y - 25), lab, F_NUM, 54, WHITE, scale=k)
        pop_text(img, (x, y + 45), sub, F_MED, 32, INK, scale=k)
    pop_text(img, (W / 2, 705), "TELL US BELOW", F_NUM, 50, RED, scale=ease_back((t - s0 - 0.3) / 0.35))

BOARDS = {"hook": bd_hook, "tmath": bd_tmath, "no": bd_no, "bkt": bd_bkt, "raise": bd_raise,
          "turn": bd_turn, "never": bd_turn, "punch": bd_punch, "q": bd_q, "loop": lambda img, t: hook_board(img, t)}
# per-scene staging: (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("point_up", "smug", "idle", "smile"), "tmath": ("point_up", "smug", "shrug", "smile"),
         "no": ("idle", "worried", "marker", "smile"), "bkt": ("idle", "worried", "marker", "smile"),
         "raise": ("idle", "smile", "marker", "smile"), "turn": ("shrug", "worried", "idle", "smile"),
         "never": ("idle", "smile", "point_up", "smile"), "punch": ("cheer", "smug", "facepalm", "facepalm"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("point_up", "smug", "idle", "smile")}

TX, NX, CY = 300, 780, 1030
def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("T", TX, THEO, tp, tm), ("N", NX, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.42 if who == spk else 1.30
        person(img, cx, CY + (0 if who == spk else 18), sc, col, who, t, talk=talking, pose=pose, mood=mood)
    d = ImageDraw.Draw(img)
    for who, cx, col in (("THEO", TX, THEO), ("NORA", NX, NORA)):
        pass

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

CAP_Y = 1345
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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=(140, 90, 255))
    # episode badge
    lab1, lab2 = "THEO EXPLAINS #1", "TAX BRACKETS"
    f1, f2 = font(F_NUM, 50), font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2
    x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=INK)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=INK)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=INK, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f2, fill=YEL, anchor="mm")
    # name tags under the cast
    for nm, cx, col in (("THEO", TX, THEO), ("NORA", NX, NORA)):
        pass
    # assumptions disclaimer (whole video: numbers are on screen throughout)
    c = (95, 88, 130)
    d.text((W / 2, 1515), "2026 US federal income tax, single filer, taxable income.", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1552), "Ignores state & payroll tax. Source: IRS Rev. Proc. 2025-32.", font=font(F_MED, 27), fill=c, anchor="mm")
    d.text((W / 2, 1589), "Illustration only. Not financial advice.", font=font(F_MED, 27), fill=c, anchor="mm")

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
