"""WHO WINS? #5: investment fees (the fee leak). 1080x1920 @30fps. Midnight-teal -> magenta night grid, line-chart race with a leaking gap."""
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
# ---------- background: midnight teal -> deep magenta, perspective floor grid + stars ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((8, 30, 52), np.float32); bot = np.array((64, 14, 70), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    # diagonal fine lines
    diag = (((xx + yy) % 90) < 2).astype(np.float32) * 7
    img += diag[..., None]
    # glow behind chart
    r = np.sqrt(((xx - W / 2) / 1.2) ** 2 + (yy - 650) ** 2)
    img += (np.clip(1 - r / 700, 0, 1) ** 2)[..., None] * np.array((20, 60, 70), np.float32)
    rng = np.random.default_rng(5)
    out = np.clip(img, 0, 255).astype(np.uint8)
    for _ in range(90):
        x, y = rng.integers(0, W), rng.integers(0, 1000)
        out[y:y + 3, x:x + 3] = (150, 200, 220)
    return Image.fromarray(out)
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 95, 110)
LAV = (190, 200, 235); GRID = (70, 100, 130)
def money(v): return "${:,.0f}".format(v)

NXC, TXC = 300, 780     # cast centres (Nora left, Theo right)
# ---- chart data: yearly balances ----
def series(r):
    m = (1 + r) ** (1 / 12) - 1; b = 0.0; out = [0.0]
    for y in range(40):
        for _ in range(12):
            b = (b + 500) * (1 + m)
        out.append(b)
    return out
SN, ST = series(0.0695), series(0.06)
CX0, CX1, CY0, CY1 = 150, 900, 340, 880    # plot box
YMAX = 1_300_000
def px(yr): return CX0 + (CX1 - CX0) * yr / 40
def py(v): return CY1 - (CY1 - CY0) * v / YMAX
def val(s, yr):
    i = int(min(yr, 39.999)); f = yr - i
    return s[i] + (s[min(i + 1, 40)] - s[i]) * f

def chart(img, t, prog, gap_k=0.0, end_k=0.0, boat_k=0.0, fee_k=(1.0, 1.0)):
    yr = 40 * clamp(prog)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([CX0 - 110, CY0 - 50, CX1 + 70, CY1 + 80], radius=36, fill=(6, 18, 40, 150), outline=(80, 140, 170, 160), width=3)
    for v in (0, 250_000, 500_000, 750_000, 1_000_000, 1_250_000):
        d.line([CX0, py(v), CX1, py(v)], fill=GRID + (110,), width=2)
        lab = "$0" if v == 0 else (f"${v // 1000}K" if v < 1_000_000 else f"${v / 1e6:.2f}M".replace(".00M", "M").replace("0M", "M"))
        d.text((CX0 - 14, py(v)), lab, font=font(F_MED, 24), fill=(150, 180, 210, 255), anchor="rm")
    for y_ in (0, 10, 20, 30, 40):
        d.text((px(y_), CY1 + 30), f"{y_}y", font=font(F_MED, 24), fill=(150, 180, 210, 255), anchor="mm")
    if yr > 0.05:
        n = max(2, int(yr * 6))
        ys = [yr * i / n for i in range(n + 1)]
        pn = [(px(y_), py(val(SN, y_))) for y_ in ys]
        pt = [(px(y_), py(val(ST, y_))) for y_ in ys]
        # leak: red shaded gap between lines
        a = int(150 * (0.35 + 0.65 * gap_k))
        d.polygon(pn + pt[::-1], fill=SOFTRED + (a,))
        d.line(pt, fill=(70, 196, 230, 255), width=10, joint="curve")
        d.line(pn, fill=(255, 140, 82, 255), width=12, joint="curve")
        for p0, col in ((pn[-1], NORA), (pt[-1], THEO)):
            d.ellipse([p0[0] - 14, p0[1] - 14, p0[0] + 14, p0[1] + 14], fill=col + (255,), outline=(255, 255, 255, 255), width=4)
        # dripping fee coins falling out of the gap
        if yr > 4:
            for i in range(5):
                ph = (t * 0.7 + i / 5) % 1.0
                yx = max(4, yr - 14) + min(14, yr - 4) * ((i * 0.37) % 1)
                x0 = px(yx); y0 = py((val(SN, yx) + val(ST, yx)) / 2)
                yd = y0 + ph * (CY1 - y0)
                al = int(200 * (1 - ph))
                d.ellipse([x0 - 9, yd - 9, x0 + 9, yd + 9], fill=GOLD + (al,), outline=GOLD_D + (al,), width=2)
    img.alpha_composite(lay)
    # year counter
    pop_text(img, (W / 2, CY0 - 8), f"YEAR {int(round(yr))}", F_NUM, 40, WHITE, stroke=5, sfill=(10, 20, 40))
    # fee badges next to legend
    pop_text(img, (CX0 + 10, CY0 + 70), "NORA 0.05%", F_NUM, 36, NORA, scale=fee_k[0], stroke=5, sfill=(10, 20, 40), anchor_c=False)
    pop_text(img, (CX0 + 10, CY0 + 120), "THEO 1%", F_NUM, 36, THEO, scale=fee_k[1], stroke=5, sfill=(10, 20, 40), anchor_c=False)
    if end_k > 0.02:
        pop_text(img, (px(40) - 30, py(SN[40]) - 52), "$1.23M", F_NUM, 54, MINT, scale=end_k, stroke=7, sfill=(10, 20, 40))
        pop_text(img, (px(40) - 30, py(ST[40]) + 58), "$958K", F_NUM, 50, (130, 220, 255), scale=end_k, stroke=7, sfill=(10, 20, 40))
    if gap_k > 0.02:
        gx, gy = px(19), py(880_000)
        bx = 300 * gap_k; by = 56 * gap_k
        dd = ImageDraw.Draw(img)
        dd.rounded_rectangle([gx - bx / 2 - 20, gy - by, gx + bx / 2 + 20, gy + by], radius=24 * gap_k, fill=SOFTRED, outline=(140, 20, 40), width=max(2, int(5 * gap_k)))
        dd.polygon([(gx + 40 * gap_k, gy + by - 2), (gx + 90 * gap_k, gy + by - 2), (px(36), py((SN[36] + ST[36]) / 2))], fill=SOFTRED)
        dd.polygon([(gx + 40 * gap_k, gy + by - 2), (gx + 90 * gap_k, gy + by - 2), (px(36), py((SN[36] + ST[36]) / 2))], outline=(140, 20, 40))
        pop_text(img, (gx, gy), "FEES: -$268K", F_NUM, 50, WHITE, scale=gap_k)
    if boat_k > 0.02:
        boat(img, px(31), py(170_000), boat_k, t)

def boat(img, x, y, k, t):
    d = ImageDraw.Draw(img)
    y = y + math.sin(t * 3) * 6
    s = k
    d.polygon([(x - 110 * s, y), (x + 120 * s, y), (x + 80 * s, y + 50 * s), (x - 80 * s, y + 50 * s)], fill=WHITE, outline=(40, 40, 70))
    d.rectangle([x - 50 * s, y - 40 * s, x + 50 * s, y], fill=(220, 230, 245), outline=(40, 40, 70))
    d.line([x, y - 40 * s, x, y - 120 * s], fill=(40, 40, 70), width=max(2, int(6 * s)))
    d.polygon([(x, y - 120 * s), (x + 70 * s, y - 50 * s), (x, y - 50 * s)], fill=GOLD)
    pop_text(img, (x, y + 25 * s), "FEE$", F_NUM, 30, (200, 40, 60), scale=s)

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 115), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(40, 10, 60))
    if sub:
        pop_text(img, (W / 2, 220), sub, F_NUM, 48, sub_col, stroke=5, sfill=(20, 10, 40))

def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0

def sc_hook(img, t):
    headline(img, t, "SAME $500/MONTH FOR 40 YEARS")
    if scene_at(t)["scene"] == "loop":
        chart(img, t, 1.0, gap_k=1.0, end_k=1.0); return
    chart(img, t, 1.0, gap_k=1.0, end_k=0.0)

def sc_tiny(img, t):
    headline(img, t, "THEO: \"1% IS NOTHING!\"", (130, 220, 255))
    chart(img, t, 1.0, gap_k=1.0)

def sc_fees(img, t):
    headline(img, t, "YEARLY FUND FEES", GOLD)
    chart(img, t, 0.0, fee_k=(kpop(tok("fees", 2), t), kpop(tok("fees", 4), t)))

def sc_time(img, t):
    headline(img, t, "SAME 7% RETURN BEFORE FEES", MINT)
    t0 = seg_start("time"); t1 = SEG["ask"]["end"]
    chart(img, t, ease_out((t - t0) / (t1 - t0)) if t > t0 else 0.0)

def sc_ask(img, t):
    headline(img, t, "SO WHO ENDS UP RICHER?", GOLD)
    sc_time_chart = ease_out((t - seg_start("time")) / (SEG["ask"]["end"] - seg_start("time")))
    chart(img, t, sc_time_chart)

def sc_result(img, t):
    two = t > tok("result", 2) - 0.1
    headline(img, t, "NORA $1.23M vs THEO $958K" if two else "NORA: $1.23 MILLION", MINT)
    chart(img, t, 1.0, end_k=kpop(tok("result", 1), t), gap_k=kpop(tok("result", 3), t))

def sc_punch(img, t):
    headline(img, t, "THE GAP > ALL $240K HE PUT IN", SOFTRED)
    chart(img, t, 1.0, end_k=1.0, gap_k=1.0, boat_k=kpop(tok("punch", 2), t))

def sc_q(img, t):
    headline(img, t, "")
    chart(img, t, 1.0, end_k=1.0, gap_k=1.0)
    s0 = seg_start("q")
    d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.35)
    if k > 0.03:
        d.rounded_rectangle([W / 2 - 430 * k, 640 - 250 * k, W / 2 + 430 * k, 640 + 250 * k], radius=40 * k, fill=(255, 255, 255), outline=MINT, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 490), "WHAT'S YOUR", F_NUM, 66, (20, 30, 70), scale=k)
        pop_text(img, (W / 2, 590), "FUND'S FEE?", F_NUM, 100, (200, 50, 80), scale=k)
        pop_text(img, (W / 2, 695), "Look for \"expense ratio\" in your 401(k)", F_MED, 36, (60, 60, 110), scale=k)
        pop_text(img, (W / 2, 775), "NORA OR THEO? TELL US", F_NUM, 46, (20, 140, 90), scale=k)

SCENES = {"hook": sc_hook, "tiny": sc_tiny, "fees": sc_fees, "time": sc_time, "ask": sc_ask, "result": sc_result,
          "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "smile", "point_up", "smile"), "tiny": ("cheer", "smug", "idle", "smile"),
         "fees": ("shrug", "smile", "marker", "smile"), "time": ("idle", "smile", "point_up", "smile"),
         "ask": ("shrug", "worried", "idle", "smile"), "result": ("idle", "worried", "cheer", "smile"),
         "punch": ("facepalm", "worried", "shrug", "smile"), "q": ("idle", "smile", "point_up", "smile"),
         "loop": ("idle", "smile", "idle", "smile")}

CY = 1200
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
        if who == "N" and s["scene"] in ("result", "punch"):
            crown(img, cx, cy, sc, kpop(tok("result", 3), t) if s["scene"] == "result" else 1.0)
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
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=MINT)
    c = (180, 196, 225)
    lines = ["Index equity funds averaged a 0.05% fee in 2025 (ICI, Mar 2026).",
             "Theo's 1% fee is an assumption. $500/month each for 40 years,",
             "7%/yr before fees, held constant, no taxes or inflation.",
             "Returns aren't guaranteed. Illustration only. Not financial advice."]
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
