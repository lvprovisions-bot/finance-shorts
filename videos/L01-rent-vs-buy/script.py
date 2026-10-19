# LONG-FORM L01 "Renting vs Buying a Home: Who's Richer After 30 Years?"  (16:9, ~12-13 min)
# Every number comes from model.py (run it). Base case:
#   price $417,500 (NAR Sep 2026) | 7.40% 30-yr (Freddie Mac 15 Oct 2026) | rent $1,962 (Zillow ZORI Jul 2026)
#   20% down $83,500 + 3% closing $12,525 = $96,025 upfront | loan $334,000 -> P&I $2,313
#   month 1: interest $2,060, principal $253 | tax $313 ins $234 maint $348 -> owner $3,208 vs renter $1,977 (rent + $15 ins)
#   gap $1,231/mo | scoreboard (net, after selling costs + tax): y1 N 77K / T 117K, y5 162K / 214K, y10 292K / 366K
#   y30: house $1.35M, Nora $1,182,066, Theo $1,718,270 | 30y costs: interest $498,517 tax $214,575 ins $133,592
#   maint $238,417 = $1,085,101 vs rent paid $1,120,116
#   Twist A (Theo spends the gap, only invests the $96K): Theo y30 $676,882 -> Nora wins
#   Twist B (similar house rents $2,400): Nora ahead from y9; y30 $1,251,267 vs $1,129,279
#   Twist C (rent $2,400 + rate 6%): Nora ahead from y5; y30 $1,344,834 vs $884,590
#   price-to-rent: 417,500/(1,962x12)=17.7 ; /(2,400x12)=14.5
# Token markup: {CAPTION|spoken words} shows CAPTION on screen while the spoken words are read.

S = []
def seg(i, scene, text, pause=0.25, **show):
    S.append(dict(id=i, scene=scene, text=text, pause=pause, show=show))

# ---------- HOOK (frame 0: both characters, both homes, the question) ----------
seg("h1", "hook", "Same salary. Same city. Nora buys a house. Theo rents.", 0.25)
seg("h2", "hook", "Thirty years later, one of them is half a million dollars richer.", 0.3, k=1)
seg("h3", "hook", "And the answer flips. More than once.", 0.35, k=2)
seg("h4", "hook", "So stick around, because by the end you'll know exactly which one wins where you live.", 0.6, k=2)

# ---------- 1 THE SETUP ----------
seg("s1", "setup", "Here's the setup. Every number comes from real, current data.", 0.2, chap="The setup", st=0)
seg("s2", "setup", "Nora buys the typical American home: {$417,500|four hundred seventeen thousand, five hundred dollars}, the median price in September.", 0.2, st=1)
seg("s3", "setup", "Her mortgage rate is {7.40%|seven point four percent}, the average thirty year fixed rate this month.", 0.2, st=2)
seg("s4", "setup", "Theo rents. The typical American rent is {$1,962|one thousand, nine hundred and sixty two dollars} a month.", 0.3, st=3)
seg("s5", "rule", "And here's the one rule that makes this fair.", 0.15, chap="The setup")
seg("s6", "rule", "They both spend exactly the same amount on housing every month.", 0.15, st=1)
seg("s7", "rule", "Whoever's housing is cheaper invests the difference, and it grows at {7%|seven percent} a year.", 0.25, st=2)
seg("s8", "rule", "That's below the stock market's long run average, to stay on the cautious side.", 0.15, st=3)
seg("s9", "rule", "We'll also assume home prices rise {4%|four percent} a year, a little under the long run U.S. average of {4.4%|four point four}, and rents rise {3%|three percent} a year.", 0.5, st=4)

# ---------- 2 WHAT BUYING REALLY COSTS ----------
seg("c1", "upfront", "Day one. Before Nora gets her keys, she needs cash.", 0.15, chap="What buying really costs", st=0)
seg("c2", "upfront", "A twenty percent down payment: {$83,500|eighty three thousand, five hundred dollars}.", 0.15, st=1)
seg("c3", "upfront", "Plus closing costs of about three percent: another {$12,525|twelve and a half thousand}.", 0.15, st=2)
seg("c4", "upfront", "That's {$96,025|ninety six thousand dollars} gone, on day one.", 0.25, st=3)
seg("c5", "upfront", "Theo doesn't need any of that. So, following the rule, his {$96K|ninety six thousand} goes straight into investments.", 0.5, st=4)
seg("c6", "mortgage", "Now the monthly bill. Nora's mortgage payment is {$2,313|two thousand, three hundred and thirteen dollars}.", 0.2, chap="What buying really costs", st=0)
seg("c7", "mortgage", "But look at where her first payment actually goes.", 0.2, st=0)
seg("c8", "mortgage", "{$2,060|Two thousand and sixty dollars} is interest, paid to the bank.", 0.15, st=1)
seg("c9", "mortgage", "Only {$253|two hundred and fifty three dollars} pays down her loan.", 0.3, st=2)
seg("c10", "mortgage", "At {7.4%|seven point four percent}, almost ninety percent of her early payments is interest.", 0.5, st=2)
seg("c11", "monthly", "And the mortgage is just the start.", 0.15, chap="What buying really costs", st=0)
seg("c12", "monthly", "Property tax, about {$313|three hundred and thirteen dollars} a month.", 0.1, st=1)
seg("c13", "monthly", "Home insurance, {$234|two hundred and thirty four}.", 0.1, st=2)
seg("c14", "monthly", "And maintenance. Roofs, boilers, plumbing. The rule of thumb is one percent of the home's value a year, so {$348|three hundred and forty eight} a month.", 0.2, st=3)
seg("c15", "monthly", "Nora's real monthly cost: {$3,208|three thousand, two hundred and eight dollars}.", 0.2, st=4)
seg("c16", "monthly", "Theo pays rent, plus about fifteen dollars of renter's insurance: {$1,977|one thousand, nine hundred and seventy seven}.", 0.2, st=5)
seg("c17", "monthly", "That's a gap of {$1,231|one thousand, two hundred and thirty one dollars} every month. And Theo invests all of it.", 0.6, st=6)

# ---------- 2b WHAT RENTING REALLY COSTS ----------
seg("r1", "rentup", "But renting has its own hidden cost. It goes up, every single year.", 0.2, chap="Buying's secret weapons", st=0)
seg("r2", "rentup", "By year ten, Theo's rent is {$2,560|two thousand, five hundred and sixty dollars}. By year thirty, {$4,624|four thousand, six hundred and twenty four}.", 0.25, st=1)
seg("r3", "rentup", "Nora's mortgage payment? Still {$2,313|two thousand, three hundred and thirteen}, thirty years later. Only her taxes, insurance and repairs go up.", 0.4, st=2)
seg("r4", "lever", "And buying has a second secret weapon: leverage.", 0.2, chap="Buying's secret weapons", st=0)
seg("r5", "lever", "If prices rise four percent in year one, Nora's home gains about {$16,700|sixteen thousand, seven hundred dollars} in value.", 0.2, st=1)
seg("r6", "lever", "But she only put in ninety six thousand of her own money. That's like a {17%|seventeen percent} return on her cash.", 0.25, st=2)
seg("r7", "lever", "Leverage cuts both ways, though. If prices fall, she loses on the whole house, not just her deposit.", 0.6, st=3)

# ---------- 3 THE SCOREBOARD ----------
seg("b1", "score", "So let's keep score. We'll count what each of them would walk away with,", 0.05, chap="The scoreboard", y=1, st=0)
seg("b2", "score", "after selling costs, after paying off the loan, and after tax.", 0.25, y=1, st=0)
seg("b3", "score", "After one year: Nora has {$77K|seventy seven thousand}. Theo has {$117K|a hundred and seventeen thousand}.", 0.25, y=1, st=1)
seg("b4", "score", "Nora's behind, because selling a home costs around six percent, and her early payments were mostly interest.", 0.3, y=1, st=1)
seg("b5", "score", "Year five: Nora {$162K|a hundred and sixty two thousand}. Theo {$214K|two hundred and fourteen thousand}.", 0.25, y=5, st=1)
seg("b6", "score", "Year ten: Nora {$292K|two hundred and ninety two thousand}. Theo {$366K|three hundred and sixty six thousand}.", 0.3, y=10, st=1)
seg("b7", "score", "Theo is winning. But Nora's home keeps rising in value, and her loan keeps shrinking. So does she catch up?", 0.6, y=10, st=2)

# ---------- 4 WHERE THE MONEY GOES ----------
seg("w1", "where", "Before we jump to year thirty, here's something most people never add up.", 0.15, chap="Where the money goes", st=0)
seg("w2", "where", "Over thirty years, Nora pays {$499K|almost half a million dollars} in interest.", 0.1, st=1)
seg("w3", "where", "{$215K|Two hundred and fifteen thousand} in property tax.", 0.1, st=2)
seg("w4", "where", "{$134K|A hundred and thirty four thousand} in insurance.", 0.1, st=3)
seg("w5", "where", "And {$238K|two hundred and thirty eight thousand} in maintenance.", 0.2, st=4)
seg("w6", "where", "That's {$1.09M|one point oh nine million dollars} she never gets back.", 0.25, st=5)
seg("w7", "where", "Theo's total rent over the same thirty years? {$1.12M|One point one two million}.", 0.25, st=6)
seg("w8", "where", "Almost the same. So the old line that renting is throwing money away? Owning throws money away too. Just in different places.", 0.4, st=6)
seg("w9", "outro", "Before I show you year thirty, pause and comment who you think wins. Nora, or Theo?", 0.8, st=2)

# ---------- 5 THIRTY YEARS LATER ----------
seg("t1", "chart", "Okay. Thirty years later.", 0.2, chap="30 years later", mode="base", st=0)
seg("t2", "chart", "Nora owns her home outright. It's now worth {$1.35M|one point three five million dollars}.", 0.2, st=1)
seg("t3", "chart", "If she sold, she'd walk away with about {$1.18M|one point one eight million}.", 0.2, st=2)
seg("t4", "chart", "Theo's investments? {$1.72M|One point seven two million}.", 0.25, st=3)
seg("t5", "chart", "With these numbers, Theo wins by more than half a million dollars.", 0.4, st=3)
seg("t6", "chart", "But hold on. This is where it flips.", 0.7, st=3)

# ---------- 6 TWIST 1 ----------
seg("x1", "twist", "Twist number one. Theo only wins because he invested every spare dollar, every month, for thirty years.", 0.2, chap="Twist 1: the real Theo", n=1, st=0)
seg("x2", "twist", "That's three hundred and sixty months in a row of not touching it. No new car. No upgrade when he gets a raise.", 0.25, n=1, st=0)
seg("x3", "chart", "So what if Theo is a normal human, and the extra twelve hundred a month just quietly gets spent?", 0.2, mode="spend", st=0)
seg("x4", "chart", "He'd still have his starting {$96K|ninety six thousand} invested. After thirty years, that's about {$677K|six hundred and seventy seven thousand}.", 0.2, st=1)
seg("x5", "chart", "Nora's {$1.18M|one point one eight million} crushes that.", 0.25, st=2)
seg("x6", "chart", "A mortgage forces you to save. Renting only wins if you invest the difference. Every single month.", 0.6, st=2)

# ---------- 7 TWIST 2 ----------
seg("y1", "twist", "Twist number two. Our comparison wasn't totally fair.", 0.2, chap="Twist 2: a fair rent", n=2, st=0)
seg("y2", "twist", "The typical rent includes lots of small apartments. But Nora bought a whole house.", 0.2, n=2, st=1)
seg("y3", "twist", "Renting a similar house often costs more. Let's say {$2,400|twenty four hundred dollars} a month.", 0.3, n=2, st=2)
seg("y4", "chart", "Now watch the lines.", 0.15, mode="rent2400", st=0)
seg("y5", "chart", "Theo still leads at first. But around year nine, Nora overtakes him.", 0.2, st=1)
seg("y6", "chart", "By year thirty: Nora {$1.25M|one point two five million}. Theo {$1.13M|one point one three million}.", 0.25, st=2)
seg("y7", "chart", "And if mortgage rates drop to six percent, Nora takes the lead in just five years, and wins by more than four hundred thousand.", 0.4, mode="rent2400r6", st=3)
seg("y8", "chart", "One catch. Even with the fairer rent, if Nora sells after five years, Theo is still ahead: {$181K|a hundred and eighty one thousand} versus {$162K|a hundred and sixty two}. Buying is a long game.", 0.6, mode="rent2400", st=4)

# ---------- 8 PRICE TO RENT ----------
seg("p1", "ptr", "So how do you know which world you live in? There's a simple test called the price to rent ratio.", 0.2, chap="The 30-second test", st=0)
seg("p2", "ptr", "Take the price of a home, and divide it by a year of rent for a similar place.", 0.25, st=1)
seg("p3", "ptr", "Our first example: {$417,500|four hundred seventeen thousand five hundred}, divided by twelve months of {$1,962|nineteen sixty two}, is about {17.7|seventeen point seven}.", 0.2, st=2)
seg("p4", "ptr", "With the fairer rent of {$2,400|twenty four hundred}, it's {14.5|fourteen point five}.", 0.25, st=3)
seg("p5", "ptr", "A common rule of thumb: below about fifteen, buying tends to win. Above about twenty, renting tends to win.", 0.2, st=4)
seg("p6", "ptr", "In between, it really depends on the other details.", 0.6, st=4)

# ---------- 9 IT DEPENDS ----------
seg("d1", "check", "So, should you rent or buy? Honestly, it depends on four things.", 0.2, chap="So who wins?", st=0)
seg("d2", "check", "One. Your price to rent ratio.", 0.15, st=1)
seg("d3", "check", "Two. How long you'll stay. Selling costs eat your gains if you move after a few years, and the typical seller now stays about eleven years.", 0.2, st=2)
seg("d4", "check", "Three. Would you really invest the difference, every month?", 0.15, st=3)
seg("d5", "check", "And four. The things that aren't money. Stability, freedom, and a place that's truly yours.", 0.5, st=4)
seg("d6", "check", "These numbers are illustrations, not predictions. Home prices, rates and returns can all go differently.", 0.6, st=4, small=True)

# ---------- OUTRO (loops back to the opening line) ----------
seg("o1", "outro", "So, are you Team Nora or Team Theo? And what's the price to rent ratio where you live? Tell me in the comments.", 0.3, st=0)
seg("o2", "outro", "Because remember. Same salary. Same city. Nora buys a house. Theo rents.", 0.8, st=1)

SEGMENTS = S
VOICE = "af_heart"
LANG = "en-us"
SPEED = 1.0

# ---------- END CARD (appended with endcard_tts.py; logo + "watch our Shorts") ----------
SEGMENTS.append(dict(id="e1", scene="endcard", text="Want money maths in under a minute? Watch our Shorts, there's a new one every day. And subscribe to Finance Advised.", pause=7.0, show={}))
