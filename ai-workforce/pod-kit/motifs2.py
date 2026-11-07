"""Detailed motifs (second generation): painted in many more passes than
motifs.py, the way an illustrator builds a finished watercolor: a pale
first wash for the form, patchy wet-in-wet color, shaped shadows wet on dry,
lifted highlights, dry-brush texture, opaque gouache last (snow, glints,
chrome), and a fine pen line where an edge must read.

Coordinates: (x, y) in canvas px, y down; s = the motif's size in px.
"""
import math
from watercolor import ellipse, leaf, rect, deform
from motifs import _rot, smooth, gouache, _rgb, _band, _star_pts, CONSTELLATIONS

# Capricornus, simplified to its familiar arrowhead outline (alpha-beta at the top right, delta at the left tip)
CONSTELLATIONS.setdefault('capricornus', {
    'stars': [(0.74, -0.62), (0.66, -0.44), (0.22, -0.22), (-0.12, -0.18), (-0.52, -0.2), (-0.7, -0.26), (-0.3, 0.3), (0.18, 0.5),
              (0.38, 0.32)],
    'lines': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 1)],
    'bright': [0, 1, 5]})


def _lerp(a, b, t):
    return a + (b - a) * t


def _path_normal(path, i):
    n = len(path)
    qx, qy = path[min(i + 1, n - 1)]; rx, ry = path[max(i - 1, 0)]
    dx, dy = qx - rx, qy - ry
    L = math.hypot(dx, dy) or 1
    return -dy / L, dx / L


# ---------------------------------------------------------------- backgrounds
def splash(c, x, y, s, P, color=None, color2=None, vary=None, aspect=0.82, strength=0.4, drips=8, blooms=0):
    """A loose background wash behind a scene: an irregular blot with soft
    and hard edges, a few backruns and a spray of drips around it, the way
    watercolor illustrations sit on the page. s = half the width."""
    rnd = c.rnd
    col = color or P.get('sky', '#a9c5db'); col2 = color2 or P.get('sky2', '#f2e8dc')
    pts = []
    for k in range(30):
        a = 2 * math.pi * k / 30
        r = s * (0.95 + 0.05 * math.sin(3 * a + rnd.uniform(0, 1))) * rnd.uniform(0.94, 1.03)
        pts.append((x + r * math.cos(a), y + r * aspect * math.sin(a)))
    c.wash(pts, col, col2, strength=strength, spread=0.07, layers=34, edge=0.8, granulate=0.3, base_depth=4,
           vary=vary or P.get('sky3', '#c4d6ea'), vary_amt=0.35, blooms=blooms, bloom_size=0.09, ang=math.pi / 2)
    for _ in range(drips):
        a = rnd.uniform(0, 2 * math.pi); r = s * rnd.uniform(1.02, 1.22)
        px, py = x + r * math.cos(a), y + r * aspect * math.sin(a)
        rr = s * rnd.uniform(0.004, 0.013)
        c.wash(ellipse(px, py, rr, rr, 9), col, None, strength=strength * rnd.uniform(0.6, 1.1), spread=0.12, layers=8, edge=0.9)


def snowfall(c, x, y, s, P, n=120, aspect=0.82, size=0.006, clear=None):
    """Falling snow: white gouache dots of a few sizes inside the splash
    (so no stray white lands on a colored shirt). clear = list of (x0, y0, x1, y1)
    boxes to keep free (lettering)."""
    rnd = c.rnd
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi); r = s * math.sqrt(rnd.random()) * 0.92
        px, py = x + r * math.cos(a), y + r * aspect * math.sin(a)
        if clear and any(b[0] < px < b[2] and b[1] < py < b[3] for b in clear):
            continue
        rr = s * size * rnd.choice((0.6, 0.8, 1.0, 1.0, 1.4, 1.9))
        gouache(c, ellipse(px, py, rr, rr, 9), color=(255, 255, 255), alpha=rnd.randint(200, 245), soft=0.15)


def far_forest(c, x, y, s, P, n=24, height=0.22, color=None, color2=None):
    """A misty line of distant firs along the horizon: pale blue-green
    silhouettes, softer and bluer than the trees in front (aerial perspective).
    (x, y) = the middle of the horizon line, s = half its length."""
    rnd = c.rnd
    col = color or P.get('far', '#86a6aa'); col2 = color2 or P.get('far2', '#bfd2d4')
    xs = sorted(x - s + 2 * s * (k + rnd.uniform(-0.3, 0.3)) / (n - 1) for k in range(n))
    for px in xs:
        h = s * height * rnd.uniform(0.5, 1.15) * (1 - 0.35 * abs(px - x) / s)
        w = h * rnd.uniform(0.28, 0.36)
        pts = [(px, y - h)]
        for k in range(1, 6):
            t = k / 5
            pts.append((px + w * t * (1.0 if k % 2 else 0.8), y - h * (1 - t) + h * 0.04 * (k % 2)))
        pts.append((px + w, y + h * 0.02))
        pts.append((px - w, y + h * 0.02))
        for k in range(5, 0, -1):
            t = k / 5
            pts.append((px - w * t * (1.0 if k % 2 else 0.8), y - h * (1 - t) + h * 0.04 * (k % 2)))
        c.wash(pts, col2, col, strength=rnd.uniform(0.4, 0.58), spread=0.03, layers=14, edge=0.6, ang=math.pi / 2)
    # a soft band of mist at the foot of the trees
    band = [(x - s * 1.02, y - s * 0.02), (x + s * 1.02, y - s * 0.02), (x + s * 0.98, y + s * 0.035), (x - s * 0.98, y + s * 0.035)]
    c.wash(band, col2, None, strength=0.22, spread=0.05, layers=12, edge=0.2)


def snow_drift(c, x, y, s, P, depth=0.16, tracks=True, color=None):
    """Snowy ground in a watercolor vignette: the paper is the snow, so it is
    painted as blue-grey shadow only, darker in the hollows, a lighter wavy top,
    tyre tracks curving back into the distance. (x, y) = middle of the ground
    line, s = half its width."""
    rnd = c.rnd
    col = color or P.get('shadow', '#9fb4c8')
    top = [(x - s + 2 * s * k / 20, y - s * (0.02 + 0.025 * math.sin(k * 1.1 + rnd.uniform(-0.4, 0.4)))) for k in range(21)]
    bot = [(x + s * 0.9, y + s * depth * 0.7), (x + s * 0.4, y + s * depth), (x - s * 0.4, y + s * depth), (x - s * 0.9, y + s * depth * 0.7)]
    c.wash(smooth(top + bot, 2), col, '#e3ebf1', strength=0.27, spread=0.06, layers=22, edge=0.75, vary='#bfd0e2',
           vary_amt=0.4, ang=-math.pi / 2)
    # hollows and mounds: soft shadow strokes
    for k in range(7):
        px = x + s * rnd.uniform(-0.85, 0.85); py = y + s * rnd.uniform(0.0, depth * 0.6)
        c.wash(ellipse(px, py, s * rnd.uniform(0.08, 0.2), s * rnd.uniform(0.008, 0.018), 12), col, None,
               strength=rnd.uniform(0.12, 0.22), spread=0.08, layers=8, edge=0.4)
    if tracks:
        for off in (0.012, 0.05):
            pts = [(x + s * (0.9 - 1.8 * t), y + s * (off + 0.03 * math.sin(math.pi * t))) for t in [k / 12 for k in range(13)]]
            c.wash(_band(pts, s * 0.006, s * 0.004), col, None, strength=0.22, spread=0.02, layers=8, edge=0.6)


def grass_tufts(c, x, y, s, P, n=9, color=None):
    """Dry winter grass poking through the snow: thin tapered strokes."""
    rnd = c.rnd
    col = color or P.get('grass', '#8a7a52')
    for _ in range(n):
        px = x + s * rnd.uniform(-1, 1)
        for k in range(rnd.randint(3, 6)):
            a = -math.pi / 2 + rnd.uniform(-0.5, 0.5)
            L = s * rnd.uniform(0.06, 0.14)
            c.wash(leaf(px + rnd.uniform(-1, 1) * s * 0.01, y, L, L * 0.05, a), col, '#b9a777', strength=0.55, spread=0.03,
                   layers=6, edge=0.6)


# ---------------------------------------------------------------- spruce
def spruce(c, x, y, s, P, color=None, color2=None, dark=None, snow=0.75, slim=1.0, levels=16, trunk=True, far=False,
           light=-1, lights=None, seed_tilt=0.0):
    """A full spruce, built branch by branch the way a painter does it: a pale
    underwash of the whole cone, then drooping branches from the bottom up,
    each light on top and dark underneath (wet-in-wet), a fringe of dark needle
    strokes along each lower edge, needle texture through the body, a deep
    shadow core by the trunk, lifted light on the sunny side, and lumpy snow
    resting on the branches with a cool shadow under each clump.
    (x, y) = foot of the trunk, s = height. light = -1 lit from the left."""
    rnd = c.rnd
    mid = color or P.get('pine', '#2f6248'); hi = color2 or P.get('pine2', '#7ea56f'); dk = dark or P.get('pine_dark', '#173a2c')
    blue = P.get('pine_blue', '#3f6b78'); warm = P.get('pine_warm', '#a4b35f')
    if far:
        hi, mid, dk = P.get('far2', '#c8d8d8'), P.get('far', '#9db7b4'), '#7f9ea0'

    def env(t):     # half width of the cone at height fraction t (0 = bottom branch, 1 = tip)
        return s * 0.34 * slim * (1 - t) ** 0.92 + s * 0.012

    base_y = y - s * (0.13 if trunk else 0.02)
    top_y = y - s
    if trunk:
        tw = s * 0.032
        c.wash(rect(x - tw, y - s * 0.2, x + tw, y), '#6e4a33', '#93674a', strength=0.85, layers=14, vary='#4a3426', ang=0)
        for k in range(3):
            c.dry_brush([(x - tw * 0.6 + k * tw * 0.6, y - s * 0.19), (x - tw * 0.5 + k * tw * 0.6, y - s * 0.01)], tw * 0.5,
                        '#3d2a1f', strength=0.5, bristles=3, gap=0.5)
    cone = [(x, top_y)]
    for k in range(9):
        t = 1 - k / 8
        cone.append((x + env(t) * 1.02, _lerp(base_y, top_y, t) + s * 0.02))
    for k in range(9):
        t = k / 8
        cone.append((x - env(t) * 1.02, _lerp(base_y, top_y, t) + s * 0.02))
    c.wash(cone, hi, mid, strength=0.34 if not far else 0.3, spread=0.04, layers=22, edge=0.4, vary=blue, vary_amt=0.4,
           ang=math.pi / 2 + 0.4 * light)
    if not far:
        core = [(x, top_y + s * 0.12), (x + env(0.2) * 0.38, base_y - s * 0.05), (x, base_y + s * 0.02), (x - env(0.2) * 0.38, base_y - s * 0.05)]
        c.wash(smooth(core, 1), dk, None, strength=0.5, spread=0.05, layers=14, edge=0.2)
    branches = []
    rows = []
    for i in range(levels):
        t = i / (levels - 1)
        rows.append((t, 1.0))
        if 0.05 < t < 0.85 and rnd.random() < 0.45:
            rows.append((t + 0.5 / (levels - 1), 0.7))
    for (t, scale) in rows:
        by = _lerp(base_y, top_y + s * 0.06, min(1, t) ** 0.95)
        for side in (-1, 1):
            L = env(min(t, 1)) * rnd.uniform(0.78, 1.12) * scale
            if L < s * 0.02:
                continue
            droop = s * (0.03 + 0.06 * (1 - t)) * rnd.uniform(0.7, 1.3)
            lift_ = s * rnd.uniform(0.02, 0.05)
            th = s * (0.048 - 0.024 * t) * rnd.uniform(0.8, 1.2) * (0.85 + 0.15 * scale)
            path = []
            for k in range(9):
                u = k / 8
                path.append((x + side * L * u, by - lift_ * math.sin(math.pi * u * 0.75) + droop * u ** 2.2))
            up, lo = [], []
            for k, (px, py) in enumerate(path):
                u = k / 8
                tk = th * (1 - u) ** 0.5 + s * 0.006
                up.append((px, py - tk * 0.45))
                hang = tk * (0.9 + (0.7 if k % 2 else 0.0)) * rnd.uniform(0.75, 1.25)
                lo.append((px + side * tk * 0.15 * (k % 2), py + hang))
            shape = up + lo[::-1]
            lit = (side == light)
            c.wash(shape, hi if lit else mid, dk, strength=rnd.uniform(0.58, 0.78) if not far else 0.32, spread=0.03, layers=14,
                   edge=0.9, granulate=0.45, vary=warm if lit else blue, vary_amt=0.45, ang=math.pi / 2)
            branches.append((path, th, side, lit, t))
    if not far:
        for (path, th, side, lit, t) in branches:
            for k in range(2, 9):
                if rnd.random() < 0.3:
                    continue
                px, py = path[k]
                a = math.pi / 2 - side * rnd.uniform(0.2, 0.75)
                for _n in range(2):
                    Ln = th * rnd.uniform(0.8, 1.6)
                    c.wash(leaf(px + rnd.uniform(-1, 1) * th * 0.3, py + th * 0.3, Ln, Ln * 0.055, a + rnd.uniform(-0.25, 0.25)),
                           dk if rnd.random() < 0.7 else mid, None, strength=rnd.uniform(0.5, 0.85), spread=0.02, layers=5, edge=0.7,
                           granulate=0.2)
            if lit:
                for k in range(3, 9, 2):
                    px, py = path[k]
                    a = -math.pi / 2 - side * rnd.uniform(0.6, 1.2)
                    Ln = th * rnd.uniform(0.6, 1.0)
                    c.wash(leaf(px, py - th * 0.2, Ln, Ln * 0.07, a), warm, None, strength=0.5, spread=0.02, layers=5, edge=0.6)
        # needle texture through the body of the tree
        for _ in range(int(levels * 12)):
            t = rnd.random() ** 0.8
            py = _lerp(base_y, top_y, t)
            px = x + rnd.uniform(-1, 1) * env(t) * 0.85
            a = math.pi / 2 + (0.6 if px > x else -0.6) + rnd.uniform(-0.4, 0.4)
            Ln = s * rnd.uniform(0.018, 0.035)
            c.wash(leaf(px, py, Ln, Ln * 0.07, a), rnd.choice((dk, dk, mid, blue)), None, strength=rnd.uniform(0.35, 0.6),
                   spread=0.02, layers=4, edge=0.6, granulate=0.2)
        lx = x + light * env(0.4) * 0.45
        c.lift(smooth([(x + light * s * 0.02, top_y + s * 0.15), (lx + light * s * 0.06, _lerp(base_y, top_y, 0.35)),
                       (lx, base_y - s * 0.03), (x + light * s * 0.05, base_y - s * 0.1)], 1), amount=0.16, soft=0.12)
    if snow:
        shadow = P.get('snow_shadow', '#9fb4c8')
        clumps = []
        for (path, th, side, lit, t) in branches:
            if rnd.random() > snow:
                continue
            k0 = rnd.randint(1, 3); k1 = min(8, k0 + rnd.randint(3, 6))
            seg0 = path[k0:k1 + 1]
            if len(seg0) < 2:
                continue
            seg = []
            for j in range(len(seg0) - 1):
                for q in range(4):
                    u = q / 4
                    seg.append((_lerp(seg0[j][0], seg0[j + 1][0], u), _lerp(seg0[j][1], seg0[j + 1][1], u)))
            seg.append(seg0[-1])
            thick = th * rnd.uniform(0.22, 0.5)
            m = len(seg) - 1
            topl = []
            for j, (px, py) in enumerate(seg):
                u = j / m
                bump = math.sin(math.pi * u) ** 0.6 * (1 + 0.25 * math.sin(u * 11 + rnd.uniform(0, 6)))
                topl.append((px, py - th * 0.4 - thick * bump * rnd.uniform(0.88, 1.1)))
            botl = [(px, py - th * 0.18 + thick * 0.3 * math.sin(math.pi * j / m)) for j, (px, py) in enumerate(seg)]
            clumps.append((topl, botl, thick))
            c.wash(smooth([(px, py + thick * 0.25) for px, py in botl] + [(px, py + thick * 0.7) for px, py in botl[::-1]], 1),
                   shadow, None, strength=0.32, spread=0.05, layers=8, edge=0.5)
        for topl, botl, thick in clumps:
            gouache(c, smooth(topl + botl[::-1], 2), color=(253, 253, 252), alpha=244, soft=0.012)
            gouache(c, smooth([(px, py - thick * 0.02) for px, py in botl] + [(px, py - thick * 0.3) for px, py in botl[::-1]], 1),
                    color=(210, 223, 235), alpha=150, soft=0.04)
        gouache(c, smooth([(x - s * 0.025, top_y + s * 0.05), (x, top_y + s * 0.012), (x + s * 0.022, top_y + s * 0.05), (x, top_y + s * 0.06)], 2),
                color=(253, 253, 252), alpha=235, soft=0.08)
    if lights:
        string_lights(c, x, y, s, env, base_y, top_y, P, rows=lights)


def string_lights(c, x, y, s, env, base_y, top_y, P, rows=4):
    """Warm string lights draped across a tree: a dark wire, small bulbs in
    several colors, each with a soft glow and a white glint."""
    rnd = c.rnd
    bulbs = P.get('bulbs', ['#f2c24f', '#e35b4b', '#f6e3a0', '#e9a03b', '#7fb5d6'])
    k = 0
    for j in range(rows):
        t0 = 0.12 + 0.72 * j / max(1, rows)
        t1 = t0 + 0.13
        sgn = 1 if j % 2 == 0 else -1
        pts = []
        for q in range(17):
            u = q / 16
            t = _lerp(t0, t1, u)
            yy = _lerp(base_y, top_y, t)
            pts.append((x + sgn * env(t) * (1 - 2 * u) * 0.92, yy + s * 0.025 * math.sin(math.pi * u)))
        c.ink_line(pts, width=max(1.5, s * 0.004), closed=False, alpha=150, passes=1, jitter=0, color=(30, 46, 36))
        for q in range(1, 16, 2):
            bx, by = pts[q]
            col = bulbs[k % len(bulbs)]; k += 1
            c.glow(bx, by + s * 0.01, s * 0.03, '#f7d77e', strength=0.22)
            gouache(c, ellipse(bx, by + s * 0.012, s * 0.008, s * 0.012, 9), color=_rgb(col), alpha=250, soft=0.06)
            gouache(c, ellipse(bx - s * 0.002, by + s * 0.008, s * 0.003, s * 0.004, 6), color=(255, 252, 238), alpha=230, soft=0.1)


# ---------------------------------------------------------------- vintage pickup
def vintage_truck(c, x, y, s, P, color=None, facing=1, tree=True, snow=True, lights=3, wreath=True):
    """A 1950s stepside pickup in profile: rounded cab, long hood, separate
    bulbous fenders, running board, chrome bumpers, whitewall tyres with
    body-color rims. Glossy paint is built as patchy red washes, shaped
    shadow, lifted highlights along every top curve and gouache glints; a
    fresh-cut spruce with string lights stands in the bed behind the bed wall.
    (x, y) = middle of the ground line, s = half the truck's length, facing 1
    = nose to the right."""
    rnd = c.rnd
    red = color or P.get('truck', '#c0312e')
    red_hi = P.get('truck2', '#e2604c'); red_dk = P.get('truck_dark', '#7e1b20')
    inkc = P.get('truck_ink', (74, 28, 30))
    f = facing

    def T(px, py):
        return (x + f * s * px, y + s * py)

    def poly(pts):
        return [T(px, py) for px, py in pts]
    occ0 = None if c.occl is None else c.occl.copy()
    start = c.snapshot()
    wd = max(1.5, s * 0.008)
    # --- glass first, so the body goes around it
    win = smooth(poly([(-0.15, -0.66), (0.17, -0.66), (0.29, -0.67), (0.22, -0.9), (0.14, -0.94), (-0.12, -0.94), (-0.15, -0.9)]), 1)
    g0 = c.snapshot()
    c.wash(win, '#dce9ee', '#9fbfcc', strength=0.6, spread=0.008, layers=16, edge=0.9, vary='#c9d6e4', ang=math.pi / 2)
    # the steering wheel and seat back seen through the glass
    c.wash(smooth(poly([(-0.14, -0.67), (-0.14, -0.79), (-0.12, -0.83), (-0.07, -0.84), (-0.05, -0.8), (-0.04, -0.67)]), 2), '#7d8f9c',
           None, strength=0.25, layers=10, edge=0.5)
    # reflections: two lifted diagonal streaks
    for a, b in ((-0.08, 0.02), (0.06, 0.1)):
        c.lift(poly([(a, -0.93), (a + 0.05, -0.93), (b + 0.04, -0.67), (b - 0.01, -0.67)]), amount=0.5, soft=0.08)
    c.paint_around(g0)
    # --- the body silhouette in one wash (bed, cab, hood, fender bottoms)
    outline = [(-1.0, -0.36), (-1.0, -0.64), (-0.99, -0.67), (-0.96, -0.68), (-0.25, -0.68), (-0.22, -0.67), (-0.21, -0.66),
               (-0.21, -0.9), (-0.19, -0.97), (-0.12, -1.0), (0.14, -1.0), (0.21, -0.97), (0.33, -0.7),
               (0.38, -0.69), (0.7, -0.665), (0.88, -0.645), (0.96, -0.62), (1.0, -0.57), (1.02, -0.5), (1.035, -0.36),
               (1.03, -0.3), (0.95, -0.29), (0.9, -0.3)]
    # front wheel arch (fender lip), running board line, rear fender
    arc_f = [(0.6 + 0.29 * math.cos(math.pi * k / 10), -0.2 - 0.29 * math.sin(math.pi * k / 10)) for k in range(11)]
    outline += arc_f + [(0.28, -0.3), (0.26, -0.33), (-0.2, -0.33), (-0.24, -0.3)]
    arc_r = [(-0.55 + 0.29 * math.cos(math.pi * k / 10), -0.2 - 0.29 * math.sin(math.pi * k / 10)) for k in range(11)]
    outline += arc_r + [(-0.87, -0.3), (-0.9, -0.34), (-0.97, -0.36)]
    body = smooth(poly(outline), 1)
    c.wash(body, red_hi, red, strength=0.92, spread=0.0025, layers=30, edge=1.0, granulate=0.35, vary=red_dk, vary_amt=0.35,
           ang=math.pi / 2, blur=max(1.0, s * 0.002))
    # shaped shadow wet on dry: lower half of the body, bed side, under the window line
    c.wash(smooth(poly([(-0.99, -0.47), (1.02, -0.45), (1.02, -0.31), (-0.99, -0.34)]), 1), red_dk, None, strength=0.32, spread=0.02,
           layers=12, edge=0.3)
    c.wash(smooth(poly([(-0.2, -0.65), (0.33, -0.66), (0.33, -0.62), (-0.2, -0.61)]), 1), red_dk, None, strength=0.3, layers=8, edge=0.3)
    # the horizon reflected along the doors and the bed side (gloss)
    c.lift(smooth(poly([(-0.97, -0.535), (1.0, -0.515), (1.0, -0.49), (-0.97, -0.51)]), 1), amount=0.22, soft=0.25)
    # the fenders: each a separate panel, darker under its top curve
    fend_f = [(0.3, -0.33), (0.36, -0.5), (0.5, -0.59), (0.72, -0.6), (0.9, -0.55), (1.0, -0.45), (1.03, -0.3)]
    fend_r = [(-0.88, -0.32), (-0.85, -0.47), (-0.72, -0.55), (-0.5, -0.56), (-0.32, -0.5), (-0.23, -0.33)]
    for fen, cx0 in ((fend_f, 0.6), (fend_r, -0.55)):
        inner = [(px, py + 0.04) for px, py in fen[1:-1]]
        c.wash(smooth(poly(fen + [(cx0 + 0.3, -0.25), (cx0 - 0.3, -0.25)]), 1), red_dk, None, strength=0.2, spread=0.02, layers=12, edge=0.5)
        c.lift(smooth(poly(fen[1:-1] + inner[::-1]), 1), amount=0.35, soft=0.03)
        c.ink_line(smooth(poly(fen), 1), width=wd, closed=False, alpha=190, passes=1, jitter=0, color=inkc)
    # long highlights along the roof, the hood and the bed rail (gloss)
    for band in ([(-0.14, -0.985), (0.13, -0.985), (0.16, -0.965), (-0.14, -0.965)],
                 [(0.38, -0.678), (0.86, -0.638), (0.86, -0.62), (0.38, -0.655)],
                 [(-0.96, -0.665), (-0.26, -0.665), (-0.26, -0.645), (-0.96, -0.645)]):
        c.lift(poly(band), amount=0.55, soft=0.2)
    for gx, gy, gw in ((-0.04, -0.982, 0.045), (0.56, -0.66, 0.05)):
        gouache(c, smooth(poly([(gx - gw, gy), (gx + gw, gy - 0.003), (gx + gw, gy + 0.004), (gx - gw, gy + 0.006)]), 1),
                color=(255, 240, 234), alpha=190, soft=0.06)
    c.occl = occ0
    # --- running board
    rb = poly([(0.27, -0.33), (-0.22, -0.33), (-0.24, -0.29), (0.29, -0.29)])
    c.wash(rb, '#3b3437', '#5a5254', strength=0.9, layers=12, edge=0.6)
    # --- wheel wells: the dark inside of each fender above the tyre
    for cx0 in (-0.55, 0.6):
        well = [(cx0 + 0.285 * math.cos(math.pi * k / 12), -0.2 - 0.285 * math.sin(math.pi * k / 12)) for k in range(13)]
        c.wash(smooth(poly(well), 1), '#2b2326', '#4a3134', strength=0.95, spread=0.004, layers=14, edge=0.5, ang=-math.pi / 2)
    # --- wheels: tyre, tread texture, whitewall, red rim, chrome hubcap
    for cx0 in (-0.55, 0.6):
        wx, wy = T(cx0, -0.2)
        R = s * 0.2
        c.wash(ellipse(wx, wy, R, R, 24), '#2f2b2e', '#4f4a4b', strength=1.15, spread=0.006, layers=22, edge=0.6, vary='#1c1a1c')
        for k in range(18):
            a = 2 * math.pi * k / 18
            c.dry_brush([(wx + R * 0.86 * math.cos(a), wy + R * 0.86 * math.sin(a)), (wx + R * 0.98 * math.cos(a + 0.12), wy + R * 0.98 * math.sin(a + 0.12))],
                        R * 0.06, '#151315', strength=0.5, bristles=3, gap=0.4)
        c.lift(smooth([(wx - R * 0.9, wy - R * 0.2), (wx - R * 0.6, wy - R * 0.75), (wx - R * 0.45, wy - R * 0.68), (wx - R * 0.72, wy - R * 0.15)], 1),
               amount=0.3, soft=0.2)
        gouache(c, ellipse(wx, wy, R * 0.66, R * 0.66, 22), color=(243, 240, 233), alpha=245, soft=0.02)
        gouache(c, ellipse(wx, wy, R * 0.5, R * 0.5, 20), color=_rgb(red), alpha=250, soft=0.02)
        gouache(c, crescent_pts(wx, wy, R * 0.5, 0.3, 2.6, R * 0.12), color=_rgb('#8e2226'), alpha=200, soft=0.05)
        gouache(c, ellipse(wx, wy, R * 0.26, R * 0.26, 18), color=(200, 204, 208), alpha=250, soft=0.03)
        gouache(c, ellipse(wx - R * 0.06, wy - R * 0.07, R * 0.12, R * 0.09, 12), color=(244, 246, 248), alpha=235, soft=0.08)
        for k in range(5):
            a = 2 * math.pi * k / 5 + 0.3
            gouache(c, ellipse(wx + R * 0.38 * math.cos(a), wy + R * 0.38 * math.sin(a), R * 0.03, R * 0.03, 6),
                    color=(214, 216, 220), alpha=240, soft=0.05)
        c.ink_line(ellipse(wx, wy, R * 0.66, R * 0.66, 26), width=wd * 0.7, alpha=110, passes=1, jitter=0, color=(90, 88, 90))
        c.ink_line(ellipse(wx, wy, R, R, 28), width=wd, alpha=150, passes=1, jitter=0, color=(25, 22, 24))
    # --- chrome: bumpers, grille edge, trim, headlight, mirror, handle
    def chrome(pts, soft=0.03):
        gouache(c, smooth(poly(pts), 1), color=(176, 182, 190), alpha=248, soft=soft)
    fb = [(0.97, -0.35), (1.09, -0.35), (1.11, -0.31), (1.09, -0.265), (0.97, -0.265)]
    rbm = [(-1.07, -0.41), (-0.95, -0.41), (-0.95, -0.33), (-1.07, -0.33), (-1.085, -0.37)]
    for b in (fb, rbm):
        chrome(b)
        ys = [py for _, py in b]; xs = [px for px, _ in b]
        gouache(c, poly([(min(xs) + 0.01, min(ys) + 0.012), (max(xs) - 0.01, min(ys) + 0.012), (max(xs) - 0.01, min(ys) + 0.026),
                         (min(xs) + 0.01, min(ys) + 0.026)]), color=(246, 248, 250), alpha=235, soft=0.1)
        c.ink_line(smooth(poly(b), 1), width=wd * 0.7, alpha=150, passes=1, jitter=0, color=(80, 84, 92))
    for gy in (-0.54, -0.5, -0.46, -0.42, -0.38):
        chrome([(1.0, gy), (1.04, gy), (1.04, gy + 0.018), (1.0, gy + 0.018)], soft=0.05)
    chrome([(0.4, -0.6), (0.92, -0.565), (0.92, -0.555), (0.4, -0.588)], soft=0.06)
    hx, hy = T(0.93, -0.53)
    gouache(c, ellipse(hx, hy, s * 0.05, s * 0.055, 16), color=(190, 194, 200), alpha=250, soft=0.03)
    gouache(c, ellipse(hx + f * s * 0.008, hy, s * 0.036, s * 0.042, 16), color=(252, 240, 200), alpha=250, soft=0.03)
    gouache(c, ellipse(hx + f * s * 0.014, hy - s * 0.012, s * 0.012, s * 0.012, 8), color=(255, 255, 255), alpha=240, soft=0.1)
    chrome([(0.14, -0.6), (0.21, -0.6), (0.21, -0.585), (0.14, -0.585)], soft=0.05)
    mx, my = T(0.3, -0.77)
    c.ink_line([T(0.27, -0.7), (mx, my)], width=wd * 1.2, closed=False, alpha=200, passes=1, jitter=0, color=(110, 114, 120))
    gouache(c, ellipse(mx, my, s * 0.03, s * 0.035, 12), color=(180, 186, 194), alpha=248, soft=0.04)
    # tail light
    gouache(c, smooth(poly([(-1.0, -0.6), (-0.975, -0.6), (-0.975, -0.53), (-1.0, -0.53)]), 1), color=_rgb('#e04a3a'), alpha=245, soft=0.05)
    # --- pen: silhouette, glass, door, hood seam and vents, bed seams
    c.ink_line(body, width=wd * 1.1, alpha=200, passes=1, jitter=0, color=inkc)
    c.ink_line(win, width=wd, alpha=190, passes=1, jitter=0, color=inkc)
    for seg in ([(-0.17, -0.62), (-0.17, -0.34)], [(0.31, -0.66), (0.29, -0.34)], [(-0.17, -0.62), (0.31, -0.64)],
                [(0.34, -0.68), (0.9, -0.64)], [(-0.96, -0.62), (-0.25, -0.62)], [(-0.25, -0.67), (-0.25, -0.34)]):
        c.ink_line(poly(seg), width=wd * 0.75, closed=False, alpha=150, passes=1, jitter=0, color=inkc)
    for k in range(3):
        vx = 0.6 + 0.06 * k
        c.ink_line(poly([(vx, -0.6), (vx + 0.035, -0.6)]), width=wd * 1.4, closed=False, alpha=140, passes=1, jitter=0, color=inkc)
    c.ink_line(smooth(poly(fb), 1), width=wd * 0.6, alpha=120, passes=1, jitter=0, color=(80, 84, 92))
    # wreath on the cab door
    if wreath:
        wx, wy = T(0.06, -0.5)
        mini_wreath(c, wx, wy, s * 0.075, P)
    # --- snow resting on the roof, hood, fenders and bed rail
    if snow:
        for pts in ([(-0.19, -0.98), (-0.12, -1.035), (0.03, -1.05), (0.15, -1.03), (0.21, -0.98), (0.0, -0.99)],
                    [(0.4, -0.69), (0.55, -0.715), (0.75, -0.7), (0.88, -0.665), (0.7, -0.66), (0.45, -0.675)],
                    [(-0.97, -0.675), (-0.8, -0.7), (-0.6, -0.695), (-0.45, -0.7), (-0.28, -0.68), (-0.6, -0.672)]):
            pp = smooth(poly(pts), 2)
            gouache(c, pp, color=(253, 253, 252), alpha=246, soft=0.008)
            gouache(c, [(px, py + s * 0.004) for px, py in pp[len(pp) // 2:]] + [(px, py - s * 0.004) for px, py in pp[len(pp) // 2:][::-1]],
                    color=(200, 214, 228), alpha=120, soft=0.03)
    # the truck is in front now: the tree goes behind the bed wall and the cab
    c.paint_around(start)
    # a soft cool shadow on the snow under the truck
    c.wash(smooth(poly([(-1.05, -0.02), (-0.6, -0.06), (0.6, -0.06), (1.1, -0.02), (0.6, 0.035), (-0.6, 0.035)]), 2),
           P.get('snow_shadow', '#9fb4c8'), None, strength=0.6, spread=0.04, layers=14, edge=0.5)
    if tree:
        tx, ty = T(-0.6, -0.5)
        spruce(c, tx, ty, s * 1.02, P, snow=0.55, slim=0.92, levels=12, trunk=False, lights=lights, light=-1)
        # twine round the trunk end and a red bow on the tree
        bx, by = T(-0.6, -0.7)
        from motifs import bow
        bow(c, bx + f * s * 0.17, by - s * 0.2, s * 0.06, P, color=P.get('bow', '#b8333a'))
    c.occl = occ0


def crescent_pts(x, y, r, a0, a1, thick, n=14):
    outer = [(x + r * math.cos(a0 + (a1 - a0) * i / n), y + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inner = [(x + (r - thick * math.sin(math.pi * i / n)) * math.cos(a0 + (a1 - a0) * i / n),
              y + (r - thick * math.sin(math.pi * i / n)) * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n, -1, -1)]
    return outer + inner


def mini_wreath(c, x, y, r, P):
    """A small fir wreath with berries and a red bow, hung on a painted door:
    done in opaque gouache, since transparent green over red paint turns brown."""
    rnd = c.rnd
    greens = [_rgb(P.get('pine', '#2f6248')), _rgb(P.get('pine2', '#7ea56f')), _rgb(P.get('pine_dark', '#173a2c')), (74, 122, 86)]
    for k in range(46):
        a = 2 * math.pi * k / 46 + rnd.uniform(-0.08, 0.08)
        rr = r * rnd.uniform(0.85, 1.08)
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        for j in range(3):
            b = a + math.pi / 2 + rnd.uniform(-0.8, 0.8)
            L = r * rnd.uniform(0.26, 0.4)
            gouache(c, leaf(px, py, L, L * 0.13, b), color=rnd.choice(greens), alpha=240, soft=0.03)
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.4
        bx, by = x + r * 0.98 * math.cos(a), y + r * 0.98 * math.sin(a)
        gouache(c, ellipse(bx, by, r * 0.11, r * 0.11, 9), color=_rgb('#d0283a'), alpha=250, soft=0.04)
        gouache(c, ellipse(bx - r * 0.03, by - r * 0.03, r * 0.035, r * 0.035, 6), color=(255, 236, 236), alpha=220, soft=0.1)
    for side in (-1, 1):
        loop = [(x, y + r * 0.95), (x + side * r * 0.25, y + r * 0.65), (x + side * r * 0.5, y + r * 0.72), (x + side * r * 0.45, y + r * 1.05),
                (x + side * r * 0.2, y + r * 1.02)]
        gouache(c, smooth(loop, 2), color=_rgb('#c42a35'), alpha=250, soft=0.03)
        tail = [(x, y + r * 0.98), (x + side * r * 0.18, y + r * 1.4), (x + side * r * 0.08, y + r * 1.42), (x - side * r * 0.02, y + r * 1.05)]
        gouache(c, tail, color=_rgb('#a8202b'), alpha=250, soft=0.03)
    gouache(c, ellipse(x, y + r * 0.95, r * 0.1, r * 0.09, 9), color=_rgb('#8e1a24'), alpha=250, soft=0.04)


# ---------------------------------------------------------------- cozy / bookish
def cozy_glow(c, x, y, s, P, color=None, color2=None, bokeh=14, aspect=0.95):
    """A warm lamplit background: a soft round wash, golden at the centre and
    rose toward the rim, with out-of-focus lights (bokeh) glowing in it."""
    rnd = c.rnd
    col = color or P.get('glow', '#f2d7a4'); col2 = color2 or P.get('glow2', '#efc9bf')
    pts = []
    for k in range(30):
        a = 2 * math.pi * k / 30
        r = s * (0.95 + 0.05 * math.sin(3 * a + rnd.uniform(0, 1))) * rnd.uniform(0.94, 1.03)
        pts.append((x + r * math.cos(a), y + r * aspect * math.sin(a)))
    c.wash(pts, col, col2, strength=0.36, spread=0.07, layers=30, edge=0.7, granulate=0.3, base_depth=4, vary='#f6e6c4', vary_amt=0.4,
           ang=math.pi / 2)
    c.glow(x, y - s * 0.1, s * 0.55, '#f7e2a8', strength=0.25)
    for _ in range(bokeh):
        a = rnd.uniform(0, 2 * math.pi); r = s * 0.85 * math.sqrt(rnd.random())
        bx, by = x + r * math.cos(a), y + r * aspect * math.sin(a)
        rr = s * rnd.uniform(0.025, 0.06)
        c.glow(bx, by, rr * 1.6, rnd.choice(('#f6d58a', '#f3c2a8', '#f8e3a6')), strength=0.18)
        c.wash(ellipse(bx, by, rr, rr, 16), '#f6dca0', None, strength=0.16, spread=0.02, layers=10, edge=1.4)


def twinkle(c, x, y, s, P, color=None, glow=True):
    """A four-point twinkle star in gold with a soft glow."""
    col = color or P.get('star', '#d6a33e')
    pts = []
    for k in range(8):
        a = math.pi / 4 * k - math.pi / 2
        r = s if k % 2 == 0 else s * 0.2
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    if glow:
        c.glow(x, y, s * 0.9, '#f7e3a4', strength=0.2)
    c.wash(smooth(pts, 1), col, P.get('star2', '#f1d27c'), strength=0.9, spread=0.01, layers=12, edge=0.8)


def _book_spine(c, x0, y0, x1, y1, col, rnd, s, P, kind):
    """One book seen from the side: a cloth spine with gold bands and a label,
    or the cream page block between two thin colored boards."""
    hh = y1 - y0; ww = x1 - x0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    dark = P.get('book_shadow', '#3a2a2e')
    gold = _rgb(P.get('gold', '#d8b25a')); gold_dk = _rgb(P.get('gold_dk', '#9c7a2e'))
    if kind == 'pages':
        c.wash(rect(x0, y0, x1, y1), '#f3e7cd', '#e5d3ae', strength=0.55, spread=0.004, layers=14, edge=0.8, ang=math.pi / 2)
        for k in range(1, 6):
            yy = y0 + hh * (0.18 + 0.64 * k / 6)
            c.ink_line([(x0 + ww * 0.02, yy), (x1 - ww * 0.02, yy + rnd.uniform(-1, 1) * hh * 0.02)], width=max(1, hh * 0.012),
                       closed=False, alpha=70, passes=1, jitter=0, color=(150, 120, 90))
        for (a, b) in ((y0 - hh * 0.06, y0 + hh * 0.12), (y1 - hh * 0.12, y1 + hh * 0.02)):
            c.wash(rect(x0 - ww * 0.012, a, x1 + ww * 0.012, b), col, None, strength=0.85, spread=0.004, layers=12, edge=0.9, vary=dark,
                   vary_amt=0.25)
        c.ink_line(rect(x0 - ww * 0.012, y0 - hh * 0.06, x1 + ww * 0.012, y1 + hh * 0.02), width=max(1.5, s * 0.0035), alpha=150,
                   passes=1, jitter=0, color=(50, 36, 38))
        return
    c.wash(rect(x0, y0, x1, y1), col, None, strength=0.86, spread=0.004, layers=22, edge=1.0, granulate=0.45, vary=dark, vary_amt=0.3)
    # round spine: shade underneath, lifted light along the top
    c.wash(rect(x0, y1 - hh * 0.35, x1, y1), dark, None, strength=0.25, spread=0.01, layers=10, edge=0.3)
    c.lift(rect(x0 + ww * 0.01, y0 + hh * 0.1, x1 - ww * 0.01, y0 + hh * 0.28), amount=0.35, soft=0.05)
    style = rnd.choice(('bands', 'label', 'bands_label', 'dots'))
    if style in ('bands', 'bands_label'):
        for bx in (x0 + ww * rnd.uniform(0.08, 0.12), x1 - ww * rnd.uniform(0.08, 0.12)):
            for off in (-0.022, 0.022):
                gouache(c, rect(bx + ww * off - hh * 0.035, y0 + hh * 0.08, bx + ww * off + hh * 0.035, y1 - hh * 0.08), color=gold, alpha=235,
                        soft=0.01)
    if style in ('label', 'bands_label'):
        lw = ww * rnd.uniform(0.18, 0.28)
        lx = cx + ww * rnd.uniform(-0.12, 0.12)
        lab = rect(lx - lw / 2, y0 + hh * 0.26, lx + lw / 2, y1 - hh * 0.26)
        if rnd.random() < 0.5:
            gouache(c, lab, color=(36, 30, 34), alpha=200, soft=0.01)
        else:
            gouache(c, lab, color=(242, 230, 204), alpha=230, soft=0.01)
        c.ink_line(lab, width=max(1.2, hh * 0.03), alpha=220, passes=1, jitter=0, color=gold)
        for k in range(2):
            yy = y0 + hh * (0.43 + 0.14 * k)
            c.ink_line([(lx - lw * 0.32, yy), (lx + lw * (0.32 - 0.2 * k), yy)], width=max(1, hh * 0.035), closed=False, alpha=200,
                       passes=1, jitter=0, color=gold_dk if k else gold)
    if style == 'dots':
        for k in range(5):
            gouache(c, ellipse(x0 + ww * (0.2 + 0.15 * k), cy, hh * 0.07, hh * 0.07, 8), color=gold, alpha=230, soft=0.04)
    c.ink_line(rect(x0, y0, x1, y1), width=max(1.5, s * 0.0035), alpha=165, passes=1, jitter=0, color=(44, 32, 36))


def book_tree2(c, x, y, s, P, rows=11, lights=5, star=True, colors=None):
    """A Christmas tree of stacked books, painted book by book: cloth spines in
    deep red, forest green, navy, gold and plum with gold bands and labels,
    some books turned to show their cream page edges, each a little off-line,
    a garland of warm string lights spiralling round it and a glowing gold
    star on top. (x, y) = middle of the bottom edge, s = height."""
    rnd = c.rnd
    cols = colors or [P.get('book1', '#8b2333'), P.get('book2', '#2c5b43'), P.get('book3', '#c99a3c'), P.get('book4', '#2a4466'),
                      P.get('book5', '#a8433a'), P.get('book6', '#6f8f6a'), P.get('book7', '#5b3352')]
    h = s * 0.84 / rows
    books = []
    last = None
    for i in range(rows):
        t = i / max(1, rows - 1)
        hw = s * (0.36 - 0.3 * t) * rnd.uniform(0.94, 1.05)
        off = s * rnd.uniform(-0.02, 0.02)
        y1 = y - i * h; y0 = y1 - h * rnd.uniform(0.82, 0.95)
        kind = 'pages' if (i % 3 == 1 and rnd.random() < 0.85) else 'spine'
        col = rnd.choice([cc for cc in cols if cc != last]); last = col
        # wide rows are sometimes two books side by side
        if hw > s * 0.18 and kind == 'spine' and rnd.random() < 0.55:
            split = x + off + hw * rnd.uniform(-0.25, 0.25)
            col2 = rnd.choice([cc for cc in cols if cc != col])
            books.append((x - hw + off, y0, split, y1, col, 'spine'))
            books.append((split, y0 + h * rnd.uniform(0.0, 0.12), x + hw + off, y1, col2, 'spine'))
        else:
            books.append((x - hw + off, y0, x + hw + off, y1, col, kind))
    for (x0, y0, x1, y1, col, kind) in books:
        _book_spine(c, x0, y0, x1, y1, col, rnd, s, P, kind)
    top_y = y - rows * h
    # string lights: the wire loops across the front, row to row
    if lights:
        bulbs = P.get('bulbs', ['#f2c24f', '#e35b4b', '#f6e3a0', '#e9a03b', '#7fb5d6', '#e88aa0'])
        k = 0
        for j in range(lights):
            ya = 0.08 + 0.8 * j / lights; yb = ya + 0.8 / lights * 0.85
            sgn = 1 if j % 2 == 0 else -1
            pts = []
            for q in range(21):
                u = q / 20
                hh = _lerp(ya, yb, u)
                yy = y - s * hh * 0.84
                ww = s * (0.36 - 0.3 * min(1, hh / 0.84)) * 1.05
                pts.append((x + sgn * ww * (1 - 2 * u), yy + s * 0.018 * math.sin(math.pi * u)))
            c.ink_line(pts, width=max(1.5, s * 0.0035), closed=False, alpha=170, passes=1, jitter=0, color=(36, 52, 40))
            for q in range(1, 20, 2):
                bx, by = pts[q]
                col = bulbs[k % len(bulbs)]; k += 1
                c.glow(bx, by + s * 0.012, s * 0.035, '#f8d982', strength=0.3)
                gouache(c, ellipse(bx, by + s * 0.013, s * 0.0085, s * 0.013, 10), color=_rgb(col), alpha=252, soft=0.05)
                gouache(c, ellipse(bx - s * 0.002, by + s * 0.009, s * 0.003, s * 0.004, 6), color=(255, 253, 240), alpha=235, soft=0.1)
                gouache(c, rect(bx - s * 0.004, by - s * 0.001, bx + s * 0.004, by + s * 0.004), color=(70, 74, 60), alpha=230, soft=0.02)
    if star:
        sy = top_y - s * 0.07
        c.glow(x, sy, s * 0.16, '#f8dd8c', strength=0.45)
        for k in range(8):
            a = math.pi / 4 * k + math.pi / 8
            if math.sin(a) > 0.3:   # no rays down into the top book
                continue
            c.ink_line([(x + s * 0.1 * math.cos(a), sy + s * 0.1 * math.sin(a)), (x + s * 0.15 * math.cos(a), sy + s * 0.15 * math.sin(a))],
                       width=max(1.5, s * 0.004), closed=False, alpha=150, passes=1, jitter=0, color=(214, 170, 70))
        st = _star_pts(x, sy, s * 0.085, s * 0.036)
        c.wash(st, P.get('star', '#d39e35'), P.get('star2', '#f3d679'), strength=1.0, spread=0.006, layers=18, edge=1.0,
               vary='#b07d22', vary_amt=0.3, ang=math.pi / 2)
        c.lift(_star_pts(x - s * 0.012, sy - s * 0.012, s * 0.04, s * 0.016), amount=0.35, soft=0.1)
        c.ink_line(st, width=max(1.5, s * 0.004), alpha=170, passes=1, jitter=0, color=(130, 92, 30))


def gift2(c, x, y, s, P, color=None, ribbon=None, pattern=None, tall=1.0, angle=0.0):
    """A wrapped present: patchy paper with a printed pattern (stripes, dots
    or stars) in opaque paint, a satin ribbon both ways with a highlight, and
    a full bow with shaded loops and notched tails. (x, y) = middle of the
    bottom edge, s = half the width."""
    rnd = c.rnd
    col = color or P.get('gift', '#2c5b43'); rib = _rgb(ribbon or P.get('ribbon', '#d8b25a'))
    pattern = pattern or rnd.choice(('stripes', 'dots', 'stars'))
    H = s * 1.3 * tall

    def R(pts):
        return _rot(pts, x, y, angle)
    box = R(rect(x - s, y - H, x + s, y))
    c.wash(box, col, None, strength=0.85, spread=0.004, layers=22, edge=1.0, vary=P.get('book_shadow', '#3a2a2e'), vary_amt=0.25)
    c.wash(R(rect(x + s * 0.35, y - H, x + s, y)), P.get('book_shadow', '#3a2a2e'), None, strength=0.2, layers=10, edge=0.3)
    deco = (246, 236, 214) if pattern != 'stars' else _rgb(P.get('gold', '#d8b25a'))
    if pattern == 'stripes':
        for k in range(-6, 7):
            px = x + k * s * 0.22
            gouache(c, R([(px - s * 0.035, y - H), (px + s * 0.035, y - H), (px + s * 0.035 + s * 0.12, y), (px - s * 0.035 + s * 0.12, y)]),
                    color=deco, alpha=170, soft=0.01) if abs(k * 0.22) <= 0.85 else None
    elif pattern == 'dots':
        for i in range(5):
            for j in range(int(5 * tall) + 1):
                px = x - s * 0.8 + i * s * 0.4 + (s * 0.2 if j % 2 else 0); py = y - H * 0.1 - j * s * 0.3
                if abs(px - x) < s * 0.9 and py > y - H * 0.95:
                    gouache(c, R(ellipse(px, py, s * 0.05, s * 0.05, 8)), color=deco, alpha=215, soft=0.04)
    else:
        for i in range(4):
            for j in range(int(4 * tall) + 1):
                px = x - s * 0.7 + i * s * 0.47 + (s * 0.23 if j % 2 else 0); py = y - H * 0.15 - j * s * 0.36
                if abs(px - x) < s * 0.9 and py > y - H * 0.9:
                    gouache(c, R(_star_pts(px, py, s * 0.08, s * 0.035)), color=deco, alpha=225, soft=0.02)
    # lid
    lid = R(rect(x - s * 1.06, y - H - s * 0.14, x + s * 1.06, y - H + s * 0.1))
    c.wash(lid, col, None, strength=0.95, spread=0.004, layers=16, edge=1.0)
    c.wash(R(rect(x - s * 1.06, y - H + s * 0.04, x + s * 1.06, y - H + s * 0.1)), P.get('book_shadow', '#3a2a2e'), None, strength=0.3, layers=8)
    # ribbon with a satin highlight
    rw = s * 0.13
    gouache(c, R(rect(x - rw, y - H - s * 0.14, x + rw, y)), color=rib, alpha=248, soft=0.01)
    gouache(c, R(rect(x - rw * 0.35, y - H - s * 0.14, x - rw * 0.05, y)), color=tuple(min(255, v + 45) for v in rib), alpha=200, soft=0.03)
    dk = tuple(int(v * 0.72) for v in rib)
    for side in (-1, 1):
        loop = [(x, y - H - s * 0.12), (x + side * s * 0.3, y - H - s * 0.62), (x + side * s * 0.72, y - H - s * 0.6),
                (x + side * s * 0.7, y - H - s * 0.3), (x + side * s * 0.25, y - H - s * 0.14)]
        gouache(c, R(smooth(loop, 2)), color=rib, alpha=248, soft=0.02)
        inner = [(x + side * s * 0.12, y - H - s * 0.2), (x + side * s * 0.35, y - H - s * 0.48), (x + side * s * 0.55, y - H - s * 0.42),
                 (x + side * s * 0.3, y - H - s * 0.22)]
        gouache(c, R(smooth(inner, 2)), color=dk, alpha=200, soft=0.04)
        tail = [(x, y - H - s * 0.1), (x + side * s * 0.28, y - H + s * 0.3), (x + side * s * 0.2, y - H + s * 0.36),
                (x + side * s * 0.12, y - H + s * 0.28), (x + side * s * 0.03, y - H + s * 0.34)]
        gouache(c, R(tail), color=rib, alpha=245, soft=0.02)
    gouache(c, R(ellipse(x, y - H - s * 0.13, s * 0.11, s * 0.09, 10)), color=dk, alpha=250, soft=0.03)
    c.ink_line(box, width=max(1.5, s * 0.025), alpha=150, passes=1, jitter=0, color=(44, 32, 36))
    c.ink_line(lid, width=max(1.5, s * 0.025), alpha=150, passes=1, jitter=0, color=(44, 32, 36))


def cozy_cat(c, x, y, s, P, scarf=None, tail=1):
    """The sitting black cat (motifs.cat) with soft fur strokes, a lifted
    sheen on the head and back, and a red knitted scarf with cream stripes."""
    from motifs import cat
    cat(c, x, y, s, P, tail=tail)
    rnd = c.rnd
    for _ in range(40):
        px = x + s * rnd.uniform(-0.45, 0.45); py = y + s * rnd.uniform(0.15, 1.0)
        a = math.pi / 2 + rnd.uniform(-0.5, 0.5) + (0.3 if px > x else -0.3)
        c.dry_brush([(px, py), (px + s * 0.06 * math.cos(a), py + s * 0.06 * math.sin(a))], s * 0.02, '#1c1822', strength=0.35, bristles=3,
                    gap=0.45)
    c.lift(smooth([(x - s * 0.3, y - s * 0.4), (x - s * 0.1, y - s * 0.5), (x - s * 0.05, y - s * 0.42), (x - s * 0.28, y - s * 0.3)], 1),
           amount=0.25, soft=0.15)
    col = _rgb(scarf or P.get('scarf', '#b8303a')); dk = tuple(int(v * 0.72) for v in col)
    band = smooth([(x - s * 0.36, y - s * 0.02), (x, y + s * 0.07), (x + s * 0.36, y - s * 0.02), (x + s * 0.34, y + s * 0.12),
                   (x, y + s * 0.2), (x - s * 0.34, y + s * 0.12)], 2)
    gouache(c, band, color=col, alpha=250, soft=0.01)
    tailp = smooth([(x + s * 0.12, y + s * 0.12), (x + s * 0.27, y + s * 0.1), (x + s * 0.3, y + s * 0.55), (x + s * 0.16, y + s * 0.57)], 1)
    gouache(c, tailp, color=dk, alpha=250, soft=0.01)
    for k in range(3):
        yy = y + s * (0.22 + 0.11 * k)
        gouache(c, [(x + s * 0.18, yy), (x + s * 0.285, yy - s * 0.005), (x + s * 0.29, yy + s * 0.035), (x + s * 0.185, yy + s * 0.04)],
                color=(244, 232, 210), alpha=235, soft=0.02)
    for k in range(4):
        fx = x + s * (0.17 + 0.035 * k)
        c.ink_line([(fx, y + s * 0.56), (fx, y + s * 0.63)], width=max(1.5, s * 0.012), closed=False, alpha=230, passes=1, jitter=0, color=dk)
    for k in range(9):
        u = -0.3 + 0.6 * k / 8
        px = x + s * u; py = y + s * (0.07 + 0.09 * (1 - (u / 0.34) ** 2) * 0.5)
        c.ink_line([(px, py), (px + s * 0.02, py + s * 0.08)], width=max(1, s * 0.008), closed=False, alpha=110, passes=1, jitter=0, color=dk)


def base_garland(c, x, y, s, P, cones=3, baubles=4):
    """Pine sprigs, pinecones and a few small glass baubles lying along the
    floor line at the foot of the tree. s = half the length."""
    from motifs import pine_bough, pinecone
    rnd = c.rnd
    for k in range(5):
        px = x - s + 2 * s * (k + 0.5) / 5
        pine_bough(c, px, y - s * 0.02, s * 0.2, dict(P, leaf=P.get('pine', '#2c5b43'), leaf2=P.get('pine2', '#7aa36c'),
                   leaf_dark=P.get('pine_dark', '#163829')), angle=rnd.uniform(-0.2, 0.2) + (0.08 if k % 2 else -0.08), bend=0.2,
                   snow=False, twigs=2)
    for k in range(cones):
        pinecone(c, x + s * rnd.uniform(-0.8, 0.8), y - s * 0.02, s * 0.07, P, angle=rnd.uniform(1.2, 1.9))
    cols = [P.get('book1', '#8b2333'), P.get('book3', '#c99a3c'), P.get('book4', '#2a4466'), P.get('scarf', '#b8303a')]
    for k in range(baubles):
        bx = x + s * (-0.75 + 1.5 * (k + rnd.uniform(0.2, 0.8)) / baubles)
        r = s * rnd.uniform(0.045, 0.06)
        mini_bauble(c, bx, y - r * 0.9, r, cols[k % len(cols)], P)


def mini_bauble(c, x, y, r, col, P):
    """A small glass ball: deep color, a darker rim, a window highlight, gold cap."""
    c.wash(ellipse(x, y, r, r, 20), col, None, strength=0.95, spread=0.006, layers=18, edge=1.3, vary=P.get('book_shadow', '#3a2a2e'),
           vary_amt=0.3)
    c.lift(ellipse(x - r * 0.3, y - r * 0.35, r * 0.32, r * 0.22, 12, -0.6), amount=0.6, soft=0.15)
    gouache(c, ellipse(x - r * 0.38, y - r * 0.4, r * 0.1, r * 0.07, 8, -0.6), color=(255, 255, 255), alpha=235, soft=0.08)
    gouache(c, rect(x - r * 0.22, y - r * 1.18, x + r * 0.22, y - r * 0.9), color=_rgb(P.get('gold', '#d8b25a')), alpha=245, soft=0.02)
    c.ink_line(ellipse(x, y, r, r, 22), width=max(1, r * 0.03), alpha=120, passes=1, jitter=0, color=(50, 36, 40))



# ---------------------------------------------------------------- glass ornaments
def _shade(hexcol, k):
    r, g, b = _rgb(hexcol)
    return '#%02x%02x%02x' % (int(r * k), int(g * k), int(b * k))


GLASS_SHAPES = {
    'finial': [(0.0, -1.0), (0.12, -0.96), (0.2, -0.86), (0.3, -0.72), (0.55, -0.46), (0.72, -0.13), (0.7, 0.17), (0.52, 0.44),
               (0.3, 0.61), (0.2, 0.72), (0.23, 0.8), (0.15, 0.89), (0.08, 1.08), (0.03, 1.3), (0.0, 1.4)],
    'teardrop': [(0.0, -1.0), (0.28, -0.86), (0.58, -0.47), (0.78, 0.02), (0.74, 0.48), (0.5, 0.84), (0.22, 1.02), (0.0, 1.06)],
}


def glass_bauble(c, x, y, s, P, color=None, color2=None, kind='round', deco=None, angle=0.0, hang=0.0, ribbon=None, deco_color=None):
    """A vintage glass ornament painted like glass: light wet-in-wet into the
    deep color (lit from the upper left), a shadow core on the far side, bounce
    light along the lower rim, a lifted window reflection and a crisp white
    glint, hand-painted decoration (gold bands with a zigzag, frosted
    snowflakes, cream stripes, gold stars or glitter), and a ridged gold cap
    with its wire loop, optionally hung from a ribbon. s = the ball's radius."""
    rnd = c.rnd
    col = color or P.get('main', '#8e2b3a'); col2 = color2 or P.get('main2', '#c45a64')
    deep = _shade(col, 0.55)
    gold = P.get('cap', '#d6a84a')
    gold_rgb = _rgb(deco_color or gold); gold_dk = _rgb(_shade(deco_color or gold, 0.6))
    deco = deco or rnd.choice(('gold_bands', 'frost', 'stripes', 'stars', 'glitter'))

    def R(pts):
        return _rot(pts, x, y, angle)
    if kind in GLASS_SHAPES:
        half = GLASS_SHAPES[kind]
        shape = smooth([(x + s * px, y + s * py) for px, py in half] + [(x - s * px, y + s * py) for px, py in reversed(half[1:-1])], 2)
        ytop = y - s * 1.0
    else:
        shape = ellipse(x, y, s, s, 36)
        ytop = y - s * 0.98
    c.wash(R(shape), col2, col, strength=0.92, spread=0.003, layers=26, edge=1.25, granulate=0.35, vary=deep, vary_amt=0.35,
           ang=math.pi / 4 + angle, blur=max(1.0, s * 0.006))
    body = R(shape)
    if kind in GLASS_SHAPES:
        # shadow core: the shape again, nudged down-right, kept inside the glass
        c.wash(R([(px + s * 0.22, py + s * 0.12) for px, py in shape]), deep, None, strength=0.36, spread=0.02, layers=12, edge=0.3, clip=body)
    else:
        c.wash(R(crescent_pts(x, y + s * 0.05, s * 0.95, -0.35, 1.95, s * 0.5)), deep, None, strength=0.38, spread=0.02, layers=12, edge=0.3,
               clip=body)
        c.lift(R(crescent_pts(x, y, s * 0.93, 0.25, 1.45, s * 0.12)), amount=0.35, soft=0.12, clip=body)

    def hw(py):    # half width of the glass at height py (canvas px)
        if kind not in GLASS_SHAPES:
            v = (py - y) / s
            return s * math.sqrt(max(0.0, 1 - v * v))
        v = (py - y) / s
        pts = GLASS_SHAPES[kind]
        for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
            if b0 <= v <= b1:
                return s * (a0 + (a1 - a0) * (v - b0) / max(1e-6, b1 - b0))
        return 0.0
    if kind in GLASS_SHAPES and deco not in ('gold_bands', 'stars', 'frost'):
        deco = 'gold_bands'
    # decoration
    if deco == 'gold_bands':
        for dy in (-0.2, 0.22):
            half_w = hw(y + s * (dy + 0.03)) / s * 0.97
            top = [(x + s * half_w * u, y + s * (dy + 0.07 * (1 - u * u))) for u in [-1 + 2 * k / 16 for k in range(17)]]
            band = top + [(px, py + s * 0.055) for px, py in top[::-1]]
            gouache(c, R(band), color=gold_rgb, alpha=235, soft=0.01)
            c.ink_line(R(top), width=max(1, s * 0.008), closed=False, alpha=120, passes=1, jitter=0, color=gold_dk)
        zz = []
        zw = hw(y + s * 0.02) / s * 0.9
        for k in range(15):
            u = -zw + 2 * zw * k / 14
            zz.append((x + s * u, y + s * (0.01 + (0.09 if k % 2 else -0.06) + 0.07 * (1 - u * u))))
        c.ink_line(R(zz), width=max(1.5, s * 0.025), closed=False, alpha=235, passes=1, jitter=0, color=gold_rgb)
        dw = hw(y - s * 0.33) / s * 0.8
        for k in range(6):
            u = -dw + 2 * dw * k / 5
            gouache(c, R(ellipse(x + s * u, y + s * (-0.33 + 0.06 * (1 - u * u)), s * 0.035, s * 0.035, 8)), color=gold_rgb, alpha=230, soft=0.05)
    elif deco == 'frost':
        for (fx, fy, fr) in ((-0.25, 0.1, 0.24), (0.3, -0.25, 0.16), (0.32, 0.38, 0.13), (-0.42, -0.35, 0.1)):
            cx0, cy0 = x + fx * hw(y + s * fy) * 0.95, y + s * fy
            fr = min(fr, hw(cy0) / s * 0.4)
            for k in range(6):
                a = math.pi / 3 * k
                ex, ey = cx0 + s * fr * math.cos(a), cy0 + s * fr * math.sin(a)
                c.ink_line(R([(cx0, cy0), (ex, ey)]), width=max(1.5, s * 0.02), closed=False, alpha=215, passes=1, jitter=0, color=(250, 248, 244))
                for side in (-1, 1):
                    mx, my = cx0 + s * fr * 0.6 * math.cos(a), cy0 + s * fr * 0.6 * math.sin(a)
                    b = a + side * 0.7
                    c.ink_line(R([(mx, my), (mx + s * fr * 0.3 * math.cos(b), my + s * fr * 0.3 * math.sin(b))]), width=max(1, s * 0.014),
                               closed=False, alpha=200, passes=1, jitter=0, color=(250, 248, 244))
        for _ in range(14):
            a = rnd.uniform(0, 2 * math.pi); r = s * 0.85 * math.sqrt(rnd.random())
            gouache(c, R(ellipse(x + r * math.cos(a), y + r * math.sin(a), s * 0.018, s * 0.018, 6)), color=(250, 248, 244), alpha=200, soft=0.1)
    elif deco == 'stripes':
        for a_k in (-0.72, -0.38, 0.0, 0.38, 0.72):
            pts = [(x + s * a_k * math.cos(t), y + s * 0.97 * math.sin(t)) for t in [-math.pi / 2 + math.pi * k / 20 for k in range(21)]]
            band = [(px - s * 0.03 * math.cos(math.asin(max(-1, min(1, (py - y) / s)))), py) for px, py in pts]
            band += [(px + s * 0.03 * math.cos(math.asin(max(-1, min(1, (py - y) / s)))), py) for px, py in pts[::-1]]
            gouache(c, R(band), color=(244, 234, 214), alpha=175, soft=0.02)
    elif deco == 'stars':
        for (fx, fy, fr) in ((-0.3, -0.2, 0.15), (0.25, -0.38, 0.1), (0.35, 0.15, 0.13), (-0.15, 0.4, 0.11), (0.05, 0.02, 0.09), (-0.55, 0.15, 0.08)):
            w_here = hw(y + s * fy) / s
            if w_here < 0.2:
                continue
            fr = min(fr, w_here * 0.35)
            gouache(c, R(_star_pts(x + s * fx * w_here, y + s * fy, s * fr, s * fr * 0.42, angle=rnd.uniform(-0.3, 0.3))), color=gold_rgb,
                    alpha=240, soft=0.01)
    elif deco == 'glitter':
        for _ in range(90):
            u = rnd.uniform(-0.95, 0.95); v = rnd.gauss(0, 0.09)
            py = y + s * (v + 0.06 * (1 - u * u)); px = x + s * u * math.sqrt(max(0, 1 - ((py - y) / s) ** 2))
            gouache(c, R(ellipse(px, py, s * 0.012, s * 0.012, 5)), color=gold_rgb if rnd.random() < 0.8 else (255, 250, 236), alpha=235, soft=0.05)
    # window reflection and glints
    c.lift(R(crescent_pts(x, y, s * (0.62 if kind in GLASS_SHAPES else 0.8), math.pi * 1.08, math.pi * 1.4, s * 0.2)), amount=0.62,
           soft=0.05, clip=body)
    gouache(c, R(ellipse(x - s * 0.47, y - s * 0.42, s * 0.075, s * 0.05, 10, -0.7)), color=(255, 255, 255), alpha=240, soft=0.04)
    gouache(c, R(ellipse(x - s * 0.3, y - s * 0.6, s * 0.03, s * 0.022, 8, -0.7)), color=(255, 255, 255), alpha=220, soft=0.06)
    c.ink_line(R(shape), width=max(1, s * 0.012), alpha=90, passes=1, jitter=0, color=(50, 32, 36))
    # ridged gold cap and wire loop
    cw = s * (0.17 if kind == 'finial' else 0.2)
    capb = R(rect(x - cw, ytop - s * 0.2, x + cw, ytop + s * 0.04))
    c.wash(capb, P.get('cap2', '#f0d58c'), gold, strength=1.0, spread=0.003, layers=14, edge=1.0, ang=angle, vary=_shade(gold, 0.7), vary_amt=0.3)
    for k in range(5):
        rx = x - cw + cw * 2 * (k + 0.5) / 5
        c.ink_line(R([(rx, ytop - s * 0.18), (rx, ytop + s * 0.02)]), width=max(1, s * 0.012), closed=False, alpha=150, passes=1, jitter=0,
                   color=gold_dk)
    gouache(c, R(rect(x - cw * 0.7, ytop - s * 0.17, x - cw * 0.45, ytop + s * 0.01)), color=(252, 240, 200), alpha=200, soft=0.05)
    c.ink_line(R(ellipse(x, ytop - s * 0.29, s * 0.07, s * 0.09, 12)), width=max(1.5, s * 0.022), alpha=200, passes=1, jitter=0,
               color=(140, 120, 80))
    if hang:
        top = (x, ytop - s * 0.38 - s * hang)
        rib = ribbon or P.get('bow', '#b8333a')
        c.wash(_rot(_band([(x, ytop - s * 0.36), (x + s * 0.02, ytop - s * 0.36 - s * hang * 0.5), top], s * 0.022, s * 0.02), x, y, angle),
               rib, None, strength=0.85, spread=0.01, layers=10, edge=0.8)
        from motifs import bow
        tx, ty = _rot([top], x, y, angle)[0]
        bow(c, tx, ty, s * 0.2, P, color=rib, angle=angle)


# ---------------------------------------------------------------- winter birth flowers
def narcissus(c, x, y, s, P, angle=0.0, stem=1.0):
    """A paperwhite narcissus (December's birth flower): six pale petals shaded
    blue-grey at the base so white reads on white, a small golden cup with a
    darker rim, on a green stem with a strap leaf. (x, y) = flower centre, s = petal length."""
    rnd = c.rnd
    g1, g2 = P.get('leaf', '#5f8f62'), P.get('leaf2', '#a9c79a')
    if stem:
        st = [(x, y), (x + s * 0.15, y + s * 1.2 * stem), (x + s * 0.1, y + s * 2.6 * stem)]
        c.wash(_band(st, s * 0.07, s * 0.06), g2, g1, strength=0.7, layers=10, edge=0.8)
        lf = [(x + s * 0.2, y + s * 2.5 * stem), (x + s * 0.55, y + s * 1.5 * stem), (x + s * 0.75, y + s * 0.6 * stem)]
        c.wash(_band(lf, s * 0.12, s * 0.02), g2, g1, strength=0.65, layers=10, edge=0.8, vary=g1)
    for k in range(6):
        a = angle + k * math.pi / 3 + rnd.uniform(-0.08, 0.08)
        pt = petal_pts(x, y, s, s * 0.42, a)
        c.wash(pt, '#f4f1e8', '#c9d3dc', strength=0.55, spread=0.02, layers=14, edge=1.3, ang=a + math.pi)
        c.wash(petal_pts(x, y, s * 0.45, s * 0.22, a), '#b8c4cf', None, strength=0.25, spread=0.03, layers=8, edge=0.4)
    c.wash(ellipse(x, y, s * 0.28, s * 0.28, 16), P.get('cup', '#f0b93a'), P.get('cup2', '#f7dc85'), strength=0.9, layers=16, edge=1.2,
           vary='#d98f2b', vary_amt=0.4)
    c.wash(ellipse(x, y, s * 0.12, s * 0.12, 10), '#d98f2b', None, strength=0.7, layers=10, edge=1.0)
    gouache(c, ellipse(x - s * 0.07, y - s * 0.07, s * 0.04, s * 0.03, 8), color=(255, 248, 220), alpha=220, soft=0.1)


def petal_pts(cx, cy, length, width, angle, n=14):
    from watercolor import petal
    return petal(cx, cy, length, width, angle, n)


def snowdrop(c, x, y, s, P, facing=1):
    """A snowdrop (January's flower): an arching stem with a drooping bell of
    three pale outer petals, a green-tipped inner cup, and two grey-green leaves.
    (x, y) = the base of the stem, s = its height."""
    g1, g2 = P.get('leaf', '#5f8f62'), P.get('leaf2', '#a9c79a')
    f = facing
    st = [(x, y), (x + f * s * 0.05, y - s * 0.5), (x + f * s * 0.2, y - s * 0.92), (x + f * s * 0.36, y - s * 0.86)]
    c.wash(_band(st, s * 0.022, s * 0.016), g2, g1, strength=0.75, layers=10, edge=0.8)
    for side in (-1, 1):
        lf = [(x, y), (x + side * s * 0.1, y - s * 0.35), (x + side * s * 0.16, y - s * 0.6)]
        c.wash(_band(lf, s * 0.05, s * 0.01), '#9fb8a0', g1, strength=0.6, layers=10, edge=0.8)
    bx, by = x + f * s * 0.38, y - s * 0.72      # bell hangs from the stem tip
    c.wash(ellipse(bx, by - s * 0.1, s * 0.035, s * 0.05, 8), g1, None, strength=0.8, layers=8)
    for a, L in ((-0.35, 0.3), (0.35, 0.3), (0.0, 0.32)):
        pt = petal_pts(bx, by - s * 0.07, s * L, s * 0.11, math.pi / 2 + a)
        c.wash(pt, '#f4f1e8', '#c4cfda', strength=0.5, spread=0.02, layers=12, edge=1.4, ang=-math.pi / 2)
    c.wash(ellipse(bx, by + s * 0.1, s * 0.05, s * 0.035, 10), '#8fbf7a', None, strength=0.7, layers=10, edge=1.0)



def night_sky2(c, x, y, s, P, stars=70):
    """A round watercolor night sky painted richly: deep blue wet-in-wet with
    patches drifting to violet, a lifted Milky Way band across it, soft nebula
    tints, and white gouache stars of many sizes with a few four-point ones."""
    rnd = c.rnd
    col = P.get('sky', '#1f2a57'); col2 = P.get('sky2', '#4a5fa8')
    disc = ellipse(x, y, s, s, 48)
    c.wash(disc, col2, col, strength=1.0, spread=0.02, layers=40, edge=1.0, granulate=0.5, vary=P.get('sky3', '#3a2c6e'), vary_amt=0.4,
           ang=math.pi / 4)
    for (dx, dy, r, colr) in ((-0.35, 0.25, 0.4, '#6a4fa8'), (0.3, -0.3, 0.35, '#2f6fa8'), (0.1, 0.45, 0.3, '#4b3a8a')):
        c.wash(ellipse(x + s * dx, y + s * dy, s * r, s * r * 0.7, 18, rnd.uniform(0, 3)), colr, None, strength=0.22, spread=0.08, layers=14,
               edge=0.2, clip=disc)
    band = [(x - s * 1.1, y + s * 0.55), (x + s * 0.55, y - s * 1.1), (x + s * 0.9, y - s * 0.75), (x - s * 0.75, y + s * 0.9)]
    c.lift(band, amount=0.32, soft=0.18, clip=disc)
    for _ in range(int(stars * 0.6)):
        t = rnd.uniform(-0.9, 0.9); off = rnd.gauss(0, 0.12)
        px, py = x + s * (t * 0.7 + off * 0.7), y + s * (-t * 0.7 + off * 0.7)
        if math.hypot(px - x, py - y) < s * 0.93:
            rr = s * rnd.uniform(0.003, 0.007)
            gouache(c, ellipse(px, py, rr, rr, 6), color=(250, 248, 238), alpha=rnd.randint(140, 220), soft=0.1)
    for _ in range(stars):
        a, r = rnd.uniform(0, 2 * math.pi), s * 0.9 * math.sqrt(rnd.random())
        rr = s * rnd.choice((0.004, 0.006, 0.008, 0.011, 0.015))
        gouache(c, ellipse(x + r * math.cos(a), y + r * math.sin(a), rr, rr, 8), color=(252, 249, 236), alpha=rnd.randint(170, 245), soft=0.08)
    for _ in range(6):
        a, r = rnd.uniform(0, 2 * math.pi), s * 0.85 * math.sqrt(rnd.random())
        px, py, R = x + r * math.cos(a), y + r * math.sin(a), s * rnd.uniform(0.02, 0.035)
        pts = [(px + (R if k % 2 == 0 else R * 0.25) * math.cos(k * math.pi / 4 - math.pi / 2),
                py + (R if k % 2 == 0 else R * 0.25) * math.sin(k * math.pi / 4 - math.pi / 2)) for k in range(8)]
        gouache(c, pts, color=(255, 250, 232), alpha=230, soft=0.04)



# Aquarius, simplified: the Water Jar (gamma, zeta, eta, pi) at the top left, alpha and beta across to epsilon,
# and the stream falling from theta and lambda down to delta and 88 Aqr (positions from the stars' RA/Dec)
CONSTELLATIONS.setdefault('aquarius', {
    'stars': [(0.97, -0.02), (0.4, -0.23), (-0.06, -0.5), (-0.26, -0.45), (-0.36, -0.52), (-0.45, -0.52), (-0.31, -0.6),
              (-0.2, -0.11), (-0.67, -0.12), (-0.63, 0.2), (-0.7, 0.31), (-0.96, -0.2), (-0.98, 0.04), (-0.89, 0.6)],
    'lines': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (4, 6), (2, 7), (7, 8), (8, 9), (9, 10), (10, 13), (8, 11), (11, 12)],
    'bright': [1, 2, 10]})


def carnation(c, x, y, s, P, angle=0.0, stem=1.0, color=None, color2=None):
    """A carnation (January's birth flower), seen from the side: a rounded dome of
    ruffled petals with frilled edges, pale on top and deeper in the folds, over a
    tapered green calyx with pointed sepals, on a stem with narrow blue-green
    leaves. (x, y) = the middle of the bloom, s = its width."""
    rnd = c.rnd
    col = color or P.get('carn', '#e0668e'); col2 = color2 or P.get('carn2', '#f7c1d2'); col3 = P.get('carn3', '#b8406a')
    g1, g2 = P.get('leaf', '#5f8f62'), P.get('carn_leaf', '#8fb5a6')
    ca, sa = math.cos(angle), math.sin(angle)
    R = lambda px, py: (x + px * ca - py * sa, y + px * sa + py * ca)
    if stem:
        st = [R(0, s * 0.44), R(s * 0.05, s * (0.44 + 0.9 * stem)), R(s * 0.02, s * (0.44 + 1.9 * stem))]
        c.wash(_band(st, s * 0.04, s * 0.034), g2, g1, strength=0.7, layers=10, edge=0.8)
        for t, side in ((0.55, -1), (1.15, 1)):
            if t > 1.7 * stem:
                continue
            bx, by = R(s * 0.035, s * (0.4 + t * stem))
            lf = [(bx, by), R(side * s * 0.3, s * (0.3 + t * stem)), R(side * s * 0.55, s * (0.08 + t * stem))]
            c.wash(_band(lf, s * 0.045, s * 0.006), g2, g1, strength=0.6, layers=10, edge=0.8, vary=g1)
    # calyx: a tapered cup with pointed sepals at its rim
    cal = [R(-s * 0.15, s * 0.2), R(-s * 0.11, s * 0.32), R(-s * 0.065, s * 0.44), R(s * 0.065, s * 0.44), R(s * 0.11, s * 0.32), R(s * 0.15, s * 0.2)]
    c.wash(cal, g2, g1, strength=0.8, layers=12, edge=0.9, ang=angle + math.pi / 2)

    def ruffle(px, py, rx, ry, rot, freq):
        pts = []
        n = 40
        ph = rnd.uniform(0, 6.3)
        for i in range(n):
            t = 2 * math.pi * i / n
            k = 1 + 0.09 * math.sin(freq * t + ph) + 0.04 * math.sin(2.3 * freq * t + ph * 2)
            ex, ey = rx * k * math.cos(t), ry * k * math.sin(t)
            pts.append(R(px + ex * math.cos(rot) - ey * math.sin(rot), py + ex * math.sin(rot) + ey * math.cos(rot)))
        return pts
    # back row high and pale, then middle, then a front skirt that sits on the calyx
    rows = [(-0.2, 0.24, 5, col2, 0.5), (-0.08, 0.3, 5, col, 0.62), (0.06, 0.34, 4, col, 0.68)]
    for ry_off, w, n, k, stg in rows:
        for i in range(n):
            u = (i / (n - 1) - 0.5) if n > 1 else 0
            px = u * 2 * w * s * 0.95
            py = s * ry_off + abs(u) * s * 0.12 + rnd.uniform(-0.02, 0.02) * s
            c.wash(ruffle(px, py, s * 0.16, s * 0.12, u * 0.9, rnd.choice((9, 10, 11))), k, col3, strength=stg, spread=0.03,
                   layers=14, edge=1.15, ang=angle + math.pi / 2, vary=col3, vary_amt=0.25)
    # fringe: short darker strokes along the frilled tops
    for i in range(9):
        u = i / 8 - 0.5
        p0 = R(u * s * 0.55, -s * 0.08 + abs(u) * s * 0.1)
        p1 = R(u * s * 0.62, -s * 0.2 + abs(u) * s * 0.14)
        c.wash(_band([p0, p1], s * 0.008, s * 0.002), col3, None, strength=0.35, layers=6, edge=0.3)
    c.lift(ellipse(*R(-s * 0.1, -s * 0.2), s * 0.13, s * 0.06, 12, angle - 0.2), amount=0.28, soft=0.3)


def _heart_leaf(x, y, s, angle, n=28):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((hx / 17 * s, (hy + 4) / 17 * s))
    ca, sa = math.cos(angle), math.sin(angle)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def violet(c, x, y, s, P, angle=0.0, stem=1.0, leaves=2, color=None, color2=None):
    """A sweet violet (February's birth flower): two upright back petals, two side
    petals and a wide lower petal with dark veins and a white-and-gold throat, on
    a nodding stem with heart-shaped leaves. (x, y) = flower centre, s = its width."""
    rnd = c.rnd
    col = color or P.get('viol', '#6a4fb0'); col2 = color2 or P.get('viol2', '#b9a2e6')
    g1, g2 = P.get('leaf', '#5f8f62'), P.get('leaf2', '#a9c79a')
    if stem:
        st = [(x + s * 0.03, y + s * 0.5), (x + s * 0.18, y + s * (0.5 + 0.55 * stem)), (x + s * 0.1, y + s * (0.5 + 1.4 * stem))]
        c.wash(_band(st, s * 0.035, s * 0.03), g2, g1, strength=0.7, layers=10, edge=0.8)
        for k in range(leaves):
            side = -1 if k % 2 == 0 else 1
            lx, ly = x + s * (0.1 + side * 0.42), y + s * (1.35 + 0.25 * k) * stem
            c.wash(_band([(x + s * 0.12, y + s * 1.85 * stem), (lx, ly + s * 0.2)], s * 0.02, s * 0.015), g2, g1, strength=0.6, layers=8)
            hl = _heart_leaf(lx, ly, s * 0.36, side * 0.5 + math.pi)
            c.wash(hl, g2, g1, strength=0.7, layers=14, edge=1.0, vary=P.get('leaf_dark', '#2e5a3c'), vary_amt=0.35)
            c.wash(_band([(lx, ly + s * 0.14), (lx - side * s * 0.02, ly - s * 0.2)], s * 0.008, s * 0.003), P.get('leaf_dark', '#2e5a3c'),
                   None, strength=0.45, layers=6, edge=0.3)
    for a, L, W, k in ((-math.pi / 2 - 0.42, 0.55, 0.36, col), (-math.pi / 2 + 0.42, 0.55, 0.36, col),
                       (math.pi - 0.25, 0.48, 0.3, col2), (0.25, 0.48, 0.3, col2), (math.pi / 2, 0.58, 0.42, col2)):
        aa = angle + a + rnd.uniform(-0.05, 0.05)
        c.wash(petal_pts(x, y, s * L, s * W, aa), k, col, strength=0.75, spread=0.02, layers=14, edge=1.3, ang=aa + math.pi,
               vary=P.get('viol3', '#4a338a'), vary_amt=0.35)
    for dv in (-0.35, 0.0, 0.35):
        aa = angle + math.pi / 2 + dv
        c.wash(_band([(x, y + s * 0.04), (x + s * 0.3 * math.cos(aa), y + s * 0.3 * math.sin(aa))], s * 0.01, s * 0.003),
               P.get('viol3', '#3d2a75'), None, strength=0.6, layers=6, edge=0.4)
    gouache(c, ellipse(x, y + s * 0.02, s * 0.09, s * 0.08, 10), color=(252, 250, 244), alpha=235, soft=0.06)
    gouache(c, ellipse(x, y + s * 0.03, s * 0.045, s * 0.04, 8), color=_rgb(P.get('accent', '#e2b04a')), alpha=240, soft=0.06)


MOTIFS2 = {'splash': splash, 'snowfall': snowfall, 'far_forest': far_forest, 'snow_drift': snow_drift, 'grass_tufts': grass_tufts,
           'spruce': spruce, 'vintage_truck': vintage_truck, 'mini_wreath': mini_wreath, 'cozy_glow': cozy_glow, 'twinkle': twinkle,
           'book_tree2': book_tree2, 'gift2': gift2, 'cozy_cat': cozy_cat, 'base_garland': base_garland, 'mini_bauble': mini_bauble,
           'glass_bauble': glass_bauble, 'narcissus': narcissus, 'snowdrop': snowdrop, 'night_sky2': night_sky2,
           'carnation': carnation, 'violet': violet}
