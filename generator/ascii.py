import sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter, ImageOps

src, cols, rows, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
CHAR_ASPECT = 9.6 / 20  # sirina znaka / visina reda u SVG-u

img = Image.open(src).convert("RGB")
W, H = img.size
# isjeci na odnos stranica mreze znakova
target = (cols * CHAR_ASPECT) / rows
cw = min(W, int(H * target))
ch = min(H, int(cw / target))
x0 = (W - cw) // 2
img = img.crop((x0, 0, x0 + cw, ch))

# maska pozadine: flood fill od gornje/lijeve/desne ivice preko svijetlih, nezasicenih piksela
small = img.resize((cw // 3, ch // 3), Image.LANCZOS)
a = np.asarray(small).astype(float) / 255
mx, mn = a.max(2), a.min(2)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
lum = a @ [0.299, 0.587, 0.114]
bgcand = (lum > 0.72) & (sat < 0.09)
h, w = bgcand.shape
bg = np.zeros_like(bgcand)
q = deque()
for x in range(w):
    if bgcand[0, x]: q.append((0, x))
for y in range(h):
    for x in (0, w - 1):
        if bgcand[y, x]: q.append((y, x))
while q:
    y, x = q.popleft()
    if bg[y, x]: continue
    bg[y, x] = True
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and bgcand[ny, nx] and not bg[ny, nx]:
            q.append((ny, nx))
mask = Image.fromarray((~bg * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))

gray = ImageOps.grayscale(img)
gray = gray.filter(ImageFilter.UnsharpMask(radius=4, percent=160, threshold=2))
g = np.asarray(gray.resize((cols, rows), Image.LANCZOS)).astype(float) / 255
m = np.asarray(mask.resize((cols, rows), Image.BILINEAR)).astype(float) / 255

# rastegni kontrast samo unutar figure
fg = g[m > 0.5]
lo, hi = np.percentile(fg, 3), np.percentile(fg, 97)
g = np.clip((g - lo) / (hi - lo), 0, 1)

RAMP = " .'`,:;!|ijlrt*kmM%H#@"  # od rijetkog ka gustom
lines = []
for y in range(rows):
    s = ""
    for x in range(cols):
        if m[y, x] < 0.5:
            s += " "
            continue
        v = g[y, x] if mode == "dark" else 1 - g[y, x]
        s += RAMP[1 + int(v * (len(RAMP) - 2) + 0.5)]
    lines.append(s.rstrip())
print("\n".join(lines))
