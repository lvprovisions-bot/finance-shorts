# "The Car Payment Math" Short.
# $500/mo = $6,000/yr invested yearly at 7% avg.
#   10y = $82,899  20y = $245,973  30y = $566,765  40y = $1,197,811
#   contributed 40y = $240,000  growth = $957,811

SEGMENTS = [
    ("hook",   [("YOUR", "Your"), ("CAR PAYMENT", "car payment"), ("COULD MAKE", "could make"),
                ("YOU A", "you a"), ("MILLIONAIRE.", "millionaire.")], 0.35),
    ("hook2",  [("NOT", "Not"), ("THE CAR.", "the car."), ("THE", "The"), ("PAYMENT.", "payment.")], 0.3),
    ("setup",  [("SAY YOU", "Say you"), ("PAY", "pay"), ("$500", "five hundred dollars"),
                ("A MONTH", "a month"), ("FOR YOUR", "for your"), ("CAR.", "car."),
                ("THAT'S", "That's"), ("$6,000", "six thousand dollars"), ("A YEAR.", "a year.")], 0.25),
    ("cycle",  [("FIVE YEARS", "Five years"), ("LATER,", "later,"), ("IT'S", "it's"), ("PAID OFF.", "paid off."),
                ("AND A LOT", "And a lot"), ("OF PEOPLE", "of people"), ("GO STRAIGHT", "go straight"),
                ("INTO A", "into a"), ("NEW ONE.", "new one.")], 0.2),
    ("cycle2", [("NEW CAR.", "New car."), ("NEW LOAN.", "New loan."), ("SAME", "Same"),
                ("$500.", "five hundred dollars."), ("FOREVER.", "Forever.")], 0.3),
    ("invest", [("NOW IMAGINE", "Now imagine"), ("YOU DROVE", "you drove"), ("A RELIABLE", "a reliable"),
                ("USED CAR,", "used car,"), ("AND INVESTED", "and invested"), ("THAT $500", "that five hundred"),
                ("INSTEAD,", "instead,"), ("AT A", "at a"), ("7%", "seven percent"),
                ("AVERAGE", "average"), ("RETURN.", "return.")], 0.3),
    ("y10",    [("AFTER", "After"), ("10 YEARS?", "ten years?"), ("ABOUT", "About"),
                ("$83,000.", "eighty three thousand.")], 0.2),
    ("y20",    [("20 YEARS?", "Twenty years?"), ("$246,000.", "two hundred and forty six thousand.")], 0.2),
    ("y30",    [("30 YEARS?", "Thirty years?"), ("$567,000.", "five hundred and sixty seven thousand.")], 0.2),
    ("y40a",   [("AND AFTER", "And after"), ("40 YEARS...", "forty years...")], 0.55),
    ("y40",    [("$1.2", "One point two"), ("MILLION", "million"), ("DOLLARS.", "dollars.")], 0.4),
    ("split",  [("YOU ONLY", "You only"), ("PUT IN", "put in"),
                ("$240,000.", "two hundred and forty thousand."), ("THE OTHER", "The other"),
                ("$958,000?", "nine hundred and fifty eight thousand?"), ("COMPOUND", "Compound"),
                ("INTEREST.", "interest.")], 0.35),
    ("twist",  [("I'M NOT", "I'm not"), ("SAYING", "saying"), ("NEVER BUY", "never buy"),
                ("A NICE CAR.", "a nice car.")], 0.2),
    ("pick",   [("JUST KNOW", "Just know"), ("WHAT THAT", "what that"), ("PAYMENT", "payment"),
                ("IS REALLY", "is really"), ("COSTING", "costing"), ("YOU.", "you.")], 0.35),
    ("cta",    [("FOLLOW", "Follow"), ("FOR MORE", "for more"), ("NUMBERS", "numbers"),
                ("THAT CHANGE", "that change"), ("HOW YOU", "how you"), ("SPEND.", "spend.")], 0.6),
]

VOICE = "af_heart"
SPEED = 1.08
