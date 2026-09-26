// Build a KDP coloring book from a book.json.
// usage: node build.js books/<id>.json OUT_DIR
// Writes: interior.pdf (8.5x11, no bleed), cover-paperback.pdf (full wrap with
// bleed and spine), cover-kindle.jpg, preview-*.png, listing.json, and
// index.html (the delivery page with Save and Copy buttons).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const KIT = __dirname;
const [bookFile, outArg] = process.argv.slice(2);
if (!bookFile || !outArg) { console.error('usage: node build.js books/<id>.json OUT_DIR'); process.exit(1); }
const book = JSON.parse(fs.readFileSync(bookFile, 'utf8'));
const out = path.resolve(outArg); fs.mkdirSync(out, { recursive: true });

// ---- KDP numbers (see BOOK-DESK.md for sources) ----
const TRIM_W = 8.5, TRIM_H = 11, BLEED = 0.125, PAPER = 0.002252; // white paper, inches per page
const font = w => fs.readFileSync(path.join(KIT, `fonts/fredoka-latin-${w}-normal.woff2`)).toString('base64');
const FONTS = [400, 600, 700].map(w => `@font-face{font-family:Fredoka;font-weight:${w};src:url(data:font/woff2;base64,${font(w)}) format('woff2')}`).join('');
const artJs = ['art/core.js', ...book.art].map(f => fs.readFileSync(path.join(KIT, f), 'utf8')).join('\n');
const vm = require('vm'); const ctx = {}; vm.createContext(ctx); vm.runInContext(artJs, ctx);
const ART = ctx.ART;
const missing = (book.subjects || []).concat(book.cover.hero, book.cover.back_minis).filter(id => !ART.subjects[id]);
if (missing.length) { console.error('unknown subjects: ' + missing.join(', ')); process.exit(2); }
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// ---- checks on the listing (KDP limits) ----
const L = book.listing, problems = [];
if (book.subjects.length !== book.count) problems.push(`subjects ${book.subjects.length} != count ${book.count}`);
if ((L.title + ': ' + L.subtitle).length > 200) problems.push('title + subtitle over 200 characters');
if (L.keywords.length !== 7) problems.push('need exactly 7 keywords');
L.keywords.forEach(k => { if (k.length > 50) problems.push(`keyword over 50 chars: ${k}`); });
if (L.description_html.length > 4000) problems.push('description over 4000 characters');
if (problems.length) { console.error('LISTING PROBLEMS:\n' + problems.join('\n')); process.exit(2); }

// ---- interior ----
// title page, blank, then each picture on its own sheet with a blank back,
// then a certificate and a blank. Pictures print on one side only so marker
// bleed-through never spoils the next picture.
const label = (t, size) => `<svg class="lab" viewBox="0 0 1000 200"><text x="500" y="160" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="${size}" fill="#fff" stroke="#111" stroke-width="9" stroke-linejoin="round" paint-order="stroke">${esc(t)}</text></svg>`;
function interiorHtml() {
  let pages = [];
  pages.push(`<div class="pg title"><div class="t1">${esc(book.cover.kicker)}</div><div class="t2">${esc(book.cover.word)}</div><div class="t3">Coloring Book</div>
    <div class="own">This book belongs to:</div><div class="line"></div></div>`);
  pages.push('<div class="pg"></div>');
  for (const id of book.subjects) {
    pages.push(`<div class="pg"><div class="labwrap">SUBJ_LABEL_${id}</div><div class="art" data-id="${id}"></div></div>`);
    pages.push('<div class="pg"></div>');
  }
  pages.push(`<div class="pg cert"><div class="box">${label('Great job!', 170)}<p>You colored all ${book.count} ${esc(book.cover.word.toLowerCase())}!</p><div class="star"></div><p class="nm">Name: ______________________</p></div></div>`);
  pages.push('<div class="pg"></div>');
  return `<html><head><style>${FONTS}
  @page{size:${TRIM_W}in ${TRIM_H}in;margin:0} body{margin:0}
  .pg{width:${TRIM_W}in;height:${TRIM_H}in;position:relative;page-break-after:always;overflow:hidden;font-family:Fredoka}
  .labwrap{position:absolute;left:0.6in;right:0.6in;top:0.45in;height:1.7in}
  .lab{width:100%;height:100%}
  .art{position:absolute;left:0.55in;right:0.55in;top:2.05in;bottom:0.55in}
  .art svg{width:100%;height:100%}
  .title{text-align:center}
  .t1{margin-top:2.2in;font:600 40pt Fredoka}.t2{font:700 88pt Fredoka;line-height:1}.t3{font:600 36pt Fredoka;margin-top:.2in}
  .own{margin-top:1.6in;font:600 26pt Fredoka}.line{margin:0.5in auto 0;width:5.5in;border-bottom:4px solid #111}
  .cert .box{position:absolute;inset:1in;border:10px solid #111;border-radius:.6in;text-align:center;font:600 30pt Fredoka}
  .cert .lab{height:2in;width:90%;margin-top:.8in}
  .cert .nm{position:absolute;bottom:1in;left:0;right:0;font-size:24pt}
  .star{margin:.4in auto;width:3.2in;height:3.2in}
  </style></head><body>${pages.join('')}<script>${artJs}</script><script>
  document.querySelectorAll('.art').forEach(el=>{el.innerHTML=ART.svg(el.dataset.id,'line','preserveAspectRatio="xMidYMid meet"')});
  document.querySelectorAll('.star').forEach(el=>{el.innerHTML='<svg viewBox="0 0 100 100"><path d="M50 6 L62 38 L96 38 L68 58 L79 92 L50 71 L21 92 L32 58 L4 38 L38 38 Z" fill="#fff" stroke="#111" stroke-width="3" stroke-linejoin="round"/></svg>'});
  </script></body></html>`.replace(/SUBJ_LABEL_([a-z0-9-]+)/g, (m, id) => label(ART.subjects[id].label, 185));
}

// ---- cover (full wrap) ----
function coverHtml(pages, frontOnly) {
  const spine = pages * PAPER;
  const W = frontOnly ? TRIM_W : BLEED * 2 + TRIM_W * 2 + spine, H = frontOnly ? TRIM_H : TRIM_H + BLEED * 2;
  const frontX = frontOnly ? 0 : BLEED + TRIM_W + spine, bx = frontOnly ? 0 : BLEED;
  const c = book.cover, colors = ['#ff6b6b', '#ff9f43', '#f5c400', '#4caf50', '#2196f3', '#9c6ade'];
  const word = [...c.word.toUpperCase()].map((ch, i) => `<tspan fill="${colors[i % colors.length]}">${esc(ch)}</tspan>`).join('');
  const hero = c.hero.map((id, i) => `<div class="hero h${i}">${'HERO_' + id}</div>`).join('');
  const front = `<div class="front" style="left:${frontX}in">
    <div class="sun"><svg viewBox="0 0 200 200">${Array.from({ length: 12 }, (_, i) => `<line x1="100" y1="100" x2="${100 + 95 * Math.cos(i * Math.PI / 6)}" y2="${100 + 95 * Math.sin(i * Math.PI / 6)}" stroke="#ffc300" stroke-width="10" stroke-linecap="round"/>`).join('')}<circle cx="100" cy="100" r="58" fill="#ffd23f" stroke="#e8a700" stroke-width="5"/><circle cx="80" cy="90" r="6" fill="#333"/><circle cx="120" cy="90" r="6" fill="#333"/><path d="M76 112 Q100 134 124 112" fill="none" stroke="#333" stroke-width="6" stroke-linecap="round"/></svg></div>
    <div class="rainbow"><svg viewBox="0 0 800 400">${['#ff6b6b', '#ff9f43', '#ffd23f', '#7bd389', '#6ec6ff', '#b39ddb'].map((col, i) => `<path d="M${40 + i * 24} 400 A${360 - i * 24} ${360 - i * 24} 0 0 1 ${760 - i * 24} 400" fill="none" stroke="${col}" stroke-width="26"/>`).join('')}</svg></div>
    <div class="cloud c1"></div><div class="cloud c2"></div>
    <div class="badge"><svg viewBox="0 0 200 200"><path d="${Array.from({ length: 24 }, (_, i) => { const a = i * Math.PI / 12, r = i % 2 ? 80 : 98; return (i ? 'L' : 'M') + (100 + r * Math.cos(a)).toFixed(1) + ' ' + (100 + r * Math.sin(a)).toFixed(1); }).join(' ')} Z" fill="#ffd23f" stroke="#e8a700" stroke-width="4"/><text x="100" y="92" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="30" fill="#333">AGES</text><text x="100" y="132" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="40" fill="#333">${esc(c.ages)}</text></svg></div>
    <div class="tbox"><div class="k">${esc(c.kicker)}</div>
      <svg class="w" viewBox="0 0 1000 190"><text x="500" y="160" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="${Math.min(190, 1500 / Math.max(6, c.word.length))}" stroke="#fff" stroke-width="10" paint-order="stroke" stroke-linejoin="round">${word}</text></svg>
      <div class="cb">Coloring Book</div><div class="tag">${esc(c.tagline)}</div></div>
    <div class="ground"></div>${hero}
    <div class="series">${esc(book.listing.series)}</div>
  </div>`;
  const back = frontOnly ? '' : `<div class="back" style="left:${bx}in"><div class="bbox">
      <div class="bt">${esc(c.back_title)}</div>
      <ul>${c.back_points.map(p => `<li>${esc(p)}</li>`).join('')}</ul>
      <div class="bs">${esc(book.listing.series)} · by ${esc(book.listing.author)}</div></div>
      <div class="minis">${c.back_minis.map(id => `<div class="mini">MINI_${id}</div>`).join('')}</div>
      <div class="barcode"></div></div>
      <div class="spine" style="left:${BLEED + TRIM_W}in;width:${spine}in"></div>`;
  return { spine, W, H, html: `<html><head><style>${FONTS}
  @page{size:${W}in ${H}in;margin:0} body{margin:0}
  .wrap{position:relative;width:${W}in;height:${H}in;overflow:hidden;background:linear-gradient(#bfe6ff,#e6f6ff 60%,#fff);font-family:Fredoka}
  .front,.back{position:absolute;top:${frontOnly ? 0 : BLEED}in;width:${TRIM_W}in;height:${TRIM_H}in}
  .spine{position:absolute;top:0;bottom:0;background:#6ec6ff}
  .sun{position:absolute;left:.35in;top:.35in;width:1.9in;height:1.9in}
  .rainbow{position:absolute;left:.9in;right:.9in;top:1.1in;height:3.35in}.rainbow svg{width:100%;height:100%}
  .cloud{position:absolute;background:#fff;border-radius:1in;box-shadow:0 0 0 .02in #d6ecfa}
  .cloud.c1{left:5.6in;top:.8in;width:1.9in;height:.62in}.cloud.c2{left:.6in;top:3.4in;width:1.5in;height:.5in}
  .badge{position:absolute;right:.4in;top:.4in;width:1.55in;height:1.55in}
  .tbox{position:absolute;left:1in;right:1in;top:3.1in;background:#fff;border:.07in solid #555;border-radius:.35in;text-align:center;padding:.2in .2in .25in;box-shadow:0 .05in 0 #0002}
  .tbox .k{font:600 30pt Fredoka;color:#444}.tbox .w{width:100%;height:1.35in;display:block}
  .tbox .cb{font:600 30pt Fredoka;color:#444}.tbox .tag{font:600 15pt Fredoka;color:#666;margin-top:.08in}
  .ground{position:absolute;left:0;right:0;bottom:0;height:2.5in;background:#8fd694;border-top:.08in solid #5fb865}
  .hero{position:absolute;bottom:.55in;width:2.95in;height:2.95in}.hero svg{width:100%;height:100%}
  .h0{left:.1in}.h1{left:2.78in;bottom:.9in}.h2{left:5.45in}
  .series{position:absolute;left:0;right:0;bottom:.3in;text-align:center;font:600 13pt Fredoka;color:#2e6b33}
  .bbox{position:absolute;left:.75in;right:.75in;top:1in;background:#fffe;border-radius:.3in;border:.05in solid #555;padding:.35in .45in;font:400 15pt Fredoka;color:#333}
  .bt{font:700 24pt Fredoka;margin-bottom:.15in}.bbox ul{margin:0;padding-left:.3in}.bbox li{margin:.08in 0}.bs{margin-top:.2in;font:600 12pt Fredoka;color:#666}
  .minis{position:absolute;left:.75in;right:.75in;top:5.6in;display:flex;justify-content:space-between}.mini{width:1.6in;height:1.6in;background:#fff;border-radius:.2in;border:.04in solid #555}.mini svg{width:100%;height:100%}
  .barcode{position:absolute;right:.35in;bottom:.35in;width:2.1in;height:1.3in}
  </style></head><body><div class="wrap">${back}${front}</div><script>${artJs}</script><script>
  document.querySelectorAll('.hero,.mini').forEach(el=>{const id=el.textContent.replace(/^(HERO|MINI)_/,'');el.innerHTML=ART.svg(id,el.classList.contains('hero')?'color':'line')});
  </script></body></html>` };
}

(async () => {
  const b = await chromium.launch(); const errs = [];
  const newPage = async vp => { const p = await b.newPage(vp ? { viewport: vp } : {}); p.on('pageerror', e => errs.push(e.message)); return p; };
  // interior
  let p = await newPage();
  await p.setContent(interiorHtml(), { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(out, 'interior.pdf'), width: `${TRIM_W}in`, height: `${TRIM_H}in`, printBackground: true, preferCSSPageSize: true });
  const pages = await p.evaluate(() => document.querySelectorAll('.pg').length);
  // interior preview: title + first 5 pictures
  await p.setViewportSize({ width: 816, height: 1056 });
  const shots = [];
  for (const i of [0, 2, 4, 6, 8, 10]) {
    const el = (await p.$$('.pg'))[i]; const f = path.join(out, `_pg${i}.png`); await el.screenshot({ path: f }); shots.push(f);
  }
  // paperback cover (full wrap) and kindle cover (front only)
  const cov = coverHtml(pages, false);
  const fixHero = h => h;
  p = await newPage();
  await p.setContent(fixHero(cov.html), { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(out, 'cover-paperback.pdf'), width: `${cov.W}in`, height: `${cov.H}in`, printBackground: true, preferCSSPageSize: true });
  await p.setViewportSize({ width: Math.round(cov.W * 96), height: Math.round(cov.H * 96) });
  await p.screenshot({ path: path.join(out, 'preview-cover-wrap.png') });
  const fr = coverHtml(pages, true);
  p = await newPage({ width: 1980, height: 2562 });
  await p.setContent(fixHero(fr.html).replace('<body>', '<body style="zoom:2.4265">'), { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(out, 'cover-kindle.jpg'), type: 'jpeg', quality: 92 });
  await b.close();
  if (errs.length) { console.error('PAGE ERRORS:\n' + errs.join('\n')); process.exit(3); }
  // preview strip of interior pages
  fs.writeFileSync(path.join(out, '_shots.json'), JSON.stringify(shots));
  const listing = {
    title: L.title, subtitle: L.subtitle, series: L.series, author: L.author, description_html: L.description_html,
    keywords: L.keywords, categories: L.categories, reading_age: L.reading_age, price_note: L.price_note,
    ai_disclosure: L.ai_disclosure,
    print: { trim: `${TRIM_W} x ${TRIM_H} in`, bleed: 'No bleed (interior)', paper: 'White', pages, spine_in: +cov.spine.toFixed(4), cover_in: `${cov.W.toFixed(3)} x ${cov.H.toFixed(3)}`, spine_text: pages > 79 ? 'allowed' : 'none (79 pages or fewer)' },
  };
  fs.writeFileSync(path.join(out, 'listing.json'), JSON.stringify(listing, null, 1));
  console.log(JSON.stringify(listing.print));
})().catch(e => { console.error(e); process.exit(1); });
