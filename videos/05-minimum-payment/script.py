# "The Minimum Payment Math" Short.
# $5,000 at 22% APR, minimum = interest + 1% of balance ($25 floor):
#   first payment $141.67 ($91.67 interest), 230 months (19.2 yrs), total paid $13,100, interest $8,100
#   balance yr5 $2,736  yr10 $1,497
# Fixed $200/mo: 34 months (2.8 yrs), interest $1,750.  Saved: $6,350

SEGMENTS = [
    ("hook",   [("$5,000", "Five thousand dollars"), ("ON A", "on a"), ("CREDIT CARD.", "credit card."),
                ("PAY THE", "Pay the"), ("MINIMUM,", "minimum,"), ("AND YOU'LL", "and you'll"),
                ("BE PAYING", "be paying"), ("FOR", "for"), ("19 YEARS.", "nineteen years.")], 0.25),
    ("hook2",  [("AND IT'LL", "And it'll"), ("COST YOU", "cost you"), ("$13,000.", "thirteen thousand dollars.")], 0.35),
    ("how",    [("HERE'S", "Here's"), ("THE TRICK.", "the trick."), ("YOUR MINIMUM", "Your minimum"),
                ("SHRINKS", "shrinks"), ("AS YOUR", "as your"), ("BALANCE", "balance"), ("SHRINKS.", "shrinks."),
                ("SO IT", "So it"), ("FEELS EASY...", "feels easy..."), ("BUT IT TAKES", "but it takes"),
                ("FOREVER.", "forever.")], 0.25),
    ("first",  [("YOUR FIRST", "Your first"), ("MINIMUM?", "minimum?"), ("ABOUT", "About"),
                ("$142.", "a hundred and forty two dollars."), ("$92", "Ninety two dollars"),
                ("OF THAT", "of that"), ("IS JUST", "is just"), ("INTEREST.", "interest.")], 0.25),
    ("slow",   [("AFTER", "After"), ("5 YEARS,", "five years,"), ("YOU STILL", "you still"), ("OWE", "owe"),
                ("$2,700.", "twenty seven hundred."), ("AFTER 10?", "After ten?"),
                ("STILL", "Still"), ("$1,500.", "fifteen hundred.")], 0.25),
    ("total",  [("19 YEARS", "Nineteen years"), ("LATER,", "later,"), ("IT'S FINALLY", "it's finally"),
                ("GONE.", "gone."), ("YOU PAID", "You paid"), ("$13,100.", "thirteen thousand one hundred."),
                ("$8,100", "Eight thousand one hundred"), ("OF THAT?", "of that?"), ("PURE", "Pure"),
                ("INTEREST.", "interest.")], 0.35),
    ("fix",    [("NOW PAY", "Now pay"), ("A FIXED", "a fixed"), ("$200", "two hundred dollars"),
                ("A MONTH", "a month"), ("INSTEAD.", "instead."), ("DEBT FREE", "Debt free"),
                ("IN UNDER", "in under"), ("3 YEARS.", "three years."), ("INTEREST?", "Interest?"),
                ("ABOUT", "About"), ("$1,750.", "seventeen fifty.")], 0.3),
    ("save",   [("THAT'S", "That's"), ("$6,350", "sixty three hundred and fifty dollars"),
                ("SAVED.", "saved."), ("SAME DEBT.", "Same debt."), ("DIFFERENT", "Different"),
                ("PAYMENT.", "payment.")], 0.4),
    ("cta",    [("FOLLOW", "Follow"), ("FOR MORE", "for more"), ("NUMBERS", "numbers"),
                ("THAT CHANGE", "that change"), ("HOW YOU", "how you"), ("SPEND.", "spend.")], 0.6),
]

VOICE = "af_heart"
SPEED = 1.08
