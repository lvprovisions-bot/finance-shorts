"""Make a clear, text-first Shorts thumbnail (1080x1920 JPEG, <2 MB).

Usage: python3 engine/thumbnail.py <video.mp4> <spec.json> <out.jpg>

spec.json:
{
  "bg_time": 24.0,                     # seconds into the video to use as the blurred background
  "tag": "WHO WINS?",                  # small pill above the headline (series / pillar name)
  "tag_color": "#FFD84D",
  "lines": [["SAME RAISE.", "#FFFFFF"], ["$283K", "#34D378"], ["vs $0", "#FF5454"]]
}
All important content stays inside the central band (y 520-1400) so 3:2 crops on the channel page/search keep it.
"""
import json, subprocess, sys, tempfile, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

W, H = 1080, 1920
F_BIG = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_TAG = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def grab(video, t):
    tmp = tempfile.mktemp(suffix=".png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); os.remove(tmp)
    return im.resize((W, H))


def fit_font(draw, text, max_w, start, path=F_BIG, stroke=14):
    size = start
    while size > 40:
        f = ImageFont.truetype(path, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
        if r - l <= max_w:
            return f, (r - l, b - t)
        size -= 6
    f = ImageFont.truetype(path, size)
    l, t, r, b = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    return f, (r - l, b - t)


def make(video, spec, out):
    bg = grab(video, spec.get("bg_time", 1.0))
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    img = bg.convert("RGBA")
    # central glow band
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.rounded_rectangle([40, 520, W - 40, 1400], radius=60, fill=(0, 0, 0, 120))
    img.alpha_composite(band)
    d = ImageDraw.Draw(img)
    lines = spec["lines"]
    rendered = []
    for i, (txt, col) in enumerate(lines):
        f, (tw, th) = fit_font(d, txt, 960, 230 if i else 200)
        rendered.append((txt, col, f, tw, th))
    total = sum(r[4] for r in rendered) + 40 * (len(rendered) - 1)
    tag = spec.get("tag")
    tag_h = 110 if tag else 0
    y = 960 - (total + tag_h) / 2
    if tag:
        ft = ImageFont.truetype(F_TAG, 58)
        l, t, r, b = d.textbbox((0, 0), tag, font=ft)
        pw = r - l + 80
        tc = hexrgb(spec.get("tag_color", "#FFD84D"))
        d.rounded_rectangle([W / 2 - pw / 2, y, W / 2 + pw / 2, y + 86], radius=43, fill=tc)
        d.text((W / 2, y + 43), tag, font=ft, fill=(10, 12, 16), anchor="mm")
        y += tag_h
    for txt, col, f, tw, th in rendered:
        d.text((W / 2, y + th / 2), txt, font=f, fill=hexrgb(col), anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0))
        y += th + 40
    img.convert("RGB").save(out, "JPEG", quality=88, optimize=True)
    assert os.path.getsize(out) < 2_000_000, "thumbnail over 2MB"
    print("thumbnail ok", out, os.path.getsize(out))


if __name__ == "__main__":
    make(sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3])
