"""Render 'Same Raise' Short: 1080x1920 @30fps, frames piped to ffmpeg."""
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

ACT = {"hook": "hook", "setup": "setup", "mia": "mia", "sam": "sam", "grow": "grow",
       "fin_a": "grow", "fin": "grow", "q": "q"}

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
ACT_BG = {"hook": "purple", "setup": "blue", "mia": "red", "sam": "blue", "grow": "green", "q": "purple"}

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

# ---------- same-raise acts (spliced into render.py) ----------
MIA = (255, 110, 170)
SAM = (70, 160, 255)
GOLD = (255, 200, 60)
ORANGE = (255, 150, 50)

def money(v): return "${:,.0f}".format(v)
def kfmt(v): return "${:,.0f}K".format(v / 1000)
def fv(a, n): return a * ((1.07 ** n - 1) / 0.07) if n > 0 else 0.0
def sam_val(yrs): return fv(3000, yrs)

VCY = 820
LX, RX = W / 2 - 230, W / 2 + 230   # Mia left, Sam right

def person(img, cx, cy, s, col, alpha=1.0, crown=0.0):
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

def duo(img, t, s=1.15, mia_alpha=1.0, sam_alpha=1.0, crown=0.0, dy=0):
    person(img, LX, VCY - 40 + dy, s, MIA, alpha=mia_alpha)
    person(img, RX, VCY - 40 + dy, s, SAM, alpha=sam_alpha, crown=crown)
    d = ImageDraw.Draw(img)
    text_c(d, (LX, VCY + 170 + dy * 1.4), "MIA", font(F_NUM, 60), MIA)
    text_c(d, (RX, VCY + 170 + dy * 1.4), "SAM", font(F_NUM, 60), SAM)

def act_hook(img, t):
    # Frame 0: both characters, headline and "WHO WINS?" already on screen (no pop-in).
    pulse = 1 + 0.04 * math.sin(t * 6)
    duo(img, t)
    pop_text(img, (W / 2, VCY - 470), "SAME JOB. SAME RAISE.", F_NUM, 78, WHITE)
    th = tok_time("hook", 5); tz = tok_time("hook", 7)
    if t < th:
        pop_text(img, (W / 2, VCY - 350), "WHO WINS?", F_NUM, 130, YEL, scale=pulse, glow=YEL)
        for x in (LX, RX):
            pop_text(img, (x, VCY + 270), "?", F_NUM, 110, GREY)
    else:
        pop_text(img, (W / 2, VCY - 350), "30 YEARS LATER", F_NUM, 100, YEL)
        sc = ease_back((t - th) / 0.35); sh = max(0, 1 - (t - th) / 0.35) * 14
        pop_text(img, (RX + math.sin(t * 90) * sh, VCY + 270), "$283K", F_NUM, 110, GREEN, scale=sc, glow=GREEN)
        if t > tz - 0.05:
            pop_text(img, (LX, VCY + 270), "$0", F_NUM, 110, RED, scale=ease_back((t - tz + 0.05) / 0.35))
        else:
            pop_text(img, (LX, VCY + 270), "?", F_NUM, 110, GREY)

def badge(img, cx, cy, s, text, col):
    if s < 0.03: return
    f = font(F_NUM, 56 * s); l, tp, r, b = f.getbbox(text)
    w, h = r - l + 60 * s, 96 * s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2, fill=col + (255,))
    img.alpha_composite(lay)
    pop_text(img, (cx, cy), text, F_NUM, 56 * s, BG)

def act_setup(img, t):
    s0 = seg_start("setup"); duo(img, t)
    pop_text(img, (W / 2, VCY - 470), "BOTH GET A RAISE", F_NUM, 84, WHITE, scale=ease_back((t - s0) / 0.35))
    tr = tok_time("setup", 2)
    if t > tr - 0.1:
        k = ease_back((t - tr + 0.1) / 0.35)
        badge(img, LX, VCY - 300, k, "+$500/mo", GREEN)
        badge(img, RX, VCY - 300, k, "+$500/mo", GREEN)

def house(d, cx, cy, s, col):
    d.polygon([(cx - 90 * s, cy - 20 * s), (cx, cy - 100 * s), (cx + 90 * s, cy - 20 * s)], fill=col)
    d.rectangle([cx - 70 * s, cy - 20 * s, cx + 70 * s, cy + 80 * s], fill=col)
    d.rectangle([cx - 18 * s, cy + 20 * s, cx + 18 * s, cy + 80 * s], fill=BG)
    for dx in (-45, 45):
        d.rectangle([cx + (dx - 15) * s, cy, cx + (dx + 15) * s, cy + 28 * s], fill=(255, 230, 150))

def car_icon(d, cx, cy, s, col):
    d.polygon([(cx - 60 * s, cy - 10 * s), (cx - 35 * s, cy - 50 * s), (cx + 40 * s, cy - 50 * s), (cx + 70 * s, cy - 10 * s)], fill=col)
    d.rounded_rectangle([cx - 110 * s, cy - 15 * s, cx + 110 * s, cy + 35 * s], radius=18 * s, fill=col)
    for dx in (-60, 60):
        d.ellipse([cx + (dx - 24) * s, cy + 12 * s, cx + (dx + 24) * s, cy + 60 * s], fill=(25, 25, 30))

def act_mia(img, t):
    s0 = seg_start("mia"); k = ease_back((t - s0) / 0.4)
    person(img, W / 2, VCY - 60, 1.2 * k, MIA)
    d = ImageDraw.Draw(img)
    tc = tok_time("mia", 3); ta = tok_time("mia", 5); tg = tok_time("mia", 7)
    if t > tc - 0.1:
        u = ease_back((t - tc + 0.1) / 0.35)
        car_icon(d, W / 2 - 300, VCY - 260, 0.9 * u, (230, 70, 70))
    if t > ta - 0.1:
        u = ease_back((t - ta + 0.1) / 0.35)
        house(d, W / 2 + 300, VCY - 260, 1.0 * u, (150, 120, 230))
    # money flying away
    if t > tok_time("mia", 6):
        for i in range(6):
            ph = (t - tok_time("mia", 6)) * 1.4 + i * 0.17
            x = W / 2 + math.sin(i * 2.1) * 160 + ph * (160 if i % 2 else -160)
            y = VCY + 120 - ph * 520
            if 200 < y < 1400:
                d.rounded_rectangle([x - 46, y - 24, x + 46, y + 24], radius=8, fill=GREEN)
                text_c(d, (x, y), "$", font(F_NUM, 36), BG)
    if t > tg - 0.05:
        pop_text(img, (W / 2, VCY + 260), "SAVED: $0", F_NUM, 110, RED, scale=ease_back((t - tg + 0.05) / 0.35), glow=RED)
    pop_text(img, (W / 2, VCY - 470), "MIA SPENDS IT ALL", F_NUM, 80, MIA, scale=k)

def act_sam(img, t):
    s0 = seg_start("sam"); k = ease_back((t - s0) / 0.4)
    person(img, W / 2, VCY - 120, 1.0 * k, SAM)
    pop_text(img, (W / 2, VCY - 470), "SAM SPLITS IT", F_NUM, 80, SAM, scale=k)
    d = ImageDraw.Draw(img)
    L, R, y0, y1 = 140, 940, VCY + 120, VCY + 260
    th = tok_time("sam", 1); ti = tok_time("sam", 2)
    d.rounded_rectangle([L, y0, R, y1], radius=30, fill=(40, 44, 54))
    xm = (L + R) / 2
    if t > th - 0.1:
        u = ease_out((t - th + 0.1) / 0.4)
        d.rounded_rectangle([L, y0, L + max(60, (xm - L) * u), y1], radius=30, fill=ORANGE)
        if u > 0.7:
            text_c(d, ((L + xm) / 2, (y0 + y1) / 2), "$250 ENJOY", font(F_NUM, 50), BG)
    if t > ti - 0.1:
        u = ease_out((t - ti + 0.1) / 0.4)
        d.rounded_rectangle([xm, y0, xm + max(60, (R - xm) * u), y1], radius=30, fill=GREEN)
        d.rectangle([xm, y0, xm + 30, y1], fill=GREEN)
        if u > 0.7:
            text_c(d, ((xm + R) / 2, (y0 + y1) / 2), "$250 INVEST", font(F_NUM, 50), BG)

def chart_years(t):
    t10 = tok_time("grow", 0); t20 = tok_time("grow", 2)
    if t < t10: return 0.5
    if t < t20: return lerp(0.5, 10, ease_out((t - t10) / 0.9))
    if t < seg_start("fin_a"): return lerp(10, 20, ease_out((t - t20) / 0.9))
    if t < seg_start("fin"): return lerp(20, 30, ease_out((t - seg_start("fin_a")) / 1.3))
    return 30

def act_grow(img, t):
    d = ImageDraw.Draw(img); s0 = seg_start("grow"); k = ease_out((t - s0) / 0.5)
    L, R, T, B = 150, 930, VCY - 250, VCY + 290; YM = 300000; XM = 32
    d.line([(L, T), (L, B), (L + (R - L) * k, B)], fill=(90, 100, 95), width=5)
    if k > 0.9:
        for yr in (0, 10, 20, 30):
            text_c(d, (L + (R - L) * yr / XM, B + 45), f"{yr} yrs", font(F_MED, 36), GREY)
    pop_text(img, (L + 160, T + 30), "7% / yr", F_NUM, 60, GREEN)
    yrs = chart_years(t)
    def pt(y, f): return (L + (R - L) * y / XM, B - (B - T - 40) * f(y) / YM)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    sp = [pt(y, sam_val) for y in np.linspace(0, yrs, 80)]
    ld.polygon(sp + [(sp[-1][0], B), (L, B)], fill=SAM + (50,))
    ld.line(sp, fill=SAM + (255,), width=12, joint="curve")
    ld.line([(L, B - 6), (L + (R - L) * yrs / XM, B - 6)], fill=MIA + (255,), width=12)
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    x, y = sp[-1]; d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=SAM)
    xm = L + (R - L) * yrs / XM; d.ellipse([xm - 16, B - 22, xm + 16, B + 10], fill=MIA)
    final = scene_at(t) == "fin"
    if final:
        tf = seg_start("fin"); sc = ease_back((t - tf) / 0.4); sh = max(0, 1 - (t - tf) / 0.35) * 14
        pop_text(img, (RX + math.sin(t * 90) * sh, T - 140), "$283K", F_NUM, 120, SAM, scale=sc, glow=SAM)
    else:
        pop_text(img, (RX, T - 140), kfmt(round(sam_val(yrs), -3)), F_NUM, 104, SAM)
    pop_text(img, (LX, T - 140), "$0", F_NUM, 104, MIA)
    text_c(d, (RX, T - 60), "SAM", font(F_MED, 38), GREY)
    text_c(d, (LX, T - 60), "MIA", font(F_MED, 38), GREY)

def act_q(img, t):
    # Mirrors the opening frame so the loop back to the start feels seamless.
    s0 = seg_start("q")
    duo(img, t, crown=ease_back((t - s0) / 0.4), dy=30, s=1.0)
    pop_text(img, (W / 2, VCY - 470), "SAME JOB. SAME RAISE.", F_NUM, 78, WHITE)
    pop_text(img, (W / 2, VCY - 350), "WHO ARE YOU?", F_NUM, 120, YEL, scale=ease_back((t - s0) / 0.35), glow=YEL)
    pop_text(img, (RX, VCY + 300), "$283K", F_NUM, 110, GREEN)
    pop_text(img, (LX, VCY + 300), "$0", F_NUM, 110, RED)

ACTS = {"hook": act_hook, "setup": act_setup, "mia": act_mia, "sam": act_sam, "grow": act_grow, "q": act_q}

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
    f = font(F_MED, 40); label = "THE RAISE MATH"
    l, tp, r, b = f.getbbox(label); pw = r - l + 70
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([W / 2 - pw / 2, 175, W / 2 + pw / 2, 245], radius=35, fill=(255, 255, 255, 28), outline=(255, 255, 255, 200), width=3)
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    text_c(d, (W / 2, 211), label, f, WHITE)
    if seg_start("grow") <= t < seg_end("fin") + 0.3:
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
