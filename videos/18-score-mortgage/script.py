# WHO WINS? #7 — credit score vs mortgage cost. Nora & Theo buy the SAME house with the SAME $300,000 30-year fixed
# mortgage. Nora's credit score is 760 and she gets 6.0%; Theo's is 620 and he gets 7.5%.
# Rates are EXAMPLE rates (stated on screen as illustrative). The 1.5-point gap is in line with the typical spread
# between the top (760-850) and bottom (620-639) FICO bands in lender rate tables; live rate pages could not be
# fetched this run, so no specific source is claimed — the video labels them "example rates".
# Assumptions (on screen): $300K loan, 30-yr fixed, monthly payments, principal + interest only (no taxes,
#   insurance, PMI or fees), same house, same down payment.
# Maths (python, see bottom): payment = P*i/(1-(1+i)^-360), i = rate/12
#   Nora 6.0%: $1,798.65/mo ; Theo 7.5%: $2,097.64/mo ; difference $298.99/mo (~$299)
#   over 360 months: 298.99*360 = $107,637 more (Theo's total interest $455,152 vs Nora's $347,515)
# First line (3 drafts):
#   (a) "Theo's credit score just cost him $107K."
#   (b) "Same house, same loan. Theo pays $107,000 more. Because of three digits."
#   (c) "Same $300K house. Theo pays $107K more."
#   -> picked (c): conflict + number in the first 3 seconds, and the loop line "Same $300K house..." repeats it.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",   "N", [("SAME", "Same"), ("$300K", "three hundred K"), ("HOUSE.", "house."),
                     ("THEO", "Theo"), ("PAYS", "pays"), ("$107K MORE.", "a hundred and seven K more.")], 0.15),
    ("huh",    "T", [("FOR THE", "For the"), ("SAME", "same"), ("HOUSE?!", "house?!")], 0.15),
    ("score",  "N", [("MY SCORE:", "My score:"), ("760.", "seven sixty."), ("I GOT 6%.", "I got six percent."),
                     ("YOURS:", "Yours:"), ("620.", "six twenty."), ("7.5%.", "Seven and a half.")], 0.1),
    ("only",   "T", [("IT'S", "It's"), ("ONLY", "only"), ("1.5%!", "one and a half percent!")], 0.15),
    ("month",  "N", [("THAT'S", "That's"), ("$299 MORE", "two ninety nine more"), ("EVERY", "every"), ("MONTH.", "month."),
                     ("FOR", "For"), ("30 YEARS.", "thirty years.")], 0.15),
    ("fix",    "N", [("PAY", "Pay"), ("ON TIME.", "on time."), ("KEEP CARDS", "Keep card balances"), ("LOW.", "low."),
                     ("SCORE", "Your score"), ("CLIMBS.", "climbs.")], 0.15),
    ("punch",  "T", [("SO", "So"), ("THREE DIGITS...", "three digits..."), ("COST ME", "cost me"), ("SIX DIGITS.", "six digits.")], 0.2),
    ("q",      "N", [("FIX YOUR", "Fix your"), ("SCORE", "score"), ("OR BUY", "or buy"), ("NOW?", "now?"), ("TELL ME.", "Tell me.")], 0.1),
    ("loop",   "T", [("SAME", "Same"), ("$300K HOUSE...", "three hundred K house...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.1

if __name__ == "__main__":
    def pmt(P, r, n=360):
        i = r / 12
        return P * i / (1 - (1 + i) ** -n)
    a, b = pmt(300_000, 0.06), pmt(300_000, 0.075)
    print(round(a, 2), round(b, 2), round(b - a, 2), round((b - a) * 360), round(a * 360 - 3e5), round(b * 360 - 3e5))
