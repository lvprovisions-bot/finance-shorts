"""1280x720 thumbnail for the long-form video (reuses render.py drawing helpers)."""
import os, sys
os.environ.setdefault("TIMINGS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "timings.json"))
import render as R
from PIL import Image, ImageDraw
W, H = 1920, 1080
img = Image.new("RGB", (W, H), R.BG); d = ImageDraw.Draw(img)
d.rectangle([0, 0, W / 2, H], fill=(52, 30, 22)); d.rectangle([W / 2, 0, W, H], fill=(14, 40, 52))
R.house(d, 300, 640, 1.7); R.person(d, 700, 760, 1.5, R.NORA, "N", 0.5)
R.apartment(d, 1640, 700, 1.55); R.person(d, 1230, 760, 1.5, R.THEO, "T", 0.5)
R.text(d, (480, 150), "BUY", R.font(R.F_BLK, 210), R.NORA, stroke=10)
R.text(d, (1440, 150), "RENT", R.font(R.F_BLK, 210), R.THEO, stroke=10)
d.ellipse([W / 2 - 110, 420, W / 2 + 110, 640], fill=(255, 216, 77)); R.text(d, (W / 2, 530), "VS", R.font(R.F_BLK, 110), (20, 20, 20))
d.rectangle([0, 900, W, H], fill=(255, 216, 77))
R.text(d, (W / 2, 990), "WHO'S RICHER IN 30 YEARS?", R.font(R.F_BLK, 104), (20, 20, 20))
out = os.path.join(R.HERE, "thumb.jpg"); img.resize((1280, 720), Image.LANCZOS).save(out, quality=90); print(out)
