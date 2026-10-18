# "The Subscriptions Math" Short.
# 5 subs x $15 = $75/mo = $900/yr, invested yearly at 7% avg.
#   10y = $12,435  20y = $36,896  30y = $85,015  contributed = $27,000  growth = $58,015

SEGMENTS = [
    ("hook",   [("FIVE APPS", "Five apps"), ("ON YOUR", "on your"), ("PHONE", "phone"),
                ("ARE COSTING", "are costing"), ("YOU", "you"),
                ("$85,000.", "eighty five thousand dollars.")], 0.35),
    ("hook2",  [("AND YOU'VE", "And you've"), ("PROBABLY", "probably"), ("FORGOTTEN", "forgotten"),
                ("ABOUT", "about"), ("ONE", "one"), ("OF THEM.", "of them.")], 0.25),
    ("list",   [("STREAMING.", "Streaming."), ("MUSIC.", "Music."), ("CLOUD", "Cloud"),
                ("STORAGE.", "storage."), ("THAT", "That"), ("FITNESS APP.", "fitness app."),
                ("THAT", "That"), ("FREE TRIAL", "free trial"), ("YOU NEVER", "you never"),
                ("CANCELLED.", "cancelled.")], 0.25),
    ("month",  [("$15", "Fifteen dollars"), ("EACH.", "each."), ("THAT'S", "That's"),
                ("$75", "seventy five dollars"), ("A MONTH.", "a month.")], 0.2),
    ("year",   [("$900", "Nine hundred dollars"), ("A YEAR.", "a year.")], 0.3),
    ("invest", [("NOW", "Now"), ("CANCEL", "cancel"), ("THEM,", "them,"), ("AND", "and"),
                ("INVEST", "invest"), ("THAT MONEY", "that money"), ("INSTEAD,", "instead,"),
                ("AT A", "at a"), ("7%", "seven percent"), ("AVERAGE", "average"), ("RETURN.", "return.")], 0.3),
    ("y10",    [("AFTER", "After"), ("10 YEARS?", "ten years?"), ("ABOUT", "About"),
                ("$12,000.", "twelve thousand.")], 0.25),
    ("y20",    [("20 YEARS?", "Twenty years?"), ("$37,000.", "thirty seven thousand.")], 0.25),
    ("y30a",   [("AFTER", "After"), ("30 YEARS...", "thirty years...")], 0.55),
    ("y30",    [("$85,000.", "Eighty five thousand dollars.")], 0.2),
    ("apps",   [("FROM APPS", "From apps"), ("YOU DON'T", "you don't"), ("EVEN", "even"),
                ("OPEN.", "open.")], 0.45),
    ("split",  [("YOU ONLY", "You only"), ("PUT IN", "put in"),
                ("$27,000.", "twenty seven thousand."), ("THE OTHER", "The other"),
                ("$58,000?", "fifty eight thousand?"), ("THAT'S", "That's"), ("COMPOUND", "compound"),
                ("INTEREST.", "interest.")], 0.35),
    ("twist",  [("KEEP", "Keep"), ("THE ONES", "the ones"), ("YOU ACTUALLY", "you actually"),
                ("LOVE.", "love.")], 0.25),
    ("pick",   [("BUT GO", "But go"), ("CHECK", "check"), ("YOUR", "your"), ("SUBSCRIPTIONS", "subscriptions"),
                ("RIGHT NOW.", "right now."), ("I BET", "I bet"), ("THERE'S ONE", "there's one"),
                ("YOU FORGOT", "you forgot"), ("ABOUT.", "about.")], 0.3),
    ("cta",    [("FOLLOW", "Follow"), ("FOR MORE", "for more"), ("NUMBERS", "numbers"),
                ("THAT CHANGE", "that change"), ("HOW YOU", "how you"), ("SPEND.", "spend.")], 0.6),
]

VOICE = "af_heart"
SPEED = 1.08
