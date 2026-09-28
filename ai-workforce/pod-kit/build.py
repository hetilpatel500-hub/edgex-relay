#!/usr/bin/env python3
"""Build a finished print-on-demand design: print file, mockups, listing, and
a delivery page the owner opens to download and copy everything.

usage: build.py designs/<id>.json OUT_DIR [--preview]

The spec's "listing" section:
  "listing": {
    "title": "...",                     # <= 140 characters
    "tags": [13 phrases, each <= 20 characters],
    "description": "...",               # the product-specific opening; the
                                         # standard printing/care/production
                                         # partner text is appended here
    "products": ["Unisex tee (Bella+Canvas 3001)", "Crewneck sweatshirt (Gildan 18000)"],
    "price_note": "suggested range + source",
    "trademark_check": "what was searched and what was found"
  }
Checks refuse the build when a rule is broken (title length, tag count and
length, risky words, missing trademark note).
"""
import html, json, os, re, subprocess, sys
import design as D

HERE = os.path.dirname(os.path.abspath(__file__))
# Words that invite trademark or policy trouble on Etsy print-on-demand.
# This is a floor, not a clearance: every phrase still gets a trademark search.
RISKY = re.compile(r"\b(disney|pixar|marvel|star wars|harry potter|hogwarts|taylor swift|swiftie|eras tour|barbie|"
                   r"nike|adidas|stanley|starbucks|coca.?cola|nfl|nba|mlb|nhl|super bowl|olympic|pokemon|hello kitty|"
                   r"sanrio|peanuts|snoopy|bluey|paw patrol|sesame street|minecraft|fortnite|lego|crocs|yeti|"
                   r"best ?seller|free shipping|#1)\b", re.I)
STANDARD_DESC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'standard_description.txt')).read()


def check(listing):
    errs = []
    t = listing.get('title', '')
    if not t or len(t) > 140:
        errs.append(f'title must be 1-140 characters (is {len(t)})')
    tags = listing.get('tags', [])
    if len(tags) != 13:
        errs.append(f'need exactly 13 tags (have {len(tags)})')
    for tg in tags:
        if len(tg) > 20:
            errs.append(f'tag over 20 characters: {tg!r}')
    if len({x.lower() for x in tags}) != len(tags):
        errs.append('duplicate tags')
    for field in [t, listing.get('description', '')] + tags:
        m = RISKY.search(field or '')
        if m:
            errs.append(f'risky word {m.group(0)!r} in {field[:60]!r}')
    if not listing.get('trademark_check'):
        errs.append('trademark_check note is required (what was searched, what was found)')
    return errs


def page(spec, out, files):
    L = spec['listing']
    desc = L['description'].strip() + STANDARD_DESC
    sid = spec['id']
    def copy(label, text, rows=3):
        return (f'<div class="cp"><div class="lb">{html.escape(label)}<button type="button" data-copy>Copy</button></div>'
                f'<textarea rows="{rows}" readonly>{html.escape(text)}</textarea></div>')
    imgs = ''.join(f'<figure><img src="{f}" alt="{html.escape(f)}"><figcaption>{html.escape(f)}</figcaption></figure>'
                   for f in files if f.endswith('.jpg'))
    body = f'''<title>{html.escape(spec.get('name') or spec.get('top', 'Design'))} Tee</title>
<style>
:root{{--bg:#f6f3ee;--ink:#2d2a2e;--mut:#6d6670;--line:#ddd6cc;--card:#fffdf9;--acc:#a1506b}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1c1a1d;--ink:#efeae4;--mut:#a9a1ab;--line:#3a353b;--card:#252226;--acc:#e59ab3;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#1c1a1d;--ink:#efeae4;--mut:#a9a1ab;--line:#3a353b;--card:#252226;--acc:#e59ab3;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif;padding-inline:16px;padding-block:24px 48px}}
main{{max-width:980px;margin:0 auto;display:grid;gap:20px}}
h1{{font:600 30px/1.2 Georgia,serif;margin:0;text-wrap:balance}} h2{{font:600 18px/1.3 Georgia,serif;margin:0 0 8px}}
.mut{{color:var(--mut)}} .card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
figure{{margin:0}} figure img{{width:100%;border-radius:8px;border:1px solid var(--line);display:block}} figcaption{{font-size:12px;color:var(--mut);margin-top:4px;overflow-wrap:anywhere}}
.cp{{display:grid;gap:4px;margin-top:10px}} .lb{{display:flex;justify-content:space-between;align-items:center;font-weight:600;font-size:13px}}
textarea{{width:100%;box-sizing:border-box;border:1px solid var(--line);border-radius:8px;padding:8px;background:var(--bg);color:var(--ink);font:13px/1.5 ui-monospace,monospace;resize:vertical}}
button{{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:4px 12px;font:600 12px system-ui;cursor:pointer}}
.dl{{display:flex;flex-wrap:wrap;gap:8px}} .dl button{{border-color:var(--acc);color:var(--acc)}}
ol{{margin:0;padding-left:20px}} li{{margin:4px 0}}
</style>
<main>
<div><div class="mut">Edgex print-on-demand desk</div><h1>{html.escape(L['title'])}</h1></div>
<div class="card"><h2>Files</h2><p class="mut">The print file is 4500 x 5400 px, transparent, 300 dpi: Printify's front print area for most tees and sweatshirts.</p>
<div class="dl">{''.join(f'<button type="button" data-file="{f}">{html.escape(f)}</button>' for f in files)}</div></div>
<div class="grid">{imgs}</div>
<div class="card"><h2>Listing (copy into Etsy)</h2>
{copy('Title (' + str(len(L['title'])) + '/140)', L['title'], 2)}
{copy('13 tags', ', '.join(L['tags']), 3)}
{copy('Description', desc, 14)}
<p class="mut">Products: {html.escape(', '.join(L.get('products', [])))}. Price: {html.escape(L.get('price_note', ''))}</p>
<p class="mut">Trademark check: {html.escape(L['trademark_check'])}</p></div>
<div class="card"><h2>How to publish (about 10 minutes)</h2><ol>
<li>In Printify, create a product for each item listed above and upload <b>{sid}.png</b> to the front print area. Keep it centred; don't stretch it.</li>
<li>Choose the colors shown in the mockups (the art is made for light shirts).</li>
<li>Publish to your Etsy shop from Printify, then in Etsy paste the title, tags and description above.</li>
<li>In Etsy's listing settings, add Printify as the production partner. If Etsy asks how the design was made, say it was designed by you with digital tools.</li>
<li>Use the mockup images as listing photos, and add Printify's own mockups too.</li></ol></div>
</main>
<script>
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{{const t=b.closest('.cp').querySelector('textarea');
navigator.clipboard.writeText(t.value).then(()=>{{b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1500)}},()=>{{t.select()}})}}));
(async()=>{{let dl=null;try{{dl=window.claude&&await window.claude.use('downloads')}}catch(e){{}}
document.querySelectorAll('[data-file]').forEach(b=>{{if(!dl){{b.disabled=true;b.title='Downloads are not available in this view';return}}
b.addEventListener('click',async()=>{{try{{const r=await fetch(b.dataset.file);await dl.save({{filename:b.dataset.file,data:await r.blob()}})}}catch(e){{}}}})}})}})();
</script>'''
    open(os.path.join(out, 'index.html'), 'w').write(body)


def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path))
    errs = check(spec.get('listing', {}))
    if errs:
        print('REFUSED:\n- ' + '\n- '.join(errs)); sys.exit(1)
    args = [sys.executable, os.path.join(HERE, 'design.py'), spec_path, out] + (['--preview'] if '--preview' in sys.argv else [])
    subprocess.check_call(args)
    sid = spec['id']
    files = sorted(f for f in os.listdir(out) if f.startswith(sid) and not f.endswith('-preview.jpg'))
    json.dump(spec['listing'], open(os.path.join(out, f'{sid}-listing.json'), 'w'), indent=1)
    files.append(f'{sid}-listing.json')
    page(spec, out, files)
    print('built', out, files)


if __name__ == '__main__':
    main()
