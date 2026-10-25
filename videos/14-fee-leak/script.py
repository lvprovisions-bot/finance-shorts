# WHO WINS? #5 — investment fees. Nora & Theo each invest the SAME $500 a month for 40 years (age 25 -> 65).
# Nora's index fund charges 0.05% a year; Theo's fund charges 1% a year. Same 7% return BEFORE fees.
# Real-world figure (web-searched 25 Oct 2026): ICI "Trends in the Expenses and Fees of Funds, 2025" (Mar 2026):
#   index equity mutual funds had an asset-weighted average expense ratio of 0.05% in 2025.
#   Theo's 1% is an ASSUMPTION (a pricey fund / advisory-fee level), stated on screen.
# Assumptions (on screen): $500/month for 40 years, 7%/yr before fees, net rate compounded monthly
#   ((1+r)^(1/12)-1), fees deducted as a lower annual return, returns held constant, no taxes, no inflation.
# Maths (python, see bottom):
#   Nora (6.95% net): $1,226,542 -> "$1.23 million"   Theo (6.00% net): $958,482 -> "$958K"
#   Gap $268,060 -> "$268K" ; both put in 500*12*40 = $240,000 ; gap = 21.9% of Nora's pot ("over a fifth")
#   Gap is bigger than everything Theo paid in ($240,000).
# First line (3 drafts): (a) "Theo's 1% fee cost him $268,000."  (b) "One percent. That tiny fee cost Theo $268K."
#   (c) "Same $500 a month. Theo's 1% fee cost him $268K."  -> picked (c): setup + number + conflict in one breath,
#   and "Same $500 a month..." loops cleanly from the last line.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "N", [("SAME", "Same"), ("$500", "five hundred"), ("A MONTH.", "a month."), ("THEO'S", "Theo's"),
                    ("1% FEE", "one percent fee"), ("COST HIM", "cost him"), ("$268K.", "two hundred sixty eight grand.")], 0.15),
    ("tiny",  "T", [("ONE", "One"), ("PERCENT?", "percent?"), ("THAT'S", "That's"), ("NOTHING!", "nothing!")], 0.15),
    ("fees",  "N", [("MY INDEX FUND", "My index fund"), ("CHARGES", "charges"), ("0.05%.", "zero point zero five percent."),
                    ("YOURS?", "Yours?"), ("1%.", "One percent.")], 0.15),
    ("time",  "N", [("40 YEARS.", "Forty years."), ("SAME 7%", "Same seven percent"), ("BEFORE FEES.", "before fees.")], 0.15),
    ("ask",   "T", [("SO WHAT", "So what"), ("DO I", "do I"), ("END UP WITH?", "end up with?")], 0.15),
    ("result", "N", [("ME:", "Me:"), ("$1.23M.", "one point two three million."), ("YOU:", "You:"), ("$958K.", "nine fifty eight thousand.")], 0.2),
    ("punch", "T", [("SO MY", "So my"), ("TINY FEE", "tiny fee"), ("BOUGHT", "bought"), ("SOMEONE", "someone"), ("A BOAT.", "a boat.")], 0.2),
    ("q",     "N", [("WHAT'S", "What's"), ("YOUR FUND'S", "your fund's"), ("FEE?", "fee?"), ("GO CHECK.", "Go check.")], 0.1),
    ("loop",  "T", [("SAME", "Same"), ("$500", "five hundred"), ("A MONTH...", "a month...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.12

if __name__ == "__main__":
    def fv(pm, r, yrs):
        m = (1 + r) ** (1 / 12) - 1; b = 0.0
        for _ in range(yrs * 12):
            b = (b + pm) * (1 + m)
        return b
    n, t = fv(500, 0.07 - 0.0005, 40), fv(500, 0.07 - 0.01, 40)
    print(round(n), round(t), round(n - t), 500 * 12 * 40, round((n - t) / n * 100, 1))
