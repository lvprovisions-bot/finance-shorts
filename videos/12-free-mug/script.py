# WHO WINS? #4 — savings account interest. Nora & Theo each keep the SAME $10,000 emergency fund in savings.
# Theo leaves his at his big bank (it gave him a free mug); Nora moved hers to a high-yield savings account.
# Real-world figures (web-searched 23 Oct 2026):
#   FDIC "National Rates and Rate Caps", published 19 Oct 2026 (month-end Sep data): national average savings rate 0.38%.
#   Leading online high-yield savings accounts paid roughly 3.1%-4.05% APY in Sep/Oct 2026 -> we ASSUME 3.5% (mid-range).
# Assumptions (on screen): $10,000 each, rates treated as APY and held constant, interest left in the account, before tax.
# Maths (python, see bottom):
#   Year 1: Theo 10,000*0.0038 = $38 ; Nora 10,000*0.035 = $350 ; gap $312 ; ratio 9.2x ("9 times")
#   5 yrs:  Theo 10,000*(1.0038**5-1) = $191 ; Nora 10,000*(1.035**5-1) = $1,877 ; gap $1,685 ("almost $1,700")
# First line (3 drafts): (a) "Theo's bank gave him a free mug. It cost him $312."  (b) "Nora and I saved the same ten grand..."
#   (c) "Same ten grand. My bank paid me $350. Theo's paid him $38."  -> picked (c): number + conflict instantly, loops cleanly.
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "N", [("SAME", "Same"), ("$10K.", "ten grand."), ("MY BANK", "My bank"), ("PAID ME", "paid me"),
                    ("$350.", "three hundred and fifty."), ("THEO'S?", "Theo's?"), ("$38.", "thirty eight.")], 0.15),
    ("mug",   "T", [("BUT MINE", "But mine"), ("GAVE ME", "gave me"), ("A FREE MUG!", "a free mug!")], 0.2),
    ("theo",  "N", [("YOUR BANK", "Your bank"), ("PAYS", "pays"), ("0.38%.", "zero point three eight percent.")], 0.15),
    ("nora",  "N", [("MINE'S A", "Mine's a"), ("HIGH-YIELD", "high yield"), ("SAVINGS", "savings"), ("ACCOUNT.", "account."),
                    ("3.5%.", "Three and a half percent."), ("ALSO", "Also"), ("FDIC INSURED.", "F D I C insured.")], 0.2),
    ("ask",   "T", [("SO WHAT", "So what"), ("DID MY MUG", "did my mug"), ("COST ME?", "cost me?")], 0.15),
    ("cost",  "N", [("$312", "Three hundred and twelve dollars"), ("THIS YEAR.", "this year."),
                    ("FIVE YEARS?", "Five years?"), ("ALMOST", "Almost"), ("$1,700.", "seventeen hundred.")], 0.2),
    ("punch", "T", [("MOST", "Most"), ("EXPENSIVE", "expensive"), ("MUG", "mug"), ("EVER.", "ever.")], 0.2),
    ("q",     "N", [("WHAT DOES", "What does"), ("YOURS PAY?", "yours pay?"), ("GO CHECK.", "Go check.")], 0.1),
    ("loop",  "T", [("SAME", "Same"), ("$10K...", "ten grand...")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.12

if __name__ == "__main__":
    p, a, b = 10000, 0.0038, 0.035
    print(p * a, p * b, p * (b - a), round(b / a, 1))
    print(round(p * ((1 + a) ** 5 - 1)), round(p * ((1 + b) ** 5 - 1)), round(p * ((1 + b) ** 5 - (1 + a) ** 5)))
