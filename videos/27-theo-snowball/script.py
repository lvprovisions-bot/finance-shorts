# THEO EXPLAINS #10: simple vs compound growth (new topic: compounding itself; 04-twins was about starting age, 17/25 about losses).
# Theo multiplies 7% x 30 years = 210% and expects $10,000 -> $31,000. Nora: compounded yearly it is $76,123.
# Year 1 earns $700 (7% of $10,000); year 30 earns $4,980 (7% of $71,143) -> interest earns interest ("snowballs").
# Theo was wrong by $45,123, in his favour. Illustration only: example 7% a year (not a forecast, real returns vary and
# can be negative), compounded yearly, no fees, taxes, withdrawals or new deposits. No external statistics used.
# Maths (python, see bottom):
#   Theo:  10,000 * (1 + 0.07*30)   = 31,000
#   Real:  10,000 * 1.07**30        = 76,122.55
#   Y1 interest  = 700.00 ; Y30 interest = 0.07 * 71,142.57 = 4,979.98
#   Gap: 76,122.55 - 31,000 = 45,122.55
# First line drafts (picked #1):
#   1 "Seven percent a year for thirty years is two hundred ten percent! My ten grand becomes thirty-one thousand!"  <- number + wrong claim
#   2 "Thirty years at seven percent? Easy. Thirty-one thousand. Did it in my head."
#   3 "My ten grand will only be thirty-one K at retirement. Investing is overrated."
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("7% A YEAR", "Seven percent a year"), ("FOR 30 YEARS", "for thirty years"), ("IS 210%!", "is two hundred ten percent!"),
                    ("MY $10,000", "My ten grand"), ("BECOMES", "becomes"), ("$31,000!", "thirty-one thousand!")], 0.12),
    ("no",    "N", [("THEO.", "Theo."), ("IT'S", "It's"), ("$76,000.", "seventy-six thousand.")], 0.12),
    ("y1",    "N", [("YEAR ONE,", "Year one,"), ("YOU EARN", "you earn"), ("$700.", "seven hundred dollars.")], 0.08),
    ("y30",   "N", [("YEAR 30,", "Year thirty,"), ("YOU EARN", "you earn"), ("ALMOST", "almost"), ("$5,000.", "five thousand."),
                    ("SAME", "Same"), ("7%.", "seven percent.")], 0.12),
    ("why",   "N", [("YOUR", "Your"), ("INTEREST", "interest"), ("EARNS", "earns"), ("INTEREST.", "interest."), ("IT", "It"), ("SNOWBALLS.", "snowballs.")], 0.2),
    ("punch", "T", [("SO I WAS", "So I was"), ("WRONG BY", "wrong by"), ("$45,000...", "forty-five thousand dollars..."), ("IN MY", "in my"), ("FAVOR?", "favor?")], 0.12),
    ("fix",   "N", [("ONLY IF", "Only if"), ("YOU", "you"), ("LEAVE IT", "leave it"), ("ALONE.", "alone.")], 0.2),
    ("q",     "N", [("DID YOU", "Did you"), ("GUESS", "guess"), ("31", "thirty-one"), ("OR 76?", "or seventy-six?"), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("WAIT.", "Wait."), ("7% A YEAR", "Seven percent a year"), ("FOR 30 YEARS...", "for thirty years...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    s = 10000; r = .07; v = s; ints = []
    for y in range(30):
        ints.append(v * r); v *= 1 + r
    print("theo", s * (1 + r * 30), "real", round(v, 2), "y1", round(ints[0], 2), "y30", round(ints[-1], 2), "gap", round(v - s * (1 + r * 30), 2))
