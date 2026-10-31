# WHO WINS? #8 — car loan term. Nora & Theo buy the SAME $45,000 car with the SAME 7% APR.
# Nora takes a 48-month (4-yr) loan; Theo takes an 84-month (7-yr) loan because the payment is lower.
# Real-world anchors (Edmunds Q3 2026 new-vehicle data, released 1 Oct 2026, via KPRC Click2Houston 19 Oct 2026):
#   average new-car APR 7.0%; average amount financed $44,664 (rounded to $45,000 here);
#   25.5% of financed new-car purchases used loans of 84 months or longer ("1 in 4").
# Assumptions (on screen): same car, same $45K financed, same 7% APR for both terms (in reality longer terms
#   often carry HIGHER rates, so this is conservative), monthly payments, no fees/taxes/insurance.
# Maths (python, see bottom): payment = P*i/(1-(1+i)^-n), i = 0.07/12
#   Nora 48 mo: $1,077.58/mo, total interest $6,723.89
#   Theo 84 mo: $679.17/mo  ($398.41 less per month), total interest $12,050.33
#   Theo pays $5,326.44 more interest. After 48 months Nora owes $0; Theo still owes $21,995.93 (~$22K).
# First line (3 drafts):
#   (a) "Theo picked the cheaper car payment. It cost him $5,326."
#   (b) "Same $45K car. Theo's 'cheap' payment costs $5,326 more."
#   (c) "Four years or seven? Same car, and Theo just lost $5,326."
#   -> picked (b): conflict + number in the first 3 s, and the loop line "Same $45K car..." repeats it.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",   "N", [("SAME", "Same"), ("$45K", "forty-five K"), ("CAR.", "car."),
                     ("THEO'S", "Theo's"), ("\"CHEAP\"", "cheap"), ("PAYMENT", "payment"), ("COSTS", "costs"),
                     ("$5,326 MORE.", "five thousand three hundred more.")], 0.15),
    ("huh",    "T", [("BUT MINE'S", "But mine's"), ("$400 LESS", "four hundred less"), ("A MONTH!", "a month!")], 0.15),
    ("term",   "N", [("MINE:", "Mine:"), ("4 YEARS.", "four years."), ("YOURS:", "Yours:"), ("7 YEARS.", "seven years."),
                     ("SAME", "Same"), ("7%.", "seven percent.")], 0.1),
    ("year4",  "N", [("YEAR 4:", "Year four:"), ("MY CAR'S", "my car's"), ("PAID OFF.", "paid off."),
                     ("YOU STILL", "You still"), ("OWE $22K.", "owe twenty-two K.")], 0.15),
    ("total",  "N", [("TOTAL", "Total"), ("INTEREST:", "interest:"), ("ME $6,724.", "me, sixty-seven hundred."),
                     ("YOU", "You,"), ("$12,050.", "twelve thousand fifty.")], 0.15),
    ("punch",  "T", [("GREAT.", "Great."), ("IT'LL BE", "It'll be"), ("PAID OFF", "paid off"),
                     ("RIGHT WHEN", "right when"), ("IT DIES.", "it dies.")], 0.2),
    ("q",      "N", [("4 YEARS", "Four years"), ("OR 7?", "or seven?"), ("TELL ME.", "Tell me.")], 0.1),
    ("loop",   "T", [("SAME", "Same"), ("$45K CAR...", "forty-five K car...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.1

if __name__ == "__main__":
    def pmt(P, r, n):
        i = r / 12
        return P * i / (1 - (1 + i) ** -n)
    def bal(P, r, n, k):
        i = r / 12; p = pmt(P, r, n)
        return P * (1 + i) ** k - p * ((1 + i) ** k - 1) / i
    a, b = pmt(45_000, 0.07, 48), pmt(45_000, 0.07, 84)
    print(round(a, 2), round(b, 2), round(a - b, 2), round(a * 48 - 45e3, 2), round(b * 84 - 45e3, 2),
          round(b * 84 - a * 48, 2), round(bal(45_000, 0.07, 84, 48), 2))
