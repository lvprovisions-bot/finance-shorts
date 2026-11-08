# THEO EXPLAINS #11: the Rule of 72 (8 Nov review idea #1 teaser: "Theo thinks 7% doubles money in 72 years").
# New angle vs 27 (compound vs simple growth): doubling TIME. Theo misreads the Rule of 72 as "money doubles in 72 years".
# Nora: you DIVIDE 72 by the rate: 72 / 7 = 10.3 -> about 10 years (exact at 7% compounded yearly: ln2/ln1.07 = 10.24 yrs).
# Doubling ladder from $10,000: $20K (~10.2 yrs), $40K (~20.5), $80K (~30.7), ... 7 doublings by ~71.7 yrs.
# In 72 years: 10,000 * 1.07**72 = $1,305,065 ("about 1.3 million"), not $20,000.
# Lower rate check: 72 / 6 = 12 yrs (exact ln2/ln1.06 = 11.90).
# Illustration only: example 7% a year (not a forecast, returns vary and can be negative), compounded yearly,
# no fees, taxes, withdrawals or new deposits. Rule of 72 is an estimate. No external statistics used.
# Maths (python, see bottom).
# First line drafts (picked #1):
#   1 "Rule of seventy-two! At seven percent, my ten grand doubles in seventy-two years!"  <- wrong claim + numbers, frame 0
#   2 "Seventy-two years to turn ten grand into twenty? Thanks, Rule of seventy-two."
#   3 "My money doubles when I'm seventy-two. That's the rule!"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("RULE OF 72!", "Rule of seventy-two!"), ("AT 7%,", "At seven percent,"), ("MY $10K", "my ten grand"),
                    ("DOUBLES", "doubles"), ("IN 72", "in seventy-two"), ("YEARS!", "years!")], 0.12),
    ("no",    "N", [("THEO.", "Theo."), ("YOU", "You"), ("DIVIDE.", "divide."), ("72", "Seventy-two"), ("OVER 7.", "over seven."),
                    ("ABOUT", "About"), ("TEN YEARS.", "ten years.")], 0.1),
    ("ladder","N", [("TEN YEARS,", "Ten years,"), ("$20K.", "twenty grand."), ("TWENTY,", "Twenty,"), ("$40K.", "forty."),
                    ("THIRTY,", "Thirty,"), ("$80K.", "eighty.")], 0.1),
    ("big",   "N", [("BY YEAR 72,", "By year seventy-two,"), ("IT DOUBLED", "it doubled"), ("SEVEN TIMES.", "seven times."),
                    ("$1.3", "One point three"), ("MILLION.", "million.")], 0.15),
    ("punch", "T", [("SO THE 72", "So the seventy-two"), ("WAS", "was"), ("MATH?", "math?"), ("I THOUGHT", "I thought"),
                    ("IT WAS", "it was"), ("A DEADLINE.", "a deadline.")], 0.15),
    ("fix",   "N", [("AT 6%?", "At six percent?"), ("72 OVER 6.", "Seventy-two over six."), ("TWELVE", "Twelve"), ("YEARS.", "years.")], 0.12),
    ("q",     "N", [("WHAT'S", "What's"), ("YOUR", "your"), ("RATE?", "rate?"), ("DIVIDE IT.", "Divide it."), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("RULE OF 72!", "Rule of seventy-two!"), ("AT 7%...", "At seven percent...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    import math
    print("72/7", 72 / 7, "exact", math.log(2) / math.log(1.07))
    print("72 yrs", round(10000 * 1.07 ** 72, 2), "doublings", 72 / (math.log(2) / math.log(1.07)))
    print("72/6", 72 / 6, "exact", math.log(2) / math.log(1.06))
    for k in range(1, 8): print(10000 * 2 ** k, round(k * math.log(2) / math.log(1.07), 2))
