"""Lease vs finance vs cash over 9 years (3 back-to-back 36-month leases). Monthly model.
Sourced: car $50,562 (KBB avg new transaction price, Sep 2026); loan APR 7.0%, down $5,554 (Edmunds Q3 2026);
         5-yr depreciation 41.8% (iSeeCars 2026 study); value curve: -20% year 1 (common rule of thumb), 72%/66%/62% yrs 2-4, 58.2% yr 5, then -5%/yr; lease due-at-signing ~$4,000 (Forbes lease survey Oct 2026).
Assumptions: 72-month loan; lease residual 62% after 36 mo, money factor = APR/2400; car prices flat; sales tax/fees ignored;
 out-of-warranty repairs $1,000/yr from year 4 for owners; investments 7%/yr; everyone starts with $50,562 cash and has the same
 monthly car budget (= the loan payment); whatever isn't spent on the car is invested."""
P = dict(price=50562, apr=0.07, down=5554, term=72, retain5=0.582, residual=0.62, lease_due=4000, repairs=1000, ret=0.07, years=9)
def run(**kw):
    p = dict(P, **kw); r = p["apr"] / 12; loan = p["price"] - p["down"]
    pmt = loan * r / (1 - (1 + r) ** -p["term"]); B = pmt
    mf = p["apr"] * 100 / 2400; res = p["price"] * p["residual"]
    lease = (p["price"] - res) / 36 + (p["price"] + res) * mf
    VAL = [1, 0.80, 0.72, 0.66, 0.62, p["retain5"]] + [p["retain5"] * 0.95 ** k for k in range(1, 6)]
    g = 1 + p["ret"] / 12
    # starting cash
    inv = {"cash": 0.0, "fin": p["price"] - p["down"], "lease": p["price"] - p["lease_due"]}
    bal = loan; rows = []; tot = {"lease": p["lease_due"], "fin_interest": 0.0}
    for m in range(1, p["years"] * 12 + 1):
        for k in inv: inv[k] *= g
        yr = (m - 1) // 12 + 1; rep = p["repairs"] / 12 if yr >= 4 else 0
        # cash buyer: invests whole budget minus repairs
        inv["cash"] += B - rep
        # financer
        if bal > 0.01:
            it = bal * r; bal -= (pmt - it); tot["fin_interest"] += it; spend = pmt
        else: spend = 0
        inv["fin"] += B - spend - rep
        # leaser: new lease every 36 months (due at signing at months 37, 73)
        spend_l = lease + (p["lease_due"] if m in (37, 73) else 0); tot["lease"] += spend_l
        inv["lease"] += B - spend_l
        if m % 12 == 0:
            car = p["price"] * VAL[yr]
            rows.append(dict(y=yr, cash=round(inv["cash"] + car), fin=round(inv["fin"] + car - max(bal, 0)),
                             lease=round(inv["lease"]), car=round(car)))
    return dict(pmt=pmt, lease=lease, rows=rows, interest=round(tot["fin_interest"]), lease_total=round(tot["lease"]))
if __name__ == "__main__":
    b = run(); print("loan pmt %.0f lease pmt %.0f interest %d lease total %d" % (b["pmt"], b["lease"], b["interest"], b["lease_total"]))
    for x in b["rows"]: print(x)
    for lab, kw in [("apr4", dict(apr=0.04)), ("apr10", dict(apr=0.10)), ("ret5", dict(ret=0.05)), ("res55", dict(residual=0.55)), ("rep2000", dict(repairs=2000))]:
        f = run(**kw)["rows"][-1]; print(lab, f)
