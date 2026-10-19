"""1280x720 thumbnail for L02 (reuses render.py drawing helpers)."""
import os
os.environ.setdefault("TIMINGS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "timings.json"))
import render as R
from PIL import Image, ImageDraw
W, H = 1920, 1080
img = Image.new("RGB", (W, H), R.BG); d = ImageDraw.Draw(img)
for i, col in enumerate([(52, 34, 22), (34, 26, 58), (14, 40, 52)]):
    d.rectangle([i * W / 3, 0, (i + 1) * W / 3, H], fill=col)
for (lab, colr, who), x in zip([("CASH", R.NORA, "N"), ("LOAN", R.MAX, "M"), ("LEASE", R.THEO, "T")], (320, 960, 1600)):
    R.text(d, (x, 140), lab, R.font(R.F_BLK, 150), colr, stroke=9)
    R.person3(d, x - 90, 650, 1.05, colr, who, 0.5)
    R.car(d, x + 110, 730, 0.75, colr)
d.rectangle([0, 880, W, H], fill=(255, 216, 77))
R.text(d, (W / 2, 980), "ONE COSTS $56,000 MORE", R.font(R.F_BLK, 110), (20, 20, 20))
out = os.path.join(R.HERE, "thumb.jpg"); img.resize((1280, 720), Image.LANCZOS).save(out, quality=90); print(out)
