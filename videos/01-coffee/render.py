"""Render the coffee-maths Short: 1080x1920 @30fps, frames piped to ffmpeg."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
TM = json.load(open(os.path.join(HERE, "timings.json")))
TOTAL = TM["total"] + 0.4
NF = int(TOTAL * FPS)
PREVIEW = [float(x) for x in sys.argv[1:]]  # optional: times to dump as PNG instead of video

F_CAP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_NUM = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_MED = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
_fc = {}
def font(path, size):
    k = (path, max(2, int(size)))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, k[1])
    return _fc[k]

BG = (9, 14, 12)
WHITE = (255, 255, 255)
YEL = (255, 216, 77)
GREEN = (52, 211, 120)
RED = (255, 84, 84)
GREY = (150, 160, 155)
BROWN = (150, 96, 60)
CREAM = (240, 226, 205)

def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def clamp(x): return min(max(x, 0), 1)
def lerp(a, b, t): return a + (b - a) * t

# ---------- timeline helpers ----------
SEG = {s["scene"]: s for s in TM["segments"]}
def tok_time(scene, i):
    return SEG[scene]["tokens"][i]["start"]
def seg_start(scene): return SEG[scene]["start"]
def seg_end(scene): return SEG[scene]["end"]

def scene_at(t):
    cur = TM["segments"][0]["scene"]
    for s in TM["segments"]:
        if t >= s["start"] - 0.05:
            cur = s["scene"]
    return cur

# visual "acts" group several scenes
ACT = {"hook": "cup", "hook2": "cup", "week": "week", "year": "year", "invest": "chart",
       "y10": "chart", "y20": "chart", "y30a": "chart", "y30": "chart", "coffee": "fromcoffee",
       "split": "split", "twist": "enjoy", "pick": "grow", "cta": "cta"}

# ---------- background (precomputed) ----------
yy, xx = np.mgrid[0:H, 0:W]
def make_bg(color):
    cx, cy = W / 2, H * 0.40
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 0.8) ** 2) / 900
    g = np.clip(1 - d, 0, 1) ** 2
    img = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32)
    img += g[..., None] * np.array(color, np.float32) * 0.45
    # subtle grid
    grid = ((xx % 90 == 0) | (yy % 90 == 0)).astype(np.float32) * 6
    img += grid[..., None] * (0.3 + 0.7 * g[..., None])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BGS = {"warm": make_bg((150, 90, 40)), "green": make_bg((30, 150, 80)),
       "red": make_bg((170, 40, 40)), "blue": make_bg((40, 90, 170))}
ACT_BG = {"cup": "warm", "week": "warm", "year": "warm", "chart": "green", "fromcoffee": "red",
          "split": "green", "enjoy": "warm", "grow": "green", "cta": "blue"}

# ---------- drawing primitives ----------
def text_c(d, xy, s, f, fill, stroke=0, sfill=(0, 0, 0), anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

def pop_text(img, xy, s, path, size, fill, scale=1.0, stroke=0, alpha=1.0, glow=None):
    """Render text into its own layer so it can be scaled / faded."""
    if scale <= 0.01 or alpha <= 0.01:
        return
    f = font(path, size * scale)
    pad = 40 + stroke
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    layer = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((pad - l, pad - t), s, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    if glow:
        gl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).text((pad - l, pad - t), s, font=f, fill=glow + (170,))
        gl = gl.filter(ImageFilter.GaussianBlur(22))
        layer = Image.alpha_composite(gl, layer)
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha)); layer.putalpha(a)
    img.alpha_composite(layer, (int(xy[0] - layer.width / 2), int(xy[1] - layer.height / 2)))

def draw_cup(img, cx, cy, s, t, label=None, alpha=1.0):
    """Takeaway coffee cup, scale s (1 = ~ 300px tall)."""
    if s < 0.03 or alpha <= 0.01:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    h = 300 * s; wt = 210 * s; wb = 160 * s
    top = cy - h / 2; bot = cy + h / 2
    a = int(255 * alpha)
    # body
    d.polygon([(cx - wt / 2, top + 30 * s), (cx + wt / 2, top + 30 * s), (cx + wb / 2, bot), (cx - wb / 2, bot)], fill=CREAM + (a,))
    # sleeve
    sy0, sy1 = top + 105 * s, top + 215 * s
    def wat(y):
        k = (y - (top + 30 * s)) / (bot - (top + 30 * s)); return lerp(wt, wb, k) / 2
    d.polygon([(cx - wat(sy0), sy0), (cx + wat(sy0), sy0), (cx + wat(sy1), sy1), (cx - wat(sy1), sy1)], fill=BROWN + (a,))
    # lid
    d.rounded_rectangle([cx - wt / 2 - 16 * s, top + 4 * s, cx + wt / 2 + 16 * s, top + 36 * s], radius=10 * s, fill=(245, 245, 240, a))
    d.rounded_rectangle([cx - wt / 2 + 8 * s, top - 18 * s, cx + wt / 2 - 8 * s, top + 8 * s], radius=10 * s, fill=(230, 230, 225, a))
    # steam
    for k in (-1, 0, 1):
        pts = []
        for j in range(24):
            yv = top - 40 * s - j * 7 * s
            xv = cx + k * 50 * s + math.sin(j * 0.45 + t * 4 + k) * 14 * s
            pts.append((xv, yv))
        d.line(pts, fill=(255, 255, 255, int(a * 0.35)), width=max(2, int(9 * s)), joint="curve")
    img.alpha_composite(lay)
    if label:
        pop_text(img, (cx, (sy0 + sy1) / 2), label, F_NUM, 70 * s, WHITE, alpha=alpha)

def money(v):
    return "${:,.0f}".format(v)

def counter(t, t0, t1, v0, v1):
    return lerp(v0, v1, ease_out((t - t0) / max(1e-3, t1 - t0)))

# ---------- acts ----------
VCY = 820  # visual centre y

def act_cup(img, t):
    s0 = seg_start("hook")
    k = ease_back((t - s0 + 0.1) / 0.45)
    t172 = tok_time("hook", 5)
    if t < t172:
        draw_cup(img, W / 2, VCY + 40, 1.45 * k, t, label="$5")
    else:
        # cup shrinks up, number slams in
        u = ease_out((t - t172) / 0.35)
        draw_cup(img, W / 2, lerp(VCY + 40, VCY - 200, u), lerp(1.45, 0.75, u), t, label="$5")
        sc = ease_back((t - t172) / 0.4)
        shake = max(0, 1 - (t - t172) / 0.4) * 18
        dx = math.sin(t * 90) * shake
        pop_text(img, (W / 2 + dx, VCY + 230), "$172,000", F_NUM, 190, RED, scale=sc, glow=RED)
        if scene_at(t) == "hook2":
            q = ease_back((t - seg_start("hook2")) / 0.4)
            pop_text(img, (W / 2, VCY + 420), "...really?", F_MED, 64, GREY, scale=q)

def act_week(img, t):
    s0 = seg_start("week")
    d = ImageDraw.Draw(img)
    t35 = tok_time("week", 3)
    for i in range(7):
        ti = s0 + i * (t35 - s0) / 7
        k = ease_back((t - ti) / 0.3)
        if k > 0:
            cx = W / 2 + (i - 3) * 128
            draw_cup(img, cx, VCY - 40, 0.36 * k, t + i)
    days = "MTWTFSS"
    for i in range(7):
        ti = s0 + i * (t35 - s0) / 7
        if t > ti:
            text_c(d, (W / 2 + (i - 3) * 128, VCY + 90), days[i], font(F_MED, 40), GREY)
    if t > t35:
        sc = ease_back((t - t35) / 0.35)
        pop_text(img, (W / 2, VCY + 250), "$35", F_NUM, 200, YEL, scale=sc, glow=YEL)
        pop_text(img, (W / 2, VCY + 390), "PER WEEK", F_MED, 56, GREY, scale=sc)

def act_year(img, t):
    s0 = seg_start("year"); s1 = seg_end("year")
    d = ImageDraw.Draw(img)
    # 365 dots (25 x 15 grid) filling
    n = int(365 * ease_out((t - s0) / (s1 - s0 + 0.2)))
    cols, sp = 25, 34
    x0 = W / 2 - (cols - 1) * sp / 2; y0 = VCY - 390
    for i in range(365):
        r, c = divmod(i, cols)
        x, y = x0 + c * sp, y0 + r * sp
        col = BROWN if i < n else (40, 46, 43)
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=col)
    v = counter(t, s0, tok_time("year", 2) + 0.2, 0, 1825)
    sc = ease_back((t - s0) / 0.3)
    pop_text(img, (W / 2, VCY + 230), money(v), F_NUM, 190, YEL, scale=sc, glow=YEL)
    pop_text(img, (W / 2, VCY + 360), "PER YEAR", F_MED, 56, GREY, scale=sc)

def growth(year):
    return 1825 * ((1.07 ** year - 1) / 0.07)

def act_chart(img, t):
    d = ImageDraw.Draw(img)
    s0 = seg_start("invest")
    k = ease_out((t - s0) / 0.6)
    # axes
    L, R, T, B = 150, 930, VCY - 360, VCY + 290
    d.line([(L, T), (L, B), (L + (R - L) * k, B)], fill=(90, 100, 95), width=5)
    for yr in (10, 20, 30):
        x = L + (R - L) * yr / 32
        if k > 0.9:
            text_c(d, (x, B + 45), f"{yr} yrs", font(F_MED, 38), GREY)
    # 7% badge
    t7 = tok_time("invest", 9)
    if t > t7:
        sc = ease_back((t - t7) / 0.35)
        pop_text(img, (L + 175, T + 30), "7% / yr", F_NUM, 72, GREEN, scale=sc)
    # growth curve progress
    if t < seg_start("y10"):
        yrs = 0
    elif t < seg_start("y20"):
        yrs = lerp(0, 10, ease_out((t - seg_start("y10")) / 1.6))
    elif t < seg_start("y30"):
        yrs = lerp(10, 20, ease_out((t - seg_start("y20")) / 1.2)) if t < seg_start("y30a") else \
              lerp(20, 30, ease_out((t - seg_start("y30a")) / 2.0))
    else:
        yrs = 30
    ymax = 180000
    def pt(yr): return (L + (R - L) * yr / 32, B - (B - T - 60) * growth(yr) / ymax)
    if yrs > 0.05:
        pts = [pt(y) for y in np.linspace(0, yrs, 80)]
        poly = pts + [(pts[-1][0], B), (L, B)]
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.polygon(poly, fill=GREEN + (55,))
        ld.line(pts, fill=GREEN + (255,), width=12, joint="curve")
        # contributions line (what you put in)
        cp = [(L + (R - L) * y / 32, B - (B - T - 60) * 1825 * y / ymax) for y in np.linspace(0, yrs, 20)]
        ld.line(cp, fill=(200, 200, 200, 140), width=5)
        img.alpha_composite(lay)
        x, y = pts[-1]
        d = ImageDraw.Draw(img)
        d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=WHITE)
        # live value label
        v = growth(yrs)
        big = scene_at(t) == "y30"
        if big:
            sc = ease_back((t - seg_start("y30")) / 0.4)
            shake = max(0, 1 - (t - seg_start("y30")) / 0.35) * 16
            pop_text(img, (W / 2 + math.sin(t * 90) * shake, T - 110), "$172,000", F_NUM, 190, GREEN, scale=sc, glow=GREEN)
        else:
            pop_text(img, (W / 2, T - 100), money(round(v / 100) * 100), F_NUM, 150, WHITE)
    else:
        pop_text(img, (W / 2, T - 100), "INVEST IT", F_NUM, 120, WHITE, scale=ease_back((t - s0) / 0.4))

def act_fromcoffee(img, t):
    s0 = seg_start("coffee")
    k = ease_back((t - s0) / 0.35)
    draw_cup(img, W / 2, VCY + 230, 1.25 * k, t)
    pop_text(img, (W / 2, VCY - 400), "$172,000", F_NUM, 160, GREEN, scale=k, glow=GREEN)
    pop_text(img, (W / 2, VCY - 280), "= THIS", F_MED, 70, GREY, scale=k)

def act_split(img, t):
    d = ImageDraw.Draw(img)
    s0 = seg_start("split")
    L, R = 140, 940
    y0, y1 = VCY - 120, VCY + 120
    tot = 172393; put = 54750
    tin = tok_time("split", 5); tgr = tok_time("split", 7)
    k1 = ease_out((t - tin + 0.1) / 0.6)
    k2 = ease_out((t - tgr + 0.1) / 0.8)
    xm = L + (R - L) * put / tot
    d.rounded_rectangle([L, y0, R, y1], radius=26, outline=(70, 80, 75), width=4)
    if k1 > 0:
        d.rounded_rectangle([L, y0, L + (xm - L) * k1, y1], radius=26, fill=(170, 175, 172))
    if k2 > 0:
        d.rectangle([xm, y0, xm + (R - xm) * k2, y1], fill=GREEN)
        d.rounded_rectangle([xm + (R - xm) * k2 - 40, y0, xm + (R - xm) * k2, y1], radius=26, fill=GREEN)
    if k1 > 0:
        pop_text(img, ((L + xm) / 2, y0 - 120), "$55K", F_NUM, 110, WHITE, scale=ease_back((t - tin) / 0.35))
        pop_text(img, ((L + xm) / 2, y0 - 45), "YOU PUT IN", F_MED, 36, GREY, scale=ease_back((t - tin) / 0.35))
    if k2 > 0:
        pop_text(img, ((xm + R) / 2, y1 + 110), "$117K", F_NUM, 150, GREEN, scale=ease_back((t - tgr) / 0.35), glow=GREEN)
        pop_text(img, ((xm + R) / 2, y1 + 210), "COMPOUND INTEREST", F_MED, 40, GREEN,
                 scale=ease_back((t - tok_time("split", 9)) / 0.35))
    if t < tin - 0.1:
        pop_text(img, (W / 2, VCY - 300), "THE CRAZY PART", F_NUM, 96, YEL, scale=ease_back((t - s0) / 0.4))

def heart(d, cx, cy, s, col):
    pts = []
    for i in range(100):
        a = i / 100 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * s, cy - y * s))
    d.polygon(pts, fill=col)

def act_enjoy(img, t):
    s0 = seg_start("twist")
    k = ease_back((t - s0) / 0.4)
    tq = tok_time("twist", 3); ten = tok_time("twist", 5)
    draw_cup(img, W / 2, VCY + 40, 1.4 * k, t)
    d = ImageDraw.Draw(img)
    if tq < t < ten:  # red cross "quit?"
        u = ease_out((t - tq) / 0.25)
        d.line([(W / 2 - 230, VCY - 190), (W / 2 - 230 + 460 * u, VCY - 190 + 460 * u)], fill=RED, width=26)
        if u >= 1:
            d.line([(W / 2 + 230, VCY - 190), (W / 2 - 230, VCY + 270)], fill=RED, width=26)
    if t >= ten:
        hb = ease_back((t - ten) / 0.35) * (1 + 0.06 * math.sin(t * 9))
        heart(d, W / 2 + 190, VCY - 200, 6.5 * hb, (255, 90, 120))
        pop_text(img, (W / 2, VCY - 330), "ENJOY IT", F_NUM, 110, WHITE, scale=ease_back((t - ten) / 0.35))

def act_grow(img, t):
    d = ImageDraw.Draw(img)
    s0 = seg_start("pick")
    k = ease_back((t - s0) / 0.4)
    pop_text(img, (W / 2, VCY - 330), "ONE THING", F_NUM, 120, YEL, scale=k, glow=YEL)
    tg = tok_time("pick", 7)
    # seedling growing
    g = ease_out((t - tg + 0.2) / 1.0)
    base = VCY + 300
    d.rounded_rectangle([W / 2 - 150, base, W / 2 + 150, base + 60], radius=20, fill=BROWN)
    if g > 0:
        top = base - 420 * g
        d.line([(W / 2, base), (W / 2, top)], fill=GREEN, width=20)
        for j, frac in enumerate((0.35, 0.6, 0.85)):
            if g > frac - 0.25:
                lk = clamp((g - frac + 0.25) / 0.3)
                yv = base - 420 * g * frac
                sgn = -1 if j % 2 == 0 else 1
                w_, h_ = 120 * lk, 55 * lk
                cx = W / 2 + sgn * w_ * 0.55
                d.ellipse([cx - w_ / 2, yv - h_ / 2, cx + w_ / 2, yv + h_ / 2], fill=GREEN)
        # coin at top
        d.ellipse([W / 2 - 55 * g, top - 110 * g, W / 2 + 55 * g, top], fill=YEL)
        if g > 0.5:
            text_c(d, (W / 2, top - 55 * g), "$", font(F_NUM, 80 * g), BG)
    else:
        draw_cup(img, W / 2, VCY + 60, 0.9 * k, t)

def act_cta(img, t):
    s0 = seg_start("cta")
    k = ease_back((t - s0) / 0.4)
    pulse = 1 + 0.05 * math.sin((t - s0) * 7)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bw, bh = 560 * k * pulse, 170 * k * pulse
    if bw > 2:
        d.rounded_rectangle([W / 2 - bw / 2, VCY - bh / 2, W / 2 + bw / 2, VCY + bh / 2], radius=bh / 2, fill=(255, 60, 60, 255))
    img.alpha_composite(lay)
    pop_text(img, (W / 2, VCY), "FOLLOW", F_NUM, 92, WHITE, scale=k * pulse)
    pop_text(img, (W / 2, VCY - 260), "MORE MONEY MATH", F_MED, 58, GREY, scale=k)

ACTS = {"cup": act_cup, "week": act_week, "year": act_year, "chart": act_chart, "fromcoffee": act_fromcoffee,
        "split": act_split, "enjoy": act_enjoy, "grow": act_grow, "cta": act_cta}

# ---------- captions ----------
GROUPS = []  # (start, end, [tokens])
for s in TM["segments"]:
    toks = s["tokens"]; cur = []
    for tk in toks:
        cur.append(tk)
        chars = sum(len(x["text"]) for x in cur)
        if chars >= 11 or tk["text"][-1] in ".?!," or len(cur) == 3:
            GROUPS.append(cur); cur = []
    if cur: GROUPS.append(cur)
for i, g in enumerate(GROUPS):
    end = GROUPS[i + 1][0]["start"] if i + 1 < len(GROUPS) else g[-1]["end"] + 0.5
    GROUPS[i] = (g[0]["start"], min(end, g[-1]["end"] + 0.6), g)

CAP_Y = 1330
def draw_captions(img, t):
    for gs, ge, toks in GROUPS:
        if gs <= t < ge:
            break
    else:
        return
    f = font(F_CAP, 92)
    words = [tk["text"] for tk in toks]
    sizes = [f.getbbox(w_, stroke_width=12) for w_ in words]
    widths = [b[2] - b[0] for b in sizes]
    space = 52
    # wrap to lines of max 900px
    lines, line, lw = [], [], 0
    for i, w_ in enumerate(widths):
        if line and lw + space + w_ > 920:
            lines.append(line); line, lw = [], 0
        lw += (space if line else 0) + w_; line.append(i)
    lines.append(line)
    gk = ease_back((t - gs) / 0.18)
    for li, ln in enumerate(lines):
        tw = sum(widths[i] for i in ln) + space * (len(ln) - 1)
        x = W / 2 - tw / 2
        y = CAP_Y + (li - (len(lines) - 1) / 2) * 112
        for i in ln:
            tk = toks[i]
            active = tk["start"] <= t < tk["end"] + 0.05 or (i == len(toks) - 1 and t >= tk["start"])
            is_money = "$" in tk["text"] or "%" in tk["text"]
            col = GREEN if is_money else (YEL if active else WHITE)
            sc = gk * (1.05 if active else 1.0)
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 92, col, scale=sc, stroke=12)
            x += widths[i] + space

# ---------- persistent UI ----------
def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    # progress bar
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=YEL)
    # title pill
    f = font(F_MED, 40)
    label = "THE $5 COFFEE MATH"
    l, tp, r, b = f.getbbox(label)
    pw = r - l + 70
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([W / 2 - pw / 2, 175, W / 2 + pw / 2, 245], radius=35, fill=(255, 255, 255, 28), outline=(255, 255, 255, 200), width=3)
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    text_c(d, (W / 2, 211), label, f, WHITE)
    # disclaimer while numbers are on screen
    if seg_start("invest") <= t < seg_end("split") + 0.3:
        text_c(d, (W / 2, 1520), "Illustration only. Assumes a 7% average yearly return,", font(F_MED, 28), (125, 135, 130))
        text_c(d, (W / 2, 1558), "which is not guaranteed. Not financial advice.", font(F_MED, 28), (125, 135, 130))

def frame(t):
    act = ACT[scene_at(t)]
    img = BGS[ACT_BG[act]].copy().convert("RGBA")
    # act transition: quick fade-in of new act
    ACTS[act](img, t)
    draw_captions(img, t)
    draw_ui(img, t)
    # flash on act change
    for s in TM["segments"]:
        if ACT[s["scene"]] != ACT.get(scene_at(s["start"] - 0.1), None) and 0 <= t - s["start"] + 0.05 < 0.12:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(70 * (1 - (t - s["start"] + 0.05) / 0.12))))
            img.alpha_composite(fl)
    return img.convert("RGB")

if PREVIEW:
    for tt in PREVIEW:
        frame(tt).save(os.path.join(HERE, f"prev_{tt:05.2f}.png"))
    sys.exit()

out = os.path.join(HERE, "video_noaudio.mp4")
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                      "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
start, end = (int(os.environ.get("F0", 0)), int(os.environ.get("F1", NF)))
for i in range(start, end):
    p.stdin.write(frame(i / FPS).tobytes())
    if i % 150 == 0:
        print("frame", i, "/", NF, flush=True)
p.stdin.close(); p.wait()
print("done", out)
