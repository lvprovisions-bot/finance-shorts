# LONG-FORM L02 "Lease, Finance or Pay Cash? We Ran 9 Years of Numbers"  (16:9, ~9-10 min, OWNER'S VOICE)
# All numbers from model.py (base case):
#   car $50,562 (KBB ATP Sep 2026) | loan 7.0% APR, $5,554 down (Edmunds Q3 2026), 72 months -> $767/mo, interest $10,241
#   lease (estimate): residual 62% at 36 mo, money factor = 7%/2400 -> $773/mo + $4,000 due at signing every 3 years
#   lease paid over 9 yrs $95,442 | car value: yr1 $40,450 (-20%), yr5 $29,427 (-41.8%, iSeeCars), yr9 $23,969
#   net worth (car + investments - loan): yr1 cash/fin $49,959 lease $49,863 | yr3 $64,011 / $57,197 | yr6 $93,045 / $65,406
#   yr9 $131,531 / $75,527  -> gap $56,004 | owner's 9-yr cost of driving $42,834
#   0% loan: finance $125,860 vs cash $110,245 (+$15,615) | 10% loan: cash $141,492 vs finance $134,186 (+$7,306)
# Written for a human narrator (British, mild lisp): short sentences, few "s" clusters, numbers rounded where natural.
# Token markup: {CAPTION|spoken words}. Each segment = one paragraph in the recording script.

S = []
def seg(i, scene, text, pause=0.3, **show):
    S.append(dict(id=i, scene=scene, text=text, pause=pause, show=show))

# HOOK (frame 0: three characters, three cars, the question)
seg("h1", "hook", "Three friends. The same fifty thousand dollar car. Nora pays cash. Max takes a car loan. Theo leases.")
seg("h2", "hook", "Nine years later, one of them is {$56,000|fifty six thousand dollars} poorer than the other two.", st=1)
seg("h3", "hook", "And the one who paid cash? She didn't win. Let me show you why.", st=2)

# SETUP
seg("s1", "setup", "Here's the setup, with real numbers from this month.", chap="The setup", st=0)
seg("s2", "setup", "The average new car in America now sells for {$50,562|about fifty thousand, five hundred dollars}.", st=1)
seg("s3", "setup", "The average new car loan is at {7%|seven percent} interest.", st=2)
seg("s4", "setup", "And a typical car loses about {42%|forty two percent} of its value in five years.", st=3)
seg("s5", "rule", "To make it fair, all three start with the same pile of cash: the price of the car.", chap="The setup", st=0)
seg("s6", "rule", "And each month, they all set aside the same car budget. Whatever they don't spend on the car gets invested, and earns {7%|seven percent} a year.", st=1)

# THE THREE WAYS
seg("n1", "nora", "Nora pays cash. She hands over the whole {$50,562|fifty thousand five hundred}. No loan, no interest, no monthly payment.", chap="Three ways to get a car", st=0)
seg("n2", "nora", "So every month, she invests her entire car budget instead.", st=1)
seg("m1", "max", "Max finances. He puts down {$5,554|about five and a half thousand}, the average down payment right now, and invests the rest of his cash.", chap="Three ways to get a car", st=0)
seg("m2", "max", "His loan is six years at {7%|seven percent}. That's {$767|seven hundred and sixty seven dollars} a month.", st=1)
seg("m3", "max", "Over the six years, he pays about {$10,200|ten thousand two hundred dollars} in interest.", st=2)
seg("m4", "loanlen", "And Max is in good company. One in four new car loans is now seven years or longer.", chap="Three ways to get a car", st=0)
seg("m5", "loanlen", "A seven year loan would drop his payment to {$679|six hundred and seventy nine dollars} a month. But the interest climbs to about {$12,000|twelve thousand dollars}.", st=1)
seg("m6", "loanlen", "A five year loan costs {$891|eight hundred and ninety one} a month, but only about {$8,500|eight and a half thousand} in interest.", st=2)
seg("m7", "loanlen", "Longer loans feel cheaper. They're not. You just pay for longer.", pause=0.5, st=3)
seg("t1", "theo", "And Theo leases. He never owns the car. He just pays to use it for three years, then hands it back and gets a new one.", chap="Three ways to get a car", st=0)
seg("t2", "theo", "A lease payment covers the value the car loses while you drive it, plus a finance charge.", st=1)
seg("t3", "theo", "For this car, that's roughly {$773|seven hundred and seventy three dollars} a month, plus about {$4,000|four thousand dollars} up front every time he starts a new lease.", st=2)
seg("t4", "theo", "And here's the first surprise. With interest rates this high, the lease payment is about the same as the loan payment.", pause=0.5, st=3)

# DEPRECIATION
seg("d1", "depr", "Now, the thing that really decides this: depreciation.", chap="The silent cost", st=0)
seg("d2", "depr", "The moment you drive off, your car starts losing value. Roughly a fifth in the first year.", st=1)
seg("d3", "depr", "By year five, it's down about {42%|forty two percent}. By year nine, Nora and Max's car is worth about {$24,000|twenty four thousand dollars}.", st=2)
seg("d4", "depr", "Theo never feels that loss directly. But he pays for it, inside every lease payment.", pause=0.5, st=3)

# SCOREBOARD
seg("b1", "score", "So let's keep score. Each person's total: their car, plus their investments, minus any loan they still owe.", chap="The scoreboard", y=1, st=0)
seg("b2", "score", "After one year, they're almost level. About fifty thousand each.", y=1, st=1)
seg("b3", "score", "Year three: Nora and Max have {$64,000|sixty four thousand}. Theo has {$57,000|fifty seven thousand}. And now he has to sign a new lease.", y=3, st=1)
seg("b4", "score", "Year six: Nora and Max, {$93,000|ninety three thousand}. Theo, {$65,000|sixty five thousand}.", y=6, st=1)
seg("b5", "score", "Year nine: Nora and Max, {$131,500|a hundred and thirty one and a half thousand}. Theo, {$75,500|seventy five and a half thousand}.", y=9, st=1)
seg("b6", "score", "That's the fifty six thousand dollar gap. But look closely. Nora and Max are exactly tied.", pause=0.6, y=9, st=2)

# TWIST 1
seg("x1", "twist", "Twist number one. Paying cash didn't beat the loan. Why?", chap="Twist 1: cash isn't king", n=1, st=0)
seg("x2", "twist", "Because Max's loan costs {7%|seven percent}, and the money he kept invested earned {7%|seven percent}. They cancel out.", n=1, st=1)
seg("x3", "twist", "So the real rule is simple. If your loan rate is lower than what your money can earn, financing wins. If it's higher, paying cash wins.", n=1, st=2)
seg("x4", "rates", "Say Max gets one of those zero percent dealer deals. Now Max beats Nora by about {$15,600|fifteen thousand six hundred dollars}.", st=0)
seg("x5", "rates", "But if his loan is ten percent, Nora wins by about {$7,300|seven thousand three hundred}.", pause=0.6, st=1)

# TWIST 2
seg("y1", "twist", "Twist number two. Theo isn't stupid. He got something for that money.", chap="Twist 2: what Theo paid for", n=2, st=0)
seg("y2", "twist", "He drove a brand new car the whole time. Always under warranty. No big repair bills. In our numbers, Nora and Max paid around a thousand a year in repairs once their car got older.", n=2, st=1)
seg("y3", "twist", "So the fifty six thousand dollars is really the price of always having a new car. Is that worth it to you? That's the real question.", pause=0.6, n=2, st=2)

# THE TOTAL BILL
seg("z1", "bill", "Let's look at it one more way. What did it actually cost each of them to drive for nine years?", chap="The real bill", st=0)
seg("z2", "bill", "Theo paid about {$95,400|ninety five thousand four hundred dollars} in lease payments and signing fees. And at the end, he has no car.", st=1)
seg("z3", "bill", "Max's real cost was the value his car lost, about {$26,600|twenty six thousand six hundred}, plus {$10,200|ten thousand two hundred} of interest, plus repairs. Around {$42,800|forty two thousand eight hundred} in total.", st=2)
seg("z4", "bill", "Nora had the same value loss and repairs, and no interest. But her fifty thousand dollars wasn't invested and growing for her. That hidden cost is why she ended up level with Max.", pause=0.6, st=3)

# WHEN LEASING MAKES SENSE + TRAPS
seg("l1", "lease_ok", "Leasing can make sense when a manufacturer offers a really cheap lease deal, when you'd swap your car every few years anyway, or when you drive very little.", chap="When leasing makes sense", st=0)
seg("l2", "lease_ok", "But watch for the traps. Most leases limit your miles, often around ten to twelve thousand a year, and charge you for every mile over.", st=1)
seg("l3", "lease_ok", "You can also pay for wear and tear when you hand it back. And ending a lease early can be very expensive.", pause=0.6, st=2)

# THREE WAYS TO PAY LESS
seg("q1", "tips", "Whichever one you choose, three habits save real money.", chap="Three ways to pay less", st=0)
seg("q2", "tips", "First, get a loan quote from your bank or a credit union before you visit the dealer. On this loan, just one percent lower saves about {$1,500|fifteen hundred dollars}.", st=1)
seg("q3", "tips", "Second, keep your car longer. The biggest drop in value happens in the first few years. After that, every extra year is cheap.", st=2)
seg("q4", "tips", "And third, negotiate the price of the car, not the monthly payment. A low payment can hide a much longer loan.", pause=0.6, st=3)

# CHECKLIST
seg("c1", "check", "So, lease, finance, or pay cash? Here's the thirty second version.", chap="So which should you pick?", st=0)
seg("c2", "check", "One. If you keep cars for a long time, owning usually wins.", st=1)
seg("c3", "check", "Two. Compare your loan rate to what your money could earn. That decides cash or finance.", st=2)
seg("c4", "check", "Three. If you love a new car every few years, a lease can be fair. Just know what it costs you.", st=3)
seg("c5", "check", "These numbers are examples, not predictions. Your car, your rate and your returns will be different.", pause=0.6, st=3, small=True)

# OUTRO (loops to the hook)
seg("o1", "outro", "So, are you a Nora, a Max, or a Theo? Tell me in the comments.", st=0)
seg("o2", "outro", "Because remember. Three friends. The same car. Only one way to lose fifty six thousand dollars.", pause=0.8, st=1)
seg("e1", "endcard", "Want money maths in under a minute? Watch our Shorts, there's a new one every day. And subscribe to Finance Advised.", pause=7.0)

SEGMENTS = S
VOICE = "af_heart"   # only used for the guide track / fallback; the real narration is the owner's recording
LANG = "en-us"
SPEED = 1.0
