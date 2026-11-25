// "My First Easter & Spring": 30 eggs, bunnies, baby animals and spring things for ages 2-5.
// Generic subjects only: no brands, candy trademarks, religious figures or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const W = '#ffffff', P = '#ffb3c7', LP = '#ffe0ea', PU = '#c9a7ff', LPU = '#e6d9ff', Y = '#ffd23f', LY = '#fff1a8', O = '#ff9f43',
    G = '#7bd389', LG = '#c8f0cf', B = '#8fd3ff', LB = '#d4efff', BR = '#c68b59', DB = '#8d5a3b', TAN = '#e8b98a',
    CH = '#9a5b3a', CR = '#fff4e6', GR = '#cfd8dc', R = '#ff5a6e';

  const f = v => (+v).toFixed(1);
  const g = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${f(cx)} ${f(cy)})">${s}</g>`;
  let uid = 0;

  // ---------- helpers ----------
  // an egg centred on x,y: half-width w, half-height h (wider low down)
  const eggP = (x, y, w, h) =>
    `M${f(x)} ${f(y - h)} C${f(x + 0.72 * w)} ${f(y - h)} ${f(x + w)} ${f(y - 0.3 * h)} ${f(x + w)} ${f(y + 0.18 * h)} ` +
    `C${f(x + w)} ${f(y + 0.72 * h)} ${f(x + 0.56 * w)} ${f(y + h)} ${f(x)} ${f(y + h)} ` +
    `C${f(x - 0.56 * w)} ${f(y + h)} ${f(x - w)} ${f(y + 0.72 * h)} ${f(x - w)} ${f(y + 0.18 * h)} ` +
    `C${f(x - w)} ${f(y - 0.3 * h)} ${f(x - 0.72 * w)} ${f(y - h)} ${f(x)} ${f(y - h)} Z`;
  // a zigzag band of thickness t across x1..x2, centred on yc
  const zig = (d, x1, x2, yc, t, amp, n, k) => {
    const top = [], bot = [];
    for (let i = 0; i <= n; i++) {
      const x = x1 + (x2 - x1) * i / n, o = i % 2 ? amp : -amp;
      top.push([x, yc - t / 2 + o]); bot.unshift([x, yc + t / 2 + o]);
    }
    return d.poly(top.concat(bot), k);
  };
  // a decorated egg; the pattern is clipped to the egg, then the outline is drawn again on top
  const egg = (d, x, y, w, h, pat = 'zig', k = 'main', a = 'accent', b = 'accent2', rot = 0) => {
    const id = 'eggclip' + (uid++), p = eggP(x, y, w, h), X = x - w - 40, WW = 2 * w + 80;
    let deco = '';
    if (pat === 'zig') deco = d.R(X, y - 0.62 * h, WW, 0.17 * h, 0, b) + zig(d, X, x + w + 40, y + 0.08 * h, 0.3 * h, 0.1 * h, 8, a) + d.R(X, y + 0.55 * h, WW, 0.17 * h, 0, b);
    else if (pat === 'stripes') deco = d.R(X, y - 0.55 * h, WW, 0.2 * h, 0, a) + d.R(X, y - 0.05 * h, WW, 0.2 * h, 0, b) + d.R(X, y + 0.45 * h, WW, 0.2 * h, 0, a);
    else if (pat === 'dots') deco = [[0, -0.55], [-0.5, -0.08], [0.5, -0.08], [0, 0.22], [-0.45, 0.6], [0.45, 0.6]]
      .map(([u, v], i) => d.C(x + u * w, y + v * h, 0.19 * w, i % 2 ? b : a)).join('');
    else if (pat === 'flower') deco = d.R(X, y - 0.62 * h, WW, 0.16 * h, 0, b) + daisy(d, x, y + 0.1 * h, 0.75 * w, a, b) + d.R(X, y + 0.62 * h, WW, 0.16 * h, 0, b);
    const body = d.P(p, k) + (deco ? `<defs><clipPath id="${id}"><path d="${p}"/></clipPath></defs><g clip-path="url(#${id})">${deco}</g>` : '') + d.L(p);
    return rot ? g(body, rot, x, y) : body;
  };
  // a daisy: six petals around a round centre, radius r
  const daisy = (d, x, y, r, k = 'light', c = 'accent') => {
    let s = '';
    for (let i = 0; i < 6; i++) {
      const a = i * 60, t = a * Math.PI / 180;
      s += d.E(f(x + Math.cos(t) * r * 0.6), f(y + Math.sin(t) * r * 0.6), f(r * 0.44), f(r * 0.3), k, a);
    }
    return s + d.C(f(x), f(y), f(r * 0.38), c);
  };
  // a five-petal blossom
  const blossom = (d, x, y, r, k = 'light', c = 'accent') => {
    let s = '';
    for (let i = 0; i < 5; i++) { const t = (i * 72 - 90) * Math.PI / 180; s += d.C(f(x + Math.cos(t) * r * 0.55), f(y + Math.sin(t) * r * 0.55), f(r * 0.45), k); }
    return s + d.C(f(x), f(y), f(r * 0.32), c);
  };
  // a tulip cup centred on x,y, scale s
  const tulip = (d, x, y, s = 1, k = 'main') =>
    d.P(`M${f(x - 70 * s)} ${f(y - 40 * s)} L${f(x - 35 * s)} ${f(y - 5 * s)} L${f(x)} ${f(y - 62 * s)} L${f(x + 35 * s)} ${f(y - 5 * s)} L${f(x + 70 * s)} ${f(y - 40 * s)} ` +
      `Q${f(x + 82 * s)} ${f(y + 70 * s)} ${f(x)} ${f(y + 75 * s)} Q${f(x - 82 * s)} ${f(y + 70 * s)} ${f(x - 70 * s)} ${f(y - 40 * s)} Z`, k);
  // bunny ears and head with a cute face and a little nose
  const bunnyHead = (d, x, y, s = 1, k = 'main') =>
    d.E(f(x - 62 * s), f(y - 175 * s), f(48 * s), f(125 * s), k, -10) + d.E(f(x - 62 * s), f(y - 168 * s), f(22 * s), f(88 * s), 'pink', -10) +
    d.E(f(x + 62 * s), f(y - 175 * s), f(48 * s), f(125 * s), k, 10) + d.E(f(x + 62 * s), f(y - 168 * s), f(22 * s), f(88 * s), 'pink', 10) +
    d.C(f(x), f(y), f(140 * s), k) + d.face(x, y + 5 * s, 150 * s) + d.E(f(x), f(y + 20 * s), f(17 * s), f(12 * s), 'pink');
  // a ribbon bow centred on x,y
  const bow = (d, x, y, s = 1, k = 'accent') =>
    d.P(`M${f(x)} ${f(y)} Q${f(x - 60 * s)} ${f(y - 70 * s)} ${f(x - 105 * s)} ${f(y - 30 * s)} Q${f(x - 120 * s)} ${f(y + 30 * s)} ${f(x)} ${f(y)} Z`, k) +
    d.P(`M${f(x)} ${f(y)} Q${f(x + 60 * s)} ${f(y - 70 * s)} ${f(x + 105 * s)} ${f(y - 30 * s)} Q${f(x + 120 * s)} ${f(y + 30 * s)} ${f(x)} ${f(y)} Z`, k) +
    d.poly([[x - 12 * s, y + 5 * s], [x - 55 * s, y + 85 * s], [x - 22 * s, y + 80 * s]], k) +
    d.poly([[x + 12 * s, y + 5 * s], [x + 55 * s, y + 85 * s], [x + 22 * s, y + 80 * s]], k) +
    d.C(f(x), f(y), f(24 * s), k);
  // a puffy cloud w wide, centred on cx,cy
  const cloud = (d, cx, cy, w, k = 'light') => {
    const p = (x, y) => `${f(cx + x * w)} ${f(cy + y * w)}`;
    return d.P(`M${p(-0.46, 0.19)} A1 1 0 0 1 ${p(-0.33, -0.05)} A1 1 0 0 1 ${p(-0.02, -0.28)} A1 1 0 0 1 ${p(0.3, -0.1)} A1 1 0 0 1 ${p(0.46, 0.19)} Q${p(0, 0.27)} ${p(-0.46, 0.19)} Z`, k);
  };
  // a smiling sun with triangle rays
  const sun = (d, x, y, r, k = 'accent') => {
    let s = '';
    for (let i = 0; i < 8; i++) {
      const t = i * Math.PI / 4, q = (rr, da) => [x + Math.cos(t + da) * rr, y + Math.sin(t + da) * rr];
      s += d.poly([q(r + 10, -0.22), q(r + 52, 0), q(r + 10, 0.22)], k);
    }
    return s + d.C(x, y, r, k) + d.face(x, y + 4, r * 1.15);
  };
  // a raindrop centred on x,y
  const drop = (d, x, y, s = 1, k = 'light') =>
    d.P(`M${f(x)} ${f(y - 45 * s)} Q${f(x + 34 * s)} ${f(y + 2 * s)} ${f(x + 28 * s)} ${f(y + 18 * s)} A${f(30 * s)} ${f(30 * s)} 0 0 1 ${f(x - 28 * s)} ${f(y + 18 * s)} Q${f(x - 34 * s)} ${f(y + 2 * s)} ${f(x)} ${f(y - 45 * s)} Z`, k);
  // a clump of grass blades standing on y, half-width w, height h
  const tuft = (d, x, y, w, h, k = 'accent2') =>
    d.poly([[x - w, y], [x - 0.8 * w, y - 0.75 * h], [x - 0.52 * w, y - 0.22 * h], [x - 0.3 * w, y - h], [x - 0.05 * w, y - 0.25 * h],
      [x + 0.22 * w, y - 0.95 * h], [x + 0.45 * w, y - 0.22 * h], [x + 0.72 * w, y - 0.8 * h], [x + 0.85 * w, y - 0.2 * h], [x + w, y]], k);
  // a carrot hanging from its top (x,y), length len, with leaves
  const carrot = (d, x, y, len, face) =>
    d.E(x - 38, y - 78, 26, 72, 'accent2', -25) + d.E(x, y - 96, 26, 82, 'accent2', 0) + d.E(x + 38, y - 78, 26, 72, 'accent2', 25) +
    d.P(`M${x - 72} ${y} Q${x} ${y - 30} ${x + 72} ${y} Q${x + 52} ${y + len * 0.6} ${x} ${y + len} Q${x - 52} ${y + len * 0.6} ${x - 72} ${y} Z`, 'main') +
    d.Lt(`M${x - 50} ${y + len * 0.5} L${x - 22} ${y + len * 0.5} M${x + 18} ${y + len * 0.66} L${x + 40} ${y + len * 0.66}`) +
    (face ? d.face(x, y + 95, 120) : '');

  // ---------------- Easter fun ----------------
  A.add('easter-egg', 'Easter Egg', { main: PU, accent: Y, accent2: P, light: W, pink: P }, d =>
    d.grass(905) +
    d.L('M170 905 L170 830 M830 905 L830 830') + daisy(d, 170, 800, 70, 'light', 'accent') + daisy(d, 830, 800, 70, 'light', 'accent') +
    egg(d, 500, 520, 255, 340, 'zig', 'main', 'accent', 'accent2'));

  A.add('easter-bunny', 'Easter Bunny', { main: TAN, light: W, accent: B, accent2: Y, pink: P }, d =>
    d.grass(925) + d.C(690, 800, 55, 'light') +
    d.E(500, 700, 195, 195) +
    d.E(385, 880, 88, 46) + d.E(615, 880, 88, 46) +
    bunnyHead(d, 500, 360, 1.05) +
    egg(d, 500, 692, 108, 138, 'dots', 'accent', 'accent2', 'light') +
    d.E(390, 650, 52, 45) + d.E(610, 650, 52, 45));

  A.add('easter-basket', 'Easter Basket', { main: TAN, dark: BR, light: B, accent: Y, accent2: G, pink: P }, d =>
    d.P('M215 600 Q215 175 500 175 Q785 175 785 600 L735 600 Q735 228 500 228 Q265 228 265 600 Z', 'dark') +
    egg(d, 355, 435, 100, 128, 'stripes', 'light', 'accent', 'pink', -15) +
    egg(d, 645, 435, 100, 128, 'dots', 'accent', 'pink', 'light', 15) +
    egg(d, 500, 395, 108, 140, 'zig', 'pink', 'light', 'accent') +
    zig(d, 205, 795, 548, 50, 22, 14, 'accent2') +
    d.P('M205 575 L795 575 L728 885 L272 885 Z', 'main') + d.R(180, 545, 640, 70, 35, 'dark') +
    d.Lt('M242 690 L758 690 M258 790 L742 790') + d.Lt('M380 615 L392 885 M500 615 L500 885 M620 615 L608 885'));

  A.add('chocolate-bunny', 'Chocolate Bunny', { main: CH, dark: DB, light: BR, accent: P, accent2: Y, pink: '#f08a8a' }, d =>
    d.E(430, 200, 50, 135, 'main', -8) + d.E(430, 210, 22, 95, 'light', -8) +
    d.E(570, 200, 50, 135, 'main', 8) + d.E(570, 210, 22, 95, 'light', 8) +
    d.E(500, 680, 180, 215) +
    d.C(500, 380, 135) + d.face(500, 385, 150) + d.E(500, 402, 16, 11, 'pink') +
    d.E(352, 650, 42, 88, 'main', 18) + d.E(648, 650, 42, 88, 'main', -18) +
    d.E(500, 720, 85, 110, 'light') +
    d.R(270, 860, 460, 62, 30, 'dark') +
    bow(d, 500, 520, 0.85, 'accent'));

  A.add('jelly-beans', 'Jelly Beans', { main: R, light: LB, dark: PU, accent: Y, accent2: G, pink: O }, d => {
    const beans = [[372, 375, 20], [490, 365, -15], [610, 380, 30], [425, 470, -30], [545, 475, 10], [645, 470, -20], [365, 570, 15], [480, 580, -10],
      [600, 565, 25], [405, 675, -25], [525, 680, 5], [640, 670, -35], [370, 780, 10], [490, 790, -20], [610, 785, 15]];
    const ks = ['main', 'accent', 'accent2', 'pink', 'dark'];
    return d.L('M80 905 L920 905') +
      d.R(275, 255, 450, 640, 90, 'light') + d.Lt('M318 340 L318 470') +
      beans.map(([x, y, r], i) => d.E(x, y, 46, 29, ks[i % 5], r)).join('') +
      d.R(325, 170, 350, 95, 28, 'dark') + d.Lt('M370 200 L370 240 M430 200 L430 240 M490 200 L490 240 M550 200 L550 240 M610 200 L610 240') +
      d.E(170, 875, 46, 29, 'main', -20) + d.E(835, 875, 46, 29, 'accent2', 25);
  });

  A.add('egg-hunt', 'Egg Hunt', { main: LG, light: B, accent: Y, accent2: G, pink: P }, d =>
    sun(d, 820, 190, 78, 'accent') +
    d.L('M60 720 Q500 520 940 720') +
    egg(d, 290, 630, 78, 100, 'stripes', 'light', 'accent', 'pink', -15) +
    egg(d, 700, 610, 82, 105, 'zig', 'pink', 'light', 'accent', 15) +
    egg(d, 500, 790, 88, 112, 'dots', 'accent', 'pink', 'light') +
    tuft(d, 290, 725, 115, 95) + tuft(d, 700, 712, 115, 95) + tuft(d, 500, 925, 125, 90) +
    d.L('M150 720 L150 600') + daisy(d, 150, 560, 70, 'light', 'accent') +
    d.L('M860 760 L860 650') + daisy(d, 860, 615, 62, 'pink', 'accent'));

  A.add('bunny-ears', 'Bunny Ears', { main: W, dark: PU, pink: P, accent: Y, accent2: P }, d =>
    d.E(392, 300, 72, 205, 'main', -12) + d.E(392, 318, 33, 148, 'pink', -12) +
    d.E(608, 300, 72, 205, 'main', 12) + d.E(608, 318, 33, 148, 'pink', 12) +
    d.P('M215 840 Q215 470 500 470 Q785 470 785 840 L735 840 Q735 522 500 522 Q265 522 265 840 Z', 'dark') +
    bow(d, 690, 545, 0.85, 'accent') +
    daisy(d, 300, 610, 62, 'accent2', 'accent'));

  A.add('easter-bonnet', 'Easter Bonnet', { main: LY, accent: PU, accent2: Y, light: W, pink: P }, d =>
    d.E(500, 600, 340, 100) +
    d.P('M325 600 Q325 300 500 300 Q675 300 675 600 Z') +
    d.P('M326 505 Q500 528 674 505 L675 575 Q500 598 325 575 Z', 'accent') +
    d.poly([[640, 585], [735, 760], [690, 772], [610, 600]], 'accent') + d.poly([[600, 592], [640, 790], [595, 790], [570, 598]], 'accent') +
    daisy(d, 420, 540, 66, 'light', 'accent2') + daisy(d, 560, 535, 54, 'pink', 'accent2'));

  A.add('painted-eggs', 'Painted Eggs', { main: B, accent: Y, accent2: P, light: G, pink: PU }, d =>
    d.L('M90 815 L910 815') +
    egg(d, 320, 600, 130, 170, 'stripes', 'light', 'accent', 'accent2', -12) +
    egg(d, 680, 600, 130, 170, 'flower', 'accent2', 'light', 'accent', 12) +
    egg(d, 500, 610, 150, 200, 'zig', 'main', 'accent', 'pink'));

  A.add('bunny-slippers', 'Bunny Slippers', { main: LP, dark: PU, pink: P, accent: P }, d => {
    const slip = (x, y, k = 1.25) => {
      const q = v => f(v * k);
      return d.E(f(x - 52 * k), f(y - 190 * k), q(32), q(88), 'main', -15) + d.E(f(x - 52 * k), f(y - 185 * k), q(14), q(60), 'pink', -15) +
        d.E(f(x + 52 * k), f(y - 190 * k), q(32), q(88), 'main', 15) + d.E(f(x + 52 * k), f(y - 185 * k), q(14), q(60), 'pink', 15) +
        d.E(x, f(y + 75 * k), q(165), q(58), 'dark') +
        d.P(`M${f(x - 155 * k)} ${f(y + 70 * k)} Q${f(x - 160 * k)} ${f(y - 125 * k)} ${x} ${f(y - 125 * k)} Q${f(x + 160 * k)} ${f(y - 125 * k)} ${f(x + 155 * k)} ${f(y + 70 * k)} Z`) +
        d.face(x, y - 20 * k, 140 * k) + d.E(x, f(y - 2 * k), q(15), q(10), 'pink');
    };
    return slip(275, 600) + slip(725, 600);
  });

  A.add('carrots', 'Carrots', { main: O, accent2: G, accent: PU, pink: P }, d =>
    g(carrot(d, 360, 300, 500, true), -18, 360, 300) +
    g(carrot(d, 640, 300, 500, true), 18, 640, 300) +
    bow(d, 500, 640, 0.9, 'accent'));

  // ---------------- baby animals & garden friends ----------------
  A.add('chick', 'Chick', { main: Y, accent: O, light: W, pink: P }, d =>
    d.grass(925) + d.E(435, 872, 52, 26, 'accent') + d.E(565, 872, 52, 26, 'accent') +
    d.C(500, 600, 250) +
    d.E(262, 625, 50, 100, 'main', 25) + d.E(738, 625, 50, 100, 'main', -25) +
    d.eye(428, 560, 28) + d.eye(572, 560, 28) +
    d.P('M455 615 L500 590 L545 615 L500 660 Z', 'accent') + d.L('M460 616 L540 616') +
    d.C(365, 640, 30, 'pink') + d.C(635, 640, 30, 'pink') +
    g(d.P('M330 432 Q330 222 500 212 Q670 222 670 432 L628 396 L586 436 L543 396 L500 436 L457 396 L414 436 L372 396 Z', 'light'), -10, 500, 330));

  A.add('lamb', 'Lamb', { main: CR, light: W, dark: GR, pink: P, accent: Y, accent2: B }, d =>
    d.scallop(500, 690, 165, 12, 70, 'light') +
    d.E(420, 905, 46, 30, 'dark') + d.E(580, 905, 46, 30, 'dark') +
    d.E(352, 372, 78, 32, 'main', -20) + d.E(352, 374, 44, 15, 'pink', -20) +
    d.E(648, 372, 78, 32, 'main', 20) + d.E(648, 374, 44, 15, 'pink', 20) +
    d.E(500, 400, 125, 140) +
    d.C(452, 272, 40, 'light') + d.C(500, 258, 46, 'light') + d.C(548, 272, 40, 'light') +
    d.face(500, 420, 150) +
    d.P('M420 525 Q500 572 580 525 L582 552 Q500 600 418 552 Z', 'accent2') + d.C(500, 598, 32, 'accent'));

  A.add('duckling', 'Duckling', { main: Y, accent: O, light: B, pink: P, accent2: W }, d =>
    d.poly([[300, 600], [228, 512], [345, 552]]) +
    d.E(480, 630, 225, 150) +
    d.P('M330 610 Q440 520 560 610 Q450 690 330 610 Z') +
    d.C(600, 410, 118) +
    d.E(712, 432, 68, 30, 'accent') + d.L('M650 432 L775 432') +
    d.eye(622, 392, 25) + d.C(588, 455, 24, 'pink') +
    d.L('M585 293 Q578 250 612 262') +
    d.E(480, 810, 420, 120, 'light') + d.Lt('M150 845 Q190 825 230 845 M690 870 Q735 850 780 870 M420 890 Q460 870 500 890') +
    daisy(d, 210, 770, 52, 'accent2', 'accent'));

  A.add('fawn', 'Fawn', { main: BR, light: W, dark: DB, pink: P }, d =>
    d.grass(905) +
    d.R(345, 600, 42, 270, 21) + d.R(415, 610, 42, 260, 21) + d.R(580, 610, 42, 260, 21) + d.R(650, 600, 42, 270, 21) +
    d.E(366, 875, 28, 16, 'dark') + d.E(436, 875, 28, 16, 'dark') + d.E(601, 875, 28, 16, 'dark') + d.E(671, 875, 28, 16, 'dark') +
    d.E(300, 520, 26, 42, 'light', -35) +
    d.E(505, 580, 215, 125) +
    d.P('M598 545 Q632 430 662 352 L756 374 Q722 468 702 572 Z') +
    d.E(640, 240, 32, 75, 'main', -40) + d.E(640, 244, 14, 45, 'pink', -40) +
    d.E(795, 238, 32, 75, 'main', 40) + d.E(795, 242, 14, 45, 'pink', 40) +
    d.E(718, 335, 92, 80) + d.E(780, 375, 50, 38, 'light') + d.dot(812, 365, 12) +
    d.eye(712, 318, 22) + d.C(700, 368, 20, 'pink') +
    d.C(440, 540, 22, 'light') + d.C(520, 515, 18, 'light') + d.C(570, 580, 20, 'light') + d.C(420, 615, 18, 'light') + d.C(500, 620, 16, 'light'));

  A.add('baby-bunny', 'Baby Bunny', { main: GR, light: W, pink: P, accent: P, accent2: G }, d =>
    d.grass(905) +
    d.C(285, 640, 48, 'light') +
    d.E(470, 680, 205, 155) + d.C(380, 720, 115) +
    d.E(392, 860, 118, 42) + d.E(660, 860, 55, 32) +
    d.E(600, 290, 42, 125, 'main', -18) + d.E(600, 296, 18, 88, 'pink', -18) +
    d.E(680, 300, 42, 118, 'main', 12) + d.E(680, 306, 18, 82, 'pink', 12) +
    d.C(650, 470, 118) +
    d.eye(675, 450, 24) + d.E(758, 482, 17, 12, 'pink') + d.L('M740 512 Q725 530 700 515') + d.C(650, 515, 22, 'pink') +
    d.L('M845 905 L845 830') + daisy(d, 845, 800, 55, 'accent', 'light'));

  A.add('frog', 'Frog', { main: G, light: LG, accent2: '#5cb85c', pink: P, accent: P }, d =>
    d.E(500, 810, 360, 95, 'accent2') + d.Lt('M500 810 L330 760 M500 810 L690 765 M500 810 L640 870') +
    d.E(320, 735, 95, 48, 'main', -10) + d.E(680, 735, 95, 48, 'main', 10) +
    d.E(500, 640, 195, 150) +
    d.E(500, 500, 215, 125) +
    d.C(395, 405, 72) + d.C(605, 405, 72) +
    d.eye(395, 405, 34) + d.eye(605, 405, 34) +
    d.smile(500, 535, 95, 45) + d.C(335, 520, 32, 'pink') + d.C(665, 520, 32, 'pink') +
    d.E(500, 670, 105, 85, 'light') +
    d.E(415, 770, 44, 26) + d.E(585, 770, 44, 26));

  A.add('robins-nest', "Robin's Nest", { main: BR, dark: DB, light: B, accent: O, accent2: '#9e8a78', pink: P }, d =>
    d.E(500, 560, 290, 60, 'dark') +
    egg(d, 405, 545, 58, 76, '', 'light', 'light', 'light', -12) +
    egg(d, 500, 528, 60, 80, '', 'light') +
    egg(d, 595, 545, 58, 76, '', 'light', 'light', 'light', 12) +
    d.P('M205 570 Q500 640 795 570 Q780 820 500 840 Q220 820 205 570 Z') +
    d.Lt('M260 640 Q400 690 560 660 M300 720 Q470 760 700 700 M380 790 Q520 810 640 780 M640 640 Q700 650 750 630') +
    d.L('M735 470 L728 535 M775 472 L772 535') +
    d.poly([[668, 390], [600, 360], [650, 430]], 'accent2') +
    d.E(745, 405, 98, 80, 'accent2') + d.E(770, 435, 62, 52, 'accent') +
    d.C(820, 330, 62, 'accent2') + d.eye(838, 318, 18) + d.poly([[875, 330], [925, 345], [876, 360]], 'accent2'));

  A.add('caterpillar', 'Caterpillar', { main: G, light: LG, accent: Y, accent2: G, pink: P, dark: '#5cb85c' }, d => {
    let s = d.E(500, 720, 410, 135, 'dark', -4) + d.Lt('M120 735 Q500 700 880 690');
    const seg = [[205, 560], [300, 525], [395, 560], [490, 525], [585, 560]];
    seg.forEach(([x, y], i) => { s += d.E(x - 10, y + 82, 18, 26) + d.E(x + 22, y + 82, 18, 26); });
    seg.forEach(([x, y], i) => { s += d.C(x, y, 72, i % 2 ? 'light' : 'main'); });
    return s + d.L('M690 380 Q665 285 615 270 M760 380 Q790 290 840 285') + d.C(615, 265, 20, 'accent') + d.C(840, 280, 20, 'accent') +
      d.C(715, 470, 112) + d.face(715, 470, 135);
  });

  A.add('butterfly', 'Butterfly', { main: PU, light: P, accent: Y, dark: B, pink: P }, d =>
    d.E(370, 650, 125, 112, 'light', 20) + d.E(630, 650, 125, 112, 'light', -20) +
    d.E(335, 385, 175, 145, 'main', -25) + d.E(665, 385, 175, 145, 'main', 25) +
    d.C(320, 375, 55, 'accent') + d.C(680, 375, 55, 'accent') + d.C(380, 660, 38, 'accent') + d.C(620, 660, 38, 'accent') +
    d.E(500, 555, 45, 215, 'dark') +
    d.L('M470 260 Q430 150 380 160 M530 260 Q570 150 620 160') + d.C(378, 160, 18) + d.C(622, 160, 18) +
    d.C(500, 310, 70, 'dark') + d.face(500, 312, 88));

  A.add('bumblebee', 'Bumblebee', { main: Y, dark: '#4a4a4a', light: LB, accent: P, accent2: W, pink: P }, d =>
    d.L('M200 905 L200 830') + daisy(d, 200, 800, 68, 'accent2', 'main') +
    d.E(420, 320, 85, 115, 'light', -20) + d.E(565, 310, 85, 115, 'light', 20) +
    d.poly([[290, 515], [218, 540], [290, 565]], 'dark') +
    d.E(480, 520, 210, 165) +
    d.band(480, 520, 210, 165, 405, 455, 'dark') + d.band(480, 520, 210, 165, 530, 580, 'dark') +
    d.L('M690 410 Q680 320 640 300 M745 418 Q780 330 825 320') + d.C(640, 298, 18, 'dark') + d.C(827, 318, 18, 'dark') +
    d.C(705, 510, 108) + d.face(708, 515, 125));

  // ---------------- spring flowers & rainy days ----------------
  A.add('tulip', 'Tulip', { main: R, accent2: G, accent: Y, pink: P }, d =>
    d.grass(905) +
    d.R(485, 520, 30, 385, 15, 'accent2') +
    d.P('M500 820 Q350 720 330 560 Q450 630 500 770 Z', 'accent2') + d.P('M500 800 Q650 690 680 540 Q560 610 500 750 Z', 'accent2') +
    tulip(d, 500, 380, 2.6, 'main') + d.face(500, 440, 150));

  A.add('daffodil', 'Daffodil', { main: LY, accent: O, accent2: G, pink: P }, d => {
    let s = d.grass(905) + d.R(485, 520, 30, 385, 15, 'accent2') +
      d.P('M490 880 Q380 760 380 600 Q440 700 495 820 Z', 'accent2') + d.P('M510 880 Q630 740 620 590 Q560 700 505 820 Z', 'accent2');
    for (let i = 0; i < 6; i++) {
      const t = (i * 60 - 90) * Math.PI / 180;
      s += d.E(f(500 + Math.cos(t) * 150), f(370 + Math.sin(t) * 150), 105, 70, 'main', i * 60 - 90);
    }
    return s + d.scallop(500, 370, 88, 10, 26, 'accent') + d.C(500, 370, 88, 'accent') + d.face(500, 372, 120);
  });

  A.add('flower-pot', 'Flower Pot', { main: O, accent2: G, light: W, accent: Y, pink: P, dark: PU }, d =>
    d.L('M380 590 L380 380 M500 590 L500 330 M620 590 L620 380') +
    d.E(440, 480, 50, 22, 'accent2', -30) + d.E(560, 470, 50, 22, 'accent2', 30) +
    daisy(d, 360, 330, 95, 'light', 'accent') + tulip(d, 500, 250, 1.3, 'pink') + daisy(d, 640, 330, 95, 'dark', 'accent') +
    d.P('M330 620 L670 620 L628 885 L372 885 Z') + d.R(300, 575, 400, 85, 22) +
    d.face(500, 745, 140));

  A.add('watering-can', 'Watering Can', { main: B, accent: Y, light: LB, accent2: G, pink: P }, d =>
    d.P('M330 470 Q330 250 480 250 Q630 250 630 470 L585 470 Q585 298 480 298 Q375 298 375 470 Z') +
    d.poly([[600, 600], [835, 395], [868, 432], [640, 660]]) +
    d.P('M290 460 L670 460 L640 830 L320 830 Z') + d.R(275, 440, 410, 55, 25) +
    d.E(870, 405, 55, 34, 'accent', -45) +
    drop(d, 905, 520, 0.7) + drop(d, 845, 580, 0.7) + drop(d, 920, 640, 0.7) +
    d.L('M860 905 L860 800') + d.E(820, 790, 45, 22, 'accent2', -30) + d.E(900, 780, 45, 22, 'accent2', 30) +
    d.L('M80 905 L940 905') +
    d.face(480, 650, 170));

  A.add('sprout', 'Sprout', { main: G, dark: BR, accent: Y, light: LG, pink: P }, d =>
    sun(d, 180, 180, 75, 'accent') +
    d.L('M500 760 Q485 640 505 500') +
    d.P('M503 540 Q340 380 210 450 Q320 610 503 540 Z') + d.Lt('M490 535 Q360 470 260 455') +
    d.P('M507 510 Q665 330 800 395 Q700 565 507 510 Z') + d.Lt('M520 505 Q650 430 750 400') +
    d.P('M110 885 Q500 620 890 885 Z', 'dark') + d.face(500, 815, 115));

  A.add('rain-boots', 'Rain Boots', { main: Y, dark: O, light: B, accent: W, pink: P }, d => {
    const boot = x =>
      d.P(`M${x} 300 L${x + 135} 300 L${x + 135} 690 Q${x + 245} 690 ${x + 255} 800 L${x + 255} 855 L${x} 855 Z`) +
      d.R(x - 12, 850, 280, 42, 18, 'dark') + d.R(x - 18, 275, 171, 55, 22, 'dark') +
      d.C(x + 45, 430, 24, 'accent') + d.C(x + 95, 525, 24, 'accent') + d.C(x + 45, 620, 24, 'accent') + d.C(x + 185, 790, 24, 'accent');
    return d.E(500, 900, 400, 52, 'light') + boot(180) + boot(520) +
      drop(d, 140, 160, 0.8) + drop(d, 470, 130, 0.8) + drop(d, 860, 190, 0.8);
  });

  A.add('umbrella', 'Umbrella', { main: PU, dark: DB, light: B, accent: Y, pink: P }, d =>
    d.P('M487 515 L513 515 L513 795 Q513 875 445 875 Q385 875 385 815 L411 815 Q411 849 445 849 Q487 849 487 795 Z', 'dark') +
    d.C(500, 182, 20, 'dark') +
    d.P('M180 520 Q180 200 500 190 Q820 200 820 520 Q767 472 713 520 Q660 472 607 520 Q553 472 500 520 Q447 472 393 520 Q340 472 287 520 Q233 472 180 520 Z') +
    d.L('M500 192 Q300 290 287 518 M500 192 Q700 290 713 518') +
    d.face(500, 375, 170) +
    drop(d, 140, 200, 0.85) + drop(d, 860, 230, 0.85) + drop(d, 160, 700, 0.85) + drop(d, 840, 680, 0.85) + drop(d, 640, 860, 0.85));

  A.add('kite', 'Kite', { main: R, accent: Y, light: W, accent2: B, pink: P }, d =>
    cloud(d, 790, 230, 230, 'accent2') +
    d.L('M520 430 Q760 650 910 960') +
    d.L('M500 700 Q430 760 480 820 Q530 880 450 950') +
    bow(d, 470, 775, 0.55, 'accent2') + bow(d, 470, 890, 0.55, 'accent') +
    d.poly([[500, 140], [700, 400], [500, 400]], 'accent') + d.poly([[500, 140], [300, 400], [500, 400]], 'main') +
    d.poly([[300, 400], [500, 700], [500, 400]], 'accent') + d.poly([[700, 400], [500, 700], [500, 400]], 'main') +
    d.C(500, 410, 92, 'light') + d.face(500, 412, 120));

  A.add('blossom-tree', 'Blossom Tree', { main: LP, dark: BR, light: W, accent: Y, accent2: P, pink: P }, d =>
    d.grass(905) +
    d.P('M445 900 Q450 760 455 590 L545 590 Q550 760 555 900 Q610 905 640 925 L360 925 Q390 905 445 900 Z', 'dark') +
    d.scallop(500, 380, 190, 10, 100, 'main') +
    blossom(d, 400, 300, 60, 'light', 'accent') + blossom(d, 590, 285, 60, 'accent2', 'accent') + blossom(d, 500, 420, 60, 'light', 'accent') +
    blossom(d, 330, 470, 54, 'accent2', 'accent') + blossom(d, 670, 450, 54, 'light', 'accent') +
    d.C(180, 860, 26, 'main') + d.C(260, 880, 22, 'main') + d.C(780, 870, 24, 'main'));
})();
