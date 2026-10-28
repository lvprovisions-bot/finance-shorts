# THEO EXPLAINS #5: Percentages in investing. Theo thinks -50% then +50% puts him back to even.
# Pure illustration (no external statistics): hypothetical $10,000, no fees, dividends or taxes.
# First line drafts (picked #3):
#   1 "Down fifty, up fifty. Back to even, baby!"
#   2 "Minus fifty percent plus fifty percent equals zero. Easy."
#   3 "My $10K fell 50%, then rose 50%. I'm back to even!"   <- numbers + wrong claim, first words
# Maths (python, see bottom):
#   10,000 x 0.5 = 5,000 ; 5,000 x 1.5 = 7,500 -> still $2,500 down
#   gain needed to recover from -50%: 10,000 / 5,000 - 1 = +100%
#   reverse order: 10,000 x 1.5 = 15,000 ; 15,000 x 0.5 = 7,500 (same result)
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("MY $10K", "My ten K"), ("FELL 50%,", "fell fifty percent,"), ("THEN ROSE", "then rose"),
                    ("50%.", "fifty percent."), ("BACK TO", "I'm back to"), ("EVEN!", "even!")], 0.15),
    ("no",    "N", [("THEO.", "Theo."), ("CHECK", "Check"), ("THE MATH.", "the math.")], 0.12),
    ("drop",  "N", [("DOWN 50%:", "Down fifty percent:"), ("$10,000", "ten thousand"), ("BECOMES", "becomes"), ("$5,000.", "five thousand.")], 0.12),
    ("up",    "N", [("UP 50%", "Up fifty percent"), ("OF $5,000?", "of five thousand?"), ("ONLY", "Only"), ("$2,500", "twenty five hundred"), ("MORE.", "more.")], 0.12),
    ("total", "N", [("SO YOU HAVE", "So you have"), ("$7,500.", "seventy five hundred."), ("TO GET BACK,", "To get back,"),
                    ("YOU NEEDED", "you needed"), ("+100%.", "plus one hundred percent.")], 0.15),
    ("flip",  "T", [("FINE!", "Fine!"), ("NEXT TIME", "Next time"), ("I'LL GO", "I'll go"), ("UP FIRST.", "up first.")], 0.12),
    ("flip2", "N", [("$15,000,", "Fifteen thousand,"), ("THEN HALF", "then half"), ("OF THAT...", "of that..."), ("STILL", "still"), ("$7,500.", "seventy five hundred.")], 0.2),
    ("punch", "T", [("SO MATH", "So math"), ("OWES ME", "owes me"), ("$2,500.", "twenty five hundred dollars.")], 0.3),
    ("q",     "N", [("DID YOU", "Did you"), ("SPOT IT?", "spot it?"), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("WAIT.", "Wait."), ("MY $10K", "My ten K"), ("FELL 50%...", "fell fifty percent...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    a = 10_000
    down = a * 0.5; up = down * 1.5
    print("down", down, "up", up, "loss", a - up, "needed gain %", (a / down - 1) * 100)
    r = a * 1.5 * 0.5
    print("reverse", a * 1.5, r)
