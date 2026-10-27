# WHO WINS? #6 — debt vs investing. Nora & Theo each get the SAME $10,000 bonus and each owe the SAME $10,000 on a
# credit card. Nora pays the card off. Theo invests the bonus and keeps the card balance, paying only the interest.
# Real-world figure (web-searched 27 Oct 2026): Federal Reserve G.19 Consumer Credit (release 7 Oct 2026):
#   commercial-bank credit card plans, accounts assessed interest, Q2 2026 = 22.15% APR.
# Theo's 7%/yr investment return is an ASSUMPTION (stated on screen, not guaranteed).
# Assumptions (on screen): one year; Theo pays interest only (balance stays $10,000), interest = APR x balance
#   (22.15%/12 a month, paid monthly, no compounding); investment +7% over the year; no taxes, no fees.
# Maths (python, see bottom):
#   Theo's interest: 10,000 * 0.2215 = $2,215 (= $184.58/month)
#   Theo's gain:     10,000 * 0.07   = $700
#   Theo is behind Nora by 2,215 - 700 = $1,515 after one year (Nora: no debt, no interest, no investments).
#   Line 'why': paying off a 22.15% card = a guaranteed 22.15% "return" (interest you no longer pay).
# First line (3 drafts):
#   (a) "Theo invested his $10K bonus. It cost him $1,515."
#   (b) "Same $10K bonus. I paid off my card. Theo invested his. He's $1,515 behind."
#   (c) "Theo invested while owing 22% on a credit card. Bad idea."
#   -> picked (b): conflict + number in one breath, and "Same $10K bonus..." loops from the last line.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",   "N", [("SAME", "Same"), ("$10K BONUS.", "ten K bonus."), ("I PAID OFF", "I paid off"), ("MY CARD.", "my card."),
                     ("THEO", "Theo"), ("INVESTED HIS.", "invested his.")], 0.15),
    ("brag",   "T", [("STOCKS", "Stocks"), ("MAKE 7%!", "make seven percent!"), ("I'M A", "I'm a"), ("GENIUS.", "genius.")], 0.15),
    ("apr",    "N", [("YOUR CARD", "Your card"), ("CHARGES", "charges"), ("22%.", "twenty two percent.")], 0.1),
    ("oh",     "T", [("...OH.", "Oh.")], 0.2),
    ("year",   "N", [("ONE YEAR:", "One year:"), ("YOU MADE", "you made"), ("$700.", "seven hundred."),
                     ("INTEREST", "Interest"), ("TOOK", "took"), ("$2,215.", "twenty two fifteen.")], 0.15),
    ("result", "N", [("YOU'RE", "You're"), ("$1,515", "fifteen hundred fifteen dollars"), ("BEHIND ME.", "behind me.")], 0.2),
    ("why",    "N", [("PAYING OFF", "Paying off"), ("A 22% CARD", "a twenty two percent card"), ("IS A", "is a"),
                     ("GUARANTEED", "guaranteed"), ("22% RETURN.", "twenty two percent return.")], 0.15),
    ("punch",  "T", [("SO I", "So I"), ("INVESTED...", "invested..."), ("IN MY", "in my"), ("CARD COMPANY.", "credit card company.")], 0.2),
    ("q",      "N", [("CARD FIRST", "Card first"), ("OR INVEST", "or invest"), ("FIRST?", "first?"), ("TELL ME.", "Tell me.")], 0.1),
    ("loop",   "T", [("SAME", "Same"), ("$10K BONUS...", "ten K bonus...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.1

if __name__ == "__main__":
    interest = 10_000 * 0.2215
    gain = 10_000 * 0.07
    print(round(interest, 2), round(interest / 12, 2), gain, round(interest - gain, 2))
