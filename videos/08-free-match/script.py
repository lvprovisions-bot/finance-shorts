# WHO WINS? #3 — the 401(k) match. Nora & Theo save the SAME $300/month. Nora saves hers in her 401(k) with an
# employer match; Theo keeps his in his own account "to stay flexible". Same effort, very different result.
# Assumptions (illustrative, shown on screen): $60,000 salary each; both save 6% = $3,600/yr ($300/mo);
#   Nora's employer matches 50 cents per $1 on the first 6% of pay -> +$1,800/yr ($150/mo), fully vested;
#   both invested at the same 7%/yr average return, contributions at year end, 25 years; before taxes & fees.
# Maths (python, see bottom): annuity factor ((1.07**25 - 1) / 0.07) = 63.249
#   Theo  = 3,600 * 63.249 = $227,697   (put in $90,000)
#   Nora  = 5,400 * 63.249 = $341,545   (put in $90,000 + $45,000 from employer)
#   Gap   = 1,800 * 63.249 = $113,848  -> "$114,000"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("NORA AND I", "Nora and I"), ("SAVE THE", "save the"), ("SAME", "same"), ("$300", "three hundred"),
                    ("A MONTH.", "a month.")], 0.12),
    ("hook2", "N", [("BUT I'LL", "But I'll"), ("END UP", "end up"), ("$114,000", "a hundred and fourteen thousand"),
                    ("RICHER.", "richer.")], 0.2),
    ("how",   "T", [("HOW?!", "How?!"), ("SAME SALARY.", "Same salary."), ("SAME SAVINGS!", "Same savings!")], 0.2),
    ("nora",  "N", [("MINE GOES", "Mine goes"), ("IN MY", "in my"), ("401(K).", "four oh one k."),
                    ("MY BOSS", "My boss"), ("ADDS 50¢", "adds fifty cents"), ("FOR EVERY $1.", "for every dollar."),
                    ("FREE MONEY.", "Free money.")], 0.2),
    ("theo",  "T", [("MINE STAYS", "Mine stays"), ("IN MY OWN", "in my own"), ("ACCOUNT.", "account."),
                    ("FLEXIBLE!", "Flexible!")], 0.2),
    ("grow",  "N", [("25 YEARS", "Twenty five years"), ("AT 7%.", "at seven percent."),
                    ("THEO:", "Theo,"), ("$228,000.", "two hundred and twenty eight thousand."),
                    ("ME:", "Me,"), ("$342,000.", "three hundred and forty two thousand.")], 0.25),
    ("punch", "T", [("SO I SKIPPED", "So I skipped"), ("A FREE RAISE?", "a free raise?")], 0.1),
    ("every", "N", [("EVERY.", "Every."), ("SINGLE.", "single."), ("YEAR.", "year.")], 0.25),
    ("q",     "N", [("DOES YOUR", "Does your"), ("BOSS MATCH?", "boss match?"), ("GO CHECK.", "Go check.")], 0.15),
    ("loop",  "T", [("BUT NORA", "But Nora"), ("AND I", "and I"), ("SAVE THE", "save the"), ("SAME...", "same...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.14

if __name__ == "__main__":
    f = (1.07 ** 25 - 1) / 0.07
    print(round(f, 3), round(3600 * f), round(5400 * f), round(1800 * f))
