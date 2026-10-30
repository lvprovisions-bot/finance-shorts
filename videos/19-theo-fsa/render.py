"""THEO EXPLAINS #6: FSA use-it-or-lose-it. 1080x1920 @30fps. Pastel lemon gingham, wood-framed cork board with pinned sticky notes, money jars, shredder, sunscreen rain. Nora left / Theo right."""
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




# ---------- palette (episode 6: pastel lemon gingham, wood-framed cork board with pinned notes, jars, shredder) ----------
WOOD = (150, 98, 58); WOOD2 = (120, 76, 44); CORK = (214, 170, 118); CORK_D = (186, 140, 92)
NOTE_Y = (255, 236, 120); NOTE_P = (255, 190, 210); NOTE_B = (180, 225, 255); PAPER = (255, 252, 240)
C_GREEN = (34, 160, 90); C_RED = (220, 50, 60); C_NAVY = (40, 46, 96); CORAL = (255, 112, 96)

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    base = np.array((255, 246, 200), np.float32)
    img = np.ones((H, W, 3), np.float32) * base
    vs = ((xx // 70) % 2 == 0)[..., None]; hs = ((yy // 70) % 2 == 0)[..., None]
    img = np.where(vs, img * 0.965 + np.array((255, 214, 120)) * 0.035, img)
    img = np.where(hs, img * 0.965 + np.array((255, 214, 120)) * 0.035, img)
    f = (yy / H)[..., None]
    img = img * (1 - 0.06 * f)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

BX0, BY0, BX1, BY1 = 70, 300, 1010, 850
rng = np.random.default_rng(6)
SPECK = [(int(rng.uniform(BX0 + 40, BX1 - 40)), int(rng.uniform(BY0 + 40, BY1 - 40)), int(rng.uniform(2, 5))) for _ in range(420)]

def marker(img, xy, s, size, fill, scale=1.0, path=None, stroke=0, sfill=(0, 0, 0)):
    pop_text(img, xy, s, path or F_NUM, size, fill, scale=scale, stroke=stroke, sfill=sfill)

def pin(d, x, y, col=C_RED):
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=col); d.ellipse([x - 5, y - 8, x + 1, y - 2], fill=(255, 255, 255))

def board(img, t, title="THEO'S FSA"):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([BX0 + 12, BY0 + 18, BX1 + 12, BY1 + 18], radius=26, fill=(160, 110, 40, 60))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=26, fill=WOOD)
    d.rounded_rectangle([BX0 + 8, BY0 + 8, BX1 - 8, BY1 - 8], radius=20, fill=WOOD2)
    d.rectangle([BX0 + 28, BY0 + 28, BX1 - 28, BY1 - 28], fill=CORK)
    for x, y, r in SPECK:
        d.ellipse([x - r, y - r, x + r, y + r], fill=CORK_D)
    img.alpha_composite(lay)
    # pinned title strip
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w = tw(title, F_NUM, 40) + 80
    d.rectangle([W / 2 - w / 2, BY0 + 46, W / 2 + w / 2, BY0 + 116], fill=PAPER)
    pin(d, W / 2 - w / 2 + 22, BY0 + 60); pin(d, W / 2 + w / 2 - 22, BY0 + 60)
    img.alpha_composite(lay)
    pop_text(img, (W / 2, BY0 + 82), title, F_NUM, 40, C_NAVY)

def note(img, cx, cy, w, h, col, lines, angle=-4, s=1.0, size=52, tcol=C_NAVY):
    if s < 0.05: return
    lay = Image.new("RGBA", (int(w + 60), int(h + 60)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([36, 38, 36 + w, 38 + h], fill=(90, 60, 30, 70))
    d.rectangle([30, 30, 30 + w, 30 + h], fill=col)
    pin(d, 30 + w / 2, 50)
    n = len(lines)
    for i, (txt, c) in enumerate(lines):
        y = 30 + h / 2 + 14 + (i - (n - 1) / 2) * size * 1.15
        d.text((30 + w / 2, y), txt, font=font(F_NUM, size), fill=(c or tcol), anchor="mm")
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    if abs(s - 1) > 0.01:
        lay = lay.resize((max(2, int(lay.width * s)), max(2, int(lay.height * s))))
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def jar(img, cx, cy, s, frac, amount, label, acol=C_GREEN, t=0.0):
    """glass jar, bottom at cy; frac = fill level 0..1"""
    if s < 0.05: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 230 * s, 300 * s
    x0, y0, x1, y1 = cx - w / 2, cy - h, cx + w / 2, cy
    d.rounded_rectangle([x0, y0, x1, y1], radius=40 * s, fill=(225, 245, 255, 150), outline=(255, 255, 255, 230), width=max(2, int(7 * s)))
    fy = y1 - (h - 24 * s) * frac
    if frac > 0.01 and fy < y1 - 12 * s - 30 * s:
        d.rounded_rectangle([x0 + 12 * s, fy, x1 - 12 * s, y1 - 12 * s], radius=26 * s, fill=(110, 200, 120, 255))
        for k in range(int(frac * 6) + 1):        # bill stripes
            yk = y1 - 30 * s - k * 40 * s
            if yk > fy + 10 * s:
                d.line([(x0 + 30 * s, yk), (x1 - 30 * s, yk - 8 * s)], fill=(70, 150, 85, 255), width=max(2, int(6 * s)))
    d.rounded_rectangle([x0 - 8 * s, y0 - 34 * s, x1 + 8 * s, y0 + 4 * s], radius=10 * s, fill=(240, 140, 60))
    d.line([(x0 + 30 * s, y0 + 30 * s), (x0 + 30 * s, y1 - 60 * s)], fill=(255, 255, 255, 170), width=max(2, int(10 * s)))
    img.alpha_composite(lay)
    # label sticker
    lw = max(tw(amount, F_NUM, 50 * s), tw(label, F_MED, 26 * s)) + 40 * s
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx - lw / 2, cy - h * 0.62 - 50 * s, cx + lw / 2, cy - h * 0.62 + 52 * s], radius=14 * s, fill=PAPER, outline=C_NAVY, width=max(2, int(4 * s)))
    pop_text(img, (cx, cy - h * 0.62 - 16 * s), label, F_MED, 26 * s, C_NAVY)
    pop_text(img, (cx, cy - h * 0.62 + 20 * s), amount, F_NUM, 50 * s, acol)

def stamp(img, cx, cy, s, text, col, angle=-12, back=None, size=120):
    if s < 0.03: return
    f = font(F_NUM, size * s); l, t, r, b = f.getbbox(text)
    w, h = r - l + 70 * s, b - t + 50 * s
    lay = Image.new("RGBA", (int(w + 40), int(h + 40)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=20 * s, fill=back + (255,) if back else None, outline=col + (255,), width=max(2, int(12 * s)))
    d.text((20 + w / 2, 20 + h / 2), text, font=f, fill=col + (255,), anchor="mm")
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def money(v): return f"${v:,.0f}"

def bd_hook(img, t):
    board(img, t)
    jar(img, 330, 800, 1.0, 0.75, "$2,000", "LEFT IN DEC", t=t)
    note(img, 740, 560, 380, 320, NOTE_Y, [("ROLLS", None), ("OVER", None), ("FOREVER?", C_RED)], angle=5, size=60)

def bd_no(img, t):
    board(img, t, title="HSA vs FSA")
    s0 = seg_start("no")
    k1 = ease_back((t - s0) / 0.35); k2 = ease_back((t - tok("no", 3) + 0.1) / 0.35)
    note(img, 300, 610, 380, 360, NOTE_B, [("HSA", C_NAVY), ("✓ ROLLS", C_GREEN), ("OVER", C_GREEN)], angle=-4, s=k1, size=58)
    note(img, 770, 610, 380, 360, NOTE_P, [("FSA", C_NAVY), ("USE IT", C_RED), ("OR LOSE IT", C_RED)], angle=4, s=k2, size=50)

def bd_carry(img, t):
    board(img, t, title="WHAT CARRIES OVER")
    s0 = seg_start("carry"); k = ease_out((t - tok("carry", 2) + 0.2) / 1.0)
    left = lerp(2000, 1320, k)
    jar(img, 300, 810, 1.0, lerp(0.75, 0.5, k), money(left), "2026", t=t)
    jar(img, 780, 810, 0.85, lerp(0.0, 0.26, k), money(lerp(0, 680, k)), "2027", t=t)
    if 0.02 < k < 0.98:   # coins flying along an arc
        d = ImageDraw.Draw(img)
        for i in range(5):
            u = (k * 3 + i * 0.2) % 1
            x = lerp(330, 760, u); y = 470 - math.sin(u * math.pi) * 110 + 20
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(255, 205, 60), outline=(200, 140, 20), width=4)
    if k > 0.9:
        stamp(img, 540, 600, 0.42 * ease_back((t - tok("carry", 2) - 0.8) / 0.3), "MAX $680", C_GREEN, angle=-6, back=PAPER)

def shredder(img, cx, cy, t, k):
    d = ImageDraw.Draw(img)
    # strips coming out the bottom
    n = 9
    for i in range(n):
        x = cx - 120 + i * 30
        ln = 20 + 70 * k * (0.7 + 0.3 * math.sin(i * 1.7))
        d.rectangle([x, cy + 40, x + 16, cy + 40 + ln], fill=(110, 200, 120))
    # bill going in
    if k < 1:
        by = cy - 80 + 80 * k
        d.rectangle([cx - 100, by - 60, cx + 100, by + 40], fill=(110, 200, 120), outline=(70, 150, 85), width=5)
        pop_text(img, (cx, by - 10), "$", F_NUM, 60, (40, 110, 60))
    d.rounded_rectangle([cx - 160, cy - 40, cx + 160, cy + 50], radius=18, fill=(70, 74, 96))
    d.rectangle([cx - 130, cy - 44, cx + 130, cy - 30], fill=(30, 30, 40))
    on = (t * 3) % 1 < 0.5
    d.ellipse([cx + 110, cy, cx + 134, cy + 24], fill=C_RED if on else (120, 40, 40))

def bd_lose(img, t):
    board(img, t, title="AFTER THE DEADLINE")
    s0 = seg_start("lose"); k = ease_out((t - s0 - 0.2) / 1.8)
    shredder(img, 330, 690, t, k)
    if t < tok("lose", 2) - 0.1:
        marker(img, (330, 480), money(lerp(1320, 0, k)), 64, C_RED, stroke=6, sfill=PAPER)
    # calendar page
    note(img, 780, 590, 300, 340, PAPER, [("PLAN", C_NAVY), ("DEADLINE", C_RED)], angle=4, size=44)
    d = ImageDraw.Draw(img)
    rk = ease_out((t - s0) / 0.8)
    d.arc([660, 600, 900, 720], 0, 360 * rk, fill=C_RED, width=8)
    if t > tok("lose", 2) - 0.1:
        stamp(img, 400, 500, 0.55 * ease_back((t - tok("lose", 2) + 0.1) / 0.3), "$1,320 GONE", C_RED, angle=-7, back=PAPER)

def bottle(img, x, y, s, ang):
    lay = Image.new("RGBA", (120, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([25, 40, 95, 190], radius=20, fill=(255, 150, 60))
    d.rectangle([45, 10, 75, 42], fill=(255, 255, 255))
    d.rectangle([25, 90, 95, 135], fill=(255, 240, 200))
    d.text((60, 112), "SPF", font=font(F_NUM, 22), fill=C_NAVY, anchor="mm")
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    if abs(s - 1) > 0.01: lay = lay.resize((max(2, int(lay.width * s)), max(2, int(lay.height * s))))
    img.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def bd_panic(img, t):
    board(img, t, title="THEO'S PLAN B")
    s0 = seg_start("panic")
    r = np.random.default_rng(3)
    n = int(clamp((t - s0) / 2.0) * 24)
    for i in range(24):
        bx = r.uniform(140, 940); land = r.uniform(520, 800); ang = r.uniform(-40, 40); delay = i * 0.08
        if i >= n: continue
        u = clamp((t - s0 - delay) / 0.45)
        y = lerp(340, land, ease_out(u))
        bottle(img, bx, y, 1.0, ang)
    marker(img, (W / 2, 540), "x100", 120, CORAL, stroke=8, sfill=PAPER, scale=ease_back((t - tok("panic", 1)) / 0.3))

def bar(img, x, y, wtot, parts, label):
    d = ImageDraw.Draw(img)
    pop_text(img, (x, y - 50), label, F_NUM, 36, C_NAVY, anchor_c=False)
    cx = x
    for w_, col, txt in parts:
        if w_ <= 1: continue
        d.rectangle([cx, y - 6, cx + w_, y + 70], fill=col)
        if txt: pop_text(img, (cx + w_ / 2, y + 32), txt, F_NUM, 34, WHITE)
        cx += w_

def bd_fix(img, t):
    board(img, t, title="NEXT YEAR")
    ImageDraw.Draw(img).rectangle([W / 2 - 410, 475, W / 2 + 410, 805], fill=PAPER)
    full = 700; sc = full / 3400
    bar(img, 190, 560, full, [(1400 * sc, C_GREEN, "SPENT $1,400"), (2000 * sc, C_RED, "UNUSED")], "2026: PUT IN $3,400")
    k = ease_out((t - tok("fix", 2) + 0.1) / 0.6)
    bar(img, 190, 720, full, [(1400 * sc * k, C_GREEN, "$1,400" if k > 0.6 else "")], "NEXT YEAR: PUT IN WHAT YOU SPEND")

def bd_punch(img, t):
    board(img, t, title="THEO'S NEW NAME")
    s0 = seg_start("punch")
    words = [("F", "ORFEIT", 2), ("S", "PENDING", 3), ("A", "CCOUNT", 4)]
    for i, (L, rest, ti) in enumerate(words):
        y = 440 + i * 130
        k = ease_back((t - s0 - 0.1 * i) / 0.3)
        note(img, 260, y + 30, 120, 110, [NOTE_Y, NOTE_P, NOTE_B][i], [(L, C_NAVY)], angle=(-5, 4, -3)[i], s=k, size=72)
        kk = ease_back((t - tok("punch", ti) + 0.05) / 0.25)
        marker(img, (370 + tw(rest, F_NUM, 84) / 2, y + 42), rest, 84, C_RED if i == 0 else C_NAVY, scale=kk, stroke=6, sfill=PAPER)

def bd_q(img, t):
    board(img, t, title="YOUR TURN")
    s0 = seg_start("q")
    marker(img, (W / 2, 450), "GOT AN FSA?", 80, C_NAVY, stroke=6, sfill=PAPER)
    d = ImageDraw.Draw(img)
    for i, (lab, col) in enumerate([("KNOW MY DEADLINE", C_GREEN), ("NO IDEA", CORAL)]):
        x = 300 + i * 480; y = 610
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        w_ = 210 if i == 0 else 170
        d.rounded_rectangle([x - w_ * k, y - 60 * k, x + w_ * k, y + 60 * k], radius=30 * k, fill=col)
        pop_text(img, (x, y), lab, F_NUM, (36 if i == 0 else 48) * k, WHITE)
    if t > tok("q", 3) - 0.1:
        marker(img, (W / 2, 750), "TELL US BELOW", 60, C_RED, scale=ease_back((t - tok("q", 3) + 0.1) / 0.3), stroke=6, sfill=PAPER)

BOARDS = {"hook": bd_hook, "no": bd_no, "carry": bd_carry, "lose": bd_lose, "panic": bd_panic, "fix": bd_fix,
          "punch": bd_punch, "q": bd_q, "loop": bd_hook}
# per-scene staging: (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "worried", "point_up", "smile"),
         "carry": ("idle", "smile", "marker", "smile"), "lose": ("facepalm", "worried", "point_up", "smile"),
         "panic": ("cheer", "smug", "facepalm", "facepalm"), "fix": ("idle", "smile", "marker", "smile"),
         "punch": ("shrug", "smug", "facepalm", "facepalm"), "q": ("idle", "smile", "shrug", "smile"),
         "loop": ("cheer", "smug", "idle", "worried")}

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
    lab1, lab2 = "THEO EXPLAINS #6", "FSA DEADLINES"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=C_NAVY)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=C_NAVY)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=C_NAVY, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (110, 80, 40)
    d.text((W / 2, 1530), "Illustration. IRS 2026: FSA limit $3,400; max carryover $680 if your plan allows.", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1568), "Plans differ (carryover, grace period or neither). Not financial advice.", font=font(F_MED, 26), fill=c, anchor="mm")

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
