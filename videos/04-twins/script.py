# "The Twin Math" Short.
# $300/mo = $3,600/yr at 7% avg.
# Emma: invests age 25-35 (10 yrs, $36,000 in), then stops.   Age 65: $378,628
# Jack: invests age 35-65 (30 yrs, $108,000 in).               Age 65: $340,059
# Age 45: Emma $97,845  Jack $49,739 | Age 55: Emma $192,475  Jack $147,584

SEGMENTS = [
    ("hook",   [("TWO TWINS.", "Two twins."), ("ONE", "One"), ("INVESTED", "invested"),
                ("FOR 10 YEARS.", "for ten years."), ("THE OTHER,", "The other,"), ("FOR 30.", "for thirty.")], 0.25),
    ("hook2",  [("THE 10-YEAR", "The ten year"), ("TWIN", "twin"), ("ENDED UP", "ended up"),
                ("RICHER.", "richer.")], 0.35),
    ("emma",   [("EMMA", "Emma"), ("STARTS AT", "starts at"), ("25.", "twenty five."),
                ("$300", "Three hundred dollars"), ("A MONTH.", "a month."), ("AT 35,", "At thirty five,"),
                ("SHE", "she"), ("STOPS.", "stops."), ("NEVER ADDS", "Never adds"),
                ("ANOTHER", "another"), ("DOLLAR.", "dollar.")], 0.25),
    ("jack",   [("JACK", "Jack"), ("WAITS", "waits"), ("UNTIL 35.", "until thirty five."),
                ("THEN HE", "Then he"), ("INVESTS", "invests"), ("THE SAME", "the same"), ("$300", "three hundred"),
                ("A MONTH,", "a month,"), ("ALL THE WAY", "all the way"), ("TO 65.", "to sixty five.")], 0.25),
    ("put",    [("EMMA", "Emma"), ("PUT IN", "put in"), ("$36,000.", "thirty six thousand."),
                ("JACK", "Jack"), ("PUT IN", "put in"), ("$108,000.", "a hundred and eight thousand."),
                ("THREE TIMES", "Three times"), ("AS MUCH.", "as much.")], 0.3),
    ("race",   [("BOTH", "Both"), ("EARN", "earn"), ("7%", "seven percent"), ("A YEAR.", "a year."),
                ("AT 45,", "At forty five,"), ("EMMA HAS", "Emma has"), ("$98,000.", "ninety eight thousand."),
                ("JACK,", "Jack,"), ("$50,000.", "fifty thousand.")], 0.25),
    ("race2",  [("AT 55,", "At fifty five,"), ("JACK'S", "Jack's"), ("CATCHING UP.", "catching up.")], 0.3),
    ("fin_a",  [("BUT AT 65...", "But at sixty five...")], 0.55),
    ("fin",    [("EMMA:", "Emma,"), ("$379,000.", "three hundred and seventy nine thousand."),
                ("JACK:", "Jack,"), ("$340,000.", "three hundred and forty thousand.")], 0.35),
    ("why",    [("EMMA", "Emma"), ("WINS,", "wins,"), ("WITH", "with"), ("A THIRD", "a third"),
                ("OF THE MONEY.", "of the money."), ("WHY?", "Why?"), ("TIME.", "Time.")], 0.3),
    ("twist",  [("THE BEST", "The best"), ("TIME", "time"), ("TO START", "to start"),
                ("WAS 10", "was ten"), ("YEARS AGO.", "years ago.")], 0.3),
    ("pick",   [("THE SECOND", "The second"), ("BEST TIME", "best time"), ("IS TODAY.", "is today.")], 0.4),
    ("cta",    [("FOLLOW", "Follow"), ("FOR MORE", "for more"), ("NUMBERS", "numbers"),
                ("THAT CHANGE", "that change"), ("HOW YOU", "how you"), ("SPEND.", "spend.")], 0.6),
]

VOICE = "af_heart"
SPEED = 1.08
