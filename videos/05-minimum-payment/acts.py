# ---------- minimum-payment acts (spliced into render.py) ----------
GOLD = (255, 200, 60)
CARD = (150, 40, 70)

# precomputed payoff schedules
def schedule(minimum=True):
    bal, r, out = 5000.0, 0.22 / 12, [(5000.0, 0.0)]
    while bal > 0.005:
        i = bal * r
        pay = max(25, i + 0.01 * bal) if minimum else 200
        pay = min(pay, bal + i); bal = bal + i - pay
        out.append((max(bal, 0.0), pay))
    return out
SCH_MIN = schedule(True); SCH_FIX = schedule(False)
def bal_at(years, sch=SCH_MIN):
    m = years * 12
    if m >= len(sch) - 1: return 0.0
    a = int(m); f = m - a
    return lerp(sch[a][0], sch[a + 1][0], f)
def pay_at(years):
    m = min(int(years * 12) + 1, len(SCH_MIN) - 1)
    return SCH_MIN[m][1]

def money(v): return "${:,.0f}".format(v)
VCY = 820

def credit_card(img, cx, cy, s, t, col=CARD, alpha=1.0, tilt=0.0):
    if s < 0.03: return
    w, h = 600 * s, 378 * s
    lay = Image.new("RGBA", (int(w + 80), int(h + 80)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    o = 40
    a = int(255 * alpha)
    d.rounded_rectangle([o, o, o + w, o + h], radius=34 * s, fill=col + (a,))
    # diagonal sheen
    for k in range(6):
        x0 = o + w * (0.35 + k * 0.06)
        d.polygon([(x0, o), (x0 + 40 * s, o), (x0 - w * 0.25 + 40 * s, o + h), (x0 - w * 0.25, o + h)], fill=(255, 255, 255, int(a * 0.035)))
    d.rounded_rectangle([o + 60 * s, o + 110 * s, o + 150 * s, o + 180 * s], radius=12 * s, fill=GOLD + (a,))
    d.line([(o + 60 * s, o + 145 * s), (o + 150 * s, o + 145 * s)], fill=(200, 150, 40, a), width=max(1, int(3 * s)))
    d.line([(o + 105 * s, o + 110 * s), (o + 105 * s, o + 180 * s)], fill=(200, 150, 40, a), width=max(1, int(3 * s)))
    # contactless waves
    for k in range(3):
        rr = (18 + k * 14) * s
        d.arc([o + 200 * s - rr, o + 145 * s - rr, o + 200 * s + rr, o + 145 * s + rr], -50, 50, fill=(255, 255, 255, int(a * 0.7)), width=max(1, int(5 * s)))
    f = font(F_MED, 40 * s)
    d.text((o + 60 * s, o + 240 * s), "****  ****  ****  4821", font=f, fill=(255, 255, 255, int(a * 0.9)))
    d.text((o + 60 * s, o + 305 * s), "22% APR", font=font(F_NUM, 34 * s), fill=(255, 220, 220, int(a * 0.85)))
    if tilt:
        lay = lay.rotate(tilt, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def act_hook(img, t):
    # everything key is fully on screen at frame 0 (no pop-in) so scrollers see the hook instantly
    bob = math.sin(t * 2.2) * 8
    credit_card(img, W / 2, VCY - 10 + bob, 1.1, t, tilt=-6)
    pop_text(img, (W / 2, VCY - 470), "PAYING THE MINIMUM?", F_NUM, 74, WHITE)
    pulse = 1 + 0.04 * math.sin(t * 6)
    pop_text(img, (W / 2, VCY - 340), "= 19 YEARS", F_NUM, 140, RED, scale=pulse, glow=RED)
    if "hook2" in SEG and t > tok_time("hook2", 2) - 0.05:
        tt = tok_time("hook2", 2)
        sc = ease_back((t - tt) / 0.4); sh = max(0, 1 - (t - tt) / 0.35) * 16
        pop_text(img, (W / 2 + math.sin(t * 90) * sh, VCY + 290), "$13,100 PAID", F_NUM, 110, RED, scale=sc)
    else:
        pop_text(img, (W / 2, VCY + 290), "$5,000 DEBT", F_NUM, 96, WHITE)

def act_how(img, t):
    s0 = seg_start("how"); d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.4)
    tsh = tok_time("how", 3)
    # years run forward from first "shrinks"
    yrs = 0 if t < tsh else 19.2 * ease_out((t - tsh) / max(1.0, seg_end("how") - tsh))
    base = VCY + 220; maxh = 520
    for cx, label, val, vmax, col in ((W / 2 - 200, "BALANCE", bal_at(yrs), 5000, (230, 90, 110)),
                                      (W / 2 + 200, "MINIMUM", pay_at(yrs), 142, ORANGE)):
        h = maxh * val / vmax * k
        d.rounded_rectangle([cx - 115, base - max(h, 8), cx + 115, base], radius=24, fill=col)
        text_c(d, (cx, base + 55), label, font(F_NUM, 48), col)
        pop_text(img, (cx, base - h - 60), money(val), F_NUM, 70, WHITE, scale=k)
    text_c(d, (W / 2, VCY - 470), f"YEAR {yrs:.0f}", font(F_NUM, 72), WHITE)
    if t > tok_time("how", 10):
        pop_text(img, (W / 2, VCY - 360), "...FOREVER", F_NUM, 90, RED, scale=ease_back((t - tok_time("how", 10)) / 0.35), glow=RED)
    elif t > tok_time("how", 8):
        pop_text(img, (W / 2, VCY - 360), "FEELS EASY", F_NUM, 90, GREEN, scale=ease_back((t - tok_time("how", 8)) / 0.35))

def act_first(img, t):
    s0 = seg_start("first"); d = ImageDraw.Draw(img)
    k = ease_back((t - s0) / 0.4)
    t142 = tok_time("first", 3); t92 = tok_time("first", 4)
    pop_text(img, (W / 2, VCY - 450), "1ST MINIMUM PAYMENT", F_NUM, 70, WHITE, scale=k)
    if t > t142 - 0.1:
        pop_text(img, (W / 2, VCY - 280), "$142", F_NUM, 200, ORANGE, scale=ease_back((t - t142 + 0.1) / 0.35), glow=ORANGE)
    L, R, y0, y1 = 140, 940, VCY - 60, VCY + 120
    d.rounded_rectangle([L, y0, R, y1], radius=30, fill=(48, 52, 62))
    if t > t92 - 0.1:
        u = ease_out((t - t92 + 0.1) / 0.6)
        xm = L + (R - L) * 91.67 / 141.67
        d.rounded_rectangle([L, y0, L + max(60, (xm - L) * u), y1], radius=30, fill=RED)
        if u > 0.6:
            d.rounded_rectangle([xm, y0, R, y1], radius=30, fill=GREEN)
            d.rectangle([xm, y0, xm + 40, y1], fill=GREEN)
            pop_text(img, ((L + xm) / 2, (y0 + y1) / 2), "$92", F_NUM, 90, WHITE)
            pop_text(img, ((xm + R) / 2, (y0 + y1) / 2), "$50", F_NUM, 70, BG)
            text_c(d, ((L + xm) / 2, y1 + 55), "INTEREST", font(F_NUM, 44), RED)
            text_c(d, ((xm + R) / 2, y1 + 55), "DEBT", font(F_NUM, 44), GREEN)

def act_slow(img, t):
    d = ImageDraw.Draw(img); s0 = seg_start("slow"); k = ease_out((t - s0) / 0.5)
    L, R, T, B = 150, 930, VCY - 300, VCY + 270
    XM = 20
    d.line([(L, T), (L, B), (L + (R - L) * k, B)], fill=(90, 100, 95), width=5)
    if k > 0.9:
        for yr in (0, 5, 10, 15, 19):
            text_c(d, (L + (R - L) * yr / XM, B + 45), f"{yr}", font(F_MED, 38), GREY)
        text_c(d, (W / 2, B + 95), "YEARS", font(F_MED, 32), (110, 116, 128))
    t5 = tok_time("slow", 1); t10 = tok_time("slow", 5)
    if t < t5: yrs = 0.3 * k
    elif t < t10: yrs = lerp(0.3, 5, ease_out((t - t5) / 0.8))
    else: yrs = lerp(5, 10, ease_out((t - t10) / 0.8))
    def pt(y, sch=SCH_MIN): return (L + (R - L) * y / XM, B - (B - T) * bal_at(y, sch) / 5000)
    # ghost of full curve
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.line([pt(y) for y in np.linspace(0, 19.2, 80)], fill=(255, 255, 255, 40), width=6)
    pts = [pt(y) for y in np.linspace(0, yrs, 60)]
    ld.line(pts, fill=RED + (255,), width=12, joint="curve")
    img.alpha_composite(lay); d = ImageDraw.Draw(img)
    x, y = pts[-1]; d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=WHITE)
    pop_text(img, (W / 2, T - 120), "STILL OWE " + money(round(bal_at(yrs), -2)), F_NUM, 86, WHITE)

def act_total(img, t):
    s0 = seg_start("total"); d = ImageDraw.Draw(img)
    tp = tok_time("total", 5); ti = tok_time("total", 6)
    k = ease_back((t - s0) / 0.4)
    if t < tp:
        pop_text(img, (W / 2, VCY - 300), "19 YEARS LATER", F_NUM, 100, WHITE, scale=k)
        credit_card(img, W / 2, VCY + 40, 0.85 * k, t, col=(70, 74, 86), tilt=-6)
        if t > tok_time("total", 3):
            pop_text(img, (W / 2, VCY + 40), "PAID OFF", F_NUM, 110, GREEN, scale=ease_back((t - tok_time("total", 3)) / 0.35))
        return
    base = VCY + 300; cx = W / 2 + 120; bw = 300; scale_h = 700 / 13100
    hb = 5000 * scale_h; hi = 8100 * scale_h * (ease_out((t - ti + 0.1) / 0.7) if t > ti - 0.1 else 0)
    d.rounded_rectangle([cx - bw / 2, base - hb, cx + bw / 2, base], radius=20, fill=(170, 175, 172))
    text_c(d, (cx - bw / 2 - 30, base - hb / 2), "BORROWED", font(F_MED, 34), GREY, anchor="rm")
    text_c(d, (cx, base - hb / 2), "$5,000", font(F_NUM, 64), BG)
    if hi > 2:
        d.rounded_rectangle([cx - bw / 2, base - hb - hi, cx + bw / 2, base - hb + 20], radius=20, fill=RED)
        d.rectangle([cx - bw / 2, base - hb - 10, cx + bw / 2, base - hb], fill=(170, 175, 172))
        if hi > 150:
            text_c(d, (cx, base - hb - hi / 2), "$8,100", font(F_NUM, 80), WHITE)
            text_c(d, (cx - bw / 2 - 30, base - hb - hi / 2), "INTEREST", font(F_NUM, 40), RED, anchor="rm")
    pop_text(img, (W / 2, VCY - 470), "TOTAL PAID: $13,100", F_NUM, 76, WHITE, scale=ease_back((t - tp) / 0.35))

def act_fix(img, t):
    s0 = seg_start("fix"); d = ImageDraw.Draw(img); k = ease_back((t - s0) / 0.4)
    L, R = 150, 930; XM = 20
    def xs(y): return L + (R - L) * y / XM
    rows = [("MINIMUM", RED, 19.2, VCY - 160, "19 YRS", "$8,100"),
            ("$200/MO", GREEN, 2.83, VCY + 70, "<3 YRS", "$1,750")]
    t200 = tok_time("fix", 2); tdf = tok_time("fix", 5); tint = tok_time("fix", 8)
    for i, (lab, col, yrs, y, ytxt, itxt) in enumerate(rows):
        show = k if i == 0 else (ease_back((t - t200) / 0.35) if t > t200 else 0)
        if show <= 0: continue
        text_c(d, (L, y - 70), lab, font(F_NUM, 50), col, anchor="lm")
        d.rounded_rectangle([L, y - 28, R, y + 28], radius=28, fill=(40, 44, 54))
        fill = 1 if i == 0 else (ease_out((t - tdf) / 0.5) if t > tdf else 0)
        if fill > 0:
            d.rounded_rectangle([L, y - 28, max(L + 56, L + (xs(yrs) - L) * fill), y + 28], radius=28, fill=col)
            text_c(d, (min(xs(yrs) + 30, R - 10) if i == 1 else R, y - 70), ytxt, font(F_NUM, 50), col, anchor="lm" if i == 1 else "rm")
        if t > tint:
            pop_text(img, (W / 2 + (-230 if i == 0 else 230), VCY + 330), itxt, F_NUM, 100, col, scale=ease_back((t - tint - i * 0.5) / 0.35))
    if t > tint:
        text_c(d, (W / 2, VCY + 240), "INTEREST PAID", font(F_MED, 40), GREY)
    for yr in (0, 5, 10, 15, 20):
        text_c(d, (xs(yr), VCY + 160), str(yr), font(F_MED, 34), (110, 116, 128))

def sparkle(d, cx, cy, r, col):
    d.polygon([(cx, cy - r), (cx + r * 0.25, cy - r * 0.25), (cx + r, cy), (cx + r * 0.25, cy + r * 0.25),
               (cx, cy + r), (cx - r * 0.25, cy + r * 0.25), (cx - r, cy), (cx - r * 0.25, cy - r * 0.25)], fill=col)

def act_save(img, t):
    s0 = seg_start("save"); d = ImageDraw.Draw(img)
    ts = tok_time("save", 1)
    u = ease_back((t - ts + 0.1) / 0.4) if t > ts - 0.1 else 0
    for i, (dx, dy, r) in enumerate([(-330, -260, 40), (320, -230, 52), (360, 60, 30), (-370, 40, 34), (0, -380, 28)]):
        tw = 0.7 + 0.3 * math.sin(t * 8 + i)
        sparkle(d, W / 2 + dx, VCY + dy, r * u * tw, (200, 255, 220))
    sh = max(0, 1 - (t - ts) / 0.35) * 14 if t > ts else 0
    pop_text(img, (W / 2 + math.sin(t * 90) * sh, VCY - 120), "$6,350", F_NUM, 220, GREEN, scale=u, glow=GREEN)
    pop_text(img, (W / 2, VCY + 40), "SAVED", F_NUM, 110, WHITE, scale=u)
    if t > tok_time("save", 3):
        pop_text(img, (W / 2, VCY + 230), "SAME DEBT.", F_NUM, 70, GREY, scale=ease_back((t - tok_time("save", 3)) / 0.35))
    if t > tok_time("save", 4):
        pop_text(img, (W / 2, VCY + 320), "DIFFERENT PAYMENT.", F_NUM, 70, YEL, scale=ease_back((t - tok_time("save", 4)) / 0.35))
    if t < ts - 0.1:
        credit_card(img, W / 2, VCY - 60, 0.9, t, tilt=-6)

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

ACTS = {"hook": act_hook, "how": act_how, "first": act_first, "slow": act_slow, "total": act_total,
        "fix": act_fix, "save": act_save, "cta": act_cta}

