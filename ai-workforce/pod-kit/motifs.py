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


# ---------------------------------------------------------------- kitchen & soup
def bowl_body(x, y0, s, rim_h, depth=0.72, n=24):
    """Outside of a round bowl: from the front lip of the rim ellipse (centre
    y0, half-height rim_h) down around the belly."""
    lip = [(x + s * math.cos(math.pi * i / n), y0 + rim_h * math.sin(math.pi * i / n)) for i in range(n + 1)]
    belly = [(x + s * math.cos(math.pi * i / n), y0 + s * depth * math.sin(math.pi * i / n)) for i in range(n, -1, -1)]
    return lip, belly


def soup_bowl(c, x, y, s, P, color=None, color2=None, broth='#e3a54c', broth2='#f3d18d', steam=True):
    """A steaming bowl of vegetable soup seen a little from above; s = half the bowl width."""
    rnd = c.rnd
    col = color or P.get('object', '#8fb0b8'); col2 = color2 or P.get('object2', '#c8dade')
    y0 = y - s * 0.18
    rim_h = s * 0.27
    lip, belly = bowl_body(x, y0, s, rim_h)
    # the bowl: light first wash, then a darker glaze on the shadow side (wet on dry)
    c.wash(lip + belly, col2, col, strength=0.65, spread=0.01, layers=30, edge=0.8)
    n = 24
    shade = [(x + s * math.cos(math.pi * i / n), y0 + rim_h * math.sin(math.pi * i / n)) for i in range(0, 4)]
    shade += [(x + s * 0.6 * math.cos(math.pi * i / n), y0 + s * 0.62 * math.sin(math.pi * i / n)) for i in range(3, 13)]
    shade += [(x + s * 0.99 * math.cos(math.pi * i / n), y0 + s * 0.71 * math.sin(math.pi * i / n)) for i in range(12, -1, -1)]
    c.wash(smooth(shade, rounds=2), col, None, strength=0.35, spread=0.03, layers=18, edge=0.35)
    # a painted band just under the lip, following the bowl's curve
    band = [(x + s * 0.99 * math.cos(math.pi * i / 20), y0 + rim_h * math.sin(math.pi * i / 20) + s * 0.1) for i in range(21)]
    band += [(x + s * 0.95 * math.cos(math.pi * i / 20), y0 + rim_h * math.sin(math.pi * i / 20) + s * 0.19) for i in range(20, -1, -1)]
    c.wash(band, P.get('main', '#c8643b'), None, strength=0.55, spread=0.01, layers=14, edge=0.6)
    # foot ring
    fy = y0 + s * 0.66
    foot = [(x - s * 0.3, fy), (x + s * 0.3, fy), (x + s * 0.36, fy + s * 0.13), (x - s * 0.36, fy + s * 0.13)]
    c.wash(foot, col, col2, strength=0.55, spread=0.01, layers=14)
    # inside wall at the back, then the broth
    c.wash(ellipse(x, y0, s, rim_h, 28), col2, None, strength=0.25, spread=0.008, layers=16, edge=0.5)
    c.wash(ellipse(x, y0 + s * 0.035, s * 0.86, rim_h * 0.78, 28), broth, broth2, strength=0.85, spread=0.012, layers=26, edge=1.0)
    # what's in it: carrot coins, herbs, a few noodles
    def spot(r_max):
        a = rnd.uniform(0, 2 * math.pi); r = math.sqrt(rnd.random()) * r_max
        return x + s * 0.8 * r * math.cos(a), y0 + s * 0.035 + rim_h * 0.7 * r * math.sin(a)
    for _ in range(9):
        cx, cy = spot(0.8)
        c.wash(ellipse(cx, cy, s * 0.07, s * 0.042, 10), '#f07a2a', '#f7a55a', strength=0.8, layers=12, spread=0.03, edge=1.1)
    for _ in range(4):
        cx, cy = spot(0.7)
        c.wash(ellipse(cx, cy, s * 0.06, s * 0.035, 10), '#f4ead6', None, strength=0.3, layers=10, spread=0.04, edge=1.2)
    for _ in range(10):
        cx, cy = spot(0.85)
        c.wash(leaf(cx, cy, s * 0.07, s * 0.025, rnd.uniform(0, 6.28)), '#5f8f45', None, strength=1.0, layers=8, spread=0.04)
    for _ in range(4):
        cx, cy = spot(0.6)
        c.ink_line([(cx + s * 0.03 * k, cy + s * 0.012 * math.sin(k * 1.7)) for k in range(7)], width=max(2, s * 0.016),
                   closed=False, alpha=170, passes=1, color=(244, 222, 170), jitter=0)
    # ink: rim, belly, foot
    w = max(2, s * 0.02)
    c.ink_line(smooth(ellipse(x, y0, s, rim_h, 24), rounds=2), width=w, alpha=200, passes=1, jitter=0)
    c.ink_line(belly, width=w, closed=False, alpha=200, passes=1, jitter=0)
    c.ink_line(foot[1:] + foot[:1], width=w * 0.9, closed=False, alpha=190, passes=1, jitter=0)
    if steam:
        for k, (dx, ln) in enumerate(((-0.33, 8), (0.02, 10), (0.36, 7))):
            ph = rnd.uniform(0, 6.28)
            pts = [(x + s * dx + s * 0.06 * math.sin(t * 0.8 + ph) * (0.5 + t / ln), y0 - rim_h * 0.95 - s * 0.07 * t)
                   for t in range(ln)]
            body = smooth([(px - s * 0.06, py) for px, py in pts] + [(px + s * 0.06, py) for px, py in pts[::-1]], rounds=2)
            c.wash(body, '#d6cdc4', None, strength=0.22, layers=12, spread=0.05, edge=0.3)
            c.ink_line(smooth(pts, rounds=2, closed=False), width=max(2, s * 0.013), closed=False, alpha=115, passes=1, jitter=0)


def carrot(c, x, y, s, P, angle=0.0, greens=True):
    """A whole carrot lying along `angle` (the thick end at (x, y)); s = its length."""
    n = 14
    top = [(s * t, s * 0.13 * (1 - t) ** 0.8 + s * 0.012) for t in [i / n for i in range(n + 1)]]
    pts = top + [(px, -py) for px, py in reversed(top[:-1])]
    root = [(x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)) for px, py in pts]
    c.wash(root, '#f39a4a', '#e0612a', strength=0.85, spread=0.02, layers=26, edge=0.9)
    ca, sa = math.cos(angle), math.sin(angle)
    for t in (0.18, 0.33, 0.47, 0.6, 0.72, 0.83):
        hw = s * 0.13 * (1 - t) ** 0.8 * 0.7
        px, py = x + s * t * ca, y + s * t * sa
        side = 1 if int(t * 100) % 2 else -1
        c.ink_line([(px - sa * hw * side, py + ca * hw * side), (px - sa * hw * 0.2 * side + ca * s * 0.02, py + ca * hw * 0.2 * side + sa * s * 0.02)],
                   width=max(1, s * 0.01), closed=False, alpha=140, passes=1, color=(150, 70, 30), jitter=0)
    c.ink_line(smooth(root, rounds=1), width=max(2, s * 0.013), alpha=170, passes=1, jitter=0, color=(120, 60, 35))
    if greens:
        for d in (-0.55, -0.2, 0.15, 0.5):
            a = angle + math.pi + d
            sx, sy = x - ca * s * 0.01, y - sa * s * 0.01
            c.wash(leaf(sx, sy, s * 0.42, s * 0.018, a), '#5f8f45', None, strength=0.9, layers=8, spread=0.02)
            for k in range(3):
                t = 0.4 + 0.2 * k
                lx, ly = sx + s * 0.42 * t * math.cos(a), sy + s * 0.42 * t * math.sin(a)
                for side in (-1, 1):
                    c.wash(leaf(lx, ly, s * 0.1, s * 0.035, a + side * 0.7), '#6f9e4f', '#9cc471', strength=0.7, layers=10, spread=0.05)


def garlic(c, x, y, s, P):
    """A garlic bulb: round shoulders, violet streaks, a papery neck and a root tuft."""
    by = y + s * 0.1
    bulb = []
    for i in range(32):
        a = 2 * math.pi * i / 32
        px, py = math.cos(a), math.sin(a)
        ry = 0.5 if py < 0 else 0.42              # a little flatter underneath
        pinch = 1 - 0.28 * max(0, -py) ** 6       # shoulders draw in toward the neck
        bulb.append((x + s * 0.62 * px * pinch, by + s * ry * py))
    bulb = smooth(bulb, rounds=1)
    neck = [(x - s * 0.13, by - s * 0.42), (x - s * 0.04, by - s * 0.82), (x + s * 0.04, by - s * 0.82), (x + s * 0.13, by - s * 0.42)]
    c.wash(neck, '#d8c7a6', '#efe4cf', strength=0.7, layers=14, spread=0.02, edge=0.8)
    c.wash(bulb, '#e9dcc8', '#f6efe4', strength=0.7, spread=0.015, layers=24, edge=1.0)
    for dx in (-0.38, -0.13, 0.13, 0.38):
        stripe = leaf(x + s * dx * 0.45, by + s * 0.4, s * 0.8, s * 0.045, -math.pi / 2 + dx * 0.75)
        c.wash(stripe, '#c4a0c0', None, strength=0.3, layers=10, spread=0.05, edge=0.3)
    w = max(2, s * 0.022)
    c.ink_line(bulb, width=w, alpha=180, passes=1, jitter=0, color=(90, 70, 70))
    c.ink_line(neck, width=w * 0.8, closed=False, alpha=150, passes=1, jitter=0, color=(110, 90, 70))
    for dx in (-0.46, -0.18, 0.18, 0.46):
        c.ink_line([(x + s * dx * math.sin(math.pi * t) ** 0.8, by - s * 0.42 + s * 0.86 * t) for t in [k / 12 for k in range(13)]],
                   width=w * 0.6, closed=False, alpha=110, passes=1, jitter=0, color=(120, 90, 110))
    for k in range(7):
        a = math.pi / 2 + (k - 3) * 0.22
        rx = x + s * 0.05 * (k - 3)
        c.ink_line([(rx, by + s * 0.42), (rx + s * 0.14 * math.cos(a), by + s * 0.42 + s * 0.14 * math.sin(a))],
                   width=w * 0.5, closed=False, alpha=130, passes=1, jitter=0, color=(120, 100, 80))


def mushroom(c, x, y, s, P, angle=0.0, color=None):
    """A little brown cap mushroom with gills and a pale stem."""
    col = color or '#a8643e'
    cap = [(x + s * 0.62 * math.cos(math.pi + math.pi * i / 16), y - s * 0.12 + s * 0.52 * math.sin(math.pi + math.pi * i / 16)) for i in range(17)]
    cap += [(x + s * 0.5, y - s * 0.02), (x, y + s * 0.04), (x - s * 0.5, y - s * 0.02)]
    cap = _rot(cap, x, y, angle)
    stem = _rot([(x - s * 0.15, y), (x + s * 0.15, y), (x + s * 0.19, y + s * 0.62), (x - s * 0.19, y + s * 0.62)], x, y, angle)
    c.wash(stem, '#efe3cf', '#d9c6a6', strength=0.75, spread=0.015, layers=20, edge=0.9)
    c.wash(_rot(ellipse(x, y - s * 0.03, s * 0.5, s * 0.07, 14), x, y, angle), '#dcc4a2', None, strength=0.6, layers=12)
    c.wash(cap, '#d49a68', col, strength=0.85, spread=0.02, layers=28, edge=1.0)
    c.wash(_rot(ellipse(x - s * 0.18, y - s * 0.38, s * 0.14, s * 0.07, 10), x, y, angle), '#f0d6b4', None, strength=0.35, layers=10)
    w = max(2, s * 0.025)
    c.ink_line(smooth(cap, rounds=1), width=w, alpha=185, passes=1, jitter=0, color=(80, 50, 40))
    c.ink_line(stem[1:3] + stem[3:4], width=w * 0.8, closed=False, alpha=160, passes=1, jitter=0, color=(90, 70, 55))
    c.ink_line([stem[0], stem[3]], width=w * 0.8, closed=False, alpha=160, passes=1, jitter=0, color=(90, 70, 55))


def bay_leaf(c, x, y, s, P, angle=0.0):
    c.wash(leaf(x, y, s, s * 0.22, angle), '#7f9a5a', '#b3c48a', strength=0.65, spread=0.03, layers=20, edge=0.8)
    c.ink_line([(x, y), (x + s * 0.95 * math.cos(angle), y + s * 0.95 * math.sin(angle))], width=max(1, s * 0.012),
               closed=False, alpha=110, passes=1, jitter=0, color=(80, 90, 50))


def peppercorns(c, x, y, s, P, n=5):
    berries(c, x, y, s, P, n=n, color='#5b463a')



# ---------------------------------------------------------------- winter birds & greenery
def gouache(c, shape, color=(252, 251, 248), alpha=235, soft=0.012):
    """Opaque white body color on top of the washes (snow), the way a watercolorist
    finishes with white gouache: painted into the ink layer, edges softened a touch."""
    from watercolor import deform
    from PIL import Image, ImageDraw, ImageFilter
    pts = deform([(p[0], p[1]) for p in shape], 2, 0.03, rnd=c.rnd)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    size = max(max(xs) - min(xs), max(ys) - min(ys), 1)
    pad = int(size * 0.1) + 4
    x0 = max(0, int(min(xs)) - pad); y0 = max(0, int(min(ys)) - pad)
    x1 = min(c.w, int(max(xs)) + pad); y1 = min(c.h, int(max(ys)) + pad)
    if x1 <= x0 or y1 <= y0:
        return
    m = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(px - x0, py - y0) for px, py, *_ in pts], fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(max(0.8, size * soft)))
    layer = Image.new('RGBA', m.size, tuple(color) + (0,))
    layer.putalpha(m)
    c.composite_around(layer, (x0, y0))


def _pine_path(x, y, s, angle, bend, n=13):
    """Points along a gently curved bough, base to tip."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        px = -s + 2 * s * t
        py = bend * s * (t - 0.5) ** 2 * 1.6 - bend * s * 0.1
        pts.append((x + px, y + py))
    return _rot(pts, x, y, angle)


def _needles(c, path, L0, L1, P, clear=None, dense=3):
    """Tapered needle strokes angled forward along a twig, both sides.
    clear = (x0, x1, y): skip needles pointing up from under something perched there."""
    rnd = c.rnd
    g1, g2, g3 = P.get('leaf', '#4f7a5a'), P.get('leaf2', '#8fb39a'), P.get('leaf_dark', '#2f5443')
    n = len(path)
    for i in range(1, n):
        t = i / (n - 1)
        px, py = path[i]
        a0 = math.atan2(path[i][1] - path[i - 1][1], path[i][0] - path[i - 1][0])
        L = L0 * (1 - t) + L1 * t
        for side in (-1, 1):
            for k in range(dense):
                a = a0 + side * rnd.uniform(0.5, 1.05) - 0.1 * k * side
                if clear and clear[0] < px < clear[1] and math.sin(a) < -0.25:
                    continue
                col = rnd.choice((g1, g1, g3, g2))
                c.wash(leaf(px, py, L * rnd.uniform(0.75, 1.1), L * 0.085, a), col, None,
                       strength=rnd.uniform(0.55, 0.85), spread=0.03, layers=7, edge=0.7, granulate=0.2)
    c.ink_line(path, width=max(2, L0 * 0.09), closed=False, alpha=190, passes=1, jitter=0, color=(95, 65, 45))


def pine_bough(c, x, y, s, P, angle=0.0, bend=0.35, snow=True, cones=0, clear=None, twigs=3):
    """A fir bough: a pale first wash, a main stem with forward-angled side
    twigs, needle strokes in three greens, and clumps of snow (a blue-grey
    shadow wash under white gouache) resting on top."""
    rnd = c.rnd
    path = _pine_path(x, y, s, angle, bend)
    n = len(path)
    # 1. soft first wash under the whole bough
    top, bot = [], []
    for i, (px, py) in enumerate(path):
        t = i / (n - 1)
        wdt = s * 0.24 * math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.7
        j = min(i + 1, n - 1); k = max(i - 1, 0)
        dx, dy = path[j][0] - path[k][0], path[j][1] - path[k][1]
        L = math.hypot(dx, dy) or 1
        top.append((px - dy / L * wdt, py + dx / L * wdt)); bot.append((px + dy / L * wdt, py - dx / L * wdt))
    c.wash(top + bot[::-1], P.get('leaf2', '#8fb39a'), None, strength=0.18, spread=0.1, layers=14, edge=0.35)
    # 2. side twigs first (they sit behind the main stem), then the main stem
    tw = []
    for k in range(twigs):
        t = 0.2 + 0.55 * k / max(1, twigs - 1) + rnd.uniform(-0.05, 0.05)
        i = int(t * (n - 1))
        px, py = path[i]
        a0 = math.atan2(path[i + 1][1] - py, path[i + 1][0] - px)
        side = 1 if k % 2 == 0 else -1
        a = a0 + side * rnd.uniform(0.45, 0.7)
        ln = s * (0.75 - 0.45 * t)
        twig = [(px + ln * u * math.cos(a + side * 0.15 * u), py + ln * u * math.sin(a + side * 0.15 * u)) for u in
                (0, 0.25, 0.5, 0.75, 1.0)]
        tw.append(twig)
        _needles(c, twig, s * 0.24, s * 0.12, P, clear=clear, dense=3)
    _needles(c, path, s * 0.34, s * 0.14, P, clear=clear, dense=4)
    if cones:
        for k in range(cones):
            px, py = path[int((n - 1) * (0.4 + 0.2 * k))]
            pinecone(c, px, py + s * 0.3, s * 0.2, P, angle=angle + rnd.uniform(-0.25, 0.25))
    # 3. snow clumps resting on top of the stem and twigs
    if snow:
        spots = [path[i] for i in range(2, n - 2, 3)] + [t[2] for t in tw]
        for px, py in spots:
            if rnd.random() < 0.25 or (clear and clear[0] - s * 0.15 < px < clear[1] + s * 0.1):
                continue
            w, h = s * rnd.uniform(0.13, 0.2), s * rnd.uniform(0.05, 0.075)
            cx, cy = px + rnd.uniform(-0.04, 0.04) * s, py - h * 0.35
            blob = smooth([(cx - w, cy + h * 0.5), (cx - w * 0.6, cy - h * 0.6), (cx - w * 0.1, cy - h),
                           (cx + w * 0.5, cy - h * 0.8), (cx + w, cy + h * 0.4), (cx + w * 0.3, cy + h * 0.9),
                           (cx - w * 0.4, cy + h * 0.8)], rounds=2)
            blob = _rot(blob, cx, cy, angle * 0.6)
            c.wash([(bx, by + h * 0.45) for bx, by in blob], P.get('shadow', '#a9bccb'), None, strength=0.4,
                   spread=0.04, layers=8, edge=0.9)
            gouache(c, blob, alpha=236, soft=0.03)


def pinecone(c, x, y, s, P, angle=0.0):
    body = _rot(ellipse(x, y, s * 0.42, s * 0.72, 18), x, y, angle)
    c.wash(body, '#b4835a', '#d7ae7d', strength=0.6, spread=0.03, layers=20, edge=0.9)
    rnd = c.rnd
    rows = 6
    for r in range(rows):
        yy = y - s * 0.55 + r * s * 1.1 / (rows - 1)
        half = s * 0.4 * math.sin(math.pi * (0.15 + 0.7 * r / (rows - 1)))
        k = 3 if r % 2 == 0 else 2
        for j in range(k):
            xx = x - half + (j + 0.5) * 2 * half / k
            sc = _rot([(xx - s * 0.16, yy - s * 0.02), (xx, yy + s * 0.14), (xx + s * 0.16, yy - s * 0.02),
                       (xx, yy + s * 0.04)], x, y, angle)
            c.wash(sc, '#6f4a2f', None, strength=0.6 * rnd.uniform(0.8, 1.1), spread=0.03, layers=8, edge=0.9)
    c.ink_line(body, width=max(1, s * 0.03), alpha=120, passes=1, jitter=0, color=(90, 60, 40))
    st = _rot([(x, y - s * 0.72), (x + s * 0.04, y - s * 0.9)], x, y, angle)
    c.ink_line(st, width=max(2, s * 0.06), closed=False, alpha=190, passes=1, jitter=0, color=(90, 60, 40))


def holly_leaf(x, y, s, angle, n=5):
    """A spiky holly leaf pointing along `angle`, base at (x, y)."""
    top, bot = [], []
    for i in range(n * 2 + 1):
        t = i / (n * 2)
        w = s * 0.34 * math.sin(math.pi * t) ** 0.8
        spike = 1.0 if i % 2 == 1 else 0.62
        top.append((s * t, -w * spike)); bot.append((s * t, w * spike))
    pts = top + bot[::-1][1:-1]
    ca, sa = math.cos(angle), math.sin(angle)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def holly(c, x, y, s, P, angle=0.0):
    for da in (-0.9, 0.25, 2.3):
        a = angle + da + c.rnd.uniform(-0.15, 0.15)
        shp = holly_leaf(x, y, s * 0.95, a)
        c.wash(shp, P.get('holly', '#2f6b4f'), P.get('holly2', '#6fa27e'), strength=0.7, spread=0.02, layers=18, edge=1.0)
        c.ink_line([(x, y), (x + s * 0.85 * math.cos(a), y + s * 0.85 * math.sin(a))], width=max(1, s * 0.02),
                   closed=False, alpha=110, passes=1, jitter=0, color=(30, 60, 45))
        c.ink_line(shp, width=max(1, s * 0.02), alpha=120, passes=1, jitter=0, color=(30, 60, 45))
    for k in range(3):
        a = angle + 1.2 + k * 0.9
        bx, by = x + s * 0.13 * math.cos(a), y + s * 0.13 * math.sin(a)
        c.wash(ellipse(bx, by, s * 0.13, s * 0.13, 12), P.get('berry', '#c1272d'), '#e2574c', strength=0.85,
               spread=0.03, layers=16, edge=1.0)
        c.ink_line(ellipse(bx, by, s * 0.13, s * 0.13, 12), width=max(1, s * 0.018), alpha=110, passes=1, jitter=0,
                   color=(90, 20, 25))


# cardinal outline, facing right, in units of s (center of the motif at 0, 0)
CARDINAL = ((0.82, -0.2), (0.64, -0.36), (0.55, -0.47), (0.44, -0.55), (0.36, -0.62), (0.18, -0.95), (0.22, -0.72),
            (0.12, -0.72), (0.02, -0.58), (0.0, -0.44), (-0.16, -0.32), (-0.4, -0.14), (-0.56, 0.06),
            (-0.8, 0.36), (-1.0, 0.62), (-0.93, 0.7), (-0.74, 0.62), (-0.46, 0.4), (-0.16, 0.5), (0.14, 0.46),
            (0.4, 0.3), (0.56, 0.08), (0.64, -0.08))
CARD_WING = ((0.28, -0.14), (0.06, -0.24), (-0.22, -0.18), (-0.5, 0.06), (-0.78, 0.46), (-0.5, 0.36),
             (-0.18, 0.3), (0.1, 0.18), (0.26, 0.04))
CARD_MASK = ((0.68, -0.33), (0.56, -0.38), (0.45, -0.35), (0.42, -0.25), (0.47, -0.13), (0.56, -0.02), (0.64, -0.04),
             (0.68, -0.16))
CARD_BEAK = ((0.6, -0.36), (0.92, -0.22), (0.6, -0.07), (0.55, -0.22))


def cardinal(c, x, y, s, P, facing=1, female=False, perch=True, angle=0.0, snow=False):
    """A plump watercolor cardinal perched on a snowy pine sprig. facing 1 = right."""
    u = s * 0.62
    by = y - s * 0.09
    def pts(seq, dy=0.0):
        return _rot([(x + facing * px * u, by + (py + dy) * u) for px, py in seq], x, y, angle)
    if perch:
        pine_bough(c, x - facing * s * 0.1, y + s * 0.3, s * 0.8, P, angle=angle + facing * 0.1 + c.rnd.uniform(-0.08, 0.08),
                   bend=0.25, snow=snow, clear=(x - 0.62 * s, x + 0.55 * s), twigs=2)
    body = smooth(pts(CARDINAL), rounds=2)
    if female:
        c.wash(body, '#b99474', '#d9bb9a', strength=0.6, spread=0.02, layers=28, edge=1.0, granulate=0.3)
        c.wash(smooth(pts(CARD_WING), rounds=2), '#b5503f', '#8f6a50', strength=0.5, spread=0.03, layers=18, edge=0.8)
        crest = pts(((0.36, -0.62), (0.18, -0.95), (0.22, -0.72), (0.12, -0.72), (0.2, -0.56)))
        c.wash(crest, '#c0523f', None, strength=0.45, spread=0.03, layers=12)
        tail = pts(((-0.56, 0.06), (-0.8, 0.36), (-1.0, 0.62), (-0.93, 0.7), (-0.74, 0.62), (-0.5, 0.3)))
        c.wash(tail, '#b5503f', None, strength=0.45, spread=0.03, layers=12)
    else:
        red, red2, dark = P.get('bird', '#c62b33'), P.get('bird2', '#e8604e'), P.get('bird_dark', '#8e1f2b')
        c.wash(body, red2, red, strength=0.7, spread=0.02, layers=30, edge=1.1, granulate=0.3)
        # rounder breast glow, then the darker wing and tail glazed wet on dry
        c.wash(ellipse(x + facing * 0.28 * u, by + 0.08 * u, 0.2 * u, 0.16 * u, 12), red2, None, strength=0.22, layers=12)
        c.wash(smooth(pts(CARD_WING), rounds=2), dark, red, strength=0.55, spread=0.03, layers=18, edge=0.9)
        tail = pts(((-0.56, 0.06), (-0.8, 0.36), (-1.0, 0.62), (-0.93, 0.7), (-0.74, 0.62), (-0.5, 0.3)))
        c.wash(tail, dark, None, strength=0.45, spread=0.03, layers=12)
    c.wash(smooth(pts(CARD_MASK), rounds=1), '#3a2a2c' if not female else '#6b5a52', None,
           strength=1.0 if not female else 0.6, spread=0.02, layers=16, edge=0.6)
    c.wash(pts(CARD_BEAK), '#ee8a3a', '#f6b35c', strength=0.85, spread=0.01, layers=14, edge=0.8)
    # eye with a catch light
    ex, ey = pts(((0.46, -0.3),))[0]
    c.wash(ellipse(ex, ey, u * 0.045, u * 0.05, 10), '#141012', None, strength=1.4, spread=0.01, layers=10, blur=1)
    gouache(c, ellipse(ex + facing * u * 0.012, ey - u * 0.016, u * 0.014, u * 0.014, 8), alpha=240, soft=0.1)
    # feather marks on the wing, loose outline, feet
    ink = (70, 30, 32) if not female else (80, 60, 50)
    for k in range(3):
        a0 = (0.1 - k * 0.18, -0.06 + k * 0.1); a1 = (-0.3 - k * 0.16, 0.2 + k * 0.1)
        c.ink_line(pts((a0, a1)), width=max(1, s * 0.012), closed=False, alpha=110, passes=1, jitter=0, color=ink)
    c.ink_line(body, width=max(2, s * 0.018), alpha=150, passes=1, jitter=0, color=ink)
    for fx in (-0.08, 0.1):
        c.ink_line(pts(((fx, 0.46), (fx + 0.04, 0.68))), width=max(2, s * 0.02), closed=False, alpha=170, passes=1,
                   jitter=0, color=(90, 60, 50))


def snowflake(c, x, y, s, P, angle=0.0):
    col = P.get('snow', '#8fb0c8')
    c.wash(ellipse(x, y, s * 0.3, s * 0.3, 10), col, None, strength=0.5, spread=0.05, layers=10)
    rgb = tuple(int(col.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    for k in range(6):
        a = angle + k * math.pi / 3
        ex, ey = x + s * math.cos(a), y + s * math.sin(a)
        c.ink_line([(x, y), (ex, ey)], width=max(1, s * 0.06), closed=False, alpha=140, passes=1, jitter=0, color=rgb)
        for f in (0.55,):
            mx, my = x + s * f * math.cos(a), y + s * f * math.sin(a)
            for side in (-1, 1):
                b = a + side * 0.7
                c.ink_line([(mx, my), (mx + s * 0.3 * math.cos(b), my + s * 0.3 * math.sin(b))], width=max(1, s * 0.05),
                           closed=False, alpha=120, passes=1, jitter=0, color=rgb)


def snow_dot(c, x, y, s, P):
    s *= c.rnd.uniform(0.55, 1.15)
    c.wash(ellipse(x, y, s, s, 10), P.get('snow', '#8fb0c8'), None, strength=c.rnd.uniform(0.3, 0.55), spread=0.08,
           layers=8, edge=0.9)


# ---------------------------------------------------------------- hot cocoa
def _rrect(x, y, w, h, r, angle=0.0, n=5):
    """A rounded rectangle centred at (x, y), rotated by angle."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -math.pi / 2), (w / 2 - r, h / 2 - r, 0.0),
                       (-w / 2 + r, h / 2 - r, math.pi / 2), (-w / 2 + r, -h / 2 + r, math.pi)):
        for i in range(n + 1):
            a = a0 + math.pi / 2 * i / n
            pts.append((x + cx + r * math.cos(a), y + cy + r * math.sin(a)))
    return _rot(pts, x, y, angle)


def marshmallow(c, x, y, s, P, angle=0.0, tint=None, ink=True):
    """A soft marshmallow in white gouache (opaque, so it sits on the cocoa),
    a warm shadow on the lower side and a light pen line. s = its width."""
    body = _rrect(x, y, s, s * 0.82, s * 0.28, angle)
    base = tint or (252, 250, 245)
    gouache(c, body, color=base, alpha=246, soft=0.02)
    ca, sa = math.cos(angle), math.sin(angle)
    shade = _rrect(x + s * 0.1 * ca - s * 0.14 * sa, y + s * 0.1 * sa + s * 0.14 * ca, s * 0.72, s * 0.36, s * 0.16, angle)
    shadow = tuple(max(0, v - 22) for v in base[:1]) + tuple(max(0, v - 30) for v in base[1:2]) + tuple(max(0, v - 40) for v in base[2:3])
    gouache(c, shade, color=shadow, alpha=120, soft=0.08)
    if ink:
        c.ink_line(smooth(body, rounds=1), width=max(1, s * 0.03), alpha=120, passes=1, jitter=0, color=(150, 110, 90))


def cinnamon_stick(c, x, y, s, P, angle=0.0, n=1):
    """Rolled cinnamon bark, (x, y) is the middle, s = its length; n = 1-3 sticks side by side."""
    ca, sa = math.cos(angle), math.sin(angle)
    for k in range(n):
        off = (k - (n - 1) / 2) * s * 0.12
        ox, oy = x - sa * off, y + ca * off
        L = s * (1 - 0.08 * k)
        wd = s * 0.055
        body = _rot([(ox - L / 2, oy - wd), (ox + L / 2, oy - wd), (ox + L / 2, oy + wd), (ox - L / 2, oy + wd)], ox, oy, angle)
        c.wash(body, '#b8703d', '#8e4f28', strength=0.85, spread=0.012, layers=20, edge=1.0, granulate=0.5)
        # the curled edge of the bark runs down one side
        curl = _rot([(ox - L / 2, oy + wd * 0.1), (ox + L / 2, oy + wd * 0.1), (ox + L / 2, oy + wd * 0.55), (ox - L / 2, oy + wd * 0.55)], ox, oy, angle)
        c.wash(curl, '#6e3a1e', None, strength=0.45, spread=0.02, layers=10, edge=0.8)
        for end in (-1, 1):
            ex, ey = ox + end * L / 2 * ca, oy + end * L / 2 * sa
            spiral = [(ex + wd * 0.9 * (1 - t * 0.7) * math.cos(t * 9) * 0.35, ey + wd * 0.9 * (1 - t * 0.7) * math.sin(t * 9))
                      for t in [i / 16 for i in range(17)]]
            spiral = _rot(spiral, ex, ey, angle)
            c.ink_line(spiral, width=max(1, s * 0.008), closed=False, alpha=150, passes=1, jitter=0, color=(90, 45, 25))
        c.ink_line(body, width=max(1, s * 0.009), alpha=150, passes=1, jitter=0, color=(90, 45, 25))
        for t in (0.22, 0.47, 0.71):
            px, py = ox + (t - 0.5) * L * ca, oy + (t - 0.5) * L * sa
            c.ink_line([(px - sa * wd * 0.8, py + ca * wd * 0.8), (px + ca * s * 0.03 - sa * wd * 0.1, py + sa * s * 0.03 + ca * wd * 0.1)],
                       width=max(1, s * 0.006), closed=False, alpha=100, passes=1, jitter=0, color=(90, 45, 25))


def orange_slice(c, x, y, s, P, angle=0.0):
    """A dried orange wheel: rind ring, pale pith, juicy segments. s = radius."""
    c.wash(ellipse(x, y, s, s, 30), '#f7c98a', None, strength=0.35, spread=0.01, layers=16, edge=0.5)
    ring = [(x + s * math.cos(2 * math.pi * i / 36), y + s * math.sin(2 * math.pi * i / 36)) for i in range(37)]
    ring += [(x + s * 0.86 * math.cos(2 * math.pi * i / 36), y + s * 0.86 * math.sin(2 * math.pi * i / 36)) for i in range(36, -1, -1)]
    c.wash(ring, '#e8782a', '#f29a3c', strength=0.9, spread=0.006, layers=18, edge=0.9)
    for k in range(9):
        a0 = angle + 2 * math.pi * k / 9 + 0.06
        a1 = angle + 2 * math.pi * (k + 1) / 9 - 0.06
        seg = [(x + s * 0.08 * math.cos((a0 + a1) / 2), y + s * 0.08 * math.sin((a0 + a1) / 2))]
        seg += [(x + s * 0.76 * math.cos(a0 + (a1 - a0) * t), y + s * 0.76 * math.sin(a0 + (a1 - a0) * t)) for t in (0, 0.25, 0.5, 0.75, 1)]
        c.wash(smooth(seg, rounds=1), '#f5a13a', '#f8c060', strength=0.85, spread=0.02, layers=14, edge=1.2)
    c.ink_line(ellipse(x, y, s, s, 30), width=max(1, s * 0.03), alpha=140, passes=1, jitter=0, color=(150, 70, 25))


def star_anise(c, x, y, s, P, angle=0.0):
    """An eight-pointed star anise pod. s = radius."""
    for k in range(8):
        a = angle + 2 * math.pi * k / 8
        pod = petal(x, y, s, s * 0.34, a)
        c.wash(pod, '#8a5230', '#b0703f', strength=0.8, spread=0.02, layers=12, edge=1.1, granulate=0.5)
        sx, sy = x + s * 0.55 * math.cos(a), y + s * 0.55 * math.sin(a)
        c.wash(ellipse(sx, sy, s * 0.1, s * 0.07, 8, rot=a), '#e0b27a', None, strength=0.5, layers=8)
        c.ink_line(pod, width=max(1, s * 0.03), alpha=120, passes=1, jitter=0, color=(80, 45, 25))
    c.wash(ellipse(x, y, s * 0.16, s * 0.16, 10), '#5e3620', None, strength=0.8, layers=10)


def peppermint(c, x, y, s, P, angle=0.0):
    """A round peppermint candy: white with red swirl wedges. s = radius."""
    red, red2 = P.get('berry', '#c62b33'), '#e0525a'
    for k in range(6):
        a0 = angle + 2 * math.pi * k / 6
        wedge = [(x, y)]
        for t in [i / 8 for i in range(9)]:
            r = s * 0.95 * t ** 0.5
            wedge.append((x + r * math.cos(a0 + 0.9 * t), y + r * math.sin(a0 + 0.9 * t)))
        for t in [i / 8 for i in range(8, -1, -1)]:
            r = s * 0.95 * t ** 0.5
            wedge.append((x + r * math.cos(a0 + 0.9 * t + 0.42), y + r * math.sin(a0 + 0.9 * t + 0.42)))
        c.wash(wedge, red, red2, strength=0.85, spread=0.01, layers=14, edge=1.0)
    c.ink_line(ellipse(x, y, s, s, 24), width=max(1, s * 0.04), alpha=150, passes=1, jitter=0, color=(120, 40, 45))


def cocoa_mug(c, x, y, s, P, color=None, color2=None, marshmallows=5, stick=True, steam=True, flake=True):
    """A steaming mug of hot cocoa seen a little from above, marshmallows
    floating, a cinnamon stick leaning on the rim. s = half the mug's width."""
    rnd = c.rnd
    col = color or P.get('object', '#b7323a'); col2 = color2 or P.get('object2', '#d9575a')
    y0 = y - s * 0.62                      # rim centre
    rim_h = s * 0.26
    yb = y + s * 0.78                      # bottom
    n = 24
    # the body tapers a touch and has soft bottom corners
    right = [(x + s * (1 - 0.06 * t), y0 + (yb - y0) * t) for t in (0.2, 0.5, 0.8, 0.95)]
    left = [(2 * x - px, py) for px, py in right]
    bottom = [(x + s * 0.9 * math.cos(math.pi * i / 12), yb + s * 0.1 * math.sin(math.pi * i / 12)) for i in range(13)]
    # handle: a thick C on the right
    hx, hy = x + s * 0.93, y0 + (yb - y0) * 0.45
    outer = [(hx + s * 0.42 * math.cos(a), hy + s * 0.48 * math.sin(a)) for a in [(-1.35 + 2.7 * i / 16) for i in range(17)]]
    inner = [(hx + s * 0.22 * math.cos(a), hy + s * 0.28 * math.sin(a)) for a in [(-1.25 + 2.5 * i / 16) for i in range(16, -1, -1)]]
    c.wash(smooth(outer + inner, rounds=1), col, col2, strength=0.75, spread=0.01, layers=20, edge=1.0)
    # the mug: first wash, then a darker glaze down the shadow side, a pale highlight left on the left
    lip = [(x + s * math.cos(math.pi * i / n), y0 + rim_h * math.sin(math.pi * i / n)) for i in range(n + 1)]   # right to left
    body_poly = lip + left + bottom[::-1] + right[::-1]
    c.wash(body_poly, col2, col, strength=0.72, spread=0.008, layers=30, edge=0.9)
    shade = [(x + s * 0.25, y0 + rim_h * 0.95), (x + s * 0.96, y0 + rim_h * 0.2)] + right + [(x + s * 0.6, yb + s * 0.07), (x + s * 0.3, yb + s * 0.09)]
    c.wash(smooth(shade, rounds=2), col, None, strength=0.35, spread=0.03, layers=16, edge=0.4)
    # a white gouache snowflake painted on the front of the mug
    if flake:
        fx, fy, fr = x - s * 0.1, y0 + (yb - y0) * 0.55, s * 0.22
        for k in range(6):
            a = k * math.pi / 3 + 0.26
            ex, ey = fx + fr * math.cos(a), fy + fr * math.sin(a)
            c.ink_line([(fx, fy), (ex, ey)], width=max(2, s * 0.028), closed=False, alpha=230, passes=1, jitter=0, color=(250, 246, 238))
            mx, my = fx + fr * 0.58 * math.cos(a), fy + fr * 0.58 * math.sin(a)
            for side in (-1, 1):
                b = a + side * 0.75
                c.ink_line([(mx, my), (mx + fr * 0.3 * math.cos(b), my + fr * 0.3 * math.sin(b))], width=max(2, s * 0.022),
                           closed=False, alpha=230, passes=1, jitter=0, color=(250, 246, 238))
        for dx, dy, rr in ((-0.62, 0.12, 0.035), (0.42, 0.3, 0.03), (0.55, -0.05, 0.025), (-0.45, 0.58, 0.03), (0.2, 0.7, 0.028)):
            gouache(c, ellipse(x + s * dx, y0 + (yb - y0) * (0.1 + dy), s * rr, s * rr, 8), color=(250, 246, 238), alpha=225, soft=0.05)
    # inside wall at the back, then the cocoa
    c.wash(ellipse(x, y0, s, rim_h, 28), col2, None, strength=0.25, spread=0.006, layers=14, edge=0.5)
    cy0 = y0 + rim_h * 0.12
    c.wash(ellipse(x, cy0, s * 0.9, rim_h * 0.8, 28), '#7a4630', '#a8704c', strength=0.95, spread=0.01, layers=28, edge=1.2)
    c.wash(ellipse(x - s * 0.1, cy0 + rim_h * 0.1, s * 0.55, rim_h * 0.4, 20), '#c79a72', None, strength=0.3, spread=0.04, layers=12, edge=0.3)
    # cinnamon stick leaning out of the back left
    if stick:
        sx0, sy0 = x - s * 0.35, cy0 + rim_h * 0.05
        ang = -2.2
        L = s * 1.1
        cinnamon_stick(c, sx0 + math.cos(ang) * L * 0.5, sy0 + math.sin(ang) * L * 0.5, L, P, angle=ang)
    # ink: rim (the back half skips where the stick crosses it), body, handle
    w = max(2, s * 0.02)
    rim = smooth(ellipse(x, y0, s, rim_h, 32), rounds=1)
    if stick:
        # where the stick crosses the back of the rim
        t = (y0 - rim_h * 0.85 - sy0) / math.sin(ang)
        gx = sx0 + t * math.cos(ang)
        gap = (gx - s * 0.085, gx + s * 0.085)
        segs, cur = [], []
        for px, py in rim + rim[:1]:
            if py < y0 and gap[0] < px < gap[1]:
                if cur: segs.append(cur); cur = []
            else:
                cur.append((px, py))
        if cur: segs.append(cur)
        for sg in segs:
            if len(sg) > 1:
                c.ink_line(sg, width=w, closed=False, alpha=200, passes=1, jitter=0, color=(70, 30, 30))
    else:
        c.ink_line(rim, width=w, alpha=200, passes=1, jitter=0, color=(70, 30, 30))
    c.ink_line(smooth([(x - s, y0)] + left + bottom[::-1] + right[::-1] + [(x + s, y0)], rounds=1, closed=False), width=w, closed=False, alpha=200, passes=1, jitter=0, color=(70, 30, 30))
    c.ink_line(smooth(outer, rounds=1, closed=False), width=w * 0.9, closed=False, alpha=190, passes=1, jitter=0, color=(70, 30, 30))
    c.ink_line(smooth(inner, rounds=1, closed=False), width=w * 0.8, closed=False, alpha=170, passes=1, jitter=0, color=(70, 30, 30))
    # marshmallows floating, a couple tipped against the rim
    spots = [(-0.02, 0.0, 0.1), (0.3, 0.12, -0.25), (-0.3, 0.25, 0.3), (0.45, -0.25, 0.5), (0.08, -0.45, -0.1), (-0.52, -0.1, 0.2)]
    for dx, dy, a in spots[:marshmallows]:
        tint = (250, 226, 230) if rnd.random() < 0.35 else None
        marshmallow(c, x + s * dx, cy0 + rim_h * dy - s * 0.06, s * 0.3, P, angle=a, tint=tint)
    if steam:
        for dx, ln in ((-0.3, 8), (0.05, 10), (0.38, 7)):
            ph = rnd.uniform(0, 6.28)
            pts = [(x + s * dx + s * 0.07 * math.sin(t * 0.8 + ph) * (0.5 + t / ln), y0 - rim_h * 1.2 - s * 0.075 * t) for t in range(ln)]
            bd = smooth([(px - s * 0.06, py) for px, py in pts] + [(px + s * 0.06, py) for px, py in pts[::-1]], rounds=2)
            c.wash(bd, '#d6cdc4', None, strength=0.22, layers=12, spread=0.05, edge=0.3)
            c.ink_line(smooth(pts, rounds=2, closed=False), width=max(2, s * 0.013), closed=False, alpha=115, passes=1, jitter=0)


# ---------------------------------------------------------------- christmas cookies
def _icing(c, pts, s, closed=True, w=0.032, alpha=235):
    """Piped royal icing: a white line on top of the paint (ink layer), with a
    faint grey-blue shadow line just below so it reads raised."""
    c.ink_line([(px + s * 0.008, py + s * 0.012) for px, py, *_ in pts], width=max(2, s * w * 1.1), closed=closed,
               alpha=70, passes=1, jitter=0, color=(150, 140, 150))
    c.ink_line(pts, width=max(2, s * w), closed=closed, alpha=alpha, passes=1, jitter=0, color=(252, 250, 244))


def _dot(c, x, y, r, color, alpha=240, hl=True):
    """A candy or icing dot in gouache with a small white highlight."""
    gouache(c, ellipse(x, y, r, r, 10), color=color, alpha=alpha, soft=0.06)
    if hl:
        gouache(c, ellipse(x - r * 0.3, y - r * 0.32, r * 0.3, r * 0.26, 8), color=(255, 252, 248), alpha=200, soft=0.1)


def gingerbread_shape(x, y, s, angle=0.0):
    """A gingerbread man: round head, arms out, legs apart. s = half his height."""
    # head arc from lower-left over the top to lower-right (screen y points down)
    head = [(x + s * 0.3 * math.cos(a), y - s * 0.62 + s * 0.3 * math.sin(a)) for a in [math.pi * (0.68 + 1.64 * i / 14) for i in range(15)]]
    pts = [(x + s * 0.13, y - s * 0.36),                       # neck right
           (x + s * 0.62, y - s * 0.3), (x + s * 0.74, y - s * 0.2), (x + s * 0.66, y - s * 0.07),  # right arm
           (x + s * 0.3, y - s * 0.06),
           (x + s * 0.34, y + s * 0.3), (x + s * 0.56, y + s * 0.78), (x + s * 0.48, y + s * 0.93), (x + s * 0.32, y + s * 0.92),  # right leg
           (x + s * 0.02, y + s * 0.5),
           (x - s * 0.02, y + s * 0.5),
           (x - s * 0.32, y + s * 0.92), (x - s * 0.48, y + s * 0.93), (x - s * 0.56, y + s * 0.78), (x - s * 0.34, y + s * 0.3),
           (x - s * 0.3, y - s * 0.06),
           (x - s * 0.66, y - s * 0.07), (x - s * 0.74, y - s * 0.2), (x - s * 0.62, y - s * 0.3),
           (x - s * 0.13, y - s * 0.36)]
    full = [(x - s * 0.13, y - s * 0.36)] + [p for p in head] + pts
    return _rot(smooth(full, rounds=2), x, y, angle)


def gingerbread_man(c, x, y, s, P, angle=0.0, buttons=None):
    """A baked gingerbread man: warm ginger wash with a darker baked rim,
    white piped icing at wrists, ankles and smile, gouache candy buttons."""
    rnd = c.rnd
    body = gingerbread_shape(x, y, s, angle)
    c.wash(body, '#c98a4e', '#b06c35', strength=0.9, spread=0.006, layers=26, edge=1.3, granulate=0.55)
    c.wash(_rot(smooth([(x - s * 0.22, y - s * 0.3), (x + s * 0.18, y - s * 0.32), (x + s * 0.12, y + s * 0.3), (x - s * 0.18, y + s * 0.28)]), x, y, angle),
           '#e0a868', None, strength=0.25, spread=0.05, layers=10, edge=0.2)
    c.ink_line(body, width=max(2, s * 0.018), alpha=150, passes=1, jitter=0, color=(110, 60, 30))
    R = lambda px, py: _rot([(x + px * s, y + py * s)], x, y, angle)[0]
    # icing squiggles: wrists and ankles
    for (ax, ay, bx, by) in ((0.5, -0.27, 0.56, -0.09), (-0.5, -0.27, -0.56, -0.09), (0.3, 0.7, 0.5, 0.66), (-0.3, 0.7, -0.5, 0.66)):
        zz = []
        for i in range(7):
            t = i / 6
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            nx, ny = -(by - ay), (bx - ax)
            nl = math.hypot(nx, ny) or 1
            o = 0.045 * (1 if i % 2 else -1)
            zz.append(R(px + nx / nl * o, py + ny / nl * o))
        _icing(c, smooth(zz, rounds=1, closed=False), s, closed=False, w=0.03)
    # face: eyes and a smile
    for sx in (-1, 1):
        ex, ey = R(sx * 0.1, -0.66)
        gouache(c, ellipse(ex, ey, s * 0.045, s * 0.05, 8), color=(60, 35, 25), alpha=235, soft=0.05)
    smile = [R(-0.13 + 0.26 * t, -0.53 + 0.06 * math.sin(math.pi * t)) for t in [i / 8 for i in range(9)]]
    _icing(c, smile, s, closed=False, w=0.03)
    cheeks = [R(-0.2, -0.56), R(0.2, -0.56)]
    for cx, cy in cheeks:
        c.wash(ellipse(cx, cy, s * 0.06, s * 0.04, 8), '#e06a5a', None, strength=0.45, layers=10, spread=0.05)
    # candy buttons down the middle
    cols = buttons or [(198, 43, 51), (63, 122, 82), (198, 43, 51)]
    for k, py in enumerate((-0.25, -0.05, 0.15)):
        bx, by = R(0, py)
        _dot(c, bx, by, s * 0.06, tuple(cols[k % len(cols)]))


def _star_pts(x, y, r, r2, n=5, angle=0.0):
    pts = []
    for i in range(n * 2):
        a = angle - math.pi / 2 + math.pi * i / n
        rr = r if i % 2 == 0 else r2
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return pts


def cookie_shape(kind, x, y, s, angle=0.0):
    """Outline of a cut-out cookie: star, tree, heart, round, mitten. s = radius."""
    if kind == 'star':
        pts = smooth(_star_pts(x, y, s, s * 0.52), rounds=1)
    elif kind == 'tree':
        pts = [(x, y - s), (x + s * 0.42, y - s * 0.45), (x + s * 0.25, y - s * 0.45), (x + s * 0.68, y + s * 0.15),
               (x + s * 0.42, y + s * 0.15), (x + s * 0.88, y + s * 0.68), (x + s * 0.16, y + s * 0.68), (x + s * 0.16, y + s * 0.98),
               (x - s * 0.16, y + s * 0.98), (x - s * 0.16, y + s * 0.68), (x - s * 0.88, y + s * 0.68), (x - s * 0.42, y + s * 0.15),
               (x - s * 0.68, y + s * 0.15), (x - s * 0.25, y - s * 0.45), (x - s * 0.42, y - s * 0.45)]
        pts = smooth(pts, rounds=1)
    elif kind == 'heart':
        pts = []
        for i in range(36):
            t = 2 * math.pi * i / 36
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((x + hx / 17 * s, y + (hy + 2) / 17 * s))
    elif kind == 'mitten':
        pts = [(x - s * 0.5, y + s * 0.95), (x - s * 0.55, y - s * 0.2), (x - s * 0.45, y - s * 0.75), (x - s * 0.05, y - s * 0.95),
               (x + s * 0.35, y - s * 0.8), (x + s * 0.48, y - s * 0.4), (x + s * 0.5, y - s * 0.1), (x + s * 0.72, y - s * 0.38),
               (x + s * 0.9, y - s * 0.3), (x + s * 0.85, y), (x + s * 0.5, y + s * 0.45), (x + s * 0.48, y + s * 0.95)]
        pts = smooth(pts, rounds=2)
    else:
        pts = ellipse(x, y, s, s, 32)
    return _rot(pts, x, y, angle)


def _inset(pts, x, y, k):
    return [(x + (px - x) * k, y + (py - y) * k) for px, py, *_ in pts]


ICING = {'red': ('#cf3a40', '#e2605f'), 'green': ('#3f8a5a', '#6fae7f'), 'blue': ('#8fbad6', '#bcd7e8'),
         'pink': ('#eea2b0', '#f6c6cf'), 'white': None}


def sugar_cookie(c, x, y, s, P, kind=None, icing=None, angle=0.0):
    """An iced cut-out sugar cookie: a golden baked edge, flooded icing in a
    Christmas color (or white gouache), then piped white details and sprinkles."""
    rnd = c.rnd
    kind = kind or rnd.choice(('star', 'tree', 'heart', 'round', 'mitten', 'star', 'tree'))
    if icing is None:
        icing = {'tree': rnd.choice(('green', 'green', 'white')), 'heart': rnd.choice(('red', 'pink', 'red')),
                 'star': rnd.choice(('white', 'blue', 'red')), 'mitten': rnd.choice(('red', 'blue', 'green')),
                 'round': rnd.choice(('white', 'red', 'green', 'blue'))}[kind]
    outer = cookie_shape(kind, x, y, s, angle)
    inner = smooth(_inset(outer, x, y, 0.84), rounds=1)
    # the baked edge is painted as a ring, so the icing colors stay clean
    ring = list(outer) + [outer[0]] + [inner[0]] + list(inner[::-1])
    c.wash(outer, '#efd3a2', None, strength=0.25 if ICING.get(icing) else 0.6, spread=0.004, layers=14, edge=0.6, granulate=0.4)
    c.wash(ring, '#e2b475', '#d39a55', strength=0.8, spread=0.004, layers=18, edge=1.2, granulate=0.5)
    c.ink_line(smooth(outer, rounds=1), width=max(2, s * 0.02), alpha=130, passes=1, jitter=0, color=(150, 95, 45))
    if ICING.get(icing):
        a, b = ICING[icing]
        c.wash(inner, a, b, strength=0.9, spread=0.004, layers=22, edge=0.9, granulate=0.15)
    else:
        gouache(c, inner, color=(250, 248, 242), alpha=238, soft=0.008)
        gouache(c, _inset(inner, x + s * 0.06, y + s * 0.08, 0.8), color=(222, 228, 236), alpha=70, soft=0.08)
    _icing(c, inner, s, w=0.04)
    accent = (198, 43, 51) if icing in ('white', 'green', 'blue') else (63, 122, 82)
    R = lambda px, py: _rot([(x + px * s, y + py * s)], x, y, angle)[0]
    if kind == 'tree':
        for yy, ww in ((-0.38, 0.22), (0.05, 0.42), (0.48, 0.62)):
            zz = [R(-ww + 2 * ww * t, yy + 0.07 * math.sin(math.pi * t) + (t - 0.5) * 0.12) for t in [i / 8 for i in range(9)]]
            _icing(c, zz, s, closed=False, w=0.032)
        for px, py in ((-0.12, -0.2), (0.2, 0.2), (-0.3, 0.35), (0.1, 0.55), (0.4, 0.58), (-0.08, 0.15)):
            bx, by = R(px, py)
            _dot(c, bx, by, s * 0.055, rnd.choice(((198, 43, 51), (240, 200, 80), (250, 248, 242))))
        sx, sy = R(0, -0.88)
        gouache(c, _star_pts(sx, sy, s * 0.16, s * 0.07), color=(240, 200, 80), alpha=245, soft=0.03)
    elif kind == 'star':
        for i in range(5):
            a = angle - math.pi / 2 + 2 * math.pi * i / 5
            _icing(c, [(x + s * 0.12 * math.cos(a), y + s * 0.12 * math.sin(a)), (x + s * 0.55 * math.cos(a), y + s * 0.55 * math.sin(a))],
                   s, closed=False, w=0.03)
        _dot(c, x, y, s * 0.08, accent)
    elif kind == 'heart':
        for k in range(3):
            pts = [R(-0.42 + 0.84 * t, -0.15 + 0.24 * k + 0.06 * math.sin(math.pi * 3 * t)) for t in [i / 12 for i in range(13)]]
            _icing(c, pts, s, closed=False, w=0.026)
    elif kind == 'mitten':
        gouache(c, smooth([R(-0.4, 0.5), R(0.4, 0.5), R(0.4, 0.74), R(-0.4, 0.74)], rounds=1), color=(250, 248, 242), alpha=240, soft=0.01)
        for k in range(5):
            _dot(c, *R(-0.3 + 0.15 * k, 0.62), s * 0.035, (120, 170, 200) if icing != 'blue' else (198, 43, 51), hl=False)
        for px, py in ((-0.15, -0.45), (0.12, -0.2), (-0.22, 0.1), (0.2, 0.25)):
            fx, fy = R(px, py)
            for j in range(3):
                b = math.pi / 3 * j + angle
                _icing(c, [(fx - s * 0.08 * math.cos(b), fy - s * 0.08 * math.sin(b)), (fx + s * 0.08 * math.cos(b), fy + s * 0.08 * math.sin(b))],
                       s, closed=False, w=0.022)
    else:
        if icing == 'white':
            for _ in range(14):
                a = rnd.uniform(0, 2 * math.pi); r = s * 0.62 * math.sqrt(rnd.random())
                px, py = x + r * math.cos(a), y + r * math.sin(a)
                b = rnd.uniform(0, math.pi)
                col = rnd.choice(((198, 43, 51), (63, 122, 82), (240, 200, 80), (143, 186, 214)))
                gouache(c, _rrect(px, py, s * 0.13, s * 0.045, s * 0.02, b), color=col, alpha=240, soft=0.03)
        else:
            for j in range(6):
                b = math.pi / 3 * j + angle
                _icing(c, [(x, y), (x + s * 0.55 * math.cos(b), y + s * 0.55 * math.sin(b))], s, closed=False, w=0.03)
                mx, my = x + s * 0.34 * math.cos(b), y + s * 0.34 * math.sin(b)
                for side in (-1, 1):
                    bb = b + side * 0.8
                    _icing(c, [(mx, my), (mx + s * 0.15 * math.cos(bb), my + s * 0.15 * math.sin(bb))], s, closed=False, w=0.024)


def candy_cane(c, x, y, s, P, angle=0.0, flip=False):
    """A striped candy cane: white kept as bare paper, red stripes spiralling
    round it, a soft shadow down one side. s = half its length."""
    sg = -1 if flip else 1
    sx = x - sg * s * 0.18                       # the shaft
    path = [(sx, y + s - t / 9 * s * 1.35) for t in range(10)]
    hr = s * 0.28                                # the hook: over the top and a little way down
    hx, hy = sx + sg * hr, y - s * 0.35
    for i in range(1, 15):
        a = (math.pi + math.pi * i / 11) if sg > 0 else (-math.pi * i / 11)
        path.append((hx + hr * math.cos(a), hy + hr * math.sin(a) + (s * 0.05 * (i - 11) if i > 11 else 0)))
    path = _rot(path, x, y, angle)
    w = s * 0.085
    L, Rr = [], []
    n = len(path)
    for i in range(n):
        p0 = path[max(0, i - 1)]; p1 = path[min(n - 1, i + 1)]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        L.append((path[i][0] + nx * w, path[i][1] + ny * w)); Rr.append((path[i][0] - nx * w, path[i][1] - ny * w))
    body = L + Rr[::-1]
    c.reserve(body)
    mid = [((L[i][0] + Rr[i][0]) / 2, (L[i][1] + Rr[i][1]) / 2) for i in range(n)]
    c.wash(Rr + mid[::-1], '#d9c9cf', None, strength=0.35, spread=0.01, layers=12, edge=0.4)   # shadow side
    for i in range(0, n - 2, 2):
        stripe = [L[i], L[i + 1], Rr[i + 2], Rr[i + 1]]
        c.wash(stripe, '#c62b33', '#e0525a', strength=0.95, spread=0.01, layers=10, edge=0.9, granulate=0.1)
    c.ink_line(smooth(body, rounds=1), width=max(2, s * 0.012), alpha=150, passes=1, jitter=0, color=(120, 40, 45))


def sprinkles(c, x, y, s, P, n=9):
    """A scatter of rainbow-free Christmas sprinkles in gouache: red, green, gold, white."""
    rnd = c.rnd
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi); r = s * math.sqrt(rnd.random())
        col = rnd.choice(((198, 43, 51), (63, 122, 82), (240, 200, 80), (250, 248, 242), (198, 43, 51)))
        gouache(c, _rrect(x + r * math.cos(a), y + r * math.sin(a), s * 0.32, s * 0.11, s * 0.05, rnd.uniform(0, math.pi)),
                color=col, alpha=240, soft=0.03)


# ---------------------------------------------------------------- hanukkah
GOLD, GOLD2, GOLD_INK = '#d29a38', '#f0cc72', (120, 78, 25)


def _arc_band(x, y, r, w, n=24):
    """A U-shaped band (lower half circle) centred at (x, y), radius r, width w."""
    outer = [(x + (r + w / 2) * math.cos(math.pi * i / n), y + (r + w / 2) * math.sin(math.pi * i / n)) for i in range(n + 1)]
    inner = [(x + (r - w / 2) * math.cos(math.pi * i / n), y + (r - w / 2) * math.sin(math.pi * i / n)) for i in range(n, -1, -1)]
    return outer + inner


def flame(c, x, y, s, glow=True):
    """A candle flame (x, y) = its base, s = its height: a soft glow, a gold
    outer flame, a pale core and a touch of blue at the wick."""
    if glow:
        c.wash(ellipse(x, y - s * 0.5, s * 0.62, s * 0.85, 18), '#f8dc8c', '#fbe9b8', strength=0.2, spread=0.09,
               layers=14, edge=0.15, granulate=0.15)
    body = [(x, y - s)] + [(x + s * 0.3 * math.sin(math.pi * t) * (1 - 0.35 * t), y - s * (1 - t)) for t in (0.2, 0.4, 0.6, 0.8)]
    body += [(x + s * 0.2 * math.cos(a), y + s * 0.02 * math.sin(a)) for a in (0.0, 1.2, 1.9, 3.14)]
    body += [(x - s * 0.3 * math.sin(math.pi * t) * (1 - 0.35 * t), y - s * (1 - t)) for t in (0.8, 0.6, 0.4, 0.2)]
    body = smooth(body, rounds=2)
    c.wash(body, '#f2a43a', '#f6c656', strength=0.95, spread=0.01, layers=14, edge=1.0, granulate=0.1)
    core = [(px * 0.55 + x * 0.45, py * 0.6 + (y - s * 0.12) * 0.4) for px, py in body]
    gouache(c, core, color=(255, 246, 214), alpha=225, soft=0.08)
    c.wash(ellipse(x, y - s * 0.03, s * 0.08, s * 0.1, 8), '#6f8fc0', None, strength=0.6, layers=8)


def menorah(c, x, y, s, P, lit=9, candle=None, candle2=None):
    """A nine-branch Hanukkah menorah in gold with blue candles, the raised
    centre candle (shamash) lit plus `lit` - 1 others. (x, y) = centre of the
    arms, s = half the width across the outer cups."""
    col = candle or P.get('candle', '#4a7fc0'); col2 = candle2 or P.get('candle2', '#9cc2e6')
    d = s / 4                                    # spacing between branches
    cup_y = y - s * 0.12                         # top of the eight side cups
    sh_y = cup_y - s * 0.2                       # top of the shamash cup
    base_y = y + s * 0.95
    w = s * 0.055                                # arm width
    # arms: nested U bands from each pair of cups down to the stem
    for k in (4, 3, 2, 1):
        c.wash(_arc_band(x, cup_y, k * d, w), GOLD, GOLD2, strength=0.85, spread=0.008, layers=16, edge=1.0, granulate=0.45)
    # the centre stem and a stepped foot
    stem = [(x - w * 0.8, sh_y + s * 0.04), (x + w * 0.8, sh_y + s * 0.04), (x + w * 0.9, base_y - s * 0.12), (x - w * 0.9, base_y - s * 0.12)]
    c.wash(stem, GOLD, GOLD2, strength=0.9, spread=0.006, layers=16, edge=1.0, granulate=0.45)
    knop = ellipse(x, cup_y + s * 0.62, w * 1.7, w * 1.1, 14)
    c.wash(knop, GOLD, None, strength=0.95, spread=0.01, layers=12, edge=1.1)
    foot = [(x - s * 0.36, base_y), (x - s * 0.3, base_y - s * 0.07), (x - s * 0.1, base_y - s * 0.13), (x + s * 0.1, base_y - s * 0.13),
            (x + s * 0.3, base_y - s * 0.07), (x + s * 0.36, base_y)]
    foot = smooth(foot + [(x + s * 0.34, base_y + s * 0.04), (x - s * 0.34, base_y + s * 0.04)], rounds=1)
    c.wash(foot, GOLD, GOLD2, strength=0.9, spread=0.008, layers=18, edge=1.0, granulate=0.5)
    # shading down the right of the stem and foot
    c.wash([(x + w * 0.1, sh_y + s * 0.05), (x + w * 0.85, sh_y + s * 0.05), (x + w * 0.9, base_y - s * 0.13), (x + w * 0.1, base_y - s * 0.13)],
           '#a8732a', None, strength=0.35, spread=0.01, layers=8, edge=0.4)
    ink = dict(alpha=190, passes=1, jitter=0, color=GOLD_INK)
    lw = max(1, s * 0.008)
    for k in (4, 3, 2, 1):
        for rr in (k * d + w / 2, k * d - w / 2):
            c.ink_line([(x + rr * math.cos(math.pi * i / 24), cup_y + rr * math.sin(math.pi * i / 24)) for i in range(25)],
                       width=lw, closed=False, **ink)
    c.ink_line(stem, width=lw, closed=False, **ink)
    c.ink_line(foot, width=lw, **ink)
    c.ink_line(smooth(knop, rounds=1), width=lw, **ink)
    # cups, candles, flames: side candles left to right, the shamash raised in the middle
    tops = [(x + (i - 4) * d, cup_y) for i in range(9) if i != 4]
    order = [tops[i] for i in (0, 1, 2, 3)] + [(x, sh_y)] + [tops[i] for i in (4, 5, 6, 7)]
    ch, cw = s * 0.36, s * 0.062
    lit_idx = {4} | set(sorted(range(9), key=lambda i: -i)[:max(0, lit - 1)] if lit < 9 else range(9))
    if lit >= 9:
        lit_idx = set(range(9))
    for i, (px, py) in enumerate(order):
        cup = _rrect(px, py, s * 0.13, s * 0.07, s * 0.02)
        c.wash(cup, GOLD, GOLD2, strength=0.95, spread=0.008, layers=12, edge=1.1)
        c.ink_line(cup, width=lw, **ink)
        ctop = py - s * 0.035 - ch
        body = _rrect(px, (ctop + py - s * 0.035) / 2, cw, ch, cw * 0.25)
        cc = col if i % 2 == 0 else col2
        c.wash(body, cc, col2 if cc == col else col, strength=0.8, spread=0.008, layers=14, edge=0.9)
        c.wash([(px + cw * 0.12, ctop + s * 0.01), (px + cw * 0.48, ctop + s * 0.01), (px + cw * 0.48, py - s * 0.04), (px + cw * 0.12, py - s * 0.04)],
               '#3a5f94', None, strength=0.3, spread=0.01, layers=8, edge=0.3)
        c.ink_line(body, width=max(1, s * 0.006), alpha=150, passes=1, jitter=0, color=(45, 65, 100))
        c.ink_line([(px, ctop), (px + s * 0.004, ctop - s * 0.03)], width=max(1, s * 0.008), closed=False, alpha=200, passes=1, jitter=0, color=(50, 40, 35))
        if i in lit_idx:
            flame(c, px, ctop - s * 0.025, s * 0.14)


def plate(c, x, y, s, P, color=None, color2=None):
    """A shallow round serving plate seen from the front: s = half its width.
    A pale blue glaze with a darker rim band."""
    col = color or P.get('plate', '#8fb6da'); col2 = color2 or P.get('plate2', '#d6e6f3')
    ry = s * 0.3
    c.wash(ellipse(x, y, s, ry, 40), col2, '#f3f7fb', strength=0.55, spread=0.006, layers=18, edge=0.6)
    ring = [(x + s * math.cos(2 * math.pi * i / 40), y + ry * math.sin(2 * math.pi * i / 40)) for i in range(41)]
    ring += [(x + s * 0.84 * math.cos(2 * math.pi * i / 40), y + ry * 0.8 * math.sin(2 * math.pi * i / 40)) for i in range(40, -1, -1)]
    c.wash(ring, col, None, strength=0.75, spread=0.006, layers=14, edge=1.0)
    # the plate's front edge thickness
    lip = [(x + s * math.cos(math.pi * i / 20), y + ry * math.sin(math.pi * i / 20)) for i in range(21)]
    lip += [(x + s * 0.97 * math.cos(math.pi * i / 20), y + ry * math.sin(math.pi * i / 20) + s * 0.06) for i in range(20, -1, -1)]
    c.wash(lip, col, None, strength=0.6, spread=0.01, layers=12, edge=0.8)
    c.ink_line(smooth(ellipse(x, y, s, ry, 40), rounds=1), width=max(1, s * 0.012), alpha=170, passes=1, jitter=0, color=(50, 70, 100))
    c.ink_line([(x + s * 0.97 * math.cos(math.pi * i / 20), y + ry * math.sin(math.pi * i / 20) + s * 0.06) for i in range(21)],
               width=max(1, s * 0.012), closed=False, alpha=170, passes=1, jitter=0, color=(50, 70, 100))


def sufganiyah(c, x, y, s, P, jam=None, angle=0.0):
    """A jam-filled Hanukkah doughnut: a round golden fried bun with the pale
    band round its middle, a heavy dusting of powdered sugar and a dab of red
    jam piped in on top. s = radius."""
    rnd = c.rnd
    jam = jam or P.get('jam', '#b5222f')
    h = s * 0.86
    dome = smooth([(x + s * math.cos(a), y + h * 0.62 * math.sin(a)) for a in [math.pi + math.pi * i / 16 for i in range(17)]] +
                  [(x + s * 0.98, y + h * 0.14), (x + s * 0.84, y + h * 0.36), (x + s * 0.42, y + h * 0.46), (x - s * 0.42, y + h * 0.46),
                   (x - s * 0.84, y + h * 0.36), (x - s * 0.98, y + h * 0.14)], rounds=2)
    c.wash(dome, '#dba25a', '#c47c36', strength=0.85, spread=0.012, layers=26, edge=1.0, granulate=0.45)
    # the pale ring where the dough floated above the oil
    band = [(x + s * 0.99 * math.cos(a), y + h * 0.12 + h * 0.2 * math.sin(a)) for a in [math.pi * i / 18 for i in range(19)]]
    band += [(x + s * 0.93 * math.cos(a), y + h * 0.02 + h * 0.12 * math.sin(a)) for a in [math.pi * i / 18 for i in range(18, -1, -1)]]
    gouache(c, smooth(band, rounds=1), color=(244, 222, 178), alpha=215, soft=0.03)
    # a darker crown and shadow under the belly
    c.wash(ellipse(x - s * 0.1, y - h * 0.3, s * 0.7, h * 0.3, 18), '#a8622a', None, strength=0.3, spread=0.03, layers=12, edge=0.4)
    c.wash(ellipse(x + s * 0.1, y + h * 0.36, s * 0.7, h * 0.1, 18), '#9a5a26', None, strength=0.35, spread=0.03, layers=10, edge=0.3)
    # powdered sugar: soft drifts and a scatter of dots over the top
    for _ in range(7):
        a = rnd.uniform(math.pi * 1.1, math.pi * 1.9); r = rnd.uniform(0.15, 0.7)
        gouache(c, ellipse(x + s * r * math.cos(a), y - h * 0.2 + h * 0.5 * r * math.sin(a), s * 0.32, h * 0.11, 12, rot=rnd.uniform(-0.3, 0.3)),
                color=(253, 251, 247), alpha=150, soft=0.12)
    for _ in range(70):
        a = rnd.uniform(math.pi * 1.04, math.pi * 1.96); r = s * math.sqrt(rnd.random()) * 0.92
        px, py = x + r * math.cos(a), y - h * 0.06 + r * 0.6 * math.sin(a)
        rr = s * rnd.uniform(0.012, 0.03)
        gouache(c, ellipse(px, py, rr, rr, 6), color=(254, 252, 248), alpha=240, soft=0.06)
    # the jam: a glossy dab piped in on top, with a small drip
    k = 1.35
    jx, jy = x + s * 0.06, y - h * 0.5
    blob = smooth([(jx - s * 0.2 * k, jy), (jx - s * 0.1 * k, jy - s * 0.1 * k), (jx + s * 0.12 * k, jy - s * 0.11 * k), (jx + s * 0.22 * k, jy - s * 0.02 * k),
                   (jx + s * 0.15 * k, jy + s * 0.06 * k), (jx + s * 0.1 * k, jy + s * 0.2 * k), (jx + s * 0.04 * k, jy + s * 0.21 * k),
                   (jx + s * 0.02 * k, jy + s * 0.07 * k), (jx - s * 0.14 * k, jy + s * 0.06 * k)], rounds=2)
    c.wash(blob, jam, '#d6404a', strength=1.05, spread=0.01, layers=18, edge=1.2)
    gouache(c, ellipse(jx - s * 0.05, jy - s * 0.06, s * 0.06, s * 0.03, 8), color=(255, 236, 236), alpha=210, soft=0.1)
    c.ink_line(blob, width=max(1, s * 0.012), alpha=150, passes=1, jitter=0, color=(110, 20, 30))
    c.ink_line(dome, width=max(1, s * 0.014), alpha=150, passes=1, jitter=0, color=(110, 65, 30))


def _letter(c, name, x, y, h, color=(250, 244, 226), width=None, angle=0.0, skew=0.0):
    """A Hebrew dreidel letter drawn as brush strokes (nun, gimel, hei, shin),
    h = letter height, (x, y) its centre; skew shears it onto a face."""
    w = width or max(2, h * 0.13)
    S = {
        'nun':   [[(-0.08, -0.5), (0.18, -0.5), (0.2, 0.45), (-0.3, 0.45)]],
        'gimel': [[(-0.22, -0.5), (0.1, -0.5), (0.14, 0.45)], [(0.14, 0.2), (-0.26, 0.48)]],
        'hei':   [[(-0.32, -0.48), (0.32, -0.48), (0.32, 0.48)], [(-0.24, -0.1), (-0.24, 0.48)]],
        'shin':  [[(-0.36, -0.48), (-0.3, 0.42), (0.36, 0.42), (0.36, -0.48)], [(0.0, -0.48), (-0.05, 0.1), (-0.3, 0.38)]],
    }
    for stroke in S[name]:
        pts = [(x + (px + skew * py) * h, y + py * h) for px, py in stroke]
        c.ink_line(_rot(pts, x, y, angle), width=w, closed=False, alpha=235, passes=1, jitter=0, color=color)


def dreidel(c, x, y, s, P, angle=0.0, color=None, color2=None, letters=('nun', 'gimel')):
    """A spinning top with four lettered sides, seen at three quarters: front
    face, side face, top with its stem, and the point. s = front face width."""
    col = color or P.get('dreidel', '#3f72b0'); col2 = color2 or P.get('dreidel2', '#86b2de')
    f = s / 2
    sk = s * 0.42                                   # depth of the side face
    up = s * 0.2
    front = [(x - f, y - f), (x + f, y - f), (x + f, y + f), (x - f, y + f)]
    side = [(x + f, y - f), (x + f + sk, y - f - up), (x + f + sk, y + f - up), (x + f, y + f)]
    top = [(x - f, y - f), (x - f + sk, y - f - up), (x + f + sk, y - f - up), (x + f, y - f)]
    tip = (x + sk * 0.35, y + f + s * 0.62)
    point_f = [(x - f, y + f), (x + f, y + f), tip]
    point_s = [(x + f, y + f), (x + f + sk, y + f - up), tip]
    R = lambda pts: _rot(pts, x, y, angle)
    c.wash(R(top), col2, '#cfe1f2', strength=0.7, spread=0.008, layers=14, edge=0.8)
    c.wash(R(front), col, col2, strength=0.85, spread=0.008, layers=20, edge=1.0, granulate=0.4)
    c.wash(R(side), col, None, strength=1.1, spread=0.008, layers=18, edge=1.0, granulate=0.4)
    c.wash(R(point_f), col, col2, strength=0.85, spread=0.008, layers=14, edge=1.0)
    c.wash(R(point_s), col, None, strength=1.15, spread=0.008, layers=12, edge=1.0)
    # stem on the top face
    tcx, tcy = x + sk / 2, y - f - up / 2
    stem = [(tcx - s * 0.07, tcy), (tcx - s * 0.06, tcy - s * 0.4), (tcx + s * 0.06, tcy - s * 0.4), (tcx + s * 0.07, tcy)]
    ink = dict(alpha=185, passes=1, jitter=0, color=(30, 45, 80))
    lw = max(1, s * 0.016)
    for poly in (front, side, top, point_f, point_s):
        c.ink_line(R(poly), width=lw, **ink)
    # the stem goes on last in opaque gold so the top face's outline doesn't cross it
    gouache(c, R(stem), color=(214, 160, 70), alpha=250, soft=0.01)
    gouache(c, R([(tcx + s * 0.005, tcy), (tcx + s * 0.005, tcy - s * 0.4), (tcx + s * 0.06, tcy - s * 0.4), (tcx + s * 0.07, tcy)]),
            color=(178, 122, 45), alpha=150, soft=0.04)
    gouache(c, R(ellipse(tcx, tcy - s * 0.4, s * 0.06, s * 0.025, 10)), color=(236, 198, 112), alpha=245, soft=0.02)
    c.ink_line(R(stem), width=lw, closed=False, **ink)          # open at the foot, where it meets the top
    # letters in gold-cream gouache: one on the front, a narrower one on the side
    _letter(c, letters[0], *(_rot([(x, y)], x, y, angle)[0]), s * 0.52, color=(248, 230, 170), width=max(2, s * 0.07), angle=angle)
    sx, sy = x + f + sk / 2, y - up / 2
    _letter(c, letters[1], *(_rot([(sx, sy)], x, y, angle)[0]), s * 0.42, color=(240, 214, 140), width=max(2, s * 0.05),
            angle=angle, skew=-0.25)


def gelt(c, x, y, s, P, angle=0.0, silver=False):
    """A foil-wrapped chocolate coin seen at a slant. s = radius."""
    c1, c2, ink = ('#b9c0c8', '#e4e8ec', (90, 95, 105)) if silver else (GOLD, GOLD2, GOLD_INK)
    rim = ellipse(x, y, s, s * 0.62, 28, rot=angle)
    c.wash(rim, c1, c2, strength=0.95, spread=0.008, layers=16, edge=1.1, granulate=0.5)
    c.wash(ellipse(x + s * 0.04, y + s * 0.07, s * 0.98, s * 0.6, 28, rot=angle), c1, None, strength=0.5, spread=0.01, layers=10, edge=0.6)
    c.wash(ellipse(x, y, s * 0.72, s * 0.44, 24, rot=angle), c2, None, strength=0.55, spread=0.01, layers=10, edge=0.8)
    c.ink_line(smooth(rim, rounds=1), width=max(1, s * 0.04), alpha=170, passes=1, jitter=0, color=ink)
    c.ink_line(smooth(ellipse(x, y, s * 0.72, s * 0.44, 24, rot=angle), rounds=1), width=max(1, s * 0.025), alpha=130, passes=1, jitter=0, color=ink)
    gouache(c, ellipse(x - s * 0.35, y - s * 0.2, s * 0.16, s * 0.06, 8, rot=angle - 0.4), color=(255, 250, 230), alpha=190, soft=0.1)


def olive_sprig(c, x, y, s, P, angle=-1.0, n=7):
    """An olive branch: a thin stem with narrow silvery-green leaves in pairs
    and two or three small olives. s = branch length."""
    ca, sa = math.cos(angle), math.sin(angle)
    stem = [(x + s * ca * t + s * 0.04 * math.sin(t * 3) * -sa, y + s * sa * t + s * 0.04 * math.sin(t * 3) * ca) for t in [i / 10 for i in range(11)]]
    c.ink_line(stem, width=max(2, s * 0.012), closed=False, alpha=200, passes=1, jitter=0, color=(95, 100, 60))
    for i in range(n):
        t = (i + 0.6) / (n + 0.4)
        px, py = stem[min(10, int(t * 10))]
        side = 1 if i % 2 else -1
        la = angle + side * 0.75 + c.rnd.uniform(-0.15, 0.15)
        L = s * 0.24 * (1 - t * 0.35)
        lf = leaf(px + L * 0.5 * math.cos(la), py + L * 0.5 * math.sin(la), L, L * 0.17, la)
        c.wash(lf, P.get('olive', '#7c8a4c'), P.get('olive2', '#aeb88a'), strength=0.75, spread=0.03, layers=14, edge=0.9)
        c.ink_line([(px, py), (px + L * 0.9 * math.cos(la), py + L * 0.9 * math.sin(la))], width=max(1, s * 0.005), closed=False,
                   alpha=110, passes=1, jitter=0, color=(80, 85, 50))
    for t, off in ((0.35, 0.06), (0.62, -0.05)):
        px, py = stem[int(t * 10)]
        ox, oy = px - sa * s * off, py + ca * s * off
        c.wash(ellipse(ox, oy, s * 0.045, s * 0.032, 10, rot=angle), '#5b5a3a', '#8a8a52', strength=0.9, layers=10, edge=1.0)



MOTIFS = {'rose': rose, 'daisy': daisy, 'wildflower': wildflower, 'tulip': tulip, 'sprig': sprig, 'eucalyptus': eucalyptus,
          'berries': berries, 'bouquet': bouquet, 'mug': mug, 'books': books, 'heart': heart, 'paw': paw, 'dog': dog,
          'lemon': lemon, 'strawberry': strawberry, 'sun': sun, 'succulent': succulent, 'pumpkin': pumpkin,
          'ghost': ghost, 'maple_leaf': maple_leaf, 'acorn': acorn, 'sparkle': sparkle, 'moon': moon, 'bat': bat,
          'book_single': book_single, 'soup_bowl': soup_bowl, 'carrot': carrot,
          'garlic': garlic, 'mushroom': mushroom, 'bay_leaf': bay_leaf, 'peppercorns': peppercorns,
          'cardinal': cardinal, 'pine_bough': pine_bough, 'pinecone': pinecone, 'holly': holly,
          'snowflake': snowflake, 'snow_dot': snow_dot,
          'cocoa_mug': cocoa_mug, 'marshmallow': marshmallow, 'cinnamon_stick': cinnamon_stick,
          'orange_slice': orange_slice, 'star_anise': star_anise, 'peppermint': peppermint,
          'gingerbread_man': gingerbread_man, 'sugar_cookie': sugar_cookie, 'candy_cane': candy_cane, 'sprinkles': sprinkles,
          'menorah': menorah, 'flame': flame, 'plate': plate, 'sufganiyah': sufganiyah, 'dreidel': dreidel,
          'gelt': gelt, 'olive_sprig': olive_sprig}
