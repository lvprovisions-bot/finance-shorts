"""Rent vs buy model (monthly). Sources:
 price $417,500  NAR median existing-home price, Sep 2026
 rate 7.40%      Freddie Mac PMMS 30-yr fixed, 15 Oct 2026
 rent $1,962     Zillow Observed Rent Index, Jul 2026 (typical US asking rent)
 prop tax 0.9%   ATTOM 2025 national average effective rate
 insurance $2,808/yr  Insurify 2026 national average ($300k dwelling)
 home growth 4%/yr   FHFA HPI long-run CAGR since 1991 is 4.4%; we use 4%
 down 20%  (NAR 2025: 19% median for all buyers)
Assumptions (rules of thumb): buyer closing 3%, selling costs 6%, maintenance 1%/yr of value,
 rent + insurance + other costs grow 3%/yr, investments return 7%/yr, renter's insurance $180/yr,
 15% tax on investment gains when cashed out; home gain up to $250k tax-free (single).
Both people spend the same each month on housing; whoever's housing costs less invests the difference."""
import json, sys
P = dict(price=417500, rate=0.074, rent=1962, ptax=0.009, ins=2808, hg=0.04, down=0.20, close=0.03, sell=0.06,
         maint=0.01, infl=0.03, ret=0.07, rins=180, cgt=0.15, excl=250000)

def run(years=30, **kw):
    p = dict(P, **kw)
    loan = p["price"] * (1 - p["down"]); r = p["rate"] / 12; n = 360
    pmt = loan * r / (1 - (1 + r) ** -n)
    upfront = p["price"] * (p["down"] + p["close"])
    bal = loan; value = p["price"]; rent = p["rent"]; ins = p["ins"]; rins = p["rins"]
    renter_pf = upfront; renter_basis = upfront; owner_pf = 0.0; owner_basis = 0.0
    out = []; tot = dict(interest=0, ptax=0, ins=0, maint=0, rent=0, principal=0)
    for m in range(1, years * 12 + 1):
        interest = bal * r; princ = pmt - interest if bal > 0 else 0
        if bal <= 0: interest = 0; princ = 0
        bal = max(0, bal - princ)
        own_cost = (pmt if princ > 0 or interest > 0 else 0) + value * p["ptax"] / 12 + ins / 12 + value * p["maint"] / 12
        rent_cost = rent + rins / 12
        tot["interest"] += interest; tot["principal"] += princ; tot["ptax"] += value * p["ptax"] / 12
        tot["ins"] += ins / 12; tot["maint"] += value * p["maint"] / 12; tot["rent"] += rent
        renter_pf *= 1 + p["ret"] / 12; owner_pf *= 1 + p["ret"] / 12
        diff = own_cost - rent_cost
        if diff > 0: renter_pf += diff; renter_basis += diff
        else: owner_pf += -diff; owner_basis += -diff
        value *= (1 + p["hg"]) ** (1 / 12)
        if m % 12 == 0:
            rent *= 1 + p["infl"]; ins *= 1 + p["infl"]; rins *= 1 + p["infl"]
            y = m // 12
            gain = value * (1 - p["sell"]) - p["price"]; htax = max(0, gain - p["excl"]) * p["cgt"]
            owner_nw = value * (1 - p["sell"]) - bal - htax + owner_pf - max(0, owner_pf - owner_basis) * p["cgt"]
            renter_nw = renter_pf - max(0, renter_pf - renter_basis) * p["cgt"]
            out.append(dict(y=y, value=round(value), bal=round(bal), owner_nw=round(owner_nw), renter_nw=round(renter_nw),
                            own_month=round(own_cost), rent_month=round(rent_cost), renter_pf=round(renter_pf), owner_pf=round(owner_pf)))
    return dict(pmt=pmt, upfront=upfront, loan=loan, rows=out, tot={k: round(v) for k, v in tot.items()})

if __name__ == "__main__":
    b = run()
    print("payment", round(b["pmt"]), "upfront", round(b["upfront"]), "loan", round(b["loan"]))
    m1 = P["price"]*P["ptax"]/12, P["ins"]/12, P["price"]*P["maint"]/12
    print("month1 own: P&I %.0f tax %.0f ins %.0f maint %.0f total %.0f | rent %.0f" % (b["pmt"], *m1, b["pmt"]+sum(m1), P["rent"]+15))
    for r in b["rows"]:
        if r["y"] in (1,2,3,5,7,10,11,12,15,20,25,30): print(r)
    be = next((r["y"] for r in b["rows"] if r["owner_nw"] > r["renter_nw"]), None); print("break-even year", be)
    print("totals 30y", b["tot"])
    for lab, kw in [("hg4.4", dict(hg=0.044)), ("rate6", dict(rate=0.06)), ("rent2400", dict(rent=2400)), ("ret10", dict(ret=0.10)), ("ret5", dict(ret=0.05)), ("hg3", dict(hg=0.03)), ("rent2400_rate6", dict(rent=2400, rate=0.06))]:
        x = run(**kw); be = next((r["y"] for r in x["rows"] if r["owner_nw"] > r["renter_nw"]), None)
        f = x["rows"][-1]; t = x["rows"][9]
        print(lab, "BE", be, "y10", t["owner_nw"], t["renter_nw"], "y30", f["owner_nw"], f["renter_nw"])
