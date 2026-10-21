# WHO WINS? #4 (UK test, £) — the Lifetime ISA price cap. Nora & Theo each pay the SAME £20,000 into a Lifetime ISA.
# Nora buys a £320,000 first flat (under the cap) and keeps the bonus. Theo falls for a £480,000 flat (over the
# £450,000 cap), so his withdrawal is "unauthorised" and pays the 25% charge on the WHOLE pot.
# Rules (GOV.UK "Lifetime ISA", pages checked 21 Oct 2026, last updated 30 Sep 2026): pay in up to £4,000/yr,
#   government bonus 25% (max £1,000/yr); first home must cost £450,000 or less, bought with a mortgage, at least
#   12 months after the first payment; any other withdrawal pays a 25% withdrawal charge.
# Assumptions (illustrative, on screen): both pay the max £4,000/yr for 5 years; cash only, interest/returns ignored.
# Maths (python, see bottom):
#   paid  = 4,000 * 5            = £20,000
#   bonus = 25% * 20,000         = £5,000   (= £1,000/yr, exactly the cap)
#   pot   = 20,000 + 5,000       = £25,000  -> Nora uses all £25,000 for her flat
#   Theo charge = 25% * 25,000   = £6,250   -> Theo gets £18,750
#   Theo vs what he paid in      = 18,750 - 20,000 = -£1,250 ; gap Nora vs Theo = £6,250
#   Theo's flat over the cap     = 480,000 - 450,000 = £30,000
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("NORA AND I", "Nora and I"), ("BOTH SAVED", "both saved"), ("£20,000", "twenty thousand pounds"),
                    ("IN A", "in a"), ("LIFETIME ISA.", "Lifetime eye-sa.")], 0.12),
    ("hook2", "N", [("I GOT", "I got"), ("£25,000.", "twenty five thousand."), ("THEO GOT", "Theo got"),
                    ("£18,750.", "eighteen thousand, seven hundred and fifty.")], 0.2),
    ("how",   "T", [("THAT'S LESS", "That's less"), ("THAN I", "than I"), ("PUT IN!", "put in!"), ("HOW?!", "How?!")], 0.25),
    ("rew",   "N", [("FIVE YEARS", "Five years"), ("AGO, WE", "ago, we"), ("BOTH STARTED.", "both started."),
                    ("£4,000", "Four thousand pounds"), ("A YEAR.", "a year."), ("THE MAX.", "The max.")], 0.2),
    ("bonus", "T", [("AND THE", "And the"), ("GOVERNMENT", "government"), ("ADDS 25%!", "adds twenty five percent!"),
                    ("£1,000", "A thousand pounds"), ("A YEAR,", "a year,"), ("FREE!", "free!")], 0.2),
    ("pot",   "N", [("FIVE YEARS", "Five years"), ("LATER, WE", "later, we"), ("EACH HAD", "each had"),
                    ("£25,000.", "twenty five thousand pounds.")], 0.25),
    ("nora",  "N", [("I BOUGHT", "I bought"), ("MY FIRST", "my first"), ("FLAT.", "flat."),
                    ("£320,000.", "Three hundred and twenty thousand."), ("BONUS", "Bonus"), ("KEPT.", "kept.")], 0.2),
    ("theo",  "T", [("AND I FOUND", "And I found"), ("MY DREAM", "my dream"), ("FLAT.", "flat."),
                    ("£480,000!", "Four hundred and eighty thousand!")], 0.2),
    ("limit", "N", [("THEO.", "Theo."), ("THE LIMIT", "The limit"), ("IS", "is"), ("£450,000.", "four hundred and fifty thousand.")], 0.2),
    ("so",    "T", [("ONLY", "Only"), ("£30K OVER.", "thirty grand over."), ("SO WHAT?", "So what?")], 0.2),
    ("charge","N", [("SO TAKING", "So taking"), ("IT OUT", "it out"), ("COSTS 25%.", "costs twenty five percent."),
                    ("OF", "Of"), ("EVERYTHING.", "everything.")], 0.2),
    ("fair",  "T", [("25% IN,", "Twenty five percent in,"), ("25% OUT.", "twenty five percent out."),
                    ("THAT'S", "That's"), ("EVEN!", "even!")], 0.2),
    ("maths", "N", [("NOPE.", "Nope."), ("A QUARTER", "A quarter"), ("OF £25,000", "of twenty five thousand"),
                    ("IS £6,250.", "is six thousand, two hundred and fifty."), ("YOUR BONUS", "Your bonus"),
                    ("WAS £5,000.", "was five thousand.")], 0.2),
    ("punch", "T", [("SO I PAID", "So I paid"), ("£1,250", "twelve hundred and fifty pounds..."),
                    ("TO USE", "to use"), ("MY OWN", "my own"), ("MONEY?", "money?")], 0.2),
    ("lesson","N", [("CHECK THE", "Check the"), ("PRICE CAP", "price cap"), ("BEFORE YOU", "before you"),
                    ("FALL IN LOVE.", "fall in love.")], 0.2),
    ("q",     "N", [("WOULD YOU", "Would you"), ("HAVE SPOTTED", "have spotted"), ("THE LIMIT?", "the limit?"), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("BECAUSE", "Because"), ("NORA AND I", "Nora and I"), ("BOTH SAVED...", "both saved...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.08

if __name__ == "__main__":
    paid = 4000 * 5; bonus = 0.25 * paid; pot = paid + bonus; charge = 0.25 * pot; theo = pot - charge
    assert bonus / 5 <= 1000
    print(paid, bonus, pot, charge, theo, theo - paid, pot - theo, 480000 - 450000)
