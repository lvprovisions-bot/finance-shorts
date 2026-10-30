# THEO EXPLAINS #6: FSA "use it or lose it". Theo thinks his leftover FSA money rolls over forever (he's mixing it up with an HSA).
# Real figures (IRS Rev. Proc. 2025-32, Oct 2025; reported by Mercer/Newfront etc.):
#   2026 health FSA salary-reduction limit = $3,400; max carryover from a 2026 plan year (only if the plan offers carryover) = $680.
#   Plans may instead offer a grace period (up to 2.5 months) or neither. HSA balances roll over indefinitely.
# Story (illustration): Theo put in the 2026 max $3,400, spent $1,400 -> $2,000 left at year end.
#   carry = min(2000, 680) = 680 ; forfeited = 2000 - 680 = 1,320
#   (side check, not in video: tax saved on $3,400 at 22% + 7.65% FICA = $1,008 < $1,320 forfeited)
# First line drafts (picked #1):
#   1 "Two grand left in my FSA? It rolls over forever!"   <- number + wrong claim, first words
#   2 "My FSA is just like an HSA. It's mine forever!"
#   3 "Unspent FSA money? Free money for next year!"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("TWO GRAND", "Two grand"), ("LEFT IN", "left in"), ("MY FSA?", "my F S A?"), ("IT ROLLS", "It rolls"),
                    ("OVER", "over"), ("FOREVER!", "forever!")], 0.15),
    ("no",    "N", [("THEO,", "Theo,"), ("THAT'S AN", "that's an"), ("HSA.", "H S A."), ("AN FSA IS", "An F S Eh is"),
                    ("USE IT", "use it"), ("OR LOSE IT.", "or lose it.")], 0.12),
    ("carry", "N", [("IF YOUR", "If your"), ("PLAN ALLOWS,", "plan allows,"), ("ONLY $680", "only six eighty"), ("CARRIES", "carries"), ("OVER.", "over.")], 0.12),
    ("lose",  "N", [("THE OTHER", "The other"), ("$1,320?", "thirteen twenty?"), ("GONE", "Gone"), ("AFTER THE", "after the"), ("DEADLINE.", "deadline.")], 0.15),
    ("panic", "T", [("THEN I'LL", "Then I'll"), ("BUY 100", "buy a hundred"), ("BOTTLES OF", "bottles of"), ("SUNSCREEN!", "sunscreen!")], 0.12),
    ("fix",   "N", [("OR NEXT", "Or next"), ("YEAR, PUT IN", "year, put in"), ("ONLY WHAT", "only what"), ("YOU'LL", "you'll"), ("SPEND.", "spend.")], 0.2),
    ("punch", "T", [("SO FSA", "So F S Eh"), ("MEANS...", "means..."), ("FORFEIT", "Forfeit"), ("SPENDING", "Spending"), ("ACCOUNT.", "Account.")], 0.3),
    ("q",     "N", [("GOT AN FSA?", "Got an F S A?"), ("CHECK YOUR", "Check your"), ("DEADLINE", "deadline"), ("AND TELL", "and tell"), ("US BELOW.", "us below.")], 0.15),
    ("loop",  "T", [("WAIT.", "Wait."), ("TWO GRAND", "Two grand"), ("LEFT IN", "left in"), ("MY FSA...", "my F S A...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    limit, carry_max, spent = 3400, 680, 1400
    left = limit - spent; carry = min(left, carry_max); lost = left - carry
    print("left", left, "carry", carry, "forfeited", lost)
    print("tax saved at 22%+7.65%", round(limit * (0.22 + 0.0765), 2))
