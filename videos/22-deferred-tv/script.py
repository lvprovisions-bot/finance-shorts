# WHO WINS? #9 — deferred interest ("0%") store-card trap, timely for Black Friday (27 Nov 2026).
# Nora & Theo buy the SAME $1,200 TV on the SAME "no interest for 12 months" store-card deal.
# Nora pays $100/mo; Theo pays $99/mo to "save" a dollar a month, so after 12 months he still owes $12.
# Real-world anchors:
#   CFPB (consumerfinance.gov/ask-cfpb, what is a deferred interest promotion): if not paid off by the end of the period,
#     "you would owe all of the interest back to the original date of the charge"; "Usually, the interest is calculated
#     based on the balance you owed in each month since you first made the purchase."
#   Bankrate Retail Cards Study (15 Sep 2025; 110 cards surveyed 21 Jul 2025): average retail card APR 30.14% -> 30% used.
# Assumptions (on screen): deferred-interest store card, 30% APR, interest = month's balance x 30%/12 with no compounding
#   (daily compounding would be higher, ~$237, so this is conservative). True 0% APR offers do NOT back-charge.
# Maths (python, see bottom):
#   Theo balances 1200, 1101, ... 111 -> monthly interest 30.00, 27.53, ... 2.77, total $196.65 (~$197). Left after 12 pays: $12.
#   Nora: 12 x $100 = $1,200, interest $0. Theo's TV: 1,188 + 12 + 196.65 = $1,396.65 (~$1,397).
#   Theo "saved" $1/mo x 12 = $12.
# First line (3 drafts):
#   (a) "Same $1,200 TV. Theo was twelve dollars short and paid $197."
#   (b) "Theo missed by twelve dollars. The store charged him a hundred ninety-seven."
#   (c) "Zero percent interest just cost Theo a hundred ninety-seven dollars."
#   -> picked (b): the conflict and both numbers in the first 4 s, and "missed by twelve dollars" loops from the last line.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "N", [("THEO", "Theo"), ("MISSED", "missed"), ("BY $12.", "by twelve dollars."),
                    ("THE STORE", "The store"), ("CHARGED HIM", "charged him"), ("$197.", "a hundred ninety-seven.")], 0.15),
    ("huh",   "T", [("BUT THE TV", "But the TV"), ("WAS 0%!", "was zero percent!")], 0.15),
    ("deal",  "N", [("SAME", "Same"), ("$1,200 TV.", "twelve hundred dollar TV."), ("SAME DEAL:", "Same deal:"),
                    ("NO INTEREST", "no interest"), ("FOR 12", "for twelve"), ("MONTHS.", "months.")], 0.1),
    ("pay",   "N", [("I PAID", "I paid"), ("$100", "a hundred"), ("A MONTH.", "a month."),
                    ("YOU PAID", "You paid"), ("$99.", "ninety-nine.")], 0.1),
    ("m12",   "N", [("MONTH 12:", "Month twelve:"), ("I OWE", "I owe"), ("$0.", "nothing."),
                    ("YOU OWE", "You owe"), ("$12.", "twelve.")], 0.1),
    ("only",  "T", [("IT'S ONLY", "It's only"), ("$12!", "twelve bucks!")], 0.1),
    ("catch", "N", [("SMALL PRINT:", "Small print:"), ("IF PAID", "if paid"), ("IN FULL.", "in full."),
                    ("MISS IT,", "Miss it,"), ("THEY", "they"), ("BACK-CHARGE", "back-charge"),
                    ("ALL 12", "all twelve"), ("MONTHS.", "months.")], 0.1),
    ("total", "N", [("INTEREST:", "Interest:"), ("ME $0.", "me, zero."), ("YOU", "You,"), ("$197.", "a hundred ninety-seven.")], 0.15),
    ("punch", "T", [("BEST $12", "Best twelve bucks"), ("I EVER", "I ever"), ("SAVED.", "saved.")], 0.2),
    ("q",     "N", [("WOULD YOU", "Would you"), ("TRUST 0%?", "trust zero percent?"), ("TELL ME.", "Tell me.")], 0.1),
    ("loop",  "T", [("I MISSED", "I missed"), ("BY $12...", "by twelve dollars...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.1

if __name__ == "__main__":
    P, R = 1200, 0.30
    months = [(P - 99 * m) * R / 12 for m in range(12)]
    print([round(x, 2) for x in months], round(sum(months), 2), P - 99 * 12, round(P + sum(months), 2))
