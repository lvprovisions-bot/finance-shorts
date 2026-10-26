# THEO EXPLAINS #4: Tax refunds. Theo thinks his tax refund is a bonus from the IRS.
# Source: IRS "2026 Filing season statistics" (cumulative to week ending 1 May 2026): average refund $3,273
#   (97,918,000 refunds). https://www.irs.gov/node/159931
# Assumptions (illustration): Theo's refund = the 2026 average, $3,273, all of it from tax over-withheld from his pay
#   (some real refunds also include refundable credits). Spread over the 12 months it was withheld.
# First line drafts (picked #3):
#   1 "My tax refund is free money from the government!"
#   2 "Three thousand bucks back? Best bonus ever!"
#   3 "The IRS just gave me a $3,273 bonus!"   <- number + wrong claim, first words
# Maths (python, see bottom):
#   3273 / 12 = 272.75 -> "about $273 a month", interest paid by the IRS on it = $0
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("THE IRS", "The I R S"), ("JUST GAVE ME", "just gave me"), ("A $3,273", "a three thousand, two hundred seventy three dollar"),
                    ("BONUS!", "bonus!")], 0.2),
    ("no",    "N", [("THEO.", "Theo."), ("THAT'S", "That's"), ("YOUR OWN", "your own"), ("MONEY.", "money.")], 0.15),
    ("over",  "N", [("YOU OVERPAID", "You overpaid"), ("TAX", "tax"), ("ALL YEAR.", "all year."), ("THEY'RE JUST", "They're just"),
                    ("GIVING IT", "giving it"), ("BACK.", "back.")], 0.2),
    ("ask",   "T", [("SO PER", "So per"), ("MONTH", "month"), ("THAT'S...?", "that's?")], 0.15),
    ("month", "N", [("ABOUT", "About"), ("$273", "two seventy three"), ("A MONTH,", "a month,"), ("LENT", "lent"),
                    ("TO THE IRS.", "to the I R S."), ("ZERO", "Zero"), ("INTEREST.", "interest.")], 0.2),
    ("loan",  "T", [("I GAVE", "I gave"), ("THE GOVERNMENT", "the government"), ("A FREE LOAN?!", "a free loan?!")], 0.2),
    ("tip",   "N", [("UPDATE", "Update"), ("YOUR W-4,", "your W 4,"), ("AND MORE", "and more"), ("LANDS IN", "lands in"),
                    ("EACH", "each"), ("PAYCHECK.", "paycheck.")], 0.25),
    ("punch", "T", [("SO I'M NOT", "So I'm not"), ("GETTING A BONUS.", "getting a bonus."), ("I'M THE IRS'S", "I'm the I R S's"),
                    ("PIGGY BANK.", "piggy bank.")], 0.35),
    ("q",     "N", [("REFUND", "Refund"), ("OR OWE", "or owe"), ("THIS YEAR?", "this year?"), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.2),
    ("loop",  "T", [("WAIT.", "Wait."), ("BUT THE IRS", "But the I R S"), ("JUST GAVE ME...", "just gave me...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    refund = 3273
    print("per month", refund / 12, "->", round(refund / 12))
