# THEO EXPLAINS #3: Insurance deductibles. Theo thinks his $1,000 car-insurance deductible is $1,000 off his taxes.
# Assumptions (illustration, US personal car policy): collision coverage with a $1,000 deductible per claim;
#   repair costs are made-up examples. The deductible is the part of each covered claim the driver pays first;
#   it is not a tax deduction (personal car). Higher deductible -> usually lower premium, more out of pocket per claim.
# First line drafts (picked #3):
#   1 "My car insurance deductible is a thousand bucks. Free tax break!"
#   2 "A deductible? Great, that's a thousand dollars off my taxes!"
#   3 "A thousand-dollar deductible means a thousand off my taxes!"   <- number + wrong claim in one sentence
# Maths (python, see bottom):
#   pole: repair 1,500 -> Theo pays min(1500, 1000) = 1,000 ; insurer pays 1500 - 1000 = 500
#   scratch: repair 600 -> Theo pays min(600, 1000) = 600 ; insurer pays max(0, 600 - 1000) = 0
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",   "T", [("A $1,000", "A thousand-dollar"), ("DEDUCTIBLE", "deductible"), ("MEANS", "means"),
                     ("$1,000 OFF", "a thousand off"), ("MY TAXES!", "my taxes!")], 0.2),
    ("no",     "N", [("THEO.", "Theo."), ("IT'S NOT", "It's not"), ("A TAX THING.", "a tax thing.")], 0.15),
    ("what",   "N", [("IT'S WHAT", "It's what"), ("YOU PAY", "you pay"), ("FIRST,", "first,"),
                     ("BEFORE", "before"), ("INSURANCE", "insurance"), ("PAYS A CENT.", "pays a cent.")], 0.2),
    ("pole",   "T", [("SO IF I", "So if I"), ("SCRAPE", "scrape"), ("A POLE?", "a pole?")], 0.15),
    ("repair", "N", [("$1,500", "Fifteen hundred dollar"), ("REPAIR.", "repair."), ("YOU PAY", "You pay"),
                     ("$1,000.", "one thousand."), ("INSURANCE", "Insurance"), ("PAYS $500.", "pays five hundred.")], 0.2),
    ("scratch","T", [("AND A", "And a"), ("$600", "six hundred dollar"), ("SCRATCH?", "scratch?")], 0.15),
    ("zero",   "N", [("ALL $600", "All six hundred"), ("IS YOURS.", "is yours."), ("INSURANCE", "Insurance"),
                     ("PAYS ZERO.", "pays zero.")], 0.2),
    ("tip",    "N", [("HIGHER", "Higher"), ("DEDUCTIBLE,", "deductible,"), ("CHEAPER", "cheaper"), ("PREMIUM.", "premium."),
                     ("JUST KEEP IT", "Just keep it"), ("SAVED.", "saved.")], 0.25),
    ("punch",  "T", [("SO IT'S", "So it's really"), ("A DEDUCT-", "a deduct"), ("FROM-ME-IBLE.", "from me ible.")], 0.35),
    ("q",      "N", [("WHAT'S", "What's"), ("YOUR", "your"), ("DEDUCTIBLE?", "deductible?"), ("TELL US", "Tell us"),
                     ("BELOW.", "below.")], 0.2),
    ("loop",   "T", [("WAIT.", "Wait."), ("I STILL", "I still"), ("THINK...", "think...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    D = 1000
    for repair in (1500, 600):
        print(repair, "theo pays", min(repair, D), "insurer pays", max(0, repair - D))
