#!/usr/bin/env python3
"""All-over watercolor patterns for wraparound products (mugs first), and a
3D mug mockup to check them.

usage: pattern.py designs/<id>.json OUT_DIR [--size 2475x1155 ...] [--preview]

A pattern spec (designs/<id>.json) has "kind": "pattern":
  "background": "#f6eee0"       paper tone printed edge to edge (null = transparent)
  "palette": "autumn"           a design.PALETTES name, or a dict
  "elements": [                 painted largest first, then smaller ones fill the gaps
    {"motif": "ghost", "size": 0.16, "count": 7, "args": {"book": true}, "tilt": 0.25},
    {"motif": "maple_leaf", "size": 0.08, "count": 14, "colors": [["#d8612e", "#f0a24a"], ...]},
    {"motif": "sparkle", "size": 0.025, "fill": true}   # "fill": as many as fit
  Optional per element: "spacing" (gap multiplier), "tilt" (random rotation),
  "y_range": [0.1, 0.6] (keep it in part of the height), "args" (motif options).
  ]
  "mug_colors": ["Orange", "Black"]   accent colors (rim, handle, inside) for mockups
Sizes are fractions of the print height. The wrap is seamless left to right:
anything painted across the right edge continues on the left, so the join
at the mug's handle is invisible.
"""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from watercolor import Canvas, hexrgb
import motifs as M
import design as D

MUG_COLORS = {'White': '#f7f7f5', 'Orange': '#e8742c', 'Black': '#2a2a2d', 'Maroon': '#6e1f2d', 'Pink': '#f2a7b8',
              'Purple': '#7a5aa6', 'Yellow': '#f3cf4a', 'Red': '#c8332f', 'Navy': '#243457', 'Blue': '#2f6fb5',
              'Light Blue': '#a9d1ea', 'Light Green': '#a9d6a2'}


def palette(spec):
    P = spec.get('palette', 'blush')
    return dict(D.PALETTES[P]) if isinstance(P, str) else dict(P)


def place(spec, W, H, rnd):
    """Dart-throwing placement on a horizontal cylinder: no overlaps, even spread."""
    items = []
    def free(x, y, r, k):
        for (ox, oy, orr, _) in items:
            dx = abs(x - ox); dx = min(dx, W - dx)
            if math.hypot(dx, y - oy) < (r + orr) * k:
                return False
        return True
    els = sorted(spec['elements'], key=lambda e: -e['size'])
    for e in els:
        r = e['size'] * H
        want = 10 ** 6 if e.get('fill') else e.get('count', 5)
        got, fails = 0, 0
        pad = r * e.get('edge', 0.9)
        while got < want and fails < (4000 if e.get('fill') else 20000):
            x = rnd.uniform(0, W)
            lo, hi = e.get('y_range', (0, 1))
            y = rnd.uniform(max(pad, lo * H), min(H - pad, hi * H))
            if free(x, y, r, e.get('spacing', 1.05)):
                items.append((x, y, r, e)); got += 1; fails = 0
            else:
                fails += 1
    return items


def paint(spec, W, H, seed_offset=0):
    """Returns an RGB(A) image W x H, seamless left to right."""
    seed = spec.get('seed', 1) + seed_offset
    rnd = random.Random(seed)
    P = palette(spec)
    items = place(spec, W, H, rnd)
    m = int(max(r for _, _, r, _ in items) * 1.6) + 8
    c = Canvas(W + 2 * m, H, seed=seed)
    for x, y, r, e in items:
        fn = M.MOTIFS[e['motif']]
        kw = dict(e.get('args', {}))
        if e.get('colors'):
            pair = rnd.choice(e['colors'])
            kw['color'] = pair[0]
            if len(pair) > 1 and e['motif'] in ('maple_leaf', 'rose'):
                kw['color2'] = pair[1]
        if e.get('tilt'):
            key = 'lean' if e['motif'] == 'ghost' else 'angle'
            kw[key] = rnd.uniform(-e['tilt'], e['tilt'])
        fn(c, m + x, y, r, P, **kw)
    # fold the spill beyond each edge back onto the other side (seamless wrap)
    A = c.absorb
    absorb = A[:, m:m + W].copy()
    absorb[:, W - m:W] += A[:, 0:m]
    absorb[:, 0:m] += A[:, W + m:W + 2 * m]
    ink_full = c.ink
    ink = ink_full.crop((m, 0, m + W, H))
    ink.alpha_composite(ink_full.crop((0, 0, m, H)), (W - m, 0))
    ink.alpha_composite(ink_full.crop((W + m, 0, W + 2 * m, H)), (0, 0))
    bg = spec.get('background')
    if bg:
        mask_im = Image.new('L', (W + 2 * m, H), 0)
        dr = ImageDraw.Draw(mask_im)
        for shape in c.reserves:
            dr.polygon([(px, py) for px, py, *_ in shape], fill=255)
        mk = np.asarray(mask_im, dtype=np.float32) / 255
        res = mk[:, m:m + W].copy()
        res[:, W - m:W] = np.maximum(res[:, W - m:W], mk[:, 0:m])
        res[:, 0:m] = np.maximum(res[:, 0:m], mk[:, W + m:W + 2 * m])
        res = np.asarray(Image.fromarray((res * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, H * 0.002))),
                         dtype=np.float32) / 255
        grain = c._grain[:, m:m + W]
        k = -np.log(np.clip(hexrgb(bg), 0.03, 1.0))
        paper = (1 + 0.35 * (grain - 0.5) * 2)[..., None] * k[None, None, :]
        absorb = absorb + paper * (1 - res[..., None])
        rgb = np.exp(-absorb)
        im = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), 'RGB').convert('RGBA')
        im.alpha_composite(ink)
        return im.convert('RGB')
    # transparent: alpha from absorbed light (as watercolor.Canvas.rgba)
    rgb = np.exp(-absorb)
    a = np.clip((1 - rgb.min(axis=2)) * 1.25, 0, 1)
    safe = np.where(a > 1e-3, a, 1)[..., None]
    col = np.clip((rgb - (1 - a[..., None])) / safe, 0, 1)
    im = Image.fromarray(np.dstack([col * 255, a * 255]).astype(np.uint8), 'RGBA')
    im.alpha_composite(ink)
    return im


def mug_mockup(wrap, accent='#f7f7f5', handle_right=True, size=1200, bg=('#efe6da', '#e2d4c2'), cover=0.81):
    """A shaded 3D 11oz mug with the wrap printed on it. cover = share of the
    circumference the print covers (centered opposite the handle)."""
    W, H = wrap.size
    wr = np.asarray(wrap.convert('RGB'), dtype=np.float32) / 255
    C = W / cover                       # full circumference in wrap px
    bw = int(size * 0.5)                # body width on screen
    s = bw / (C / math.pi)              # screen px per wrap px at the front
    bh = int(bw * 1.17)                 # an 11oz mug is about 1.17x taller than wide
    e = bw * 0.12                       # perspective: half-height of the rim ellipse
    img = Image.new('RGB', (size, int(size * 0.85)), bg[0])
    # soft vertical background gradient
    g = np.linspace(0, 1, img.height)[:, None, None]
    img = Image.fromarray((((1 - g) * hexrgb(bg[0]) + g * hexrgb(bg[1])) * np.ones((1, size, 3)) * 255).astype(np.uint8))
    cx = size // 2 - (int(bw * 0.08) if handle_right else -int(bw * 0.08)); top = int(img.height * 0.2)
    x0 = cx - bw // 2
    acc = hexrgb(accent)
    white = hexrgb('#f7f7f5')
    # shadow
    sh = Image.new('L', img.size, 0)
    ImageDraw.Draw(sh).ellipse((x0 - bw * 0.05, top + bh - e * 0.2, x0 + bw * 1.25, top + bh + e * 1.6), fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.025))
    img = Image.composite(Image.new('RGB', img.size, (120, 100, 85)), img, sh.point(lambda v: int(v * 0.55)))
    body = np.zeros((bh + int(e * 2) + 2, bw, 4), dtype=np.float32)
    a0 = math.pi * (1 - cover)
    for col in range(bw):
        u = (col + 0.5) / bw * 2 - 1
        phi = math.asin(max(-1, min(1, u)))
        alpha = (math.pi / 2 - phi) if handle_right else (1.5 * math.pi - phi)
        xw = (alpha - a0) / (2 * math.pi) * C
        dy = e * math.cos(phi)          # the column's bottom/top follow the ellipse
        light = 0.72 + 0.28 * math.cos(phi + 0.35)
        spec_hl = 0.09 * math.exp(-((u + 0.5) / 0.12) ** 2)
        ys = np.arange(bh)
        yw = ((ys / bh) - 0.05) / 0.9 * H
        colr = np.tile(white, (bh, 1))
        if 0 <= xw < W:
            inside = (yw >= 0) & (yw < H)
            colr[inside] = wr[np.clip(yw[inside].astype(int), 0, H - 1), int(xw)]
        colr = np.clip(colr * light + spec_hl, 0, 1)
        y_off = int(round(dy))
        body[y_off:y_off + bh, col, :3] = colr
        body[y_off:y_off + bh, col, 3] = 1
    bim = Image.fromarray((body * 255).astype(np.uint8), 'RGBA')
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    # handle
    hd = ImageDraw.Draw(layer)
    hx = x0 + bw - int(bw * 0.04) if handle_right else x0 - int(bw * 0.3) + int(bw * 0.04)
    hy0, hy1 = top + int(bh * 0.12) + int(e), top + int(bh * 0.78) + int(e)
    hc = tuple(int(v * 255 * 0.85) for v in acc)
    hw = int(bw * 0.36)
    hx = x0 + bw - hw // 2 if handle_right else x0 - hw // 2
    hd.ellipse((hx, hy0, hx + hw, hy1), outline=hc, width=int(bw * 0.075))
    layer.alpha_composite(bim, (x0, top))
    # rim and inside
    rd = ImageDraw.Draw(layer)
    rd.ellipse((x0, top - e, x0 + bw, top + e), fill=tuple(int(v * 255) for v in acc * 0.97) + (255,))
    rd.ellipse((x0 + bw * 0.035, top - e * 0.86, x0 + bw * 0.965, top + e * 0.86),
               fill=tuple(int(v * 255) for v in acc * 0.72) + (255,))
    rd.ellipse((x0, top - e, x0 + bw, top + e), outline=tuple(int(v * 255 * 0.8) for v in acc) + (255,), width=max(2, bw // 200))
    img = img.convert('RGBA'); img.alpha_composite(layer)
    return img.convert('RGB')


def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path)); os.makedirs(out, exist_ok=True)
    sid = spec['id']
    sizes = [tuple(int(v) for v in a.split('x')) for a in sys.argv[sys.argv.index('--size') + 1:] if 'x' in a] \
        if '--size' in sys.argv else [(2475, 1155)]
    preview = '--preview' in sys.argv
    files = []
    for W, H in sizes:
        if preview:
            im = paint(spec, W // 3, H // 3)
        else:
            im = paint(spec, W, H)
        f = os.path.join(out, f'{sid}-wrap-{W}x{H}.png'); im.save(f, dpi=(300, 300)); files.append(f)
    wrap = Image.open(files[0])
    for name in spec.get('mug_colors', ['White']):
        for side, hr in (('a', True), ('b', False)):
            f = os.path.join(out, f'{sid}-mug-{name.lower().replace(" ", "-")}-{side}.jpg')
            mug_mockup(wrap, MUG_COLORS[name], handle_right=hr, size=900 if preview else 1400).save(f, quality=90)
            files.append(f)
    print(json.dumps({'files': [os.path.basename(f) for f in files]}))


if __name__ == '__main__':
    main()
