# WHO WINS? #11 — paying $200 extra on the mortgage every month vs paying exactly the bill.
# Nora & Theo take the SAME $350,000 30-year fixed mortgage at the SAME example rate of 6.5%.
# Nora adds $200 a month that goes straight to principal; Theo pays exactly the bill.
# No external statistics: 6.5% is labelled "example rate" on screen (Freddie Mac's current weekly figure could not be
#   confirmed this run). Assumptions on screen: fixed rate, extra goes to principal, no prepayment penalty,
#   ignores taxes/insurance; investing the $200 instead is a fair alternative (said in the comment question).
# Maths (python, see bottom):
#   payment = 350,000 * r / (1 - (1+r)^-360), r = 0.065/12 -> $2,212.24/mo
#   Theo: 360 payments, interest = 2,212.24*360 - 350,000 = $446,405.71
#   Nora: 2,412.24/mo -> paid off in 286 months (23 yr 10 mo), interest $338,308.88
#   saved $108,096.83 (~$108K), 74 months (6 yr 2 mo) sooner. Extra paid ~ $57K.
# First line (3 drafts):
#   (a) "Theo's mortgage lasts six years longer than mine. Same house."
#   (b) "Two hundred bucks a month saved me a hundred and eight grand."
#   (c) "Same mortgage. I pay two hundred extra. I save a hundred and eight grand."
#   -> picked (c): conflict + both numbers in the first breath, and the loop line "Same mortgage?" lands back on it.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "N", [("SAME", "Same"), ("MORTGAGE.", "mortgage."), ("I PAY", "I pay"), ("$200", "two hundred"),
                    ("EXTRA.", "extra."), ("I SAVE", "I save"), ("$108K.", "a hundred and eight grand.")], 0.15),
    ("huh",   "T", [("$200?", "Two hundred bucks?"), ("THAT'S", "That's"), ("NOTHING.", "nothing.")], 0.15),
    ("same",  "N", [("$350K.", "Three fifty K."), ("30 YEARS.", "Thirty years."), ("6.5%.", "Six and a half percent.")], 0.1),
    ("theo",  "N", [("YOU PAY", "You pay"), ("$446K", "four hundred forty-six thousand"), ("IN INTEREST.", "in interest.")], 0.1),
    ("nora",  "N", [("MY $200", "My two hundred"), ("HITS", "hits"), ("THE BALANCE.", "the balance."),
                    ("DONE IN", "Done in"), ("UNDER 24 YEARS.", "under twenty-four years.")], 0.1),
    ("me",    "T", [("AND ME?", "And me?")], 0.1),
    ("more",  "N", [("6 MORE YEARS", "Six more years"), ("OF PAYMENTS.", "of payments.")], 0.2),
    ("punch", "T", [("SO I'LL", "So I'll"), ("PAY IT OFF", "pay it off"), ("FROM A", "from a"),
                    ("RETIREMENT HOME?", "retirement home?")], 0.25),
    ("q",     "N", [("PAY EXTRA", "Pay extra"), ("OR INVEST IT?", "or invest it?"), ("TELL ME.", "Tell me.")], 0.1),
    ("loop",  "T", [("WAIT,", "Wait,"), ("SAME MORTGAGE?", "same mortgage?")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.1

P, RATE, N, EXTRA = 350000, 0.065, 360, 200


def amort(extra):
    r = RATE / 12
    pm = P * r / (1 - (1 + r) ** -N)
    b, m, I, hist = P, 0, 0.0, [P]
    while b > 0.005:
        i = b * r; I += i
        pay = min(b + i, pm + extra)
        b = b + i - pay; m += 1; hist.append(max(b, 0))
    return pm, m, I, hist


if __name__ == "__main__":
    pm, mt, It, _ = amort(0)
    _, mn, In, _ = amort(EXTRA)
    print(round(pm, 2), mt, round(It, 2), mn, divmod(mn, 12), round(In, 2), round(It - In, 2), mt - mn, divmod(mt - mn, 12))
