# ---------------- L02 data (from model.py) ----------------
BASE = model_run()
R0 = model_run(apr=0.0001); R10 = model_run(apr=0.10)
ROWS = {r["y"]: r for r in BASE["rows"]}
MAX = (150, 110, 240)   # Max: purple
CASH_C, FIN_C, LEASE_C = NORA, MAX, THEO

def car(d, cx, cy, s, col, shine=True):
    if s < 0.05: return
    d.polygon([(cx - 105 * s, cy - 18 * s), (cx - 62 * s, cy - 80 * s), (cx + 58 * s, cy - 80 * s), (cx + 110 * s, cy - 18 * s)], fill=col)
    d.polygon([(cx - 80 * s, cy - 22 * s), (cx - 52 * s, cy - 68 * s), (cx - 4 * s, cy - 68 * s), (cx - 4 * s, cy - 22 * s)], fill=(180, 220, 250))
    d.polygon([(cx + 6 * s, cy - 22 * s), (cx + 6 * s, cy - 68 * s), (cx + 50 * s, cy - 68 * s), (cx + 84 * s, cy - 22 * s)], fill=(180, 220, 250))
    rrect(d, (cx - 175 * s, cy - 26 * s, cx + 175 * s, cy + 48 * s), 26 * s, fill=col)
    for dx in (-100, 100):
        d.ellipse([cx + (dx - 38) * s, cy + 14 * s, cx + (dx + 38) * s, cy + 90 * s], fill=(25, 25, 32))
        d.ellipse([cx + (dx - 16) * s, cy + 36 * s, cx + (dx + 16) * s, cy + 68 * s], fill=(150, 155, 165))
    d.rectangle([cx + 150 * s, cy - 8 * s, cx + 172 * s, cy + 6 * s], fill=(255, 236, 160))

def person3(d, cx, cy, s, col, who, t):
    person(d, cx, cy, s, col, "N" if who == "N" else "T", t)
    if who == "M":  # Max: cap
        hx, hy = cx, cy - 115 * s
        d.chord([hx - 68 * s, hy - 80 * s, hx + 68 * s, hy + 10 * s], 180, 360, fill=(60, 40, 120))
        d.rectangle([hx - 10 * s, hy - 40 * s, hx + 95 * s, hy - 28 * s], fill=(60, 40, 120))

TRIO = [("NORA", "pays cash", CASH_C, "N"), ("MAX", "finances", FIN_C, "M"), ("THEO", "leases", LEASE_C, "T")]
XS = [380, 960, 1540]

def sc_hook(c):
    d = c.d; t = c.t
    text(d, (W / 2, 110), "SAME $50K CAR. THREE WAYS TO PAY.", font(F_BLK, 66), WHITE)
    pulse = 1 + 0.03 * math.sin(t * 5)
    text(d, (W / 2, 205), "WHO'S RICHEST AFTER 9 YEARS?", font(F_BLK, int(80 * pulse)), YEL, stroke=4)
    for (nm, how, col, who), x in zip(TRIO, XS):
        car(d, x, 700, 0.95, col)
        person3(d, x, 520, 0.85, col, who, t + x)
        text(d, (x, 830), nm, font(F_BLK, 54), col); text(d, (x, 880), how, font(F_BLD, 34), WHITE)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4)
        if k > 0.05: pill(d, XS[2], 300, "-$56,000", font(F_BLK, int(46 * k)), WHITE, RED)
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        if k > 0.05: pill(d, XS[0], 300, "didn't win?!", font(F_BLK, int(40 * k)), (20, 20, 20), YEL)

def stat_card(c, x, y, k, big, label, src, col):
    d = c.d; kk = ease_back(k / 0.45)
    if kk < 0.05: return
    w, h = 470 * kk, 300 * kk
    card(d, (x - w / 2, y - h / 2, x + w / 2, y + h / 2), PANEL, outline=col)
    text(d, (x, y - 50 * kk), big, font(F_BLK, 84 * kk), col)
    text(d, (x, y + 40 * kk), label, font(F_BLD, 32 * kk), WHITE)
    text(d, (x, y + 95 * kk), src, font(F_MED, 24 * kk), GREY)

def sc_setup(c):
    d = c.d
    text(d, (W / 2, 150), "THE SETUP: REAL NUMBERS, OCTOBER 2026", font(F_BLK, 54), WHITE)
    if c.rv(1) >= 0: stat_card(c, 440, 470, c.rv(1), "$50,562", "Average new car price", "Source: Kelley Blue Book, Sep 2026", YEL)
    if c.rv(2) >= 0: stat_card(c, 960, 470, c.rv(2), "7.0%", "Average new car loan APR", "Source: Edmunds, Q3 2026", MAX)
    if c.rv(3) >= 0: stat_card(c, 1480, 470, c.rv(3), "-41.8%", "Value lost in 5 years", "Source: iSeeCars 2026 study", RED)

def sc_rule(c):
    d = c.d
    card(d, (260, 170, 1660, 820), PANEL)
    text(d, (W / 2, 250), "THE RULE THAT MAKES IT FAIR", font(F_BLK, 60), YEL)
    rows = [(0, "All three start with $50,562 in cash", WHITE), (1, "Same monthly car budget: $767", WHITE), (1, "Anything not spent on the car is invested at 7%/yr", GREEN)]
    for i, (k, s, col) in enumerate(rows):
        if c.rv(k) >= 0:
            a = ease_out((c.rv(k) - 0.3 * (i if k == 1 else 0)) / 0.35)
            if a <= 0: continue
            y = 400 + i * 110
            text(d, (360 + (1 - a) * 60, y), "•", font(F_BLK, 60), col, anchor="lm")
            text(d, (410 + (1 - a) * 60, y), s, font(F_BLD, 46), mix(PANEL, col, a), anchor="lm")
    for (nm, how, col, who), x in zip(TRIO, (560, 960, 1360)):
        person3(d, x, 760, 0.38, col, who, c.t + x)

def big_person_scene(c, who, title, lines):
    d = c.d; nm, how, col, wh = next(x for x in TRIO if x[3] == who)
    k = ease_back(c.since() / 0.45)
    person3(d, 380, 560, 1.25 * k, col, wh, c.t)
    car(d, 380, 820, 0.9 * k, col)
    text(d, (1150, 150), title, font(F_BLK, 64), col)
    for i, (st, s, colr, size) in enumerate(lines):
        if c.rv(st) < 0: continue
        a = ease_out(c.rv(st) / 0.35)
        text(d, (760 + (1 - a) * 40, 300 + i * 110), s, font(F_BLK if size > 50 else F_BLD, size), mix(BG, colr, a), anchor="lm")

def sc_nora(c):
    big_person_scene(c, "N", "NORA PAYS CASH", [(0, "Pays $50,562 up front", WHITE, 52), (0, "No loan. No interest.", GREEN, 46),
                                                (1, "Invests her whole $767/month", GREEN, 46), (1, "car budget instead", GREEN, 46)])

def sc_max(c):
    big_person_scene(c, "M", "MAX FINANCES", [(0, "$5,554 down (US average)", WHITE, 50), (0, "Invests the rest of his cash", GREEN, 44),
                                              (1, "6-year loan at 7%", WHITE, 50), (1, "$767 / month", MAX, 72), (2, "Interest paid: $10,241", RED, 50)])

def sc_theo(c):
    big_person_scene(c, "T", "THEO LEASES", [(0, "Rents the car for 3 years,", WHITE, 46), (0, "then swaps for a new one", WHITE, 46),
                                             (1, "Pays for the value it loses", GREY, 40), (1, "+ a finance charge", GREY, 40),
                                             (2, "≈ $773 / month + $4,000 each lease", THEO, 50), (3, "Same as the loan payment!", YEL, 54)])

def sc_loanlen(c):
    d = c.d
    text(d, (W / 2, 120), "LONGER LOANS: LOWER PAYMENT, MORE INTEREST", font(F_BLK, 54), WHITE)
    text(d, (W / 2, 190), "1 in 4 new car loans is now 7 years or longer (Edmunds, Q3 2026)", font(F_MED, 32), GREY)
    rows = [("5 years", 891, 8465, 2), ("6 years", 767, 10241, 0), ("7 years", 679, 12052, 1)]
    for i, (lab, pay, intr, st) in enumerate(rows):
        if c.rv(st) < 0: continue
        a = ease_out(c.rv(st) / 0.6); y = 330 + i * 170
        text(d, (330, y), lab, font(F_BLK, 48), WHITE, anchor="rm")
        rrect(d, (370, y - 50, 370 + 560 * pay / 900 * a, y - 6), 18, fill=MAX)
        rrect(d, (370, y + 6, 370 + 560 * intr / 12500 * a, y + 50), 18, fill=RED)
        if a > 0.8:
            text(d, (390 + 560 * pay / 900, y - 28), f"${pay}/mo", font(F_BLD, 36), WHITE, anchor="lm")
            text(d, (390 + 560 * intr / 12500, y + 28), f"${intr:,} interest", font(F_BLD, 36), RED, anchor="lm")
    if c.rv(3) >= 0:
        k = ease_back(c.rv(3) / 0.4)
        if k > 0.05:
            card(d, (1180, 360, 1760, 640), PANEL2, outline=YEL)
            ptext(c, (1470, 450), "Longer loans", F_BLK, 54, WHITE, k)
            ptext(c, (1470, 530), "FEEL cheaper.", F_BLK, 54, YEL, k)
            ptext(c, (1470, 600), "You just pay for longer.", F_BLD, 34, GREY, k)

def sc_depr(c):
    d = c.d
    text(d, (W / 2, 110), "THE SILENT COST: DEPRECIATION", font(F_BLK, 58), WHITE)
    L, R, T, B = 280, 1500, 220, 800
    vals = [50562] + [ROWS[y]["car"] for y in range(1, 10)]
    d.line([(L, B), (R, B)], fill=LINE, width=4)
    for v in (10000, 20000, 30000, 40000, 50000):
        y = B - (B - T) * v / 52000; d.line([(L, y), (R, y)], fill=(30, 38, 58), width=2)
        text(d, (L - 20, y), "${:,}".format(v), font(F_MED, 26), DIMT, anchor="rm")
    grow = ease_out(c.since() / 2.5); n = len(vals); bw = (R - L) / n
    for i, v in enumerate(vals):
        if i / n > grow: break
        h = (B - T) * v / 52000
        d.rectangle([L + i * bw + 10, B - h, L + (i + 1) * bw - 10, B], fill=mix(GREEN, RED, i / 9))
        text(d, (L + (i + 0.5) * bw, B + 32), "new" if i == 0 else f"yr {i}", font(F_MED, 26), GREY)
    if c.rv(1) >= 0:
        k = ease_back(c.rv(1) / 0.4); x = L + 1.5 * bw
        ptext(c, (x, B - (B - T) * vals[1] / 52000 - 50), "-20%", F_BLK, 50, RED, k)
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        ptext(c, (L + 5.5 * bw, B - (B - T) * vals[5] / 52000 - 50), "-42%", F_BLK, 50, RED, k)
        ptext(c, (L + 9.5 * bw, B - (B - T) * vals[9] / 52000 - 50), "$24K", F_BLK, 50, WHITE, k)
    if c.rv(3) >= 0:
        k = ease_back(c.rv(3) / 0.4)
        if k > 0.05: pill(d, 1180, 300, "Theo pays for this inside every lease payment", font(F_BLD, int(32 * k)), (20, 20, 20), THEO)

def sc_score(c):
    d = c.d
    cur = c.cur(); y = cur["show"].get("y", 1)
    ys = [s["show"].get("y", 1) for s in c.run["segs"] if s["start"] <= c.t + 0.05]
    prev_y = ys[-2] if len(ys) > 1 and ys[-2] != y else y
    a = ease_io((c.t - cur["start"]) / 0.9) if prev_y != y else 1
    yy = lerp(prev_y, y, a)
    def val(key, yv):
        i = int(math.floor(yv)); f = yv - i
        lo = ROWS[max(1, i)][key]; hi = ROWS[min(9, i + 1)][key] if i < 9 else lo
        return lo + (hi - lo) * f
    text(d, (W / 2, 100), "SCOREBOARD", font(F_BLK, 60), YEL)
    text(d, (W / 2, 165), "Car value + investments - any loan left", font(F_MED, 32), GREY)
    rrect(d, (W / 2 - 170, 210, W / 2 + 170, 300), 45, fill=PANEL2)
    text(d, (W / 2, 255), f"YEAR {int(round(yy))}", font(F_BLK, 56), WHITE)
    L, R = 430, 1650; mx = 140000
    for i, ((nm, how, col, who), key) in enumerate(zip(TRIO, ("cash", "fin", "lease"))):
        v = val(key, yy); yc = 410 + i * 175
        person3(d, 210, yc + 40, 0.45, col, who, c.t + i)
        rrect(d, (L, yc - 50, R, yc + 50), 30, fill=PANEL)
        if c.rv(1) >= 0:
            w = (R - L) * min(1, v / mx) * ease_out(c.rv(1) / 0.8)
            rrect(d, (L, yc - 50, L + max(60, w), yc + 50), 30, fill=col)
            text(d, (L + max(60, w) + 25, yc), kfmt(round(v, -2)), font(F_BLK, 50), WHITE, anchor="lm")
        text(d, (L + 20, yc - 78), f"{nm} ({how})", font(F_BLD, 28), col, anchor="lm")
    if c.rv(2) >= 0:
        k = ease_back(c.rv(2) / 0.4)
        if k > 0.05:
            pill(d, 1340, 870, "GAP: $56,000", font(F_BLK, int(44 * k)), WHITE, RED)
            pill(d, 650, 870, "NORA = MAX ?!", font(F_BLK, int(44 * k)), (20, 20, 20), YEL)

def sc_twist(c):
    d = c.d; n = c.run["show"].get("n", 1)
    k = ease_back(c.since() / 0.45)
    if k > 0.05: pill(d, W / 2, 190, f"TWIST #{n}", font(F_BLK, int(80 * k)), (20, 20, 20), YEL, padx=50)
    lines = {1: [(0, "Paying cash didn't beat the loan.", WHITE), (1, "Loan cost 7%  =  investments earned 7%", WHITE),
                 (2, "Loan rate < what your money earns: FINANCE", GREEN), (2, "Loan rate > what your money earns: CASH", NORA)],
             2: [(0, "Theo isn't stupid.", WHITE), (1, "Brand-new car the whole time.", WHITE), (1, "Always under warranty. No big repairs.", WHITE),
                 (2, "$56K = the price of always driving new", YEL)]}[n]
    for i, (st, s, col) in enumerate(lines):
        if c.rv(st) < 0: continue
        a = ease_out(c.rv(st) / 0.4)
        text(d, (W / 2, 380 + i * 115 + (1 - a) * 30), s, font(F_BLK, 56), mix(BG, col, a))

def sc_rates(c):
    d = c.d
    text(d, (W / 2, 130), "IT ALL DEPENDS ON YOUR LOAN RATE", font(F_BLK, 58), WHITE)
    for i, (st, title, run_, col) in enumerate([(0, "0% DEALER DEAL", R0, GREEN), (1, "10% LOAN", R10, RED)]):
        if c.rv(st) < 0: continue
        k = ease_back(c.rv(st) / 0.45)
        if k < 0.05: continue
        x = 560 + i * 800; f9 = run_["rows"][-1]
        card(d, (x - 330, 260, x + 330, 760), PANEL, outline=col)
        ptext(c, (x, 330), title, F_BLK, 54, col, k)
        ptext(c, (x, 450), f"Max (finance)  {kfmt(round(f9['fin'], -2))}", F_BLD, 42, MAX, k)
        ptext(c, (x, 540), f"Nora (cash)  {kfmt(round(f9['cash'], -2))}", F_BLD, 42, NORA, k)
        diff = f9["fin"] - f9["cash"]
        ptext(c, (x, 670), ("FINANCE wins +" if diff > 0 else "CASH wins +") + kfmt(round(abs(diff), -2)), F_BLK, 46, YEL, k)

def sc_bill(c):
    d = c.d
    text(d, (W / 2, 110), "WHAT 9 YEARS OF DRIVING REALLY COST", font(F_BLK, 56), WHITE)
    B = 820; sc = 560 / 96000
    stacks = [(1, "THEO", LEASE_C, [(95442, LEASE_C, "Lease payments + fees $95.4K")]),
              (2, "MAX", FIN_C, [(26593, (255, 150, 70), "Value lost $26.6K"), (10241, RED, "Interest $10.2K"), (6000, (200, 120, 220), "Repairs $6K")]),
              (3, "NORA", CASH_C, [(26593, (255, 150, 70), "Value lost $26.6K"), (6000, (200, 120, 220), "Repairs $6K")])]
    for i, (st, nm, col, parts) in enumerate(stacks):
        if c.rv(st) < 0: continue
        x = 330 + i * 560; y = B; a = ease_out(c.rv(st) / 0.7)
        for v, pc, lab in parts:
            h = v * sc * a; d.rectangle([x - 110, y - h, x + 110, y], fill=pc)
            if a > 0.9: text(d, (x + 130, y - h / 2), lab, font(F_BLD, 30), pc, anchor="lm")
            y -= h
        text(d, (x, B + 40), nm, font(F_BLK, 44), col)
        if nm == "NORA" and c.rv(3) > 0.6:
            pill(d, x, y - 60, "+ lost investment growth", font(F_BLD, 28), (20, 20, 20), YEL)
        if nm == "MAX" and a > 0.9: text(d, (x, y - 40), "$42.8K", font(F_BLK, 46), WHITE)
        if nm == "THEO" and a > 0.9: text(d, (x, y - 40), "No car at the end", font(F_BLD, 32), RED)

def checklist(c, title, items, col=GREEN, warn=False):
    d = c.d
    text(d, (W / 2, 120), title, font(F_BLK, 56), YEL)
    for i, (st, s) in enumerate(items):
        k = c.rv(st)
        if k < 0: continue
        a = ease_back(k / 0.35); y = 280 + i * 140
        rrect(d, (220, y - 52, 1700, y + 52), 30, fill=PANEL)
        if a > 0.05:
            d.ellipse([270 - 32 * a, y - 32 * a, 270 + 32 * a, y + 32 * a], fill=RED if (warn and i > 0) else col)
            text(d, (270, y), "!" if (warn and i > 0) else str(i + 1), font(F_BLK, int(36 * a)), (15, 20, 25))
        text(d, (330, y), s, font(F_BLD, 40), WHITE, anchor="lm")

def sc_lease_ok(c):
    checklist(c, "WHEN LEASING CAN MAKE SENSE (AND THE TRAPS)",
              [(0, "Cheap manufacturer lease deals, swapping every few years, low miles"),
               (1, "Mileage caps, often ~10-12K miles a year, with fees for every mile over"),
               (2, "Wear-and-tear charges at hand-back"), (2, "Ending a lease early can be very expensive")], warn=True)

def sc_tips(c):
    checklist(c, "3 HABITS THAT SAVE REAL MONEY",
              [(1, "Get a bank or credit union loan quote first (1% lower = ~$1,500 saved)"),
               (2, "Keep your car longer: the big value drop is early"),
               (3, "Negotiate the car's price, not the monthly payment")])

def sc_check(c):
    checklist(c, "LEASE, FINANCE OR CASH? THE 30-SECOND VERSION",
              [(1, "Keep cars a long time? Owning usually wins"),
               (2, "Loan rate vs what your money earns decides cash or finance"),
               (3, "Love a new car every few years? Leasing can be fair, at a price")])

def sc_outro(c):
    d = c.d; t = c.t
    for (nm, how, col, who), x in zip(TRIO, XS):
        car(d, x, 700, 0.95, col); person3(d, x, 520, 0.85, col, who, t + x)
        text(d, (x, 830), nm, font(F_BLK, 54), col); text(d, (x, 880), how, font(F_BLD, 34), WHITE)
    if c.rv(1) >= 0:
        text(d, (W / 2, 110), "SAME $50K CAR. THREE WAYS TO PAY.", font(F_BLK, 66), WHITE)
        text(d, (W / 2, 205), "WHO'S RICHEST AFTER 9 YEARS?", font(F_BLK, 80), YEL, stroke=4)
    else:
        k = ease_back(c.since() / 0.4)
        ptext(c, (W / 2, 140), "ARE YOU A NORA, A MAX OR A THEO?", F_BLK, 74, YEL, k, stroke=4)
        ptext(c, (W / 2, 235), "Tell me in the comments  ↓", F_BLD, 44, WHITE, k)
