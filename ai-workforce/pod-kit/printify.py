#!/usr/bin/env python3
"""Create a Printify product from a built design and (optionally) publish it
to the owner's connected Etsy shop.

usage: printify.py designs/<id>.json BUILD_DIR [--publish] [--price 2600]

The Printify key never appears here: it is stored as an API credential on
the cloud environment and attached to requests to api.printify.com by the
environment's proxy.

Spending rule (owner, 2026-09-28): Etsy charges $0.20 per published listing.
Agents may publish up to $3.00 of listing fees per day (15 listings). Before
publishing, count today's `pod_listings` docs in the Office DB with
`published: true`; if 15 or more, create the product unpublished instead.
This script prints what it did as JSON so the caller can write that doc.
"""
import base64, io, json, os, sys, time, urllib.request
from PIL import Image

API = 'https://api.printify.com/v1'
BLUEPRINT = 12            # Bella+Canvas 3001 Unisex Jersey Short Sleeve Tee
PROVIDER = 29             # Monster Digital (US)
SIZES = ['S', 'M', 'L', 'XL', '2XL']
COLOR_MAP = {'white': 'White', 'natural': 'Natural', 'heather_pink': 'Soft Pink', 'sand': 'Soft Cream',
             'sage': 'Heather Mint', 'light_blue': 'Light Blue', 'ivory': 'Soft Cream', 'heather_gray': 'Athletic Heather'}
HERE = os.path.dirname(os.path.abspath(__file__))


def call(method, path, body=None, tries=3):
    data = json.dumps(body).encode() if body is not None else None
    for k in range(tries):
        req = urllib.request.Request(API + path, data=data, method=method,
                                     headers={'Content-Type': 'application/json', 'User-Agent': 'edgex-pod-desk'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt.strip() else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:600]
            if e.code >= 500 and k < tries - 1:
                time.sleep(3 * (k + 1)); continue
            raise SystemExit(f'Printify {method} {path} -> HTTP {e.code}: {msg}')


def shop_id():
    shops = call('GET', '/shops.json')
    etsy = [s for s in shops if s.get('sales_channel') == 'etsy']
    if not etsy:
        raise SystemExit('No Etsy-connected Printify shop: ' + json.dumps(shops))
    return etsy[0]['id']


def print_file(build_dir, sid, area=(3319, 3761)):
    """Crop the transparent design to its artwork and fit it to the print area."""
    im = Image.open(os.path.join(build_dir, f'{sid}.png')).convert('RGBA')
    box = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    pad = int(0.02 * im.width)
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
    art = im.crop(box)
    r = min(area[0] / art.width, area[1] / art.height)
    if r < 1:
        art = art.resize((int(art.width * r), int(art.height * r)), Image.LANCZOS)
    buf = io.BytesIO(); art.save(buf, 'PNG', optimize=True)
    return art.size, buf.getvalue()


def main():
    spec = json.load(open(sys.argv[1])); build_dir = sys.argv[2]
    publish = '--publish' in sys.argv
    price = int(sys.argv[sys.argv.index('--price') + 1]) if '--price' in sys.argv else 2600
    sid, L = spec['id'], spec['listing']
    shop = shop_id()
    # variants for the chosen colors and sizes
    vs = call('GET', f'/catalog/blueprints/{BLUEPRINT}/print_providers/{PROVIDER}/variants.json')['variants']
    want = [COLOR_MAP[c] for c in spec.get('shirt_colors', ['white', 'natural']) if c in COLOR_MAP]
    want = list(dict.fromkeys(want))[:4]
    chosen = [v for v in vs if v['options']['color'] in want and v['options']['size'] in SIZES]
    if not chosen:
        raise SystemExit('no variants matched ' + str(want))
    ph = next(p for p in chosen[0]['placeholders'] if p['position'] == 'front')
    (aw, ah), png = print_file(build_dir, sid, (ph['width'], ph['height']))
    up = call('POST', '/uploads/images.json', {'file_name': f'{sid}.png', 'contents': base64.b64encode(png).decode()})
    # scale = image width / print-area width; keep it inside the area with an even margin
    scale = round(min(0.92, 0.92 * (ph['height'] / ph['width']) * (aw / ah)), 3)
    desc = L['description'].strip() + open(os.path.join(HERE, 'standard_description.txt')).read()
    body = {
        'title': L['title'], 'description': desc, 'tags': L['tags'],
        'blueprint_id': BLUEPRINT, 'print_provider_id': PROVIDER,
        'variants': [{'id': v['id'], 'price': price + (200 if v['options']['size'] == '2XL' else 0), 'is_enabled': True}
                     for v in chosen],
        'print_areas': [{'variant_ids': [v['id'] for v in chosen],
                         'placeholders': [{'position': 'front', 'images': [
                             {'id': up['id'], 'x': 0.5, 'y': 0.5, 'scale': scale, 'angle': 0}]}]}],
    }
    prod = call('POST', f'/shops/{shop}/products.json', body)
    costs = sorted({(v.get('cost'), v.get('title')) for v in prod.get('variants', []) if v.get('is_enabled')}, key=lambda x: x[0] or 0)
    out = {'design': sid, 'shop_id': shop, 'product_id': prod['id'], 'image_id': up['id'], 'colors': want,
           'sizes': SIZES, 'price_cents': price, 'scale': scale,
           'cost_cents_range': [costs[0][0], costs[-1][0]] if costs else None, 'published': False}
    if publish:
        call('POST', f'/shops/{shop}/products/{prod["id"]}/publish.json',
             {'title': True, 'description': True, 'images': True, 'variants': True, 'tags': True,
              'keyFeatures': True, 'shipping_template': True})
        out['published'] = True
        out['listing_fee_usd'] = 0.20
    print(json.dumps(out))


if __name__ == '__main__':
    main()
