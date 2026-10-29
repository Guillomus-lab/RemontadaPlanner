"""Regenerate app.ico to match Remontada Planner's actual brand gradient
(--accent #8b5cf6 purple -> --accent2 #ec4899 pink, used everywhere in the
UI: header title, buttons, level ring...) instead of the old generic
blue/green calendar+checkmark icon."""
import math
from PIL import Image, ImageDraw

SIZE = 256
ACCENT = (139, 92, 246)   # #8b5cf6
ACCENT2 = (236, 72, 153)  # #ec4899
GOLD = (251, 191, 36)     # #fbbf24 (the same accent used in splash/level-up gradients)

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i]-a[i])*t) for i in range(3))

def diag_gradient(size, c1, c2, c3=None):
    img = Image.new('RGB', (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2*(size-1))
            if c3 is None:
                px[x, y] = lerp(c1, c2, t)
            else:
                if t < 0.5:
                    px[x, y] = lerp(c1, c2, t/0.5)
                else:
                    px[x, y] = lerp(c2, c3, (t-0.5)/0.5)
    return img

def rounded_mask(size, radius):
    mask = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size-1, size-1], radius=radius, fill=255)
    return mask

base = diag_gradient(SIZE, ACCENT, ACCENT2, GOLD)
mask = rounded_mask(SIZE, SIZE // 5)
canvas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
canvas.paste(base, (0, 0), mask)
draw = ImageDraw.Draw(canvas)

# Calendar body (white rounded card) on the gradient background
pad = int(SIZE*0.14)
body_top = int(SIZE*0.26)
draw.rounded_rectangle([pad, body_top, SIZE-pad, SIZE-pad], radius=int(SIZE*0.08),
                        fill=(255, 250, 247, 255))

# Calendar "header strip" (darker band across the top of the card)
draw.rounded_rectangle([pad, body_top, SIZE-pad, body_top+int(SIZE*0.12)],
                        radius=int(SIZE*0.08), fill=lerp(ACCENT, ACCENT2, 0.5)+(255,))
draw.rectangle([pad, body_top+int(SIZE*0.06), SIZE-pad, body_top+int(SIZE*0.12)],
               fill=lerp(ACCENT, ACCENT2, 0.5)+(255,))

# Two binder rings poking above the card
ring_w = int(SIZE*0.045)
for cx in (SIZE*0.34, SIZE*0.66):
    draw.rounded_rectangle([cx-ring_w, int(SIZE*0.10), cx+ring_w, body_top+int(SIZE*0.08)],
                            radius=ring_w, fill=(255, 255, 255, 255))

# Three faint "task line" rows inside the card
line_color = (230, 220, 235, 255)
for i, ly in enumerate([0.46, 0.58, 0.70]):
    y = int(SIZE*ly)
    draw.rounded_rectangle([pad+int(SIZE*0.08), y, SIZE-pad-int(SIZE*0.08), y+int(SIZE*0.035)],
                            radius=int(SIZE*0.017), fill=line_color)

# Gold-outlined green checkmark badge, bottom-right — same "done" color as
# the rest of the app's UI (--done: #10d896)
badge_r = int(SIZE*0.22)
bx, by = int(SIZE*0.73), int(SIZE*0.78)
draw.ellipse([bx-badge_r, by-badge_r, bx+badge_r, by+badge_r], fill=(255, 250, 247, 255))
inner_r = int(badge_r*0.82)
draw.ellipse([bx-inner_r, by-inner_r, bx+inner_r, by+inner_r], fill=(16, 216, 150, 255))
# checkmark
check_w = int(SIZE*0.022)
pts = [(bx-inner_r*0.5, by+inner_r*0.05), (bx-inner_r*0.12, by+inner_r*0.45), (bx+inner_r*0.55, by-inner_r*0.4)]
draw.line(pts, fill=(255, 255, 255, 255), width=check_w, joint='curve')
for p in (pts[0], pts[-1]):
    draw.ellipse([p[0]-check_w/2, p[1]-check_w/2, p[0]+check_w/2, p[1]+check_w/2], fill=(255,255,255,255))

canvas.save('icon_source.png')
canvas.resize((256, 256), Image.LANCZOS).save('icon_preview.png')
sizes = [16, 24, 32, 48, 64, 128, 256]
canvas.save('app.ico', sizes=[(s, s) for s in sizes])
print('done')
