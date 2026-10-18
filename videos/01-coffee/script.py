# Script for "What your $5 coffee really costs" Short.
# Each segment: scene id, list of (caption_text, spoken_text), pause after (s).
# Maths: $5/day = $1,825/yr, invested yearly at 7% avg return.
#   10y = $25,214   20y = $74,816   30y = $172,393   contributed 30y = $54,750

SEGMENTS = [
    ("hook",   [("THIS", "This"), ("$5", "five dollar"), ("COFFEE", "coffee"),
                ("IS COSTING", "is costing"), ("YOU", "you"),
                ("$172,000", "a hundred and seventy two thousand dollars.")], 0.35),
    ("hook2",  [("SOUNDS", "Sounds"), ("INSANE,", "insane,"), ("RIGHT?", "right?"),
                ("LET'S", "Let's"), ("BREAK IT", "break it"), ("DOWN.", "down.")], 0.25),
    ("week",   [("$5", "Five dollars"), ("A DAY", "a day"), ("IS", "is"),
                ("$35", "thirty five dollars"), ("A WEEK.", "a week.")], 0.2),
    ("year",   [("THAT'S", "That's"), ("$1,825", "eighteen hundred and twenty five dollars"),
                ("A YEAR.", "a year.")], 0.3),
    ("invest", [("NOW", "Now"), ("IMAGINE", "imagine"), ("YOU", "you"), ("INVESTED", "invested"),
                ("THAT", "that"), ("INSTEAD,", "instead,"), ("IN AN", "in an"), ("INDEX FUND", "index fund"),
                ("AVERAGING", "averaging"), ("7%", "seven percent"), ("A YEAR.", "a year.")], 0.3),
    ("y10",    [("AFTER", "After"), ("10 YEARS,", "ten years,"), ("YOU'D HAVE", "you'd have"),
                ("ABOUT", "about"), ("$25,000.", "twenty five thousand dollars.")], 0.25),
    ("y20",    [("AFTER", "After"), ("20 YEARS?", "twenty years?"),
                ("$75,000.", "seventy five thousand.")], 0.25),
    ("y30a",   [("AFTER", "After"), ("30 YEARS...", "thirty years...")], 0.55),
    ("y30",    [("$172,000.", "A hundred and seventy two thousand dollars.")], 0.2),
    ("coffee", [("FROM", "From"), ("COFFEE.", "coffee.")], 0.45),
    ("split",  [("AND THE", "And the"), ("CRAZY PART?", "crazy part?"), ("YOU ONLY", "You only"),
                ("PUT IN", "put in"), ("ABOUT", "about"), ("$55,000.", "fifty five thousand."),
                ("THE OTHER", "The other"), ("$117,000?", "hundred and seventeen thousand?"),
                ("THAT'S", "That's"), ("COMPOUND", "compound"), ("INTEREST.", "interest.")], 0.35),
    ("twist",  [("NOW,", "Now,"), ("I'M NOT", "I'm not"), ("SAYING", "saying"), ("QUIT", "quit"),
                ("COFFEE.", "coffee."), ("ENJOY", "Enjoy"), ("YOUR", "your"), ("COFFEE.", "coffee.")], 0.25),
    ("pick",   [("BUT PICK", "But pick"), ("ONE THING", "one thing"), ("YOU DON'T", "you don't"),
                ("ACTUALLY", "actually"), ("CARE ABOUT,", "care about,"), ("AND", "and"),
                ("LET IT", "let it"), ("GROW", "grow"), ("INSTEAD.", "instead.")], 0.3),
    ("cta",    [("FOLLOW", "Follow"), ("FOR MORE", "for more"), ("NUMBERS", "numbers"),
                ("THAT CHANGE", "that change"), ("HOW YOU", "how you"), ("SPEND.", "spend.")], 0.6),
]

VOICE = "af_heart"
SPEED = 1.08
