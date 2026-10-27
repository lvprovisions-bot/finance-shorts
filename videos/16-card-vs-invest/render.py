"""WHO WINS? #6: pay off the card or invest the bonus? 1080x1920 @30fps. Royal navy -> violet halftone, two scoreboard panels, chomping credit card."""
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
# ---------- background: royal navy -> violet, halftone dots + top spotlight ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((12, 18, 66), np.float32); bot = np.array((74, 26, 118), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    # halftone dots, bigger towards the bottom
    cell = 36
    cx_ = (xx % cell) - cell / 2; cy_ = (yy % cell) - cell / 2
    rad = 2 + 7 * (yy / H)
    dots = ((cx_ ** 2 + cy_ ** 2) < rad ** 2).astype(np.float32) * 9
    img += dots[..., None]
    # spotlight cone from top centre
    r = np.sqrt(((xx - W / 2) / 1.6) ** 2 + ((yy - 120) / 1.0) ** 2)
    img += (np.clip(1 - r / 900, 0, 1) ** 2)[..., None] * np.array((40, 40, 90), np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); MINT = (60, 230, 150); SOFTRED = (255, 95, 110)
CARD_C = (40, 44, 60); CARD_HI = (90, 96, 130)
def money(v): return "${:,.0f}".format(v)

def kpop(t0, t):
    return ease_back((t - t0 + 0.1) / 0.35) if t > t0 - 0.1 else 0.0

# panels: Nora left, Theo right
PY0, PY1 = 285, 905
PN = (40, 525); PT = (555, 1040)
def panel(img, x0, x1, col, name, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x0, PY0, x1, PY1], radius=34, fill=(10, 12, 40, 175), outline=col + (230,), width=5)
    d.rounded_rectangle([x0, PY0, x1, PY0 + 74], radius=34, fill=col + (235,))
    d.rectangle([x0, PY0 + 40, x1, PY0 + 74], fill=col + (235,))
    img.alpha_composite(lay)
    pop_text(img, ((x0 + x1) / 2, PY0 + 38), name, F_NUM, 44, WHITE, stroke=4, sfill=(30, 20, 50))

def coin(d, x, y, r=18, a=255):
    d.ellipse([x - r, y - r, x + r, y + r], fill=GOLD + (a,), outline=GOLD_D + (a,), width=3)
    d.text((x, y), "$", font=font(F_NUM, int(r * 1.3)), fill=GOLD_D + (a,), anchor="mm")

def credit_card(img, cx, cy, s, t, chomp=0.0, apr_k=0.0, label="", stamp_k=0.0):
    """Credit card prop; chomp>0 opens a toothy mouth that eats coins."""
    w, h = 340 * s, 210 * s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10], radius=26 * s, fill=(0, 0, 20, 90))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=26 * s, fill=CARD_C, outline=CARD_HI, width=max(2, int(4 * s)))
    d.rectangle([cx - w / 2, cy - h / 2 + 30 * s, cx + w / 2, cy - h / 2 + 62 * s], fill=(15, 15, 25))
    d.rounded_rectangle([cx - w / 2 + 28 * s, cy - 10 * s, cx - w / 2 + 88 * s, cy + 35 * s], radius=8 * s, fill=(220, 190, 90))
    for i in range(4):
        d.text((cx - w / 2 + 40 * s + i * 72 * s, cy + 70 * s), "••••", font=font(F_MED, 22 * s), fill=(170, 175, 200), anchor="lm")
    if chomp > 0.01:
        op = (0.35 + 0.65 * abs(math.sin(t * 7))) * chomp
        mx, my, mw = cx + 55 * s, cy + 5 * s, 120 * s
        mh = 60 * s * op
        d.ellipse([mx - mw / 2, my - mh / 2 - 4, mx + mw / 2, my + mh / 2 + 4], fill=(110, 20, 40))
        for i in range(5):
            tx = mx - mw / 2 + 14 * s + i * (mw - 28 * s) / 4
            d.polygon([(tx - 9 * s, my - mh / 2), (tx + 9 * s, my - mh / 2), (tx, my - mh / 2 + 14 * s)], fill=WHITE)
            d.polygon([(tx - 9 * s, my + mh / 2), (tx + 9 * s, my + mh / 2), (tx, my + mh / 2 - 14 * s)], fill=WHITE)
        for ex in (-30, 30):   # angry eyes
            d.ellipse([mx + ex * s - 11 * s, cy - 55 * s, mx + ex * s + 11 * s, cy - 33 * s], fill=WHITE)
            d.ellipse([mx + ex * s - 5 * s, cy - 48 * s, mx + ex * s + 5 * s, cy - 38 * s], fill=(20, 20, 30))
            d.line([mx + ex * s - 16 * s, cy - 66 * s + (8 if ex < 0 else -8) * s * 0, mx + ex * s + 16 * s, cy - 58 * s if ex < 0 else cy - 66 * s],
                   fill=(20, 20, 30), width=max(2, int(5 * s)))
    img.alpha_composite(lay)
    if label:
        pop_text(img, (cx, cy - h / 2 - 34 * s), label, F_NUM, 34, (210, 215, 240), scale=s, stroke=4, sfill=(10, 10, 30))
    if apr_k > 0.02:
        pop_text(img, (cx - w / 2 + 92 * s, cy - h / 2 + 46 * s), "22% APR", F_NUM, 34, SOFTRED, scale=apr_k * s, stroke=6, sfill=(40, 0, 10))
    if stamp_k > 0.02:
        st = Image.new("RGBA", (440, 160), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([10, 10, 430, 150], radius=22, outline=MINT + (255,), width=10, fill=(10, 40, 30, 150))
        sd.text((220, 80), "PAID OFF", font=font(F_NUM, 78), fill=MINT + (255,), anchor="mm")
        sc = lerp(1.8, 1.0, ease_out(stamp_k)) * s * 0.86
        st = st.resize((max(2, int(440 * sc)), max(2, int(160 * sc)))).rotate(-14, expand=True)
        if stamp_k < 1:
            st.putalpha(st.getchannel("A").point(lambda v: int(v * clamp(stamp_k * 1.5))))
        img.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))

def mini_chart(img, x0, y0, x1, y1, k, t):
    """Theo's little stock line going up 7% over the year."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(8, 30, 34), outline=(40, 120, 100), width=3)
    n = 24; pts = []
    for i in range(int(n * clamp(k)) + 1):
        f = i / n
        v = f + 0.08 * math.sin(i * 1.7) * (1 - f * 0.4)
        pts.append((x0 + 24 + (x1 - x0 - 48) * f, y1 - 24 - (y1 - y0 - 60) * clamp(v)))
    if len(pts) > 1:
        d.line(pts, fill=MINT, width=7, joint="curve")
        ex, ey = pts[-1]
        d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=WHITE)

def coins_into_card(img, x0, y0, x1, y1, t, k):
    if k < 0.02: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(4):
        ph = (t * 1.1 + i / 4) % 1.0
        x = lerp(x0, x1, ease_out(ph)); y = lerp(y0, y1, ph) - math.sin(ph * math.pi) * 60
        coin(d, x, y, 16, int(255 * k * (1 - max(0, ph - 0.85) / 0.15)))
    img.alpha_composite(lay)

def counter(t, t0, t1, v):
    return v * ease_out((t - t0) / max(0.1, t1 - t0)) if t > t0 else 0.0

def boards(img, t, st):
    """st: dict of state for both panels."""
    panel(img, *PN, NORA, "NORA", t)
    panel(img, *PT, THEO, "THEO", t)
    nx = (PN[0] + PN[1]) / 2; tx = (PT[0] + PT[1]) / 2
    # common row: bonus chip
    for x in (nx, tx):
        pop_text(img, (x, PY0 + 112), "$10K BONUS", F_NUM, 40, GOLD, stroke=5, sfill=(30, 20, 10))
    # ---- Nora: card paid off
    credit_card(img, nx, 600, 1.0, t, label="$10K CARD DEBT", stamp_k=st.get("stamp", 1.0))
    pop_text(img, (nx, 748), "INTEREST: $0", F_NUM, 40, MINT, stroke=5, sfill=(10, 30, 20))
    if st.get("guar", 0) > 0.02:
        pop_text(img, (nx, 797), "GUARANTEED 22%", F_NUM, 40, GOLD, scale=st["guar"], stroke=5, sfill=(40, 20, 0))
    # ---- Theo: invested + card still there
    mini_chart(img, tx - 205, PY0 + 150, tx - 15, PY0 + 270, st.get("chart", 1.0), t)
    pop_text(img, (tx + 105, PY0 + 180), "STOCKS", F_MED, 30, (170, 220, 200))
    gain = st.get("gain", None)
    pop_text(img, (tx + 105, PY0 + 235), "+7%" if gain is None else "+" + money(gain), F_NUM, 50, MINT, scale=st.get("gain_k", 1.0), stroke=6, sfill=(10, 30, 20))
    credit_card(img, tx, 712, 0.9, t, chomp=st.get("chomp", 0.0), apr_k=st.get("apr", 0.0), label="STILL OWES $10K")
    coins_into_card(img, tx - 110, PY0 + 250, tx + 50, 712, t, st.get("chomp", 0.0) * st.get("coins", 0.0))
    intr = st.get("interest", None)
    if intr is not None:
        pop_text(img, (tx, 852), "INTEREST: -" + money(intr), F_NUM, 42, SOFTRED, stroke=5, sfill=(40, 0, 10))
    if st.get("month", None) is not None:
        pop_text(img, (W / 2, PY1 + 30), f"MONTH {st['month']} OF 12", F_NUM, 38, WHITE, stroke=5, sfill=(20, 10, 50))
    if st.get("net", 0) > 0.02:
        k = st["net"]
        pop_text(img, (nx, 852), "+$1,515 AHEAD", F_NUM, 44, MINT, scale=k, stroke=6, sfill=(10, 30, 20))

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 105), "WHO WINS?", F_NUM, 124, YEL, scale=pulse, stroke=10, sfill=(40, 10, 70))
    if sub:
        pop_text(img, (W / 2, 210), sub, F_NUM, 46, sub_col, stroke=5, sfill=(20, 10, 50))

FINAL = dict(stamp=1.0, chart=1.0, gain=700, chomp=1.0, apr=1.0, interest=2215, coins=0.0)

def sc_hook(img, t):
    headline(img, t, "SAME $10K BONUS. SAME $10K DEBT.")
    boards(img, t, dict(stamp=1.0, chart=1.0))

def sc_brag(img, t):
    headline(img, t, "THEO: \"STOCKS MAKE 7%!\"", (130, 220, 255))
    t0 = seg_start("brag")
    boards(img, t, dict(chart=ease_out((t - t0) / 1.5), gain_k=0.9 + 0.1 * math.sin(t * 8)))

def sc_apr(img, t):
    headline(img, t, "HIS CARD CHARGES 22% APR", SOFTRED)
    boards(img, t, dict(apr=kpop(tok("apr", 2), t), chomp=clamp((t - tok("apr", 2)) / 0.4)))

def sc_oh(img, t):
    headline(img, t, "HIS CARD CHARGES 22% APR", SOFTRED)
    boards(img, t, dict(apr=1.0, chomp=1.0))

def sc_year(img, t):
    headline(img, t, "ONE YEAR LATER...", GOLD)
    t0 = seg_start("year"); t1 = SEG["year"]["end"]
    m = max(1, min(12, int(1 + 12 * (t - t0) / (t1 - t0 - 0.3))))
    boards(img, t, dict(apr=1.0, chomp=1.0, coins=1.0, month=m,
                        gain=700 * m / 12, interest=2215 * m / 12))

def sc_result(img, t):
    headline(img, t, "THEO: -$1,515 vs NORA", SOFTRED)
    boards(img, t, dict(FINAL, net=kpop(tok("result", 1), t)))

def sc_why(img, t):
    headline(img, t, "PAYING IT OFF = A SURE 22%", MINT)
    boards(img, t, dict(FINAL, net=1.0, guar=kpop(tok("why", 3), t)))

def sc_punch(img, t):
    headline(img, t, "WHO REALLY GOT HIS BONUS?", GOLD)
    boards(img, t, dict(FINAL, net=1.0, coins=1.0, guar=1.0))
    k = kpop(tok("punch", 2), t)
    if k > 0.03:   # speech bubble from Theo's card
        d = ImageDraw.Draw(img)
        bx, by = 800, 520
        d.rounded_rectangle([bx - 190 * k, by - 55 * k, bx + 190 * k, by + 55 * k], radius=30 * k, fill=WHITE, outline=SOFTRED, width=max(2, int(6 * k)))
        d.polygon([(bx + 40 * k, by + 50 * k), (bx + 90 * k, by + 50 * k), (bx + 110 * k, by + 110 * k)], fill=WHITE)
        pop_text(img, (bx, by), "THANKS, THEO!", F_NUM, 46, (200, 40, 60), scale=k)

def sc_q(img, t):
    headline(img, t, "")
    boards(img, t, dict(FINAL, net=1.0, guar=1.0))
    s0 = seg_start("q")
    d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.35)
    if k > 0.03:
        d.rounded_rectangle([W / 2 - 440 * k, 600 - 250 * k, W / 2 + 440 * k, 600 + 250 * k], radius=40 * k, fill=WHITE, outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 445), "CARD FIRST", F_NUM, 96, (200, 50, 80), scale=k)
        pop_text(img, (W / 2, 545), "OR", F_NUM, 56, (20, 30, 70), scale=k)
        pop_text(img, (W / 2, 645), "INVEST FIRST?", F_NUM, 96, (20, 140, 90), scale=k)
        pop_text(img, (W / 2, 755), "NORA OR THEO? TELL US 👇".replace(" 👇", ""), F_NUM, 46, (20, 30, 70), scale=k)

SCENES = {"hook": sc_hook, "brag": sc_brag, "apr": sc_apr, "oh": sc_oh, "year": sc_year, "result": sc_result,
          "why": sc_why, "punch": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("cheer", "smug", "point_up", "smile"), "brag": ("cheer", "smug", "idle", "smile"),
         "apr": ("idle", "smile", "point_up", "smile"), "oh": ("shrug", "worried", "idle", "smile"),
         "year": ("idle", "worried", "marker", "smile"), "result": ("facepalm", "worried", "cheer", "smile"),
         "why": ("idle", "worried", "point_up", "smile"), "punch": ("facepalm", "worried", "shrug", "smile"),
         "q": ("idle", "smile", "point_up", "smile"), "loop": ("cheer", "smug", "idle", "smile")}
NXC, TXC = 282, 797
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
    for who, cx, col, pose, mood in (("N", NXC, NORA, np_, nm), ("T", TXC, THEO, tp, tm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.0 if who == spk else 0.95
        cy = CY + (0 if who == spk else 12)
        person(img, cx, cy, sc, col, who, t, talk=talking, pose=pose, mood=mood)
        if who == "N" and s["scene"] in ("result", "why", "punch", "q"):
            crown(img, cx, cy, sc, kpop(tok("result", 1), t) if s["scene"] == "result" else 1.0)
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
    c = (190, 196, 235)
    lines = ["Card APR 22.15%: Fed G.19, Q2 2026 (accounts assessed interest).",
             "Theo's 7% return is an assumption, not guaranteed. One year,",
             "Theo pays interest only on $10K; no taxes or fees.",
             "Illustration only. Not financial advice."]
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
