"""A copy of a reference photo, enlarged, with a pixel grid, for reading positions off it by eye.

    python Analizes_ocarinas/Low_voicing/photo_grid.py reference_photos/spencer_02_thumb_face.png [scale] [step]
"""
import pathlib
import sys

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
src = HERE / sys.argv[1]
scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
step = int(sys.argv[3]) if len(sys.argv) > 3 else 25
im = Image.open(src).convert("RGB")
im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
d = ImageDraw.Draw(im)
for x in range(0, im.width, step * scale):
    d.line([(x, 0), (x, im.height)], fill=(255, 60, 60) if (x // scale) % 100 == 0 else (255, 200, 0), width=1)
    d.text((x + 2, 2), str(x // scale), fill=(255, 255, 255))
for y in range(0, im.height, step * scale):
    d.line([(0, y), (im.width, y)], fill=(255, 60, 60) if (y // scale) % 100 == 0 else (255, 200, 0), width=1)
    d.text((2, y + 2), str(y // scale), fill=(255, 255, 255))
out = HERE / "reference_photos" / (src.stem + "_grid.png")
im.save(out)
print(out)
