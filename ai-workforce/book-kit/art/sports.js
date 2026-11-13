// "My First Sports": 30 friendly balls, sports gear and things to ride, for ages 2-5.
// Generic subjects only: no brands, logos, team marks or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', PU = '#b39ddb', T = '#4db6ac', W = '#ffffff', CREAM = '#fff3d6', GOLD = '#f6c945', LIME = '#d4e157', NAVY = '#5c6bc0';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // a capsule from x1,y1 to x2,y2 with radius r, as one closed outline
  const cap = (d, x1, y1, x2, y2, r, k = 'main') => {
    const L = Math.hypot(x2 - x1, y2 - y1), nx = -(y2 - y1) / L * r, ny = (x2 - x1) / L * r;
    return d.P(`M${f(x1 + nx)} ${f(y1 + ny)} L${f(x2 + nx)} ${f(y2 + ny)} A${r} ${r} 0 0 0 ${f(x2 - nx)} ${f(y2 - ny)} L${f(x1 - nx)} ${f(y1 - ny)} A${r} ${r} 0 0 0 ${f(x1 + nx)} ${f(y1 + ny)} Z`, k);
  };
  // thick tubes (frames, ropes, handles): every path gets a black stroke, then a
  // coloured stroke on top, so where tubes meet the joints merge cleanly
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const pent = (d, cx, cy, r, rot, k) => d.poly([0, 1, 2, 3, 4].map(i => {
    const a = (rot + i * 72) * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  }), k);
  const qpt = (p0, p1, p2, t) => [0, 1].map(i => (1 - t) * (1 - t) * p0[i] + 2 * (1 - t) * t * p1[i] + t * t * p2[i]);
  const qtan = (p0, p1, p2, t) => [0, 1].map(i => 2 * (1 - t) * (p1[i] - p0[i]) + 2 * t * (p2[i] - p1[i]));
  // a seam (quadratic curve) with short stitches across it
  const seam = (d, p0, p1, p2, n = 0, len = 18) => {
    let s = d.Lt(`M${p0} Q${p1} ${p2}`), ticks = '';
    for (let i = 1; i <= n; i++) {
      const t = i / (n + 1), [x, y] = qpt(p0, p1, p2, t), [tx, ty] = qtan(p0, p1, p2, t), L = Math.hypot(tx, ty);
      const nx = -ty / L * len, ny = tx / L * len;
      ticks += `M${f(x - nx + tx / L * 8)} ${f(y - ny + ty / L * 8)} L${f(x + nx - tx / L * 8)} ${f(y + ny - ty / L * 8)} `;
    }
    return s + (n ? d.Lt(ticks) : '');
  };
  const star = (d, cx, cy, r, k = 'accent') => d.poly([...Array(10)].map((_, i) => {
    const a = (-90 + i * 36) * Math.PI / 180, rr = i % 2 ? r * 0.45 : r; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  }), k);

  // ---------------- balls ----------------
  A.add('soccer-ball', 'Soccer Ball', { main: W, dark: '#546e7a', pink: P }, d => {
    const C = [500, 500], pts = [[500, 245, -90], [258, 425, -90], [742, 425, -90], [335, 735, -90], [665, 735, -90]];
    const links = [[0, 1], [0, 2], [1, 3], [2, 4], [3, 4]];
    let seams = links.map(([a, b]) => `M${pts[a][0]} ${pts[a][1]} L${pts[b][0]} ${pts[b][1]}`).join(' ');
    pts.forEach(([x, y]) => { const dx = x - C[0], dy = y - C[1], L = Math.hypot(dx, dy); seams += ` M${x} ${y} L${f(500 + dx / L * 325)} ${f(500 + dy / L * 325)}`; });
    return d.C(500, 500, 330) + d.Lt(seams) + pts.map(([x, y, r]) => pent(d, x, y, 66, r, 'dark')).join('') + d.face(500, 545, 230);
  });

  A.add('basketball', 'Basketball', { main: O, pink: P }, d =>
    d.C(500, 500, 330) +
    d.L('M500 170 L500 368 M178 430 Q500 330 822 430 M300 238 Q395 500 300 762 M700 238 Q605 500 700 762') +
    d.face(500, 565, 230));

  A.add('football', 'Football', { main: BR, light: W, pink: P }, d =>
    group(
      d.E(500, 500, 380, 225) +
      d.band(500, 500, 380, 225, 205, 240, 'light') + d.band(500, 500, 380, 225, 760, 795, 'light') +
      d.R(390, 360, 220, 30, 12, 'light') +
      d.Lt('M420 342 L420 408 M465 342 L465 408 M510 342 L510 408 M555 342 L555 408 M600 342 L600 408'), -18) +
    d.face(500, 555, 220));

  A.add('baseball', 'Baseball', { main: W, pink: P }, d =>
    d.C(500, 500, 320) +
    seam(d, [330, 229], [400, 500], [330, 771], 7, 15) + seam(d, [670, 229], [600, 500], [670, 771], 7, 15) +
    d.face(500, 535, 180));

  A.add('tennis-ball', 'Tennis Ball', { main: LIME, pink: P }, d =>
    d.C(500, 500, 300) +
    d.L('M330 253 Q420 500 330 747 M670 253 Q580 500 670 747') +
    d.face(500, 530, 180));

  A.add('volleyball', 'Volleyball', { main: W, accent: Y, accent2: B, pink: P }, d =>
    d.C(500, 500, 330) +
    d.L('M192 390 Q500 245 808 390 M279 255 Q500 150 721 255 M178 470 Q252 700 400 812 M822 470 Q748 700 600 812') +
    d.face(500, 560, 220));

  A.add('beach-ball', 'Beach Ball', { main: W, accent: R, accent2: B, light: Y, pink: P }, d =>
    d.C(500, 500, 320) +
    d.P('M500 180 Q80 500 500 820 Q250 500 500 180 Z', 'accent') +
    d.P('M500 180 Q920 500 500 820 Q750 500 500 180 Z', 'accent2') +
    d.E(500, 196, 52, 26, 'light') +
    d.face(500, 560, 185));

  A.add('bowling-ball', 'Bowling Ball', { main: PU, pink: P }, d =>
    d.C(500, 520, 320) +
    d.C(415, 335, 34, 'ink') + d.C(515, 315, 34, 'ink') + d.C(465, 410, 34, 'ink') +
    d.Lt('M705 330 Q760 400 765 470') +
    d.face(500, 605, 230));

  A.add('golf-ball', 'Golf Ball', { main: W, accent: R, pink: P }, d => {
    let dimples = '';
    [180, 203, 226, 249, 272, 295, 318, 341, 0].forEach(a => {
      const rr = 195, t = a * Math.PI / 180;
      dimples += `<circle cx="${f(500 + rr * Math.cos(t))}" cy="${f(420 + rr * Math.sin(t))}" r="17" fill="none" stroke="#111" stroke-width="8"/>`;
    });
    [[423, 328], [500, 300], [577, 328]].forEach(([x, y]) => { dimples += `<circle cx="${x}" cy="${y}" r="17" fill="none" stroke="#111" stroke-width="8"/>`; });
    return d.grass(905) + d.P('M410 660 L590 660 L525 712 L520 870 Q500 900 480 870 L475 712 Z', 'accent') +
      d.C(500, 420, 250) + dimples + d.face(500, 470, 210);
  });

  // ---------------- gear to hit, catch and jump ----------------
  A.add('baseball-bat', 'Baseball Bat', { main: TAN(), dark: DB, light: W, pink: P }, d =>
    group(
      d.P('M478 880 L470 620 Q440 330 448 190 Q500 110 552 190 Q560 330 530 620 L522 880 Z') +
      d.R(468, 700, 64, 150, 12, 'dark') + d.E(500, 892, 58, 22, 'dark'), 35) +
    d.C(735, 715, 145, 'light') +
    seam(d, [650, 600], [685, 715], [650, 830]) + seam(d, [820, 600], [785, 715], [820, 830]) +
    d.face(735, 735, 110));

  A.add('baseball-glove', 'Baseball Glove', { main: BR, dark: DB, light: '#e0b07a', pink: P }, d =>
    d.R(300, 190, 92, 330, 46) + d.R(397, 150, 92, 360, 46) + d.R(494, 160, 92, 350, 46) + d.R(591, 205, 92, 300, 46) +
    d.E(245, 560, 92, 175, 'main', -28) +
    d.P('M270 430 L705 430 Q735 650 645 790 L335 790 Q245 650 270 430 Z') +
    d.P('M330 460 Q490 430 650 460', 'none') +
    d.R(330, 780, 330, 95, 32, 'dark') +
    d.face(490, 590, 230));

  A.add('tennis-racket', 'Tennis Racket', { main: R, dark: NAVY, light: W, accent: LIME, pink: P }, d => {
    const cx = 450, cy = 370, rx = 160, ry = 210;
    let strings = '';
    for (let k = -3; k <= 3; k++) {
      const x = cx + k * 42, h = ry * Math.sqrt(1 - (k * 42 / rx) ** 2);
      strings += `M${x} ${f(cy - h)} L${x} ${f(cy + h)} `;
    }
    for (let k = -4; k <= 4; k++) {
      const y = cy + k * 44, w = rx * Math.sqrt(1 - (k * 44 / ry) ** 2);
      strings += `M${f(cx - w)} ${y} L${f(cx + w)} ${y} `;
    }
    return group(
      d.R(420, 600, 60, 300, 22, 'dark') + d.P('M395 560 L450 650 L505 560 L475 560 L450 600 L425 560 Z') +
      d.E(cx, cy, 205, 255) + d.E(cx, cy, rx, ry, 'light') + d.Lt(strings), -20, 450, 500) +
      d.C(765, 760, 120, 'accent') +
      d.face(765, 770, 130);
  });

  A.add('hockey-stick', 'Hockey Stick', { main: B, dark: '#455a64', light: W, accent: Y, pink: P }, d =>
    cap(d, 330, 110, 548, 712, 32) +
    d.P('M352 180 L408 160 L430 222 L374 242 Z', 'accent') +
    d.P('M512 660 L590 728 Q605 800 672 810 L838 810 Q868 812 868 845 Q868 878 838 880 L640 880 Q538 872 512 780 Z') +
    d.Lt('M700 812 L700 878 M760 812 L760 878') +
    d.P('M120 790 L120 845 Q255 905 390 845 L390 790 Z', 'dark') + d.E(255, 790, 135, 48, 'dark'));

  A.add('table-tennis', 'Table Tennis', { main: R, dark: DB, light: W, pink: P }, d =>
    d.R(408, 610, 84, 280, 30, 'dark') + d.R(392, 600, 116, 60, 20, 'dark') +
    d.C(450, 390, 255) + d.C(820, 210, 62, 'light') +
    d.face(450, 410, 240));

  A.add('shuttlecock', 'Shuttlecock', { main: W, dark: DB, accent: R, light: CREAM, pink: P }, d => {
    let top = 'M380 700 L250 232', lines = '';
    for (let k = 0; k < 6; k++) top += ` Q${f(250 + 83.3 * k + 41.7)} 180 ${f(250 + 83.3 * (k + 1))} 232`;
    top += ' L620 700 Z';
    for (let k = 1; k < 6; k++) lines += `M${f(250 + 83.3 * k)} 236 L${380 + 40 * k} 690 `;
    return d.P(top, 'light') + d.Lt(lines) + d.R(330, 360, 340, 34, 14, 'accent') +
      d.P('M385 700 L615 700 Q630 870 500 870 Q370 870 385 700 Z') +
      d.R(372, 682, 256, 44, 16, 'accent') +
      d.face(500, 775, 150);
  });

  A.add('jump-rope', 'Jump Rope', { main: R, dark: B, accent: Y, pink: P }, d =>
    tube(d, ['M300 330 C 70 980, 930 980, 700 330'], 'main', 50) +
    cap(d, 300, 110, 300, 340, 44, 'dark') + cap(d, 700, 110, 700, 340, 44, 'dark') +
    d.R(252, 300, 96, 40, 16, 'accent') + d.R(652, 300, 96, 40, 16, 'accent'));

  A.add('bowling-pin', 'Bowling Pin', { main: W, accent: R, pink: P }, d =>
    d.P('M500 120 C560 120 585 170 580 210 C576 260 545 290 545 330 C545 400 650 480 650 620 C650 760 600 840 595 880 L405 880 C400 840 350 760 350 620 C350 480 455 400 455 330 C455 290 424 260 420 210 C415 170 440 120 500 120 Z') +
    d.P('M453 338 L547 338 L552 365 L448 365 Z', 'accent') + d.P('M446 388 L554 388 L566 414 L434 414 Z', 'accent') +
    d.face(500, 630, 230));

  // ---------------- things to ride and glide ----------------
  A.add('bicycle', 'Bicycle', { main: R, dark: '#455a64', light: GR, accent: Y, pink: P }, d => {
    const wheel = (x, y) => {
      let sp = '';
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; sp += `M${x} ${y} L${f(x + 128 * Math.cos(a))} ${f(y + 128 * Math.sin(a))} `; }
      return d.C(x, y, 170, 'dark') + d.C(x, y, 132, 'light') + d.Lt(sp) + d.C(x, y, 30, 'accent');
    };
    return wheel(255, 680) + wheel(745, 680) +
      tube(d, ['M255 680 L470 690 L420 430 Z', 'M420 430 L680 440 L470 690', 'M680 440 L745 680', 'M680 440 L700 330 L620 300'], 'main', 56) +
      d.C(470, 690, 42, 'accent') + d.R(420, 760, 90, 30, 12, 'dark') +
      d.P('M335 405 Q330 360 380 360 L470 365 Q500 370 495 400 Q480 420 440 420 L360 425 Q338 425 335 405 Z', 'dark') +
      cap(d, 590, 300, 640, 300, 26, 'dark');
  });

  A.add('scooter', 'Scooter', { main: T, dark: '#455a64', light: GR, accent: Y, pink: P }, d =>
    tube(d, ['M690 720 L640 200', 'M520 200 L760 200'], 'main', 60) +
    d.C(240, 770, 95, 'dark') + d.C(240, 770, 40, 'light') + d.C(720, 770, 95, 'dark') + d.C(720, 770, 40, 'light') +
    d.P('M170 635 L640 635 Q690 635 700 690 L700 730 L190 730 Q160 730 160 700 L160 645 Q160 635 170 635 Z') +
    d.R(480, 170, 70, 60, 26, 'accent') + d.R(735, 170, 70, 60, 26, 'accent') +
    d.face(420, 668, 110));

  A.add('skateboard', 'Skateboard', { main: O, dark: '#455a64', light: GR, accent: Y, pink: P }, d =>
    d.R(255, 545, 110, 42, 12, 'dark') + d.R(635, 545, 110, 42, 12, 'dark') +
    d.C(310, 640, 66, 'accent') + d.C(310, 640, 24, 'light') + d.C(690, 640, 66, 'accent') + d.C(690, 640, 24, 'light') +
    d.P('M200 440 L800 440 Q860 440 890 380 Q905 358 922 374 Q938 395 908 444 Q860 552 790 552 L210 552 Q140 552 92 444 Q62 395 78 374 Q95 358 110 380 Q140 440 200 440 Z') +
    d.face(500, 476, 120));

  const boot = (d, k = 'main') =>
    d.P('M300 190 L560 190 L560 520 Q700 520 760 600 Q790 655 765 705 L285 705 Q262 705 262 680 L270 250 Q275 190 300 190 Z', k) +
    d.R(282, 170, 300, 60, 26, 'light') +
    d.Lt('M480 280 L540 320 M540 280 L480 320 M480 360 L540 400 M540 360 L480 400 M480 440 L540 480 M540 440 L480 480');
  A.add('roller-skate', 'Roller Skate', { main: P, dark: '#455a64', light: W, accent: Y, accent2: R, pink: '#ff8fab' }, d =>
    d.C(345, 785, 72, 'accent') + d.C(535, 785, 72, 'accent') + d.C(715, 785, 72, 'accent') +
    d.C(345, 785, 24, 'light') + d.C(535, 785, 24, 'light') + d.C(715, 785, 24, 'light') +
    d.R(262, 690, 520, 50, 18, 'dark') + d.E(800, 712, 42, 36, 'accent2') +
    boot(d) + d.face(400, 600, 160));

  A.add('ice-skate', 'Ice Skate', { main: W, dark: '#455a64', light: B, accent: GR, pink: P }, d =>
    d.R(318, 690, 56, 110, 10, 'dark') + d.R(640, 690, 56, 110, 10, 'dark') +
    d.P('M220 790 L800 790 Q868 790 862 722 Q905 752 888 805 Q870 842 800 842 L220 842 Q196 842 196 816 Q196 790 220 790 Z', 'accent') +
    boot(d) + d.face(400, 600, 160));

  A.add('sled', 'Sled', { main: R, dark: DB, light: W, accent: Y, pink: P }, d =>
    d.grass(880) +
    tube(d, ['M180 760 L780 760 Q880 760 860 660 Q845 600 800 615'], 'dark', 50) +
    d.R(270, 600, 44, 160, 10, 'dark') + d.R(640, 600, 44, 160, 10, 'dark') +
    d.L('M872 392 Q930 330 905 250') +
    d.P('M170 520 Q170 480 210 480 L690 480 Q790 480 815 405 Q832 362 866 380 Q895 398 880 445 Q842 610 720 610 L210 610 Q170 610 170 570 Z') +
    d.Lt('M330 492 L330 598 M600 492 L600 598') +
    d.face(465, 528, 125));

  A.add('surfboard', 'Surfboard', { main: B, accent: Y, light: W, pink: P }, d =>
    d.water(905) +
    d.P('M500 85 C665 250 685 640 605 860 Q500 925 395 860 C315 640 335 250 500 85 Z') +
    d.P('M405 285 L595 285 L607 335 L393 335 Z', 'accent') +
    d.P('M380 760 L620 760 L612 800 L388 800 Z', 'accent') +
    d.face(500, 535, 200));

  // ---------------- sports things ----------------
  A.add('trophy', 'Trophy', { main: GOLD, dark: DB, light: CREAM, accent: R, pink: P }, d =>
    tube(d, ['M315 260 Q170 255 180 365 Q192 460 330 470', 'M685 260 Q830 255 820 365 Q808 460 670 470'], 'main', 54) +
    d.R(455, 540, 90, 140, 12) + d.R(370, 660, 260, 60, 16, 'dark') + d.R(320, 715, 360, 110, 22, 'dark') +
    d.R(410, 745, 180, 50, 12, 'light') +
    d.P('M290 200 L710 200 Q712 520 500 565 Q288 520 290 200 Z') +
    d.E(500, 200, 210, 42, 'light') +
    star(d, 500, 105, 62, 'accent') +
    d.face(500, 355, 220));

  A.add('medal', 'Medal', { main: GOLD, dark: DB, light: CREAM, accent: B, accent2: R, pink: P }, d =>
    d.P('M330 90 L450 90 L560 470 L440 470 Z', 'accent') + d.P('M670 90 L550 90 L440 470 L560 470 Z', 'accent2') +
    d.E(500, 430, 46, 34, 'dark') +
    d.C(500, 650, 235) + d.C(500, 650, 185, 'light') +
    d.face(500, 650, 210));

  A.add('sneaker', 'Sneaker', { main: B, dark: NAVY, light: W, accent: GR, accent2: R, pink: P }, d =>
    d.P('M150 640 L870 640 Q882 640 882 662 Q882 732 820 732 L190 732 Q138 732 138 682 Q138 640 150 640 Z', 'accent') +
    d.P('M392 368 L452 300 Q492 284 510 318 L585 505 Z', 'light') +
    d.P('M180 640 L198 420 Q208 360 268 360 L405 360 L560 500 L720 520 Q838 546 850 640 Z') +
    d.P('M720 520 Q838 546 850 640 L705 640 Q700 565 720 520 Z', 'light') +
    d.P('M198 470 L262 470 L262 640 L185 640 Z', 'accent2') +
    d.Lt('M467 368 L421 421 M505 403 L459 456 M544 438 L498 491') +
    d.face(440, 565, 150));

  A.add('cap', 'Cap', { main: R, light: W, dark: DB, accent: Y, pink: P }, d =>
    d.P('M690 560 Q900 548 925 630 Q905 690 690 660 Z', 'main') +
    d.P('M220 640 Q215 300 500 290 Q785 300 780 640 Z') +
    d.L('M470 300 Q340 400 320 640 M530 300 Q660 400 680 640') +
    d.R(215, 610, 570, 50, 18, 'light') +
    d.C(500, 286, 30, 'accent') +
    d.face(500, 480, 190));

  A.add('goal', 'Goal', { main: W, light: W, dark: '#546e7a', pink: P }, d => {
    let net = '';
    for (let x = 270; x <= 730; x += 58) net += `M${x} 375 L${x} 800 `;
    for (let y = 375; y <= 800; y += 60) net += `M255 ${y} L745 ${y} `;
    const pts = [[408, 722, -90], [592, 722, -90]];
    return d.Lt(net) + d.Lt('M200 300 L255 375 M800 300 L745 375') +
      tube(d, ['M200 820 L200 300 L800 300 L800 820', 'M255 375 L745 375'], 'main', 52) +
      d.grass(870) +
      d.C(500, 750, 125) + pts.map(([x, y, r]) => pent(d, x, y, 24, r, 'dark')).join('') + d.face(500, 770, 115);
  });

  A.add('basketball-hoop', 'Basketball Hoop', { main: W, dark: '#455a64', light: W, accent: R, accent2: O, pink: P }, d =>
    d.R(470, 470, 60, 430, 12, 'dark') +
    d.R(240, 130, 520, 360, 26) +
    d.R(405, 320, 190, 140, 6, 'none') +
    d.P('M380 510 L620 510 L578 720 L422 720 Z', 'light') +
    d.Lt('M400 520 L470 715 M470 520 L410 650 M440 520 L520 715 M520 520 L440 715 M560 520 L480 715 M600 520 L530 715 M560 520 L590 650 M530 520 L580 700') +
    d.E(500, 505, 135, 32, 'accent') +
    d.face(500, 230, 170));

  function TAN() { return '#e8b27a'; }
})();
