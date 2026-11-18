"""Detailed motifs (second generation): painted in many more passes than
motifs.py, the way an illustrator builds a finished watercolor: a pale
first wash for the form, patchy wet-in-wet color, shaped shadows wet on dry,
lifted highlights, dry-brush texture, opaque gouache last (snow, glints,
chrome), and a fine pen line where an edge must read.

Coordinates: (x, y) in canvas px, y down; s = the motif's size in px.
"""
import math
from watercolor import ellipse, leaf, petal, rect, deform
from motifs import _rot, smooth, gouache, _rgb, _band, _star_pts, CONSTELLATIONS, crescent

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


def far_forest(c, x, y, s, P, n=24, height=0.22, color=None, color2=None, strength=1.0):
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
        c.wash(pts, col2, col, strength=rnd.uniform(0.4, 0.58) * strength, spread=0.03, layers=14, edge=0.6, ang=math.pi / 2)
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


def gift2(c, x, y, s, P, color=None, ribbon=None, pattern=None, tall=1.0, angle=0.0, ink=150, shadow=False, shade=None, soft=False):
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
    g0 = c.snapshot() if shadow else None
    sh = _shade(col, 0.7) if shade == 'auto' else (shade or P.get('book_shadow', '#3a2a2e'))
    c.wash(box, col, None, strength=0.85, spread=0.004, layers=22, edge=1.0, vary=sh, vary_amt=0.25)
    if soft:
        c.wash(R(rect(x + s * 0.2, y - H, x + s * 1.2, y)), sh, None, strength=0.3, layers=10, edge=0.0, blur=s * 0.12, clip=box)
    else:
        c.wash(R(rect(x + s * 0.35, y - H, x + s, y)), sh, None, strength=0.2, layers=10, edge=0.3)
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
    if soft:
        c.wash(R(rect(x - s, y - H + s * 0.1, x + s, y - H + s * 0.2)), sh, None, strength=0.3, layers=8, edge=0.0, blur=s * 0.04, clip=box)
    else:
        c.wash(R(rect(x - s * 1.06, y - H + s * 0.04, x + s * 1.06, y - H + s * 0.1)), sh, None, strength=0.3, layers=8)
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
    c.ink_line(box, width=max(1.5, s * 0.025), alpha=ink, passes=1, jitter=0, color=(44, 32, 36))
    c.ink_line(lid, width=max(1.5, s * 0.025), alpha=ink, passes=1, jitter=0, color=(44, 32, 36))
    if shadow:
        # a soft contact shadow on the table, painted around the box
        c.paint_around(g0)
        c.wash(ellipse(x + s * 0.12, y + s * 0.04, s * 1.3, s * 0.13, 20), P.get('table_shadow', '#c9b7c0'), None, strength=0.3,
               spread=0.03, layers=10, edge=0.0, blur=s * 0.05)


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
    return '#%02x%02x%02x' % tuple(min(255, int(v * k)) for v in (r, g, b))


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


# ---------------------------------------------------------------- lake at dawn (Grandpa's Fishing Hole)
def sunrise(c, x, y, s, P, color=None, glow=None):
    """A low sun at dawn: a wide warm glow on the sky, then a pale gold disc
    with a hot centre. (x, y) = centre of the disc, s = its radius."""
    col = color or P.get('sun', '#f4bd62'); g = glow or P.get('sun_glow', '#f3a27a')
    c.glow(x, y, s * 3.4, g, strength=0.3)
    c.glow(x, y, s * 1.9, col, strength=0.34)
    c.wash(ellipse(x, y, s, s, 30), '#fbe6a8', col, strength=0.6, spread=0.008, layers=16, edge=0.45, ang=math.pi / 2)
    c.lift(ellipse(x - s * 0.15, y - s * 0.2, s * 0.45, s * 0.4, 16), amount=0.35, soft=0.3)


def mountains2(c, x, y, s, P, peaks=None, color=None, color2=None, dark=None, snow=0.3):
    """A painterly mountain range at dawn: jagged ridgelines (midpoint
    displacement), a pale wash for the lit faces and a deeper wash for the
    shadow side of each peak, dry-brush gullies, and snow in white gouache
    that streaks down the gullies. Back peaks paler (aerial perspective).
    (x, y) = middle of the base, s = half the width."""
    rnd = c.rnd
    col = color or P.get('mtn', '#8e8db2'); col2 = color2 or P.get('mtn2', '#c6c0da'); dk = dark or P.get('mtn_dark', '#5f5c88')
    peaks = peaks or [(-0.55, 0.62, 0.55, 0), (0.45, 0.78, 0.6, 0), (-0.05, 1.0, 0.62, 1)]
    for dx, h, w, near in peaks:
        px = x + s * dx; top = (px, y - s * h)

        def ridge(a, b, n=5, amp=0.06):
            pts = [a]
            for k in range(1, n):
                t = k / n
                pts.append((a[0] + (b[0] - a[0]) * t + rnd.uniform(-1, 1) * s * amp * 0.3,
                            a[1] + (b[1] - a[1]) * t + rnd.uniform(-0.4, 1) * s * amp))
            return pts
        left = ridge((px - s * w, y), top); right = ridge(top, (px + s * w, y))
        sil = left + right[:]
        lit, shade = (col2, col) if not near else (col, dk)
        c.wash(sil + [(px + s * w, y)], lit, col, strength=0.38 if not near else 0.5, spread=0.012, layers=22, edge=0.6,
               vary=P.get('sky3', '#f0b8a2'), vary_amt=0.25, ang=math.pi / 2)
        # the shadow side: from the summit down a jagged central rib to the base
        rib = ridge(top, (px + s * w * 0.15, y), n=6, amp=0.03)
        c.wash(rib + list(reversed(right))[:-1][::-1][::-1] + [(px + s * w, y)], shade, None, strength=0.32 if not near else 0.45,
               spread=0.015, layers=16, edge=0.5)
        for k in range(4):   # gullies
            gx = px + s * w * rnd.uniform(-0.6, 0.6); gy = y - s * h * rnd.uniform(0.2, 0.6)
            c.dry_brush([(gx, gy), (gx + s * 0.02, gy + s * h * 0.12), (gx + s * 0.01, gy + s * h * 0.25)], s * 0.02, dk, strength=0.16,
                        bristles=4, gap=0.4)
        # snow: a cap following the ridge, with streaks running down
        if snow:
            cap_l = [p for p in left if p[1] < y - s * h * (1 - snow)]
            cap_r = [p for p in right if p[1] < y - s * h * (1 - snow)]
            if cap_l and cap_r:
                base_y = y - s * h * (1 - snow * 0.9)
                cap = cap_l + cap_r + [(cap_r[-1][0], base_y + s * 0.02), (px + s * w * 0.05, base_y - s * 0.03),
                                       (px - s * w * 0.1, base_y + s * 0.015), (cap_l[0][0], base_y)]
                gouache(c, cap, color=(251, 249, 245), alpha=200, soft=0.02)
                for k in range(5):
                    sx = px + s * w * rnd.uniform(-0.25, 0.3); sy = base_y + rnd.uniform(-0.01, 0.01) * s
                    L = s * h * rnd.uniform(0.08, 0.18)
                    gouache(c, [(sx - s * 0.008, sy), (sx + s * 0.008, sy), (sx + s * 0.003, sy + L), (sx - s * 0.002, sy + L * 0.9)],
                            color=(251, 249, 245), alpha=170, soft=0.08)
                c.lift(cap_r + [(px + s * w * 0.1, y - s * h * 0.6)], amount=0.15, soft=0.2)



def lake(c, x, y, s, P, depth=0.6, sun=None, color=None, color2=None):
    """Still water at dawn. (x, y) = middle of the far shoreline, s = half its
    width, depth = how far down the water reaches (fraction of s). A gradient
    wash (pale sky colour at the horizon, deeper blue in front), dark tree
    reflections under the far shore, a broken column of light under the sun,
    and dry-brush ripples that spread out toward the front (perspective)."""
    rnd = c.rnd
    deep = color or P.get('water', '#4c82aa'); pale = color2 or P.get('water2', '#cfe1ea')
    dark = P.get('water_dark', '#2f5f83'); refl = P.get('refl', '#56786f')
    D = s * depth
    sun_x = None if sun is None else x + s * sun
    pts = [(x + s * math.cos(math.pi * k / 30), y + D * math.sin(math.pi * k / 30)) for k in range(31)]
    c.wash(pts, pale, deep, strength=0.62, spread=0.012, layers=30, edge=0.45, granulate=0.25,
           vary=P.get('water3', '#7fb0c9'), vary_amt=0.35, ang=math.pi / 2)
    # a second, deeper glaze over the front half
    front = [(x + s * 0.97 * math.cos(math.pi * k / 24), y + D * 0.35 + D * 0.62 * math.sin(math.pi * k / 24)) for k in range(25)]
    c.wash(front, deep, dark, strength=0.24, spread=0.05, layers=18, edge=0.0, blur=s * 0.04, ang=math.pi / 2)

    def half_w(py):
        t = (py - y) / D
        return s * math.sqrt(max(0.0, 1 - t * t))
    # far-shore reflections: soft vertical streaks of the dark trees
    for k in range(30):
        px = x - s * 0.96 + 1.92 * s * k / 29 + rnd.uniform(-1, 1) * s * 0.02
        w = s * rnd.uniform(0.018, 0.04); h = D * rnd.uniform(0.07, 0.17)
        c.wash([(px - w, y + s * 0.003), (px + w, y + s * 0.003), (px + w * 0.15, y + h), (px - w * 0.15, y + h)], refl, None,
               strength=rnd.uniform(0.14, 0.24), spread=0.08, layers=10, edge=0.15, blur=s * 0.004)
    c.wash(rect(x - s * 0.98, y - s * 0.004, x + s * 0.98, y + s * 0.01), dark, None, strength=0.3, spread=0.02, layers=8, edge=0.5)
    # the sun's path: lifted dashes, wider toward the viewer, a few gold glints
    if sun_x is not None:
        for i in range(22):
            u = i / 21
            py = y + D * (0.02 + 0.8 * u ** 1.25)
            if abs(sun_x - x) > half_w(py) * 0.9:
                continue
            w = s * (0.02 + 0.07 * u) * rnd.uniform(0.6, 1.3)
            px = sun_x + rnd.uniform(-1, 1) * s * 0.012 * (1 + 2 * u)
            c.lift(ellipse(px, py, w, s * (0.004 + 0.004 * u), 12), amount=0.7, soft=0.12)
            if rnd.random() < 0.55:
                gw = w * rnd.uniform(0.25, 0.6)
                gouache(c, ellipse(px + rnd.uniform(-1, 1) * w * 0.4, py, gw, s * 0.0028, 10), color=(252, 226, 160), alpha=rnd.randint(150, 215), soft=0.25)
    # ripples: short dry-brush strokes, larger and further apart toward the front
    for i in range(34):
        u = rnd.random() ** 0.85
        py = y + D * (0.06 + 0.86 * u)
        hw = half_w(py) * 0.88
        px = x + rnd.uniform(-1, 1) * hw
        L = s * rnd.uniform(0.03, 0.08) * (0.6 + 1.2 * u)
        path = [(px - L + 2 * L * k / 7, py + s * 0.0025 * math.sin(k * 1.4)) for k in range(8)]
        c.dry_brush(path, s * (0.004 + 0.006 * u) * rnd.uniform(0.7, 1.2), dark, strength=rnd.uniform(0.22, 0.38), bristles=5, gap=0.4)
    for i in range(14):
        u = rnd.random() ** 0.9
        py = y + D * (0.08 + 0.8 * u); hw = half_w(py) * 0.85
        px = x + rnd.uniform(-1, 1) * hw
        L = s * rnd.uniform(0.03, 0.07) * (0.6 + u)
        c.lift(ellipse(px, py, L, s * 0.0035 * (1 + u), 10), amount=0.45, soft=0.2)


def birds(c, x, y, s, P, n=3):
    """A few distant birds: small loose pen 'v' strokes. s = spread."""
    rnd = c.rnd
    inkc = P.get('bird_ink', (74, 70, 86))
    for k in range(n):
        px = x + s * rnd.uniform(-1, 1); py = y + s * rnd.uniform(-0.4, 0.4)
        w = s * rnd.uniform(0.09, 0.14)
        pts = [(px - w, py - w * 0.25), (px - w * 0.45, py - w * 0.35), (px, py + w * 0.05), (px + w * 0.45, py - w * 0.4), (px + w, py - w * 0.3)]
        c.ink_line(smooth(pts, 2, closed=False), width=max(2, w * 0.13), closed=False, alpha=190, passes=1, jitter=0.0003)


def dock(c, x, y, s, P, rod=True, box=True, bobber=None):
    """A weathered wooden dock running out over the water from the left, in
    perspective (near end big, far end small): plank deck with seams and
    dry-brush grain, a front beam, posts standing in the water with rings,
    nail heads, a green tackle box, and a fishing rod whose line runs out to a
    red-and-white bobber. (x, y) = far (right) end of the deck's front edge,
    s = the dock's length. bobber = (bx, by) in units of s from (x, y)."""
    rnd = c.rnd
    wood = P.get('wood', '#c39a6b'); wood2 = P.get('wood2', '#e2c49b'); wood_dk = P.get('wood_dark', '#6e4c32')
    grey = P.get('wood_grey', '#a8a092'); inkc = P.get('dock_ink', (70, 50, 36))
    F0, F1 = (x - s, y + s * 0.11), (x, y)
    B0, B1 = (x - s * 0.93, y - s * 0.085), (x + s * 0.025, y - s * 0.058)

    def L(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    thick0, thick1 = s * 0.06, s * 0.026
    # posts first (behind the beam), each with water rings at its foot
    for t in (0.06, 0.37, 0.68, 0.97):
        top = L(F0, F1, t)
        w = s * (0.042 - 0.024 * t); h = s * (0.25 - 0.15 * t)
        px, py = top[0], top[1] + thick0 * (1 - t) + thick1 * t
        c.wash(rect(px - w, py - s * 0.01, px + w, py + h), wood_dk, wood, strength=0.75, spread=0.01, layers=14, edge=0.7, ang=0.0)
        c.dry_brush([(px - w * 0.3, py), (px - w * 0.25, py + h * 0.5), (px - w * 0.35, py + h * 0.95)], w * 0.6, wood_dk, strength=0.5, bristles=4)
        c.wash(rect(px - w, py + h * 0.82, px + w, py + h), P.get('water_dark', '#2f5f83'), None, strength=0.35, spread=0.02, layers=8, edge=0.4)
        for r in (1.6, 2.6):
            c.ink_line(ellipse(px, py + h, w * r, w * r * 0.22, 20), width=max(2, s * 0.0025), alpha=110, passes=1, jitter=0.0002)
    # the front beam (its face toward us)
    beam = [F0, F1, (F1[0], F1[1] + thick1), (F0[0], F0[1] + thick0)]
    c.wash(beam, wood, wood_dk, strength=0.8, spread=0.006, layers=16, edge=0.7, vary=grey, vary_amt=0.3, ang=math.pi / 2)
    # the deck: weathered planks, lighter toward the far end
    deck = [B0, B1, F1, F0]
    c.wash(deck, wood2, wood, strength=0.72, spread=0.006, layers=22, edge=0.6, vary=grey, vary_amt=0.45, ang=0.0, blooms=2, bloom_size=0.08)
    n = 15
    us = [(k / n) ** 1.18 for k in range(1, n)]
    for i, u in enumerate(us):
        a, b = L(B0, B1, u), L(F0, F1, u)
        if i % 3 == 1:   # one plank in three a little darker (weathering)
            u2 = us[i + 1] if i + 1 < len(us) else 1.0
            c.wash([a, L(B0, B1, u2), L(F0, F1, u2), b], wood_dk, None, strength=0.16, spread=0.01, layers=8, edge=0.4)
        c.ink_line([a, b], width=max(2, s * 0.0032 * (1.2 - 0.7 * u)), closed=False, alpha=150, passes=1, jitter=0.0002)
        for k in (0.2, 0.8):   # nail heads near both ends of the plank
            q = L(L(B0, B1, u), L(F0, F1, u), k)
            c.wash(ellipse(q[0] + s * 0.006, q[1], s * 0.0035 * (1.2 - 0.7 * u), s * 0.0028, 8), '#4a3b30', None, strength=0.7, layers=6, edge=0.6)
    for k in range(10):   # grain
        u = rnd.uniform(0.02, 0.95); off = rnd.uniform(0.15, 0.85)
        a, b = L(B0, B1, u), L(F0, F1, u)
        p0 = L(a, b, off * 0.4); p1 = L(a, b, min(1.0, off * 0.4 + 0.5))
        c.dry_brush([p0, L(p0, p1, 0.5), p1], s * 0.012 * (1.2 - 0.7 * u), wood_dk, strength=0.4, bristles=4, gap=0.4)
    c.ink_line([B0, B1], width=max(2, s * 0.003), closed=False, alpha=140, passes=1, jitter=0.0002)
    c.ink_line([F0, F1, (F1[0], F1[1] + thick1), (F0[0], F0[1] + thick0)], width=max(2, s * 0.0035), closed=False, alpha=170, passes=1, jitter=0.0002)
    if box:   # a green tackle box sitting on the planks
        m = L(L(B0, B1, 0.3), L(F0, F1, 0.3), 0.55)
        bw, bh, bd = s * 0.085, s * 0.06, s * 0.03
        bx, by = m
        green = P.get('box', '#4f8460'); green_dk = P.get('box_dark', '#2f5a41')
        front_face = [(bx - bw, by - bh), (bx + bw, by - bh), (bx + bw, by), (bx - bw, by)]
        top_face = [(bx - bw, by - bh), (bx - bw + bd, by - bh - bd * 0.7), (bx + bw + bd, by - bh - bd * 0.7), (bx + bw, by - bh)]
        side = [(bx + bw, by - bh), (bx + bw + bd, by - bh - bd * 0.7), (bx + bw + bd, by - bd * 0.7), (bx + bw, by)]
        c.wash(front_face, green, green_dk, strength=0.8, spread=0.005, layers=14, edge=0.7, ang=math.pi / 2)
        c.wash(side, green_dk, None, strength=0.8, spread=0.005, layers=10, edge=0.6)
        c.wash(top_face, '#7fae8a', green, strength=0.7, spread=0.005, layers=10, edge=0.6)
        c.wash(rect(bx - bw * 0.15, by - bh * 0.62, bx + bw * 0.15, by - bh * 0.42), '#d9b45a', None, strength=0.85, layers=8, edge=0.6)
        c.ink_line(smooth([(bx - bw * 0.45, by - bh - bd * 0.35), (bx - bw * 0.3, by - bh - bd * 1.6), (bx + bw * 0.45, by - bh - bd * 1.6),
                           (bx + bw * 0.6, by - bh - bd * 0.35)], 2, closed=False), width=max(2, s * 0.004), closed=False, alpha=200, passes=1, jitter=0.0002)
        c.ink_line(front_face, width=max(2, s * 0.003), alpha=170, passes=1, jitter=0.0002)
        c.lift(rect(bx - bw * 0.9, by - bh * 0.95, bx - bw * 0.5, by - bh * 0.15), amount=0.3, soft=0.2)
        # a shadow on the planks
        c.wash(ellipse(bx + bw * 0.3, by + s * 0.004, bw * 1.15, s * 0.008, 14), wood_dk, None, strength=0.3, spread=0.04, layers=8, edge=0.3)
    if rod:
        butt = L(L(B0, B1, 0.78), L(F0, F1, 0.78), 0.6)
        tip = (x + s * 0.34, y - s * 0.56)
        mid = ((butt[0] + tip[0]) / 2 - s * 0.03, (butt[1] + tip[1]) / 2 - s * 0.03)
        path = [butt] + smooth([butt, mid, tip], 2, closed=False) + [tip]   # keep both ends (open Chaikin trims them)
        c.ink_line(path, width=max(3, s * 0.0085), closed=False, color=(48, 40, 34), alpha=235, passes=1, jitter=0.0001)
        c.wash(_band([butt, L(butt, tip, 0.12)], s * 0.013, s * 0.01), '#7a5236', None, strength=0.9, layers=8, edge=0.6)   # cork grip
        r0 = L(butt, tip, 0.17)
        c.wash(ellipse(r0[0], r0[1] + s * 0.016, s * 0.022, s * 0.022, 14), '#9aa3ab', '#5d666e', strength=0.8, layers=10, edge=0.7)
        bxu, byu = bobber or (0.6, 0.12)
        bb = (x + s * bxu, y + s * byu)
        sag = ((tip[0] + bb[0]) / 2 + s * 0.04, (tip[1] + bb[1]) / 2 + s * 0.06)
        c.ink_line([tip] + smooth([tip, sag, bb], 3, closed=False) + [bb], width=max(1, s * 0.0022), closed=False, color=(90, 96, 104), alpha=170, passes=1, jitter=0.00005)
        br = s * 0.02
        for r in (1.8, 3.0, 4.4):
            c.ink_line(ellipse(bb[0], bb[1] + br * 0.5, br * r, br * r * 0.25, 22), width=max(2, s * 0.0022), alpha=95, passes=1, jitter=0.0002)
        c.wash(ellipse(bb[0], bb[1] + br * 0.2, br, br * 0.85, 16), '#f4efe6', None, strength=0.35, layers=8, edge=0.8)
        c.wash([(bb[0] - br, bb[1]), (bb[0] - br * 0.7, bb[1] - br * 0.75), (bb[0], bb[1] - br), (bb[0] + br * 0.7, bb[1] - br * 0.75), (bb[0] + br, bb[1])],
               '#d8433a', None, strength=0.95, layers=10, edge=0.7)
        c.ink_line(ellipse(bb[0], bb[1], br, br * 0.95, 18), width=max(2, s * 0.0025), alpha=170, passes=1, jitter=0.0001)


def rowboat(c, x, y, s, P, facing=1, color=None):
    """A wooden rowboat floating side-on: painted hull with a cream rub rail,
    the wooden inside showing above the near gunwale, two thwarts, an oar
    resting in the water, a dark waterline and a broken reflection.
    (x, y) = middle of the waterline, s = half its length; facing 1 = bow right."""
    rnd = c.rnd
    red = color or P.get('boat', '#c4553a'); red_hi = P.get('boat2', '#e3815c'); red_dk = P.get('boat_dark', '#7f2f24')
    inside = P.get('boat_in', '#b48659'); inside_dk = P.get('wood_dark', '#6e4c32')
    f = facing

    def T(px, py):
        return (x + f * s * px, y + s * py)
    near = [(-1.0, -0.38), (-0.6, -0.31), (-0.2, -0.29), (0.2, -0.3), (0.55, -0.35), (0.82, -0.44), (1.0, -0.6)]
    far = [(-0.97, -0.48), (-0.6, -0.42), (-0.2, -0.4), (0.2, -0.41), (0.55, -0.45), (0.82, -0.51), (1.0, -0.6)]
    # reflection first (under everything)
    refl = [T(px, -py * 0.6 + 0.02) for px, py in near] + [T(0.75, 0.02), T(-0.95, 0.02)]
    c.wash(smooth(refl, 1), P.get('water2', '#cfe1ea'), P.get('water', '#4c82aa'), strength=0.5, spread=0.06, layers=12, edge=0.0,
           blur=s * 0.03, ang=math.pi / 2)
    c.wash(smooth(refl, 1), red, None, strength=0.24, spread=0.08, layers=12, edge=0.0, blur=s * 0.04)
    for k in range(9):   # the surface breaks the reflection into bands
        py = s * rnd.uniform(0.04, 0.24); px = rnd.uniform(-0.9, 0.7)
        c.lift(ellipse(T(px, 0)[0], y + py, s * rnd.uniform(0.12, 0.3), s * 0.01, 10), amount=0.55, soft=0.25)
    # the inside of the hull
    c.wash(smooth([T(*p) for p in far] + [T(*p) for p in reversed(near)], 1), inside, inside_dk, strength=0.75, spread=0.01, layers=16,
           edge=0.7, ang=math.pi / 2)
    for tx in (-0.5, 0.3):   # thwarts (seats)
        a = T(tx - 0.06, -0.41); b = T(tx + 0.06, -0.41)
        c.wash([a, b, T(tx + 0.07, -0.3), T(tx - 0.05, -0.3)], P.get('wood2', '#e2c49b'), None, strength=0.75, layers=10, edge=0.7)
    # the hull side
    hull = [T(*p) for p in near] + [T(0.93, -0.32), T(0.84, -0.12), T(0.7, 0.0), T(-0.96, 0.0)]
    c.wash(smooth(hull, 1), red_hi, red, strength=0.85, spread=0.008, layers=24, edge=0.75, vary=red_dk, vary_amt=0.3, ang=math.pi / 2)
    # planking lines and a shadow along the bottom
    for k in (0.42, 0.62, 0.82):
        line = [T(-0.98, -0.38 * (1 - k)), T(-0.3, -0.3 * (1 - k)), T(0.4, -0.31 * (1 - k)), T(0.86 - 0.16 * k, -0.4 * (1 - k))]
        c.ink_line(smooth(line, 2, closed=False), width=max(1, s * 0.004), closed=False, color=(110, 44, 34), alpha=120, passes=1, jitter=0.0002)
    c.wash([T(-0.96, -0.08), T(0.74, -0.06), T(0.7, 0.0), T(-0.96, 0.0)], red_dk, None, strength=0.5, spread=0.02, layers=10, edge=0.4)
    # cream rub rail along the near gunwale
    rail = [T(px, py) for px, py in near] + [T(px, py + 0.06) for px, py in reversed(near[:-1])] + [T(-1.0, -0.32)]
    c.wash(smooth(rail, 1), '#f3ead8', '#d9c9a8', strength=0.6, spread=0.004, layers=12, edge=0.7)
    c.lift(smooth([T(-0.8, -0.24), T(0.3, -0.22), T(0.6, -0.27), T(0.3, -0.18), T(-0.8, -0.2)], 1), amount=0.35, soft=0.2)
    # the oar: shaft from the oarlock down into the water, blade just under the surface
    a = T(-0.1, -0.36); b = T(-0.55, 0.1)
    c.wash(_band([a, b], s * 0.02, s * 0.018), P.get('wood2', '#e2c49b'), None, strength=0.8, layers=10, edge=0.7)
    c.wash(ellipse(T(-0.62, 0.17)[0], T(-0.62, 0.17)[1], s * 0.12, s * 0.035, 16, f * 0.55), P.get('wood2', '#e2c49b'), P.get('water', '#4c82aa'),
           strength=0.4, layers=10, edge=0.4)
    c.ink_line([a, b], width=max(2, s * 0.004), closed=False, alpha=150, passes=1, jitter=0.0002)
    # waterline and pen edges
    c.wash([T(-0.98, -0.012), T(0.72, -0.012), T(0.72, 0.016), T(-0.98, 0.016)], '#2f4f63', None, strength=0.55, spread=0.03, layers=8, edge=0.5)
    c.ink_line(smooth(hull, 1), width=max(2, s * 0.005), alpha=150, passes=1, jitter=0.0002)
    c.ink_line(smooth([T(*p) for p in far], 1, closed=False), width=max(2, s * 0.004), closed=False, alpha=130, passes=1, jitter=0.0002)
    for r in (1.08, 1.2):
        c.ink_line([T(-r, 0.03), T(-r + 0.25, 0.035)], width=max(2, s * 0.003), closed=False, alpha=110, passes=1, jitter=0.0002)
        c.ink_line([T(r * 0.8, 0.03), T(r * 0.8 - 0.22, 0.035)], width=max(2, s * 0.003), closed=False, alpha=110, passes=1, jitter=0.0002)


def trout(c, x, y, s, P, facing=1, arc=0.55, water=None):
    """A rainbow trout leaping clear of the water: arched body (olive back with
    dark spots, a rosy band along the side, pale belly), forked tail, fins,
    eye and gill line; spray droplets and rings where it broke the surface.
    (x, y) = middle of the body, s = half its length. water = the surface's
    distance below (x, y) in units of s."""
    rnd = c.rnd
    f = facing
    back = P.get('trout', '#76905a'); belly = P.get('trout2', '#e9e4d0'); rose = P.get('trout_rose', '#e08a92'); dk = P.get('trout_dark', '#3f5233')
    N = 21
    cen = [(x + f * s * (2 * u - 1), y - s * arc * 4 * u * (1 - u) + s * arc * 0.5) for u in [k / (N - 1) for k in range(N)]]
    prof = [0.05, 0.08, 0.1, 0.12, 0.145, 0.17, 0.19, 0.205, 0.215, 0.222, 0.226, 0.226, 0.222, 0.212, 0.198, 0.178, 0.152, 0.12, 0.085, 0.05, 0.02]
    up, lo = [], []
    for i, (px, py) in enumerate(cen):
        nx, ny = _path_normal(cen, i)
        if ny > 0:
            nx, ny = -nx, -ny
        w = s * prof[i]
        up.append((px + nx * w, py + ny * w)); lo.append((px - nx * w * 0.95, py - ny * w * 0.95))
    body = up + list(reversed(lo))
    # tail: a forked fin at the tail end (u = 0)
    t0, t1 = cen[0], cen[2]
    dx, dy = t0[0] - t1[0], t0[1] - t1[1]; Ld = math.hypot(dx, dy) or 1; dx, dy = dx / Ld, dy / Ld
    nx, ny = -dy, dx
    tail = [(t0[0] + nx * s * 0.04, t0[1] + ny * s * 0.04), (t0[0] + dx * s * 0.3 + nx * s * 0.2, t0[1] + dy * s * 0.3 + ny * s * 0.2),
            (t0[0] + dx * s * 0.2, t0[1] + dy * s * 0.2), (t0[0] + dx * s * 0.3 - nx * s * 0.2, t0[1] + dy * s * 0.3 - ny * s * 0.2),
            (t0[0] - nx * s * 0.04, t0[1] - ny * s * 0.04)]
    c.wash(smooth(tail, 1), back, dk, strength=0.75, spread=0.02, layers=14, edge=0.8)
    # dorsal and lower fins
    m = 9
    c.wash([up[m - 2], (up[m][0] + (up[m][0] - cen[m][0]) * 0.9, up[m][1] + (up[m][1] - cen[m][1]) * 0.9), up[m + 2]], back, dk, strength=0.7, layers=10, edge=0.7)
    m2 = 14
    c.wash([lo[m2 - 1], (lo[m2][0] + (lo[m2][0] - cen[m2][0]) * 0.8, lo[m2][1] + (lo[m2][1] - cen[m2][1]) * 0.8), lo[m2 + 1]], '#c9a98a', None,
           strength=0.6, layers=8, edge=0.7)
    # the body: olive back over a pale belly, then the rosy band
    c.wash(smooth(body, 1), back, belly, strength=0.82, spread=0.006, layers=22, edge=0.7, vary='#9fb07a', vary_amt=0.35, ang=-math.pi / 2 if f > 0 else -math.pi / 2)
    band = [(cen[i][0] + (lo[i][0] - cen[i][0]) * 0.05, cen[i][1] + (lo[i][1] - cen[i][1]) * 0.05) for i in range(3, N - 4)]
    c.wash(_band(band, s * 0.05, s * 0.035), rose, '#c96b7a', strength=0.65, spread=0.02, layers=12, edge=0.5)
    c.lift(smooth([lo[i] for i in range(4, N - 4)] + [cen[i] for i in range(N - 5, 3, -1)], 1), amount=0.3, soft=0.25)
    # spots on the back and tail
    for _ in range(26):
        i = rnd.randint(0, N - 5)
        k = rnd.uniform(0.25, 0.85)
        px = cen[i][0] + (up[i][0] - cen[i][0]) * k; py = cen[i][1] + (up[i][1] - cen[i][1]) * k
        rr = s * rnd.uniform(0.008, 0.015)
        c.wash(ellipse(px, py, rr, rr * 0.85, 8), dk, None, strength=0.85, layers=6, edge=0.6)
    for _ in range(6):
        px = t0[0] + dx * s * rnd.uniform(0.05, 0.2) + nx * s * rnd.uniform(-0.12, 0.12)
        py = t0[1] + dy * s * rnd.uniform(0.05, 0.2) + ny * s * rnd.uniform(-0.12, 0.12)
        c.wash(ellipse(px, py, s * 0.008, s * 0.007, 8), dk, None, strength=0.8, layers=6, edge=0.6)
    # head: eye, gill line, mouth
    h = cen[N - 4]
    ex, ey = h[0] + (up[N - 4][0] - h[0]) * 0.25, h[1] + (up[N - 4][1] - h[1]) * 0.25
    c.wash(ellipse(ex, ey, s * 0.03, s * 0.03, 12), '#e8c56a', None, strength=0.8, layers=8, edge=0.7)
    c.wash(ellipse(ex, ey, s * 0.017, s * 0.017, 10), '#1f1f22', None, strength=1.0, layers=6, edge=0.5)
    gouache(c, ellipse(ex - s * 0.007, ey - s * 0.008, s * 0.006, s * 0.006, 8), alpha=230, soft=0.1)
    g = N - 7
    gill = [(up[g][0] * 0.7 + cen[g][0] * 0.3, up[g][1] * 0.7 + cen[g][1] * 0.3), (cen[g + 1][0], cen[g + 1][1]),
            (lo[g][0] * 0.75 + cen[g][0] * 0.25, lo[g][1] * 0.75 + cen[g][1] * 0.25)]
    c.ink_line(smooth(gill, 2, closed=False), width=max(2, s * 0.008), closed=False, alpha=150, passes=1, jitter=0.0002)
    c.ink_line(smooth(body, 1), width=max(2, s * 0.007), alpha=140, passes=1, jitter=0.0002)
    # spray and rings where it left the water
    if water is not None:
        sx = cen[3][0]
        water = y + s * water
        for r in (0.18, 0.32, 0.48):
            c.ink_line(ellipse(sx, water, s * r, s * r * 0.18, 24), width=max(2, s * 0.006), alpha=110, passes=1, jitter=0.0002)
        c.lift(ellipse(sx, water, s * 0.3, s * 0.05, 16), amount=0.5, soft=0.3)
        for _ in range(22):
            a = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05)
            r = s * rnd.uniform(0.08, 0.45)
            px = sx + r * math.cos(a) * 1.2; py = water + r * math.sin(a) * 0.9
            rr = s * rnd.uniform(0.006, 0.016)
            c.wash(ellipse(px, py, rr, rr * 1.2, 8), P.get('water', '#4c82aa'), None, strength=0.55, layers=6, edge=0.8)
            gouache(c, ellipse(px - rr * 0.3, py - rr * 0.3, rr * 0.45, rr * 0.45, 8), alpha=225, soft=0.1)


def cattails(c, x, y, s, P, n=4, reeds=9, lean=0.0):
    """A clump of cattails at the water's edge: long blade leaves, some bent,
    brown velvety heads on thin stems with a spike above each.
    (x, y) = foot of the clump, s = its height."""
    rnd = c.rnd
    g1 = P.get('reed', '#6f9a58'); g2 = P.get('reed2', '#b6c97f'); gd = P.get('reed_dark', '#3f6a3c')
    brown = P.get('cattail', '#7a4c2e'); brown2 = P.get('cattail2', '#a7714a')
    for k in range(reeds):
        a = -math.pi / 2 + lean + rnd.uniform(-0.45, 0.45)
        L = s * rnd.uniform(0.55, 1.0)
        px = x + s * rnd.uniform(-0.12, 0.12)
        c.wash(leaf(px, y, L, L * 0.035, a), g2 if k % 2 else g1, gd, strength=0.75, spread=0.01, layers=10, edge=0.7)
        if rnd.random() < 0.35:   # a broken, bent-over blade
            tip = (px + L * 0.55 * math.cos(a), y + L * 0.55 * math.sin(a))
            c.wash(leaf(tip[0], tip[1], L * 0.35, L * 0.03, a + rnd.choice((-1, 1)) * rnd.uniform(1.0, 1.6)), g1, gd, strength=0.7, layers=8, edge=0.7)
    for k in range(n):
        a = -math.pi / 2 + lean + rnd.uniform(-0.18, 0.18)
        L = s * rnd.uniform(0.75, 1.05)
        px = x + s * rnd.uniform(-0.1, 0.1)
        top = (px + L * math.cos(a), y + L * math.sin(a))
        c.ink_line([(px, y), top], width=max(2, s * 0.01), closed=False, color=(86, 104, 62), alpha=210, passes=1, jitter=0.0002)
        hx = px + L * 0.82 * math.cos(a); hy = y + L * 0.82 * math.sin(a)
        hl = s * rnd.uniform(0.13, 0.17)
        head = ellipse(hx, hy, hl / 2, s * 0.028, 16, a)
        c.wash(head, brown2, brown, strength=0.9, spread=0.01, layers=14, edge=0.8, ang=0.0)
        c.dry_brush([(hx - math.cos(a) * hl * 0.4 - s * 0.012, hy - math.sin(a) * hl * 0.4), (hx + math.cos(a) * hl * 0.4 - s * 0.012, hy + math.sin(a) * hl * 0.4)],
                    s * 0.01, '#4a2c1a', strength=0.5, bristles=3)
        c.lift(ellipse(hx + s * 0.01, hy, hl * 0.3, s * 0.008, 10, a), amount=0.3, soft=0.3)


def lily_pads(c, x, y, s, P, n=4, flower=True):
    """Floating lily pads (flat ellipses with a notch) and one white water lily.
    (x, y) = centre of the group, s = its spread."""
    rnd = c.rnd
    g1 = P.get('pad', '#7fa860'); g2 = P.get('pad2', '#c3d48a'); gd = P.get('pad_dark', '#46703f')
    spots = [(x + s * rnd.uniform(-1, 1), y + s * rnd.uniform(-0.25, 0.25)) for _ in range(n)]
    for k, (px, py) in enumerate(spots):
        r = s * rnd.uniform(0.18, 0.3)
        a0 = rnd.uniform(0, 2 * math.pi)
        pts = [(px, py)]
        for j in range(26):
            a = a0 + 0.35 + (2 * math.pi - 0.7) * j / 25
            pts.append((px + r * math.cos(a), py + r * 0.32 * math.sin(a)))
        c.wash(pts, g2, g1, strength=0.8, spread=0.006, layers=14, edge=0.75, vary=gd, vary_amt=0.3)
        c.ink_line([(px, py), (px + r * 0.8 * math.cos(a0 + 2.2), py + r * 0.26 * math.sin(a0 + 2.2))], width=max(1, s * 0.006), closed=False, alpha=100, passes=1)
    if flower:
        fx, fy = spots[0][0] + s * 0.05, spots[0][1] - s * 0.04
        for k in range(7):
            ang = -math.pi / 2 + (k - 3) * 0.42
            c.wash(petal(fx, fy, s * 0.13, s * 0.045, ang), '#fbf6ef', '#f0c6d2', strength=0.45, layers=10, edge=0.9)
        c.wash(ellipse(fx, fy - s * 0.02, s * 0.03, s * 0.02, 10), '#f2c64b', None, strength=0.85, layers=8, edge=0.7)
        c.ink_line(smooth([(fx - s * 0.13, fy), (fx, fy + s * 0.02), (fx + s * 0.13, fy)], 1, closed=False), width=max(1, s * 0.006), closed=False, alpha=110, passes=1)


# ---------------------------------------------------------------- spring and summer birth flowers (Gemini)
# Gemini, simplified: Castor's figure (tau, theta, epsilon down to mu and eta) and Pollux's (upsilon, delta, zeta down to
# gamma), joined at the shoulders through iota (positions from the stars' RA/Dec)
CONSTELLATIONS.setdefault('gemini', {
    'stars': [(-0.58, -0.64), (-0.79, -0.3), (0.55, 0.72), (0.43, -0.05), (0.84, 0.18), (1.0, 0.18), (-0.29, 0.23), (0.03, 0.35),
              (-0.11, -0.49), (0.25, -0.82), (-0.61, -0.2), (-0.4, -0.28), (-0.77, 0.02), (0.72, 0.38), (-0.25, 0.7)],
    'lines': [(0, 8), (8, 9), (8, 3), (3, 4), (4, 5), (3, 13), (1, 10), (10, 6), (6, 7), (7, 2), (6, 14), (1, 12), (10, 11), (11, 8)],
    'bright': [0, 1, 2]})


def _ruffled(cx, cy, rx, ry, rot, rnd, freq=7, amp=0.07, n=36):
    ph = rnd.uniform(0, 6.3)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1 + amp * math.sin(freq * t + ph) + amp * 0.4 * math.sin(2.3 * freq * t + ph * 2)
        ex, ey = rx * k * math.cos(t), ry * k * math.sin(t)
        pts.append((cx + ex * math.cos(rot) - ey * math.sin(rot), cy + ex * math.sin(rot) + ey * math.cos(rot)))
    return pts


def _rose_leaflet(x, y, L, W, angle, teeth=9, n=40):
    """An ovate rose leaflet with a finely toothed edge, base at (x, y), pointing along angle."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        u = (1 - math.cos(t)) / 2                       # 0 at the base, 1 at the tip
        w = W * math.sin(math.pi * u) ** 0.8 * (1 - 0.25 * u)
        tooth = 1 + 0.08 * abs(math.sin(teeth * math.pi * u))
        side = 1 if t < math.pi else -1
        px, py = L * u, side * w * tooth
        pts.append((x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)))
    return pts


def rose_leaves(c, x, y, s, P, angle=0.0, n=3):
    """A rose leaf: a short reddish-green stalk with a pair (or two) of toothed
    leaflets and a larger one at the tip, each with a darker midrib.
    (x, y) = where the stalk leaves the stem, s = its length."""
    g1, g2, gd = P.get('leaf', '#4f8358'), P.get('leaf2', '#9cc08f'), P.get('leaf_dark', '#2e5a3c')
    ca, sa = math.cos(angle), math.sin(angle)
    at = lambda t: (x + s * t * ca, y + s * t * sa)
    c.wash(_band([at(0), at(0.55), at(0.95)], s * 0.025, s * 0.015), P.get('stalk', '#8a6a4a'), g1, strength=0.7, layers=8, edge=0.7)
    spots = [(0.95, 0.0, 0.5, 0.24)]
    pairs = [(0.6, 0.38, 0.18), (0.3, 0.32, 0.15)][:max(1, (n - 1) // 2)]
    for t, L, W in pairs:
        for side in (-1, 1):
            spots.append((t, side * 0.9, L, W))
    for t, da, L, W in spots[::-1]:
        bx, by = at(t)
        aa = angle + da
        lf = _rose_leaflet(bx, by, s * L, s * W, aa)
        c.wash(lf, g2, g1, strength=0.72, spread=0.015, layers=14, edge=1.15, ang=aa, vary=gd, vary_amt=0.35)
        tip = (bx + s * L * 0.85 * math.cos(aa), by + s * L * 0.85 * math.sin(aa))
        c.wash(_band([(bx, by), tip], s * 0.008, s * 0.002), gd, None, strength=0.5, layers=6, edge=0.3)
        c.lift(ellipse(bx + s * L * 0.4 * math.cos(aa) - s * W * 0.35 * math.sin(aa),
                       by + s * L * 0.4 * math.sin(aa) + s * W * 0.35 * math.cos(aa), s * L * 0.22, s * W * 0.18, 10, aa),
               amount=0.22, soft=0.3)


def garden_rose(c, x, y, s, P, angle=0.0, stem=1.0, leaves=1, color=None, color2=None, bud=False, leaf_dir=-1):
    """A garden rose (June's birth flower) in three-quarter view: a cupped bloom
    with pale back petals, a deep spiralled centre, ruffled side petals and broad
    front petals whose rolled rims are lifted to the paper, on a stem with toothed
    rose leaves. (x, y) = middle of the bloom, s = its width."""
    rnd = c.rnd
    col = color or P.get('rose', '#e27a8c'); col2 = color2 or P.get('rose2', '#f8c9cf'); col3 = P.get('rose3', '#b5475d')
    g1, g2 = P.get('leaf', '#4f8358'), P.get('leaf2', '#9cc08f')
    ca, sa = math.cos(angle), math.sin(angle)
    R = lambda px, py: (x + px * ca - py * sa, y + px * sa + py * ca)
    if stem:
        st = [R(0, s * 0.4), R(s * 0.04, s * (0.4 + 0.8 * stem)), R(-s * 0.02, s * (0.4 + 1.7 * stem))]
        c.wash(_band(st, s * 0.035, s * 0.03), g2, g1, strength=0.72, layers=10, edge=0.8)
        for k in range(leaves):
            side = (1 if k % 2 == 0 else -1) * leaf_dir
            bx, by = R(s * 0.02, s * (0.55 + 0.5 * k) * stem + s * 0.2)
            rose_leaves(c, bx, by, s * 0.62, P, angle=angle + math.pi / 2 + side * 1.05, n=3 if k else 5)
    if bud:
        bx, by = R(s * 0.42, -s * 0.18)
        c.wash(ellipse(bx, by, s * 0.1, s * 0.15, 16, angle + 0.5), col, col3, strength=0.75, layers=14, edge=1.1)
        for side in (-1, 1):
            c.wash(petal_pts(bx, by + s * 0.12, s * 0.16, s * 0.05, angle + math.pi / 2 + side * 0.35 + 0.5), g2, g1, strength=0.7, layers=8)
    # 1 a pale first wash over the whole bloom, soft-edged, deeper low down
    c.wash(_ruffled(*R(0, s * 0.02), s * 0.5, s * 0.42, angle, rnd, 5, 0.04), col2, col, strength=0.42, spread=0.03, layers=28,
           edge=0.7, ang=angle + math.pi / 2, vary=col3, vary_amt=0.12)
    # 2 one pale back petal rising behind the cup
    c.wash(_ruffled(*R(0, -s * 0.22), s * 0.34, s * 0.15, angle, rnd, 4, 0.05), col2, col, strength=0.3, spread=0.02, layers=16,
           edge=1.0, ang=angle - math.pi / 2)
    # 3 the open centre: a dark cup with petals spiralling in
    cx, cy = R(0, -s * 0.07)
    c.wash(ellipse(cx, cy, s * 0.22, s * 0.13, 24, angle), col3, col, strength=0.5, spread=0.02, layers=16, edge=0.9)
    a = rnd.uniform(0, 6.28)
    for i, (r, th, st_) in enumerate(((0.2, 0.06, 0.5), (0.14, 0.05, 0.6), (0.09, 0.04, 0.75), (0.05, 0.03, 0.9))):
        a += 2.1
        cr = crescent(cx, cy, s * r, a, a + 3.3, s * th, n=16)
        cr = [(cx + (px - cx), cy + (py - cy) * 0.62) for px, py in cr]
        c.wash(cr, col3 if i > 1 else col, None, strength=st_, spread=0.02, layers=12, edge=1.1)
    # 4 two side petals cupping the centre, rims lifted to light
    for side in (-1, 1):
        c.wash(_ruffled(*R(side * s * 0.3, s * 0.05), s * 0.19, s * 0.26, angle + side * 0.45, rnd, 4, 0.05), col2, col,
               strength=0.4, spread=0.02, layers=16, edge=1.05, ang=angle + side * 0.6, vary=col3, vary_amt=0.15)
        c.lift(ellipse(*R(side * s * 0.34, -s * 0.1), s * 0.08, s * 0.03, 12, angle + side * 0.8), amount=0.4, soft=0.35)
    # 5 one broad front petal; its rolled rim is lifted back to the paper
    c.wash(_ruffled(*R(0, s * 0.22), s * 0.34, s * 0.18, angle, rnd, 4, 0.04), col, col3, strength=0.42, spread=0.02,
           layers=18, edge=1.1, ang=angle + math.pi / 2, vary=col3, vary_amt=0.2)
    c.lift(ellipse(*R(0, s * 0.11), s * 0.27, s * 0.045, 18, angle), amount=0.55, soft=0.3)
    # soft shadow under the front petal, and a glint on the brightest rim
    c.wash(ellipse(*R(0, s * 0.37), s * 0.24, s * 0.05, 16, angle), col3, None, strength=0.25, spread=0.03, layers=8, edge=0.4)
    gouache(c, ellipse(*R(-s * 0.1, s * 0.11), s * 0.04, s * 0.012, 10, angle - 0.15), color=(255, 246, 246), alpha=170, soft=0.2)


def _curved_leaf(p0, p1, p2, W, n=26, tip=0.3):
    """A smooth lance-shaped leaf along a quadratic curve p0 (base) -> p2 (tip), widest a third of the way up."""
    def at(t):
        return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        (ax, ay), (bx, by) = at(max(0, t - 0.01)), at(min(1, t + 0.01))
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = W * math.sin(math.pi * t) ** 0.65 * (1 - tip * t)
        x, y = at(t)
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))
    return left + right[::-1], at


def lily_valley(c, x, y, s, P, facing=1, bells=6, leaves=2):
    """Lily of the valley (May's birth flower): two broad, ribbed leaves, and an
    arching stem hung with nodding white bells with scalloped rims, shaded grey-green
    so white reads on white, largest near the stem and smaller to the tip.
    (x, y) = base of the stem, s = its height."""
    rnd = c.rnd
    g1, g2, gd = P.get('leaf', '#4f8358'), P.get('leaf2', '#9cc08f'), P.get('leaf_dark', '#2e5a3c')
    f = facing
    for k in range(leaves):
        side = -f if k == 0 else f
        L = s * (0.92 if k == 0 else 0.74)
        p0, p1, p2 = (x, y), (x + side * s * 0.3, y - L * 0.5), (x + side * s * 0.16, y - L)
        lf, at = _curved_leaf(p0, p1, p2, s * 0.13)
        c.wash(lf, g2, g1, strength=0.68, spread=0.012, layers=16, edge=1.1, ang=-math.pi / 2, vary=gd, vary_amt=0.3)
        for rib in (-0.45, 0.0, 0.45):
            pts = []
            for j in range(1, 10):
                t = j / 10
                (ax, ay), (bx, by) = at(max(0, t - 0.01)), at(min(1, t + 0.01))
                L2 = math.hypot(bx - ax, by - ay) or 1
                w = rib * s * 0.13 * math.sin(math.pi * t) ** 0.65 * (1 - 0.3 * t)
                px, py = at(t)
                pts.append((px - (by - ay) / L2 * w, py + (bx - ax) / L2 * w))
            c.wash(_band(pts, s * 0.005, s * 0.002), gd, None, strength=0.3, layers=5, edge=0.3)
        mx, my = at(0.45)
        c.lift(ellipse(mx + side * s * 0.03, my, s * 0.03, s * 0.12, 10, side * 0.3), amount=0.22, soft=0.4)
    path = smooth([(x + f * s * 0.02, y), (x + f * s * 0.06, y - s * 0.55), (x + f * s * 0.2, y - s * 0.97), (x + f * s * 0.5, y - s * 1.05),
                   (x + f * s * 0.76, y - s * 0.9)], 2, closed=False)
    c.wash(_band(path, s * 0.018, s * 0.009), g2, g1, strength=0.78, layers=10, edge=0.8)
    n = len(path)
    for b in range(bells):
        t = 0.42 + 0.56 * b / max(1, bells - 1)
        i = min(n - 1, int(t * (n - 1)))
        px, py = path[i]
        sz = s * (0.175 - 0.075 * b / max(1, bells - 1))
        drop = sz * (0.95 if b % 2 == 0 else 0.75)
        hx, hy = px + f * sz * 0.08, py + drop          # the bell hangs on a short curved pedicel
        ped = smooth([(px, py), (px + f * sz * 0.16, py + drop * 0.35), (hx, hy - sz * 0.42)], 2, closed=False)
        c.wash(_band(ped, sz * 0.05, sz * 0.04), g2, g1, strength=0.72, layers=8, edge=0.7)
        if b >= bells - 1:                              # the last one is a round bud
            gouache(c, ellipse(hx, hy - sz * 0.12, sz * 0.3, sz * 0.34, 18), color=(252, 252, 246), alpha=235, soft=0.03)
            c.wash(ellipse(hx, hy - sz * 0.12, sz * 0.3, sz * 0.34, 18), '#f4f6ee', '#c2cfc0', strength=0.4, layers=10, edge=1.3)
            continue
        dome = [(hx - sz * 0.45 * math.cos(math.pi * j / 20), hy - sz * 0.36 - sz * 0.14 * math.sin(math.pi * j / 20)) for j in range(21)]
        shape = [(hx - sz * 0.56, hy + sz * 0.05), (hx - sz * 0.48, hy - sz * 0.28)] + dome + [(hx + sz * 0.48, hy - sz * 0.28),
                                                                                              (hx + sz * 0.56, hy + sz * 0.05)]
        for j in range(30, -1, -1):                      # scalloped rim, five little flared lobes
            u = j / 30
            shape.append((hx + sz * 0.56 * (u * 2 - 1), hy + sz * 0.05 + sz * 0.1 * abs(math.sin(u * math.pi * 5))))
        shape = smooth(shape, 1)
        gouache(c, shape, color=(252, 252, 247), alpha=240, soft=0.02)
        c.wash(shape, '#f7f7f1', '#c8d3d0', strength=0.42, spread=0.006, layers=14, edge=1.5, ang=-math.pi / 2)
        c.wash(_band([(hx + f * sz * 0.3, hy - sz * 0.3), (hx + f * sz * 0.36, hy + sz * 0.02)], sz * 0.07, sz * 0.05), '#b6c4c2', None,
               strength=0.22, layers=8, edge=0.3)
        c.ink_line(shape, width=max(1, sz * 0.022), alpha=95, passes=1, jitter=0, color=(96, 118, 112))
        gouache(c, ellipse(hx - f * sz * 0.2, hy - sz * 0.2, sz * 0.07, sz * 0.12, 8), color=(255, 255, 255), alpha=230, soft=0.15)



# ---------------------------------------------------------------- kitchen herbs
def _at_path(path, t):
    """Point and direction (radians) at fraction t along a polyline."""
    n = len(path) - 1
    f = max(0.0, min(1.0, t)) * n
    i = min(n - 1, int(f)); u = f - i
    (ax, ay), (bx, by) = path[i][:2], path[i + 1][:2]
    return (ax + (bx - ax) * u, ay + (by - ay) * u), math.atan2(by - ay, bx - ax)


def _snap(c, box):
    """A cheap local snapshot (only inside box) for _front."""
    import numpy as np
    x0, y0, x1, y1 = max(0, int(box[0])), max(0, int(box[1])), min(c.w, int(box[2])), min(c.h, int(box[3]))
    ink = np.asarray(c.ink.crop((x0, y0, x1, y1)).getchannel('A'), dtype=np.float32)
    return (x0, y0, x1, y1), c.cover[y0:y1, x0:x1].copy(), ink, c.paint[y0:y1, x0:x1].copy()


def _front(c, snap):
    """Like Canvas.paint_around, inside the snapshot's box: what was painted since
    the snapshot is in front, and later leaves and stems go around it."""
    import numpy as np
    from PIL import Image, ImageFilter
    (x0, y0, x1, y1), cov0, ink0, p0 = snap
    ink1 = np.asarray(c.ink.crop((x0, y0, x1, y1)).getchannel('A'), dtype=np.float32)
    m = np.clip(np.maximum((c.cover[y0:y1, x0:x1] - cov0) * 4, (ink1 - ink0) / 64), 0, 1)
    m = np.maximum(m, np.clip((c.paint[y0:y1, x0:x1] - p0) * 3, 0, 1))
    im = Image.fromarray((m * 255).astype(np.uint8))
    m = np.asarray(im.filter(ImageFilter.GaussianBlur(max(0.8, c.w / 3500))), dtype=np.float32) / 255
    if c.occl is None:
        c.occl = np.zeros((c.h, c.w), dtype=np.float32)
    c.occl[y0:y1, x0:x1] = np.maximum(c.occl[y0:y1, x0:x1], m)


def _herb_leaf(c, p0, p1, p2, W, cols, veins='ink', teeth=0, strength=0.72, shade=0.3, gran=0.35, outline=0, widest=0.62,
               pebble=0, n=28, bias=1.0):
    """One painted herb leaf along a curve p0 (base) -> p1 -> p2 (tip), W = half its width:
    a light first wash with darker pigment drifting in, the lower half shaded wet on dry,
    a midrib and side veins (pen-dark, or lifted pale for glossy and downy leaves), a lifted
    highlight on the upper half, optional toothed edge, pebbled texture and fine outline."""
    light, mid, dark = cols
    rnd = c.rnd

    def at(t):
        return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

    def nrm(t):
        (ax, ay), (bx, by) = at(max(0, t - 0.01)), at(min(1, t + 0.01))
        L = math.hypot(bx - ax, by - ay) or 1
        return -(by - ay) / L, (bx - ax) / L

    def width(t):
        w = W * math.sin(math.pi * t ** bias) ** widest * (1 - 0.3 * t)
        if teeth:
            w *= 1 + 0.1 * abs(math.sin(teeth * math.pi * t)) * min(1.0, t * 5)
        return w

    left, right, rib = [], [], []
    for i in range(n + 1):
        t = i / n
        x, y = at(t); nx, ny = nrm(t); w = width(t)
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w)); rib.append((x, y))
    shape = left + right[::-1]
    ang = math.atan2(p2[1] - p0[1], p2[0] - p0[0])
    length = math.hypot(p2[0] - p0[0], p2[1] - p0[1])
    c.wash(shape, light, mid, strength=strength, spread=0.01, layers=14, edge=1.1, granulate=gran, ang=ang, vary=dark, vary_amt=0.3)
    nx, ny = nrm(0.5)
    low, up = (left, 1) if ny > 0 else (right, -1)          # light from above: shade the lower half
    if shade:
        inner = [(rx + (lx - rx) * 0.45, ry + (ly - ry) * 0.45) for (rx, ry), (lx, ly) in zip(rib, low)]
        c.wash(inner + low[::-1], mid, dark, strength=shade, spread=0.014, layers=12, edge=0.0, granulate=gran, blur=W * 0.3, clip=shape)
    if pebble:                                               # velvety, pebbled surface (sage): little lifted bumps
        for _ in range(pebble):
            t = rnd.uniform(0.12, 0.88); side = rnd.uniform(-0.8, 0.8)
            x, y = at(t); qx, qy = nrm(t); w = width(t) * side
            r = W * rnd.uniform(0.05, 0.09)
            c.lift(ellipse(x + qx * w, y + qy * w, r, r * 0.8, 7, ang), amount=0.22, soft=0.45)
    if veins:
        main = rib[1:int(n * 0.9)]
        if veins == 'lift':
            c.lift(_band(main, W * 0.06, W * 0.025), amount=0.5, soft=W * 0.03 / max(1.0, length), clip=shape)
        else:
            c.wash(_band(main, W * 0.05, W * 0.015), dark, None, strength=0.55, layers=5, edge=0.3)
        for k in range(4):
            t0 = 0.14 + 0.17 * k; t1 = min(0.95, t0 + 0.15)
            for side in (1, -1):
                x0, y0 = at(t0); x1, y1 = at(t1); qx, qy = nrm(t1); w = width(t1) * 0.74 * side
                v = [(x0, y0), ((x0 + x1) / 2 + qx * w * 0.55, (y0 + y1) / 2 + qy * w * 0.55), (x1 + qx * w, y1 + qy * w)]
                if veins == 'lift':
                    c.lift(_band(v, W * 0.035, W * 0.012), amount=0.4, soft=W * 0.03 / max(1.0, length * 0.3), clip=shape)
                else:
                    c.wash(_band(v, W * 0.032, W * 0.01), dark, None, strength=0.38, layers=4, edge=0.3)
    hx, hy = at(0.4); w = width(0.4)
    c.lift(ellipse(hx - up * nx * w * 0.45, hy - up * ny * w * 0.45, length * 0.15, w * 0.22, 10, ang), amount=0.26, soft=0.35)
    if outline:
        c.ink_line(shape, width=max(1, W * 0.035), alpha=outline, passes=1, jitter=0, color=_rgb(dark))
    return shape


def _dew(c, x, y, r):
    """A drop of water on a leaf: a clear bead with a shadowed lower rim and a white glint."""
    c.wash(ellipse(x, y, r, r * 0.92, 14), '#e3efe6', None, strength=0.2, layers=6, edge=1.6)
    c.wash(ellipse(x + r * 0.2, y + r * 0.38, r * 0.62, r * 0.3, 12), '#24502f', None, strength=0.32, layers=5, edge=0.7)
    gouache(c, ellipse(x - r * 0.32, y - r * 0.34, r * 0.3, r * 0.22, 9, -0.5), color=(255, 255, 255), alpha=245, soft=0.08)
    gouache(c, ellipse(x + r * 0.35, y + r * 0.2, r * 0.09, r * 0.07, 6), color=(255, 255, 255), alpha=170, soft=0.2)


def _stem_path(x, y, s, lean, height=0.86):
    return smooth([(x, y), (x + s * 0.01, y - s * height * 0.35), (x + s * lean * 0.6, y - s * height * 0.72), (x + s * lean, y - s * height)],
                  2, closed=False)


def _crown(c, tip, s, sizes, cols, box=None, **kw):
    tx, ty = tip
    for a, L in sizes:
        snap = _snap(c, box) if box else None
        LL = s * L
        p2 = (tx + LL * math.cos(a), ty - LL * math.sin(a))
        p1 = (tx + LL * 0.5 * math.cos(a) + LL * 0.08 * math.sin(a), ty - LL * 0.5 * math.sin(a) + LL * 0.05)
        b0 = (tx + LL * 0.06 * math.cos(a), ty - LL * 0.06 * math.sin(a))
        _herb_leaf(c, b0, p1, p2, LL * kw.get('wf', 0.3), cols, **{k: v for k, v in kw.items() if k != 'wf'})
        if snap:
            _front(c, snap)


def _pairs(c, path, s, nodes, cols, wf, droop=0.1, box=None, petioles=None, pet=0.12, **kw):
    arch = kw.pop('arch', 0.12)
    """Opposite leaf pairs along a stem: nodes = [(t, length, upward angle)], painted
    from the top pair down, each pair in front of the ones below it."""
    rnd = c.rnd
    shapes = []
    for t, L, up in sorted(nodes, key=lambda n: -n[0]):
        snap = _snap(c, box) if box else None
        (px, py), th = _at_path(path, t)
        for side in (-1, 1):
            a = up + rnd.uniform(-0.06, 0.06)
            LL = s * L * rnd.uniform(0.95, 1.04)
            p2 = (px + side * LL * math.cos(a), py - LL * math.sin(a) + LL * droop)
            p1 = (px + side * LL * 0.5, py - LL * math.sin(a) * 1.1 - LL * arch)
            b0 = (px + (p1[0] - px) * pet * 2, py + (p1[1] - py) * pet * 2)      # the blade starts past a short petiole
            if petioles is not None:
                petioles.append([(px, py), ((px + b0[0]) / 2, (py + b0[1]) / 2 + LL * 0.01), (b0[0] + (p1[0] - b0[0]) * 0.08, b0[1] + (p1[1] - b0[1]) * 0.08)])
            shapes.append((_herb_leaf(c, b0, p1, p2, LL * wf, cols, **kw), b0, p1, p2, LL))
        if snap:
            _front(c, snap)
    return shapes[::-1]


def _sprig(c, x, y, s, P, cols, stem_cols, nodes, wf, crown, crown_wf, lean, droop, leaf_kw, crown_kw, stem_w=0.017):
    """A cut sprig: crown leaves first, then the opposite pairs from the top down
    (each in front of the ones below), then the stem last so it passes behind."""
    path = _stem_path(x, y, s, lean)
    box = (x - s * 0.62, y - s * 1.12, x + s * 0.62, y + s * 0.08)
    tip, _ = _at_path(path, 0.95)
    _crown(c, tip, s, crown, cols, box=box, wf=crown_wf, **crown_kw)
    k = max(3, int(len(path) * 0.95))
    path = path[:k] + [tip]
    pets = []
    leaves = _pairs(c, path, s, nodes, cols, wf, droop=droop, box=box, petioles=pets, **leaf_kw)
    c.wash(_band(path, s * stem_w, s * stem_w * 0.5), stem_cols[0], stem_cols[1], strength=0.8, layers=10, edge=0.8, spread=0.004)
    for p in pets:
        c.wash(_band(smooth(p, 2, closed=False), s * stem_w * 0.38, s * stem_w * 0.26), stem_cols[0], stem_cols[1], strength=0.8, layers=8,
               edge=0.8, spread=0.01)
    # the stem's shadow side, a darker line wet on dry
    c.wash(_band([(px + s * stem_w * 0.4, py) for px, py in path[1:-1]], s * stem_w * 0.2, s * stem_w * 0.1), stem_cols[1], None,
           strength=0.22, layers=5, edge=0.3, spread=0.004)
    return path, leaves


def basil(c, x, y, s, P, lean=0.04, dew=True):
    """Sweet basil: a green stem with pairs of broad, glossy, cupped leaves with
    pointed tips that arch out and droop, smaller toward the crown, with pale
    lifted veins and a glossy highlight, and a tuft of young leaves on top.
    (x, y) = the cut end of the stem, s = the sprig's height."""
    cols = (P.get('basil2', '#acd67e'), P.get('basil', '#5c9b38'), P.get('basil_dark', '#2b6224'))
    kw = dict(veins='lift', strength=0.78, shade=0.22, gran=0.22, outline=55, bias=0.78, widest=0.85)
    path, leaves = _sprig(c, x, y, s, P, cols, ('#98c76c', '#4f8a32'),
                          [(0.26, 0.44, 0.2), (0.52, 0.36, 0.42), (0.75, 0.27, 0.68)], 0.28,
                          [(math.pi / 2 + 0.72, 0.15), (math.pi / 2 - 0.72, 0.15), (math.pi / 2 + 0.06, 0.17)], 0.3, lean, 0.05,
                          dict(kw, arch=0.06), dict(kw, strength=0.72, shade=0.22))
    if dew:
        _, (px, py), p1, p2, LL = leaves[1]
        _dew(c, (px + p1[0] * 2 + p2[0]) / 4, (py + p1[1] * 2 + p2[1]) / 4 + LL * 0.04, s * 0.024)


def sage(c, x, y, s, P, lean=-0.03):
    """Garden sage: a sturdy pale stem with pairs of long oval grey-green leaves,
    velvety and pebbled (granulated pigment, lifted bumps and pale net veins),
    and a small crown of young silvery leaves."""
    cols = (P.get('sage2', '#cfdac4'), P.get('sage', '#8ba487'), P.get('sage_dark', '#4f664d'))
    kw = dict(veins='lift', strength=0.76, shade=0.28, gran=0.9, outline=45, pebble=16)
    _sprig(c, x, y, s, P, cols, ('#b3bea6', '#7c8b71'),
           [(0.22, 0.45, 0.34), (0.5, 0.37, 0.6), (0.74, 0.27, 0.86)], 0.2,
           [(math.pi / 2 + 0.45, 0.15), (math.pi / 2 - 0.45, 0.15), (math.pi / 2, 0.12)], 0.22, lean, 0.04,
           kw, dict(kw, strength=0.64, shade=0.18, pebble=5), stem_w=0.018)


def mint(c, x, y, s, P, lean=0.03, dew=True):
    """Spearmint: a square green stem with pairs of bright, toothed, oval leaves
    with deep pen-dark veins, smaller up the stem, and a tight tip of new leaves."""
    cols = (P.get('mint2', '#b4dd98'), P.get('mint', '#4c9e4f'), P.get('mint_dark', '#245c31'))
    kw = dict(veins='ink', teeth=12, strength=0.78, shade=0.28, gran=0.25, outline=75, bias=0.85)
    path, leaves = _sprig(c, x, y, s, P, cols, ('#84bd6c', '#3f7f3c'),
                          [(0.26, 0.36, 0.12), (0.5, 0.31, 0.36), (0.72, 0.24, 0.62)], 0.31,
                          [(math.pi / 2 + 0.55, 0.13), (math.pi / 2 - 0.55, 0.13), (math.pi / 2 + 0.05, 0.1)], 0.34, lean, 0.13,
                          kw, dict(kw, teeth=8, strength=0.72, shade=0.2), stem_w=0.016)
    c.lift(_band(path[2:-2], s * 0.005, s * 0.003), amount=0.3, soft=0.3)
    if dew:
        _, (px, py), p1, p2, LL = leaves[0]
        _dew(c, (px + p1[0] * 2 + p2[0]) / 4, (py + p1[1] * 2 + p2[1]) / 4 + LL * 0.05, s * 0.022)


def _tiny_flower(c, x, y, r, col, col2, dark, petals=5, rot=0.0, strength=0.75):
    for k in range(petals):
        a = rot + 2 * math.pi * k / petals
        c.wash(petal(x, y, r, r * 0.45, a), col2, col, strength=strength, layers=5, edge=1.1)
    c.wash(ellipse(x, y, r * 0.2, r * 0.2, 8), dark, None, strength=0.75, layers=4, edge=0.6)


def rosemary(c, x, y, s, P, flowers=5):
    """Rosemary: a woody brown sprig with two side shoots, set with narrow,
    leathery needle leaves that point forward along the stem (green-grey above,
    a silvery underside showing on some), tufted at the tips, with small pale
    blue flowers tucked among the upper leaves. (x, y) = base, s = height."""
    rnd = c.rnd
    top, under, dk = P.get('rosemary', '#4d7c66'), P.get('rosemary2', '#b2c9bd'), P.get('rosemary_dark', '#2f5244')
    main = smooth([(x, y), (x + s * 0.02, y - s * 0.4), (x - s * 0.01, y - s * 0.7), (x + s * 0.03, y - s * 0.94)], 3, closed=False)
    paths = [(main, 1.0)]
    for t, side, L in ((0.22, -1, 0.62), (0.38, 1, 0.55)):
        (bx, by), th = _at_path(main, t)
        ba = -math.pi / 2 + side * 0.75
        paths.append((smooth([(bx, by), (bx + side * s * 0.13, by - L * s * 0.3), (bx + side * s * 0.22 + L * s * 0.12 * math.cos(ba), by - L * s * 0.92)],
                             3, closed=False), L))
    snap = _snap(c, (x - s * 0.6, y - s * 1.1, x + s * 0.6, y + s * 0.05))
    for f in range(flowers):
        path, L = paths[f % len(paths)]
        (px, py), th = _at_path(path, 0.5 + 0.13 * (f // len(paths)) + rnd.uniform(-0.04, 0.04))
        side = 1 if f % 2 else -1
        nx, ny = -math.sin(th), math.cos(th)
        fx, fy = px + side * nx * s * 0.06, py + side * ny * s * 0.06
        _tiny_flower(c, fx, fy, s * 0.036, P.get('rosemary_fl', '#7896d8'), P.get('rosemary_fl2', '#d7e2f7'), '#3f4f8f',
                     petals=4, rot=rnd.uniform(0, 1.5), strength=0.85)
    _front(c, snap)                                   # the flowers sit in front of the needles
    for path, L in paths:
        c.wash(_band(path, s * 0.013 * (0.7 + 0.3 * L), s * 0.005), '#a08a6c', '#6e5c46', strength=0.84, layers=8, edge=0.8, spread=0.005)
    for path, L in paths:
        n = int(34 * L) + 6
        for i in range(n):
            t = (0.14 if L == 1.0 else 0.08) + (0.84 if L == 1.0 else 0.9) * i / (n - 1)
            (px, py), th = _at_path(path, t)
            side = 1 if i % 2 else -1
            na = th + side * (0.6 + 0.25 * (1 - t)) + rnd.uniform(-0.1, 0.1)
            nl = s * (0.105 - 0.03 * t) * rnd.uniform(0.88, 1.08)
            silver = rnd.random() < 0.3
            c.wash(leaf(px, py, nl, nl * 0.15, na), under if silver else '#86a898', '#8aa99c' if silver else top, strength=0.85,
                   spread=0.02, layers=5, edge=1.15, granulate=0.2)
            c.wash(_band([(px, py), (px + nl * 0.9 * math.cos(na), py + nl * 0.9 * math.sin(na))], nl * 0.028, nl * 0.008), dk, None,
                   strength=0.45 if not silver else 0.2, layers=3, edge=0.3)
        (px, py), th = _at_path(path, 1.0)
        for da in (-0.32, -0.1, 0.12, 0.34):
            nl = s * 0.058
            c.wash(leaf(px - s * 0.02 * math.cos(th), py - s * 0.02 * math.sin(th), nl, nl * 0.15, th + da), '#86a898', top,
                   strength=0.85, layers=5, edge=1.1)


def thyme(c, x, y, s, P, stems=6):
    """Thyme: a bunch of thin, wiry red-brown stems that branch as they rise,
    set with small oval grey-green leaves in pairs and tipped with little round
    clusters of pale pink-lilac flowers. (x, y) = base, s = height."""
    rnd = c.rnd
    lt, md, dk = P.get('thyme2', '#c3d6a2'), P.get('thyme', '#7a9a5e'), P.get('thyme_dark', '#4b6a40')
    fl, fl2, fld = '#dc9cc3', '#f6d9e8', '#9c5583'
    paths = []
    for k in range(stems):
        off = (k - (stems - 1) / 2) / ((stems - 1) / 2)
        a = -math.pi / 2 + off * 0.46 + rnd.uniform(-0.05, 0.05)
        L = s * (0.96 - 0.22 * abs(off)) * rnd.uniform(0.9, 1.0)
        pts = [(x + off * s * 0.018, y)]
        for j in range(1, 6):
            t = j / 5
            wob = s * 0.02 * math.sin(t * 5 + k)
            pts.append((x + L * t * math.cos(a) - wob * math.sin(a), y + L * t * math.sin(a) + wob * math.cos(a)))
        path = smooth(pts, 2, closed=False)
        paths.append((path, L))
        if k % 2 == 0:
            (bx, by), th = _at_path(path, 0.5)
            ba = th + (0.45 if off >= 0 else -0.45)
            bl = L * 0.34
            bp = smooth([(bx, by), (bx + bl * 0.5 * math.cos(ba), by + bl * 0.5 * math.sin(ba)), (bx + bl * math.cos(ba), by + bl * math.sin(ba))],
                        2, closed=False)
            paths.append((bp, bl))
    for path, L in paths:
        c.wash(_band(path, s * 0.0058, s * 0.0028), '#9a6c58', '#77523f', strength=0.85, layers=6, edge=0.8, spread=0.006)
    for path, L in paths:
        m = max(4, int(L / (s * 0.05)))
        for i in range(m):
            t = 0.14 + 0.8 * i / max(1, m - 1) + rnd.uniform(-0.015, 0.015)
            (px, py), th = _at_path(path, t)
            for side in (-1, 1):                          # tiny elliptic leaves in pairs, angled forward
                la = th + side * (0.9 + rnd.uniform(-0.2, 0.2))
                ll = s * rnd.uniform(0.034, 0.044) * (1 - 0.3 * t)
                c.wash(leaf(px, py, ll, ll * 0.3, la), lt, md, strength=0.85, spread=0.02, layers=4, edge=1.15, vary=dk, vary_amt=0.3)
        (tx, ty), th = _at_path(path, 1.0)
        cx_, cy_ = tx + s * 0.018 * math.cos(th), ty + s * 0.018 * math.sin(th)
        c.wash(ellipse(cx_, cy_, s * 0.026, s * 0.024, 12), fl2, fl, strength=0.45, layers=6, edge=1.0)
        for j in range(11):
            a = rnd.uniform(0, 2 * math.pi); rr = s * 0.024 * math.sqrt(rnd.random())
            fx, fy = cx_ + rr * math.cos(a), cy_ + rr * math.sin(a)
            c.wash(ellipse(fx, fy, s * 0.012, s * 0.0095, 8, a), fl2, fl, strength=0.8, layers=4, edge=1.2)
            if j % 3 == 0:
                c.wash(ellipse(fx, fy, s * 0.0035, s * 0.0035, 6), fld, None, strength=0.7, layers=3, edge=0.6)


def _chive_bloom(c, x, y, r):
    """A chive flower head: a round pom-pom of tiny lilac-pink star florets,
    shaded on the lower right, with a papery bract below."""
    rnd = c.rnd
    c.wash(ellipse(x, y, r, r * 0.95, 20), '#efd6f1', '#c99bd5', strength=0.55, layers=14, edge=1.0, vary='#a873b8', vary_amt=0.35,
           granulate=0.4)
    for k in range(44):
        a = rnd.uniform(0, 2 * math.pi); rr = r * math.sqrt(rnd.uniform(0.04, 1)) * 0.86
        fx, fy = x + rr * math.cos(a), y + rr * math.sin(a) * 0.95
        for p in range(3):
            pa = a + (p - 1) * 0.6 + rnd.uniform(-0.2, 0.2)
            c.wash(petal(fx, fy, r * 0.28, r * 0.09, pa), '#e8c6ec', '#c196cf', strength=0.45, layers=4, edge=0.6)
    c.wash(ellipse(x + r * 0.32, y + r * 0.36, r * 0.62, r * 0.48, 14, 0.6), '#7c4a8e', None, strength=0.2, layers=8, edge=0.5)
    for k in range(6):
        a = rnd.uniform(3.4, 4.6); rr = r * rnd.uniform(0.25, 0.7)
        gouache(c, ellipse(x + rr * math.cos(a), y + rr * math.sin(a), r * 0.05, r * 0.04, 7), color=(252, 238, 252), alpha=210, soft=0.15)
    c.wash(leaf(x - r * 0.05, y + r * 0.82, r * 0.42, r * 0.13, math.pi / 2 + 0.25), '#ece4cc', '#c2b28a', strength=0.6, layers=6, edge=1.0)


def chives(c, x, y, s, P, blooms=3, leaves=9):
    """Chives: a clump of long, hollow, grass-like leaves with a pale lifted line
    down each, and taller flower stalks topped with round lilac pom-pom blossoms."""
    rnd = c.rnd
    g, g2, gd = P.get('chive2', '#94c26a'), P.get('chive', '#4a8a38'), P.get('chive_dark', '#2c5e29')
    for k in range(leaves):
        off = (k - (leaves - 1) / 2) / ((leaves - 1) / 2)
        a = -math.pi / 2 + off * 0.34 + rnd.uniform(-0.04, 0.04)
        L = s * rnd.uniform(0.6, 0.8)
        curve = s * 0.07 * off
        path = smooth([(x + off * s * 0.035, y), (x + L * 0.5 * math.cos(a) + curve * 0.25, y + L * 0.5 * math.sin(a)),
                       (x + L * math.cos(a) + curve, y + L * math.sin(a))], 3, closed=False)
        c.wash(_band(path, s * 0.011, s * 0.003), g, g2, strength=0.76, layers=7, edge=0.9, vary=gd, vary_amt=0.25, spread=0.005)
        c.lift(_band(path[2:-3], s * 0.003, s * 0.001), amount=0.3, soft=0.3)
    heads = []
    for b in range(blooms):
        off = (b - (blooms - 1) / 2)
        a = -math.pi / 2 + off * 0.3
        L = s * (0.9 if off == 0 else 0.76)
        path = smooth([(x + off * s * 0.02, y), (x + L * 0.5 * math.cos(a) - off * s * 0.02, y + L * 0.5 * math.sin(a)),
                       (x + L * math.cos(a), y + L * math.sin(a))], 3, closed=False)
        c.wash(_band(path, s * 0.009, s * 0.007), g, g2, strength=0.76, layers=7, edge=0.9, spread=0.005)
        heads.append(path[-1])
    for hx, hy in heads:
        r = s * 0.085
        _chive_bloom(c, hx, hy - r * 0.8, r)


# ---------------------------------------------------------------- lovebirds (couples)
LB_BODY = ((0.30, -0.66), (0.50, -0.62), (0.64, -0.50), (0.72, -0.34), (0.70, -0.18), (0.62, -0.04), (0.56, 0.12), (0.44, 0.32),
           (0.24, 0.46), (0.0, 0.52), (-0.24, 0.48), (-0.44, 0.40), (-0.62, 0.46), (-0.86, 0.56), (-0.90, 0.48), (-0.70, 0.30),
           (-0.52, 0.14), (-0.40, -0.06), (-0.24, -0.28), (-0.04, -0.48), (0.12, -0.60))
LB_FACE = ((0.64, -0.50), (0.72, -0.34), (0.70, -0.18), (0.60, -0.06), (0.46, -0.04), (0.32, -0.12), (0.24, -0.30), (0.26, -0.50),
           (0.36, -0.62), (0.50, -0.62))
LB_WING = ((0.22, -0.16), (0.02, -0.28), (-0.24, -0.20), (-0.46, 0.02), (-0.66, 0.34), (-0.40, 0.30), (-0.10, 0.30), (0.14, 0.18),
           (0.26, 0.02))
LB_TAIL = ((-0.52, 0.28), (-0.86, 0.52), (-0.92, 0.60), (-0.78, 0.62), (-0.50, 0.44))
LB_BEAK = ((0.62, -0.42), (0.78, -0.40), (0.88, -0.28), (0.86, -0.15), (0.78, -0.17), (0.72, -0.11), (0.62, -0.16))
LOVEBIRD_COATS = {
    # peach-faced lovebird: grass green, a rosy peach face, a blue rump
    'green': dict(light='#b9dc86', body='#6fb35c', dark='#2f7445', wing='#4e9654', face='#f8b493', face2='#e8656b', rump='#5aa6dc',
                  ink=(40, 70, 45)),
    # a blue-green (aqua) bird with the same peach face
    'teal': dict(light='#a9ddd2', body='#4fa9a2', dark='#246d72', wing='#3c8f93', face='#f8b493', face2='#e8656b', rump='#6f8fd8',
                 ink=(30, 64, 70)),
    # a golden (lutino) bird with a rose face
    'yellow': dict(light='#fbe9a0', body='#eec455', dark='#b98a26', wing='#e0ad3c', face='#f9b09a', face2='#e45d6a', rump='#f2e6c0',
                   ink=(110, 80, 30)),
}


def _lovebird(c, x, y, u, facing, coat, P):
    """One plump lovebird, side-on, facing 1 = right; (x, y) = middle of the body, u = its unit size."""
    k = LOVEBIRD_COATS.get(coat, LOVEBIRD_COATS['green'])
    def pts(seq):
        return [(x + facing * px * u, y + py * u) for px, py in seq]
    body = smooth(pts(LB_BODY), rounds=2)
    # 1 the whole bird in one light wash, the colour pooling low on the belly
    c.wash(body, k['light'], k['body'], strength=0.6, spread=0.02, layers=28, edge=1.0, granulate=0.3, vary=k['dark'], vary_amt=0.12,
           ang=math.pi / 2)
    # 2 a warm glow on the breast, the tail and rump glazed wet on dry
    c.wash(ellipse(x + facing * 0.36 * u, y + 0.12 * u, 0.2 * u, 0.16 * u, 14), k['light'], None, strength=0.22, layers=10)
    c.wash(smooth(pts(LB_TAIL), rounds=1), k['body'], k['dark'], strength=0.5, spread=0.03, layers=14, edge=0.9)
    c.wash(ellipse(x - facing * 0.5 * u, y + 0.3 * u, 0.13 * u, 0.07 * u, 12, facing * 0.5), k['rump'], None, strength=0.4,
           spread=0.03, layers=12, edge=0.9)
    # 3 the wing: darker, with three rows of scalloped feather edges
    wing = smooth(pts(LB_WING), rounds=2)
    c.wash(wing, k['wing'], k['dark'], strength=0.55, spread=0.025, layers=18, edge=1.0, ang=math.pi / 2)
    for row, (fx, fy, n) in enumerate(((-0.02, -0.12, 3), (-0.2, 0.06, 3), (-0.36, 0.2, 2))):
        for i in range(n):
            cx_ = fx - i * 0.12 + row * 0.04
            arc = [(x + facing * (cx_ + 0.06 * math.cos(t)) * u, y + (fy + 0.05 * math.sin(t)) * u)
                   for t in [math.pi * (0.1 + 0.8 * j / 6) for j in range(7)]]
            c.ink_line(arc, width=max(1, u * 0.018), closed=False, alpha=95, passes=1, jitter=0, color=k['ink'])
    # a soft shadow along the belly, wet on dry
    c.wash(smooth(pts(((0.5, 0.12), (0.3, 0.4), (0.0, 0.5), (-0.3, 0.44), (-0.1, 0.36), (0.22, 0.26))), rounds=2), k['body'], None,
           strength=0.22, spread=0.03, layers=10, edge=0.5)
    # 4 the rosy face mask, deepest on the forehead: the green is lifted off first so the peach stays clean
    face = smooth(pts(LB_FACE), rounds=2)
    c.lift(face, amount=0.93, soft=0.04)
    c.wash(face, k['face'], k['face2'], strength=0.62, spread=0.02, layers=18, edge=0.9, ang=-math.pi / 2)
    c.wash(ellipse(x + facing * 0.5 * u, y - 0.52 * u, 0.13 * u, 0.08 * u, 14, facing * 0.2), k['face2'], None, strength=0.35,
           spread=0.03, layers=10, edge=0.6)
    # 5 the hooked beak in pale horn, a line between the halves
    beak = smooth(pts(LB_BEAK), rounds=1)
    c.wash(beak, '#f3c995', '#d9895a', strength=0.9, spread=0.01, layers=14, edge=1.0, ang=math.pi / 2)
    c.ink_line(beak, width=max(1, u * 0.016), alpha=110, passes=1, jitter=0, color=(130, 80, 55))
    c.ink_line(pts(((0.70, -0.25), (0.86, -0.22))), width=max(1, u * 0.016), closed=False, alpha=120, passes=1, jitter=0,
               color=(120, 80, 60))
    # 6 a lifted highlight on the crown, the eye with a pale ring and catch light
    c.lift(ellipse(x + facing * 0.34 * u, y - 0.52 * u, 0.14 * u, 0.05 * u, 14, -facing * 0.35), amount=0.4, soft=0.35)
    ex, ey = pts(((0.47, -0.36),))[0]
    c.wash(ellipse(ex, ey, u * 0.058, u * 0.064, 12), '#141012', None, strength=1.4, spread=0.01, layers=10, blur=1)
    gouache(c, ellipse(ex + facing * u * 0.018, ey - u * 0.02, u * 0.018, u * 0.018, 8), alpha=240, soft=0.1)
    # 7 a loose outline, and two feet gripping the branch
    c.ink_line(body, width=max(2, u * 0.022), alpha=130, passes=1, jitter=0, color=k['ink'])
    for fx in (-0.06, 0.16):
        top = (fx, 0.44); bot = (fx + 0.03, 0.62)
        c.ink_line(pts((top, bot)), width=max(2, u * 0.03), closed=False, alpha=170, passes=1, jitter=0, color=(150, 110, 100))
        for dx in (-0.07, 0.0, 0.07):
            c.ink_line(pts((bot, (bot[0] + dx, bot[1] + 0.05))), width=max(1, u * 0.022), closed=False, alpha=150, passes=1,
                       jitter=0, color=(150, 110, 100))


def lovebirds(c, x, y, s, P, pair=('green', 'teal'), angle=0.0, heart=True, flowers=True):
    """Two lovebirds on a branch, turned to each other with their beaks almost
    touching, a small painted heart between them and blossoms on the branch.
    (x, y) = between the birds, s = half the width of the scene."""
    rnd = c.rnd
    u = s * 0.42
    occ0 = None if c.occl is None else c.occl.copy()
    g0 = c.snapshot()
    for side, coat in ((-1, pair[0]), (1, pair[1])):
        _lovebird(c, x + side * s * 0.44, y + rnd.uniform(-0.02, 0.02) * s, u, -side, coat, P)
    # the birds are in front: the branch, leaves and blossoms go around them
    c.paint_around(g0)
    by = y + s * 0.27
    if flowers:
        # three little blossoms on the branch (five petals, a gold centre), painted before the branch so it passes behind them
        g1_ = c.snapshot()
        for fx, fdy in ((0.0, -0.03), (-0.97, 0.0), (0.97, -0.01)):
            fx_, fy_ = x + fx * s, by + fdy * s
            for i in range(5):
                a = i * 2 * math.pi / 5 + rnd.uniform(-0.2, 0.2)
                c.wash(ellipse(fx_ + s * 0.045 * math.cos(a), fy_ + s * 0.045 * math.sin(a), s * 0.045, s * 0.034, 12, a),
                       P.get('blossom', '#f6c3cc'), P.get('blossom2', '#e98a9c'), strength=0.6, spread=0.03, layers=12, edge=1.0)
            c.wash(ellipse(fx_, fy_, s * 0.02, s * 0.02, 10), '#f1c45a', '#d99a32', strength=0.8, layers=8, edge=0.9)
        c.paint_around(g1_)
    br = [(x - s * 0.98, by + s * 0.05), (x - s * 0.5, by + s * 0.01), (x, by - s * 0.01), (x + s * 0.5, by + s * 0.0),
          (x + s * 0.98, by + s * 0.04)]
    c.wash(_band(br, s * 0.038, s * 0.026), '#b48a64', '#7a5238', strength=0.7, spread=0.02, layers=14, edge=1.0, granulate=0.5)
    c.dry_brush(br, s * 0.03, '#5a3a28', strength=0.45, bristles=5)
    g1, g2, gd = P.get('leaf', '#5f9365'), P.get('leaf2', '#a9cc95'), P.get('leaf_dark', '#2f5c3e')
    for end in (-1, 1):
        bx, by2 = x + end * s * 0.9, by + s * 0.04
        for a, L in ((end * 0.5 - 0.9, 0.3), (end * 0.9 + 0.2, 0.26), (end * 0.2 + 0.6, 0.22)):
            tip = (bx + math.cos(a) * s * L, by2 + math.sin(a) * s * L)
            mid = (bx + math.cos(a + 0.25) * s * L * 0.5, by2 + math.sin(a + 0.25) * s * L * 0.5)
            shape, _ = _curved_leaf((bx, by2), mid, tip, s * 0.05)
            c.wash(shape, g2, g1, strength=0.62, spread=0.02, layers=14, edge=1.0, vary=gd, vary_amt=0.15)
            c.ink_line([(bx, by2), mid, tip], width=max(1, s * 0.006), closed=False, alpha=80, passes=1, jitter=0, color=(40, 70, 45))
    if heart:
        hx, hy, hs = x, y - s * 0.4, s * 0.11
        hp = [(hx + hs * 0.06 * 16 * math.sin(t) ** 3,
               hy - hs * 0.06 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
              for t in [i / 28 * 2 * math.pi for i in range(28)]]
        c.wash(hp, P.get('heart', '#e0566a'), P.get('heart2', '#f29aa6'), strength=0.75, spread=0.02, layers=20, edge=1.1,
               ang=-math.pi / 4)
        c.lift(ellipse(hx - hs * 0.42, hy - hs * 0.35, hs * 0.22, hs * 0.12, 12, -0.6), amount=0.5, soft=0.3)
    c.occl = occ0



# ---------------------------------------------------------------- birthday cake (2026-11-13)
def _teardrop(cx, cy, L, W, ang, n=18):
    """A piped shell or drop: round head at (cx, cy), the tail running out to
    length L along ang, widest W."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        X = L * (1 + math.cos(t)) / 2 - L * 0.18
        Y = W / 2 / 0.77 * math.sin(t) * math.sin(t / 2)
        pts.append((X, Y))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + px * ca - py * sa, cy + px * sa + py * ca) for px, py in pts]


def _ring_shells(c, x, y, rx, ry, a0, a1, n, L, W, cols, front_first=True, strength=0.58):
    """A piped shell border along an ellipse from angle a0 to a1: each shell's
    tail runs on along the rim. Even shells are painted first and the odd ones
    go around them, so neighbours overlap cleanly instead of showing through."""
    cream, shade, rim = cols
    heads = []
    for k in range(n):
        a = a0 + (a1 - a0) * (k + 0.5) / n
        px, py = x + rx * math.cos(a), y + ry * math.sin(a)
        tx, ty = -rx * math.sin(a), ry * math.cos(a)
        ang = math.atan2(ty, tx) if (a1 > a0) else math.atan2(-ty, -tx)
        # seen edge-on at the sides of the cake, a shell is foreshortened to a short round blob
        fs = max(0.4, math.hypot(tx, ty) / rx)
        heads.append((px, py, ang, fs))
    for parity in (0, 1):
        g = c.snapshot()
        for k, (px, py, ang, fs) in enumerate(heads):
            if k % 2 != parity:
                continue
            Lk, Wk = L * fs, W * (0.8 + 0.2 * fs)
            shp = _teardrop(px, py, Lk, Wk, ang)
            c.wash(shp, cream, shade, strength=strength, spread=0.02, layers=12, edge=1.15, granulate=0.15, ang=math.pi / 2)
            # the shell's ridge and its shadowed underside
            c.wash(_teardrop(px + Wk * 0.05, py + Wk * 0.3, Lk * 0.85, Wk * 0.55, ang), rim, None, strength=0.34, spread=0.02,
                   layers=8, edge=0.0, blur=Wk * 0.18, clip=shp)
            hx, hy = px - Wk * 0.1, py - Wk * 0.16
            gouache(c, ellipse(hx, hy, Wk * 0.2, Wk * 0.09, 10, ang), color=(255, 252, 246), alpha=150, soft=0.35)
        c.paint_around(g)
    return heads


def _pearl(c, px, py, r, col=(255, 252, 246), alpha=235):
    gouache(c, ellipse(px, py, r, r, 10), color=col, alpha=alpha, soft=0.12)


def _flame2(c, x, y, h):
    """A candle flame standing on its wick: (x, y) = the wick's tip, h = the
    flame's height. A soft warm glow with no edge, a round-bottomed teardrop in
    orange to gold, a pale core in gouache and a breath of blue at the base."""
    c.glow(x, y - h * 0.5, h * 1.0, '#f9e2a0', strength=0.3)
    outer = _teardrop(x, y - h * 0.2, h * 1.02, h * 0.44, -math.pi / 2, n=30)
    c.wash(outer, '#f6c456', '#ee9a34', strength=0.95, spread=0.008, layers=14, edge=1.0, granulate=0.08, ang=math.pi / 2)
    c.wash(ellipse(x, y - h * 0.05, h * 0.1, h * 0.08, 10), '#7f9fd2', None, strength=0.45, layers=8, edge=0.2, blur=h * 0.03,
           clip=outer)
    core = _teardrop(x, y - h * 0.24, h * 0.62, h * 0.24, -math.pi / 2, n=24)
    gouache(c, core, color=(255, 247, 222), alpha=225, soft=0.14)


def _candle(c, x, y, s, h, col, P, stripe=(255, 250, 244)):
    """A thin birthday candle standing on the cake top: (x, y) = middle of its
    base, s = the cake's scale, h = its height. Round shading, white spiral
    stripes in gouache, a waxy top, a dark wick and a lit flame with a glow."""
    from motifs import flame
    w = s * 0.042
    body = rect(x - w, y - h, x + w, y, 4)
    dark = _shade(col, 0.68)
    c.wash(body, col, None, strength=0.75, spread=0.004, layers=14, edge=1.0, granulate=0.2)
    c.wash(rect(x + w * 0.25, y - h, x + w, y, 3), dark, None, strength=0.4, spread=0.004, layers=8, edge=0.5, clip=body)
    # spiral stripes: parallelograms that climb around the candle
    step = w * 2.6
    k = 0
    yy = y - step * 0.6
    while yy - w * 1.2 > y - h + w * 0.6:
        band = [(x - w * 0.96, yy), (x + w * 0.96, yy - w * 1.15), (x + w * 0.96, yy - w * 1.15 - w * 0.7), (x - w * 0.96, yy - w * 0.7)]
        gouache(c, band, color=stripe, alpha=205, soft=0.04)
        yy -= step; k += 1
    c.lift(rect(x - w * 0.55, y - h + w * 0.5, x - w * 0.2, y - w * 0.4, 2), amount=0.35, soft=0.2)
    # waxy top and wick
    c.wash(ellipse(x, y - h, w, w * 0.35, 10), _shade(col, 1.12), None, strength=0.6, layers=8, edge=0.9)
    c.ink_line([(x, y - h), (x + w * 0.1, y - h - s * 0.04)], width=max(1.5, w * 0.2), closed=False, jitter=0, passes=1,
               alpha=230, color=(46, 36, 34))
    _flame2(c, x + w * 0.1, y - h - s * 0.012, s * 0.2)


def _satin_bow(c, x, y, s, col, P):
    """A satin ribbon bow (the coquette bow): two full loops with a shaded
    inner fold, a knot and long tails with notched ends, lifted where the
    satin catches the light. (x, y) = the knot, s = half the width."""
    dk = _shade(col, 0.62); lt = _shade(col, 1.25)
    for side in (-1, 1):
        loop = [(x, y - s * 0.02), (x + side * s * 0.35, y - s * 0.5), (x + side * s * 0.82, y - s * 0.58), (x + side * s * 1.0, y - s * 0.32),
                (x + side * s * 0.86, y + s * 0.0), (x + side * s * 0.4, y + s * 0.1)]
        loop = smooth(loop, 2)
        c.wash(loop, col, dk, strength=0.85, spread=0.01, layers=16, edge=1.1, ang=math.pi / 2 if side > 0 else math.pi / 2 + 0.3)
        fold = [(x + side * s * 0.15, y - s * 0.06), (x + side * s * 0.45, y - s * 0.34), (x + side * s * 0.7, y - s * 0.3),
                (x + side * s * 0.45, y - s * 0.08)]
        c.wash(smooth(fold, 2), dk, None, strength=0.5, spread=0.01, layers=10, edge=0.0, blur=s * 0.07, clip=loop)
        c.lift(ellipse(x + side * s * 0.62, y - s * 0.46, s * 0.16, s * 0.05, 12, side * 0.25), amount=0.5, soft=0.35, clip=loop)
    for side in (-1, 1):
        tail = [(x + side * s * 0.0, y + s * 0.09), (x + side * s * 0.22, y + s * 0.45), (x + side * s * 0.42, y + s * 0.95),
                (x + side * s * 0.3, y + s * 0.88), (x + side * s * 0.2, y + s * 1.02), (x + side * s * 0.12, y + s * 0.5),
                (x + side * s * 0.03, y + s * 0.12)]
        c.wash(tail, col, dk, strength=0.8, spread=0.01, layers=14, edge=1.0, ang=math.pi / 2)
        c.lift(_band([(x + side * s * 0.08, y + s * 0.12), (x + side * s * 0.2, y + s * 0.5), (x + side * s * 0.3, y + s * 0.82)],
                     s * 0.025, s * 0.015), amount=0.4, soft=0.3, clip=tail)
    knot = ellipse(x, y, s * 0.16, s * 0.14, 14)
    c.wash(knot, col, dk, strength=1.0, spread=0.01, layers=12, edge=1.0)
    c.lift(ellipse(x - s * 0.04, y - s * 0.04, s * 0.06, s * 0.035, 10), amount=0.5, soft=0.3)
    gouache(c, ellipse(x - s * 0.05, y - s * 0.05, s * 0.025, s * 0.015, 8), color=tuple(min(255, int(v)) for v in _rgb(lt)), alpha=150, soft=0.3)


def _cherry(c, px, py, r, P, stem_dir=1):
    """A glossy cherry with its stem: deep red, darker low down, a lifted
    highlight and a white glint; the stem curves up and back."""
    red, red2, red3 = P.get('cherry', '#c42b3f'), P.get('cherry2', '#e0566a'), P.get('cherry_dark', '#7a1426')
    st = [(px + r * 0.05, py - r * 0.75), (px + stem_dir * r * 0.35, py - r * 1.6), (px + stem_dir * r * 0.9, py - r * 2.35)]
    c.wash(_band(st, r * 0.09, r * 0.05), '#7d8a3c', '#5c4a2a', strength=0.85, spread=0.01, layers=8, edge=1.0)
    body = [(px + r * 1.0 * math.cos(t) * (1 - 0.06 * math.sin(t) ** 8), py + r * 0.94 * math.sin(t) + (r * 0.12 if math.sin(t) < -0.8 else 0))
            for t in [2 * math.pi * i / 26 for i in range(26)]]
    c.wash(body, red2, red, strength=0.9, spread=0.01, layers=16, edge=1.1, ang=math.pi / 2 + 0.5)
    c.wash(ellipse(px + r * 0.3, py + r * 0.45, r * 0.8, r * 0.55, 14, 0.4), red3, None, strength=0.65, spread=0.02, layers=10, edge=0.0,
           blur=r * 0.3, clip=body)
    c.lift(ellipse(px - r * 0.38, py - r * 0.3, r * 0.26, r * 0.17, 12, -0.6), amount=0.55, soft=0.3, clip=body)
    gouache(c, ellipse(px - r * 0.42, py - r * 0.36, r * 0.1, r * 0.065, 8, -0.6), color=(255, 248, 246), alpha=225, soft=0.2)


def birthday_cake(c, x, y, s, P, candles=5, cherries=True, bow=True, stand=True):
    """A vintage piped layer cake on a milk-glass cake stand, lit for a
    birthday: pale pink frosting with a piped shell border at the top and the
    foot, Lambeth-style swags with rosettes, sugar pearls and string loops, a
    satin bow, glossy cherries round the top and striped candles with flames.
    (x, y) = middle of the cake's bottom edge, s = the cake's half-width."""
    rnd = c.rnd
    e = 0.3
    Hc = s * 0.95
    yT = y - Hc
    pink, pink2, pink3 = P.get('frost', '#f6c6cd'), P.get('frost2', '#fbe3e5'), P.get('frost_dark', '#e08e9d')
    cream, cream_sh, cream_rim = P.get('pipe', '#fdf3ea'), P.get('pipe2', '#f4cfd2'), P.get('pipe_dark', '#e2a3ad')
    string = P.get('string', '#d9677e')
    occ0 = None if c.occl is None else c.occl.copy()

    def top_pt(a, k=1.0):
        return (x + s * k * math.cos(a), yT + s * e * k * math.sin(a))

    # 1 candles, front row first so the back row goes around it, with a warm glow above
    if candles:
        spots = [(-0.52, 0.04, 0.62), (0.0, -0.04, 0.58), (0.52, 0.04, 0.6), (-0.27, -0.46, 0.7), (0.27, -0.46, 0.68)][:candles]
        cols = P.get('candles', ['#8fb7e0', '#f2cf6b', '#9ccfb4', '#f2a0b4', '#b9a3dd'])
        order = sorted(range(len(spots)), key=lambda i: -spots[i][1])
        c.glow(x, yT - s * 0.78, s * 0.75, '#f9e2a6', strength=0.22)
        for i in order:
            u, v, hh = spots[i]
            g = c.snapshot()
            _candle(c, x + s * u, yT + s * e * v, s, s * hh, cols[i % len(cols)], P)
            c.paint_around(g)
    # 2 cherries on rosettes round the top rim (back ones go around the candles)
    if cherries:
        for a in (1.22 * math.pi, 1.78 * math.pi, 0.08 * math.pi, 0.5 * math.pi, 0.92 * math.pi):
            px, py = top_pt(a, 0.86)
            g = c.snapshot()
            _cherry(c, px, py - s * 0.075, s * 0.085, P, stem_dir=1 if math.cos(a) >= 0 else -1)
            c.paint_around(g)
    # 3 the bow, pinned at the front of the top swag
    ys = yT + Hc * 0.36
    if bow:
        g = c.snapshot()
        _satin_bow(c, x, ys + s * e + s * 0.02, s * 0.26, P.get('bow', '#c8324a'), P)
        c.paint_around(g)
    # 4 piping: the top shell border (back half, then front), rosettes and swags, the foot border
    g = c.snapshot()
    _ring_shells(c, x, yT, s * 0.97, s * e * 0.97, math.pi, 2 * math.pi, 12, s * 0.33, s * 0.12, (cream, cream_sh, cream_rim))
    c.paint_around(g)
    g = c.snapshot()
    _ring_shells(c, x, yT + s * 0.01, s * 0.99, s * e * 0.99, 0.0, math.pi, 12, s * 0.34, s * 0.13, (cream, cream_sh, cream_rim))
    c.paint_around(g)
    joins = [0.07 * math.pi + k * 0.86 * math.pi / 6 for k in range(7)]
    # rosettes with a hanging drop under each join
    g = c.snapshot()
    for k, a in enumerate(joins):
        px, py = x + s * math.cos(a), ys + s * e * math.sin(a)
        if bow and k == 3:
            continue
        rr = s * 0.058 * (0.7 + 0.3 * math.sin(a))
        c.wash(ellipse(px, py, rr, rr * 0.92, 16), cream, cream_sh, strength=0.45, spread=0.02, layers=12, edge=1.15, ang=math.pi / 2)
        ang0 = rnd.uniform(0, 6.28)
        c.wash(crescent(px, py, rr * 0.55, ang0, ang0 + 3.6, rr * 0.22, n=12), cream_rim, None, strength=0.35, layers=8, edge=0.9)
        c.wash(_teardrop(px, py + rr * 2.1, rr * 1.5, rr * 0.75, -math.pi / 2), cream, cream_sh, strength=0.42, spread=0.02, layers=10,
               edge=1.1, ang=math.pi / 2)
    c.paint_around(g)
    # swags (drapes) between the joins, each with sugar pearls along it
    g = c.snapshot()
    pearls = []
    for k in range(6):
        a0, a1 = joins[k], joins[k + 1]
        path = []
        for i in range(13):
            t = i / 12
            a = a0 + (a1 - a0) * t
            path.append((x + s * math.cos(a), ys + s * e * math.sin(a) + Hc * 0.17 * math.sin(math.pi * t)))
        w0 = s * 0.05
        left, right = [], []
        for i, (px, py) in enumerate(path):
            nx, ny = _path_normal(path, i)
            w = w0 * (0.35 + 0.65 * math.sin(math.pi * i / 12))
            left.append((px + nx * w, py + ny * w)); right.append((px - nx * w, py - ny * w))
        band = left + right[::-1]
        c.wash(band, cream, cream_sh, strength=0.45, spread=0.015, layers=12, edge=1.15, ang=math.pi / 2)
        low = [(px, py + w0 * 0.55) for px, py in path[1:12]]
        c.wash(_band(low, w0 * 0.45, w0 * 0.45), cream_rim, None, strength=0.32, layers=8, edge=0.0, blur=w0 * 0.35, clip=band)
        hi = [(px, py - w0 * 0.35) for px, py in path[3:10]]
        gouache(c, _band(hi, w0 * 0.12, w0 * 0.08), color=(255, 252, 247), alpha=140, soft=0.2)
        pearls += [path[i] for i in (3, 6, 9)]
    c.paint_around(g)
    # string loops below the swags, a fine line in deeper pink
    for k in range(6):
        a0, a1 = joins[k], joins[k + 1]
        path = []
        for i in range(15):
            t = i / 14
            a = a0 + (a1 - a0) * t
            path.append((x + s * math.cos(a), ys + s * e * math.sin(a) + Hc * 0.3 * math.sin(math.pi * t)))
        c.wash(_band(path, s * 0.009, s * 0.009), string, None, strength=0.7, spread=0.01, layers=8, edge=1.0)
    g = c.snapshot()
    _ring_shells(c, x, y + s * 0.015, s * 1.02, s * e * 1.02, -0.04 * math.pi, 1.04 * math.pi, 13, s * 0.33, s * 0.14,
                 (cream, cream_sh, cream_rim), strength=0.5)
    c.paint_around(g)
    # 5 the frosted top and the round side, shaded like a cylinder (light from the upper left)
    g5 = c.snapshot()
    top = ellipse(x, yT, s, s * e, 40)
    c.wash(top, pink2, pink, strength=0.42, spread=0.01, layers=22, edge=0.6, ang=math.pi / 2, vary=pink, vary_amt=0.2)
    body = [(x + s, yT), (x + s, y)] + [(x + s * math.cos(a), y + s * e * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]] + \
           [(x - s, yT)] + [(x + s * math.cos(a), yT + s * e * math.sin(a)) for a in [math.pi * (30 - i) / 30 for i in range(31)]]
    c.wash(body, pink2, pink, strength=0.58, spread=0.006, layers=26, edge=0.8, ang=0.0, vary=pink3, vary_amt=0.15, granulate=0.25)
    c.wash(rect(x + s * 0.4, yT - s * 0.3, x + s * 1.25, y + s * 0.5, 3), pink3, None, strength=0.36, spread=0.03, layers=14, edge=0.0,
           blur=s * 0.16, clip=body)
    c.wash(rect(x - s * 1.3, yT - s * 0.3, x - s * 0.88, y + s * 0.5, 3), pink3, None, strength=0.2, spread=0.03, layers=10, edge=0.0,
           blur=s * 0.08, clip=body)
    c.wash(ellipse(x, y + s * e * 0.2, s * 1.1, s * 0.16, 24), pink3, None, strength=0.22, spread=0.03, layers=10, edge=0.0, blur=s * 0.06,
           clip=body)
    c.lift(rect(x - s * 0.66, yT + s * 0.15, x - s * 0.42, y + s * 0.2, 3), amount=0.28, soft=0.45, clip=body)
    c.paint_around(g5)
    # 6 the milk-glass cake stand: plate, rim with hobnail dots, stem and foot; a soft shadow under the cake
    if stand:
        g1, g2, g3 = P.get('stand', '#d5ebe2'), P.get('stand2', '#a9cfc1'), P.get('stand_dark', '#6f9f8f')
        yp = y + s * 0.07
        R = s * 1.32
        c.wash(ellipse(x + s * 0.12, yp - s * 0.02, s * 1.05, s * e * 1.02, 30), g3, None, strength=0.3, spread=0.03, layers=12, edge=0.3)
        c.wash(ellipse(x, yp, R, R * e, 40), g1, g2, strength=0.45, spread=0.008, layers=20, edge=0.9, ang=math.pi / 2)
        th = s * 0.1
        rim = [(x + R * math.cos(a), yp + R * e * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]] + \
              [(x + R * math.cos(a), yp + th + R * e * math.sin(a)) for a in [math.pi * (30 - i) / 30 for i in range(31)]]
        c.wash(rim, g2, g3, strength=0.55, spread=0.008, layers=16, edge=1.0, ang=0.0)
        for k in range(15):
            a = math.pi * (k + 0.5) / 15
            hx, hy = x + R * math.cos(a), yp + th * 0.5 + R * e * math.sin(a)
            _pearl(c, hx, hy, s * 0.022 * (0.55 + 0.45 * math.sin(a)), col=(246, 252, 249), alpha=200)
        yb = yp + R * e + th
        yf = y + s * 0.72
        stem = [(x - s * 0.17, yb - s * 0.02), (x - s * 0.08, yb + s * 0.1), (x - s * 0.06, yf - s * 0.2), (x - s * 0.13, yf - s * 0.1),
                (x - s * 0.1, yf - s * 0.04), (x + s * 0.1, yf - s * 0.04), (x + s * 0.13, yf - s * 0.1), (x + s * 0.06, yf - s * 0.2),
                (x + s * 0.08, yb + s * 0.1), (x + s * 0.17, yb - s * 0.02)]
        gs = c.snapshot()
        stem_shape = smooth(stem, 2)
        c.wash(stem_shape, g1, g2, strength=0.6, spread=0.01, layers=16, edge=1.0, ang=0.0)
        c.wash(rect(x + s * 0.01, yb - s * 0.05, x + s * 0.2, yf, 2), g3, None, strength=0.3, layers=8, edge=0.0, blur=s * 0.03, clip=stem_shape)
        c.wash(ellipse(x, yb + s * 0.03, s * 0.2, s * 0.045, 14), g3, None, strength=0.3, layers=10, edge=0.0, blur=s * 0.02, clip=stem_shape)
        c.lift(ellipse(x - s * 0.045, yb + s * 0.22, s * 0.022, s * 0.11, 10), amount=0.45, soft=0.3)
        c.paint_around(gs)
        fr = s * 0.6; fe = fr * e * 0.8; fth = s * 0.06
        foot_top = ellipse(x, yf, fr, fe, 36)
        foot_rim = [(x + fr * math.cos(a), yf + fe * math.sin(a)) for a in [math.pi * i / 24 for i in range(25)]] + \
                   [(x + fr * math.cos(a), yf + fth + fe * math.sin(a)) for a in [math.pi * (24 - i) / 24 for i in range(25)]]
        c.wash(foot_top, g1, g2, strength=0.45, spread=0.008, layers=16, edge=0.9, ang=math.pi / 2)
        c.wash(foot_rim, g2, g3, strength=0.55, spread=0.008, layers=14, edge=1.0, ang=0.0)
        c.lift(ellipse(x - fr * 0.5, yf + fth * 0.4 + fe * 0.8, fr * 0.2, fth * 0.25, 10, 0.2), amount=0.4, soft=0.3)
        c.lift(ellipse(x - R * 0.55, yp + th * 0.4 + R * e * 0.75, s * 0.22, s * 0.025, 12, 0.25), amount=0.4, soft=0.3)
        # shadow on the table
        c.wash(ellipse(x + s * 0.1, yf + s * 0.1, s * 0.85, s * 0.1, 24), '#c9b7c0', None, strength=0.25, spread=0.04, layers=12, edge=0.2)
    # finishing: sugar pearls on the swags and glints on the shells
    for px, py in pearls:
        _pearl(c, px, py - s * 0.004, s * 0.018)
    for a in [math.pi * (k + 0.5) / 12 for k in range(12)]:
        px, py = top_pt(a, 0.99)
        gouache(c, ellipse(px - s * 0.03, py - s * 0.035, s * 0.03, s * 0.012, 8, 0.2), color=(255, 253, 249), alpha=170, soft=0.3)
    c.occl = occ0


def confetti(c, x, y, s, P, n=70, aspect=0.95, inner=0.45, clear=None, colors=None, size=0.022, avoid=None):
    """Party confetti in watercolor: round dots, little squares and curled
    paper streamers in soft colors, scattered in a ring round a scene.
    (x, y) = centre, s = outer radius; inner = the ring's inner radius (a share
    of s); clear = boxes [x0, y0, x1, y1] in units of s from the centre to keep empty;
    avoid = round spots [dx, dy, r] in the same units (sparkles painted separately)."""
    rnd = c.rnd
    cols = colors or P.get('confetti', ['#f2a0b4', '#8fb7e0', '#f2cf6b', '#9ccfb4', '#b9a3dd', '#f4a582'])
    k = 0; tries = 0; placed = []
    while k < n and tries < n * 30:
        tries += 1
        a = rnd.uniform(0, 2 * math.pi); r = s * math.sqrt(rnd.uniform(inner ** 2, 1.0))
        px, py = x + r * math.cos(a), y + r * aspect * math.sin(a)
        if clear and any(b[0] < (px - x) / s < b[2] and b[1] < (py - y) / s < b[3] for b in clear):
            continue
        u = s * size * rnd.uniform(0.7, 1.3)
        if avoid and any(math.hypot((px - x) / s - ax, (py - y) / s - ay) < ar for ax, ay, ar in avoid):
            continue
        if any(math.hypot(px - qx, py - qy) < (u + qu) * 2.2 for qx, qy, qu in placed):
            continue
        placed.append((px, py, u))
        k += 1
        col = rnd.choice(cols); dk = _shade(col, 0.75)
        kind = rnd.choice(('dot', 'dot', 'square', 'curl', 'curl'))
        rot = rnd.uniform(0, math.pi)
        if kind == 'dot':
            c.wash(ellipse(px, py, u * 0.55, u * 0.55, 12), col, dk, strength=0.75, spread=0.03, layers=10, edge=1.1)
        elif kind == 'square':
            c.wash(_rot(rect(px - u * 0.5, py - u * 0.35, px + u * 0.5, py + u * 0.35, 1), px, py, rot), col, dk, strength=0.7,
                   spread=0.02, layers=10, edge=1.0)
        else:
            L = u * rnd.uniform(2.6, 3.6); amp = u * 0.55
            path = [(px + (t - 0.5) * L * math.cos(rot) - amp * math.sin(2 * math.pi * t) * math.sin(rot),
                     py + (t - 0.5) * L * math.sin(rot) + amp * math.sin(2 * math.pi * t) * math.cos(rot)) for t in [i / 10 for i in range(11)]]
            c.wash(_band(path, u * 0.2, u * 0.16), col, dk, strength=0.72, spread=0.02, layers=10, edge=1.05)


# ---------------------------------------------------------------- classroom (Apples & Pencils)
def _loc(x, y, a):
    """Local coords (along the object's own axis) to canvas coords."""
    ca, sa = math.cos(a), math.sin(a)
    return lambda px, py: (x + px * ca - py * sa, y + px * sa + py * ca)


def _rr(x0, y0, x1, y1, r, n=5):
    """A rounded rectangle in local coords."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        for i in range(n + 1):
            a = a0 + math.pi / 2 * i / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _mix(hexcol, k):
    """Toward white by k (0 = the color, 1 = white)."""
    r, g, b = _rgb(hexcol)
    return '#%02x%02x%02x' % tuple(int(v + (255 - v) * k) for v in (r, g, b))


def _inkc(hexcol, k=0.42):
    return tuple(int(v * k) for v in _rgb(hexcol))


APPLE_KINDS = {'red': ('#d8343f', '#f2934e', '#8c1a27'), 'green': ('#8cbd47', '#e8e07a', '#4b7a2a'),
               'gold': ('#eebd45', '#f8e6a6', '#b07a20')}


def school_apple(c, x, y, s, P, angle=0.0, color=None, leaf_side=1):
    """A glossy apple: a round body with a dimple at the stem, wet-in-wet blush
    (red over warm yellow, or green over pale yellow), a shadow low on the far
    side, a lifted highlight and a white glint, a short stem and a veined leaf."""
    kind = color if color in APPLE_KINDS else 'red'
    base, blush, dark = APPLE_KINDS[kind]
    T = _loc(x, y + s * 0.12, angle); r = s * 0.74
    body = []
    for i in range(44):
        t = 2 * math.pi * i / 44
        ct, st = math.cos(t), math.sin(t)
        px = r * ct * (1.04 - 0.1 * max(0.0, st) ** 2)
        py = r * 0.93 * st
        if st < 0:
            py += r * 0.2 * math.exp(-(ct / 0.3) ** 2) * (-st)
        else:
            py -= r * 0.06 * math.exp(-(ct / 0.25) ** 2) * st
        body.append((px, py))
    B = [T(px, py) for px, py in body]
    # leaf and stem first, so the body's edge sits over their base
    sx, sy = 0.0, -r * 0.7
    stem = [T(sx, sy), T(r * 0.04, -r * 0.92), T(r * 0.14, -r * 1.12)]
    c.wash(_band(stem, s * 0.05, s * 0.035), '#8a5a33', '#5c3a20', strength=0.9, spread=0.01, layers=8, edge=1.0)
    lx, ly = T(r * 0.08, -r * 0.95)
    la = angle - math.pi / 2 + leaf_side * 1.05
    lf = leaf(lx, ly, s * 0.62, s * 0.24, la, 16)
    c.wash(lf, '#7fb34d', '#4f8a35', strength=0.85, spread=0.012, layers=12, edge=1.0, ang=la)
    c.wash(leaf(lx, ly, s * 0.62, s * 0.12, la, 12), '#3f6f2a', None, strength=0.35, spread=0.02, layers=8, edge=0.0, blur=s * 0.03, clip=lf)
    tip = (lx + s * 0.55 * math.cos(la), ly + s * 0.55 * math.sin(la))
    c.ink_line([(lx, ly), tip], width=max(1.2, s * 0.012), closed=False, alpha=110, passes=1, jitter=0, color=(40, 70, 30))
    c.ink_line(lf, width=max(1.2, s * 0.012), alpha=120, passes=1, jitter=0, color=(40, 70, 30))
    # body
    c.wash(B, blush, base, strength=0.95, spread=0.012, layers=18, edge=1.05, ang=angle + 2.2, vary=base, vary_amt=0.6)
    c.wash([T(px, py) for px, py in ellipse(r * 0.32, r * 0.42, r * 0.72, r * 0.5, 16, -0.3)], dark, None, strength=0.6,
           spread=0.02, layers=10, edge=0.0, blur=r * 0.32, clip=B)
    c.wash([T(px, py) for px, py in ellipse(0, -r * 0.62, r * 0.24, r * 0.09, 12)], dark, None, strength=0.55, spread=0.02,
           layers=8, edge=0.0, blur=r * 0.08, clip=B)
    c.lift([T(px, py) for px, py in ellipse(-r * 0.42, -r * 0.2, r * 0.17, r * 0.3, 12, 0.45)], amount=0.62, soft=0.35, clip=B)
    gouache(c, [T(px, py) for px, py in ellipse(-r * 0.45, -r * 0.3, r * 0.06, r * 0.11, 8, 0.45)], color=(255, 250, 246), alpha=220, soft=0.2)
    c.ink_line(B, width=max(1.5, s * 0.014), alpha=135, passes=1, jitter=0, color=_inkc(dark, 0.7))
    c.ink_line(stem, width=max(1.2, s * 0.012), closed=False, alpha=150, passes=1, jitter=0, color=(70, 45, 25))


PENCIL_COLORS = ['#f2c23a', '#e8574f', '#4f8fd6', '#5fae6b', '#9b74cf', '#f28a3c', '#f07fa6']


def pencil(c, x, y, s, P, angle=0.0, color=None):
    """A six-sided wooden pencil: three painted facets (light, mid, shadow), a
    metal ferrule with ridges, a pink eraser, a shaved wood cone with the
    paint's scalloped edge, and a graphite point."""
    col = color or P.get('pencil', '#f2c23a')
    T = _loc(x, y, angle)
    L, w = s * 2.0, s * 0.3; h = w / 2
    x0 = -L / 2; xe = x0 + L * 0.11; xf = xe + L * 0.09; xb = x0 + L * 0.8; xt = x0 + L
    W = lambda pts: [T(px, py) for px, py in pts]
    # wood cone and graphite (under the body's scalloped edge)
    cone = W([(xb - w * 0.1, -h * 0.96), (xt - L * 0.055, -h * 0.24), (xt, 0), (xt - L * 0.055, h * 0.24), (xb - w * 0.1, h * 0.96)])
    c.wash(cone, '#f5dcb0', '#d7a565', strength=0.85, spread=0.01, layers=12, edge=1.0, ang=angle + math.pi / 2)
    lead = W([(xt - L * 0.06, -h * 0.25), (xt + s * 0.01, 0), (xt - L * 0.06, h * 0.25)])
    c.wash(lead, '#5b5d66', '#2f3036', strength=0.95, spread=0.008, layers=10, edge=1.1)
    # body with a scalloped painted edge at the cone
    edge_pts = [(xb + w * 0.2 * abs(math.sin(3 * math.pi * k / 18)), -h + 2 * h * k / 18) for k in range(19)]
    body = W([(xf, -h)] + edge_pts + [(xf, h)])
    c.wash(body, _mix(col, 0.15), col, strength=0.95, spread=0.008, layers=14, edge=1.0, ang=angle + math.pi / 2)
    c.wash(W([(xf, h * 0.32), (xb + w * 0.2, h * 0.32), (xb + w * 0.2, h * 1.1), (xf, h * 1.1)]), _shade(col, 0.7), None,
           strength=0.55, spread=0.01, layers=8, edge=0.6, clip=body)
    c.lift(W([(xf + L * 0.02, -h * 0.92), (xb - w * 0.1, -h * 0.92), (xb - w * 0.1, -h * 0.4), (xf + L * 0.02, -h * 0.4)]),
           amount=0.4, soft=0.15, clip=body)
    # ferrule and eraser
    fer = W(_rr(xe, -h * 1.04, xf + w * 0.02, h * 1.04, w * 0.06))
    c.wash(fer, '#dfe2e6', '#9aa1aa', strength=0.9, spread=0.006, layers=10, edge=1.0, ang=angle + math.pi / 2)
    c.lift(W([(xe, -h * 0.9), (xf, -h * 0.9), (xf, -h * 0.45), (xe, -h * 0.45)]), amount=0.45, soft=0.2, clip=fer)
    er = W(_rr(x0, -h * 0.96, xe + w * 0.05, h * 0.96, w * 0.28))
    c.wash(er, '#f6b3b6', '#e27d88', strength=0.9, spread=0.01, layers=12, edge=1.0, ang=angle + math.pi / 2)
    ic = _inkc(_shade(col, 0.6), 0.75)
    for pts in (er, fer, body, cone):
        c.ink_line(pts, width=max(1.4, s * 0.012), alpha=150, passes=1, jitter=0, color=ic)
    for k in (0.3, 0.55, 0.8):
        xx = xe + (xf - xe) * k
        c.ink_line(W([(xx, -h * 1.0), (xx, h * 1.0)]), width=max(1, s * 0.008), closed=False, alpha=110, passes=1, jitter=0, color=(90, 94, 102))
    c.ink_line(W([(xf, h * 0.32), (xb + w * 0.05, h * 0.32)]), width=max(1, s * 0.007), closed=False, alpha=70, passes=1, jitter=0, color=ic)
    c.ink_line(W([(xf, -h * 0.32), (xb + w * 0.05, -h * 0.32)]), width=max(1, s * 0.007), closed=False, alpha=60, passes=1, jitter=0, color=ic)


CRAYON_COLORS = ['#e8453c', '#3f7fd0', '#f2b631', '#4fa864', '#8d63c7', '#f27b2e', '#ef6fa0', '#35b3b0']


def crayon(c, x, y, s, P, angle=0.0, color=None):
    """A wax crayon: a rounded body in strong color, a paler paper wrapper
    with two thin bands at each end, a sloped shoulder and a blunt tip, and a
    long waxy highlight."""
    col = color or P.get('crayon', '#e8453c')
    T = _loc(x, y, angle)
    L, w = s * 1.7, s * 0.36; h = w / 2
    x0 = -L / 2; xb = x0 + L * 0.8; xt = x0 + L
    W = lambda pts: [T(px, py) for px, py in pts]
    tip = W([(xb - w * 0.1, -h), (xb + L * 0.06, -h * 0.62), (xt - L * 0.035, -h * 0.3), (xt, -h * 0.05), (xt, h * 0.05),
             (xt - L * 0.035, h * 0.3), (xb + L * 0.06, h * 0.62), (xb - w * 0.1, h)])
    c.wash(tip, _mix(col, 0.1), _shade(col, 0.82), strength=0.95, spread=0.008, layers=12, edge=1.0, ang=angle + math.pi / 2)
    body = W(_rr(x0, -h, xb, h, w * 0.14))
    c.wash(body, col, _shade(col, 0.85), strength=0.95, spread=0.008, layers=14, edge=1.0, ang=angle + math.pi / 2)
    wx0, wx1 = x0 + L * 0.08, x0 + L * 0.72
    wrap = W([(wx0, -h * 1.02), (wx1, -h * 1.02), (wx1, h * 1.02), (wx0, h * 1.02)])
    c.lift(wrap, amount=0.62, soft=0.03, clip=body)
    for k in (0.05, 0.11, 0.89, 0.95):
        xx = wx0 + (wx1 - wx0) * k
        c.wash(W([(xx - w * 0.04, -h), (xx + w * 0.04, -h), (xx + w * 0.04, h), (xx - w * 0.04, h)]), _shade(col, 0.6), None,
               strength=0.8, spread=0.005, layers=6, edge=1.0, clip=body)
    c.wash(W([(x0, h * 0.35), (xt, h * 0.35), (xt, h * 1.1), (x0, h * 1.1)]), _shade(col, 0.6), None, strength=0.45, spread=0.01,
           layers=8, edge=0.4, clip=body + tip)
    c.lift(W([(x0 + L * 0.03, -h * 0.75), (xt - L * 0.08, -h * 0.55), (xt - L * 0.08, -h * 0.3), (x0 + L * 0.03, -h * 0.4)]),
           amount=0.5, soft=0.2, clip=body + tip)
    ic = _inkc(col, 0.5)
    c.ink_line(body, width=max(1.4, s * 0.012), alpha=140, passes=1, jitter=0, color=ic)
    c.ink_line(tip, width=max(1.4, s * 0.012), alpha=140, passes=1, jitter=0, color=ic)


BOOK_COLORS = [('#c94a4a', '#e88a7a'), ('#3f6fb3', '#86aee0'), ('#4f9a62', '#9fd0a2'), ('#e0a536', '#f5d27f'), ('#8a5fb8', '#c4a6e3')]


def book_stack(c, x, y, s, P, angle=0.0, color=None, n=3):
    """A stack of hardcover books seen from the spine side: each a colored
    cover with gold bands and a pale title panel, the cream page edges showing
    at one end, and a soft shadow under each book."""
    T = _loc(x, y, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    rnd = c.rnd
    cols = list(BOOK_COLORS); rnd.shuffle(cols)
    bh = s * 0.36; y_base = s * 0.62
    for i in range(n):
        col, col2 = cols[i % len(cols)]
        bw = s * (1.6 - 0.16 * i + rnd.uniform(-0.05, 0.05)); off = s * rnd.uniform(-0.1, 0.1)
        y1 = y_base - i * bh * 0.98; y0 = y1 - bh * 0.92
        xa, xz = -bw / 2 + off, bw / 2 + off
        cover = W(_rr(xa, y0, xz, y1, bh * 0.16))
        pages = W(_rr(xz - bw * 0.09, y0 + bh * 0.13, xz + bw * 0.005, y1 - bh * 0.13, bh * 0.05))
        c.wash(cover, col2, col, strength=0.92, spread=0.008, layers=14, edge=1.0, ang=angle + math.pi / 2)
        c.wash(W([(xa, y1 - bh * 0.3), (xz, y1 - bh * 0.3), (xz, y1 + bh * 0.1), (xa, y1 + bh * 0.1)]), _shade(col, 0.65), None,
               strength=0.45, spread=0.01, layers=8, edge=0.4, clip=cover)
        gouache(c, pages, color=(250, 244, 226), alpha=245, soft=0.05)
        for k in (0.3, 0.5, 0.7):
            yy = y0 + bh * 0.13 + (bh * 0.74) * k
            c.ink_line(W([(xz - bw * 0.085, yy), (xz, yy)]), width=max(1, s * 0.006), closed=False, alpha=90, passes=1, jitter=0, color=(150, 130, 100))
        for xx in (xa + bw * 0.1, xa + bw * 0.16, xz - bw * 0.2, xz - bw * 0.14):
            c.wash(W([(xx, y0 + bh * 0.04), (xx + bw * 0.025, y0 + bh * 0.04), (xx + bw * 0.025, y1 - bh * 0.04), (xx, y1 - bh * 0.04)]),
                   '#f2cf6b', '#d9a93c', strength=0.85, spread=0.005, layers=6, edge=1.0, clip=cover)
        label = W(_rr(xa + bw * 0.3, y0 + bh * 0.3, xa + bw * 0.62, y1 - bh * 0.3, bh * 0.05))
        c.lift(label, amount=0.6, soft=0.02, clip=cover)
        c.ink_line(label, width=max(1, s * 0.007), alpha=95, passes=1, jitter=0, color=_inkc(col, 0.55))
        ic = _inkc(col, 0.5)
        c.ink_line(cover, width=max(1.4, s * 0.012), alpha=140, passes=1, jitter=0, color=ic)
        c.ink_line(pages, width=max(1, s * 0.008), alpha=110, passes=1, jitter=0, color=(150, 120, 90))


def ruler(c, x, y, s, P, angle=0.0, color=None):
    """A wooden ruler: a warm wood wash with dry-brush grain, a hanging hole,
    and inked marks along one edge (longer every fourth)."""
    T = _loc(x, y, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    L, w = s * 2.1, s * 0.34; h = w / 2
    body = W(_rr(-L / 2, -h, L / 2, h, w * 0.1))
    c.wash(body, '#f4d79b', '#d9a85c', strength=0.9, spread=0.008, layers=14, edge=1.0, ang=angle + math.pi / 2)
    for k in range(3):
        yy = -h * 0.5 + h * 0.5 * k + c.rnd.uniform(-h * 0.1, h * 0.1)
        c.dry_brush(W([(-L * 0.45, yy), (0, yy + h * 0.08), (L * 0.45, yy - h * 0.05)]), w * 0.08, '#c48a45', strength=0.35)
    c.wash(W([(-L / 2, h * 0.45), (L / 2, h * 0.45), (L / 2, h * 1.1), (-L / 2, h * 1.1)]), '#b9803f', None, strength=0.4, spread=0.01,
           layers=8, edge=0.4, clip=body)
    c.lift(W(ellipse(-L * 0.44, 0, w * 0.13, w * 0.13, 12)), amount=0.85, soft=0.05, clip=body)
    c.ink_line(W(ellipse(-L * 0.44, 0, w * 0.13, w * 0.13, 14)), width=max(1, s * 0.009), alpha=130, passes=1, jitter=0, color=(110, 70, 30))
    n = 28
    for k in range(1, n):
        xx = -L * 0.38 + (L * 0.8) * k / n
        ln = h * (0.62 if k % 4 == 0 else 0.34)
        c.ink_line(W([(xx, -h), (xx, -h + ln)]), width=max(1, s * (0.011 if k % 4 == 0 else 0.008)), closed=False, alpha=170, passes=1,
                   jitter=0, color=(90, 55, 25))
    c.ink_line(body, width=max(1.4, s * 0.012), alpha=140, passes=1, jitter=0, color=(110, 70, 30))


def paper_plane(c, x, y, s, P, angle=0.0, color=None):
    """A folded paper airplane in pale paper: the near wing light, the keel
    in shadow, crisp fold lines, and a looping dashed flight trail behind."""
    col = color or '#cfe3f5'
    T = _loc(x + s * 0.18, y, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    k = s * 0.62
    nose = (k, 0); tt = (-k * 0.95, -k * 0.62); fold = (-k * 0.55, k * 0.02); tb = (-k * 0.78, k * 0.4); keel = (-k * 0.4, k * 0.22)
    wing = W([nose, tt, fold]); low = W([nose, fold, tb]); kl = W([nose, fold, keel])
    c.wash(low, _shade(col, 0.82), None, strength=0.8, spread=0.006, layers=10, edge=1.0)
    c.wash(wing, _mix(col, 0.35), col, strength=0.75, spread=0.006, layers=10, edge=1.0, ang=angle)
    c.wash(kl, _shade(col, 0.7), None, strength=0.75, spread=0.006, layers=8, edge=1.0)
    ic = _inkc(_shade(col, 0.55), 0.6)
    for pts in (wing, low, kl):
        c.ink_line(pts, width=max(1.3, s * 0.011), alpha=150, passes=1, jitter=0, color=ic)
    # dashed loop behind the tail, inside the motif's circle
    path = []
    A, Bq = s * 0.055, s * 0.15
    for i in range(49):
        u = 2 * math.pi * i / 48
        path.append((-k * 0.9 - (A * u + Bq * math.sin(u)), k * 0.08 - Bq * (1 - math.cos(u))))
    for i in range(0, len(path) - 2, 4):
        c.ink_line(W(path[i:i + 3]), width=max(1.2, s * 0.012), closed=False, alpha=120, passes=1, jitter=0, color=(110, 120, 140))


PAINT_COLORS = ['#e8453c', '#f2b631', '#3f7fd0', '#4fa864', '#8d63c7', '#ef6fa0']


def paint_palette(c, x, y, s, P, angle=0.0, color=None):
    """An artist's palette: a wooden kidney shape with a thumb hole, glossy
    dabs of paint in bright colors, and a brush lying across it."""
    T = _loc(x, y, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    R = s * 0.82
    # brush across the palette first, then everything else paints around it
    g0 = c.snapshot()
    hp = [T(-R * 1.05, R * 0.72), T(R * 0.5, -R * 0.02)]
    c.wash(_band(hp, s * 0.06, s * 0.045), '#e8574f', '#b8353a', strength=0.95, spread=0.006, layers=10, edge=1.0)
    fp = [T(R * 0.5, -R * 0.02), T(R * 0.74, -R * 0.13)]
    c.wash(_band(fp, s * 0.05, s * 0.05), '#dfe2e6', '#9aa1aa', strength=0.95, spread=0.006, layers=10, edge=1.0)
    bp = [T(R * 0.74, -R * 0.13), T(R * 0.93, -R * 0.21), T(R * 1.06, -R * 0.29)]
    c.wash(_band(bp, s * 0.05, s * 0.012), '#3f7fd0', '#24558f', strength=0.95, spread=0.008, layers=10, edge=1.0)
    for pts, w0, w1 in ((hp, s * 0.06, s * 0.045), (fp, s * 0.05, s * 0.05), (bp, s * 0.05, s * 0.012)):
        c.ink_line(_band(pts, w0, w1), width=max(1.1, s * 0.009), alpha=130, passes=1, jitter=0, color=(70, 60, 60))
    c.paint_around(g0)
    shape = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        px, py = R * 1.12 * math.cos(t), R * 0.82 * math.sin(t)
        d = math.hypot(px - R * 0.95, py - R * 0.2)
        if d < R * 0.42:
            k = (R * 0.42 - d) / (R * 0.42)
            px -= R * 0.32 * k; py -= R * 0.05 * k
        shape.append((px, py))
    B = W(shape)
    c.wash(B, '#f2d6a6', '#d6a463', strength=0.88, spread=0.01, layers=14, edge=1.0, ang=angle + 1.2)
    c.wash(W(ellipse(R * 0.1, R * 0.4, R * 1.0, R * 0.45, 18)), '#b97f40', None, strength=0.35, spread=0.02, layers=8, edge=0.0, blur=R * 0.25, clip=B)
    hole = W(ellipse(-R * 0.55, R * 0.18, R * 0.15, R * 0.12, 14))
    c.lift(hole, amount=0.9, soft=0.04, clip=B)
    c.ink_line(B, width=max(1.4, s * 0.012), alpha=140, passes=1, jitter=0, color=(110, 70, 30))
    c.ink_line(hole, width=max(1.2, s * 0.01), alpha=130, passes=1, jitter=0, color=(110, 70, 30))
    spots = [(-R * 0.7, -R * 0.28), (-R * 0.28, -R * 0.52), (R * 0.18, -R * 0.55), (R * 0.62, -R * 0.42), (R * 0.4, R * 0.42), (-R * 0.05, R * 0.52)]
    cols = list(PAINT_COLORS); c.rnd.shuffle(cols)
    for (px, py), col in zip(spots, cols):
        blob = W([(px + R * 0.16 * (1 + 0.15 * math.sin(3 * t + px)) * math.cos(t), py + R * 0.13 * (1 + 0.15 * math.cos(2 * t + py)) * math.sin(t))
                  for t in [2 * math.pi * i / 18 for i in range(18)]])
        c.wash(blob, _mix(col, 0.15), col, strength=0.95, spread=0.012, layers=10, edge=1.15)
        gouache(c, W(ellipse(px - R * 0.06, py - R * 0.05, R * 0.04, R * 0.025, 8)), color=(255, 252, 248), alpha=215, soft=0.2)


def gold_star(c, x, y, s, P, angle=0.0, color=None):
    """A gold star sticker: five points with alternate facets in shadow, so it
    reads as raised, a lifted highlight and a white glint."""
    col = color or '#f0c14b'
    r = s * 0.9; r2 = r * 0.45
    pts = _star_pts(x, y, r, r2, 5, angle)
    c.wash(pts, _mix(col, 0.3), col, strength=0.95, spread=0.008, layers=14, edge=1.05)
    for i in range(5):
        a = pts[2 * i]; b = pts[(2 * i + 1) % 10]
        c.wash([(x, y), a, b], _shade(col, 0.78), None, strength=0.55, spread=0.004, layers=6, edge=0.8, clip=pts)
    c.lift(ellipse(x - r * 0.18, y - r * 0.2, r * 0.12, r * 0.08, 10, -0.5), amount=0.55, soft=0.3, clip=pts)
    c.ink_line(pts, width=max(1.2, s * 0.012), alpha=140, passes=1, jitter=0, color=_inkc(col, 0.55))


STETH_COLORS = {'teal': ('#56c2bb', '#2a9090'), 'navy': ('#5878b6', '#2f4b86'), 'pink': ('#f2a0b9', '#d3708f'),
                'purple': ('#a28ad6', '#7258ab'), 'red': ('#e46f74', '#b0424b')}


def _sm(pts, rounds=2):
    """Chaikin smoothing that keeps both end points."""
    return [pts[0]] + smooth(pts, rounds, closed=False) + [pts[-1]]


def _tube(c, path, hw, col, col2, ink, alpha=150, hi=0.62, shade=0.32, strength=0.8):
    """A round tube along a path: the base wash, a shadow along the lower
    right, a lifted highlight along the upper left, ink on both edges."""
    band = _band(path, hw, hw)
    c.wash(band, col, col2, strength=strength, spread=0.005, layers=12, edge=1.0)
    off = hw * 0.62
    c.wash(_band([(px + off, py + off) for px, py in path], hw * 0.8, hw * 0.8), _shade(col2, 0.8), None, strength=shade,
           spread=0.005, layers=8, edge=0.5, clip=band)
    off = hw * 0.34
    c.lift(_band([(px - off, py - off) for px, py in path], hw * 0.26, hw * 0.26), amount=hi, soft=0.25, clip=band)
    n = len(band) // 2
    for side in (band[:n], band[n:]):
        c.ink_line(side, width=max(1.2, hw * 0.16), closed=False, alpha=alpha, passes=1, jitter=0, color=ink)
    return band


def stethoscope(c, x, y, s, P, color=None, drop=1, ink=None):
    """A stethoscope as a heart: rubber tubing over two round lobes (the
    parametric heart), meeting at the point and running on to a chestpiece
    (silver rim, pale diaphragm) that hangs to one side; at the notch a silver
    yoke from which the two binaurals rise and turn in to dark ear tips.
    x, y is the heart's center, s half its width."""
    if color in STETH_COLORS or not color:
        col, col2 = STETH_COLORS[color or 'teal']
    else:
        col, col2 = color, _shade(color, 0.72)
    k = s / 16.0
    T = lambda px, py: (x + px * k, y + py * k)
    W = lambda pts: [T(px, py) for px, py in pts]
    ic = _inkc(col2, 0.62)
    metal, metal2, mink = '#eef1f4', '#a8b0ba', (82, 88, 98)
    hw = 1.05  # rubber half width, in k

    def hp(t, side):
        return (side * 16 * math.sin(t) ** 3,
                -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) - 2.5)

    # the yoke in the notch: painted first, so the binaurals and the lobes' ends tuck behind it
    yx0, yy0 = T(-2.2, -13.6); yx1, yy1 = T(2.2, -9.0)
    ysnap = _snap(c, (yx0, yy0, yx1, yy1))
    yoke = W(_rr(-1.75, -13.0, 1.75, -9.6, 0.8))
    c.wash(yoke, metal, metal2, strength=0.9, spread=0.005, layers=12, edge=1.0, ang=0.0)
    c.wash(W(_rr(0.4, -13.0, 1.75, -9.6, 0.6)), metal2, None, strength=0.35, spread=0.005, layers=6, edge=0.6, clip=yoke)
    c.lift(W(_rr(-1.25, -12.6, -0.55, -10.0, 0.3)), amount=0.55, soft=0.3, clip=yoke)
    c.ink_line(yoke, width=max(1.2, s * 0.009), alpha=150, passes=1, jitter=0, color=mink)
    _front(c, ysnap)
    # binaurals: from the yoke up and out, then in to the ear tips
    bin_r = _sm([(0.8, -12.6), (1.1, -14.2), (2.3, -17.4), (4.3, -20.6), (5.6, -23.2), (5.5, -25.4), (4.6, -26.9)])
    for sd in (-1, 1):
        path = W([(sd * px, py) for px, py in bin_r])
        _tube(c, path, hw * 0.48 * k, metal, metal2, mink, alpha=135, hi=0.5, shade=0.3, strength=0.85)
        (ax, ay), (bx, by) = path[-2], path[-1]
        a = math.atan2(by - ay, bx - ax)
        ex, ey = bx + math.cos(a) * 1.0 * k, by + math.sin(a) * 1.0 * k
        tip = ellipse(ex, ey, 1.45 * k, 1.05 * k, 16, a)
        c.wash(tip, '#5c616a', '#33363c', strength=0.92, spread=0.006, layers=12, edge=1.0)
        c.lift(ellipse(ex - 0.35 * k, ey - 0.4 * k, 0.55 * k, 0.28 * k, 10, a), amount=0.5, soft=0.35, clip=tip)
        c.ink_line(tip, width=max(1.2, s * 0.009), alpha=150, passes=1, jitter=0, color=(30, 32, 36))
    # tubing: the chestpiece drop and the drop-side lobe as one tube; the other
    # lobe joins it at the point, its end tucked just under the first tube's edge
    ts = [math.pi - math.pi * i / 70 for i in range(60)]
    drop_pts = [(drop * 4.6, 21.2), (drop * 2.4, 19.9), (drop * 0.9, 18.3), (drop * 0.15, 16.4)]
    lobe_a = [hp(t, drop) for t in ts]
    path_a = _sm(drop_pts + lobe_a)
    jx0, jy0 = T(-4.0, 10.5); jx1, jy1 = T(4.0, 18.5)
    snap = _snap(c, (min(jx0, jx1), jy0, max(jx0, jx1), jy1))
    _tube(c, W(path_a), hw * k, col, col2, ic)
    _front(c, snap)  # the other lobe's end tucks behind this tube at the joint
    lobe_b = [hp(t, -drop) for t in ts]
    _tube(c, W(_sm(lobe_b[1:])), hw * k, col, col2, ic)
    # chestpiece: a short stem and a round head
    sx0, sy0 = drop * 4.6, 21.2
    a = math.atan2(21.2 - 19.9, drop * 2.2)
    sx1, sy1 = sx0 + math.cos(a) * 1.5, sy0 + math.sin(a) * 1.5
    _tube(c, W([(sx0 - math.cos(a) * 0.12, sy0 - math.sin(a) * 0.12), (sx1, sy1)]), hw * 0.62 * k, metal, metal2, mink,
          alpha=135, strength=0.85)
    R = 3.3
    cx, cy = sx1 + math.cos(a) * R * 0.92, sy1 + math.sin(a) * R * 0.92
    rim = W(ellipse(cx, cy, R, R, 36))
    c.wash(rim, metal, metal2, strength=0.9, spread=0.006, layers=14, edge=1.0, ang=-2.3)
    dia = W(ellipse(cx, cy, R * 0.74, R * 0.74, 32))
    c.wash(dia, '#f8fafb', '#d5dde3', strength=0.8, spread=0.006, layers=12, edge=1.0, ang=-2.3)
    c.wash(W(ellipse(cx + R * 0.16, cy + R * 0.16, R * 0.62, R * 0.62, 28)), '#aab4be', None, strength=0.3, spread=0.008,
           layers=8, edge=0.0, blur=R * k * 0.25, clip=dia)
    c.lift(W(crescent_pts(cx, cy, R * 0.88, math.pi * 0.95, math.pi * 1.55, R * 0.1)), amount=0.55, soft=0.3, clip=rim)
    gouache(c, W(ellipse(cx - R * 0.32, cy - R * 0.36, R * 0.16, R * 0.09, 8, -0.7)), color=(255, 255, 255), alpha=210, soft=0.2)
    c.ink_line(rim, width=max(1.3, s * 0.01), alpha=150, passes=1, jitter=0, color=mink)
    c.ink_line(dia, width=max(1.1, s * 0.007), alpha=110, passes=1, jitter=0, color=mink)


# ---------------------------------------------------------------- coffee shop (Coffee & Croissants)
CUP_GLAZES = {'sage': ('#bcd3b6', '#7ea47c'), 'blue': ('#b0c8e0', '#6d95bf'), 'terracotta': ('#efb08f', '#c9704d'),
              'blush': ('#f5c6be', '#dc8e88'), 'cream': ('#f7ebd5', '#d6bb93'), 'mustard': ('#f3d48e', '#d5a446')}
FOAM = (250, 242, 226)


def _steam(c, pts_at, s, n=2, col='#bfae9c', h=0.5):
    """Soft rising steam: pale tapering wisps that wave as they rise.
    pts_at(px, py) maps local coords; wisps start at local (0, 0) and rise."""
    rnd = c.rnd
    for k in range(n):
        ox = (k - (n - 1) / 2) * s * 0.24
        ph = rnd.uniform(0, 6.28); amp = s * rnd.uniform(0.045, 0.07)
        path = [pts_at(ox + amp * math.sin(ph + 5.0 * t) * (0.4 + t), -s * h * t) for t in [i / 16 for i in range(17)]]
        c.wash(_band(path, s * 0.032, s * 0.006), col, None, strength=0.3, spread=0.02, layers=10, edge=0.6, blur=s * 0.01)


def _latte_art(c, W, cx, cy, rx, ry, kind):
    """Milk foam poured into the crema: a heart or a tulip, foreshortened like the surface."""
    def heart_pts(hx0, hy0, w, h, n=32):
        pts = []
        for i in range(n):
            t = 2 * math.pi * i / n
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((hx0 + hx / 16 * w, hy0 + (hy / 15 + 0.12) * h))
        return pts
    line = lambda y0, y1, w: W([(cx - w, y0), (cx + w, y0), (cx + w * 0.5, y1), (cx - w * 0.5, y1)])
    if kind == 'heart':
        gouache(c, W(heart_pts(cx, cy - ry * 0.02, rx * 0.5, ry * 0.66)), color=FOAM, alpha=240, soft=0.02)
        gouache(c, line(cy + ry * 0.35, cy + ry * 0.86, rx * 0.018), color=FOAM, alpha=225, soft=0.06)
    elif kind == 'tulip':
        def crescent(oy, orx, ory, iy, irx, iry, n=18):
            outer = [(cx + orx * math.cos(a), oy + ory * math.sin(a)) for a in [math.pi * i / n for i in range(n + 1)]]
            inner = [(cx + irx * math.cos(a), iy + iry * math.sin(a)) for a in [math.pi * (n - i) / n for i in range(n + 1)]]
            return W(outer + inner)
        gouache(c, crescent(cy + ry * 0.16, rx * 0.42, ry * 0.5, cy + ry * 0.1, rx * 0.3, ry * 0.26), color=FOAM, alpha=238, soft=0.02)
        gouache(c, crescent(cy - ry * 0.16, rx * 0.3, ry * 0.3, cy - ry * 0.22, rx * 0.21, ry * 0.13), color=FOAM, alpha=236, soft=0.025)
        gouache(c, W(heart_pts(cx, cy - ry * 0.56, rx * 0.15, ry * 0.24, 24)), color=FOAM, alpha=236, soft=0.03)
        gouache(c, line(cy - ry * 0.62, cy + ry * 0.8, rx * 0.012), color=FOAM, alpha=215, soft=0.06)
    else:   # a plain cappuccino: a soft island of foam
        gouache(c, W(ellipse(cx, cy + ry * 0.05, rx * 0.52, ry * 0.55, 22)), color=FOAM, alpha=215, soft=0.08)


def latte_cup(c, x, y, s, P, angle=0.0, color=None, art=None, steam=True):
    """A cappuccino cup on its saucer, seen a little from above: a glazed cup
    (soft wet-in-wet glaze, the shadow side darker, a lifted highlight), the
    crema with a heart or rosetta of milk foam, a looped handle, a saucer with
    a well and a contact shadow, and a curl of steam."""
    glaze = color if color in CUP_GLAZES else c.rnd.choice(list(CUP_GLAZES))
    g1, g2 = CUP_GLAZES[glaze]
    kind = art or c.rnd.choice(['heart', 'heart', 'tulip'])
    T = _loc(x, y + s * 0.08, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    ic = _inkc(g2, 0.5)
    rx, ry, ry0 = s * 0.6, s * 0.2, -s * 0.24          # rim ellipse
    rim = [(rx * math.cos(a), ry0 + ry * math.sin(a)) for a in [2 * math.pi * i / 40 for i in range(40)]]
    front = [(rx * math.cos(a), ry0 + ry * math.sin(a)) for a in [math.pi * i / 20 for i in range(21)]]   # x: +rx -> -rx
    side = [(-rx, ry0), (-rx * 0.99, ry0 + s * 0.12), (-rx * 0.9, ry0 + s * 0.36), (-rx * 0.72, ry0 + s * 0.56),
            (-rx * 0.48, ry0 + s * 0.7), (-rx * 0.4, ry0 + s * 0.72)]
    foot_y = ry0 + s * 0.72
    body = smooth([p for p in front] + side + [(-p[0], p[1]) for p in side[::-1]][1:], rounds=1)
    # the cup in front, then the saucer and handle go around it
    g0 = c.snapshot()
    B = W(body)
    c.wash(B, g1, g2, strength=0.9, spread=0.008, layers=16, edge=1.0, ang=angle, vary=_mix(g2, 0.3), vary_amt=0.35)
    c.wash(W([(rx * 0.3, ry0), (rx * 1.1, ry0), (rx * 1.1, foot_y), (rx * 0.3, foot_y)]), _shade(g2, 0.8), None, strength=0.45,
           spread=0.01, layers=10, edge=0.0, blur=s * 0.08, clip=B)
    c.wash(W(ellipse(0, foot_y - s * 0.02, rx * 0.5, s * 0.07, 16)), _shade(g2, 0.75), None, strength=0.35, spread=0.01, layers=8,
           edge=0.0, blur=s * 0.05, clip=B)
    c.lift(W([(-rx * 0.66, ry0 + s * 0.12), (-rx * 0.5, ry0 + s * 0.12), (-rx * 0.38, ry0 + s * 0.52), (-rx * 0.5, ry0 + s * 0.56)]),
           amount=0.55, soft=0.35, clip=B)
    # inside: the glazed inner wall (pale), then the coffee a little lower
    R = W(rim)
    c.wash(R, '#fbf6ee', _mix(g1, 0.4), strength=0.55, spread=0.006, layers=10, edge=0.8, ang=angle + math.pi / 2)
    cx, cy, crx, cry = 0, ry0 + ry * 0.12, rx * 0.9, ry * 0.82
    coffee = W(ellipse(cx, cy, crx, cry, 36))
    c.wash(coffee, '#d8a675', '#9c5e33', strength=0.95, spread=0.006, layers=14, edge=1.35, ang=angle + math.pi / 2,
           vary='#b87a46', vary_amt=0.4)
    c.wash(W(ellipse(cx, cy, crx * 0.97, cry * 0.95, 36)), '#7a4524', None, strength=0.35, spread=0.004, layers=6, edge=1.6, blur=s * 0.012,
           clip=coffee)
    _latte_art(c, W, cx + rx * 0.02, cy, crx, cry, kind)
    c.ink_line(B, width=max(1.4, s * 0.012), alpha=135, passes=1, jitter=0, color=ic)
    c.ink_line(R, width=max(1.4, s * 0.012), alpha=140, passes=1, jitter=0, color=ic)
    c.ink_line(coffee, width=max(1, s * 0.008), alpha=90, passes=1, jitter=0, color=(110, 66, 36))
    c.paint_around(g0)
    # handle: a loop on the right, tucked behind the cup at both ends
    hp = [(rx * 0.86, ry0 + s * 0.08)] + [(rx * 1.02 + s * 0.17 * math.cos(a), ry0 + s * 0.27 + s * 0.17 * math.sin(a))
                                           for a in [-math.pi * 0.62 + math.pi * 1.24 * i / 14 for i in range(15)]] + \
         [(rx * 0.8, ry0 + s * 0.46)]
    H = W(_band(hp, s * 0.055, s * 0.05))
    c.wash(H, g1, g2, strength=0.9, spread=0.008, layers=12, edge=1.0, ang=angle)
    c.ink_line(H, width=max(1.3, s * 0.011), alpha=135, passes=1, jitter=0, color=ic)
    # saucer
    sy = foot_y - s * 0.02
    S = W(ellipse(0, sy, s * 0.98, s * 0.2, 40))
    c.wash(S, _mix(g1, 0.25), g2, strength=0.8, spread=0.008, layers=14, edge=1.0, ang=angle + 0.3)
    c.wash(W(ellipse(0, sy - s * 0.01, s * 0.58, s * 0.1, 30)), _shade(g2, 0.85), None, strength=0.3, spread=0.01, layers=8, edge=0.9,
           clip=S)
    c.wash(W(ellipse(s * 0.06, sy + s * 0.02, s * 0.5, s * 0.08, 24)), '#5a3a2a', None, strength=0.4, spread=0.01, layers=8, edge=0.0,
           blur=s * 0.04, clip=S)
    c.lift(W(ellipse(-s * 0.62, sy - s * 0.06, s * 0.2, s * 0.035, 14, 0.12)), amount=0.5, soft=0.4, clip=S)
    c.ink_line(S, width=max(1.4, s * 0.012), alpha=130, passes=1, jitter=0, color=ic)
    c.paint_around(g0)          # the whole cup and saucer sit in front of what is painted later
    if steam:
        _steam(c, lambda px, py: T(px, ry0 - s * 0.12 + py), s, n=2, h=0.42)


def togo_cup(c, x, y, s, P, angle=0.0, color=None, steam=True):
    """A takeaway coffee cup: a paper cup narrowing to its base, a kraft (or
    colored) sleeve with a little painted heart, a white snap-on lid with a
    sip opening, soft shading and a curl of steam."""
    sleeve = color or '#d4a06a'
    T = _loc(x, y + s * 0.06, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    top, bot = -s * 0.5, s * 0.8
    wt, wb = s * 0.44, s * 0.31
    hw = lambda yy: wt + (wb - wt) * (yy - top) / (bot - top)
    arc = lambda yy, d, n=14: [(hw(yy) * math.cos(a), yy + d * math.sin(a)) for a in [math.pi * i / n for i in range(n + 1)]]
    body = [(-wt, top), (wt, top)] + arc(bot, s * 0.045)
    # lid first: it sits in front of the cup's top edge
    g0 = c.snapshot()
    lr = W(_rr(-s * 0.49, -s * 0.62, s * 0.49, -s * 0.48, s * 0.05))
    dome = W(smooth([(-s * 0.46, -s * 0.6), (-s * 0.42, -s * 0.72), (-s * 0.34, -s * 0.77), (s * 0.34, -s * 0.77), (s * 0.42, -s * 0.72),
                     (s * 0.46, -s * 0.6)], rounds=2, closed=False) + [(s * 0.46, -s * 0.58), (-s * 0.46, -s * 0.58)])
    for pts in (dome, lr):
        c.wash(pts, '#f8f5f0', '#bdb5aa', strength=0.7, spread=0.006, layers=12, edge=1.0, ang=angle)
    c.wash(W([(s * 0.12, -s * 0.8), (s * 0.6, -s * 0.8), (s * 0.6, -s * 0.46), (s * 0.12, -s * 0.46)]), '#9d948a', None, strength=0.35,
           spread=0.01, layers=8, edge=0.0, blur=s * 0.06, clip=dome + lr)
    slot = W(_rr(-s * 0.26, -s * 0.755, -s * 0.06, -s * 0.715, s * 0.018))
    c.wash(slot, '#4a3426', None, strength=0.9, spread=0.004, layers=6, edge=1.0)
    for pts in (dome, lr):
        c.ink_line(pts, width=max(1.3, s * 0.011), alpha=130, passes=1, jitter=0, color=(110, 100, 92))
    c.paint_around(g0)
    B = W(body)
    c.wash(B, '#fdfbf7', '#cfc6ba', strength=0.65, spread=0.006, layers=12, edge=1.0, ang=angle)
    c.wash(W([(wt * 0.35, top), (wt * 1.2, top), (wt * 1.2, bot + s * 0.1), (wt * 0.35, bot + s * 0.1)]), '#a99d90', None, strength=0.35,
           spread=0.01, layers=8, edge=0.0, blur=s * 0.07, clip=B)
    y0, y1 = -s * 0.12, s * 0.36
    sl = W([(hw(y0) * math.cos(a), y0 + s * 0.03 * math.sin(a)) for a in [math.pi * (1 - i / 14) for i in range(15)]] + arc(y1, s * 0.035))
    c.wash(sl, _mix(sleeve, 0.12), _shade(sleeve, 0.78), strength=0.92, spread=0.008, layers=14, edge=1.0, ang=angle, vary=_shade(sleeve, 0.85),
           vary_amt=0.4)
    c.wash(W([(wt * 0.3, y0), (wt * 1.2, y0), (wt * 1.2, y1 + s * 0.05), (wt * 0.3, y1 + s * 0.05)]), _shade(sleeve, 0.6), None,
           strength=0.35, spread=0.01, layers=8, edge=0.0, blur=s * 0.06, clip=sl)
    hy = (y0 + y1) / 2 + s * 0.02; hs = s * 0.1
    heart_pts = [(-s * 0.04 + hs * 0.06 * 16 * math.sin(t) ** 3,
                  hy - hs * 0.06 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
                 for t in [2 * math.pi * i / 24 for i in range(24)]]
    gouache(c, W(heart_pts), color=(250, 240, 226), alpha=215, soft=0.08)
    c.lift(W([(-wt * 0.78, top + s * 0.06), (-wt * 0.6, top + s * 0.06), (-wb * 0.55, bot - s * 0.08), (-wb * 0.75, bot - s * 0.08)]),
           amount=0.3, soft=0.3, clip=B)
    c.ink_line(B, width=max(1.3, s * 0.011), alpha=125, passes=1, jitter=0, color=(120, 108, 96))
    c.ink_line(sl, width=max(1.3, s * 0.011), alpha=135, passes=1, jitter=0, color=_inkc(sleeve, 0.5))
    c.paint_around(g0)
    if steam:
        _steam(c, lambda px, py: T(-s * 0.16 + px * 0.6, -s * 0.8 + py), s, n=1, h=0.3)


def french_press(c, x, y, s, P, angle=0.0, color=None):
    """A glass French press: brushed-steel lid, rod and knob, a steel band at
    the top and a footed base, coffee showing through the glass with a crema
    line and the plunger's mesh disc, glass glints, and a dark handle."""
    handle = color or '#3a3330'
    T = _loc(x, y + s * 0.04, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    gx, gt, gb = s * 0.34, -s * 0.5, s * 0.66                # glass half width, top, bottom
    steel = ('#e6e9ec', '#8f979f')
    # steel parts in front: base, top band, lid, rod, knob
    g0 = c.snapshot()
    base = W(_rr(-gx * 1.08, gb - s * 0.1, gx * 1.08, gb + s * 0.04, s * 0.03))
    band = W(_rr(-gx * 1.06, gt - s * 0.01, gx * 1.06, gt + s * 0.09, s * 0.02))
    lid = W(smooth([(-gx * 1.04, gt), (-gx * 0.9, gt - s * 0.1), (-gx * 0.45, gt - s * 0.15), (gx * 0.45, gt - s * 0.15), (gx * 0.9, gt - s * 0.1),
                    (gx * 1.04, gt)], rounds=2, closed=False) + [(gx * 1.04, gt + s * 0.01), (-gx * 1.04, gt + s * 0.01)])
    spout = W([(-gx * 1.02, gt - s * 0.02), (-gx * 1.26, gt - s * 0.06), (-gx * 1.22, gt + s * 0.03), (-gx * 1.02, gt + s * 0.05)])
    rod = W(_rr(-s * 0.017, gt - s * 0.42, s * 0.017, gt - s * 0.14, s * 0.01))
    knob = W(ellipse(0, gt - s * 0.46, s * 0.075, s * 0.065, 16))
    for pts in (base, band, lid, spout, rod, knob):
        c.wash(pts, steel[0], steel[1], strength=0.85, spread=0.006, layers=10, edge=1.0, ang=angle)
    for xx in (-gx * 0.8, -gx * 0.1, gx * 0.6):
        c.wash(W([(xx, gb - s * 0.1), (xx + gx * 0.12, gb - s * 0.1), (xx + gx * 0.12, gb + s * 0.04), (xx, gb + s * 0.04)]), '#6f777f', None,
               strength=0.3, spread=0.004, layers=5, edge=0.4, clip=base)
    for pts, yy in ((base, gb - s * 0.07), (band, gt + s * 0.01)):
        c.lift(W([(-gx * 0.95, yy), (gx * 0.4, yy), (gx * 0.4, yy + s * 0.025), (-gx * 0.95, yy + s * 0.025)]), amount=0.45, soft=0.3, clip=pts)
    c.lift(W(ellipse(-gx * 0.3, gt - s * 0.08, gx * 0.35, s * 0.025, 12)), amount=0.5, soft=0.4, clip=lid)
    gouache(c, W(ellipse(-s * 0.025, gt - s * 0.48, s * 0.02, s * 0.014, 8)), color=(255, 255, 255), alpha=230, soft=0.2)
    for pts in (base, band, lid, spout, rod, knob):
        c.ink_line(pts, width=max(1.2, s * 0.01), alpha=135, passes=1, jitter=0, color=(70, 76, 84))
    for xx in (-gx * 1.0, gx * 0.95):
        c.wash(W([(xx - s * 0.03, gb - s * 0.0), (xx + s * 0.03, gb), (xx + s * 0.025, gb + s * 0.1), (xx - s * 0.025, gb + s * 0.1)]),
               steel[0], steel[1], strength=0.85, spread=0.006, layers=8, edge=1.0)
    c.paint_around(g0)
    # glass, coffee, crema, plunger disc and the rod through the glass
    G = W([(-gx, gt + s * 0.09), (gx, gt + s * 0.09), (gx, gb - s * 0.1), (-gx, gb - s * 0.1)])
    c.wash(G, '#eef3f5', '#c9d6dc', strength=0.5, spread=0.004, layers=8, edge=1.2, ang=angle)
    lv = gt + s * 0.36
    cof = W([(-gx * 0.97, lv), (gx * 0.97, lv), (gx * 0.97, gb - s * 0.1), (-gx * 0.97, gb - s * 0.1)])
    c.wash(cof, '#7a4626', '#3e2314', strength=0.95, spread=0.004, layers=14, edge=1.0, ang=angle + math.pi / 2, vary='#5a321c', vary_amt=0.4)
    c.wash(W([(-gx * 0.97, lv - s * 0.01), (gx * 0.97, lv - s * 0.01), (gx * 0.97, lv + s * 0.05), (-gx * 0.97, lv + s * 0.05)]),
           '#c9935e', '#a8703f', strength=0.9, spread=0.004, layers=8, edge=0.9, ang=angle)
    disc = W(ellipse(0, lv - s * 0.04, gx * 0.94, s * 0.035, 20))
    c.wash(disc, '#d9dde1', '#9aa2aa', strength=0.8, spread=0.004, layers=8, edge=1.0, ang=angle)
    c.ink_line(disc, width=max(1, s * 0.008), alpha=120, passes=1, jitter=0, color=(80, 86, 94))
    c.wash(W(_rr(-s * 0.014, gt + s * 0.09, s * 0.014, lv - s * 0.06, s * 0.008)), '#b8bfc6', '#8a929a', strength=0.85, spread=0.004,
           layers=6, edge=1.0)
    for x0, x1, a in ((-gx * 0.78, -gx * 0.62, 0.75), (-gx * 0.5, -gx * 0.44, 0.5), (gx * 0.55, gx * 0.64, 0.35)):
        c.lift(W([(x0, gt + s * 0.14), (x1, gt + s * 0.14), (x1, gb - s * 0.16), (x0, gb - s * 0.16)]), amount=a, soft=0.12, clip=G)
    c.ink_line(G, width=max(1.2, s * 0.01), alpha=110, passes=1, jitter=0, color=(90, 100, 108))
    # handle: a C on the right from the top band to the base
    hp = [(gx * 1.02, gt + s * 0.05), (gx * 1.42, gt + s * 0.1), (gx * 1.58, gt + s * 0.4), (gx * 1.5, gb - s * 0.35),
          (gx * 1.3, gb - s * 0.18), (gx * 1.02, gb - s * 0.12)]
    Hd = W(_band(_sm(hp, 2), s * 0.06, s * 0.05))
    c.wash(Hd, _mix(handle, 0.25), handle, strength=0.95, spread=0.006, layers=12, edge=1.0, ang=angle)
    c.lift(W(_band(_sm([(gx * 1.38, gt + s * 0.14), (gx * 1.5, gt + s * 0.4), (gx * 1.44, gb - s * 0.36)], 2), s * 0.014, s * 0.008)),
           amount=0.4, soft=0.3, clip=Hd)
    c.ink_line(Hd, width=max(1.2, s * 0.01), alpha=140, passes=1, jitter=0, color=_inkc(handle, 0.6))
    c.paint_around(g0)


ENAMEL = {'blue': ('#5d8fc8', '#2f5f99'), 'red': ('#d65a4c', '#a3332c'), 'green': ('#6fa57d', '#3f7453'), 'cream': ('#f2e6cc', '#cdb68c')}


def enamel_pot(c, x, y, s, P, angle=0.0, color=None):
    """A speckled enamel coffee pot (the campfire percolator): a tapered body
    in glossy enamel with white speckles, a dark rolled rim, a domed lid with
    a clear glass knob, a long curved spout and a looped handle."""
    kind = color if color in ENAMEL else 'blue'
    e1, e2 = ENAMEL[kind]
    rim_col = '#2b3442' if kind != 'cream' else '#3d5f8f'
    T = _loc(x + s * 0.05, y + s * 0.04, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    tt, bb = -s * 0.36, s * 0.66
    tw, bw = s * 0.3, s * 0.48
    body = smooth([(-tw, tt), (tw, tt), (bw * 0.96, bb - s * 0.14), (bw, bb - s * 0.04), (bw * 0.9, bb), (-bw * 0.9, bb), (-bw, bb - s * 0.04),
                   (-bw * 0.96, bb - s * 0.14)], rounds=1)
    g0 = c.snapshot()
    B = W(body)
    c.wash(B, _mix(e1, 0.1), e2, strength=0.95, spread=0.008, layers=16, edge=1.05, ang=angle, vary=e2, vary_amt=0.35)
    c.wash(W([(bw * 0.25, tt), (bw * 1.2, tt), (bw * 1.2, bb), (bw * 0.25, bb)]), _shade(e2, 0.72), None, strength=0.45, spread=0.01, layers=8,
           edge=0.0, blur=s * 0.08, clip=B)
    c.lift(W([(-tw * 0.75, tt + s * 0.08), (-tw * 0.45, tt + s * 0.08), (-bw * 0.5, bb - s * 0.16), (-bw * 0.78, bb - s * 0.16)]), amount=0.5,
           soft=0.3, clip=B)
    rnd = c.rnd
    for _ in range(int(60 + s * 0.1)):
        v = rnd.uniform(0.04, 0.96); u = rnd.uniform(-0.92, 0.92)
        yy = tt + (bb - tt) * v; hw = tw + (bw - tw) * min(1, v * 1.15)
        r = s * rnd.uniform(0.006, 0.014)
        gouache(c, W(ellipse(u * hw * 0.95, yy, r, r * 0.9, 7)), color=(252, 250, 246), alpha=rnd.randint(170, 235), soft=0.25)
    rimb = W(_rr(-tw * 1.06, tt - s * 0.04, tw * 1.06, tt + s * 0.03, s * 0.02))
    foot = W(_rr(-bw * 0.9, bb - s * 0.035, bw * 0.9, bb + s * 0.02, s * 0.02))
    for pts in (rimb, foot):
        c.wash(pts, _mix(rim_col, 0.2), rim_col, strength=0.95, spread=0.006, layers=8, edge=1.0, ang=angle)
    lid = W(smooth([(-tw * 0.96, tt - s * 0.03), (-tw * 0.8, tt - s * 0.15), (-tw * 0.35, tt - s * 0.21), (tw * 0.35, tt - s * 0.21),
                    (tw * 0.8, tt - s * 0.15), (tw * 0.96, tt - s * 0.03)], rounds=2, closed=False) + [(tw * 0.96, tt), (-tw * 0.96, tt)])
    c.wash(lid, _mix(e1, 0.1), e2, strength=0.95, spread=0.008, layers=12, edge=1.05, ang=angle)
    c.lift(W(ellipse(-tw * 0.3, tt - s * 0.14, tw * 0.3, s * 0.025, 12)), amount=0.45, soft=0.4, clip=lid)
    knob = W(smooth([(-s * 0.07, tt - s * 0.2), (-s * 0.08, tt - s * 0.3), (-s * 0.05, tt - s * 0.37), (s * 0.05, tt - s * 0.37),
                     (s * 0.08, tt - s * 0.3), (s * 0.07, tt - s * 0.2)], rounds=2, closed=True))
    c.wash(knob, '#e8f0f2', '#b9cbd2', strength=0.55, spread=0.006, layers=8, edge=1.4)
    c.wash(W(ellipse(0, tt - s * 0.25, s * 0.05, s * 0.04, 10)), '#7a4b2c', None, strength=0.45, spread=0.01, layers=6, edge=0.6, clip=knob)
    gouache(c, W(ellipse(-s * 0.035, tt - s * 0.32, s * 0.016, s * 0.022, 8)), color=(255, 255, 255), alpha=235, soft=0.2)
    ic = _inkc(e2, 0.55)
    for pts in (B, lid):
        c.ink_line(pts, width=max(1.3, s * 0.011), alpha=135, passes=1, jitter=0, color=ic)
    for pts in (rimb, foot, knob):
        c.ink_line(pts, width=max(1.1, s * 0.009), alpha=120, passes=1, jitter=0, color=(40, 44, 52))
    c.paint_around(g0)
    # spout from low on the left, curving up and out
    sp = _sm([(-bw * 0.7, bb - s * 0.3), (-bw * 1.02, bb - s * 0.42), (-bw * 1.2, tt + s * 0.2), (-bw * 1.32, tt - s * 0.02)], 2)
    S = W(_band(sp, s * 0.09, s * 0.035))
    c.wash(S, _mix(e1, 0.1), e2, strength=0.95, spread=0.008, layers=12, edge=1.05, ang=angle)
    c.wash(W(ellipse(-bw * 1.32, tt - s * 0.02, s * 0.04, s * 0.022, 10, -0.6)), rim_col, None, strength=0.9, spread=0.006, layers=6, edge=1.0)
    c.ink_line(S, width=max(1.2, s * 0.01), alpha=130, passes=1, jitter=0, color=ic)
    # handle on the right
    hp = _sm([(tw * 0.96, tt + s * 0.04), (bw * 1.22, tt + s * 0.06), (bw * 1.42, tt + s * 0.3), (bw * 1.36, bb - s * 0.42),
              (bw * 1.12, bb - s * 0.26), (bw * 0.92, bb - s * 0.26)], 2)
    Hd = W(_band(hp, s * 0.05, s * 0.045))
    c.wash(Hd, _mix(e1, 0.1), e2, strength=0.95, spread=0.008, layers=12, edge=1.05, ang=angle)
    c.ink_line(Hd, width=max(1.2, s * 0.01), alpha=130, passes=1, jitter=0, color=ic)
    c.paint_around(g0)


def croissant(c, x, y, s, P, angle=0.0, color=None, n=5):
    """A butter croissant: one crescent of laminated dough with rounded rolls
    along its back (the middle roll fattest), deep golden brown on the baked
    tops, paler gold in the grooves and underneath, glossy from the egg wash,
    thin curled tips, and a few flakes."""
    T = _loc(x, y + s * 0.16, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    cx, cy, R = 0.0, s * 0.46, s * 0.62
    a0, a1 = math.radians(192), math.radians(348)
    g0 = c.snapshot()
    th = lambda u: s * (0.05 + 0.29 * math.sin(math.pi * u) ** 0.85)       # half thickness along the crescent
    # roll boundaries, wider in the middle
    us = [-1 + 2 * k / n for k in range(n + 1)]
    bnd = [0.5 + 0.5 * (1 if u >= 0 else -1) * abs(u) ** 0.85 for u in us]
    bnd = [0.06 + 0.88 * b for b in bnd]

    def bump(u):
        for k in range(n):
            if bnd[k] <= u <= bnd[k + 1]:
                return math.sin(math.pi * (u - bnd[k]) / (bnd[k + 1] - bnd[k]))
        return 0.0

    def pt(u, r):
        a = a0 + (a1 - a0) * u
        return (cx + r * math.cos(a), cy + r * math.sin(a))
    N = 90
    outer = [pt(u, R + th(u) * (0.62 + 0.3 * bump(u))) for u in [i / N for i in range(N + 1)]]
    inner = [pt(u, R - th(u) * (0.78 + 0.1 * bump(u))) for u in [i / N for i in range(N, -1, -1)]]
    body = W(outer + inner)
    c.wash(body, '#f6d48e', '#e0a052', strength=0.92, spread=0.006, layers=16, edge=1.0, ang=angle + math.pi / 2, vary='#e8b468', vary_amt=0.4)
    for k in range(n):
        um = (bnd[k] + bnd[k + 1]) / 2; span = bnd[k + 1] - bnd[k]
        a = a0 + (a1 - a0) * um
        hk = th(um)
        tw = (R + hk * 0.3) * (a1 - a0) * span * 0.42
        bx, by = pt(um, R + hk * 0.22)
        top = W(ellipse(bx, by, hk * 0.62, tw, 22, a))
        c.wash(top, '#c97b36', '#9a521f', strength=0.62, spread=0.01, layers=10, edge=0.3, blur=s * 0.035, ang=angle + a + math.pi, clip=body)
        hx, hy = pt(um - span * 0.18, R + hk * 0.42)
        c.lift(W(ellipse(hx, hy, hk * 0.22, tw * 0.22, 12, a + 0.3)), amount=0.42, soft=0.4, clip=body)
    for k in range(1, n):
        u = bnd[k]
        groove = [pt(u + 0.012 * (j / 6 - 0.5), R - th(u) * 0.75 + th(u) * 1.6 * j / 6) for j in range(7)]
        g = W(_band(groove, s * 0.016, s * 0.008))
        c.wash(g, '#8a4a1e', None, strength=0.55, spread=0.006, layers=6, edge=0.6, blur=s * 0.006, clip=body)
        c.ink_line(W(groove[1:-1]), width=max(1, s * 0.008), closed=False, alpha=95, passes=1, jitter=0, color=(115, 62, 26))
    c.ink_line(body, width=max(1.3, s * 0.011), alpha=135, passes=1, jitter=0, color=(122, 68, 30))
    c.paint_around(g0)
    rnd = c.rnd
    for _ in range(4):
        fx, fy = rnd.uniform(-s * 0.45, s * 0.45), cy + rnd.uniform(-s * 0.1, -s * 0.02)
        c.wash(W(ellipse(fx, fy, s * rnd.uniform(0.012, 0.024), s * rnd.uniform(0.008, 0.013), 7, rnd.uniform(0, 3))), '#d9974c', None,
               strength=0.85, spread=0.02, layers=6, edge=1.0)


def coffee_branch(c, x, y, s, P, angle=0.0, color=None, cherries=3):
    """A coffee plant sprig: a woody stem with pairs of glossy dark leaves
    (wavy edges, a lifted midrib) and clusters of coffee cherries at the leaf
    joints, mostly ripe red, a few orange or still green, each with a glint."""
    T = _loc(x, y, angle)
    W = lambda pts: [T(px, py) for px, py in pts]
    rnd = c.rnd
    stem = _sm([(-s * 0.85, s * 0.22), (-s * 0.3, s * 0.04), (s * 0.25, -s * 0.06), (s * 0.85, -s * 0.2)], 2)
    leaves = [(0.12, 1, 0.62), (0.12, -1, 0.56), (0.45, 1, 0.58), (0.45, -1, 0.6), (0.78, 1, 0.46), (0.78, -1, 0.42), (1.0, 0, 0.4)]
    cols = ('#7fb06f', '#3f7a4a', '#24502f')
    g0 = c.snapshot()
    for t in (0.12, 0.45, 0.78)[:max(1, min(3, cherries))]:
        (px, py), _ = _at_path(W(stem), t)
        k = rnd.randint(3, 4)
        for j in range(k):
            a = angle + math.pi / 2 + (j - (k - 1) / 2) * 0.65 + rnd.uniform(-0.15, 0.15)
            d = s * rnd.uniform(0.09, 0.14)
            qx, qy = px + d * math.cos(a), py + d * math.sin(a)
            r = s * rnd.uniform(0.105, 0.125)
            col = rnd.choice([('#e8474c', '#b72634')] * 5 + [('#f29a45', '#cf6a26'), ('#b5d066', '#7aa33e')])
            ch = ellipse(qx, qy, r, r * 0.86, 18, a)
            c.wash(ch, col[0], col[1], strength=0.95, spread=0.01, layers=12, edge=1.1, ang=a + math.pi)
            c.wash(ellipse(qx + r * 0.3 * math.cos(a), qy + r * 0.3 * math.sin(a), r * 0.55, r * 0.45, 12, a), _shade(col[1], 0.8), None,
                   strength=0.3, spread=0.01, layers=6, edge=0.0, blur=r * 0.25, clip=ch)
            c.wash(ellipse(qx + r * 0.78 * math.cos(a), qy + r * 0.78 * math.sin(a), r * 0.1, r * 0.08, 8), '#5a3424', None, strength=0.7,
                   spread=0.01, layers=5, edge=1.0)
            c.lift(ellipse(qx - r * 0.25, qy - r * 0.28, r * 0.38, r * 0.24, 10, -0.6), amount=0.35, soft=0.4, clip=ch)
            gouache(c, ellipse(qx - r * 0.38, qy - r * 0.38, r * 0.15, r * 0.09, 8, -0.6), color=(255, 250, 246), alpha=230, soft=0.15)
            c.ink_line(ch, width=max(1, s * 0.008), alpha=120, passes=1, jitter=0, color=_inkc(col[1], 0.6))
    c.paint_around(g0)          # cherries in front; the leaves and stem tuck behind them
    for t, side, L in leaves:
        (px, py), sa = _at_path(W(stem), min(t, 0.999))
        la = sa + side * 0.95 if side else sa
        tip = (px + s * L * math.cos(la), py + s * L * math.sin(la))
        mid = (px + s * L * 0.5 * math.cos(la) + side * s * 0.06 * math.cos(la + math.pi / 2),
               py + s * L * 0.5 * math.sin(la) + side * s * 0.06 * math.sin(la + math.pi / 2))
        _herb_leaf(c, (px, py), mid, tip, s * L * 0.26, cols, veins='lift', teeth=0, strength=0.85, shade=0.35, gran=0.25, outline=90,
                   widest=0.75)
    c.wash(_band(W(stem), s * 0.03, s * 0.016), '#8a6a45', '#5c4228', strength=0.9, spread=0.008, layers=8, edge=1.0)
    c.paint_around(g0)


def coffee_beans(c, x, y, s, P, angle=0.0, color=None, n=3):
    """Roasted coffee beans: glossy brown ovals with the S-shaped center
    crease, a darker shadow side and a small glint. n = 1-5 in a loose pile."""
    rnd = c.rnd
    spots = [(0, 0)] if n == 1 else [(math.cos(2 * math.pi * k / n + angle) * s * 0.42, math.sin(2 * math.pi * k / n + angle) * s * 0.34)
                                     for k in range(n)]
    r0 = s * (0.62 if n == 1 else 0.34)
    for (ox, oy) in spots:
        a = angle + rnd.uniform(-1.2, 1.2)
        bx, by = x + ox, y + oy
        r = r0 * rnd.uniform(0.9, 1.08)
        T = _loc(bx, by, a)
        W = lambda pts: [T(px, py) for px, py in pts]
        bean = W(ellipse(0, 0, r, r * 0.68, 20))
        c.wash(bean, '#8a5532', '#3f2213', strength=0.95, spread=0.01, layers=12, edge=1.1, ang=a + 2.4, vary='#5e341c', vary_amt=0.4)
        crease = [(-r * 0.86, r * 0.02), (-r * 0.4, -r * 0.1), (0, 0.0), (r * 0.4, r * 0.1), (r * 0.86, -r * 0.02)]
        c.wash(W(_band(_sm(crease, 2), r * 0.045, r * 0.03)), '#24130a', None, strength=0.9, spread=0.006, layers=6, edge=1.0)
        c.lift(W(ellipse(-r * 0.3, -r * 0.34, r * 0.32, r * 0.1, 10)), amount=0.4, soft=0.4, clip=bean)
        gouache(c, W(ellipse(-r * 0.36, -r * 0.36, r * 0.12, r * 0.045, 8)), color=(255, 246, 236), alpha=190, soft=0.25)
        c.ink_line(bean, width=max(1, s * 0.012), alpha=110, passes=1, jitter=0, color=(50, 28, 16))


MOTIFS2 = {'splash': splash, 'snowfall': snowfall, 'far_forest': far_forest, 'snow_drift': snow_drift, 'grass_tufts': grass_tufts,
           'spruce': spruce, 'vintage_truck': vintage_truck, 'mini_wreath': mini_wreath, 'cozy_glow': cozy_glow, 'twinkle': twinkle,
           'book_tree2': book_tree2, 'gift2': gift2, 'cozy_cat': cozy_cat, 'base_garland': base_garland, 'mini_bauble': mini_bauble,
           'glass_bauble': glass_bauble, 'narcissus': narcissus, 'snowdrop': snowdrop, 'night_sky2': night_sky2,
           'carnation': carnation, 'violet': violet,
           'sunrise': sunrise, 'mountains2': mountains2, 'lake': lake, 'birds': birds, 'dock': dock, 'rowboat': rowboat, 'trout': trout,
           'cattails': cattails, 'lily_pads': lily_pads,
           'rose_leaves': rose_leaves, 'garden_rose': garden_rose, 'lily_valley': lily_valley,
           'basil': basil, 'sage': sage, 'mint': mint, 'rosemary': rosemary, 'thyme': thyme, 'chives': chives,
           'lovebirds': lovebirds,
           'birthday_cake': birthday_cake, 'confetti': confetti,
           'school_apple': school_apple, 'pencil': pencil, 'crayon': crayon, 'book_stack': book_stack, 'ruler': ruler,
           'paper_plane': paper_plane, 'paint_palette': paint_palette, 'gold_star': gold_star,
           'stethoscope': stethoscope,
           'latte_cup': latte_cup, 'togo_cup': togo_cup, 'french_press': french_press, 'enamel_pot': enamel_pot,
           'croissant': croissant, 'coffee_branch': coffee_branch, 'coffee_beans': coffee_beans}
