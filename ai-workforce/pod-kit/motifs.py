"""Watercolor motifs. Each function paints onto a Canvas at (x, y) with size s
(roughly the motif's radius in px) using a palette dict:
  {'main': hex, 'main2': hex, 'accent': hex, 'accent2': hex, 'leaf': hex, 'leaf2': hex}
Motifs are painted the way a watercolorist would: a light first wash for the
whole form, then smaller, darker wet-on-dry strokes for shape, then details
and (for objects) a loose ink line.
"""
import math
from watercolor import ellipse, petal, leaf, rect


def _rot(pts, cx, cy, a):
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


# ---------------------------------------------------------------- florals
def crescent(x, y, r, a0, a1, thick, n=10):
    """A curved petal edge: band between radius r and r - thick from angle a0 to a1."""
    outer = [(x + r * math.cos(a0 + (a1 - a0) * i / n), y + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inner = [(x + (r - thick * math.sin(math.pi * i / n)) * math.cos(a0 + (a1 - a0) * i / n),
              y + (r - thick * math.sin(math.pi * i / n)) * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n, -1, -1)]
    return outer + inner


def rose(c, x, y, s, P, color=None, color2=None):
    col = color or P['main']; col2 = color2 or P.get('main2', col)
    rnd = c.rnd
    # light first wash for the whole bloom, lighter at one side (wet-in-wet)
    c.wash(ellipse(x, y, s, s * 0.9, 16), col2, col, strength=0.5, spread=0.05, layers=36)
    # outer cupped petals: wide crescents around the bloom
    for i in range(5):
        a = i * 2 * math.pi / 5 + rnd.uniform(-0.3, 0.3)
        c.wash(crescent(x, y, s * 0.95, a - 0.7, a + 0.7, s * 0.3), col, None, strength=0.45, spread=0.03, layers=20, edge=0.9)
    # inner petals: smaller, darker, tighter crescents that spiral in
    for i, (r, th) in enumerate(((0.62, 0.22), (0.42, 0.17), (0.25, 0.12))):
        a = rnd.uniform(0, 6.28)
        c.wash(crescent(x, y + s * 0.05, s * r, a, a + 3.4, s * th), col, None, strength=0.6 + 0.15 * i, spread=0.03,
               layers=18, edge=1.0)
    c.wash(ellipse(x, y + s * 0.03, s * 0.13, s * 0.1, 10), col, None, strength=1.1, layers=16)


def daisy(c, x, y, s, P, color=None, n=8):
    col = color or P['accent']
    for i in range(n):
        a = i * 2 * math.pi / n + c.rnd.uniform(-0.1, 0.1)
        c.wash(petal(x, y, s, s * 0.32, a), col, P.get('accent2'), strength=0.55, spread=0.04, layers=22)
    c.wash(ellipse(x, y, s * 0.24, s * 0.24, 10), '#e0a83a', '#b8741f', strength=1.0, layers=24)


def wildflower(c, x, y, s, P, color=None):
    col = color or P['accent']
    for i in range(5):
        a = i * 2 * math.pi / 5 + c.rnd.uniform(-0.25, 0.25)
        c.wash(ellipse(x + s * 0.5 * math.cos(a), y + s * 0.5 * math.sin(a), s * 0.5, s * 0.38, 10, a), col,
               P.get('accent2'), strength=0.55, spread=0.06, layers=22)
    c.wash(ellipse(x, y, s * 0.2, s * 0.2, 8), '#6b4a2e', None, strength=0.9, layers=16)


def tulip(c, x, y, s, P, color=None, angle=0.0):
    col = color or P['main']
    stem = [(x - s * 0.04, y), (x + s * 0.04, y), (x + s * 0.06, y + s * 2.2), (x - s * 0.02, y + s * 2.2)]
    c.wash(_rot(stem, x, y, angle), P['leaf'], None, strength=0.8, spread=0.02, layers=16)
    c.wash(leaf(x, y + s * 1.9, s * 1.3, s * 0.3, -math.pi / 2 - 0.5 + angle), P['leaf'], P.get('leaf2'), strength=0.6)
    cup = [(x - s * 0.55, y - s * 0.9), (x - s * 0.3, y - s * 0.55), (x, y - s * 1.0), (x + s * 0.3, y - s * 0.55),
           (x + s * 0.55, y - s * 0.9), (x + s * 0.5, y - s * 0.2), (x, y + s * 0.1), (x - s * 0.5, y - s * 0.2)]
    c.wash(_rot(cup, x, y, angle), col, P.get('main2'), strength=0.7, spread=0.04, layers=30)
    c.wash(_rot([(x - s * 0.1, y - s * 0.8), (x + s * 0.2, y - s * 0.5), (x + s * 0.1, y), (x - s * 0.2, y - s * 0.2)], x, y, angle),
           col, None, strength=0.6, spread=0.03, layers=18)


def sprig(c, x, y, s, P, angle=-1.2, n=5, color=None):
    """A stem with paired leaves."""
    col = color or P['leaf']
    ca, sa = math.cos(angle), math.sin(angle)
    c.wash(leaf(x, y, s * 2, s * 0.025, angle), '#7d9670', None, strength=0.8, spread=0.02, layers=10)
    for i in range(n):
        t = (i + 1) / (n + 1)
        px, py = x + s * 2 * ca * t, y + s * 2 * sa * t
        for side in (-1, 1):
            c.wash(leaf(px, py, s * 0.55 * (1.1 - t * 0.4), s * 0.18, angle + side * 0.8), col, P.get('leaf2'),
                   strength=0.6, spread=0.05, layers=20)
    c.wash(leaf(x + s * 2 * ca, y + s * 2 * sa, s * 0.45, s * 0.15, angle), col, P.get('leaf2'), strength=0.6, layers=18)


def eucalyptus(c, x, y, s, P, angle=-1.0, n=6):
    ca, sa = math.cos(angle), math.sin(angle)
    c.wash(leaf(x, y, s * 2.2, s * 0.022, angle), '#8a9a8e', None, strength=0.8, spread=0.02, layers=10)
    for i in range(n):
        t = (i + 0.7) / n
        side = 1 if i % 2 else -1
        px, py = x + s * 2.2 * ca * t, y + s * 2.2 * sa * t
        off = s * 0.28 * (1 - t * 0.3)
        c.wash(ellipse(px + side * off * sa * -1, py + side * off * ca, off, off * 0.9, 12), '#8fb3a6', '#b9d3c6',
               strength=0.6, spread=0.05, layers=22)


def leaves_fan(c, x, y, s, P, angles=(-2.5, -1.9, -1.2, -0.6)):
    for a in angles:
        c.wash(leaf(x, y, s, s * 0.28, a), P['leaf'], P.get('leaf2'), strength=0.65, spread=0.05, layers=24)


def berries(c, x, y, s, P, n=5, color='#a8394f'):
    for i in range(n):
        a = c.rnd.uniform(0, 6.28); r = s * 0.6 * math.sqrt(c.rnd.random())
        c.wash(ellipse(x + r * math.cos(a), y + r * math.sin(a), s * 0.22, s * 0.22, 10), color, None,
               strength=0.8, spread=0.04, layers=18, edge=0.9)


def bouquet(c, x, y, s, P, flowers=('rose', 'daisy', 'rose', 'wildflower')):
    """A loose floral cluster centred on (x, y) spanning about 2s wide."""
    leaves_fan(c, x - s * 0.55, y + s * 0.1, s * 0.75, P, angles=(-2.9, -2.4, 2.7))
    leaves_fan(c, x + s * 0.55, y + s * 0.1, s * 0.75, P, angles=(-0.3, -0.8, 0.4))
    eucalyptus(c, x - s * 0.2, y - s * 0.2, s * 0.45, P, angle=-2.2)
    sprig(c, x + s * 0.2, y - s * 0.25, s * 0.45, P, angle=-0.9)
    spots = [(-0.45, 0.05, 0.42), (0.4, -0.05, 0.46), (0.0, 0.3, 0.34), (0.05, -0.28, 0.28)]
    for (dx, dy, r), f in zip(spots, flowers):
        fx, fy, fr = x + dx * s, y + dy * s, r * s
        if f == 'none':
            continue
        if f == 'rose':
            rose(c, fx, fy, fr, P, color=P['main'] if dx < 0.2 else P.get('accent', P['main']))
        elif f == 'daisy':
            daisy(c, fx, fy, fr, P)
        else:
            wildflower(c, fx, fy, fr, P)
    berries(c, x + s * 0.6, y + s * 0.35, s * 0.2, P)
    c.splatter(x, y, s * 1.1, P['main'], n=18)


def wreath(c, x, y, R, P, gap_top=True):
    """Florals around a ring (text goes in the middle)."""
    n = 18
    for i in range(n):
        a = -math.pi / 2 + (i + 0.5) * 2 * math.pi / n
        if gap_top and abs(math.remainder(a + math.pi / 2, 2 * math.pi)) < 0.55:
            continue
        px, py = x + R * math.cos(a), y + R * math.sin(a)
        c.wash(leaf(px, py, R * 0.32, R * 0.09, a + math.pi / 2 + 0.3), P['leaf'], P.get('leaf2'), strength=0.6, layers=20)
        c.wash(leaf(px, py, R * 0.28, R * 0.08, a + math.pi / 2 - 0.4), P['leaf'], P.get('leaf2'), strength=0.55, layers=20)
    eucalyptus(c, x - R * 0.95, y - R * 0.1, R * 0.28, P, angle=-1.9)
    eucalyptus(c, x + R * 0.95, y - R * 0.1, R * 0.28, P, angle=-1.2)
    for a, kind, sz in ((math.pi * 0.72, 'rose', 0.2), (math.pi * 0.28, 'rose', 0.2), (math.pi * 0.95, 'daisy', 0.14),
                        (0.05, 'wildflower', 0.13), (math.pi * 0.5, 'rose', 0.24), (math.pi * 0.6, 'wildflower', 0.1),
                        (math.pi * 0.4, 'daisy', 0.11)):
        px, py = x + R * math.cos(a), y + R * math.sin(a)
        {'rose': rose, 'daisy': daisy, 'wildflower': wildflower}[kind](c, px, py, R * sz, P)
    berries(c, x + R * 0.8, y + R * 0.6, R * 0.12, P)
    berries(c, x - R * 0.8, y + R * 0.6, R * 0.12, P)


# ---------------------------------------------------------------- objects
def mug(c, x, y, s, P, steam=True, color=None):
    col = color or P.get('object', '#9cc0cf')
    body = rect(x - s * 0.6, y - s * 0.55, x + s * 0.6, y + s * 0.65)
    c.wash(body, col, P.get('object2'), strength=0.6, spread=0.02, layers=26)
    handle = ellipse(x + s * 0.72, y + s * 0.05, s * 0.28, s * 0.3, 14)
    c.wash(handle, col, None, strength=0.5, spread=0.02, layers=16)
    c.wash(ellipse(x, y - s * 0.55, s * 0.6, s * 0.12, 16), '#8a5a3c', '#b07a52', strength=0.8, layers=18)
    c.ink_line(body, width=max(2, s * 0.03))
    c.ink_line(ellipse(x, y - s * 0.55, s * 0.6, s * 0.12, 20), width=max(2, s * 0.025))
    c.ink_line(ellipse(x + s * 0.72, y + s * 0.05, s * 0.2, s * 0.22, 16)[4:13], width=max(2, s * 0.025), closed=False)
    if steam:
        for k in (-0.25, 0.05, 0.35):
            pts = [(x + s * k + s * 0.08 * math.sin(t * 1.3), y - s * 0.75 - s * 0.09 * t) for t in range(9)]
            c.ink_line(pts, width=max(2, s * 0.02), closed=False, alpha=150, passes=1)


def books(c, x, y, s, P, colors=None):
    cols = colors or [P['main'], P.get('object', '#9cc0cf'), P.get('accent', '#e5b85a'), P['leaf']]
    h = s * 0.28
    for i, col in enumerate(cols):
        w = s * (1.3 - 0.12 * (i % 2)) ; off = s * 0.08 * ((i * 37) % 5 - 2) / 2
        y0 = y + s * 0.6 - (i + 1) * h
        box = rect(x - w / 2 + off, y0, x + w / 2 + off, y0 + h * 0.92)
        c.wash(box, col, None, strength=0.6, spread=0.015, layers=22)
        c.ink_line(box, width=max(2, s * 0.022))
        c.ink_line([(x - w / 2 + off + w * 0.12, y0 + h * 0.45), (x + w / 2 + off - w * 0.12, y0 + h * 0.45)],
                   width=max(1, s * 0.012), closed=False, alpha=140, passes=1)


def heart(c, x, y, s, P, color=None):
    col = color or P['main']
    pts = []
    for i in range(24):
        t = i / 24 * 2 * math.pi
        pts.append((x + s * 0.06 * 16 * math.sin(t) ** 3,
                    y - s * 0.06 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))))
    c.wash(pts, col, P.get('main2'), strength=0.7, spread=0.03, layers=30)


def paw(c, x, y, s, P, color=None):
    col = color or P.get('object', '#8a6a55')
    c.wash(ellipse(x, y + s * 0.2, s * 0.45, s * 0.38, 14), col, None, strength=0.75, layers=24)
    for dx, dy in ((-0.5, -0.3), (-0.18, -0.62), (0.18, -0.62), (0.5, -0.3)):
        c.wash(ellipse(x + s * dx, y + s * dy, s * 0.17, s * 0.21, 10), col, None, strength=0.8, layers=18)


def dog(c, x, y, s, P, color=None, ink=True):
    """A sitting dog, front view, built from soft rounded washes."""
    col = color or P.get('fur', '#c8914f'); col2 = P.get('fur2', '#ecc58f')
    rnd = c.rnd
    # body: chest + haunches
    c.wash(ellipse(x, y + s * 0.55, s * 0.52, s * 0.55, 18), col2, col, strength=0.55, spread=0.04, layers=34)
    c.wash(ellipse(x - s * 0.35, y + s * 0.85, s * 0.3, s * 0.25, 14), col, None, strength=0.5, spread=0.04, layers=24)
    c.wash(ellipse(x + s * 0.35, y + s * 0.85, s * 0.3, s * 0.25, 14), col, None, strength=0.5, spread=0.04, layers=24)
    # front legs and paws
    for dx in (-0.16, 0.16):
        c.wash(ellipse(x + s * dx, y + s * 0.78, s * 0.11, s * 0.3, 12), col2, col, strength=0.5, layers=22)
        c.wash(ellipse(x + s * dx, y + s * 1.05, s * 0.13, s * 0.08, 10), col2, None, strength=0.5, layers=16)
    # chest highlight
    c.wash(ellipse(x, y + s * 0.35, s * 0.2, s * 0.25, 12), '#f6e6cc', None, strength=0.35, layers=16)
    # head, muzzle, ears
    c.wash(ellipse(x, y - s * 0.22, s * 0.36, s * 0.34, 18), col2, col, strength=0.6, spread=0.04, layers=34)
    c.wash(ellipse(x, y - s * 0.08, s * 0.19, s * 0.15, 14), '#f6e6cc', col2, strength=0.45, layers=20)
    for side in (-1, 1):
        ear = petal(x + side * s * 0.3, y - s * 0.4, s * 0.46, s * 0.16, math.pi / 2 - side * 0.5)
        c.wash(ear, col, None, strength=0.8, spread=0.04, layers=24, edge=0.9)
    # fur strokes: a few darker small washes
    for _ in range(7):
        fx, fy = x + rnd.uniform(-0.35, 0.35) * s, y + rnd.uniform(0.2, 0.9) * s
        c.wash(leaf(fx, fy, s * 0.12, s * 0.025, rnd.uniform(1.2, 1.9)), col, None, strength=0.5, layers=8)
    # face
    c.wash(ellipse(x, y - s * 0.12, s * 0.06, s * 0.045, 10), '#2f2a2a', None, strength=1.4, layers=12)
    for ex in (-0.13, 0.13):
        c.wash(ellipse(x + s * ex, y - s * 0.28, s * 0.035, s * 0.04, 8), '#2f2a2a', None, strength=1.5, layers=10)
    c.wash(crescent(x, y - s * 0.02, s * 0.27, 0.55, math.pi - 0.55, s * 0.055), P['main'], None, strength=0.9, layers=16)
    if ink:
        c.ink_line([(x - s * 0.06, y - s * 0.02), (x, y + s * 0.02), (x + s * 0.06, y - s * 0.02)], width=max(2, s * 0.015),
                   closed=False, alpha=170, passes=1)


def lemon(c, x, y, s, P):
    c.wash(ellipse(x, y, s, s * 0.72, 16, 0.3), '#f2d34f', '#f7e79a', strength=0.75, layers=30)
    c.wash(leaf(x + s * 0.7, y - s * 0.55, s * 0.8, s * 0.25, -0.6), P['leaf'], P.get('leaf2'), strength=0.7, layers=22)


def berry_shape(x, y, s, n=22):
    """Rounded strawberry outline: full width at the shoulders, soft point below."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        px, py = math.sin(a), -math.cos(a)            # py -1 top .. 1 bottom
        k = 0.45 + 0.55 * (1 - (py + 1) / 2) ** 0.8    # narrower toward the bottom
        pts.append((x + s * 0.72 * px * k, y + s * 0.2 + s * 0.8 * py))
    return pts


def strawberry(c, x, y, s, P):
    rnd = c.rnd
    body = berry_shape(x, y, s)
    c.wash(body, '#e04a55', '#f28a7c', strength=1.0, spread=0.03, layers=34)
    c.wash(berry_shape(x - s * 0.12, y + s * 0.05, s * 0.75), '#b8303f', None, strength=0.45, spread=0.03, layers=20, edge=0.9)
    for _ in range(11):
        sx = x + rnd.uniform(-0.42, 0.42) * s * (1 - rnd.random() * 0.3)
        sy = y + rnd.uniform(-0.25, 0.7) * s
        c.wash(ellipse(sx, sy, s * 0.03, s * 0.045, 6, rnd.uniform(-0.4, 0.4)), '#7a2230', None, strength=1.1, layers=6, spread=0.05)
    for i in range(6):
        a = -math.pi / 2 + (i - 2.5) * 0.5
        c.wash(leaf(x, y - s * 0.55, s * 0.42, s * 0.13, a), P['leaf'], P.get('leaf2'), strength=0.95, layers=16)
    c.wash(rect(x - s * 0.03, y - s * 0.9, x + s * 0.03, y - s * 0.55, 2), '#6f8f55', None, strength=0.9, layers=10)


def sun(c, x, y, s, P):
    c.wash(ellipse(x, y, s * 0.55, s * 0.55, 16), '#f3b64a', '#f7d98a', strength=0.8, layers=30)
    for i in range(12):
        a = i * math.pi / 6
        c.wash(petal(x + s * 0.65 * math.cos(a), y + s * 0.65 * math.sin(a), s * 0.35, s * 0.1, a), '#f3b64a', None,
               strength=0.6, layers=14)


def succulent(c, x, y, s, P):
    pot = [(x - s * 0.5, y + s * 0.1), (x + s * 0.5, y + s * 0.1), (x + s * 0.38, y + s * 0.9), (x - s * 0.38, y + s * 0.9)]
    c.wash(pot, '#c9775a', '#e2a07f', strength=0.7, spread=0.02, layers=24)
    c.ink_line(pot, width=max(2, s * 0.02))
    for r, n, sh in ((0.7, 9, 0.45), (0.45, 7, 0.6), (0.25, 5, 0.75)):
        for i in range(n):
            a = -math.pi + i * math.pi / (n - 1)
            c.wash(petal(x, y + s * 0.05, s * r, s * r * 0.35, a), '#7fae8f', '#b7d6bf', strength=sh, layers=16)


def pumpkin(c, x, y, s, P):
    for dx, w in ((-0.45, 0.5), (0.45, 0.5), (0, 0.55)):
        c.wash(ellipse(x + s * dx, y, s * w, s * 0.7, 16), '#e07b39', '#f2a766', strength=0.7, layers=26)
    c.wash(rect(x - s * 0.06, y - s * 0.95, x + s * 0.08, y - s * 0.6), '#6b5a3a', None, strength=0.9, layers=12)
    for dx in (-0.45, 0.45):
        c.ink_line([(x + s * dx * 0.6 + s * dx * 0.5 * math.sin(math.pi * t / 8), y - s * 0.62 + s * 1.24 * t / 8) for t in range(9)],
                   width=max(1, s * 0.03), closed=False, alpha=110, passes=1, color=(150, 70, 30), jitter=0.001)


# ---------------------------------------------------------------- autumn & spooky-cute
def smooth(pts, rounds=2, closed=True):
    """Chaikin corner cutting: a polygon becomes a smooth curve."""
    for _ in range(rounds):
        out = []
        m = len(pts) if closed else len(pts) - 1
        for i in range(m):
            (x0, y0), (x1, y1) = pts[i][:2], pts[(i + 1) % len(pts)][:2]
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = out
    return pts


def ghost_shape(x, y, s, lean=0.0, n=40):
    """A little sheet ghost: round head, soft sides, scalloped hem."""
    pts = []
    top = y - s * 0.62
    # head: a tall dome from the left side over the top to the right side
    for i in range(n // 2 + 1):
        a = math.pi + math.pi * i / (n // 2)
        pts.append((x + s * 0.5 * math.cos(a), top + s * 0.55 + s * 0.55 * math.sin(a)))
    # right side down, flaring a little, then a scalloped hem back to the left
    hem = y + s * 0.62
    pts.append((x + s * 0.56, y + s * 0.2)); pts.append((x + s * 0.62, hem))
    k = 3
    for j in range(k * 6 + 1):
        t = j / (k * 6)
        hx = x + s * 0.62 - t * s * 1.24
        hy = hem - s * 0.1 * abs(math.sin(math.pi * t * k))
        pts.append((hx, hy))
    pts.append((x - s * 0.56, y + s * 0.2))
    return _rot(pts, x, y, lean)


def ghost(c, x, y, s, P, lean=0.0, book=False, color=None):
    """A cute watercolor ghost; with book=True it holds an open book."""
    raw = ghost_shape(x, y, s, lean)[::2]
    wob = s * 0.012
    shape = smooth([(px + c.rnd.gauss(0, wob), py + c.rnd.gauss(0, wob)) for px, py in raw], rounds=3)
    c.reserve(shape)
    shade = color or P.get('ghost', '#cfcadf')
    c.wash(shape, shade, '#f4f1f8', strength=0.3, spread=0.006, layers=26, edge=1.2, granulate=0.2, base_depth=1, layer_depth=2)
    c.ink_line(shape, width=max(2, s * 0.024), alpha=185, passes=1, jitter=0)
    ex = s * 0.17
    for sx in (-1, 1):
        ecx, ecy = _rot([(x + sx * ex, y - s * 0.3)], x, y, lean)[0]
        c.wash(ellipse(ecx, ecy, s * 0.055, s * 0.08, 10), '#2e2a33', None, strength=1.3, layers=14, spread=0.02, blur=1)
        bcx, bcy = _rot([(x + sx * s * 0.28, y - s * 0.16)], x, y, lean)[0]
        c.wash(ellipse(bcx, bcy, s * 0.08, s * 0.05, 10), '#e89aa5', None, strength=0.45, layers=12, spread=0.04)
    if book:
        bx, by = _rot([(x, y + s * 0.18)], x, y, lean)[0]
        col = P.get('object', '#9cc0cf')
        for side in (-1, 1):
            pg = [(bx, by + s * 0.05), (bx + side * s * 0.34, by - s * 0.05), (bx + side * s * 0.34, by + s * 0.2), (bx, by + s * 0.3)]
            c.wash(pg, col, P.get('object2'), strength=0.75, spread=0.01, layers=16, edge=0.8)
            inner = [(bx, by + s * 0.02), (bx + side * s * 0.3, by - s * 0.07), (bx + side * s * 0.3, by + s * 0.14), (bx, by + s * 0.24)]
            c.reserve(inner)
            c.ink_line(pg, width=max(2, s * 0.02), alpha=190, jitter=0.001, passes=1)


MAPLE = ((0, 1.0), (10, 0.78), (16, 0.84), (24, 0.62), (34, 0.42), (48, 0.74), (56, 0.7), (64, 0.92), (74, 0.66),
         (84, 0.62), (96, 0.36), (112, 0.52), (122, 0.6), (132, 0.4), (150, 0.26), (172, 0.12))


def maple_outline(x, y, s, angle=0.0):
    """A sugar-maple leaf: five pointed lobes with small teeth, stem at the bottom."""
    half = [(d, r) for d, r in MAPLE]
    pts = [(d, r) for d, r in half] + [(360 - d, r) for d, r in reversed(half[1:])]
    out = []
    for d, r in pts:
        a = math.radians(d) - math.pi / 2 + angle
        out.append((x + s * r * math.cos(a), y + s * r * math.sin(a)))
    return out


def maple_leaf(c, x, y, s, P, angle=0.0, color=None, color2=None):
    col = color or P['main']; col2 = color2 or P.get('main2', col)
    shape = maple_outline(x, y, s, angle)
    c.wash(shape, col2, col, strength=0.6, spread=0.035, layers=30, edge=0.9)
    # second, darker glaze toward the middle (wet on dry)
    c.wash(maple_outline(x, y + s * 0.05, s * 0.55, angle + c.rnd.uniform(-0.2, 0.2)), col, None, strength=0.35,
           spread=0.05, layers=16, edge=0.6)
    for d in (0, 62, -62, 120, -120):
        a = math.radians(d) - math.pi / 2 + angle
        c.ink_line([(x, y), (x + s * 0.62 * math.cos(a), y + s * 0.62 * math.sin(a))], width=max(1, s * 0.016),
                   closed=False, alpha=85, passes=1, color=(120, 60, 40))
    a = angle + math.pi / 2
    c.ink_line([(x, y), (x + s * 0.42 * math.cos(a), y + s * 0.42 * math.sin(a))], width=max(2, s * 0.028),
               closed=False, alpha=170, passes=1, color=(110, 70, 45))


def acorn(c, x, y, s, P, angle=0.0):
    body = _rot(ellipse(x, y + s * 0.15, s * 0.36, s * 0.46, 16), x, y, angle)
    c.wash(body, '#c98f4f', '#e3b574', strength=0.65, spread=0.03, layers=22)
    cap = _rot([(x - s * 0.44, y - s * 0.12)] + [(x + s * 0.44 * math.cos(math.pi + math.pi * i / 10),
               y - s * 0.12 + s * 0.3 * math.sin(math.pi + math.pi * i / 10)) for i in range(11)] +
               [(x + s * 0.44, y - s * 0.12), (x, y + s * 0.02)], x, y, angle)
    c.wash(cap, '#7a5234', '#9b6c45', strength=0.85, spread=0.03, layers=20)
    c.ink_line(cap, width=max(2, s * 0.03), alpha=170)
    top = _rot([(x, y - s * 0.38), (x + s * 0.06, y - s * 0.52)], x, y, angle)
    c.ink_line(top, width=max(2, s * 0.05), closed=False, alpha=200, passes=1, color=(90, 60, 40))


def sparkle(c, x, y, s, P, color=None):
    col = color or P.get('accent', '#e5b85a')
    pts = []
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        r = s if i % 2 == 0 else s * 0.28
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    c.wash(pts, col, P.get('accent2'), strength=0.8, spread=0.015, layers=14, edge=0.6)


def moon(c, x, y, s, P, color=None):
    col = color or P.get('accent', '#e5b85a')
    c.wash(crescent(x, y, s, -math.pi * 0.95, math.pi * 0.35, s * 0.62, n=16), col, P.get('accent2'),
           strength=0.7, spread=0.03, layers=20)


def bat(c, x, y, s, P, color='#4a4152'):
    w = []
    for i in range(13):
        t = i / 12
        w.append((x + s * t, y - s * 0.35 * math.sin(math.pi * t) + s * 0.12 * abs(math.sin(math.pi * t * 3)) * t))
    wing = [(x, y)] + w + [(x + s * 0.2, y + s * 0.15)]
    for side in (1, -1):
        c.wash([(x + (px - x) * side, py) for px, py in wing], color, None, strength=0.8, spread=0.02, layers=16)
    c.wash(ellipse(x, y, s * 0.16, s * 0.22, 12), color, None, strength=0.9, layers=16)


def book_single(c, x, y, s, P, angle=0.0, color=None):
    col = color or P.get('object', '#9cc0cf')
    box = _rot(rect(x - s * 0.22, y - s * 0.6, x + s * 0.22, y + s * 0.6), x, y, angle)
    c.wash(box, col, P.get('object2'), strength=0.65, spread=0.012, layers=18)
    c.ink_line(box, width=max(2, s * 0.03), alpha=190)
    for dy in (-0.4, 0.4):
        band = _rot([(x - s * 0.18, y + s * dy), (x + s * 0.18, y + s * dy)], x, y, angle)
        c.ink_line(band, width=max(1, s * 0.03), closed=False, alpha=150, passes=1, color=(150, 110, 60))


MOTIFS = {'rose': rose, 'daisy': daisy, 'wildflower': wildflower, 'tulip': tulip, 'sprig': sprig, 'eucalyptus': eucalyptus,
          'berries': berries, 'bouquet': bouquet, 'mug': mug, 'books': books, 'heart': heart, 'paw': paw, 'dog': dog,
          'lemon': lemon, 'strawberry': strawberry, 'sun': sun, 'succulent': succulent, 'pumpkin': pumpkin,
          'ghost': ghost, 'maple_leaf': maple_leaf, 'acorn': acorn, 'sparkle': sparkle, 'moon': moon, 'bat': bat,
          'book_single': book_single}
