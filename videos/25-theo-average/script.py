# THEO EXPLAINS #9: average return vs actual return (1 Nov review idea #3, new angle vs 17: it is about the AVERAGE, not "half back").
# Theo's made-up fund went +60% then -40%. He adds up the percentages himself: (60 - 40) / 2 = +10% "a year", so he expects $12,100.
# Nora opens the statement: $9,600. He gained $6,000 on $10,000, then lost $6,400 on $16,000. Real result -$400, about -2% a year.
# Illustration only (no real fund, no external statistics): $10,000, no fees, taxes or dividends.
# Maths (python, see bottom):
#   Year 1: 10,000 * 1.60 = 16,000 (+6,000)
#   Year 2: 16,000 * 0.60 =  9,600 (-6,400)
#   Simple average: (60 + (-40)) / 2 = +10%
#   Theo's maths: 10,000 * 1.10^2 = 12,100; statement 9,600; gap 2,500
#   Real (compound) return: (9,600 / 10,000)^(1/2) - 1 = -2.02% a year
# First line drafts (picked #1):
#   1 "My fund averaged ten percent a year! So my ten grand is now twelve thousand one hundred!"  <- number + wrong claim
#   2 "Ten percent a year for two years, and my statement says I lost money. Typo!"
#   3 "Ten percent average! Can you believe how rich I am?"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("MY FUND", "My fund"), ("AVERAGED", "averaged"), ("10%", "ten percent"), ("A YEAR!", "a year!"),
                    ("SO MY $10,000", "So my ten grand"), ("IS NOW", "is now"), ("$12,100!", "twelve thousand one hundred!")], 0.12),
    ("no",    "N", [("THEO.", "Theo."), ("OPEN THE", "Open the"), ("STATEMENT.", "statement."), ("$9,600.", "Nine thousand six hundred.")], 0.12),
    ("up",    "N", [("YEAR ONE,", "Year one,"), ("UP 60%.", "up sixty percent."), ("$16,000.", "Sixteen thousand.")], 0.08),
    ("down",  "N", [("YEAR TWO,", "Year two,"), ("DOWN 40%.", "down forty percent."), ("$9,600.", "Nine thousand six hundred.")], 0.12),
    ("avg",   "N", [("YOUR", "Your"), ("AVERAGE", "average"), ("WENT UP.", "went up."), ("YOUR", "Your"), ("MONEY", "money"), ("WENT DOWN.", "went down.")], 0.12),
    ("why",   "N", [("YOU MADE", "You made"), ("$6,000,", "six thousand,"), ("THEN LOST", "then lost"), ("$6,400.", "six thousand four hundred."),
                    ("THE REAL", "The real"), ("RETURN:", "return,"), ("MINUS 2%", "minus two percent"), ("A YEAR.", "a year.")], 0.2),
    ("punch", "T", [("FINE.", "Fine."), ("CAN I", "Can I"), ("PAY MY", "pay my"), ("RENT", "rent"), ("IN AVERAGES?", "in averages?")], 0.25),
    ("q",     "N", [("DO YOU", "Do you"), ("CHECK", "check"), ("DOLLARS", "dollars"), ("OR", "or"), ("PERCENTAGES?", "percentages?"), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("WAIT.", "Wait."), ("MY FUND", "My fund"), ("AVERAGED 10%...", "averaged ten percent...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    s = 10000; a = s * 1.6; b = a * .6
    print("y1", a, a - s, "y2", b, b - a, "avg", (60 - 40) / 2, "theo", round(s * 1.1 ** 2, 2), "gap", round(s * 1.1 ** 2 - b, 2), "cagr %", round(((b / s) ** .5 - 1) * 100, 2))
