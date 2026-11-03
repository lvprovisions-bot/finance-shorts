# THEO EXPLAINS #8: monthly rate vs APR. Theo sees "2%" on his credit card, carries $5,000 and thinks that's $100 a year.
# Nora: it's 2% a MONTH. $100 every month, $1,200 a year, 24% APR, and if he only pays the interest he still owes all $5,000.
# Illustration only (no real product): $5,000 balance, 2% monthly rate, interest paid monthly, no fees.
# Real-world anchor on screen: Fed G.19 credit card rate for accounts assessed interest (see meta / description).
# Maths (python, see bottom):
#   Theo: 5,000 * .02 = 100 "a year"
#   Real: 5,000 * .02 = 100 a month -> * 12 = 1,200 a year (12x Theo's number) -> 2% * 12 = 24% APR
#   Balance after 12 interest-only payments: 5,000 (unchanged)
#   (If interest were left unpaid instead it would compound: 5,000 * (1.02^12 - 1) = 1,341; not used on screen.)
#   Simplified: real cards charge a daily rate and require a minimum payment.
# First line drafts (picked #1):
#   1 "Only two percent on my credit card! Five grand, so a hundred bucks a year!"  <- number + wrong claim
#   2 "A hundred bucks a year. That's all my five thousand dollar card balance costs me!"
#   3 "Two percent interest? My credit card's cheaper than my savings account!"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("ONLY 2%", "Only two percent"), ("ON MY", "on my"), ("CREDIT CARD!", "credit card!"),
                    ("$5,000?", "Five grand?"), ("THAT'S $100", "That's a hundred bucks"), ("A YEAR!", "a year!")], 0.15),
    ("no",    "N", [("THEO.", "Theo."), ("READ", "Read"), ("THE SMALL", "the small"), ("PRINT.", "print."), ("2%", "Two percent"), ("A MONTH.", "a month.")], 0.12),
    ("math",  "N", [("THAT'S $100", "That's a hundred dollars,"), ("EVERY", "every"), ("MONTH.", "month."),
                    ("$1,200", "Twelve hundred"), ("A YEAR.", "a year.")], 0.12),
    ("apr",   "N", [("THE REAL", "The real"), ("NUMBER:", "number,"), ("24% APR.", "twenty four percent A P R.")], 0.12),
    ("owe",   "N", [("AND IF YOU", "And if you"), ("ONLY PAY", "only pay"), ("THE INTEREST,", "the interest,"),
                    ("YOU STILL", "you still"), ("OWE", "owe"), ("$5,000.", "five thousand.")], 0.15),
    ("punch", "T", [("SO I'M", "So I'm"), ("PAYING RENT", "paying rent"), ("ON MONEY", "on money"), ("I ALREADY", "I already"), ("SPENT?", "spent?")], 0.3),
    ("q",     "N", [("WHAT'S", "What's"), ("YOUR CARD'S", "your card's"), ("APR?", "A P R?"), ("GO CHECK.", "Go check."), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("WAIT.", "Wait."), ("ONLY 2%...", "Only two percent...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    b, r = 5000, .02
    print("monthly", b * r, "yearly", b * r * 12, "APR", r * 12, "ratio", 12, "compound-if-unpaid", round(b * (1.02 ** 12 - 1), 2))
