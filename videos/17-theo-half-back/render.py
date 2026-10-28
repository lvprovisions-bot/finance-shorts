"""THEO EXPLAINS #5: -50% then +50%. 1080x1920 @30fps. Pastel lavender + dot grid, dark trading-screen monitor with line chart + Theo roller-coaster cart, Theo left / Nora right, IOU note."""
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



# ---------- palette (episode 5: pastel lavender + dot grid, dark trading-screen monitor with line chart) ----------
SCR = (22, 24, 44); SCR2 = (34, 38, 66); GRID = (52, 58, 96); BEZEL = (60, 52, 110)
LED_G = (60, 235, 140); LED_R = (255, 84, 104); LED_Y = (255, 222, 90); LED_W = (236, 238, 255); LED_C = (110, 200, 255)
M_NAVY = (52, 40, 120); M_ORG = (240, 130, 40); M_PURP = (130, 90, 230)

yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((226, 214, 255), np.float32); bot = np.array((250, 230, 246), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    # soft diagonal bands
    band = (np.sin((xx + yy) / 95.0) > 0.6)[..., None]
    img = np.where(band, img * 0.97 + 255 * 0.03, img)
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    for y in range(30, H, 60):
        for x in range(30 + (30 if (y // 60) % 2 else 0), W, 60):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(205, 190, 245))
    return out
BG = make_bg()

def marker(img, xy, s, size, fill, scale=1.0, path=None):
    pop_text(img, xy, s, path or F_NUM, size, fill, scale=scale)

# ---------- trading-screen monitor ----------
BX0, BY0, BX1, BY1 = 60, 290, 1020, 830
PX0, PY0, PX1, PY1 = 200, 420, 960, 780      # plot area
VMAX = 16000
def vy(v): return PY1 - (PY1 - PY0) * v / VMAX
def board(img, t, title="THEO'S PORTFOLIO", value=None, vcol=LED_W):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([BX0 + 12, BY0 + 16, BX1 + 12, BY1 + 16], radius=34, fill=(90, 60, 160, 70))
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=34, fill=BEZEL)
    d.rounded_rectangle([BX0 + 22, BY0 + 22, BX1 - 22, BY1 - 22], radius=18, fill=SCR)
    d.rectangle([BX0 + 22, BY0 + 22, BX1 - 22, BY0 + 100], fill=SCR2)
    d.rounded_rectangle([BX0 + 22, BY0 + 22, BX1 - 22, BY0 + 60], radius=18, fill=SCR2)
    # stand
    d.polygon([(W / 2 - 60, BY1), (W / 2 + 60, BY1), (W / 2 + 90, BY1 + 40), (W / 2 - 90, BY1 + 40)], fill=BEZEL)
    # scanlines
    for y in range(BY0 + 104, BY1 - 24, 6):
        d.line([(BX0 + 24, y), (BX1 - 24, y)], fill=(255, 255, 255, 6))
    # live dot
    on = (t * 2) % 1 < 0.6
    d.ellipse([BX0 + 50, BY0 + 50, BX0 + 72, BY0 + 72], fill=LED_R if on else (110, 40, 60))
    img.alpha_composite(lay)
    pop_text(img, (BX0 + 90, BY0 + 61), title, F_NUM, 36, LED_C, anchor_c=False)
    if value is not None:
        f = font(F_NUM, 46); l, tt, r, b = f.getbbox(value)
        pop_text(img, (BX1 - 60 - (r - l) / 2, BY0 + 61), value, F_NUM, 46, vcol)

def grid(img, ref=None):
    d = ImageDraw.Draw(img)
    for v in range(0, VMAX + 1, 5000):
        y = vy(v)
        d.line([(PX0, y), (PX1, y)], fill=GRID, width=2)
        pop_text(img, (PX0 - 62, y), f"${v // 1000}K", F_MED, 28, (150, 156, 200))
    if ref is not None:
        y = vy(ref)
        for x in range(PX0, PX1, 34):
            d.line([(x, y), (x + 18, y)], fill=LED_Y, width=5)
        pop_text(img, (PX0 - 62, y + 28), "START", F_NUM, 22, LED_Y)

def cart(img, x, y, ang):
    lay = Image.new("RGBA", (160, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 40, 140, 100], radius=16, fill=THEO)
    d.ellipse([60, 2, 100, 42], fill=SKIN2); d.chord([58, 0, 102, 30], 180, 360, fill=HAIR_T)
    d.ellipse([30, 92, 58, 120], fill=(230, 230, 240)); d.ellipse([102, 92, 130, 120], fill=(230, 230, 240))
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2 - 48)))

def chart(img, vals, p, show_cart=True, labels=True):
    """vals: list of values at evenly spaced x; p in [0, len-1] = how far drawn."""
    d = ImageDraw.Draw(img)
    n = len(vals); xs = [PX0 + 40 + i * (PX1 - PX0 - 80) / (n - 1) for i in range(n)]
    hx, hy = xs[0], vy(vals[0]); ang = 0
    for i in range(n - 1):
        k = clamp(p - i)
        if k <= 0: break
        x0, y0 = xs[i], vy(vals[i]); x1, y1 = lerp(x0, xs[i + 1], k), lerp(y0, vy(vals[i + 1]), k)
        col = LED_R if vals[i + 1] < vals[i] else LED_G
        d.line([(x0, y0), (x1, y1)], fill=col + (90,), width=26)
        d.line([(x0, y0), (x1, y1)], fill=col, width=12)
        hx, hy = x1, y1; ang = -math.degrees(math.atan2(vy(vals[i + 1]) - y0, xs[i + 1] - x0))
    for i in range(n):
        if p >= i - 0.02:
            d.ellipse([xs[i] - 14, vy(vals[i]) - 14, xs[i] + 14, vy(vals[i]) + 14], fill=LED_W)
    if show_cart:
        cart(img, hx, hy, ang)
    return xs

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
    board(img, t, value="$10,000?", vcol=LED_Y)
    marker(img, (W / 2 - 268, 480), "-50%", 112, LED_R)
    marker(img, (W / 2 + 268, 480), "+50%", 112, LED_G)
    marker(img, (W / 2, 485), "THEN", 46, LED_W)
    marker(img, (W / 2, 660), "= BACK TO EVEN?", 92, LED_Y)

def bd_no(img, t):
    bd_hook(img, t)
    ts = tok("no", 1)
    if t > ts - 0.1:
        stamp(img, W / 2, 570, 0.62 * ease_back((t - ts + 0.1) / 0.3), "CHECK THE MATH", LED_R, angle=-8, back=(255, 255, 255))

VALS = [10000, 5000, 7500]
def bd_drop(img, t):
    s0 = seg_start("drop"); k = ease_out((t - s0 - 0.1) / 1.6)
    v = lerp(10000, 5000, k)
    board(img, t, value=money(v), vcol=LED_R if k > 0.02 else LED_W)
    grid(img, ref=10000)
    xs = chart(img, VALS, k)
    if k > 0.95:
        marker(img, (xs[1] + 20, vy(5000) + 60), "-50%", 56, LED_R)

def bd_up(img, t):
    s0 = seg_start("up"); k = ease_out((t - s0 - 0.1) / 1.6)
    v = lerp(5000, 7500, k)
    board(img, t, value=money(v), vcol=LED_G)
    grid(img, ref=10000)
    xs = chart(img, VALS, 1 + k)
    marker(img, (xs[1] + 20, vy(5000) + 60), "-50%", 56, LED_R)
    if t > tok("up", 3) - 0.1:
        kk = ease_back((t - tok("up", 3) + 0.1) / 0.3)
        marker(img, (xs[2] - 90, vy(7500) + 85), "+$2,500", 56, LED_G, scale=kk)

def bd_total(img, t):
    board(img, t, value="$7,500", vcol=LED_Y)
    grid(img, ref=10000)
    xs = chart(img, VALS, 2, show_cart=False)
    d = ImageDraw.Draw(img)
    x = xs[2] + 40
    k = ease_out((t - seg_start("total")) / 0.5)
    y0, y1 = vy(7500), lerp(vy(7500), vy(10000), k)
    d.line([(x, y0), (x, y1)], fill=LED_Y, width=8); d.line([(x - 18, y1), (x + 18, y1)], fill=LED_Y, width=8)
    d.line([(x - 18, y0), (x + 18, y0)], fill=LED_Y, width=8)
    if k > 0.9:
        marker(img, (xs[2] - 130, vy(5000) + 45), "-$2,500", 52, LED_R)
    tn = tok("total", 3)
    if t > tn - 0.1:
        stamp(img, 560, 470, 0.5 * ease_back((t - tn + 0.1) / 0.3), "NEEDED +100%", M_PURP, angle=-6, back=(255, 255, 255))

VALS2 = [10000, 15000, 7500]
def bd_flip(img, t):
    board(img, t, title="THEO'S PLAN B", value="$10,000")
    s0 = seg_start("flip")
    marker(img, (W / 2, 520), "UP FIRST?", 120, LED_G, scale=ease_back((t - s0) / 0.3))
    k = (t * 1.5) % 1
    d = ImageDraw.Draw(img)
    y = 720 - 40 * k
    d.polygon([(W / 2, y - 60), (W / 2 - 50, y), (W / 2 + 50, y)], fill=LED_G)
    d.rectangle([W / 2 - 18, y, W / 2 + 18, y + 40], fill=LED_G)

def bd_flip2(img, t):
    s0 = seg_start("flip2"); tk1 = tok("flip2", 1)
    if t < tk1:
        k = ease_out((t - s0) / max(0.3, tk1 - s0)); v = lerp(10000, 15000, k); p = k
    else:
        k = ease_out((t - tk1) / 1.3); v = lerp(15000, 7500, k); p = 1 + k
    board(img, t, title="THEO'S PLAN B", value=money(v), vcol=LED_G if t < tk1 else LED_R)
    grid(img, ref=10000)
    xs = chart(img, VALS2, p)
    marker(img, (xs[1] - 10, vy(15000) - 60 + 120), "+50%", 50, LED_G) if p > 0.97 else None
    if p > 1.97:
        marker(img, (xs[2] - 20, vy(7500) + 64), "-50%", 50, LED_R)
    ts = tok("flip2", 3)
    if t > ts - 0.1:
        stamp(img, 360, 715, 0.5 * ease_back((t - ts + 0.1) / 0.3), "STILL $7,500", LED_R, angle=-7, back=(255, 255, 255))

def iou(img, cx, cy, s, t):
    if s < 0.05: return
    lay = Image.new("RGBA", (700, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 680, 400], radius=20, fill=(255, 250, 225), outline=(220, 200, 140), width=6)
    for k in range(5):
        d.line([(60, 170 + k * 48), (640, 170 + k * 48)], fill=(220, 225, 240), width=3)
    d.text((350, 95), "I.O.U.", font=font(F_NUM, 96), fill=M_NAVY, anchor="mm")
    d.text((350, 215), "$2,500", font=font(F_NUM, 110), fill=(30, 160, 90), anchor="mm")
    d.text((350, 330), "to Theo · signed: MATH", font=font(F_HAND, 40), fill=(200, 70, 120), anchor="mm")
    lay = lay.rotate(4 + math.sin(t * 3) * 2, expand=True, resample=Image.BICUBIC)
    if s != 1: lay = lay.resize((max(2, int(lay.width * s)), max(2, int(lay.height * s))))
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def bd_punch(img, t):
    board(img, t, title="THEO'S CLAIM", value="$7,500", vcol=LED_R)
    iou(img, W / 2, 580, 0.95 * ease_back((t - seg_start("punch")) / 0.35), t)

def bd_q(img, t):
    s0 = seg_start("q")
    board(img, t, title="YOUR VOTE")
    marker(img, (W / 2, 440), "-50% THEN +50% = ?", 64, LED_W)
    d = ImageDraw.Draw(img)
    for i, (lab, col) in enumerate([("EVEN", LED_C), ("-25%", LED_R)]):
        x = 330 + i * 420; y = 590
        k = ease_back((t - s0 - 0.15 * i) / 0.35)
        if k < 0.05: continue
        d.rounded_rectangle([x - 170 * k, y - 75 * k, x + 170 * k, y + 75 * k], radius=36 * k, fill=col)
        pop_text(img, (x, y), lab, F_NUM, 70 * k, SCR)
    if t > tok("q", 2) - 0.1:
        marker(img, (W / 2, 735), "TELL US BELOW", 56, LED_Y, scale=ease_back((t - tok("q", 2) + 0.1) / 0.3))

BOARDS = {"hook": bd_hook, "no": bd_no, "drop": bd_drop, "up": bd_up, "total": bd_total, "flip": bd_flip,
          "flip2": bd_flip2, "punch": bd_punch, "q": bd_q, "loop": bd_hook}
# per-scene staging: (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("cheer", "smug", "idle", "worried"), "no": ("idle", "smile", "point_up", "smile"),
         "drop": ("idle", "worried", "marker", "smile"), "up": ("idle", "smile", "point_up", "smile"),
         "total": ("shrug", "worried", "marker", "smile"), "flip": ("point_up", "smug", "idle", "worried"),
         "flip2": ("idle", "worried", "point_up", "smile"), "punch": ("shrug", "smug", "facepalm", "facepalm"),
         "q": ("idle", "smile", "shrug", "smile"), "loop": ("cheer", "smug", "idle", "worried")}

TX, NX, CY = 290, 790, 1060

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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=M_PURP)
    lab1, lab2 = "THEO EXPLAINS #5", "-50% THEN +50%"
    f1 = font(F_NUM, 50)
    w1 = tw(lab1, F_NUM, 50) + 60; w2 = tw(lab2, F_NUM, 50) + 60
    total = w1 + w2; x0 = W / 2 - total / 2
    d.rounded_rectangle([x0, 160, x0 + w1 + 30, 250], radius=45, fill=THEO)
    d.rounded_rectangle([x0 + w1, 160, x0 + total, 250], radius=45, fill=M_NAVY)
    d.rectangle([x0 + w1, 160, x0 + w1 + 30, 250], fill=M_NAVY)
    d.text((x0 + w1 / 2, 205), lab1, font=f1, fill=INK, anchor="mm")
    d.text((x0 + w1 + w2 / 2, 205), lab2, font=f1, fill=YEL, anchor="mm")
    c = (70, 50, 120)
    d.text((W / 2, 1530), "Illustration: hypothetical $10,000; ignores fees, dividends and taxes.", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1568), "Not financial advice.", font=font(F_MED, 26), fill=c, anchor="mm")

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
