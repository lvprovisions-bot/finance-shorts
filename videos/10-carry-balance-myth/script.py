# MONEY MYTHS: TRUE OR FALSE? #1 - "Carrying a credit card balance builds your credit score."
# One-off characters: Uncle Ray (states the myth, voice am_puck) + quiz host narrator (af_heart).
# Sources:
#   myFICO, "Myth Busting - You Don't Need to Carry Credit Card Balances to Improve Your FICO Scores"
#     (usage is judged from the balance reported, usually the statement balance; paying in full does not hurt)
#   Federal Reserve G.19 (7 Oct 2026 release): commercial-bank credit card rate, accounts assessed interest,
#     Q2 2026 = 22.15% APR (all accounts 20.94%).
# Maths (python, bottom of file):
#   $1,000 balance kept all year, interest paid each month so the balance stays $1,000:
#   1,000 * 22.15% / 12 = $18.46 a month  -> x12 = $221.50 ~ $222 a year.  Extra score points from paying interest: 0.
#   (If unpaid interest compounded daily it would be higher: 1000*((1+.2215/365)^365-1) = $247.90.)
# Verdict: MOSTLY FALSE. True part: using a card and paying on time helps. False part: interest buys no points.
# Speakers: R = Ray (am_puck), N = narrator (af_heart)

SEGMENTS = [
    ("hook",   "R", [("ALWAYS KEEP", "Always keep"), ("A BALANCE", "a balance"), ("ON YOUR CARD.", "on your card."),
                     ("IT BUILDS", "It builds"), ("YOUR CREDIT", "your credit"), ("SCORE!", "score!")], 0.15),
    ("tf",     "N", [("TRUE", "True"), ("OR FALSE?", "or false?")], 0.2),
    ("true",   "N", [("PART TRUE.", "Part true."), ("USING YOUR", "Using your"), ("CARD AND", "card and"),
                     ("PAYING ON TIME", "paying on time"), ("DOES HELP.", "does help.")], 0.2),
    ("false",  "N", [("BUT YOUR SCORE", "But your score"), ("SEES YOUR", "sees your"), ("STATEMENT", "statement"),
                     ("BALANCE.", "balance."), ("PAY IT", "Pay it"), ("ALL OFF,", "all off,"), ("AND IT STILL", "and it still"),
                     ("COUNTS.", "counts.")], 0.2),
    ("cost",   "N", [("KEEP $1,000", "Keep a thousand dollars"), ("ON IT", "on it"), ("ALL YEAR", "all year"),
                     ("AT 22%:", "at twenty two percent,"), ("ABOUT", "about"), ("$222", "two hundred twenty two dollars"),
                     ("IN INTEREST.", "in interest.")], 0.15),
    ("zero",   "N", [("EXTRA POINTS?", "Extra points?"), ("ZERO.", "Zero.")], 0.3),
    ("verdict","N", [("VERDICT:", "Verdict:"), ("MOSTLY", "mostly"), ("FALSE.", "false."), ("IT DEPENDS", "It depends"),
                     ("ON PAYING", "on paying"), ("THE FULL", "the full"), ("STATEMENT", "statement"), ("BALANCE", "balance"),
                     ("ON TIME.", "on time.")], 0.25),
    ("q",      "N", [("WHO TOLD YOU", "Who told you"), ("THIS ONE?", "this one?"), ("COMMENT", "Comment"), ("BELOW.", "below.")], 0.2),
    ("loop",   "N", [("BECAUSE", "Because"), ("SOMEONE", "someone"), ("ALWAYS SAYS...", "always says...")], 0.05),
]

VOICES = {"N": "af_heart", "R": "am_puck"}
SPEED = 1.12

if __name__ == "__main__":
    apr = 0.2215
    print(round(1000 * apr / 12, 2), round(1000 * apr / 12 * 12, 2), round(1000 * ((1 + apr / 365) ** 365 - 1), 2))
