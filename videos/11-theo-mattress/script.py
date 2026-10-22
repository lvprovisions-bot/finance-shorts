# THEO EXPLAINS #2: Inflation. Theo keeps $10,000 in his mattress because "cash can never lose value".
# Real figure: US CPI-U all items +3.7% over the 12 months to Sep 2026 (BLS CPI news release, 14 Oct 2026).
# Assumptions: illustration; $10,000 cash earning 0%; 10-year projection uses a flat 3% inflation a year
#   (rounded, below the latest 3.7% reading). Purchasing power only; ignores interest, taxes, theft risk.
# First line drafts (picked #3):
#   1 "My savings can't shrink. Ten thousand dollars, under my mattress!"
#   2 "I hid ten thousand dollars in my mattress so it can never shrink."
#   3 "Ten thousand dollars in my mattress. It can never lose value!"   <- number + wrong claim, no set-up
# Maths (python, see bottom):
#   last year: 10,000 / 1.037 = 9,643.20  -> today's $10,000 buys what $9,643 bought a year ago (-$357)
#   10 years @3%: 10,000 / 1.03**10 = 7,440.94 -> buys what $7,441 buys today ; lost 2,559.06 -> $2,559
#   (equivalently the same basket would cost 10,000 * 1.03**10 = $13,439 in ten years)
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("$10,000", "Ten thousand dollars"), ("IN MY", "in my"), ("MATTRESS.", "mattress."),
                    ("IT CAN", "It can"), ("NEVER LOSE", "never lose"), ("VALUE!", "value!")], 0.2),
    ("no",    "N", [("THEO.", "Theo."), ("IT ALREADY", "It already"), ("DID.", "did.")], 0.15),
    ("still", "T", [("IT STILL", "It still"), ("SAYS", "says"), ("TEN THOUSAND!", "ten thousand!")], 0.2),
    ("year",  "N", [("PRICES ROSE", "Prices rose"), ("3.7%", "three point seven percent"), ("LAST YEAR.", "last year."),
                    ("NOW IT BUYS", "Now it buys"), ("WHAT $9,643", "what ninety six hundred and forty three dollars"),
                    ("DID A", "did a"), ("YEAR AGO.", "year ago.")], 0.25),
    ("ten",   "N", [("AT 3%", "At three percent"), ("A YEAR,", "a year,"), ("IN TEN YEARS", "in ten years"),
                    ("IT BUYS", "it buys"), ("WHAT $7,441", "what seventy four hundred and forty one dollars"),
                    ("BUYS TODAY.", "buys today.")], 0.25),
    ("thief", "T", [("SO A THIEF", "So a thief"), ("TOOK $2,559", "took twenty five hundred and fifty nine dollars"),
                    ("AND I NEVER", "and I never"), ("HEARD A THING?", "heard a thing?")], 0.2),
    ("power", "N", [("CASH KEEPS", "Cash keeps"), ("ITS NUMBER,", "its number,"), ("NOT ITS", "not its"),
                    ("POWER.", "power.")], 0.25),
    ("punch", "T", [("FINE.", "Fine."), ("I'LL GET A", "I'll get a"), ("BIGGER", "bigger"), ("MATTRESS.", "mattress.")], 0.35),
    ("q",     "N", [("WHERE DOES", "Where does"), ("YOUR CASH", "your cash"), ("SLEEP?", "sleep?"),
                    ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.2),
    ("loop",  "T", [("RELAX.", "Relax."), ("IT'S SAFE.", "It's safe."), ("BECAUSE...", "Because...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    print(10000 / 1.037, 10000 - 10000 / 1.037)
    print(10000 / 1.03 ** 10, 10000 - 10000 / 1.03 ** 10, 10000 * 1.03 ** 10)
