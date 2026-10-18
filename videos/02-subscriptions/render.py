"""Render 'The Subscription Math' Short: 1080x1920 @30fps, frames piped to ffmpeg."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
TM = json.load(open(os.path.join(HERE, "timings.json")))
TOTAL = TM["total"] + 0.4
NF = int(TOTAL * FPS)
PREVIEW = [float(x) for x in sys.argv[1:]]

ANNUAL, YMAX = 900, 90000
FINAL, PUT, GROW = "$85,000", 27000, 58015

F_CAP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_NUM = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_MED = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
_fc = {}
def font(path, size):
    k = (path, max(2, int(size)))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, k[1])
    return _fc[k]

BG = (9, 12, 16)
WHITE = (255, 255, 255)
YEL = (255, 216, 77)
GREEN = (52, 211, 120)
RED = (255, 84, 84)
GREY = (150, 158, 168)
DIM = (48, 54, 64)

APPS = [  # kind, colour, label
    ("play", (229, 57, 70), "STREAMING"),
    ("note", (140, 90, 240), "MUSIC"),
    ("cloud", (60, 140, 255), "CLOUD"),
    ("dumbbell", (255, 140, 40), "FITNESS"),
    ("gift", (40, 180, 170), "FREE TRIAL"),
]

def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def clamp(x): return min(max(x, 0), 1)
def lerp(a, b, t): return a + (b - a) * t

SEG = {s["scene"]: s for s in TM["segments"]}
def tok_time(scene, i): return SEG[scene]["tokens"][i]["start"]
def seg_start(scene): return SEG[scene]["start"]
def seg_end(scene): return SEG[scene]["end"]
def scene_at(t):
    cur = TM["segments"][0]["scene"]
    for s in TM["segments"]:
        if t >= s["start"] - 0.05:
            cur = s["scene"]
    return cur

ACT = {"hook": "phone", "hook2": "phone", "list": "list", "month": "month", "year": "year",
       "invest": "chart", "y10": "chart", "y20": "chart", "y30a": "chart", "y30": "chart",
       "apps": "fromapps", "split": "split", "twist": "love", "pick": "check", "cta": "cta"}

yy, xx = np.mgrid[0:H, 0:W]
def make_bg(color):
    cx, cy = W / 2, H * 0.40
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 0.8) ** 2) / 900
    g = np.clip(1 - d, 0, 1) ** 2
    img = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32)
    img += g[..., None] * np.array(color, np.float32) * 0.45
    grid = ((xx % 90 == 0) | (yy % 90 == 0)).astype(np.float32) * 6
    img += grid[..., None] * (0.3 + 0.7 * g[..., None])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
BGS = {"purple": make_bg((110, 60, 190)), "green": make_bg((30, 150, 80)),
       "red": make_bg((170, 40, 40)), "blue": make_bg((40, 90, 170))}
ACT_BG = {"phone": "purple", "list": "purple", "month": "blue", "year": "blue", "chart": "green",
          "fromapps": "red", "split": "green", "love": "purple", "check": "blue", "cta": "blue"}

def text_c(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def pop_text(img, xy, s, path, size, fill, scale=1.0, stroke=0, alpha=1.0, glow=None):
    if scale <= 0.01 or alpha <= 0.01 or size * scale < 2:
        return
    f = font(path, size * scale)
    pad = 40 + stroke
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    layer = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - l, pad - t), s, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    if glow:
        gl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).text((pad - l, pad - t), s, font=f, fill=glow + (170,))
        layer = Image.alpha_composite(gl.filter(ImageFilter.GaussianBlur(22)), layer)
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(layer, (int(xy[0] - layer.width / 2), int(xy[1] - layer.height / 2)))

# ---------- app icons ----------
def glyph(d, kind, cx, cy, s, col=(255, 255, 255, 255)):
    if kind == "play":
        d.polygon([(cx - 22 * s, cy - 30 * s), (cx - 22 * s, cy + 30 * s), (cx + 32 * s, cy)], fill=col)
    elif kind == "note":
        d.ellipse([cx - 34 * s, cy + 6 * s, cx - 6 * s, cy + 30 * s], fill=col)
        d.ellipse([cx + 6 * s, cy - 2 * s, cx + 34 * s, cy + 22 * s], fill=col)
        d.rectangle([cx - 12 * s, cy - 32 * s, cx - 4 * s, cy + 18 * s], fill=col)
        d.rectangle([cx + 26 * s, cy - 40 * s, cx + 34 * s, cy + 10 * s], fill=col)
        d.polygon([(cx - 12 * s, cy - 32 * s), (cx + 34 * s, cy - 40 * s), (cx + 34 * s, cy - 28 * s), (cx - 12 * s, cy - 20 * s)], fill=col)
    elif kind == "cloud":
        d.ellipse([cx - 40 * s, cy - 6 * s, cx - 4 * s, cy + 26 * s], fill=col)
        d.ellipse([cx - 22 * s, cy - 30 * s, cx + 20 * s, cy + 12 * s], fill=col)
        d.ellipse([cx + 2 * s, cy - 14 * s, cx + 40 * s, cy + 26 * s], fill=col)
        d.rectangle([cx - 22 * s, cy + 4 * s, cx + 22 * s, cy + 26 * s], fill=col)
    elif kind == "dumbbell":
        d.rectangle([cx - 30 * s, cy - 5 * s, cx + 30 * s, cy + 5 * s], fill=col)
        for sx in (-1, 1):
            d.rounded_rectangle([cx + sx * 30 * s - 9 * s, cy - 26 * s, cx + sx * 30 * s + 9 * s, cy + 26 * s], radius=4 * s, fill=col)
            d.rounded_rectangle([cx + sx * 44 * s - 6 * s, cy - 17 * s, cx + sx * 44 * s + 6 * s, cy + 17 * s], radius=3 * s, fill=col)
    elif kind == "gift":
        d.rectangle([cx - 30 * s, cy - 8 * s, cx + 30 * s, cy + 32 * s], fill=col)
        d.rectangle([cx - 36 * s, cy - 22 * s, cx + 36 * s, cy - 6 * s], fill=col)
        d.ellipse([cx - 26 * s, cy - 40 * s, cx - 2 * s, cy - 20 * s], outline=col, width=max(1, int(6 * s)))
        d.ellipse([cx + 2 * s, cy - 40 * s, cx + 26 * s, cy - 20 * s], outline=col, width=max(1, int(6 * s)))

def tile(img, i, cx, cy, size, alpha=1.0, dim=False):
    """App tile i (index into APPS), size px."""
    if size < 4 or alpha <= 0.01:
        return
    kind, col, _ = APPS[i]
    lay = Image.new("RGBA", (int(size * 1.3), int(size * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    o = size * 0.15
    c = DIM if dim else col
    d.rounded_rectangle([o, o, o + size, o + size], radius=size * 0.23, fill=c + (int(255 * alpha),))
    glyph(d, kind, o + size / 2, o + size / 2, size / 130, (255, 255, 255, int(255 * alpha * (0.35 if dim else 1))))
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def badge(img, cx, cy, r, text, col=RED):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (255,), outline=(255, 255, 255, 255), width=max(2, int(r / 8)))
    img.alpha_composite(lay)
    pop_text(img, (cx, cy), text, F_NUM, r * 1.2, WHITE)

def heart(d, cx, cy, s, col):
    pts = []
    for i in range(100):
        a = i / 100 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * s, cy - y * s))
    d.polygon(pts, fill=col)

PHONE_ORDER = [0, None, 1, None, 2, 3, None, 4, None]  # 3x3 grid, None = blank app
def draw_phone(img, cx, cy, s, t, dim_all=False, highlight=None):
    if s < 0.03:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pw, ph = 420 * s, 820 * s
    d.rounded_rectangle([cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2], radius=60 * s, fill=(20, 22, 28, 255), outline=(90, 95, 110, 255), width=max(2, int(8 * s)))
    d.rounded_rectangle([cx - pw / 2 + 18 * s, cy - ph / 2 + 18 * s, cx + pw / 2 - 18 * s, cy + ph / 2 - 18 * s], radius=46 * s, fill=(30, 34, 46, 255))
    d.rounded_rectangle([cx - 55 * s, cy - ph / 2 + 34 * s, cx + 55 * s, cy - ph / 2 + 62 * s], radius=14 * s, fill=(10, 10, 12, 255))
    img.alpha_composite(lay)
    ts = 100 * s; gap = 120 * s
    for k, app in enumerate(PHONE_ORDER):
        r, c = divmod(k, 3)
        x = cx + (c - 1) * gap; y = cy - 210 * s + r * gap * 1.1
        if app is None:
            lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(lay2).rounded_rectangle([x - ts / 2, y - ts / 2, x + ts / 2, y + ts / 2], radius=ts * 0.23, fill=(52, 58, 72, 255))
            img.alpha_composite(lay2)
        else:
            dim = dim_all or (highlight is not None and app != highlight)
            tile(img, app, x, y, ts, dim=dim)
    return {app: (cx + (k % 3 - 1) * gap, cy - 210 * s + (k // 3) * gap * 1.1) for k, app in enumerate(PHONE_ORDER) if app is not None}

def money(v): return "${:,.0f}".format(v)
def counter(t, t0, t1, v0, v1): return lerp(v0, v1, ease_out((t - t0) / max(1e-3, t1 - t0)))
def growth(year): return ANNUAL * ((1.07 ** year - 1) / 0.07)

VCY = 820

def act_phone(img, t):
    s0 = seg_start("hook"); k = ease_back((t - s0 + 0.1) / 0.45)
    tbig = tok_time("hook", 5)
    if t < tbig:
        draw_phone(img, W / 2, VCY - 40, 0.92 * k, t)
        return
    u = ease_out((t - tbig) / 0.35)
    ps = lerp(0.92, 0.6, u); py = lerp(VCY - 40, VCY - 150, u)
    pos = draw_phone(img, W / 2, py, ps, t)
    sc = ease_back((t - tbig) / 0.4)
    shake = max(0, 1 - (t - tbig) / 0.4) * 18
    pop_text(img, (W / 2 + math.sin(t * 90) * shake, VCY + 250), FINAL, F_NUM, 190, RED, scale=sc, glow=RED)
    if scene_at(t) == "hook2":
        tf = tok_time("hook2", 2)
        if t > tf:
            x, y = pos[4]
            b = ease_back((t - tf) / 0.35) * (1 + 0.08 * math.sin(t * 10))
            badge(img, x + 40 * ps, y - 40 * ps, 30 * b, "!")

LIST_POS = [(W / 2 - 280, VCY - 260), (W / 2, VCY - 260), (W / 2 + 280, VCY - 260),
            (W / 2 - 140, VCY + 60), (W / 2 + 140, VCY + 60)]
def act_list(img, t):
    times = [tok_time("list", i) for i in (0, 1, 2, 5, 7)]
    d = ImageDraw.Draw(img)
    for i, ti in enumerate(times):
        k = ease_back((t - ti + 0.05) / 0.35)
        if k <= 0: continue
        x, y = LIST_POS[i]
        tile(img, i, x, y, 200 * k)
        if k > 0.6:
            text_c(d, (x, y + 150), APPS[i][2], font(F_MED, 36), GREY)
    if t > tok_time("list", 8):  # "you never cancelled" -> ! badge on trial
        x, y = LIST_POS[4]
        b = ease_back((t - tok_time("list", 8)) / 0.35) * (1 + 0.08 * math.sin(t * 10))
        badge(img, x + 85, y - 85, 38 * b, "!")

ROW_X = [W / 2 + (i - 2) * 180 for i in range(5)]
def act_month(img, t):
    s0 = seg_start("month"); d = ImageDraw.Draw(img)
    t15 = tok_time("month", 0); t75 = tok_time("month", 3)
    for i in range(5):
        k = ease_back((t - s0 - i * 0.08) / 0.3)
        tile(img, i, ROW_X[i], VCY - 220, 140 * k)
        if t > t15 + i * 0.1:
            pop_text(img, (ROW_X[i], VCY - 90), "$15", F_NUM, 52, WHITE, scale=ease_back((t - t15 - i * 0.1) / 0.3))
    if t > t75:
        sc = ease_back((t - t75) / 0.35)
        pop_text(img, (W / 2, VCY + 140), "$75", F_NUM, 210, YEL, scale=sc, glow=YEL)
        pop_text(img, (W / 2, VCY + 280), "PER MONTH", F_MED, 56, GREY, scale=sc)

MONTHS = "JFMAMJJASOND"
def act_year(img, t):
    s0 = seg_start("year"); s1 = seg_end("year"); d = ImageDraw.Draw(img)
    n = int(12 * ease_out((t - s0 + 0.1) / (s1 - s0)))
    bw, bh, gx, gy = 190, 110, 215, 135
    for i in range(12):
        r, c = divmod(i, 4)
        x = W / 2 + (c - 1.5) * gx; y = VCY - 330 + r * gy
        fill = (60, 110, 200) if i < n else (36, 42, 52)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=20, fill=fill)
        text_c(d, (x, y - 18), MONTHS[i], font(F_MED, 30), (220, 225, 235) if i < n else GREY)
        text_c(d, (x, y + 22), "$75", font(F_NUM, 34), WHITE if i < n else (90, 96, 108))
    v = counter(t, s0, s1 - 0.3, 75, ANNUAL)
    sc = ease_back((t - s0) / 0.3)
    pop_text(img, (W / 2, VCY + 230), money(v), F_NUM, 200, YEL, scale=sc, glow=YEL)
    pop_text(img, (W / 2, VCY + 365), "PER YEAR", F_MED, 56, GREY, scale=sc)

def act_chart(img, t):
    d = ImageDraw.Draw(img)
    s0 = seg_start("invest"); k = ease_out((t - s0) / 0.6)
    L, R, T, B = 150, 930, VCY - 360, VCY + 290
    d.line([(L, T), (L, B), (L + (R - L) * k, B)], fill=(90, 100, 95), width=5)
    if k > 0.9:
        for yr in (10, 20, 30):
            text_c(d, (L + (R - L) * yr / 32, B + 45), f"{yr} yrs", font(F_MED, 38), GREY)
    t7 = tok_time("invest", 8)
    if t > t7:
        pop_text(img, (L + 175, T + 30), "7% / yr", F_NUM, 72, GREEN, scale=ease_back((t - t7) / 0.35))
    if t < seg_start("y10"):
        yrs = 0
    elif t < seg_start("y20"):
        yrs = lerp(0, 10, ease_out((t - seg_start("y10")) / 1.6))
    elif t < seg_start("y30a"):
        yrs = lerp(10, 20, ease_out((t - seg_start("y20")) / 1.2))
    elif t < seg_start("y30"):
        yrs = lerp(20, 30, ease_out((t - seg_start("y30a")) / 1.4))
    else:
        yrs = 30
    def pt(yr): return (L + (R - L) * yr / 32, B - (B - T - 60) * growth(yr) / YMAX)
    if yrs > 0.05:
        pts = [pt(y) for y in np.linspace(0, yrs, 80)]
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.polygon(pts + [(pts[-1][0], B), (L, B)], fill=GREEN + (55,))
        ld.line(pts, fill=GREEN + (255,), width=12, joint="curve")
        cp = [(L + (R - L) * y / 32, B - (B - T - 60) * ANNUAL * y / YMAX) for y in np.linspace(0, yrs, 20)]
        ld.line(cp, fill=(200, 200, 200, 140), width=5)
        img.alpha_composite(lay)
        x, y = pts[-1]; d = ImageDraw.Draw(img)
        d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=WHITE)
        if scene_at(t) == "y30":
            sc = ease_back((t - seg_start("y30")) / 0.4)
            shake = max(0, 1 - (t - seg_start("y30")) / 0.35) * 16
            pop_text(img, (W / 2 + math.sin(t * 90) * shake, T - 110), FINAL, F_NUM, 190, GREEN, scale=sc, glow=GREEN)
        else:
            pop_text(img, (W / 2, T - 100), money(round(growth(yrs) / 100) * 100), F_NUM, 150, WHITE)
    else:
        pop_text(img, (W / 2, T - 100), "CANCEL & INVEST", F_NUM, 96, WHITE, scale=ease_back((t - s0) / 0.4))

def act_fromapps(img, t):
    s0 = seg_start("apps"); k = ease_back((t - s0) / 0.35)
    pop_text(img, (W / 2, VCY - 420), FINAL, F_NUM, 160, GREEN, scale=k, glow=GREEN)
    pop_text(img, (W / 2, VCY - 300), "= THESE", F_MED, 70, GREY, scale=k)
    pos = draw_phone(img, W / 2, VCY + 200, 0.68 * k, t, dim_all=t > tok_time("apps", 3))
    if t > tok_time("apps", 1) and pos:
        z = ease_back((t - tok_time("apps", 1)) / 0.4)
        pop_text(img, (W / 2 + 200, VCY - 110), "z z z", F_NUM, 64, GREY, scale=z)

def act_split(img, t):
    d = ImageDraw.Draw(img)
    L, R = 140, 940; y0, y1 = VCY - 120, VCY + 120
    tot = PUT + GROW
    tin = tok_time("split", 2); tgr = tok_time("split", 4)
    k1 = ease_out((t - seg_start("split") + 0.1) / 0.8); k2 = ease_out((t - tgr + 0.1) / 0.8)
    xm = L + (R - L) * PUT / tot
    d.rounded_rectangle([L, y0, R, y1], radius=26, outline=(70, 80, 75), width=4)
    if k1 > 0:
        d.rounded_rectangle([L, y0, L + (xm - L) * k1, y1], radius=26, fill=(170, 175, 172))
    if k2 > 0:
        d.rectangle([xm, y0, xm + (R - xm) * k2, y1], fill=GREEN)
        d.rounded_rectangle([xm + (R - xm) * k2 - 40, y0, xm + (R - xm) * k2, y1], radius=26, fill=GREEN)
    if t > tin - 0.1:
        a = ease_back((t - tin + 0.1) / 0.35)
        pop_text(img, ((L + xm) / 2, y0 - 120), "$27K", F_NUM, 110, WHITE, scale=a)
        pop_text(img, ((L + xm) / 2, y0 - 45), "YOU PUT IN", F_MED, 36, GREY, scale=a)
    if k2 > 0:
        pop_text(img, ((xm + R) / 2, y1 + 110), "$58K", F_NUM, 150, GREEN, scale=ease_back((t - tgr) / 0.35), glow=GREEN)
        pop_text(img, ((xm + R) / 2, y1 + 210), "COMPOUND INTEREST", F_MED, 40, GREEN,
                 scale=ease_back((t - tok_time("split", 6)) / 0.35))

def act_love(img, t):
    s0 = seg_start("twist"); tl = tok_time("twist", 3)
    d = ImageDraw.Draw(img)
    keep = (0, 1)
    for i in range(5):
        k = ease_back((t - s0 - i * 0.06) / 0.3)
        faded = t > tl and i not in keep
        y = VCY - 120 + (60 * ease_out((t - tl) / 0.4) if faded else 0)
        tile(img, i, ROW_X[i], y, 150 * k, alpha=0.35 if faded else 1.0, dim=faded)
    if t > tl:
        hb = ease_back((t - tl) / 0.35) * (1 + 0.06 * math.sin(t * 9))
        for i in keep:
            heart(d, ROW_X[i] + 55, VCY - 190, 3.2 * hb, (255, 90, 120))
        pop_text(img, (W / 2, VCY - 380), "KEEP WHAT YOU LOVE", F_NUM, 80, WHITE, scale=ease_back((t - tl) / 0.35))

def act_check(img, t):
    s0 = seg_start("pick"); k = ease_back((t - s0) / 0.4)
    pop_text(img, (W / 2, VCY - 470), "CHECK NOW", F_NUM, 120, YEL, scale=k, glow=YEL)
    pos = draw_phone(img, W / 2, VCY + 20, 0.7 * k, t)
    if not pos: return
    # magnifying glass sweeps across apps and lands on the free trial
    order = [0, 1, 2, 3, 4]
    tf = tok_time("pick", 5)  # "I bet"
    u = clamp((t - s0 - 0.4) / max(0.5, tf - s0 - 0.4))
    f = u * (len(order) - 1)
    a, b = int(f), min(int(f) + 1, len(order) - 1)
    x = lerp(pos[order[a]][0], pos[order[b]][0], ease_out(f - a))
    y = lerp(pos[order[a]][1], pos[order[b]][1], ease_out(f - a))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = 85
    d.line([(x + r * 0.7, y + r * 0.7), (x + r * 1.6, y + r * 1.6)], fill=(235, 235, 240, 255), width=26)
    d.ellipse([x - r, y - r, x + r, y + r], outline=(235, 235, 240, 255), width=16)
    d.ellipse([x - r + 8, y - r + 8, x + r - 8, y + r - 8], fill=(255, 255, 255, 40))
    img.alpha_composite(lay)
    if t > tok_time("pick", 7):
        tx, ty = pos[4]
        b = ease_back((t - tok_time("pick", 7)) / 0.35) * (1 + 0.08 * math.sin(t * 10))
        badge(img, tx + 50, ty - 50, 36 * b, "!")

def act_cta(img, t):
    s0 = seg_start("cta"); k = ease_back((t - s0) / 0.4)
    pulse = 1 + 0.05 * math.sin((t - s0) * 7)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bw, bh = 560 * k * pulse, 170 * k * pulse
    if bw > 2:
        d.rounded_rectangle([W / 2 - bw / 2, VCY - bh / 2, W / 2 + bw / 2, VCY + bh / 2], radius=bh / 2, fill=(255, 60, 60, 255))
    img.alpha_composite(lay)
    pop_text(img, (W / 2, VCY), "FOLLOW", F_NUM, 92, WHITE, scale=k * pulse)
    pop_text(img, (W / 2, VCY - 260), "MORE MONEY MATH", F_MED, 58, GREY, scale=k)

ACTS = {"phone": act_phone, "list": act_list, "month": act_month, "year": act_year, "chart": act_chart,
        "fromapps": act_fromapps, "split": act_split, "love": act_love, "check": act_check, "cta": act_cta}

# ---------- captions ----------
GROUPS = []
for s in TM["segments"]:
    cur = []
    for tk in s["tokens"]:
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
        if gs <= t < ge: break
    else:
        return
    f = font(F_CAP, 92)
    widths = [f.getbbox(tk["text"], stroke_width=12)[2] - f.getbbox(tk["text"], stroke_width=12)[0] for tk in toks]
    space = 52
    lines, line, lw = [], [], 0
    for i, w_ in enumerate(widths):
        if line and lw + space + w_ > 920:
            lines.append(line); line, lw = [], 0
        lw += (space if line else 0) + w_; line.append(i)
    lines.append(line)
    gk = ease_back((t - gs) / 0.18)
    for li, ln in enumerate(lines):
        tw = sum(widths[i] for i in ln) + space * (len(ln) - 1)
        x = W / 2 - tw / 2; y = CAP_Y + (li - (len(lines) - 1) / 2) * 112
        for i in ln:
            tk = toks[i]
            active = tk["start"] <= t < tk["end"] + 0.05 or (i == len(toks) - 1 and t >= tk["start"])
            col = GREEN if ("$" in tk["text"] or "%" in tk["text"]) else (YEL if active else WHITE)
            pop_text(img, (x + widths[i] / 2, y), tk["text"], F_CAP, 92, col, scale=gk * (1.05 if active else 1.0), stroke=12)
            x += widths[i] + space

def draw_ui(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * t / TOTAL, 10], fill=YEL)
    f = font(F_MED, 40); label = "THE SUBSCRIPTION MATH"
    l, tp, r, b = f.getbbox(label); pw = r - l + 70
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([W / 2 - pw / 2, 175, W / 2 + pw / 2, 245], radius=35, fill=(255, 255, 255, 28), outline=(255, 255, 255, 200), width=3)
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    text_c(d, (W / 2, 211), label, f, WHITE)
    if seg_start("invest") <= t < seg_end("split") + 0.3:
        text_c(d, (W / 2, 1520), "Illustration only. Assumes a 7% average yearly return,", font(F_MED, 28), (125, 135, 140))
        text_c(d, (W / 2, 1558), "which is not guaranteed. Not financial advice.", font(F_MED, 28), (125, 135, 140))

def frame(t):
    act = ACT[scene_at(t)]
    img = BGS[ACT_BG[act]].copy().convert("RGBA")
    ACTS[act](img, t)
    draw_captions(img, t)
    draw_ui(img, t)
    for s in TM["segments"]:
        if ACT[s["scene"]] != ACT.get(scene_at(s["start"] - 0.1)) and 0 <= t - s["start"] + 0.05 < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(70 * (1 - (t - s["start"] + 0.05) / 0.12)))))
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
