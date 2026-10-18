# "Same Raise" Short (two-character story, ~30s, loops back to the opening line).
# Mia and Sam both get a +$500/month raise. Mia spends all of it. Sam invests half ($250/mo = $3,000/yr) at 7% avg.
#   Sam after 10y = $41,449   20y = $122,986   30y = $283,382   (put in $90,000)
#   Mia = $0 extra saved.

SEGMENTS = [
    ("hook",   [("SAME JOB.", "Same job."), ("SAME RAISE.", "Same raise."), ("30 YEARS", "Thirty years"),
                ("LATER,", "later,"), ("ONE HAS", "one has"), ("$283,000.", "two hundred and eighty three thousand."),
                ("THE OTHER?", "The other?"), ("ZERO.", "Zero.")], 0.3),
    ("setup",  [("MIA AND SAM", "Mia and Sam"), ("BOTH GET", "both get"), ("A $500", "a five hundred dollar"),
                ("RAISE.", "raise.")], 0.2),
    ("mia",    [("MIA", "Mia"), ("UPGRADES", "upgrades"), ("EVERYTHING.", "everything."), ("NEW CAR.", "New car."),
                ("BIGGER", "Bigger"), ("APARTMENT.", "apartment."), ("ALL OF IT,", "All of it,"), ("GONE.", "gone.")], 0.2),
    ("sam",    [("SAM", "Sam"), ("ENJOYS HALF,", "enjoys half,"), ("AND INVESTS", "and invests"),
                ("THE OTHER", "the other"), ("$250.", "two fifty.")], 0.2),
    ("grow",   [("10 YEARS:", "Ten years,"), ("$41,000.", "forty one thousand."), ("20 YEARS:", "Twenty years,"),
                ("$123,000.", "a hundred and twenty three thousand.")], 0.15),
    ("fin_a",  [("30 YEARS...", "Thirty years...")], 0.45),
    ("fin",    [("$283,000.", "two hundred and eighty three thousand.")], 0.3),
    ("q",      [("SO WHO", "So who"), ("ARE YOU?", "are you?"), ("MIA", "Mia"), ("OR SAM?", "or Sam?"),
                ("SAME JOB.", "Same job."), ("SAME RAISE.", "Same raise.")], 0.15),
]

VOICE = "af_heart"
SPEED = 1.12
