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

