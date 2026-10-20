"""WHO WINS? #3: the 401(k) match. 1080x1920 @30fps. Indigo->midnight gradient, two savings jars, Nora & Theo."""
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
    ImageDraw.Draw(sh).ellipse([cx - 120 * s, cy + 140 * s - bob, cx + 120 * s, cy + 170 * s - bob], fill=(60, 40, 120, 50))
    img.alpha_composite(sh); img.alpha_composite(lay)
# ---------- background: deep indigo -> midnight blue gradient, soft light beams + specks ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg():
    top = np.array((46, 24, 96), np.float32); bot = np.array((10, 16, 48), np.float32)
    f = (yy / H)[..., None]
    img = top * (1 - f) + bot * f
    beams = (np.sin((xx * 0.6 + yy) / 140.0) > 0.82).astype(np.float32) * (1 - yy / H) * 9
    img += beams[..., None]
    d = np.sqrt((xx - W / 2) ** 2 + ((yy - 560) * 1.1) ** 2) / 700
    img += (np.clip(1 - d, 0, 1) ** 2)[..., None] * np.array((40, 30, 70), np.float32)
    rng = np.random.default_rng(3)
    for _ in range(140):
        x, y = rng.integers(0, W), rng.integers(0, 1250)
        img[y:y + 3, x:x + 3] += 70 * rng.random()
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BG = make_bg()

PANEL = (255, 255, 255)
GOLD = (255, 196, 46); GOLD_D = (200, 140, 10); JAR_T = (60, 150, 255); JAR_N = (255, 140, 82)
LAV = (190, 180, 235)
def money(v): return "${:,.0f}".format(v)
FAC = lambda y: ((1.07 ** y - 1) / 0.07) if y > 0 else 0.0
THEO_END, NORA_END = 3600 * FAC(25), 5400 * FAC(25)

# ---------- jars ----------
JY0, JY1, JW = 385, 720, 250
JX = {"T": 300, "N": 780}
def jar(img, who, fill_main, fill_gold, label_val, label_sub="", glow=0.0, t=0.0, sub_col=None, sub_k=1.0):
    cx = JX[who]; x0, x1 = cx - JW / 2, cx + JW / 2
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if glow > 0.01:
        for r in range(6, 0, -1):
            d.rounded_rectangle([x0 - r * 7, JY0 - r * 7, x1 + r * 7, JY1 + r * 7], radius=50 + r * 7, fill=GOLD + (int(14 * glow),))
    d.rounded_rectangle([x0, JY0, x1, JY1], radius=46, fill=(255, 255, 255, 40), outline=(230, 230, 255, 230), width=8)
    inner = JY1 - JY0 - 24
    yb = JY1 - 12
    hm = inner * clamp(fill_main); hg = inner * clamp(fill_gold)
    col = JAR_T if who == "T" else JAR_N
    if hm > 2:
        d.rounded_rectangle([x0 + 12, yb - hm, x1 - 12, yb], radius=34, fill=col + (255,))
    if hg > 2:
        d.rounded_rectangle([x0 + 12, yb - hm - hg, x1 - 12, yb - hm + (30 if hm > 2 else 0)], radius=34, fill=GOLD + (255,))
        if hm > 2:
            d.rectangle([x0 + 12, yb - hm - 2, x1 - 12, yb - hm + 30], fill=GOLD + (255,))
            d.rectangle([x0 + 12, yb - hm, x1 - 12, yb - hm + 30], fill=col + (255,))
    # lid
    d.rounded_rectangle([x0 + 20, JY0 - 46, x1 - 20, JY0 + 6], radius=16, fill=(235, 225, 255, 255), outline=(150, 140, 200, 255), width=5)
    # shine
    d.rounded_rectangle([x0 + 28, JY0 + 30, x0 + 46, JY0 + 200], radius=9, fill=(255, 255, 255, 90))
    img.alpha_composite(lay)
    # name pill on the lid
    nm = "THEO" if who == "T" else "NORA"
    pop_text(img, (cx, JY0 - 20), nm, F_NUM, 40, (60, 40, 110))
    if label_val:
        pop_text(img, (cx, JY1 - 120 if fill_main + fill_gold < 0.45 else (JY0 + JY1) / 2 - 10), label_val, F_NUM, 46 if len(label_val) > 5 else 66, WHITE, stroke=8, sfill=(30, 20, 60))
    if label_sub:
        pop_text(img, (cx, JY1 + 46), label_sub, F_NUM if sub_col else F_MED, 42 if sub_col else 38, sub_col or LAV, scale=sub_k)

def coin(img, x, y, r=34):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r, x + r, y + r], fill=GOLD, outline=GOLD_D, width=5)
    d.text((x, y), "$", font=font(F_NUM, int(r * 1.2)), fill=GOLD_D, anchor="mm")

def headline(img, t, sub, sub_col=WHITE):
    pulse = 1.0 + 0.03 * math.sin(t * 5)
    pop_text(img, (W / 2, 185), "WHO WINS?", F_NUM, 128, YEL, scale=pulse, stroke=10, sfill=(40, 20, 90))
    if sub:
        pop_text(img, (W / 2, 288), sub, F_NUM, 50, sub_col)

def gap_bracket(img, t, k):
    if k < 0.03: return
    d = ImageDraw.Draw(img)
    yT = JY1 - 12 - (JY1 - JY0 - 24) * 0.6
    yN = JY1 - 12 - (JY1 - JY0 - 24) * 0.9
    x = W / 2 + 10
    d.line([(x, yT), (x, yT - (yT - yN) * k)], fill=GOLD, width=8)
    d.line([(x - 22, yT), (x + 22, yT)], fill=GOLD, width=8)
    if k > 0.95:
        d.line([(x - 22, yN), (x + 22, yN)], fill=GOLD, width=8)
        pop_text(img, (x, yT + 50), "+$114K", F_NUM, 44, GOLD)

def sc_hook(img, t, sub="SAME $300 A MONTH"):
    if scene_at(t)["scene"] == "hook2" and t > tok("hook2", 2) - 0.1:
        headline(img, t, "ONE ENDS UP $114,000 RICHER?", GOLD)
    else:
        headline(img, t, sub)
    jar(img, "T", 0.12, 0, "$300", "a month", t=t)
    jar(img, "N", 0.12, 0, "$300", "a month", t=t)
    if t >= seg_start("hook2") - 0.05 and scene_at(t)["scene"] in ("hook2", "how"):
        k = ease_back((t - tok("hook2", 2) + 0.1) / 0.35) if t > tok("hook2", 2) - 0.1 else 0
        pop_text(img, (W / 2, 555), "?", F_NUM, 150, GOLD, scale=k)

def sc_how(img, t):
    sc_hook(img, t, "SAME SALARY. SAME SAVINGS.")

def sc_nora(img, t):
    headline(img, t, "NORA: 401(K) + BOSS MATCH")
    tm = tok("nora", 3)
    g = 0.06 * ease_out((t - tm) / 0.8) if t > tm else 0
    jar(img, "T", 0.12, 0, "$300", "a month", t=t)
    fr = t > tok("nora", 6) - 0.1
    jar(img, "N", 0.12, g, "$450" if t > tok("nora", 4) else "$300", "+$150 FREE" if fr else "a month", glow=1.0 if fr else 0, t=t,
        sub_col=GOLD if fr else None, sub_k=ease_back((t - tok("nora", 6) + 0.1) / 0.35) if fr else 1.0)
    if t > tm - 0.3:
        for i in range(3):
            ph = ((t - tm) * 1.1 + i / 3) % 1.0
            coin(img, JX["N"] + (i - 1) * 60, 340 + ph * 230, 30)
    if t > tok("nora", 4) - 0.1:
        k = ease_back((t - tok("nora", 4) + 0.1) / 0.35)
        pop_text(img, (W / 2 + 10, 640), "+50%", F_NUM, 64, GOLD, scale=k)

def sc_theo(img, t):
    headline(img, t, "THEO: HIS OWN ACCOUNT")
    nm = t > tok("theo", 3) - 0.1
    jar(img, "T", 0.12, 0, "$300", "NO MATCH" if nm else "a month", t=t, sub_col=(255, 110, 110) if nm else None,
        sub_k=ease_back((t - tok("theo", 3) + 0.1) / 0.35) if nm else 1.0)
    jar(img, "N", 0.12, 0.06, "$450", "+$150 FREE", t=t, sub_col=GOLD)

def grow_years(t):
    b = tok("grow", 2)
    return 25 * ease_out((t - seg_start("grow")) / (b - seg_start("grow")))

def sc_grow(img, t, final=False):
    yrs = 25 if final else grow_years(t)
    vT, vN = 3600 * FAC(yrs), 5400 * FAC(yrs)
    fT = 0.12 + (0.6 - 0.12) * vT / THEO_END
    fN_total = 0.18 + (0.9 - 0.18) * vN / NORA_END
    gold = fN_total / 3
    if not final:
        headline(img, t, f"YEAR {int(round(yrs))} OF 25 · 7% A YEAR")
    jar(img, "T", fT, 0, kfmt(vT), "", t=t)
    jar(img, "N", fN_total - gold, gold, kfmt(vN), "", glow=1.0 if t > tok("grow", 4) else 0, t=t)

def kfmt(v): return "${:,.0f}K".format(v / 1000) if v >= 1000 else money(v)

def sc_punch(img, t):
    s0 = seg_start("punch")
    headline(img, t, "GAP: $114K OF FREE MONEY", GOLD)
    sc_grow(img, t, final=True)
    gap_bracket(img, t, ease_out((t - s0) / 0.5))

def sc_q(img, t):
    headline(img, t, "")
    s0 = seg_start("q")
    d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.35)
    if k > 0.03:
        d.rounded_rectangle([W / 2 - 430 * k, 560 - 230 * k, W / 2 + 430 * k, 560 + 230 * k], radius=40 * k, fill=(255, 255, 255), outline=GOLD, width=max(2, int(10 * k)))
        pop_text(img, (W / 2, 430), "DOES YOUR BOSS", F_NUM, 70, (40, 20, 90), scale=k)
        pop_text(img, (W / 2, 520), "MATCH?", F_NUM, 110, (220, 140, 0), scale=k)
        pop_text(img, (W / 2, 630), "Check your 401(k) plan", F_MED, 44, (60, 50, 110), scale=k)
        pop_text(img, (W / 2, 705), "NORA OR THEO? TELL US", F_NUM, 46, (210, 60, 80), scale=k)

SCENES = {"hook": sc_hook, "hook2": sc_hook, "how": sc_how, "nora": sc_nora, "theo": sc_theo, "grow": sc_grow,
          "punch": sc_punch, "every": sc_punch, "q": sc_q, "loop": sc_hook}
# (theo pose, theo mood, nora pose, nora mood)
STAGE = {"hook": ("idle", "smile", "idle", "smile"), "hook2": ("idle", "smile", "cheer", "smile"),
         "how": ("shrug", "worried", "idle", "smile"), "nora": ("idle", "smile", "point_up", "smile"),
         "theo": ("cheer", "smug", "idle", "smile"), "grow": ("idle", "smile", "point_up", "smile"),
         "punch": ("facepalm", "worried", "idle", "smile"), "every": ("idle", "worried", "shrug", "smile"),
         "q": ("idle", "smile", "point_up", "smile"), "loop": ("idle", "smile", "idle", "smile")}

TX, NX, CY = 300, 780, 1085
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
    for who, cx, col, pose, mood in (("T", TX, THEO, tp, tm), ("N", NX, NORA, np_, nm)):
        talking = 1.0 if (who == spk and in_seg) else 0.0
        sc = 1.17 if who == spk else 1.09
        cy = CY + (0 if who == spk else 14)
        person(img, cx, cy, sc, col, who, t, talk=talking, pose=pose, mood=mood)
        if who == "N" and s["scene"] in ("grow", "punch", "every"):
            k = 1.0 if s["scene"] != "grow" else (ease_back((t - tok("grow", 5)) / 0.4) if t > tok("grow", 5) else 0)
            crown(img, cx, cy, sc, k)

# ---------- captions ----------
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

CAP_Y = 1365
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
    c = (175, 168, 215)
    d.text((W / 2, 1545), "Illustration: $60K salary each, both save 6% ($300/mo). Match: 50¢ per $1", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1578), "on the first 6% of pay, fully vested. Same 7%/yr avg return, 25 years,", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1611), "before taxes & fees. 401(k) money is mostly locked until 59½.", font=font(F_MED, 26), fill=c, anchor="mm")
    d.text((W / 2, 1644), "Returns not guaranteed. Not financial advice.", font=font(F_MED, 26), fill=c, anchor="mm")

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
