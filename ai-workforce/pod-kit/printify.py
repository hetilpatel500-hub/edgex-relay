#!/usr/bin/env python3
"""Create Printify products from a built design and (optionally) publish them
to the owner's connected Etsy shop.

usage: printify.py designs/<id>.json BUILD_DIR [--products tee,sweatshirt,mug,poster,sticker]
                   (pattern designs: --products mug_wrap,accent_mug)
                   [--publish]

One Etsy listing per product type. Each type has its own blueprint, printer,
colors/sizes, artwork placement, price and listing wording (PRODUCTS below).

The Printify key never appears here: it is an API credential on the cloud
environment, attached to requests to api.printify.com by the proxy.

Spending rule (owner, 2026-09-28): Etsy charges $0.20 per published listing.
Agents may publish up to $3.00 of listing fees per day (15 listings). Before
publishing, count today's `pod_listings` docs with `published: true`; only
pass --publish for as many products as the cap still allows.
"""
import base64, io, json, math, os, re, sys, time, urllib.request
from PIL import Image

API = 'https://api.printify.com/v1'
HERE = os.path.dirname(os.path.abspath(__file__))

# art: 'clear' = transparent watercolor (cropped to the artwork), 'paper' = the painting on cream paper
# fit: how the art sits in the print area; price in cents per variant (by size label, else 'default')
PRODUCTS = {
    'tee': dict(blueprint=12, provider=29, noun='Shirt', alt='Tee', art='clear', fit=('contain', 0.92, 0.5),
                colors_from_spec=True, color_map={'white': 'White', 'natural': 'Natural', 'heather_pink': 'Soft Pink',
                'sand': 'Soft Cream', 'sage': 'Heather Mint', 'light_blue': 'Light Blue'},
                sizes=['S', 'M', 'L', 'XL', '2XL'], price={'default': 2600, '2XL': 2800},
                details="- Bella+Canvas 3001 unisex tee: soft, lightweight cotton\n- Printed with water-based inks directly into the fabric (direct-to-garment)\n- Unisex fit; see the size chart photo before ordering",
                care="Wash inside out in cold water, tumble dry low or hang dry, don't iron the print."),
    'sweatshirt': dict(blueprint=49, provider=29, noun='Sweatshirt', alt='Crewneck', art='clear', fit=('contain', 0.8, 0.45),
                colors_from_spec=True, color_map={'white': 'White', 'natural': 'Sand', 'heather_pink': 'Light Pink',
                'sand': 'Sand', 'sage': 'Ash', 'light_blue': 'Light Blue'},
                sizes=['S', 'M', 'L', 'XL', '2XL'], price={'default': 4200, '2XL': 4500},
                details="- Gildan 18000 unisex heavy blend crewneck: cozy cotton-poly fleece\n- Printed with water-based inks directly into the fabric (direct-to-garment)\n- Unisex fit; see the size chart photo before ordering",
                care="Wash inside out in cold water, tumble dry low, don't iron the print."),
    'mug': dict(blueprint=68, provider=1, noun='Mug', alt='Coffee Mug', art='clear', fit=('both_sides', 0.9, 0.5),
                price={'default': 1800},
                details="- 11 oz white ceramic mug with a glossy finish\n- The design is printed on both sides\n- Microwave and dishwasher safe",
                care="Dishwasher safe; hand washing keeps the print bright longest."),
    # Full-wrap products take an all-over pattern design ("kind": "pattern", see pattern.py):
    # the art is painted at each print area's exact size, seamless around the handle.
    'mug_wrap': dict(blueprint=68, provider=1, noun='Mug', alt='Coffee Mug', art='wrap', fit=('exact', 1.0, 0.5),
                price={'default': 1800},
                details="- 11 oz white ceramic mug with a glossy finish\n- The watercolor pattern wraps all the way around\n- Microwave and dishwasher safe",
                care="Dishwasher safe; hand washing keeps the print bright longest."),
    'accent_mug': dict(blueprint=635, provider=99, noun='Mug', alt='Accent Coffee Mug', art='wrap', fit=('exact', 1.0, 0.5),
                colors_from_mug=True, sizes=['11oz', '15oz'], price={'11oz': 2200, '15oz': 2500},
                details="- Ceramic accent mug: the handle, rim and inside are colored (your choice of color)\n- 11 oz or 15 oz\n- The watercolor pattern wraps around the mug\n- Microwave and dishwasher safe",
                care="Dishwasher safe; hand washing keeps the print bright longest."),
    # Tote: not in the lineup. This organic tote costs $20.72 from Printify (2026-09-28), too
    # little margin at a market price; find a cheaper tote blueprint before using it.
    'tote': dict(blueprint=609, provider=74, noun='Tote Bag', alt='Canvas Tote', art='clear', fit=('contain', 0.9, 0.5),
                colors=['Natural'], price={'default': 2400},
                details="- Organic cotton canvas tote in natural\n- Printed on the front\n- Sturdy handles for books, groceries and market days",
                care="Spot clean, or wash cold and hang dry."),
    'poster': dict(blueprint=282, provider=2, noun='Art Print', alt='Wall Art Poster', art='paper', fit=('cover', 1.0, 0.5),
                sizes=['11″ x 14″', '16″ x 20″', '18″ x 24″'],
                price={'11″ x 14″': 2200, '16″ x 20″': 3000, '18″ x 24″': 3600},
                details="- Museum-quality matte poster paper\n- The watercolor painting printed edge to edge\n- Frame not included",
                care="Keep out of direct sunlight to protect the colors."),
    'sticker': dict(blueprint=400, provider=1, noun='Sticker', alt='Vinyl Sticker', art='clear', fit=('contain', 0.92, 0.5),
                surfaces=['White'], sizes=['3" × 3"', '4" × 4"'], price={'3" × 3"': 599, '4" × 4"': 699},
                details="- Kiss-cut vinyl sticker with a white backing\n- Durable and easy to peel\n- Great for laptops, water bottles and journals",
                care="Apply to a clean, dry, smooth surface."),
}
MIN_MARGIN_CENTS = 400     # never list below Printify cost + $4 (Etsy fees come out of the rest)


def call(method, path, body=None, tries=5):
    data = json.dumps(body).encode() if body is not None else None
    for k in range(tries):
        req = urllib.request.Request(API + path, data=data, method=method,
                                     headers={'Content-Type': 'application/json', 'User-Agent': 'edgex-pod-desk'})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt.strip() else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:800]
            if (e.code >= 500 or e.code == 429) and k < tries - 1:
                wait = int(e.headers.get('Retry-After') or 0) or 20 * (k + 1)
                time.sleep(min(wait, 90)); continue
            raise SystemExit(f'Printify {method} {path} -> HTTP {e.code}: {msg}')


def shop_id():
    etsy = [s for s in call('GET', '/shops.json') if s.get('sales_channel') == 'etsy']
    if not etsy:
        raise SystemExit('No Etsy-connected Printify shop')
    return etsy[0]['id']


def artwork(build_dir, sid, kind, max_px=4500):
    """PNG bytes and aspect (w/h) of the art to upload."""
    if kind == 'paper':
        im = Image.open(os.path.join(build_dir, f'{sid}-paper.jpg')).convert('RGB')
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=93)
        return buf.getvalue(), im.width / im.height, 'jpg'
    im = Image.open(os.path.join(build_dir, f'{sid}.png')).convert('RGBA')
    box = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    pad = int(0.02 * im.width)
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
    art = im.crop(box)
    r = min(1.0, max_px / max(art.size))
    if r < 1:
        art = art.resize((int(art.width * r), int(art.height * r)), Image.LANCZOS)
    buf = io.BytesIO(); art.save(buf, 'PNG', optimize=True)
    return buf.getvalue(), art.width / art.height, 'png'


def placements(fit, aspect, W, H, image_id):
    """Printify placement: scale = image width / print-area width."""
    mode, frac, y = fit
    q = W / H
    if mode == 'cover':
        s = max(1.0, aspect / q)
        return [{'id': image_id, 'x': 0.5, 'y': 0.5, 'scale': round(s, 4), 'angle': 0}]
    if mode == 'both_sides':      # mug wrap: one copy on each side of the handle
        s = frac * aspect / q
        s = min(s, 0.45)
        return [{'id': image_id, 'x': x, 'y': y, 'scale': round(s, 4), 'angle': 0} for x in (0.25, 0.75)]
    s = min(frac, frac * aspect / q)
    return [{'id': image_id, 'x': 0.5, 'y': y, 'scale': round(s, 4), 'angle': 0}]


def product_listing(L, spec, key, P):
    """Adapt the tee listing to this product: title, 13 tags (<= 20 chars), description."""
    noun, alt = P['noun'], P['alt']
    L = dict(L, **(L.get('per_product') or {}).get(key, {}))   # optional per-product title/tags/description
    title = L['title']
    title = re.sub(r'\bT-Shirts?\b|\bTshirts?\b', noun, title, flags=re.I)
    title = re.sub(r'\bShirts?\b', noun, title, flags=re.I)
    title = re.sub(r'\bTees?\b', alt, title, flags=re.I)
    title = re.sub(r'\bTops?\b', noun, title)
    if noun.lower() not in title.lower():
        title = f"{spec.get('name', '')} {noun}, " + title
    if len(title) > 140:
        cut = title[:141].rfind(', ')
        title = title[:cut] if cut > 60 else title[:140].rsplit(' ', 1)[0]
    title = title.rstrip(', ')
    tags = []
    for t in L['tags']:
        t2 = re.sub(r'\bt-?shirts?\b|\btshirt\b|\bshirts?\b|\btees?\b', noun.lower(), t, flags=re.I)
        if len(t2) <= 20 and t2.lower() not in [x.lower() for x in tags]:
            tags.append(t2)
    extra = [f"{spec.get('name', '').lower()} {noun.lower()}", f"watercolor {noun.lower()}", f"{noun.lower()} gift",
             f"cute {noun.lower()}", f"floral {noun.lower()}", f"{alt.lower()}"]
    for t in extra:
        if len(tags) >= 13:
            break
        if 0 < len(t) <= 20 and t.lower() not in [x.lower() for x in tags]:
            tags.append(t)
    tags = tags[:13]
    lead = re.sub(r'\bshirt\b|\btee\b', noun.lower(), L['description'].strip(), flags=re.I)
    desc = (lead + "\n\nHOW IT'S MADE\nThe artwork is digitally painted by our studio with its own watercolor-painting code "
            "(no stock art, no copied designs). Each item is made on demand and shipped by our production partner, so it's made just for you."
            "\n\nDETAILS\n" + P['details'] + "\n- Colors can look slightly different on screens\n\nCARE\n" + P['care'] +
            "\n\nBecause each item is made to order, please double-check your choices before checking out.")
    return title, tags, desc


def pick_variants(vs, spec, P):
    out = []
    colors = P.get('colors')
    if P.get('colors_from_mug'):
        colors = [c for c in spec.get('mug_colors', []) if c != 'White']
    if P.get('colors_from_spec'):
        colors = list(dict.fromkeys(P['color_map'][c] for c in spec.get('shirt_colors', ['white']) if c in P['color_map']))[:4]
    for v in vs:
        o = v['options']
        if colors and o.get('color') not in colors:
            continue
        if P.get('sizes') and o.get('size') not in P['sizes']:
            continue
        if P.get('surfaces') and o.get('surface') not in P['surfaces']:
            continue
        if o.get('paper') and o.get('paper') != 'Matte':
            continue
        out.append(v)
    return out


def make(spec, build_dir, key, shop, publish):
    P = PRODUCTS[key]
    sid, L = spec['id'], spec['listing']
    cache = os.path.join('/tmp', f"printify-variants-{P['blueprint']}-{P['provider']}.json")
    if os.path.exists(cache) and time.time() - os.path.getmtime(cache) < 86400:
        vs = json.load(open(cache))
    else:
        vs = call('GET', f"/catalog/blueprints/{P['blueprint']}/print_providers/{P['provider']}/variants.json")['variants']
        json.dump(vs, open(cache, 'w'))
    chosen = pick_variants(vs, spec, P)
    if not chosen:
        raise SystemExit(f'{key}: no variants matched')
    # group variants by print-area shape so each group gets the right scale
    groups = {}
    for v in chosen:
        ph = next(p for p in v['placeholders'] if p['position'] == 'front')
        groups.setdefault((ph['width'], ph['height']), []).append(v['id'])
    print_areas = []
    if P['art'] == 'wrap':
        # all-over pattern: painted at each print area's exact size, placed edge to edge
        for (W, H), ids in groups.items():
            f = os.path.join(build_dir, f'{sid}-wrap-{W}x{H}.png')
            if not os.path.exists(f):
                import pattern
                os.makedirs(build_dir, exist_ok=True)
                pattern.paint(spec, W, H).save(f, dpi=(300, 300))
            buf = io.BytesIO(); Image.open(f).save(buf, 'PNG', optimize=True)
            up = call('POST', '/uploads/images.json', {'file_name': f'{sid}-{key}-{W}x{H}.png',
                                                        'contents': base64.b64encode(buf.getvalue()).decode()})
            print_areas.append({'variant_ids': ids, 'placeholders': [{'position': 'front', 'images': [
                {'id': up['id'], 'x': 0.5, 'y': 0.5, 'scale': 1, 'angle': 0}]}]})
    else:
        data, aspect, ext = artwork(build_dir, sid, P['art'])
        up = call('POST', '/uploads/images.json', {'file_name': f'{sid}-{key}.{ext}', 'contents': base64.b64encode(data).decode()})
        print_areas = [{'variant_ids': ids, 'placeholders': [{'position': 'front', 'images': placements(P['fit'], aspect, W, H, up['id'])}]}
                       for (W, H), ids in groups.items()]
    def price_of(v):
        p = P['price']
        return p.get(v['options'].get('size'), p['default'] if 'default' in p else max(p.values()))
    title, tags, desc = product_listing(L, spec, key, P)
    body = {'title': title, 'description': desc, 'tags': tags, 'blueprint_id': P['blueprint'], 'print_provider_id': P['provider'],
            'variants': [{'id': v['id'], 'price': price_of(v), 'is_enabled': True} for v in chosen], 'print_areas': print_areas}
    prod = call('POST', f'/shops/{shop}/products.json', body)
    # make sure every variant clears cost + margin
    fix = []
    for pv in prod.get('variants', []):
        if pv.get('is_enabled') and pv.get('cost') and pv['price'] < pv['cost'] + MIN_MARGIN_CENTS:
            fix.append({'id': pv['id'], 'price': int(math.ceil((pv['cost'] + MIN_MARGIN_CENTS) / 100.0) * 100 - 1), 'is_enabled': True})
    if fix:
        keep = {f['id'] for f in fix}
        allv = [{'id': pv['id'], 'price': pv['price'], 'is_enabled': pv['is_enabled']} for pv in prod['variants'] if pv['id'] not in keep] + fix
        prod = call('PUT', f"/shops/{shop}/products/{prod['id']}.json", {'variants': allv})
    en = [pv for pv in prod['variants'] if pv.get('is_enabled')]
    out = {'design': sid, 'product': key, 'product_id': prod['id'], 'title': title, 'tags': tags,
           'variants': len(en), 'price_cents': sorted({pv['price'] for pv in en}),
           'cost_cents': sorted({pv.get('cost') for pv in en if pv.get('cost')}), 'published': False}
    if publish:
        call('POST', f"/shops/{shop}/products/{prod['id']}/publish.json",
             {'title': True, 'description': True, 'images': True, 'variants': True, 'tags': True, 'keyFeatures': True, 'shipping_template': True})
        out['published'] = True; out['listing_fee_usd'] = 0.20
    return out


def main():
    spec = json.load(open(sys.argv[1])); build_dir = sys.argv[2]
    keys = sys.argv[sys.argv.index('--products') + 1].split(',') if '--products' in sys.argv else ['tee']
    publish = '--publish' in sys.argv
    shop = shop_id()
    for k in keys:
        print(json.dumps(make(spec, build_dir, k, shop, publish)), flush=True)


if __name__ == '__main__':
    main()
