#!/usr/bin/env python3
"""Delivery page for one built book: previews, Save buttons for the KDP files,
Copy buttons for every listing field.   usage: page.py OUT_DIR"""
import json, os, sys, html
from PIL import Image

out = sys.argv[1]
L = json.load(open(os.path.join(out, 'listing.json')))

# Chromium rounds PDF page sizes to whole CSS pixels; KDP checks the cover size
# against its formula, so redraw the cover onto a page of the exact size.
import pymupdf
W = (0.125 * 2 + 8.5 * 2 + L['print']['pages'] * 0.002252) * 72
H = (11 + 0.25) * 72
cp = os.path.join(out, 'cover-paperback.pdf')
src = pymupdf.open(cp)
if abs(src[0].rect.width - W) > 0.01 or abs(src[0].rect.height - H) > 0.01:
    dst = pymupdf.open()
    dst.new_page(width=W, height=H).show_pdf_page(pymupdf.Rect(0, 0, W, H), src, 0, keep_proportion=False)
    dst.save(cp + '.tmp', garbage=3, deflate=True)
    src.close(); os.replace(cp + '.tmp', cp)
chk = pymupdf.open(cp)[0].rect
print(f'cover {chk.width / 72:.4f} x {chk.height / 72:.4f} in (KDP formula {W / 72:.4f} x {H / 72:.4f})')
shots = json.load(open(os.path.join(out, '_shots.json')))
# preview strip of the first interior pages
ims = [Image.open(f).convert('RGB') for f in shots]
w, h = ims[0].size
grid = Image.new('RGB', (w * 3 + 40, h * 2 + 30), '#e7edf2')
for k, im in enumerate(ims[:6]):
    grid.paste(im, (10 + (k % 3) * (w + 10), 10 + (k // 3) * (h + 10)))
grid.resize((grid.width * 2 // 3, grid.height * 2 // 3)).save(os.path.join(out, 'preview-pages.png'), optimize=True)
k = Image.open(os.path.join(out, 'cover-kindle.jpg'))
k.resize((k.width // 3, k.height // 3)).save(os.path.join(out, 'preview-cover.jpg'), quality=86)
for f in shots:
    os.remove(f)
os.remove(os.path.join(out, '_shots.json'))

e = html.escape
size = lambda f: f"{os.path.getsize(os.path.join(out, f)) / 1e6:.1f} MB"
P = L['print']
fields = [('Title', L['title']), ('Subtitle', L['subtitle']), ('Series', L['series']), ('Author', L['author']),
          ('Description (paste into KDP as is)', L['description_html'])]
fields += [(f'Keyword {i + 1}', k) for i, k in enumerate(L['keywords'])]
fields += [('Categories', '\n'.join(L['categories'])), ('Reading age', L['reading_age'])]
rows = ''.join(f'<div class="f"><div class="fl">{e(n)}</div><pre id="c{i}">{e(v)}</pre><button data-copy="c{i}">Copy</button><span class="st" role="status"></span></div>'
               for i, (n, v) in enumerate(fields))
files = [('interior.pdf', 'Paperback interior', f"{P['pages']} pages, {P['trim']}, no bleed, white paper"),
         ('cover-paperback.pdf', 'Paperback cover', f"Full wrap {P['cover_in']} in with bleed, spine {P['spine_in']} in, {'no spine text' if P['spine_text'].startswith('none') else 'spine text allowed'}"),
         ('cover-kindle.jpg', 'Kindle eBook cover', '1980 x 2562 px JPG')]
frow = ''.join(f'<div class="file"><div><b>{e(t)}</b><div class="mut">{e(d)}</div></div><button class="save" data-file="{f}">Save · {size(f)}</button><span class="st" role="status"></span></div>' for f, t, d in files)

page = f'''<title>{e(L['title'])}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;700&family=Inter:wght@400;600&display=swap">
<style>
:root{{--bg:#f4f8fb;--panel:#fff;--ink:#1d2a33;--mut:#5d6f7c;--line:#d7e2ea;--acc:#2f8fd8;--acc-ink:#fff;--code:#f1f5f8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{color-scheme:dark;--bg:#0f161b;--panel:#172128;--ink:#e8eef2;--mut:#9fb0bc;--line:#2a3943;--acc:#5ab0f0;--acc-ink:#07131c;--code:#111a20}}}}
:root[data-theme="dark"]{{color-scheme:dark;--bg:#0f161b;--panel:#172128;--ink:#e8eef2;--mut:#9fb0bc;--line:#2a3943;--acc:#5ab0f0;--acc-ink:#07131c;--code:#111a20}}
*{{box-sizing:border-box}}body{{background:var(--bg);color:var(--ink);font:15px/1.55 Inter,system-ui,sans-serif;margin:0;padding-inline:16px;padding-block:24px 56px}}
.wrap{{max-width:1080px;margin:0 auto;display:grid;gap:26px}}
h1{{font:700 clamp(26px,4.5vw,40px)/1.1 Fredoka,system-ui,sans-serif;margin:0;text-wrap:balance}}h2{{font:700 20px Fredoka,system-ui,sans-serif;margin:0 0 10px}}
.lede{{color:var(--mut);margin:6px 0 0;max-width:70ch}}
.top{{display:grid;grid-template-columns:minmax(0,300px) 1fr;gap:22px;align-items:start}}@media (max-width:640px){{.top{{grid-template-columns:1fr}}}}
img{{max-width:100%;border-radius:10px;border:1px solid var(--line);display:block}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}}
.file,.f{{display:grid;grid-template-columns:1fr auto;gap:6px 12px;align-items:center;padding:10px 0;border-top:1px solid var(--line)}}.file:first-of-type,.f:first-of-type{{border-top:0}}
.f{{grid-template-columns:1fr auto}}.fl{{grid-column:1/-1;font-weight:600;font-size:13px;color:var(--mut)}}
pre{{margin:0;background:var(--code);border-radius:8px;padding:9px 11px;white-space:pre-wrap;overflow-wrap:anywhere;font:13.5px/1.5 Inter,system-ui,sans-serif;max-height:220px;overflow:auto}}
.mut{{color:var(--mut);font-size:13px}}.st{{grid-column:1/-1;font-size:12.5px;color:var(--mut);min-height:0}}
button{{font:600 14px Inter,system-ui,sans-serif;border-radius:9px;padding:8px 13px;cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--ink)}}
button.save{{background:var(--acc);color:var(--acc-ink);border-color:var(--acc)}}button:focus-visible{{outline:3px solid var(--acc);outline-offset:2px}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;margin:0}}dt{{color:var(--mut)}}dd{{margin:0}}
ol{{margin:0;padding-left:20px;display:grid;gap:4px}}
</style>
<div class="wrap">
 <header><div class="mut">EDGEX BOOKS · {e(L['series'])}</div><h1>{e(L['title'])}</h1><p class="lede">{e(L['subtitle'])}. Written, drawn and checked by the Edgex book desk. Nothing has been published: you upload it to KDP.</p></header>
 <div class="top"><img src="preview-cover.jpg" alt="Front cover"><div class="card"><h2>KDP files</h2>{frow}</div></div>
 <div class="card"><h2>Inside the book</h2><img src="preview-pages.png" alt="Title page and the first five coloring pages"></div>
 <div class="card"><h2>Listing: copy into KDP</h2>{rows}</div>
 <div class="card"><h2>Print settings</h2><dl><dt>Trim size</dt><dd>{e(P['trim'])}</dd><dt>Interior</dt><dd>Black &amp; white, white paper, {e(P['bleed'])}</dd><dt>Pages</dt><dd>{P['pages']}</dd><dt>Cover finish</dt><dd>Glossy suits kids' books</dd><dt>Price</dt><dd>{e(L['price_note'])}</dd><dt>AI disclosure</dt><dd>{e(L['ai_disclosure'])}</dd></dl></div>
 <div class="card"><h2>Upload in KDP</h2><ol><li>Create a new Paperback and fill in the details with the Copy buttons above (add it to the <b>{e(L['series'])}</b> series).</li><li>Content: choose 8.5 x 11 in, No bleed, Black &amp; white interior with white paper. Upload interior.pdf, then "Upload a cover you already have" with cover-paperback.pdf.</li><li>Check the previewer, set your price, publish.</li><li>For the Kindle edition, use cover-kindle.jpg as the cover.</li></ol></div>
</div>
<script>
function st(b){{return b.parentElement.querySelector('.st')}}
document.querySelectorAll('button[data-copy]').forEach(b=>b.addEventListener('click',async()=>{{const el=document.getElementById(b.dataset.copy);try{{await navigator.clipboard.writeText(el.textContent);st(b).textContent='Copied'}}catch(e){{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);st(b).textContent='Selected. Press Ctrl+C or ⌘C to copy'}}}}));
let dlP=null;function dls(){{if(!dlP)dlP=(window.claude&&window.claude.use)?window.claude.use('downloads').catch(()=>null):Promise.resolve(null);return dlP}}
document.querySelectorAll('button.save').forEach(b=>b.addEventListener('click',async()=>{{const s=st(b);b.disabled=true;s.textContent='Preparing file…';try{{const d=await dls();if(!d){{s.textContent='Saving is not available in this view. Open the page on claude.ai to save.';return}}const blob=await(await fetch(b.dataset.file)).blob();await d.save({{filename:b.dataset.file,data:blob}});s.textContent='Saved'}}catch(e){{const c=e&&e.code;s.textContent=c==='declined'?'Save cancelled':c==='rate_limited'?'Another save is open. Try again in a moment.':'Could not save here. Open the page on claude.ai and try again.'}}finally{{b.disabled=false}}}}));
</script>
'''
open(os.path.join(out, 'index.html'), 'w').write(page)
print('page written', os.path.join(out, 'index.html'))
