"""Render 'The Twin Math' Short: 1080x1920 @30fps, frames piped to ffmpeg."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
TM = json.load(open(os.path.join(HERE, "timings.json")))
TOTAL = TM["total"] + 0.4
NF = int(TOTAL * FPS)
PREVIEW = [float(x) for x in sys.argv[1:]]

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

ACT = {"hook": "hook", "hook2": "hook", "emma": "story", "jack": "story", "put": "put",
       "race": "race", "race2": "race", "fin_a": "race", "fin": "race", "why": "why",
       "twist": "today", "pick": "today", "cta": "cta"}

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
ACT_BG = {"hook": "purple", "story": "blue", "put": "purple", "race": "green", "why": "purple",
          "today": "blue", "cta": "blue"}

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

# ---------- twin acts (spliced into render.py) ----------
EMMA = (190, 110, 255)
JACK = (70, 160, 255)
GOLD = (255, 200, 60)

def money(v): return "${:,.0f}".format(v)
def kfmt(v): return "${:,.0f}K".format(v / 1000)
def fv(a, n): return a * ((1.07 ** n - 1) / 0.07) if n > 0 else 0.0
def emma_val(age):
    if age <= 25: return 0.0
    return fv(3600, min(age - 25, 10)) * 1.07 ** max(0, age - 35)
def jack_val(age): return fv(3600, max(0, age - 35))

VCY = 820

def person(img, cx, cy, s, col, alpha=1.0, crown=0.0, label=None):
    if s < 0.03 or alpha <= 0.01:
        return
    a = int(255 * alpha)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([cx - 62 * s, cy - 190 * s, cx + 62 * s, cy - 66 * s], fill=col + (a,))
    d.rounded_rectangle([cx - 110 * s, cy - 50 * s, cx + 110 * s, cy + 150 * s], radius=90 * s, fill=col + (a,))
    d.rectangle([cx - 110 * s, cy + 90 * s, cx + 110 * s, cy + 150 * s], fill=col + (a,))
    if crown > 0.01:
        c = crown; yb = cy - 196 * s; w = 70 * s * c; h = 60 * s * c
        d.polygon([(cx - w, yb), (cx - w, yb - h), (cx - w / 2, yb - h * 0.5), (cx, yb - h * 1.15),
                   (cx + w / 2, yb - h * 0.5), (cx + w, yb - h), (cx + w, yb)], fill=GOLD + (a,))
    img.alpha_composite(lay)
    if label:
        pop_text(img, (cx, cy + 210 * s), label, F_NUM, 64 * s, col, alpha=alpha)

def act_hook(img, t):
    s0 = seg_start("hook"); k = ease_back((t - s0 + 0.1) / 0.45)
    t10 = tok_time("hook", 3); t30 = tok_time("hook", 5); trich = tok_time("hook2", 3)
    cr = ease_back((t - trich) / 0.4) if t > trich else 0
    person(img, W / 2 - 220, VCY - 40, 1.25 * k, EMMA, crown=cr)
    person(img, W / 2 + 220, VCY - 40, 1.25 * k, JACK)
    if t > t10:
        pop_text(img, (W / 2 - 220, VCY + 270), "10 YRS", F_NUM, 90, EMMA, scale=ease_back((t - t10) / 0.35))
    if t > t30:
        pop_text(img, (W / 2 + 220, VCY + 270), "30 YRS", F_NUM, 90, JACK, scale=ease_back((t - t30) / 0.35))
    if t > trich:
        pop_text(img, (W / 2, VCY - 420), "WHO WINS?", F_NUM, 120, GOLD, scale=ease_back((t - trich) / 0.4), glow=GOLD)

# timeline geometry
TL_L, TL_R = 150, 930
def age_x(age): return TL_L + (TL_R - TL_L) * (age - 25) / 40

def timeline(img, t, show_emma, show_jack, emma_fill, jack_fill):
    d = ImageDraw.Draw(img)
    for age in (25, 35, 45, 55, 65):
        x = age_x(age)
        d.line([(x, VCY + 170), (x, VCY + 190)], fill=(110, 116, 128), width=4)
        text_c(d, (x, VCY + 225), str(age), font(F_MED, 40), GREY)
    d.line([(TL_L, VCY + 180), (TL_R, VCY + 180)], fill=(110, 116, 128), width=4)
    text_c(d, (W / 2, VCY + 280), "AGE", font(F_MED, 34), (110, 116, 128))
    for who, y, col, show, fill, a0, a1 in (("EMMA", VCY - 60, EMMA, show_emma, emma_fill, 25, 35),
                                            ("JACK", VCY + 70, JACK, show_jack, jack_fill, 35, 65)):
        if show <= 0: continue
        text_c(d, (TL_L - 10, y - 60), who, font(F_NUM, 44), col, anchor="lm")
        d.rounded_rectangle([TL_L, y - 28, TL_R, y + 28], radius=28, fill=(38, 42, 52))
        if fill > 0:
            x0 = age_x(a0); x1 = lerp(x0, age_x(a1), fill)
            d.rounded_rectangle([x0, y - 28, max(x0 + 56, x1), y + 28], radius=28, fill=col)

def act_story(img, t):
    se = seg_start("emma"); sj = seg_start("jack")
    tstop = tok_time("emma", 7); tj35 = tok_time("jack", 2)
    k = ease_back((t - se) / 0.4)
    ef = ease_out((t - tok_time("emma", 3)) / max(0.4, tstop - tok_time("emma", 3)))
    jf = ease_out((t - tj35) / max(0.4, seg_end("jack") - tj35)) if t > tj35 else 0
    in_jack = scene_at(t) == "jack"
    person(img, W / 2 - (160 if in_jack else 0), VCY - 380, 0.62 * k, EMMA, alpha=0.4 if in_jack else 1.0)
    if in_jack:
        person(img, W / 2 + 160, VCY - 380, 0.62 * ease_back((t - sj) / 0.4), JACK)
    timeline(img, t, 1, 1 if in_jack else 0, ef, jf)
    if not in_jack and t > tstop:
        x = age_x(35) + 40
        pop_text(img, (x + 70, VCY - 140), "STOPS", F_NUM, 56, RED, scale=ease_back((t - tstop) / 0.3))
    if in_jack and t < tj35:
        pop_text(img, (age_x(30), VCY + 70), "waiting...", F_MED, 44, GREY, scale=ease_back((t - sj) / 0.3))

def act_put(img, t):
    s0 = seg_start("put"); d = ImageDraw.Draw(img)
    te = tok_time("put", 2); tj = tok_time("put", 5); t3 = tok_time("put", 6)
    base = VCY + 230; maxh = 440
    for cx, col, val, tt, name in ((W / 2 - 220, EMMA, 36000, te, "EMMA"), (W / 2 + 220, JACK, 108000, tj, "JACK")):
        k = ease_out((t - tt + 0.15) / 0.6) if t > tt - 0.15 else 0
        h = maxh * val / 108000 * k
        d.rounded_rectangle([cx - 120, base - max(h, 1), cx + 120, base], radius=24, fill=col)
        text_c(d, (cx, base + 60), name, font(F_NUM, 56), col)
        if k > 0:
            pop_text(img, (cx, base - h - 70), kfmt(val), F_NUM, 100, WHITE, scale=ease_back((t - tt) / 0.35))
    pop_text(img, (W / 2, VCY - 500), "MONEY PUT IN", F_NUM, 80, WHITE, scale=ease_back((t - s0) / 0.4))
    if t > t3:
        pop_text(img, (W / 2, base - 220), "3x", F_NUM, 110, YEL, scale=ease_back((t - t3) / 0.35), glow=YEL)

def chart_age(t):
    if t < tok_time("race", 4): return 25 + 2 * ease_out((t - seg_start("race")) / 1.0)
    if t < seg_start("race2"): return lerp(27, 45, ease_out((t - tok_time("race", 4)) / 0.9))
    if t < seg_start("fin_a"): return lerp(45, 55, ease_out((t - seg_start("race2")) / 1.2))
    if t < seg_start("fin"): return lerp(55, 65, ease_out((t - seg_start("fin_a")) / 1.4))
    return 65

def act_race(img, t):
    d = ImageDraw.Draw(img)
    s0 = seg_start("race"); k = ease_out((t - s0) / 0.6)
    L, R, T, B = 150, 930, VCY - 270, VCY + 290
    YM = 420000
    d.line([(L, T), (L, B), (L + (R - L) * k, B)], fill=(90, 100, 95), width=5)
    if k > 0.9:
        for age in (25, 35, 45, 55, 65):
            text_c(d, (L + (R - L) * (age - 25) / 40, B + 45), str(age), font(F_MED, 38), GREY)
    t7 = tok_time("race", 2)
    if t > t7:
        pop_text(img, (L + 160, T + 40), "7% / yr", F_NUM, 60, GREEN, scale=ease_back((t - t7) / 0.35))
    age = chart_age(t)
    def pt(a, f): return (L + (R - L) * (a - 25) / 40, B - (B - T - 40) * f(a) / YM)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ends = {}
    for f, col, start in ((jack_val, JACK, 35), (emma_val, EMMA, 25)):
        if age <= start + 0.05:
            ends[col] = pt(max(age, 25), f); continue
        pts = [pt(a, f) for a in np.linspace(25, age, 90)]
        ld.line(pts, fill=col + (255,), width=12, joint="curve")
        ends[col] = pts[-1]
    # shade Emma's contribution window
    ld.rectangle([L + (R - L) * 0 / 40, B - 14, L + (R - L) * min(age - 25, 10) / 40, B], fill=EMMA + (160,))
    if age > 35:
        ld.rectangle([L + (R - L) * 10 / 40, B - 28, L + (R - L) * (age - 25) / 40, B - 14], fill=JACK + (160,))
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    for col, (x, y) in ends.items():
        d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=col)
    ev, jv = emma_val(age), jack_val(age)
    final = scene_at(t) == "fin"
    if final:
        pass
    else:
        pop_text(img, (W / 2 - 250, T - 130), kfmt(round(ev, -3)), F_NUM, 96, EMMA)
        pop_text(img, (W / 2 + 250, T - 130), kfmt(round(jv, -3)), F_NUM, 96, JACK)
        text_c(d, (W / 2 - 250, T - 55), "EMMA", font(F_MED, 36), GREY)
        text_c(d, (W / 2 + 250, T - 55), "JACK", font(F_MED, 36), GREY)
        text_c(d, (W / 2, T - 235), f"AGE {int(round(age))}", font(F_NUM, 56), WHITE)
    if final:
        te = tok_time("fin", 1); tj = tok_time("fin", 3)
        if t > te - 0.1:
            sc = ease_back((t - te + 0.1) / 0.4); sh = max(0, 1 - (t - te) / 0.35) * 14
            pop_text(img, (W / 2 - 250 + math.sin(t * 90) * sh, T - 140), "$379K", F_NUM, 110, EMMA, scale=sc, glow=EMMA)
            text_c(d, (W / 2 - 250, T - 55), "EMMA", font(F_MED, 36), GREY)
        if t > tj - 0.1:
            sc = ease_back((t - tj + 0.1) / 0.4)
            pop_text(img, (W / 2 + 250, T - 140), "$340K", F_NUM, 110, JACK, scale=sc)
            text_c(d, (W / 2 + 250, T - 55), "JACK", font(F_MED, 36), GREY)

def act_why(img, t):
    s0 = seg_start("why"); k = ease_back((t - s0) / 0.4)
    ttime = tok_time("why", 6)
    if t < ttime:
        person(img, W / 2, VCY - 20, 1.3 * k, EMMA, crown=ease_back((t - s0 - 0.2) / 0.4))
        pop_text(img, (W / 2, VCY - 420), "EMMA WINS", F_NUM, 120, GOLD, scale=k, glow=GOLD)
        if t > tok_time("why", 3):
            pop_text(img, (W / 2, VCY + 330), "WITH 1/3 OF THE MONEY", F_NUM, 64, WHITE, scale=ease_back((t - tok_time("why", 3)) / 0.35))
    else:
        u = ease_back((t - ttime) / 0.4)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        r = 260 * u; cx, cy = W / 2, VCY - 40
        if r > 4:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 34, 44, 255), outline=(255, 255, 255, 255), width=max(2, int(14 * u)))
            for i in range(12):
                a = i * math.pi / 6
                d.line([(cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82), (cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92)], fill=(200, 200, 210, 255), width=8)
            am = (t - ttime) * 6; ah = (t - ttime) * 0.8
            d.line([(cx, cy), (cx + math.sin(am) * r * 0.75, cy - math.cos(am) * r * 0.75)], fill=YEL + (255,), width=12)
            d.line([(cx, cy), (cx + math.sin(ah) * r * 0.5, cy - math.cos(ah) * r * 0.5)], fill=(255, 255, 255, 255), width=16)
            d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 255, 255, 255))
        img.alpha_composite(lay)
        pop_text(img, (W / 2, VCY - 420), "TIME", F_NUM, 160, YEL, scale=u, glow=YEL)

def calendar(img, cx, cy, s, top, big, col, cross=0.0, tick=0.0):
    if s < 0.03: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 380 * s, 380 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=40 * s, fill=(245, 245, 248, 255))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 110 * s], radius=40 * s, fill=col + (255,))
    d.rectangle([cx - w / 2, cy - h / 2 + 60 * s, cx + w / 2, cy - h / 2 + 110 * s], fill=col + (255,))
    for dx in (-0.25, 0.25):
        d.rounded_rectangle([cx + dx * w - 12 * s, cy - h / 2 - 30 * s, cx + dx * w + 12 * s, cy - h / 2 + 30 * s], radius=10 * s, fill=(90, 95, 110, 255))
    img.alpha_composite(lay)
    pop_text(img, (cx, cy - h / 2 + 58 * s), top, F_NUM, 40 * s, WHITE)
    pop_text(img, (cx, cy + 50 * s), big, F_NUM, 92 * s, (30, 34, 44))
    d = ImageDraw.Draw(img)
    if cross > 0:
        u = clamp(cross)
        d.line([(cx - w / 2, cy - h / 2), (cx - w / 2 + w * u, cy - h / 2 + h * u)], fill=RED, width=int(22 * s))
        if u >= 1:
            d.line([(cx + w / 2, cy - h / 2), (cx - w / 2, cy + h / 2)], fill=RED, width=int(22 * s))
    if tick > 0:
        u = clamp(tick)
        p1 = (cx - 120 * s, cy + 40 * s); p2 = (cx - 30 * s, cy + 130 * s); p3 = (cx + 150 * s, cy - 60 * s)
        if u < 0.4:
            q = u / 0.4; d.line([p1, (lerp(p1[0], p2[0], q), lerp(p1[1], p2[1], q))], fill=GREEN, width=int(30 * s))
        else:
            q = (u - 0.4) / 0.6
            d.line([p1, p2, (lerp(p2[0], p3[0], q), lerp(p2[1], p3[1], q))], fill=GREEN, width=int(30 * s), joint="curve")

def act_today(img, t):
    s0 = seg_start("twist"); k = ease_back((t - s0) / 0.4)
    in_pick = scene_at(t) == "pick"
    tago = tok_time("twist", 4)
    if not in_pick:
        calendar(img, W / 2, VCY - 40, 1.25 * k, "10 YEARS AGO", "2016", (120, 125, 140),
                 cross=(t - tago - 0.2) / 0.3 if t > tago + 0.2 else 0)
        pop_text(img, (W / 2, VCY - 430), "BEST TIME TO START", F_NUM, 80, WHITE, scale=k)
    else:
        sp = seg_start("pick"); u = ease_back((t - sp) / 0.4)
        calendar(img, W / 2 - 250, VCY + 30, 0.6, "THEN", "2016", (90, 95, 110), cross=1.0)
        ttd = tok_time("pick", 2)
        calendar(img, W / 2 + 150, VCY - 20, 1.0 * u, "TODAY", "2026", GREEN,
                 tick=(t - ttd - 0.1) / 0.45 if t > ttd + 0.1 else 0)
        pop_text(img, (W / 2, VCY - 430), "SECOND BEST TIME", F_NUM, 84, GREEN, scale=u, glow=GREEN)

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

ACTS = {"hook": act_hook, "story": act_story, "put": act_put, "race": act_race, "why": act_why,
        "today": act_today, "cta": act_cta}

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
    f = font(F_MED, 40); label = "THE TWIN MATH"
    l, tp, r, b = f.getbbox(label); pw = r - l + 70
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([W / 2 - pw / 2, 175, W / 2 + pw / 2, 245], radius=35, fill=(255, 255, 255, 28), outline=(255, 255, 255, 200), width=3)
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    text_c(d, (W / 2, 211), label, f, WHITE)
    if seg_start("race") <= t < seg_end("why") + 0.3:
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
