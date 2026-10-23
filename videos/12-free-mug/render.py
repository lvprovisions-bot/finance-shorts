"""WHO WINS? #4: savings rates (the free mug). 1080x1920 @30fps. Navy->violet tiled vault backdrop, two interest taps."""
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
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(20, 10, 50, 70))
    img.alpha_composite(sh); img.alpha_composite(lay)
# ---------- background: navy -> deep violet, vault-door rings + faint tiles ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((14, 22, 70), np.float32); bot = np.array((52, 18, 82), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    tiles = (((xx % 120) < 3) | ((yy % 120) < 3)).astype(np.float32) * 10
    img += tiles[..., None]
    for cx0, cy0 in ((W / 2, 560),):
        r = np.sqrt((xx - cx0) ** 2 + (yy - cy0) ** 2)
        rings = ((np.abs(r - 430) < 6) | (np.abs(r - 470) < 3) | (np.abs(r - 330) < 2)).astype(np.float32)
        img += rings[..., None] * np.array((30, 34, 70), np.float32)
        img += (np.clip(1 - r / 640, 0, 1) ** 2)[..., None] * np.array((30, 40, 90), np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 105, 115)
LAV = (190, 186, 235); STEEL = (170, 180, 210); STEEL_D = (100, 110, 150)
def money(v): return "${:,.0f}".format(v)

# containers: Nora's tall glass (left), Theo's free mug (right)
NXC, TXC = 300, 780
CB = 840          # container bottom y
def tap(img, cx, flow, t, rate_txt, rate_col, rate_k):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx - 60, 262, cx + 60, 282], radius=8, fill=STEEL_D)
    d.rectangle([cx - 18, 270, cx + 18, 410], fill=STEEL_D)                 # pipe from a wall plate
    d.rounded_rectangle([cx - 70, 390, cx + 40, 440], radius=18, fill=STEEL, outline=STEEL_D, width=4)
    d.rounded_rectangle([cx + 10, 420, cx + 52, 485], radius=12, fill=STEEL, outline=STEEL_D, width=4)  # spout
    d.rounded_rectangle([cx - 56, 360, cx - 4, 386], radius=10, fill=(220, 70, 80))                   # handle
    # coins falling from the spout
    sx = cx + 31
    if flow > 0:
        n = 6 if flow > 0.5 else 1
        for i in range(n):
            ph = ((t * (1.4 if flow > 0.5 else 0.45)) + i / n) % 1.0
            y = 490 + ph * 240
            r = 17
            d.ellipse([sx - r, y - r, sx + r, y + r], fill=GOLD, outline=GOLD_D, width=4)
    if rate_k > 0.02:
        pop_text(img, (cx - 150 if cx < W / 2 else cx + 165, 420), rate_txt, F_NUM, 60, rate_col, scale=rate_k, stroke=8, sfill=(20, 14, 50))

def glass(img, fill, glow=0.0):
    cx = NXC + 31; x0, x1, y0 = cx - 110, cx + 110, 590
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if glow > 0.01:
        for r in range(6, 0, -1):
            d.rounded_rectangle([x0 - r * 7, y0 - r * 7, x1 + r * 7, CB + r * 7], radius=40 + r * 7, fill=GOLD + (int(14 * glow),))
    d.rounded_rectangle([x0, y0, x1, CB], radius=30, fill=(255, 255, 255, 38), outline=(225, 235, 255, 230), width=7)
    hf = (CB - y0 - 20) * clamp(fill)
    if hf > 4:
        d.rounded_rectangle([x0 + 10, CB - 10 - hf, x1 - 10, CB - 10], radius=22, fill=GOLD + (255,))
        for k in range(int(hf // 26)):
            yk = CB - 22 - k * 26
            d.line([x0 + 20, yk, x1 - 20, yk], fill=GOLD_D + (255,), width=3)
    d.rounded_rectangle([x0 + 20, y0 + 20, x0 + 34, y0 + 170], radius=7, fill=(255, 255, 255, 90))
    img.alpha_composite(lay)
    pop_text(img, (cx, y0 - 2 + (CB - y0) * 0.18), "HYSA", F_NUM, 44, WHITE, stroke=6, sfill=(30, 20, 70))

def mug(img, fill, price=None, price_k=0.0):
    cx = TXC + 31; x0, x1, y0 = cx - 120, cx + 120, 670
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([x1 - 40, y0 + 40, x1 + 70, y0 + 160], outline=(245, 245, 250, 255), width=22)   # handle
    d.rounded_rectangle([x0, y0, x1, CB], radius=36, fill=(245, 245, 250, 255), outline=(200, 200, 220, 255), width=5)
    d.ellipse([x0, y0 - 22, x1, y0 + 22], fill=(70, 50, 40, 255), outline=(200, 200, 220, 255), width=5)
    hf = (CB - y0 - 20) * clamp(fill)
    if hf > 3:
        d.rounded_rectangle([x0 + 10, CB - 10 - hf, x1 - 10, CB - 10], radius=20, fill=GOLD + (255,))
    img.alpha_composite(lay)
    pop_text(img, (cx, y0 + 70), "BIG BANK", F_NUM, 36, (60, 80, 170))
    pop_text(img, (cx, y0 + 112), "FREE MUG", F_MED, 26, (140, 140, 170))
    if price and price_k > 0.02:
        tag(img, cx - 10, y0 - 70, price, price_k)

def tag(img, x, y, s, k):
    d = ImageDraw.Draw(img)
    w = (tw(s, F_NUM, 58) / 2 + 40) * k; h = 50 * k
    d.polygon([(x - w - 30 * k, y), (x - w, y - h), (x + w, y - h), (x + w, y + h), (x - w, y + h)], fill=SOFTRED, outline=(150, 30, 40))
    d.ellipse([x - w - 8 * k, y - 8 * k, x - w + 8 * k, y + 8 * k], fill=(255, 255, 255))
    pop_text(img, (x + 8 * k, y), s, F_NUM, 58, WHITE, scale=k)

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 120), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(30, 16, 80))
    if sub:
        pop_text(img, (W / 2, 205), sub, F_NUM, 46, sub_col)

def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0

FN, FT = 0.85, 0.85 * 38 / 350
def rates_k(t):
    return (1.0 if t > tok("theo", 2) - 0.1 else 0.0), (1.0 if t > tok("nora", 4) - 0.1 else 0.0)

def base(img, t, nfill, tfill, nlab, tlab, nlab_col=MINT, tlab_col=SOFTRED, glow=0.0, price=None, price_k=0.0, rate_pop=None):
    rT, rN = rates_k(t)
    if rate_pop: rT, rN = rate_pop
    tap(img, NXC, 1.0, t, "3.5%", MINT, rN)
    tap(img, TXC, 0.2, t, "0.38%", SOFTRED, rT)
    glass(img, nfill, glow)
    mug(img, tfill, price, price_k)
    if nlab: pop_text(img, (NXC + 31, CB + 40), nlab, F_NUM, 50, nlab_col, stroke=6, sfill=(20, 14, 50))
    if tlab: pop_text(img, (TXC + 31, CB + 40), tlab, F_NUM, 50, tlab_col, stroke=6, sfill=(20, 14, 50))

def sc_hook(img, t):
    headline(img, t, "SAME $10,000 IN SAVINGS")
    if scene_at(t)["scene"] == "loop":
        base(img, t, FN, FT, "$350/yr", "$38/yr")
        return
    kN = clamp((t - tok("hook", 3)) / 1.6); kT = clamp((t - tok("hook", 5)) / 0.8)
    base(img, t, 0.06 + (FN - 0.06) * ease_out(kN), 0.03 + (FT - 0.03) * ease_out(kT),
         "$350/yr" if t > tok("hook", 4) - 0.1 else "$10,000", "$38/yr" if t > tok("hook", 6) - 0.1 else "$10,000",
         nlab_col=MINT if t > tok("hook", 4) - 0.1 else LAV, tlab_col=SOFTRED if t > tok("hook", 6) - 0.1 else LAV)

def sc_mug(img, t):
    headline(img, t, "THEO'S BANK GAVE HIM A FREE MUG", GOLD)
    base(img, t, FN, FT, "$350/yr", "$38/yr")
    k = kpop(tok("mug", 2), t)
    pop_text(img, (TXC + 31, 600), "FREE!", F_NUM, 70, YEL, scale=k, stroke=8, sfill=(30, 16, 80))

def sc_theo(img, t):
    headline(img, t, "THEO: NATIONAL AVERAGE RATE")
    base(img, t, FN, FT, "$350/yr", "$38/yr", rate_pop=(kpop(tok("theo", 2), t), 0.0))

def sc_nora(img, t):
    headline(img, t, "NORA: HIGH-YIELD SAVINGS" if t < tok("nora", 5) - 0.1 else "BOTH FDIC INSURED", MINT)
    base(img, t, FN, FT, "$350/yr", "$38/yr", rate_pop=(1.0, kpop(tok("nora", 4), t)))

def sc_ask(img, t):
    headline(img, t, "SO WHAT DID THE MUG COST?", GOLD)
    base(img, t, FN, FT, "$350/yr", "$38/yr")
    pop_text(img, (TXC + 31, 590), "?", F_NUM, 120, GOLD, scale=kpop(seg_start("ask"), t))

def sc_cost(img, t):
    five = t > tok("cost", 2) - 0.1
    headline(img, t, "5 YEARS: $1,877 vs $191" if five else "1 YEAR: $350 - $38 = $312", GOLD)
    if five:
        base(img, t, FN, FT * 1.0, "+$1,877", "+$191", glow=1.0, price="$1,685", price_k=kpop(tok("cost", 4), t))
    else:
        base(img, t, FN, FT, "$350/yr", "$38/yr", glow=1.0, price="$312", price_k=kpop(seg_start("cost"), t))

def sc_punch(img, t):
    headline(img, t, "MOST EXPENSIVE MUG EVER", SOFTRED)
    base(img, t, FN, FT, "+$1,877", "+$191", glow=1.0, price="$1,685", price_k=1.0)

def sc_q(img, t):
    headline(img, t, "")
    base(img, t, FN, FT, "", "")
    s0 = seg_start("q")
    d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.35)
    if k > 0.03:
        d.rounded_rectangle([W / 2 - 430 * k, 620 - 250 * k, W / 2 + 430 * k, 620 + 250 * k], radius=40 * k, fill=(255, 255, 255), outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 470), "WHAT DOES YOUR", F_NUM, 66, (30, 20, 80), scale=k)
        pop_text(img, (W / 2, 565), "SAVINGS PAY?", F_NUM, 100, (20, 150, 90), scale=k)
        pop_text(img, (W / 2, 670), "Look for the APY in your banking app", F_MED, 40, (60, 50, 110), scale=k)
        pop_text(img, (W / 2, 750), "NORA OR THEO? TELL US", F_NUM, 46, (210, 60, 80), scale=k)

SCENES = {"hook": sc_hook, "mug": sc_mug, "theo": sc_theo, "nora": sc_nora, "ask": sc_ask, "cost": sc_cost,
          "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "smile", "point_up", "smile"), "mug": ("cheer", "smug", "idle", "smile"),
         "theo": ("idle", "smile", "point_up", "smile"), "nora": ("shrug", "worried", "cheer", "smile"),
         "ask": ("shrug", "worried", "idle", "smile"), "cost": ("idle", "worried", "point_up", "smile"),
         "punch": ("facepalm", "worried", "shrug", "smile"), "q": ("idle", "smile", "point_up", "smile"),
         "loop": ("idle", "smile", "idle", "smile")}

CY = 1215
def crown(img, cx, cy, s, k):
    if k < 0.03: return
    d = ImageDraw.Draw(img)
    hy = cy - 115 * s; yb = hy - 64 * s * 1.5 - 8; w = 62 * s * k; h = 52 * s * k
    pts = [(cx - w, yb), (cx - w, yb - h), (cx - w / 2, yb - h * 0.55), (cx, yb - h * 1.15), (cx + w / 2, yb - h * 0.55), (cx + w, yb - h), (cx + w, yb)]
    d.polygon(pts, fill=GOLD, outline=GOLD_D)
    for px in (-w, 0, w):
        d.ellipse([cx + px - 8 * k, yb - h * (1.15 if px == 0 else 1.0) - 8 * k, cx + px + 8 * k, yb - h * (1.15 if px == 0 else 1.0) + 8 * k], fill=(255, 90, 120))

def draw_cast(img, t):
    s = scene_at(t); spk = s["spk"]
    tp, tm, np_, nm = STAGE[s["scene"]]
    in_seg = s["start"] - 0.05 <= t <= s["end"] + 0.05
    for who, cx, col, pose, mood in (("N", NXC + 31, NORA, np_, nm), ("T", TXC + 31, THEO, tp, tm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.0 if who == spk else 0.95
        cy = CY + (0 if who == spk else 12)
        person(img, cx, cy, sc, col, who, t, talk=talking, pose=pose, mood=mood)
        if who == "N" and s["scene"] in ("cost", "punch"):
            crown(img, cx, cy, sc, kpop(seg_start("cost"), t) if s["scene"] == "cost" else 1.0)
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

CAP_Y = 1450
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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=GOLD)
    c = (178, 176, 220)
    lines = ["Rates: FDIC national avg savings 0.38% (published 19 Oct 2026).",
             "Nora's 3.5% APY is an assumption: top online savings paid ~3-4%.",
             "$10,000 each, rates held constant, interest kept in, before tax.",
             "Rates change. Illustration only. Not financial advice."]
    for i, ln in enumerate(lines):
        d.text((W / 2, 1600 + i * 33), ln, font=font(F_MED, 26), fill=c, anchor="mm")

def frame(t):
    s = scene_at(t)
    img = BG.copy().convert("RGBA")
    SCENES[s["scene"]](img, t)
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
