#!/usr/bin/env python3
"""Render a print-on-demand design from a JSON spec.

usage: design.py SPEC.json OUT_DIR [--preview]

Writes to OUT_DIR:
  <id>.png              4500 x 5400 transparent PNG (Printify's front print
                        area for most shirts/sweatshirts at 300 dpi)
  <id>-paper.jpg        the design on watercolor paper (for listings / wall art)
  <id>-mockup-*.jpg     flat shirt mockups in the colors the spec lists
  <id>-preview.jpg      small contact image of all of the above
--preview renders at 1/3 size for quick checks.

Spec (see designs/*.json):
{
  "id": "currently-reading",
  "template": "arch" | "stack" | "badge" | "wreath",
  "top": "Currently", "bottom": "Reading", "small": "optional third line",
  "top_font": "DancingScript", "bottom_font": "PlayfairDisplay", "small_font": "JosefinSans",
  "art": [{"motif": "books", "x": 0.0, "y": 0.0, "s": 0.28}],    # x/y in design widths from centre; "front": true = painted first, later paint goes around it
  "florals": "bouquet" | "wreath" | null,
  "flowers": ["rose", "daisy", "rose", "wildflower"],   # the bouquet's four blooms
  "palette": "blush" | "sage" | "citrus" | "autumn" | "lavender" | "ocean",
  "ink": "#343034",
  "shirt_colors": ["white", "natural", "heather_pink"],
  "seed": 7
}
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont
import watercolor as wc
import motifs as M

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {f[:-4]: os.path.join(HERE, 'fonts', f) for f in os.listdir(os.path.join(HERE, 'fonts')) if f.endswith('.ttf')}

PALETTES = {
    'blush':    {'main': '#e58a9b', 'main2': '#f5c3b8', 'accent': '#f2b25c', 'accent2': '#f8dca0', 'leaf': '#7fa37a', 'leaf2': '#b9cf9c', 'object': '#9cc0cf', 'object2': '#c9e0e6'},
    'sage':     {'main': '#d9a6a0', 'main2': '#f0d2c8', 'accent': '#f4efe3', 'accent2': '#e8dcc0', 'leaf': '#7f9c86', 'leaf2': '#b8ccb4', 'object': '#a7bfa9', 'object2': '#d4e2d2'},
    'citrus':   {'main': '#f08a5d', 'main2': '#f9c784', 'accent': '#f2d34f', 'accent2': '#f7e79a', 'leaf': '#6f9e5b', 'leaf2': '#a9cf8c', 'object': '#7fb7c9', 'object2': '#c2e1ea'},
    'autumn':   {'main': '#c8643b', 'main2': '#e8a05d', 'accent': '#e2b04a', 'accent2': '#f0d08a', 'leaf': '#8a8a4a', 'leaf2': '#c2b86e', 'object': '#b57b5c', 'object2': '#dcb296'},
    'lavender': {'main': '#a88ad1', 'main2': '#dcc8ef', 'accent': '#f0b8c8', 'accent2': '#f8dde4', 'leaf': '#8aa58f', 'leaf2': '#c3d6c3', 'object': '#b3b8e0', 'object2': '#dde0f3'},
    'ocean':    {'main': '#5b9ec9', 'main2': '#a9d3ea', 'accent': '#f2c26b', 'accent2': '#f8e2ae', 'leaf': '#6aa39a', 'leaf2': '#a8d2c8', 'object': '#7fb6d8', 'object2': '#c6e2f1'},
}
SHIRTS = {'white': '#f7f7f5', 'natural': '#efe6d6', 'heather_pink': '#ecc9cc', 'light_blue': '#c9dcea', 'sand': '#dccbb0',
          'sage': '#b9c7b3', 'ivory': '#f3eee1', 'heather_gray': '#cfcfcf'}
W, H = 4500, 5400


def hex3(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fit_size(text, font, max_w, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(font, size)
        if f.getlength(text) <= max_w:
            return size
        size = int(size * 0.94)
    return size


def render(spec, scale=1.0):
    w, h = int(W * scale), int(H * scale)
    P = dict(PALETTES[spec.get('palette', 'blush')]); P.update(spec.get('colors', {}))
    c = wc.Canvas(w, h, seed=spec.get('seed', 1))
    cx, cy = w / 2, h / 2
    ink = hex3(spec.get('ink', '#343034'))
    t = spec.get('template', 'arch')
    f_top = FONTS[spec.get('top_font', 'DancingScript')]
    f_bot = FONTS[spec.get('bottom_font', 'PlayfairDisplay')]
    f_small = FONTS[spec.get('small_font', 'JosefinSans')]
    art_y = {'arch': 0.47, 'stack': 0.4, 'badge': 0.5, 'wreath': 0.5}[t] * h
    # florals first (they sit behind objects)
    fl = spec.get('florals')
    if fl == 'bouquet':
        M.bouquet(c, cx, art_y + w * spec.get('florals_dy', 0.08), w * spec.get('florals_s', 0.28), P,
                  flowers=tuple(spec.get('flowers', ('rose', 'daisy', 'rose', 'wildflower'))))
    elif fl == 'wreath':
        M.wreath(c, cx, art_y, w * spec.get('florals_s', 0.36), P)
    # objects marked "front" are painted first; everything after goes around them
    art = spec.get('art', [])
    for a in [a for a in art if a.get('front')] + [a for a in art if not a.get('front')]:
        fn = M.MOTIFS[a['motif']]
        kw = {k: v for k, v in a.items() if k not in ('motif', 'x', 'y', 's', 'front')}
        before = c.snapshot() if a.get('front') else None
        fn(c, cx + a.get('x', 0) * w, art_y + a.get('y', 0) * w, a.get('s', 0.2) * w, P, **kw)
        if before:
            c.paint_around(before)
    # lettering
    top, bot, small = spec.get('top'), spec.get('bottom'), spec.get('small')
    if t in ('arch', 'badge'):
        if top:
            size = fit_size(top, f_top, w * 0.78, int(w * 0.16))
            c.text(top, f_top, size, cx, art_y - w * 0.36, fill=ink, arc=w * 0.9 if t == 'badge' else None)
        if bot:
            size = fit_size(bot, f_bot, w * 0.82, int(w * 0.13))
            c.text(bot, f_bot, size, cx, art_y + w * 0.4, fill=ink)
        if small:
            size = fit_size(small, f_small, w * 0.6, int(w * 0.045))
            c.text(small.upper(), f_small, size, cx, art_y + w * 0.52, fill=ink)
    elif t == 'stack':
        if top:
            size = fit_size(top, f_top, w * 0.8, int(w * 0.16))
            c.text(top, f_top, size, cx, art_y + w * 0.38, fill=ink)
        if bot:
            size = fit_size(bot, f_bot, w * 0.8, int(w * 0.1))
            c.text(bot, f_bot, size, cx, art_y + w * 0.53, fill=ink)
        if small:
            size = fit_size(small, f_small, w * 0.6, int(w * 0.045))
            c.text(small.upper(), f_small, size, cx, art_y + w * 0.64, fill=ink)
    elif t == 'wreath':
        if top:
            size = fit_size(top, f_top, w * 0.5, int(w * 0.12))
            c.text(top, f_top, size, cx, art_y - w * 0.05, fill=ink)
        if bot:
            size = fit_size(bot, f_bot, w * 0.46, int(w * 0.07))
            c.text(bot, f_bot, size, cx, art_y + w * 0.09, fill=ink)
    return c


def crop_to_content(im, pad=0.03):
    box = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    return box


def shirt_mockup(design, color, size=1400):
    """Flat-lay tee drawn in code. The print is shown about 11 in wide on a
    ~20 in wide body, the usual adult front print."""
    im = Image.new('RGB', (size, size), (236, 233, 228))
    d = ImageDraw.Draw(im)
    s = size / 1000
    col = hex3(SHIRTS[color])
    dark = tuple(max(0, v - 26) for v in col)
    body = [(330, 150), (420, 118), (455, 150), (500, 160), (545, 150), (580, 118), (670, 150), (850, 250), (790, 380),
            (705, 335), (712, 900), (288, 900), (295, 335), (210, 380), (150, 250)]
    body = [(x * s, y * s) for x, y in body]
    d.polygon([(x + 9 * s, y + 12 * s) for x, y in body], fill=(214, 210, 204))
    d.polygon(body, fill=col)
    d.line([(420 * s, 118 * s), (455 * s, 150 * s), (500 * s, 160 * s), (545 * s, 150 * s), (580 * s, 118 * s)], fill=dark, width=int(9 * s))
    d.line([(295 * s, 335 * s), (305 * s, 250 * s)], fill=dark, width=int(3 * s))
    d.line([(705 * s, 335 * s), (695 * s, 250 * s)], fill=dark, width=int(3 * s))
    box = crop_to_content(design)
    art = design.crop(box) if box else design
    max_w, max_h = 300 * s, 360 * s
    r = min(max_w / art.width, max_h / art.height)
    art = art.resize((max(1, int(art.width * r)), max(1, int(art.height * r))), Image.LANCZOS)
    im.paste(art, (int(500 * s - art.width / 2), int(215 * s)), art)
    return im


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    prev = '--preview' in sys.argv
    os.makedirs(out, exist_ok=True)
    c = render(spec, 1 / 3 if prev else 1.0)
    design = c.rgba()
    sid = spec['id']
    design.save(os.path.join(out, f'{sid}.png'), dpi=(300, 300), optimize=True)
    paper = c.on_paper()
    paper.convert('RGB').save(os.path.join(out, f'{sid}-paper.jpg'), quality=90)
    mocks = []
    for col in spec.get('shirt_colors', ['white', 'natural']):
        m = shirt_mockup(design, col)
        m.save(os.path.join(out, f'{sid}-mockup-{col}.jpg'), quality=88)
        mocks.append(m)
    # contact preview
    tiles = [paper.resize((600, 720))] + [m.resize((720, 720)) for m in mocks]
    Wp = sum(t.width for t in tiles) + 20 * (len(tiles) + 1)
    sheet = Image.new('RGB', (Wp, 760), (245, 243, 238))
    x = 20
    for tl in tiles:
        sheet.paste(tl, (x, 20)); x += tl.width + 20
    sheet.save(os.path.join(out, f'{sid}-preview.jpg'), quality=85)
    print(sid, design.size, 'ok')


if __name__ == '__main__':
    main()
