# THEO EXPLAINS #1: Tax brackets. Theo turns down a raise because it "pushes him into the 22% bracket".
# Source: IRS Rev. Proc. 2025-32 (2026 rates, unmarried individuals, taxable income):
#   10% to $12,400 | 12% to $50,400 | 22% to $105,700 | 24% to $201,775 | 32% | 35% | 37%
# Assumptions: single filer, TAXABLE income (after deductions), federal income tax only (no state/payroll tax).
# Maths (python, see bottom of file):
#   Taxable $50,000: 12,400*10% = 1,240 + (50,000-12,400)*12% = 4,512  -> $5,752  (11.5% effective)
#   Taxable $52,000: 1,240 + 38,000*12% = 4,560 + (52,000-50,400)*22% = 352 -> $6,152 (11.8% effective)
#   Extra tax on the $2,000 raise = $400 ; Theo keeps $1,600.
#   Theo's WRONG flat maths: 50,000*12% = $6,000 ; 52,000*22% = $11,440 -> "+$5,440 tax for a $2,000 raise"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("I JUST", "I just"), ("TURNED DOWN", "turned down"), ("A RAISE!", "a raise!"),
                    ("IT PUSHES ME", "It pushes me"), ("INTO THE", "into the"), ("22%", "twenty two percent"),
                    ("BRACKET!", "bracket!")], 0.25),
    ("tmath", "T", [("NOW ALL", "Now all"), ("MY MONEY", "my money"), ("GETS TAXED", "gets taxed"), ("MORE.", "more."),
                    ("OVER $5,000", "Over five thousand dollars"), ("MORE TAX", "more tax"), ("FOR A", "for a"),
                    ("$2,000", "two thousand dollar"), ("RAISE!", "raise!")], 0.3),
    ("no",    "N", [("THEO.", "Theo."), ("THAT'S NOT", "That's not"), ("HOW BRACKETS", "how brackets"),
                    ("WORK.", "work.")], 0.2),
    ("bkt",   "N", [("THINK", "Think"), ("BUCKETS.", "buckets."), ("THE FIRST", "The first"),
                    ("$12,400:", "twelve thousand four hundred,"), ("10%.", "ten percent."),
                    ("UP TO", "Up to"), ("$50,400:", "fifty thousand four hundred,"), ("12%.", "twelve percent."),
                    ("ONLY MONEY", "Only money"), ("ABOVE", "above"), ("THAT LINE", "that line"),
                    ("PAYS 22%.", "pays twenty two.")], 0.25),
    ("raise", "N", [("YOUR $2,000", "Your two thousand dollar"), ("RAISE?", "raise?"), ("EXTRA TAX:", "Extra tax,"),
                    ("JUST $400.", "just four hundred."), ("YOU KEEP", "You keep"), ("$1,600.", "sixteen hundred.")], 0.25),
    ("turn",  "T", [("SO A RAISE", "So a raise"), ("NEVER MAKES", "never makes"), ("ME POORER?", "me poorer?")], 0.15),
    ("never", "N", [("NOT BECAUSE", "Not because"), ("OF BRACKETS.", "of brackets.")], 0.25),
    ("punch", "T", [("THEN I WANT", "Then I want"), ("TWO RAISES.", "two raises.")], 0.35),
    ("q",     "N", [("DID YOU", "Did you"), ("THINK IT", "think it"), ("WORKED", "worked"), ("THEO'S WAY?", "Theo's way?")], 0.2),
    ("loop",  "T", [("WAIT...", "Wait..."), ("SO WHY DID", "so why did"), ("I JUST", "I just"),
                    ("TURN DOWN", "turn down"), ("A RAISE?", "a raise?")], 0.1),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.12

if __name__ == "__main__":
    B = [(12400, .10), (50400, .12), (105700, .22), (201775, .24), (256225, .32), (640600, .35), (1e18, .37)]
    def tax(x):
        t, lo = 0, 0
        for hi, r in B:
            if x > lo: t += (min(x, hi) - lo) * r
            lo = hi
        return t
    print(tax(50000), tax(52000), tax(52000) - tax(50000), 52000 * .22 - 50000 * .12)
