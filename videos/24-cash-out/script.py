# WHO WINS? #10 — cashing out a 401(k) when changing jobs vs rolling it over.
# Nora & Theo, both 35, both change jobs with the SAME $30,000 traditional 401(k). Nora does a direct rollover; Theo cashes out.
# Real-world anchors:
#   IRS "Retirement topics - Exceptions to tax on early distributions" (irs.gov): distributions before 59 1/2 generally owe
#     a 10% additional tax on top of income tax, with exceptions.
#   IRS Topic 413 (rollovers): a direct rollover is not taxed now.
#   IRS 2026 brackets (Rev. Proc. 2025-32): 22% applies to single-filer taxable income $50,400-$105,700.
# Assumptions (on screen): 22% federal bracket on the whole $30K, no state tax (state tax would make it worse), 7%/yr return,
#   30 years, no new contributions, before tax at retirement. Illustration only, 7% is not a guarantee.
# Maths (python, see bottom):
#   penalty 30,000 x 10% = 3,000; income tax 30,000 x 22% = 6,600; Theo keeps 20,400.
#   Nora 30,000 x 1.07^30 = 228,367.65 -> ~$228K (pre-tax). Theo spends his on a jet ski -> $0.
# First line (3 drafts):
#   (a) "Theo took thirty grand out of his 401k and only got twenty."
#   (b) "Theo cashed out thirty grand. It cost him two hundred twenty-eight thousand."
#   (c) "One form at a job change cost Theo two hundred twenty-eight thousand dollars."
#   -> picked (b): action + both numbers immediately, and it loops from the last line.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "N", [("THEO", "Theo"), ("CASHED OUT", "cashed out"), ("$30K.", "thirty grand."),
                    ("IT COST", "It cost"), ("HIM", "him"), ("$228K.", "two hundred twenty-eight thousand.")], 0.15),
    ("huh",   "T", [("IT'S", "It's"), ("MY MONEY!", "my money!")], 0.15),
    ("same",  "N", [("SAME", "Same"), ("JOB CHANGE.", "job change."), ("SAME", "Same"), ("$30K", "thirty K"),
                    ("401(K).", "four oh one kay.")], 0.1),
    ("choice","N", [("I", "I"), ("ROLLED", "rolled"), ("MINE OVER.", "mine over."),
                    ("YOU", "You"), ("CASHED", "cashed"), ("YOURS OUT.", "yours out.")], 0.1),
    ("cut",   "N", [("10%", "Ten percent"), ("PENALTY:", "penalty:"), ("$3,000.", "three grand."),
                    ("TAX:", "Tax:"), ("$6,600.", "sixty-six hundred."),
                    ("YOU GOT", "You got"), ("$20,400.", "twenty thousand four hundred.")], 0.1),
    ("ski",   "T", [("STILL", "Still"), ("BOUGHT", "bought"), ("A JET SKI!", "a jet ski!")], 0.1),
    ("grow",  "N", [("30 YEARS", "Thirty years"), ("AT 7%:", "at seven percent:"), ("MINE", "mine"), ("HITS", "hits"),
                    ("$228K.", "two hundred twenty-eight thousand."), ("YOURS?", "Yours?")], 0.2),
    ("punch", "T", [("THE JET SKI", "The jet ski"), ("SANK.", "sank.")], 0.25),
    ("q",     "N", [("WOULD YOU", "Would you"), ("CASH OUT?", "cash out?"), ("TELL ME.", "Tell me.")], 0.1),
    ("loop",  "T", [("I CASHED OUT", "I cashed out"), ("$30K...", "thirty grand...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.1

if __name__ == "__main__":
    P = 30000
    pen, tax = P * 0.10, P * 0.22
    print(pen, tax, P - pen - tax, round(P * 1.07 ** 30, 2))
