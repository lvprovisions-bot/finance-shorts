# ---------- car-payment acts (spliced into render.py) ----------
ORANGE = (255, 150, 50)
GOLD = (255, 200, 60)
CAR_COLS = [(230, 70, 70), (60, 130, 240), (250, 170, 40), (150, 90, 230)]

def heart(d, cx, cy, s, col):
    pts = []
    for i in range(100):
        a = i / 100 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * s, cy - y * s))
    d.polygon(pts, fill=col)

def money(v): return "${:,.0f}".format(v)
def counter(t, t0, t1, v0, v1): return lerp(v0, v1, ease_out((t - t0) / max(1e-3, t1 - t0)))
def growth(year): return ANNUAL * ((1.07 ** year - 1) / 0.07)

def draw_car(img, cx, cy, s, col, t, alpha=1.0, spin=True):
    """Side-view car, ~520px wide at s=1."""
    if s < 0.03 or alpha <= 0.01:
        return
    a = int(255 * alpha)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # shadow
    d.ellipse([cx - 250 * s, cy + 95 * s, cx + 250 * s, cy + 125 * s], fill=(0, 0, 0, int(a * 0.45)))
    # cabin
    d.polygon([(cx - 140 * s, cy - 30 * s), (cx - 80 * s, cy - 110 * s), (cx + 90 * s, cy - 110 * s), (cx + 160 * s, cy - 30 * s)], fill=col + (a,))
    # windows
    d.polygon([(cx - 115 * s, cy - 35 * s), (cx - 70 * s, cy - 95 * s), (cx + 2 * s, cy - 95 * s), (cx + 2 * s, cy - 35 * s)], fill=(170, 210, 240, a))
    d.polygon([(cx + 18 * s, cy - 35 * s), (cx + 18 * s, cy - 95 * s), (cx + 82 * s, cy - 95 * s), (cx + 132 * s, cy - 35 * s)], fill=(170, 210, 240, a))
    # body
    d.rounded_rectangle([cx - 255 * s, cy - 40 * s, cx + 255 * s, cy + 70 * s], radius=40 * s, fill=col + (a,))
    shade = tuple(max(0, c - 45) for c in col)
    d.rounded_rectangle([cx - 255 * s, cy + 30 * s, cx + 255 * s, cy + 70 * s], radius=20 * s, fill=shade + (a,))
    # lights
    d.rounded_rectangle([cx + 225 * s, cy - 20 * s, cx + 252 * s, cy + 5 * s], radius=6 * s, fill=(255, 240, 180, a))
    d.rounded_rectangle([cx - 252 * s, cy - 20 * s, cx - 228 * s, cy + 5 * s], radius=6 * s, fill=(255, 90, 90, a))
    # door line + handle
    d.line([(cx + 10 * s, cy - 35 * s), (cx + 10 * s, cy + 40 * s)], fill=shade + (a,), width=max(1, int(4 * s)))
    d.rounded_rectangle([cx - 40 * s, cy - 12 * s, cx - 10 * s, cy - 4 * s], radius=3 * s, fill=shade + (a,))
    # wheels
    for wx in (-150, 150):
        x0 = cx + wx * s; y0 = cy + 70 * s; r = 58 * s
        d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=(25, 25, 30, a))
        d.ellipse([x0 - r * 0.55, y0 - r * 0.55, x0 + r * 0.55, y0 + r * 0.55], fill=(190, 195, 205, a))
        ang = t * 8 if spin else 0
        for k in range(5):
            th = ang + k * 2 * math.pi / 5
            d.line([(x0, y0), (x0 + math.cos(th) * r * 0.5, y0 + math.sin(th) * r * 0.5)], fill=(110, 115, 125, a), width=max(1, int(6 * s)))
    img.alpha_composite(lay)

def draw_tag(img, cx, cy, s, text, col, tcol=WHITE, string_to=None, wobble=0.0):
    if s < 0.03:
        return
    f = font(F_NUM, 86 * s)
    l, tp, r, b = f.getbbox(text)
    tw = r - l + 120 * s; th = 150 * s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if string_to:
        d.line([string_to, (cx - tw / 2 + 40 * s, cy)], fill=(230, 230, 230, 200), width=max(2, int(5 * s)))
    x0 = cx - tw / 2
    d.polygon([(x0, cy), (x0 + 50 * s, cy - th / 2), (cx + tw / 2, cy - th / 2), (cx + tw / 2, cy + th / 2), (x0 + 50 * s, cy + th / 2)], fill=col + (255,))
    d.ellipse([x0 + 28 * s, cy - 12 * s, x0 + 52 * s, cy + 12 * s], fill=BG + (255,))
    img.alpha_composite(lay)
    pop_text(img, (cx + 25 * s + math.sin(wobble) * 2, cy), text, F_NUM, 86 * s, tcol)

VCY = 820

def act_hook(img, t):
    s0 = seg_start("hook"); k = ease_back((t - s0 + 0.1) / 0.45)
    tm = tok_time("hook", 4)
    in_h2 = scene_at(t) == "hook2"
    tcar = tok_time("hook2", 1) if "hook2" in SEG else 1e9
    tpay = tok_time("hook2", 3) if "hook2" in SEG else 1e9
    dim = in_h2 and t > tcar
    draw_car(img, W / 2, VCY - 40, 1.35 * k, CAR_COLS[0], t, alpha=0.35 if dim else 1.0)
    if dim and t < tpay:
        d = ImageDraw.Draw(img); u = ease_out((t - tcar) / 0.25)
        d.line([(W / 2 - 300, VCY - 200), (W / 2 - 300 + 600 * u, VCY - 200 + 330 * u)], fill=RED, width=22)
    tag_s = 0.85 * k
    if t > tpay:
        tag_s = lerp(0.85, 1.25, ease_back((t - tpay) / 0.35))
    draw_tag(img, W / 2 + 60, VCY + 210, tag_s, "$500/mo", ORANGE if not t > tpay else GOLD,
             tcol=WHITE if not t > tpay else BG, string_to=(W / 2 + 200, VCY + 20))
    if t > tm and not in_h2:
        sc = ease_back((t - tm) / 0.4); shake = max(0, 1 - (t - tm) / 0.4) * 16
        pop_text(img, (W / 2 + math.sin(t * 90) * shake, VCY - 380), "MILLIONAIRE?", F_NUM, 120, GOLD, scale=sc, glow=GOLD)

def act_setup(img, t):
    s0 = seg_start("setup"); k = ease_back((t - s0) / 0.4)
    draw_car(img, W / 2, VCY - 360, 0.75 * k, CAR_COLS[0], t)
    t500 = tok_time("setup", 2); t6k = tok_time("setup", 7)
    if t > t500 - 0.1:
        draw_tag(img, W / 2, VCY - 110, ease_back((t - t500 + 0.1) / 0.35), "$500/mo", ORANGE)
    # 12 chips filling for the year
    n = int(12 * ease_out((t - tok_time("setup", 6)) / max(0.3, t6k - tok_time("setup", 6) + 0.4))) if t > tok_time("setup", 6) else 0
    d = ImageDraw.Draw(img)
    for i in range(12):
        r, c = divmod(i, 6)
        x = W / 2 + (c - 2.5) * 140; y = VCY + 90 + r * 95
        filled = i < n
        d.rounded_rectangle([x - 60, y - 36, x + 60, y + 36], radius=18, fill=(ORANGE if filled else (40, 44, 52)))
        text_c(d, (x, y), "$500", font(F_NUM, 32), BG if filled else (90, 96, 108))
    if t > t6k:
        sc = ease_back((t - t6k) / 0.35)
        pop_text(img, (W / 2, VCY + 340), "$6,000 / YEAR", F_NUM, 96, YEL, scale=sc, glow=YEL)

def ring(img, cx, cy, r, t, col, alpha=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    a0 = (t * 120) % 360
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 300, fill=col + (int(255 * alpha),), width=18)
    th = math.radians(a0 + 300)
    hx, hy = cx + r * math.cos(th), cy + r * math.sin(th)
    tang = th + math.pi / 2
    pts = [(hx + 44 * math.cos(tang), hy + 44 * math.sin(tang)),
           (hx + 26 * math.cos(th), hy + 26 * math.sin(th)),
           (hx - 26 * math.cos(th), hy - 26 * math.sin(th))]
    d.polygon(pts, fill=col + (int(255 * alpha),))
    img.alpha_composite(lay)

def act_loop(img, t):
    s0 = seg_start("cycle"); d = ImageDraw.Draw(img)
    tpaid = tok_time("cycle", 3); tnew = tok_time("cycle", 8)
    tcar3 = tok_time("cycle2", 0); tsame = tok_time("cycle2", 3); tfor = tok_time("cycle2", 4)
    loan = 1 + (t > tnew) + (t > tcar3)
    col = CAR_COLS[loan - 1]
    # slide-in on each new car
    last = {1: s0, 2: tnew, 3: tcar3}[loan]
    sl = ease_out((t - last) / 0.35)
    cx = lerp(W + 300, W / 2, sl) if loan > 1 else W / 2
    if t > tfor:
        ring(img, W / 2, VCY - 60, 380, t, RED)
    draw_car(img, cx, VCY - 60, 1.0 * (ease_back((t - s0) / 0.4) if loan == 1 else 1), col, t)
    pop_text(img, (W / 2, VCY - 380), f"LOAN #{loan}", F_NUM, 100, WHITE, scale=ease_back((t - last) / 0.35))
    # 5-year progress bar for loan 1
    if loan == 1:
        u = ease_out((t - s0) / max(0.4, tpaid - s0))
        L, R, y = 200, 880, VCY + 170
        d.rounded_rectangle([L, y - 22, R, y + 22], radius=22, fill=(45, 50, 60))
        d.rounded_rectangle([L, y - 22, L + (R - L) * u, y + 22], radius=22, fill=GREEN if t > tpaid else ORANGE)
        text_c(d, (W / 2, y + 70), "5 YEARS OF PAYMENTS", font(F_MED, 38), GREY)
        if t > tpaid:
            pop_text(img, (W / 2, VCY + 290), "PAID OFF!", F_NUM, 90, GREEN, scale=ease_back((t - tpaid) / 0.35), glow=GREEN)
    else:
        draw_tag(img, W / 2, VCY + 210, 0.9 * (ease_back((t - tsame) / 0.35) * 0.25 + 0.75 if t > tsame else 0.75), "$500/mo", ORANGE)
    if t > tfor:
        pop_text(img, (W / 2, VCY + 360), "FOREVER", F_NUM, 110, RED, scale=ease_back((t - tfor) / 0.35), glow=RED)

def act_chart(img, t):
    d = ImageDraw.Draw(img)
    s0 = seg_start("invest"); k = ease_out((t - s0) / 0.6)
    L, R, T, B = 150, 930, VCY - 360, VCY + 290
    XM = 42
    d.line([(L, T), (L, B), (L + (R - L) * k, B)], fill=(90, 100, 95), width=5)
    if k > 0.9:
        for yr in (10, 20, 30, 40):
            text_c(d, (L + (R - L) * yr / XM, B + 45), f"{yr} yrs", font(F_MED, 36), GREY)
    t7 = tok_time("invest", 8)
    if t > t7:
        pop_text(img, (L + 175, T + 30), "7% / yr", F_NUM, 72, GREEN, scale=ease_back((t - t7) / 0.35))
    if t < seg_start("y10"): yrs = 0
    elif t < seg_start("y20"): yrs = lerp(0, 10, ease_out((t - seg_start("y10")) / 1.4))
    elif t < seg_start("y30"): yrs = lerp(10, 20, ease_out((t - seg_start("y20")) / 1.2))
    elif t < seg_start("y40a"): yrs = lerp(20, 30, ease_out((t - seg_start("y30")) / 1.2))
    elif t < seg_start("y40"): yrs = lerp(30, 40, ease_out((t - seg_start("y40a")) / 1.5))
    else: yrs = 40
    def pt(yr): return (L + (R - L) * yr / XM, B - (B - T - 60) * growth(yr) / YMAX)
    if yrs > 0.05:
        pts = [pt(y) for y in np.linspace(0, yrs, 90)]
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.polygon(pts + [(pts[-1][0], B), (L, B)], fill=GREEN + (55,))
        ld.line(pts, fill=GREEN + (255,), width=12, joint="curve")
        cp = [(L + (R - L) * y / XM, B - (B - T - 60) * ANNUAL * y / YMAX) for y in np.linspace(0, yrs, 20)]
        ld.line(cp, fill=(200, 200, 200, 140), width=5)
        img.alpha_composite(lay)
        x, y = pts[-1]; d = ImageDraw.Draw(img)
        d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=WHITE)
        if scene_at(t) == "y40":
            sc = ease_back((t - seg_start("y40")) / 0.4)
            shake = max(0, 1 - (t - seg_start("y40")) / 0.35) * 16
            pop_text(img, (W / 2 + math.sin(t * 90) * shake, T - 110), FINAL, F_NUM, 170, GOLD, scale=sc, glow=GOLD)
        else:
            pop_text(img, (W / 2, T - 100), money(round(growth(yrs) / 1000) * 1000), F_NUM, 140, WHITE)
    else:
        pop_text(img, (W / 2, T - 100), "USED CAR + INVEST", F_NUM, 84, WHITE, scale=ease_back((t - s0) / 0.4))

def act_split(img, t):
    d = ImageDraw.Draw(img)
    L, R = 140, 940; y0, y1 = VCY - 120, VCY + 120
    tot = PUT + GROW
    tin = tok_time("split", 2); tgr = tok_time("split", 4)
    k1 = ease_out((t - seg_start("split") + 0.1) / 0.8); k2 = ease_out((t - tgr + 0.1) / 0.8)
    xm = L + (R - L) * PUT / tot
    d.rounded_rectangle([L, y0, R, y1], radius=26, outline=(70, 80, 75), width=4)
    if k1 > 0:
        d.rounded_rectangle([L, y0, L + max(40, (xm - L) * k1), y1], radius=26, fill=(170, 175, 172))
    if k2 > 0:
        d.rectangle([xm, y0, xm + (R - xm) * k2, y1], fill=GREEN)
        d.rounded_rectangle([xm + (R - xm) * k2 - 40, y0, xm + (R - xm) * k2, y1], radius=26, fill=GREEN)
    if t > tin - 0.1:
        a = ease_back((t - tin + 0.1) / 0.35)
        pop_text(img, (L + 150, y0 - 120), "$240K", F_NUM, 100, WHITE, scale=a)
        pop_text(img, (L + 150, y0 - 45), "YOU PUT IN", F_MED, 36, GREY, scale=a)
    if k2 > 0:
        pop_text(img, ((xm + R) / 2, y1 + 110), "$958K", F_NUM, 150, GREEN, scale=ease_back((t - tgr) / 0.35), glow=GREEN)
        pop_text(img, ((xm + R) / 2, y1 + 210), "COMPOUND INTEREST", F_MED, 40, GREEN,
                 scale=ease_back((t - tok_time("split", 5)) / 0.35))

def sparkle(d, cx, cy, r, col):
    d.polygon([(cx, cy - r), (cx + r * 0.25, cy - r * 0.25), (cx + r, cy), (cx + r * 0.25, cy + r * 0.25),
               (cx, cy + r), (cx - r * 0.25, cy + r * 0.25), (cx - r, cy), (cx - r * 0.25, cy - r * 0.25)], fill=col)

def act_nice(img, t):
    s0 = seg_start("twist"); k = ease_back((t - s0) / 0.4)
    draw_car(img, W / 2, VCY - 20, 1.3 * k, (40, 44, 56), t, spin=False)
    d = ImageDraw.Draw(img)
    tn = tok_time("twist", 3)
    if t > tn:
        u = ease_back((t - tn) / 0.35)
        for i, (dx, dy, r) in enumerate([(-260, -170, 40), (240, -150, 52), (300, 40, 30), (-320, 30, 34), (40, -240, 28)]):
            tw = 0.7 + 0.3 * math.sin(t * 8 + i)
            sparkle(d, W / 2 + dx, VCY + dy, r * u * tw, (255, 240, 180))
        pop_text(img, (W / 2, VCY - 400), "ENJOY IT", F_NUM, 110, WHITE, scale=u)
    else:
        pop_text(img, (W / 2, VCY - 400), "NICE CARS ARE OK", F_NUM, 80, WHITE, scale=k)

def act_tag(img, t):
    s0 = seg_start("pick"); k = ease_back((t - s0) / 0.4)
    tc = tok_time("pick", 4)
    if t < tc:
        draw_tag(img, W / 2, VCY - 40, 1.6 * k, "$500/mo", ORANGE)
        pop_text(img, (W / 2, VCY - 330), "THE REAL PRICE?", F_NUM, 86, WHITE, scale=k)
    else:
        u = (t - tc) / 0.3
        if u < 0.5:  # flip: squash horizontally via scale
            draw_tag(img, W / 2, VCY - 40, 1.6 * (1 - u * 2) + 0.05, "$500/mo", ORANGE)
        else:
            sc = ease_back((u - 0.5) * 2)
            draw_tag(img, W / 2, VCY - 40, 1.6 * sc, "$1.2M", GOLD, tcol=BG)
            pop_text(img, (W / 2, VCY - 330), "THE REAL PRICE", F_NUM, 86, GOLD, scale=1, glow=GOLD)

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

ACTS = {"hook": act_hook, "setup": act_setup, "loop": act_loop, "chart": act_chart, "split": act_split,
        "nice": act_nice, "tag": act_tag, "cta": act_cta}

