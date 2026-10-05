"""Extra Etsy listing photos (9 per listing) drawn from the real print files.

Printify gives our mugs 1 photo, tees 3, sweatshirts 2-3 and stickers 6. Etsy
allows 20 and listings with more photos sell better, so this draws 9 more for
each listing from the exact artwork Printify prints (downloaded from the
product's print area), with no stock mockups:

  01 hero          the product with the design name
  02 art           the watercolor art on paper
  03 detail        two close-up crops of the art
  04 scene         a second view (other color, other side of the mug, sticker on a laptop)
  05 options       colors or sizes, drawn to scale where size matters
  06 size/specs    size chart (shirts, sweatshirts) or product specs
  07 details       details and care, word for word from printify.py
  08 collection    every product in this design
  09 made to order how print on demand works, plus who it's for

usage: python3 photos.py OUT_DIR [--only PRODUCT_ID ...] [--skip-full]
       (--skip-full skips listings that already have 9+ Printify photos)

Printify's API ignores custom images, so the owner uploads these: on the Etsy
listing (Edit > Photos), or in Printify (product > View all mockups > Upload).
"""
import io, json, math, os, sys, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import printify as P
import pattern

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, '..', '..', 'storefront', 'etsy', '_build', 'fonts')
SHOP = 29114200
W, H = 2400, 1800
CREAM, INK, MUTED = (248, 244, 237), (38, 49, 59), (107, 117, 128)
KIND = {12: 'tee', 49: 'sweatshirt', 68: 'mug', 635: 'accent_mug', 282: 'poster', 400: 'sticker'}
NOUN = {'tee': 'Shirt', 'sweatshirt': 'Sweatshirt', 'mug': 'Mug', 'accent_mug': 'Accent Mug', 'poster': 'Art Print', 'sticker': 'Sticker'}
DESIGN_KEYS = [('Pumpkins and Purrs', 'pumpkins-and-purrs'), ("Grandma's Garden", 'grandmas-garden'), ('Sufganiyot', 'sufganiyot-season'), ('Gingerbread', 'christmas-cookies'), ('Christmas Cookie', 'christmas-cookies'),
               ('Cocoa', 'cocoa-season'), ('Cardinal', 'snowy-pine-cardinals'), ('Soup', 'soup-season'),
               ('Autumn Leaves', 'autumn-leaves'), ('Ghost', 'reading-ghosts'), ('Strawberry', 'strawberry-season'),
               ('Morning Walks', 'dog-walks-club'), ('Currently Reading', 'currently-reading')]
DISPLAY = {'dog-walks-club': 'Morning Walks & Good Dogs', 'pumpkins-and-purrs': 'Pumpkins & Purrs'}   # the name the Etsy listings use
FOR_WHO = {
    'pumpkins-and-purrs': 'cat people who like their Halloween more cozy than creepy',
    'grandmas-garden': 'grandmas who grow the best flowers, from the grandkids',
    'sufganiyot-season': 'Hanukkah hosts, latke parties and anyone who loves a jelly donut',
    'christmas-cookies': 'holiday bakers and cookie-swap regulars',
    'cocoa-season': 'snow days, cozy nights and hot cocoa lovers',
    'snowy-pine-cardinals': 'bird lovers and snowy-morning coffee drinkers',
    'soup-season': 'soup-season cooks and cozy kitchens',
    'autumn-leaves': 'fall lovers and sweater-weather mornings',
    'reading-ghosts': 'book lovers who like their Halloween cute',
    'strawberry-season': 'berry pickers, gardeners and summer lovers',
    'dog-walks-club': 'dog walkers, dog moms and dog dads',
    'currently-reading': 'book clubs, readers and library lovers',
}
# Flat measurements in inches (width armpit to armpit, length shoulder to hem), from the
# Bella+Canvas 3001 and Gildan 18000 size charts published by Merchize, OOShirts and others.
SIZE_CHART = {'tee': {'S': (18, 28), 'M': (20, 29), 'L': (22, 30), 'XL': (24, 31), '2XL': (26, 32), '3XL': (28, 33)},
              'sweatshirt': {'S': (20, 27), 'M': (22, 28), 'L': (24, 29), 'XL': (26, 30), '2XL': (28, 31), '3XL': (30, 32)}}
GARMENT = {'tee': 'Bella+Canvas 3001 unisex tee', 'sweatshirt': 'Gildan 18000 unisex crewneck'}
MUG_FACTS = ['11 oz (0.33 l) white ceramic', 'Glossy finish, C-shaped handle', 'Lead and BPA-free', 'Microwave and dishwasher safe']


def F(name, size):
    return ImageFont.truetype(os.path.join(FD, {'serif': 'Fraunces_600SemiBold.ttf', 'serif_it': 'Fraunces_400Regular_Italic.ttf',
                                               'sans': 'DMSans_400Regular.ttf', 'med': 'DMSans_500Medium.ttf',
                                               'bold': 'DMSans_700Bold.ttf'}[name]), size)


def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c, t, base=(255, 255, 255)):
    return tuple(round(a + (b - a) * t) for a, b in zip(c, base))


def wrap(d, text, f, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def text(d, xy, s, f, fill, maxw, lead=1.25):
    x, y = xy
    for ln in wrap(d, s, f, maxw):
        d.text((x, y), ln, font=f, fill=fill); y += int(f.size * lead)
    return y


def fetch(url, cache):
    p = os.path.join(cache, url.rstrip('/').split('/')[-1] + '.png')
    if not os.path.exists(p):
        req = urllib.request.Request(url, headers={'User-Agent': 'edgex-pod-desk'})
        open(p, 'wb').write(urllib.request.urlopen(req, timeout=180).read())
    return Image.open(p).convert('RGBA')


def trimmed(im):
    box = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop(box) if box else im


def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def shadow(canvas, im, xy, blur=30, off=(0, 22), op=80):
    a = im.getchannel('A') if im.mode == 'RGBA' else Image.new('L', im.size, 255)
    sh = Image.new('L', canvas.size, 0); sh.paste(a.point(lambda v: v * op // 255), (xy[0] + off[0], xy[1] + off[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(Image.new('RGB', canvas.size, (90, 80, 70)), (0, 0), sh)
    canvas.paste(im, xy, im if im.mode == 'RGBA' else None)


# ---------- mockups (all drawn here from the real print file) ----------

def garment(art, color, kind, size=1500):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = size / 1000
    col = rgb(color); dark = tuple(max(0, v - 26) for v in col)
    if kind == 'tee':
        body = [(330, 150), (420, 118), (455, 150), (500, 160), (545, 150), (580, 118), (670, 150), (850, 250), (790, 380),
                (705, 335), (712, 900), (288, 900), (295, 335), (210, 380), (150, 250)]
        box = (300, 215, 360)
    else:
        body = [(330, 150), (420, 118), (455, 150), (500, 160), (545, 150), (580, 118), (670, 150), (800, 260), (895, 600),
                (795, 645), (708, 410), (714, 860), (286, 860), (292, 410), (205, 645), (105, 600), (200, 260)]
        box = (290, 225, 330)
    pts = [(x * s, y * s) for x, y in body]
    d.polygon([(x + 9 * s, y + 12 * s) for x, y in pts], fill=(0, 0, 0, 40))
    d.polygon(pts, fill=col + (255,))
    d.line([(420 * s, 118 * s), (455 * s, 150 * s), (500 * s, 160 * s), (545 * s, 150 * s), (580 * s, 118 * s)], fill=dark, width=int(10 * s))
    if kind == 'sweatshirt':   # ribbed cuffs and waistband
        d.line([(893 * s, 590 * s), (797 * s, 634 * s)], fill=dark, width=int(30 * s))
        d.line([(107 * s, 590 * s), (203 * s, 634 * s)], fill=dark, width=int(30 * s))
        d.rectangle((286 * s, 822 * s, 714 * s, 860 * s), fill=dark)
    else:
        d.line([(295 * s, 335 * s), (305 * s, 250 * s)], fill=dark, width=int(3 * s))
        d.line([(705 * s, 335 * s), (695 * s, 250 * s)], fill=dark, width=int(3 * s))
    a = fit(trimmed(art), box[0] * s, box[2] * s)
    im.alpha_composite(a, (int(500 * s - a.width / 2), int(box[1] * s)))
    return im


def mug_wrap(product, art):
    ph = product['print_areas'][0]['placeholders'][0]['images']
    if len(ph) == 1 and abs(ph[0]['scale'] - 1) < 0.05:
        return art                                     # all-over pattern: the file is the wrap
    WW, HH = 2475, 1155
    wr = Image.new('RGBA', (WW, HH), (247, 247, 245, 255))
    for p in ph:
        a = art.resize((int(p['scale'] * WW), int(p['scale'] * WW * art.height / art.width)), Image.LANCZOS)
        wr.alpha_composite(a, (int(p['x'] * WW - a.width / 2), int(p['y'] * HH - a.height / 2)))
    return wr


def mug(wrapimg, accent='#f7f7f5', right=True, size=1500):
    # mug_mockup reads the wrap right-to-left, so mirror it to keep lettering readable,
    # then key out the flat background so the mug sits on any card color with its shadow
    bg = (248, 244, 237)
    flat = Image.new('RGB', wrapimg.size, (247, 247, 245)); flat.paste(wrapimg, (0, 0), wrapimg if wrapimg.mode == 'RGBA' else None)
    m = pattern.mug_mockup(ImageOps.mirror(flat), accent=accent, handle_right=right, size=size, bg=('#f8f4ed', '#f8f4ed'))
    import numpy as np
    a = np.asarray(m, dtype=np.int16); dist = np.abs(a - np.array(bg)).sum(axis=2)
    alpha = np.clip(dist * 6, 0, 255).astype(np.uint8)
    out = m.convert('RGBA'); out.putalpha(Image.fromarray(alpha)); return out


def sticker(art, size=1300):
    a = fit(trimmed(art), size * 0.82, size * 0.82)
    pad = int(size * 0.04)
    base = Image.new('L', (a.width + pad * 2, a.height + pad * 2), 0); base.paste(a.getchannel('A'), (pad, pad))
    edge = base.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(2))
    st = Image.new('RGBA', base.size, (255, 255, 255, 0)); st.putalpha(edge.point(lambda v: 255 if v > 90 else 0))
    st.alpha_composite(a, (pad, pad))
    return st


def poster(art, size=1300):
    a = fit(trimmed(art), size * 0.5, size * 0.62)
    pw, ph_ = int(size * 0.62), int(size * 0.62 * 1.27)
    paper = Image.new('RGBA', (pw, ph_), (252, 250, 246, 255))
    paper.alpha_composite(a, ((pw - a.width) // 2, (ph_ - a.height) // 2))
    fr = Image.new('RGBA', (pw + 50, ph_ + 50), (52, 46, 40, 255)); fr.paste(paper, (25, 25))
    return fr


def product_mock(kind, product, art, color=None, right=True):
    if kind in ('tee', 'sweatshirt'):
        return garment(art, color or '#f7f7f5', kind)
    if kind == 'mug':
        return mug(mug_wrap(product, art), right=right).convert('RGBA')
    if kind == 'accent_mug':
        return mug(art, accent=color or '#c0392b', right=right).convert('RGBA')
    if kind == 'sticker':
        return sticker(art)
    return poster(art)


# ---------- cards ----------

def canvas(tint=None):
    im = Image.new('RGB', (W, H), CREAM)
    if tint:
        ImageDraw.Draw(im).rectangle((int(W * 0.42), 0, W, H), fill=mix(tint, 0.86))
    return im


def kicker(d, s, acc, xy=(150, 170)):
    d.text(xy, s.upper(), font=F('bold', 46), fill=acc)


def footer(d, s='Edgex studio'):
    d.text((150, H - 120), s, font=F('med', 34), fill=MUTED)


def colors_of(product):
    out = []
    for o in product['options']:
        if o['type'] == 'color':
            en = {vid for v in product['variants'] if v['is_enabled'] for vid in v['options']}
            out = [(v['title'], v['colors'][0]) for v in o['values'] if v['id'] in en]
    return out


def sizes_of(product):
    en = {vid for v in product['variants'] if v['is_enabled'] for vid in v['options']}
    for o in product['options']:
        if o['type'] == 'size':
            return [v['title'] for v in o['values'] if v['id'] in en]
    return []


def make_set(product, group, art_cache, out):
    kind = KIND[product['blueprint_id']]
    did = next(v for k, v in DESIGN_KEYS if k in product['title'])
    spec = json.load(open(os.path.join(HERE, 'designs', did + '.json')))
    name, acc = DISPLAY.get(did, spec['name']), rgb(spec.get('ink', '#3b4a5a'))
    art = fetch(product['print_areas'][0]['placeholders'][0]['images'][0]['src'], art_cache)
    cols = colors_of(product); first = cols[0][1] if cols else None
    noun = NOUN[kind]; os.makedirs(out, exist_ok=True); files = []

    def save(im, n, label):
        p = os.path.join(out, f'{n:02d}-{label}.jpg'); im.convert('RGB').save(p, 'JPEG', quality=88, optimize=True); files.append(p)

    # 01 hero
    im = canvas(acc); d = ImageDraw.Draw(im)
    m = fit(product_mock(kind, product, art, first), 1300 if kind == 'sticker' else 1500, 1300 if kind == 'sticker' else 1500)
    shadow(im, m, (int(W * 0.68 - m.width / 2), int(H / 2 - m.height / 2)))
    kicker(d, noun, acc); y = text(d, (150, 250), name, F('serif', 120), INK, 820, 1.12)
    text(d, (150, y + 40), 'Watercolor art by our studio, printed to order', F('sans', 50), MUTED, 780)
    footer(d); save(im, 1, 'hero')
    # 02 art
    im = canvas(); d = ImageDraw.Draw(im)
    a = fit(trimmed(art), 1300 if trimmed(art).width > 1.5 * trimmed(art).height else 1250, 1350)
    paper = Image.new('RGBA', (a.width + 160, a.height + 160), (253, 252, 249, 255)); paper.alpha_composite(a, (80, 80))
    shadow(im, paper, (int(W * 0.66 - paper.width / 2), int(H / 2 - paper.height / 2)))
    kicker(d, 'The art', acc); y = text(d, (150, 250), 'The watercolor painting', F('serif', 96), INK, 640, 1.15)
    text(d, (150, y + 50), 'Digitally painted in a watercolor style by our studio, then printed on your ' + noun.lower() + '.',
         F('sans', 46), MUTED, 600)
    footer(d); save(im, 2, 'art')
    # 03 detail
    im = canvas(); d = ImageDraw.Draw(im); t = trimmed(art)
    cw = int(min(t.width, t.height) * (0.32 if kind not in ('mug', 'accent_mug') or t.width < 2 * t.height else 0.5))
    al = t.getchannel('A').resize((max(1, t.width // 20), max(1, t.height // 20)))
    import numpy as np
    A = np.asarray(al, dtype=np.float32); k = max(1, cw // 20); best = []
    for yy in range(0, max(1, A.shape[0] - k), max(1, k // 4)):
        for xx in range(0, max(1, A.shape[1] - k), max(1, k // 4)):
            best.append((A[yy:yy + k, xx:xx + k].mean(), xx * 20, yy * 20))
    best.sort(reverse=True); picks = []
    for sc, xx, yy in best:
        if all(abs(xx - px) > cw * 0.8 or abs(yy - py) > cw * 0.8 for px, py in picks): picks.append((xx, yy))
        if len(picks) == 2: break
    for i, (x0, y0) in enumerate(picks):
        crop = Image.new('RGBA', (cw, cw), (253, 252, 249, 255)); crop.alpha_composite(t.crop((x0, y0, x0 + cw, y0 + cw)))
        crop = crop.resize((900, 900), Image.LANCZOS)
        shadow(im, crop, (150 + i * 1050 + 0, 560))
    kicker(d, 'Up close', acc); d.text((150, 250), 'Every wash and brushstroke', font=F('serif', 96), fill=INK)
    save(im, 3, 'detail')
    # 04 scene
    im = canvas(acc); d = ImageDraw.Draw(im)
    if kind in ('tee', 'sweatshirt') and len(cols) > 1:
        m = fit(product_mock(kind, product, art, cols[1][1]), 1500, 1500); line = f'Shown in {cols[1][0]}'
    elif kind in ('mug', 'accent_mug'):
        m = fit(product_mock(kind, product, art, cols[-1][1] if cols else None, right=False), 1500, 1500)
        line = 'The other side' if kind == 'mug' else 'Printed all the way around'
    elif kind == 'sticker':
        lap = Image.new('RGBA', (1500, 1000), (0, 0, 0, 0)); ld = ImageDraw.Draw(lap)
        ld.rounded_rectangle((0, 0, 1500, 1000), 60, fill=(196, 199, 204, 255))
        s_ = fit(sticker(art), 560, 560); lap.alpha_composite(s_, (880, 380)); m = lap; line = 'Made for laptops, notebooks and planners'
    else:
        m = fit(poster(art), 1200, 1500); line = 'Frame not included'
    shadow(im, m, (int(W * 0.68 - m.width / 2), int(H / 2 - m.height / 2)))
    kicker(d, name, acc); text(d, (150, 250), line, F('serif', 96), INK, 760, 1.15); footer(d); save(im, 4, 'scene')
    # 05 options
    im = canvas(); d = ImageDraw.Draw(im)
    if kind in ('tee', 'sweatshirt', 'accent_mug') and cols:
        kicker(d, 'Options', acc); d.text((150, 250), f'{len(cols)} colors to choose from', font=F('serif', 96), fill=INK)
        n = len(cols); cw = min(640, (W - 300 - 60 * (n - 1)) // n)
        for i, (cn, ch) in enumerate(cols):
            x = 150 + i * (cw + 60)
            m = fit(product_mock(kind, product, art, ch), cw, cw); im.paste(m, (x + (cw - m.width) // 2, 560), m)
            d.ellipse((x + cw // 2 - 34, 560 + cw + 40, x + cw // 2 + 34, 560 + cw + 108), fill=rgb(ch), outline=(200, 196, 190), width=3)
            tw = d.textlength(cn, font=F('med', 44)); d.text((x + cw / 2 - tw / 2, 560 + cw + 130), cn, font=F('med', 44), fill=INK)
    else:
        sz = sizes_of(product)
        kicker(d, 'Sizes', acc)
        if kind in ('sticker', 'poster'):
            d.text((150, 250), 'Shown to scale', font=F('serif', 96), fill=INK)
            dims = []
            for s_ in sz:
                nums = [float(x) for x in ''.join(c if (c.isdigit() or c == '.') else ' ' for c in s_).split()]
                dims.append((s_, nums[0], nums[1]))
            biggest = max(max(w_, h_) for _, w_, h_ in dims); px = 1000 / biggest; x = 150
            for lab, w_, h_ in dims:
                ww, hh = int(w_ * px), int(h_ * px)
                if kind == 'poster': ww, hh = min(ww, hh), max(ww, hh)
                box = Image.new('RGBA', (ww, hh), (253, 252, 249, 255)); a = fit(trimmed(art), ww * 0.86, hh * 0.86)
                box.alpha_composite(a, ((ww - a.width) // 2, (hh - a.height) // 2))
                shadow(im, box, (x, 1560 - hh), blur=18, off=(0, 10), op=60)
                d.text((x, 1600), lab.replace('″', '"'), font=F('med', 44), fill=INK); x += ww + 120
        else:
            d.text((150, 250), '11 oz ceramic mug', font=F('serif', 96), fill=INK)
            y = 520
            for f_ in MUG_FACTS:
                d.ellipse((150, y + 18, 178, y + 46), fill=acc); d.text((210, y), f_, font=F('sans', 56), fill=INK); y += 110
            m = fit(product_mock(kind, product, art), 1100, 1100); im.paste(m, (1250, 520), m)
    save(im, 5, 'options')
    # 06 size chart / specs
    im = canvas(); d = ImageDraw.Draw(im)
    if kind in ('tee', 'sweatshirt'):
        sz = [s_ for s_ in sizes_of(product) if s_ in SIZE_CHART[kind]]
        kicker(d, 'Size chart', acc); d.text((150, 250), GARMENT[kind], font=F('serif', 84), fill=INK)
        d.text((150, 380), 'Unisex fit. Flat measurements in inches; they can vary slightly.', font=F('sans', 44), fill=MUTED)
        x0, y0, cw, rh = 150, 560, (W - 300) // (len(sz) + 1), 170
        rows = [('Size', sz), ('Width', [str(SIZE_CHART[kind][s_][0]) for s_ in sz]), ('Length', [str(SIZE_CHART[kind][s_][1]) for s_ in sz])]
        for r, (lab, vals) in enumerate(rows):
            y = y0 + r * rh
            if r == 0: d.rectangle((x0, y, W - 150, y + rh), fill=mix(acc, 0.85))
            d.text((x0 + 30, y + 52), lab, font=F('bold', 54), fill=INK)
            for i, v in enumerate(vals):
                tw = d.textlength(v, font=F('med', 60)); d.text((x0 + cw * (i + 1) + cw / 2 - tw / 2, y + 50), v, font=F('med', 60), fill=INK)
            d.line((x0, y + rh, W - 150, y + rh), fill=(220, 214, 205), width=3)
        d.text((150, y0 + 3 * rh + 80), 'Width: armpit to armpit. Length: top of the shoulder to the hem. Tip: lay a shirt you like flat and compare.',
               font=F('sans', 42), fill=MUTED)
    else:
        kicker(d, 'Good to know', acc); d.text((150, 250), 'What you get', font=F('serif', 96), fill=INK)
        lines = {'mug': ['One 11 oz white ceramic mug', 'The design on both sides' if 'both' in P.PRODUCTS['mug']['details'] and len(product['print_areas'][0]['placeholders'][0]['images']) > 1 else 'The pattern all the way around', 'Printed to order and packed for shipping'],
                 'accent_mug': ['One ceramic mug with a colored handle, rim and inside', 'Your choice of 11 oz or 15 oz', 'Printed to order and packed for shipping'],
                 'sticker': ['One kiss-cut vinyl sticker on its white backing', 'Your choice of size: ' + ', '.join(s_.replace('″', '"') for s_ in sizes_of(product)), 'Best indoors: the vinyl isn\'t waterproof'],
                 'poster': ['One matte art print on museum-grade paper', 'Sizes: ' + ', '.join(s_.replace('″', '"') for s_ in sizes_of(product)), 'Frame not included']}[kind]
        y = 520
        for ln in lines:
            d.ellipse((150, y + 18, 178, y + 46), fill=acc); y = text(d, (210, y), ln, F('sans', 58), INK, 1300) + 50
    save(im, 6, 'size' if kind in ('tee', 'sweatshirt') else 'specs')
    # 07 details & care (text from printify.py)
    im = canvas(); d = ImageDraw.Draw(im); key = {'mug': 'mug' if len(product['print_areas'][0]['placeholders'][0]['images']) > 1 else 'mug_wrap'}.get(kind, kind)
    kicker(d, 'Details & care', acc); d.text((150, 250), 'Made to last', font=F('serif', 96), fill=INK)
    y = 500
    for ln in P.PRODUCTS[key]['details'].split('\n'):
        ln = ln.lstrip('- ').replace('; see the size chart photo before ordering', '')
        if 'water bottles' in ln: ln = 'Great for laptops, notebooks and planners'
        d.ellipse((150, y + 18, 178, y + 46), fill=acc); y = text(d, (210, y), ln, F('sans', 54), INK, 1900) + 36
    d.rounded_rectangle((150, y + 40, W - 150, y + 300), 30, fill=mix(acc, 0.9))
    d.text((200, y + 80), 'CARE', font=F('bold', 40), fill=acc); text(d, (200, y + 140), P.PRODUCTS[key]['care'], F('sans', 52), INK, W - 400)
    save(im, 7, 'details')
    # 08 collection
    im = canvas(); d = ImageDraw.Draw(im)
    kicker(d, 'The collection', acc); d.text((150, 250), f'Also in {name}', font=F('serif', 96), fill=INK)
    sibs = sorted(group, key=lambda p: list(KIND).index(p['blueprint_id']))
    n = len(sibs); cw = min(700, (W - 300 - 50 * (n - 1)) // n)
    for i, sp in enumerate(sibs):
        k2 = KIND[sp['blueprint_id']]; c2 = colors_of(sp)
        m = fit(product_mock(k2, sp, fetch(sp['print_areas'][0]['placeholders'][0]['images'][0]['src'], art_cache), c2[0][1] if c2 else None), cw, cw)
        x = 150 + i * (cw + 50); im.paste(m.convert('RGB') if m.mode != 'RGBA' else m, (x + (cw - m.width) // 2, 560 + (cw - m.height) // 2), m if m.mode == 'RGBA' else None)
        lab = NOUN[k2]; tw = d.textlength(lab, font=F('med', 46))
        d.text((x + cw / 2 - tw / 2, 600 + cw), lab, font=F('med', 46), fill=INK if sp['id'] != product['id'] else acc)
    save(im, 8, 'collection')
    # 09 made to order + who it's for
    im = canvas(acc); d = ImageDraw.Draw(im)
    kicker(d, 'Printed just for you', acc); text(d, (150, 250), 'Made to order', F('serif', 110), INK, 900)
    y = 480
    for i, s_ in enumerate(['You place your order', 'Our production partner prints it for you', 'It ships to your door']):
        d.ellipse((150, y, 250, y + 100), fill=acc); n_ = str(i + 1); tw = d.textlength(n_, font=F('bold', 56))
        d.text((200 - tw / 2, y + 16), n_, font=F('bold', 56), fill=(255, 255, 255)); text(d, (290, y + 20), s_, F('sans', 54), INK, 680); y += 190
    text(d, (150, y + 60), 'Questions? Message us on Etsy.', F('sans', 48), MUTED, 800)
    text(d, (int(W * 0.47), 380), 'A gift for', F('bold', 46), acc, 1100)
    text(d, (int(W * 0.47), 460), FOR_WHO[did] + '.', F('serif_it', 92), INK, 1100, 1.2)
    m = fit(product_mock(kind, product, art, first), 800, 800)
    shadow(im, m, (int(W * 0.47), H - m.height - 120))
    save(im, 9, 'made-to-order')
    return files


def contact_sheet(files, path):
    th = [Image.open(f).resize((600, 450)) for f in files]
    sh = Image.new('RGB', (600 * 3, 450 * math.ceil(len(th) / 3)), 'white')
    for i, t in enumerate(th): sh.paste(t, ((i % 3) * 600, (i // 3) * 450))
    sh.save(path)


def main():
    out = sys.argv[1]; only = sys.argv[sys.argv.index('--only') + 1:] if '--only' in sys.argv else None
    prods = []
    for page in (1, 2, 3):
        r = P.call('GET', f'/shops/{SHOP}/products.json?limit=50&page={page}'); prods += r['data']
        if page >= r.get('last_page', 1): break
    groups = {}
    for p in prods:
        did = next((v for k, v in DESIGN_KEYS if k in p['title']), None)
        if did and p['blueprint_id'] in KIND: groups.setdefault(did, []).append(p)
    cache = os.path.join(out, '_art'); os.makedirs(cache, exist_ok=True)
    rows = []
    for did, group in groups.items():
        for p in group:
            if only and p['id'] not in only: continue
            have = len([i for i in p['images'] if i.get('is_selected_for_publishing')])
            if '--skip-full' in sys.argv and have >= 9: continue
            slug = f"{did}--{KIND[p['blueprint_id']]}"
            files = make_set(p, group, cache, os.path.join(out, slug))
            contact_sheet(files, os.path.join(out, slug, '00-sheet.png'))
            ext = p.get('external') or {}
            rows.append({'slug': slug, 'product_id': p['id'], 'title': p['title'], 'printify_photos': have, 'new_photos': len(files),
                         'total': have + len(files), 'etsy_listing_id': ext.get('id'), 'etsy_url': ext.get('handle')})
            print(slug, have, '+', len(files), flush=True)
    json.dump(rows, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
