import sys, math
sys.path.insert(0, '/home/user/edgex-relay/ai-workforce/pod-kit')
from watercolor import Canvas, ellipse, rect
from PIL import Image, ImageDraw
# usage: python3 brand/logo.py OUT.png [seed]  (the Etsy shop icon is seed 21, cropped 7% each side)
OUT = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
W = 1600
c = Canvas(W, W, seed=seed)
cx, cy, s = W * 0.47, W * 0.62, W * 0.24
SAGE, SAGE2 = '#8fb3a0', '#b9d3c4'
BLUSH, BLUSH2 = '#e7928c', '#f2bcb3'
# soft background wash (a loose round puddle of colour behind the mug)
c.wash(ellipse(W / 2, W / 2, W * 0.40, W * 0.40, 22), '#f3d9c9', '#e3eee6', strength=0.32, layers=44, spread=0.07)
# mug body + handle
body = rect(cx - s * 0.62, cy - s * 0.5, cx + s * 0.62, cy + s * 0.68)
def heart_pts(x, y, k, n=26):
    return [(x + k * 16 * math.sin(2 * math.pi * i / n) ** 3,
             y - k * (13 * math.cos(2 * math.pi * i / n) - 5 * math.cos(4 * math.pi * i / n)
                      - 2 * math.cos(6 * math.pi * i / n) - math.cos(8 * math.pi * i / n))) for i in range(n)]
c.wash(body, SAGE, SAGE2, strength=0.75, spread=0.02, layers=30)
_o = ellipse(cx + s * 0.8, cy + s * 0.08, s * 0.32, s * 0.36, 32); _i = ellipse(cx + s * 0.8, cy + s * 0.08, s * 0.17, s * 0.21, 32)
ring = _o + [_o[0]] + [_i[0]] + _i[::-1] + [_i[0]]
c.wash(ring, SAGE, None, strength=0.6, spread=0.01, layers=18)
c.wash(ellipse(cx, cy - s * 0.5, s * 0.62, s * 0.13, 16), '#a8714f', '#c99068', strength=0.8, layers=18)
# steam rising into a heart: a big blush heart wash, then one ink line curling up into it
hx, hy, hk = cx + s * 0.05, cy - s * 1.45, s * 0.033
c.wash(heart_pts(hx, hy, hk), BLUSH, BLUSH2, strength=0.62, layers=34, spread=0.04)
ink = max(3, s * 0.028)
c.ink_line(body, width=ink)
c.ink_line(ellipse(cx, cy - s * 0.5, s * 0.62, s * 0.13, 22), width=ink * 0.85)
ho = ellipse(cx + s * 0.8, cy + s * 0.08, s * 0.32, s * 0.36, 24)
c.ink_line([p for p in ho if p[0] > cx + s * 0.62], width=ink * 0.85, closed=False)
hi = ellipse(cx + s * 0.8, cy + s * 0.08, s * 0.17, s * 0.21, 24)
c.ink_line([p for p in hi if p[0] > cx + s * 0.62], width=ink * 0.7, closed=False)
steam = [(cx + s * 0.05 + s * 0.1 * math.sin(math.pi * t / 7), cy - s * 0.62 - s * 0.06 * t) for t in range(8)]
c.ink_line(steam, width=ink * 0.75, closed=False, alpha=200, passes=1)
c.ink_line(heart_pts(hx, hy, hk, 40), width=ink * 0.8, alpha=210, passes=1)
im = c.on_paper('#fbf6ef')
im.save(OUT)
