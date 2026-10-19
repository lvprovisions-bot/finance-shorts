"""Build longform/L02-lease-finance-cash.json (title, description with chapter timestamps) from timings.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import SEGMENTS
TM = json.load(open(os.path.join(HERE, "timings.json")))
show = {s["id"]: s["show"] for s in SEGMENTS}
chaps = [(0, "Three friends, one $50K car")]
for s in TM["segments"]:
    c = show[s["id"]].get("chap")
    if c and all(c != x[1] for x in chaps): chaps.append((s["start"], c))
def ts(x): x = int(x); return f"{x // 60}:{x % 60:02d}"
chap_txt = "\n".join(f"{ts(t)} {c}" for t, c in chaps)
desc = f"""Nora pays cash. Max takes a car loan. Theo leases. Same $50,562 car, same starting cash, same monthly car budget, and anything not spent on the car gets invested. We ran nine years of real numbers to see who ends up richest.

The short version: leasing cost Theo about $56,000 compared with owning, the price of always driving a brand-new car. And paying cash only beats financing when your loan rate is higher than what your money could earn.

Are you a Nora, a Max or a Theo? 👇

Chapters
{chap_txt}

Sources
- Average new-vehicle transaction price $50,562 (Sep 2026): Kelley Blue Book / Cox Automotive
- Average new-car loan APR 7.0%, average down payment $5,554, 1 in 4 loans 84+ months (Q3 2026): Edmunds
- Average 5-year depreciation 41.8%: iSeeCars 2026 study
- Typical lease due-at-signing around $4,000: Forbes lease survey, Oct 2026

⚠️ Assumptions: 72-month loan; lease payment is an estimate (36 months, 62% residual, money factor equivalent to 7% APR, about $4,000 due at signing); value falls about 20% in year 1, 41.8% by year 5, then ~5% a year; $1,000/yr repairs for owners from year 4; investments return 7%/yr; car prices flat; sales tax, fees, insurance and taxes on gains ignored. These are illustrations, not predictions; your car, rate and returns will differ, and investing involves risk. This is not financial advice.

Narrated by the channel's creator. Follow for more numbers that change how you spend.

#carbuying #leasevsbuy #carloan #personalfinance #moneytips #investing"""
meta = {"title": "Lease, Finance or Pay Cash? 9 Years of Real Numbers", "description": desc, "format": "LONG: CAR LEASE VS FINANCE VS CASH",
        "length_s": round(TM["total"], 1), "category_id": "27"}
json.dump(meta, open(os.path.join(HERE, "../../longform/L02-lease-finance-cash.json"), "w"), indent=1, ensure_ascii=False)
print(chap_txt); print(len(desc), "chars")
