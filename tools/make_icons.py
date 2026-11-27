"""Draw the home-screen icon: concentric glass rings with an ember arc on ink, like the dial itself."""
import sys, os
from PIL import Image, ImageDraw, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
S = 1024
img = Image.new("RGB", (S, S), (8, 9, 13))

# soft light field behind the glass
glow = Image.new("RGB", (S, S), (0, 0, 0))
g = ImageDraw.Draw(glow)
g.ellipse((-200, -260, 700, 640), fill=(150, 62, 30))
g.ellipse((420, 480, 1260, 1320), fill=(22, 96, 90))
glow = glow.filter(ImageFilter.GaussianBlur(170))
img = Image.blend(img, glow, 0.85)

d = ImageDraw.Draw(img, "RGBA")
c = S / 2
for r0, r1 in ((0.755, 0.94), (0.53, 0.715), (0.34, 0.49)):
    a, b = r1 * c * 0.92, r0 * c * 0.92
    d.ellipse((c - a, c - a, c + a, c + a), fill=(255, 255, 255, 20), outline=(255, 255, 255, 70), width=4)
    d.ellipse((c - b, c - b, c + b, c + b), fill=(8, 9, 13, 70), outline=(255, 255, 255, 40), width=3)
# ember progress arc on the reps ring
rm = (0.53 + 0.715) / 2 * c * 0.92
w = int(0.07 * c)
d.arc((c - rm, c - rm, c + rm, c + rm), start=-90, end=150, fill=(255, 138, 80, 255), width=w)
# glass core
core = 0.31 * c * 0.92
d.ellipse((c - core, c - core, c + core, c + core), fill=(255, 255, 255, 34), outline=(255, 255, 255, 120), width=4)
hl = core * 0.62
d.ellipse((c - hl - core * 0.25, c - core * 0.86, c + hl - core * 0.25, c - core * 0.1), fill=(255, 255, 255, 30))

for size in (512, 192, 180):
    img.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, f"icon-{size}.png"), optimize=True)
print("icons ok")
