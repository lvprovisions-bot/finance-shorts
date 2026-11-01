# THEO EXPLAINS #7: marginal vs effective tax rate. Theo earns $80K, is "in the 22% bracket", and thinks
# he pays 22% of everything ($17,600). Nora: 22% only hits the top slice; real bill $8,770 (~11%).
# Source: IRS Rev. Proc. 2025-32 (2026 tax year, single filers; confirmed via Journal of Accountancy, 9 Oct 2025):
#   standard deduction $16,100 | 10% to $12,400 | 12% to $50,400 | 22% to $105,700
# Assumptions: single filer, $80,000 salary, standard deduction only, federal income tax only (no state/FICA/credits).
# Maths (python, see bottom):
#   taxable = 80,000 - 16,100 = 63,900
#   10%: 12,400 * .10 = 1,240 | 12%: (50,400-12,400)=38,000 * .12 = 4,560 | 22%: (63,900-50,400)=13,500 * .22 = 2,970
#   tax = 8,770 -> 8,770/80,000 = 10.96% of salary ("about 11%")
#   Theo's flat maths: 80,000 * .22 = 17,600 -> overestimate 8,830 (about double)
# First line drafts (picked #1):
#   1 "Eighty K salary, twenty-two percent bracket. So I pay seventeen thousand six hundred in tax!"  <- number + wrong claim
#   2 "Seventeen thousand six hundred dollars. That's my tax bill, twenty-two percent of everything!"
#   3 "The twenty-two percent bracket takes twenty-two percent of my whole paycheck, right?"
# Speakers: N = Nora (af_heart), T = Theo (am_michael)

SEGMENTS = [
    ("hook",  "T", [("$80K SALARY,", "Eighty K salary,"), ("22%", "twenty two percent"), ("BRACKET.", "bracket."),
                    ("SO I PAY", "So I pay"), ("$17,600", "seventeen thousand six hundred"), ("IN TAX!", "in tax!")], 0.15),
    ("no",    "N", [("THEO.", "Theo."), ("22% ONLY HITS", "Twenty two percent only hits"), ("YOUR TOP", "your top"), ("SLICE.", "slice.")], 0.12),
    ("ded",   "N", [("FIRST", "First"), ("$16,100", "sixteen thousand one hundred"), ("IS", "is"), ("TAX-FREE.", "tax free.")], 0.1),
    ("slices","N", [("THEN 10%,", "Then ten percent,"), ("THEN 12%.", "then twelve percent."), ("ONLY THE LAST", "Only the last"),
                    ("$13,500", "thirteen thousand five hundred"), ("PAYS 22%.", "pays twenty two.")], 0.12),
    ("total", "N", [("REAL BILL:", "Real bill,"), ("$8,770.", "eight thousand seven hundred seventy."), ("ABOUT 11%.", "About eleven percent.")], 0.15),
    ("punch", "T", [("GREAT.", "Great."), ("NOW WHAT", "Now what"), ("DO I", "do I"), ("COMPLAIN", "complain"), ("ABOUT", "about"), ("AT PARTIES?", "at parties?")], 0.3),
    ("q",     "N", [("WHAT DID", "What did"), ("YOU THINK", "you think"), ("YOUR RATE WAS?", "your rate was?"), ("TELL US", "Tell us"), ("BELOW.", "below.")], 0.15),
    ("loop",  "T", [("WAIT.", "Wait."), ("$80K SALARY...", "Eighty K salary...")], 0.05),
]

VOICES = {"N": "af_heart", "T": "am_michael"}
SPEED = 1.15

if __name__ == "__main__":
    B = [(12400, .10), (50400, .12), (105700, .22), (201775, .24)]
    def tax(x):
        t, lo, parts = 0, 0, []
        for hi, r in B:
            if x > lo:
                p = (min(x, hi) - lo) * r; parts.append((min(x, hi) - lo, r, p)); t += p
            lo = hi
        return t, parts
    taxable = 80000 - 16100
    t, parts = tax(taxable)
    print("taxable", taxable, "parts", parts, "tax", t, "eff", round(t / 80000 * 100, 2), "theo", 80000 * .22, "diff", 80000 * .22 - t)
