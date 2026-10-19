# LONG-FORM L01: AQA GCSE Business (8132) 3.3 Business operations -> production processes + managing stock.
# Spec (aqa.org.uk 8132 subject content 3.3): "familiar with job and flow production methods and understand when
# each is appropriate"; "how production might be made more efficient by the use of lean production techniques";
# "evaluate the use of managing stock using JIT ... reduced costs vs more frequent deliveries and lost bulk-buying
# discounts ... benefit of spare stock vs cost of holding buffer stock".
#
# Illustrative numbers (fictional businesses), computed:
#   Rosa's cake: ingredients £40 + 6 h x £15 = £90 labour -> £130 to make one cake; sells for £300.
#   CrunchCo: fixed costs £500,000 / yr, variable cost 5p per pack.
#     1,000,000 packs  -> 500000/1e6  + 0.05 = £0.55 per pack
#     10,000,000 packs -> 500000/1e7  + 0.05 = £0.10 per pack
#   Kaizen: 3 seconds saved per box x 2,000 boxes/day = 6,000 s = 100 minutes per day.
#   Stock: storm delays flour 2 days. JIT (no buffer) -> line stops 2 days. JIC with 3 days buffer -> keeps running.
#
# Each segment: (id, scene, spoken text, pause after, show-data for the scene)

S = []
def seg(i, scene, text, pause=0.25, **show):
    S.append(dict(id=i, scene=scene, text=text, pause=pause, show=show))

# ---- hook ----
seg("h1", "hook", "Was your phone made before you bought it, or after?", 0.35, k="q")
seg("h2", "hook", "That one question unlocks a whole chunk of A Q A G C S E Business.", 0.2, k="aqa")
seg("h3", "menu", "In the next few minutes: job production, flow production, lean production,", 0.05,
    items=["Job production", "Flow production", "Lean production"])
seg("h4", "menu", "just in time, just in case, and kaizen.", 0.15, items=["Just in time (JIT)", "Just in case (JIC)", "Kaizen"])
seg("h5", "menu", "With the exam phrases that actually get you the marks.", 0.5, items=["+ exam tips"])

# ---- chapter 1: production ----
seg("p1", "define", "First, what is production?", 0.2, chap="1  Production", term="Production", d="")
seg("p2", "define", "Production means turning raw materials and components into finished goods or services.", 0.3,
    chap="1  Production", term="Production", d="Turning raw materials and components into finished goods or services.")
seg("p3", "define", "A Q A wants you to know two methods of production, job and flow, and when each one is appropriate.", 0.5,
    chap="1  Production", term="Methods of production", d="Job production  vs  flow production, and when each is appropriate.")

# ---- chapter 2: job production ----
seg("j1", "rosa", "Meet Rosa. She runs a bakery that makes personalised wedding cakes.", 0.2, st=0)
seg("j2", "rosa", "Nothing gets baked until a customer places an order.", 0.15, st=1)
seg("j3", "rosa", "Then she makes one unique cake, to that customer's exact design.", 0.3, st=2)
seg("j4", "define", "That's job production: making single, one off products, to a customer's specific requirements.", 0.3,
    chap="2  Job production", term="Job production", d="Making single, one-off products to a customer's specific requirements.", tag="MADE TO ORDER")
seg("j5", "define", "It's labour intensive, because it relies on skilled workers rather than machines.", 0.4,
    chap="2  Job production", term="Labour intensive", d="Relies mainly on (skilled) workers rather than machinery.", tag="KEY TERM")
seg("j6", "rosacost", "Rosa's cake costs forty pounds in ingredients, plus six hours of her time at fifteen pounds an hour.", 0.15, st=0)
seg("j7", "rosacost", "That's a hundred and thirty pounds to make just one cake.", 0.15, st=1)
seg("j8", "rosacost", "But because it's unique, she can charge three hundred.", 0.4, st=2)
seg("j9", "pc", "So, the advantages of job production.", 0.1, chap="2  Job production", title="JOB PRODUCTION", side="pro", item=None)
seg("j10", "pc", "High quality, unique products, that meet the customer's exact needs.", 0.1, side="pro", item="High quality, unique products")
seg("j11", "pc", "A higher price can be charged.", 0.1, side="pro", item="Higher prices can be charged")
seg("j12", "pc", "And the work is varied, so workers are often more motivated.", 0.25, side="pro", item="Varied work: motivated staff")
seg("j13", "pc", "The disadvantages: it's slow.", 0.1, side="con", item="Slow to produce")
seg("j14", "pc", "The cost per unit is high, because labour costs are high.", 0.1, side="con", item="High cost per unit")
seg("j15", "pc", "And tools and equipment may need changing for every new job.", 0.3, side="con", item="Equipment changed per job")
seg("j16", "examples", "Other examples: a made to measure suit, a custom built house, a tattoo, or a bridge.", 0.6,
    title="JOB PRODUCTION EXAMPLES", items=["suit", "house", "tattoo", "bridge"])

# ---- chapter 3: flow production ----
seg("f1", "flow", "Now meet CrunchCo, a biscuit factory.", 0.15, st=0)
seg("f2", "flow", "Its machines make the same biscuit, non stop, on a production line.", 0.15, st=1)
seg("f3", "flow", "The biscuits are made before anyone buys them, then sold later from stock.", 0.3, st=2)
seg("f4", "define", "That's flow production: making large quantities of identical products, continuously, on a production line.", 0.3,
    chap="3  Flow production", term="Flow production", d="Making large quantities of identical products continuously on a production line.", tag="MADE FOR STOCK")
seg("f5", "define", "It's also called mass production, and it's capital intensive, relying on machinery and automation.", 0.4,
    chap="3  Flow production", term="Capital intensive", d="Relies mainly on machinery and automation rather than workers.", tag="KEY TERM")
seg("f6", "cost", "CrunchCo's machines and factory cost five hundred thousand pounds a year, plus five pence of ingredients per pack.", 0.2, st=0)
seg("f7", "cost", "Make one million packs, and each pack costs fifty five pence.", 0.2, st=1)
seg("f8", "cost", "Make ten million, and it falls to just ten pence.", 0.2, st=2)
seg("f9", "cost", "The fixed costs are spread over more units. That's economies of scale.", 0.45, st=3)
seg("f10", "pc", "Advantages of flow production: a low cost per unit, thanks to economies of scale.", 0.1, chap="3  Flow production",
    title="FLOW PRODUCTION", side="pro", item="Low cost per unit (economies of scale)", reset=True)
seg("f11", "pc", "Very high output, often running twenty four hours a day.", 0.1, side="pro", item="High output, can run 24/7")
seg("f12", "pc", "And consistent, standardised quality.", 0.25, side="pro", item="Consistent quality")
seg("f13", "pc", "Disadvantages: it's very expensive to set up.", 0.1, side="con", item="Expensive to set up")
seg("f14", "pc", "Products can't be customised.", 0.1, side="con", item="No customisation")
seg("f15", "pc", "Repetitive work can demotivate staff.", 0.1, side="con", item="Repetitive, demotivating work")
seg("f16", "pc", "And if one machine breaks down, the whole line can stop.", 0.5, side="con", item="One breakdown stops the line")

# ---- chapter 4: which is appropriate ----
seg("a1", "table", "So which method is appropriate? It depends on the product and the customer.", 0.2, chap="4  Which is appropriate?", st=0)
seg("a2", "table", "Unique products, low quantities, and customers who'll pay more? Job production.", 0.2, st=1)
seg("a3", "table", "Identical products, huge demand, and low prices? Flow production.", 0.4, st=2)
seg("a4", "tip", "Exam tip. Always link your answer to the business in the case study.", 0.15, chap="Exam tip", st=0)
seg("a5", "tip", "For example: because the bakery makes personalised cakes, job production is appropriate, as every order is different.", 0.5, st=1)

# ---- chapter 5: lean production ----
seg("l1", "define", "Next, efficiency in production.", 0.15, chap="5  Lean production", term="Efficiency", d="")
seg("l2", "define", "Lean production means making products more efficiently, by cutting waste.", 0.15, chap="5  Lean production",
    term="Lean production", d="Making production more efficient by reducing waste.")
seg("l3", "define", "Wasted materials, wasted time, wasted stock, and faulty products.", 0.3, chap="5  Lean production",
    term="Lean production", d="Making production more efficient by reducing waste.", waste=True)
seg("l4", "define", "Two lean techniques you need are kaizen, and just in time.", 0.45, chap="5  Lean production",
    term="Lean techniques", d="Kaizen  and  just in time (JIT).")
seg("k1", "kaizen", "Kaizen is Japanese for continuous improvement.", 0.15, st=0)
seg("k2", "kaizen", "Every worker is encouraged to suggest lots of small improvements, all the time.", 0.2, st=1)
seg("k3", "kaizen", "At CrunchCo, a packer suggests moving the boxes closer. It saves three seconds per box.", 0.15, st=2)
seg("k4", "kaizen", "Over two thousand boxes a day, that's a hundred minutes saved, every single day.", 0.3, st=3)
seg("k5", "pc", "Kaizen reduces waste, and staff feel valued, which can motivate them.", 0.1, chap="5  Lean production",
    title="KAIZEN", side="pro", item="Less waste, motivated staff", reset=True)
seg("k6", "pc", "But it takes time for meetings and training, and small changes may not be enough.", 0.5, side="con",
    item="Takes time; small gains")

# ---- chapter 6: managing stock ----
seg("s1", "define", "Finally, managing stock. There are two approaches.", 0.15, chap="6  Managing stock", term="Managing stock", d="")
seg("s2", "define", "Just in time, or J I T: stock arrives exactly when it's needed, so little or no stock is held.", 0.25,
    chap="6  Managing stock", term="Just in time (JIT)", d="Stock arrives exactly when it is needed, so little or no stock is held.", tag="LEAN")
seg("s3", "define", "Just in case, or J I C: the business holds extra buffer stock, in case it's needed.", 0.4,
    chap="6  Managing stock", term="Just in case (JIC)", d="Holding extra buffer stock in case it is needed.", tag="BUFFER STOCK")
seg("s4", "stock", "CrunchCo is thinking about switching to just in time.", 0.15, st=0)
seg("s5", "stock", "It would save on storage, and its cash wouldn't be tied up in flour sitting in a warehouse.", 0.2, st=1)
seg("s6", "stock", "But then a storm hits, and the flour delivery is two days late.", 0.15, st=2)
seg("s7", "stock", "With just in time, the production line stops.", 0.15, st=3)
seg("s8", "stock", "With three days of buffer stock, it keeps running.", 0.45, st=4)
seg("s9", "pc", "So, just in time: lower storage costs, less waste from out of date stock, and more cash available.", 0.15,
    chap="6  Managing stock", title="JUST IN TIME", side="pro", item="Lower storage costs, less waste", reset=True)
seg("s10", "pc", "But more frequent deliveries, lost bulk buying discounts, and total reliance on suppliers.", 0.3, side="con",
    item="More deliveries, no bulk discounts, relies on suppliers")
seg("s11", "pc", "Just in case: you can meet sudden rises in demand, and keep producing if supplies are late.", 0.15,
    title="JUST IN CASE", side="pro", item="Meets demand spikes, keeps producing", reset=True)
seg("s12", "pc", "But storing it costs money, and stock can go out of date, or get damaged.", 0.3, side="con",
    item="Storage costs; stock can expire or be damaged")
seg("s13", "tip", "Exam tip. Weigh it up. Just in time suits fresh, perishable stock and reliable local suppliers.", 0.15,
    chap="Exam tip", st=0, alt=1)
seg("s14", "tip", "Just in case suits unpredictable demand, or suppliers that are far away or unreliable.", 0.5, st=1, alt=1)

# ---- quiz + outro ----
seg("q1", "quiz", "Quick quiz. A tailor makes a suit to fit one customer. Job, or flow?", 1.6, n=1, q="A tailor makes a suit to fit one customer.", a=("JOB", "FLOW"), st=0)
seg("q2", "quiz", "Job production.", 0.4, n=1, q="A tailor makes a suit to fit one customer.", a=("JOB", "FLOW"), st=1)
seg("q3", "quiz", "A sushi bar wants to cut waste from fish going off. Just in time, or just in case?", 1.6, n=2,
    q="A sushi bar wants to cut waste from fish going off.", a=("JIT", "JIC"), st=0)
seg("q4", "quiz", "Just in time.", 0.45, n=2, q="A sushi bar wants to cut waste from fish going off.", a=("JIT", "JIC"), st=1)
seg("o1", "outro", "So, would you rather run Rosa's bakery, or CrunchCo? Tell me in the comments.", 0.2, st=0)
seg("o2", "outro", "And remember: was it made before you bought it, or after? That's your answer.", 0.8, st=1)

SEGMENTS = S
VOICE = "bf_emma"
LANG = "en-gb"
SPEED = 1.0
