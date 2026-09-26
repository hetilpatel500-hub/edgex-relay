// Drawing helpers for coloring-book art. Every subject draws into a 1000x1000
// box. Shapes are painted in order with a fill, so a later shape hides the lines
// of an earlier one underneath it: that's how parts join into clean outlines.
// In coloring mode every fill is white. On the cover, fills come from the
// subject's palette (keys: main, dark, light, accent, accent2, pink).
(function (root) {
  const ART = root.ART = root.ART || { subjects: {} };
  const SW = 14; // outline width in art units (1000 units is about 7 in on the page)

  function mk(fillFn) {
    const F = k => (k === 'ink' ? '#111' : k === 'none' ? 'none' : fillFn(k || 'main'));
    const st = `stroke="#111" stroke-width="${SW}" stroke-linejoin="round" stroke-linecap="round"`;
    const d = {
      E: (cx, cy, rx, ry, k, rot) => `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${F(k)}" ${st}${rot ? ` transform="rotate(${rot} ${cx} ${cy})"` : ''}/>`,
      C: (cx, cy, r, k) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${F(k)}" ${st}/>`,
      P: (path, k) => `<path d="${path}" fill="${F(k)}" ${st}/>`,
      R: (x, y, w, h, rx, k) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${F(k)}" ${st}/>`,
      L: path => `<path d="${path}" fill="none" ${st}/>`,               // line only
      Lt: path => `<path d="${path}" fill="none" stroke="#111" stroke-width="${SW * 0.7}" stroke-linecap="round"/>`,
      poly: (pts, k) => `<path d="M${pts.map(p => p.map(v => v.toFixed(1)).join(',')).join(' L')} Z" fill="${F(k)}" ${st}/>`,
      // solid black eye with a white shine
      eye: (x, y, r = 24) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#111"/><circle cx="${x - r * 0.32}" cy="${y - r * 0.32}" r="${r * 0.34}" fill="#fff"/>`,
      dot: (x, y, r = 9) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#111"/>`,
      smile: (x, y, w, h) => `<path d="M${x - w} ${y} Q${x} ${y + (h || w * 0.8)} ${x + w} ${y}" fill="none" ${st}/>`,
      // a stripe across an ellipse between x1 and x2, following its curve
      band: (cx, cy, rx, ry, x1, x2, k) => {
        const top = [], bot = [];
        for (let i = 0; i <= 12; i++) {
          const x = x1 + (x2 - x1) * i / 12, t = Math.max(0, 1 - ((x - cx) / rx) ** 2);
          top.push([x, cy - ry * Math.sqrt(t)]); bot.unshift([x, cy + ry * Math.sqrt(t)]);
        }
        return d.poly(top.concat(bot), k);
      },
      // a scalloped ring (mane, wool, clouds): circles around a centre, then a
      // plain disc on top that hides the inner arcs
      scallop: (cx, cy, R, n, r, k) => {
        let s = '';
        for (let i = 0; i < n; i++) { const a = i / n * 2 * Math.PI; s += `<circle cx="${cx + R * Math.cos(a)}" cy="${cy + R * Math.sin(a)}" r="${r}" fill="${F(k)}" ${st}/>`; }
        return s + `<circle cx="${cx}" cy="${cy}" r="${R}" fill="${F(k)}"/>`;
      },
      // a cute face: two eyes, a smile and rosy cheeks, centred on x,y, size s
      face: (x, y, s = 200) => {
        const e = s * 0.34, r = Math.max(12, s * 0.085);
        return `<circle cx="${x - e}" cy="${y}" r="${r}" fill="#111"/><circle cx="${x - e - r * 0.32}" cy="${y - r * 0.32}" r="${r * 0.34}" fill="#fff"/>` +
          `<circle cx="${x + e}" cy="${y}" r="${r}" fill="#111"/><circle cx="${x + e - r * 0.32}" cy="${y - r * 0.32}" r="${r * 0.34}" fill="#fff"/>` +
          `<path d="M${x - s * 0.16} ${y + s * 0.2} Q${x} ${y + s * 0.38} ${x + s * 0.16} ${y + s * 0.2}" fill="none" stroke="#111" stroke-width="${SW * 0.85}" stroke-linecap="round"/>` +
          `<circle cx="${x - e - s * 0.08}" cy="${y + s * 0.22}" r="${s * 0.09}" fill="${F('pink')}" stroke="#111" stroke-width="${SW * 0.6}"/>` +
          `<circle cx="${x + e + s * 0.08}" cy="${y + s * 0.22}" r="${s * 0.09}" fill="${F('pink')}" stroke="#111" stroke-width="${SW * 0.6}"/>`;
      },
      grass: (y = 900) => `<path d="M60 ${y} Q280 ${y - 24} 500 ${y} T 940 ${y}" fill="none" ${st}/>`,
      water: (y = 880) => `<path d="M60 ${y} q55 -30 110 0 t110 0 t110 0 t110 0 t110 0 t110 0 t110 0 t110 0" fill="none" ${st}/>`,
    };
    return d;
  }

  ART.draw = function (id, mode) {
    const s = ART.subjects[id];
    if (!s) throw new Error('no subject ' + id);
    const pal = Object.assign({ main: '#fff', dark: '#fff', light: '#fff', accent: '#fff', accent2: '#fff', pink: '#fff' },
      mode === 'color' ? (s.pal || {}) : {});
    return s.draw(mk(k => pal[k] || '#fff'));
  };
  ART.svg = function (id, mode, attrs = '') {
    return `<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg" ${attrs}>${ART.draw(id, mode)}</svg>`;
  };
  ART.add = function (id, label, pal, draw) { ART.subjects[id] = { id, label, pal, draw }; };
  if (typeof module !== 'undefined') module.exports = ART;
})(typeof window !== 'undefined' ? window : globalThis);
