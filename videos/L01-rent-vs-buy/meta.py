"""Build the upload JSON (title, description with chapter timestamps) from timings.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import SEGMENTS
TM = json.load(open(os.path.join(HERE, "timings.json")))
show = {s["id"]: s["show"] for s in SEGMENTS}
chaps = [(0, "Nora buys, Theo rents: who wins?")]
for s in TM["segments"]:
    c = show[s["id"]].get("chap")
    if c and c != "Exam tip" and all(c != x[1] for x in chaps): chaps.append((s["start"], c))
names = {"So who wins?": "So should you rent or buy?"}
def ts(x): x = int(x); return f"{x // 60}:{x % 60:02d}"
chap_txt = "\n".join(f"{ts(t)} {names.get(c, c)}" for t, c in chaps)
desc = f"""Nora buys the typical American home. Theo rents. Same salary, same city, same monthly housing budget, and whoever's housing is cheaper invests the difference. We ran 30 years of real numbers to see who ends up richer, and then changed the assumptions to see when the answer flips.

The short version: renting only wins if you really invest the gap every month, and buying wins when homes are cheap relative to rent and you stay long enough. Use the price-to-rent test in the video to check where you live.

Are you Team Nora or Team Theo? And what's the price-to-rent ratio where you live? 👇

Chapters
{chap_txt}

Sources
- Median existing-home price $417,500 (Sep 2026): National Association of Realtors
- 30-year fixed mortgage 7.40% (15 Oct 2026): Freddie Mac Primary Mortgage Market Survey
- Typical US asking rent $1,962 (Jul 2026): Zillow Observed Rent Index
- Property tax 0.9% average effective rate (2025): ATTOM
- Home insurance $2,808/yr average ($300k dwelling, 2026): Insurify
- Long-run home price growth 4.4%/yr since 1991: FHFA House Price Index
- Median down payment and seller tenure: NAR 2025 Profile of Home Buyers and Sellers

⚠️ Assumptions: 20% down, 3% buyer closing costs, 6% selling costs, maintenance 1% of value per year, homes +4%/yr, rents and insurance +3%/yr, investments 7%/yr, 15% tax on investment gains, $250k home-sale gain exclusion, mortgage interest deduction ignored. These are illustrations, not predictions; real prices, rates and returns vary and investing involves risk. This is not financial advice.

Follow for more numbers that change how you spend.

#rentvsbuy #personalfinance #realestate #mortgage #investing #moneytips"""
meta = {"title": "Renting vs Buying a Home: Who's Richer After 30 Years?", "description": desc, "format": "LONG: RENT VS BUY",
        "length_s": round(TM["total"], 1), "category_id": "27"}
os.makedirs(os.path.join(HERE, "../../longform"), exist_ok=True)
json.dump(meta, open(os.path.join(HERE, "../../longform/L01-rent-vs-buy.json"), "w"), indent=1, ensure_ascii=False)
print(chap_txt); print(len(desc), "chars")
