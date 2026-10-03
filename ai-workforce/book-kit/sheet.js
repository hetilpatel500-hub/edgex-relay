// Contact sheet of every subject in an art file, for the art review step.
// usage: node sheet.js art/animals.js OUT.png [color]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [artFile, out, mode] = process.argv.slice(2);
(async () => {
  const kit = __dirname;
  const js = fs.readFileSync(path.join(kit, 'art/core.js'), 'utf8') + '\n' + fs.readFileSync(path.resolve(artFile), 'utf8');
  const html = `<html><body style="margin:0;background:#fff;font:600 22px sans-serif">
  <div id="g" style="display:grid;grid-template-columns:repeat(6,300px);gap:6px;padding:6px"></div>
  <script>${js}</script><script>
  const g=document.getElementById('g');let errs=[];
  for(const id of Object.keys(ART.subjects)){try{g.insertAdjacentHTML('beforeend','<div style="border:1px solid #ccc"><div style="text-align:center">'+ART.subjects[id].label+'</div>'+ART.svg(id,'${mode || 'line'}','width="300" height="300"')+'</div>')}catch(e){errs.push(id+': '+e.message)}}
  window.errs=errs;</script></body></html>`;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1850, height: 800 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.setContent(html); const e2 = await p.evaluate(() => window.errs);
  await p.screenshot({ path: out, fullPage: true }); await b.close();
  const all = errs.concat(e2 || []);
  console.log(all.length ? 'ERRORS:\n' + all.join('\n') : 'ok ' + out);
  if (all.length) process.exit(2);
})();
