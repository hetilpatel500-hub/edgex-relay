// "My First Christmas": 30 friendly Christmas things, for ages 2-5.
// Generic holiday subjects only: no licensed characters (no red-nosed reindeer, no
// shelf elf, no film or TV designs), no brands or logos.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', PU = '#b39ddb', W = '#ffffff', CREAM = '#fff3d6', GOLD = '#f6c945', SKIN = '#ffd9b8', ICE = '#d7f0ff', NAVY = '#5c6bc0', TAN = '#e0a96d';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // a capsule from x1,y1 to x2,y2 with radius r, as one closed outline
  const cap = (d, x1, y1, x2, y2, r, k = 'main') => {
    const L = Math.hypot(x2 - x1, y2 - y1), nx = -(y2 - y1) / L * r, ny = (x2 - x1) / L * r;
    return d.P(`M${f(x1 + nx)} ${f(y1 + ny)} L${f(x2 + nx)} ${f(y2 + ny)} A${r} ${r} 0 0 0 ${f(x2 - nx)} ${f(y2 - ny)} L${f(x1 - nx)} ${f(y1 - ny)} A${r} ${r} 0 0 0 ${f(x1 + nx)} ${f(y1 + ny)} Z`, k);
  };
  // thick tubes (antlers, handles, bands): a black stroke, then a coloured stroke on
  // top, so where tubes meet the joints merge cleanly
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const star = (d, cx, cy, r, k = 'accent') => d.poly([...Array(10)].map((_, i) => {
    const a = (-90 + i * 36) * Math.PI / 180, rr = i % 2 ? r * 0.45 : r; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  }), k);
  // a horizontal stripe across a circle between y1 and y2, following its edge
  const hband = (d, cx, cy, r, y1, y2, k) => {
    const pts = [];
    for (let i = 0; i <= 12; i++) { const y = y1 + (y2 - y1) * i / 12; pts.push([cx + Math.sqrt(r * r - (y - cy) ** 2), y]); }
    for (let i = 12; i >= 0; i--) { const y = y1 + (y2 - y1) * i / 12; pts.push([cx - Math.sqrt(r * r - (y - cy) ** 2), y]); }
    return d.poly(pts, k);
  };
  // a holly leaf along its own x axis (base left, tip right), turned by ang
  const holly = (d, cx, cy, L, w, ang, k = 'leaf') => {
    const pts = [0, 0.25, 0.5, 0.75, 1].map(t => [-L / 2 + L * t, (t === 0 || t === 1) ? 0 : w * Math.pow(Math.sin(Math.PI * t), 0.6)]);
    let p = `M${f(cx + pts[0][0])} ${cy}`;
    for (let i = 1; i < pts.length; i++) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
      p += ` Q${f(cx + (x0 + x1) / 2)} ${f(cy - (y0 + y1) / 2 * 0.45)} ${f(cx + x1)} ${f(cy - y1)}`;
    }
    for (let i = pts.length - 2; i >= 0; i--) {
      const [x0, y0] = pts[i + 1], [x1, y1] = pts[i];
      p += ` Q${f(cx + (x0 + x1) / 2)} ${f(cy + (y0 + y1) / 2 * 0.45)} ${f(cx + x1)} ${f(cy + y1)}`;
    }
    return group(d.P(p + ' Z', k) + d.Lt(`M${f(cx - L / 2 + 25)} ${cy} L${f(cx + L * 0.3)} ${cy}`), ang, cx, cy);
  };
  const flake = (d, x, y, r = 20) => d.Lt(`M${x - r} ${y} L${x + r} ${y} M${f(x - r / 2)} ${f(y - r * 0.87)} L${f(x + r / 2)} ${f(y + r * 0.87)} M${f(x - r / 2)} ${f(y + r * 0.87)} L${f(x + r / 2)} ${f(y - r * 0.87)}`);

  // ---------------- the tree and Santa ----------------
  A.add('christmas-tree', 'Christmas Tree', { main: G, dark: DB, accent: R, accent2: Y, light: B, pink: P }, d =>
    d.R(440, 790, 120, 120, 14, 'dark') +
    d.P('M500 420 L830 800 Q500 850 170 800 Z') +
    d.P('M500 280 L750 590 Q500 630 250 590 Z') +
    d.P('M500 150 L670 395 Q500 425 330 395 Z') +
    star(d, 500, 145, 85, 'accent2') +
    d.C(560, 330, 26, 'accent') + d.C(435, 360, 26, 'light') +
    d.C(345, 545, 28, 'accent2') + d.C(655, 540, 28, 'accent') + d.C(500, 495, 28, 'light') +
    d.C(262, 770, 30, 'light') + d.C(738, 770, 30, 'accent2') +
    d.face(500, 690, 210));

  A.add('santa', 'Santa', { main: R, light: W, skin: SKIN, pink: P }, d =>
    d.scallop(500, 600, 185, 12, 78, 'light') +
    d.C(500, 470, 170, 'skin') +
    d.P('M330 340 Q350 120 580 105 Q770 100 805 300 L700 360 Z', 'main') +
    d.C(805, 315, 55, 'light') +
    d.R(285, 290, 430, 95, 47, 'light') +
    d.eye(440, 455, 24) + d.eye(560, 455, 24) +
    d.C(382, 505, 22, 'pink') + d.C(618, 505, 22, 'pink') +
    d.E(445, 592, 68, 36, 'light', 12) + d.E(555, 592, 68, 36, 'light', -12) +
    d.C(500, 548, 32, 'pink') +
    d.smile(500, 668, 40, 26));

  A.add('reindeer', 'Reindeer', { main: BR, light: CREAM, dark: DB, accent: R, accent2: GOLD, antler: '#e8c99a', pink: P }, d =>
    tube(d, ['M410 300 Q360 200 300 120', 'M352 210 L250 192', 'M330 168 L382 92', 'M590 300 Q640 200 700 120', 'M648 210 L750 192', 'M670 168 L618 92'], 'antler', 60) +
    d.R(395, 640, 210, 270, 60) +
    d.E(290, 360, 85, 42, 'main', -25) + d.E(710, 360, 85, 42, 'main', 25) +
    d.E(500, 460, 200, 220) +
    d.E(500, 580, 130, 90, 'light') +
    d.E(500, 535, 46, 32, 'dark') +
    d.eye(430, 420, 26) + d.eye(570, 420, 26) +
    d.C(360, 470, 22, 'pink') + d.C(640, 470, 22, 'pink') +
    d.smile(500, 612, 40, 24) +
    d.R(340, 650, 320, 64, 32, 'accent') +
    d.C(500, 745, 45, 'accent2') + d.Lt('M470 755 L530 755'));

  A.add('snowman', 'Snowman', { main: W, accent: R, accent2: G, light: W, carrot: O, dark: '#555', pink: P }, d =>
    d.L('M330 650 L170 530 M230 575 L200 500 M670 650 L830 530 M770 575 L800 500') +
    d.C(500, 720, 200) +
    d.C(500, 680, 20, 'dark') + d.C(500, 760, 20, 'dark') + d.C(500, 840, 20, 'dark') +
    d.C(500, 410, 150) +
    d.P('M355 330 Q355 175 500 170 Q645 175 645 330 Z', 'accent2') +
    d.C(500, 165, 42, 'light') +
    d.R(335, 300, 330, 62, 31, 'light') +
    d.eye(445, 410, 22) + d.eye(555, 410, 22) +
    d.poly([[495, 438], [592, 462], [495, 482]], 'carrot') +
    d.smile(500, 508, 48, 30) +
    d.R(548, 560, 66, 170, 26, 'accent') + d.R(365, 535, 270, 60, 30, 'accent'));

  // ---------------- gifts and stockings ----------------
  A.add('gift', 'Gift', { main: R, accent: Y, pink: P }, d =>
    d.E(400, 290, 120, 70, 'accent', -25) + d.E(600, 290, 120, 70, 'accent', 25) +
    d.R(230, 470, 540, 410, 30) +
    d.R(285, 470, 70, 410, 0, 'accent') + d.R(645, 470, 70, 410, 0, 'accent') +
    d.R(200, 370, 600, 120, 30) +
    d.R(460, 370, 80, 120, 0, 'accent') +
    d.C(500, 335, 48, 'accent') +
    d.face(500, 650, 240));

  A.add('candy-cane', 'Candy Cane', { main: W, accent: R, pink: P }, d => {
    const p = 'M560 880 L560 370 Q560 160 410 160 Q270 160 270 330', c = col(d, 'main'), a = col(d, 'accent');
    return `<path d="${p}" fill="none" stroke="#111" stroke-width="172" stroke-linecap="round"/>` +
      `<path d="${p}" fill="none" stroke="${c}" stroke-width="144" stroke-linecap="round"/>` +
      `<path d="${p}" fill="none" stroke="#111" stroke-width="144" stroke-dasharray="80 80" stroke-dashoffset="-40"/>` +
      `<path d="${p}" fill="none" stroke="${a}" stroke-width="144" stroke-dasharray="60 100" stroke-dashoffset="-50"/>`;
  });

  A.add('stocking', 'Stocking', { main: R, light: W, accent: G, pink: P }, d =>
    d.P('M335 240 L635 240 L635 560 Q635 610 680 640 L775 705 Q860 765 805 840 Q745 915 640 860 L390 715 Q335 680 335 610 Z') +
    d.P('M705 660 L775 705 Q860 765 805 840 Q769 885 717 883 Q760 770 705 660 Z', 'accent') +
    d.P('M335 560 L335 610 Q335 680 390 715 L470 762 Q440 610 335 560 Z', 'accent') +
    d.R(300, 165, 370, 135, 40, 'light') +
    d.face(485, 440, 200));

  A.add('gingerbread-man', 'Gingerbread Man', { main: BR, light: W, accent: R, accent2: G, pink: P }, d =>
    cap(d, 500, 470, 230, 400, 72) + cap(d, 500, 470, 770, 400, 72) +
    cap(d, 450, 600, 360, 850, 78) + cap(d, 550, 600, 640, 850, 78) +
    d.E(500, 560, 165, 190) +
    d.C(500, 280, 150) +
    d.L('M300 352 q-16 17 0 34 q16 17 0 34 q-16 17 0 34 q16 17 0 34 M700 352 q16 17 0 34 q-16 17 0 34 q16 17 0 34 q-16 17 0 34') +
    d.L('M310 795 q17 -16 34 0 q17 16 34 0 q17 -16 34 0 q17 16 34 0 M554 795 q17 -16 34 0 q17 16 34 0 q17 -16 34 0 q17 16 34 0') +
    d.C(500, 485, 24, 'accent') + d.C(500, 570, 24, 'accent2') + d.C(500, 655, 24, 'accent') +
    d.face(500, 275, 210));

  A.add('ornament', 'Ornament', { main: B, accent: R, accent2: GOLD, light: W, pink: P }, d =>
    d.L('M465 222 Q465 120 500 120 Q535 120 535 222') +
    d.C(500, 560, 300) +
    hband(d, 500, 560, 300, 690, 770, 'accent') +
    d.C(380, 730, 16, 'light') + d.C(500, 730, 16, 'light') + d.C(620, 730, 16, 'light') +
    d.R(425, 215, 150, 70, 14, 'accent2') +
    d.face(500, 510, 230));

  A.add('jingle-bell', 'Jingle Bell', { main: GOLD, accent: R, leaf: G, pink: P }, d =>
    d.C(500, 570, 280) +
    d.L('M418 792 Q500 816 582 792') + d.dot(414, 790, 20) + d.dot(586, 790, 20) +
    holly(d, 395, 290, 220, 70, 200) + holly(d, 605, 290, 220, 70, -20) +
    d.C(468, 300, 34, 'accent') + d.C(532, 300, 34, 'accent') + d.C(500, 252, 34, 'accent') +
    d.face(500, 500, 230));

  A.add('wreath', 'Wreath', { main: G, accent: R, hole: W, pink: P }, d => {
    let s = d.scallop(500, 470, 255, 16, 82) + d.C(500, 470, 165, 'hole');
    [[-90], [200], [-20], [150], [30]].forEach(([a]) => {
      const x = 500 + 250 * Math.cos(a * Math.PI / 180), y = 470 + 250 * Math.sin(a * Math.PI / 180);
      s += d.C(f(x - 24), f(y - 10), 22, 'accent') + d.C(f(x + 24), f(y - 10), 22, 'accent') + d.C(f(x), f(y + 22), 22, 'accent');
    });
    return s +
      d.poly([[470, 760], [330, 905], [395, 890], [425, 940], [500, 790]], 'accent') +
      d.poly([[530, 760], [670, 905], [605, 890], [575, 940], [500, 790]], 'accent') +
      d.E(400, 760, 100, 60, 'accent', -20) + d.E(600, 760, 100, 60, 'accent', 20) +
      d.C(500, 770, 55, 'accent');
  });

  // ---------------- Santa's things ----------------
  A.add('santa-hat', 'Santa Hat', { main: R, light: W, pink: P }, d =>
    d.P('M215 690 C235 420 395 235 590 225 C750 218 835 320 845 470 L765 475 C745 395 700 365 650 372 C710 460 760 570 790 690 Z') +
    d.C(815, 495, 72, 'light') +
    d.R(165, 640, 670, 145, 72, 'light') +
    d.face(470, 480, 210));

  A.add('sleigh', 'Sleigh', { main: R, dark: DB, accent: GOLD, accent2: G, light: B, pink: P }, d =>
    d.R(300, 250, 170, 160, 16, 'accent2') + d.R(370, 250, 30, 160, 0, 'accent') +
    d.R(470, 290, 140, 120, 16, 'light') + d.R(525, 290, 30, 120, 0, 'accent') +
    d.R(330, 590, 40, 130, 10, 'dark') + d.R(620, 590, 40, 130, 10, 'dark') +
    d.L('M180 720 L760 720 Q870 720 870 620 Q870 560 820 560') +
    d.P('M230 390 L660 390 Q740 390 770 300 Q800 240 850 270 Q880 300 845 360 Q790 600 590 610 L300 610 Q230 610 230 540 Z') +
    d.face(470, 495, 190));

  A.add('toy-sack', 'Toy Sack', { main: TAN, dark: DB, accent: B, accent2: Y, bear: BR, light: CREAM, pink: P }, d =>
    d.R(510, 175, 170, 170, 14, 'accent') + d.R(580, 175, 30, 170, 0, 'accent2') +
    d.C(345, 195, 40, 'bear') + d.C(455, 195, 40, 'bear') + d.C(400, 265, 90, 'bear') +
    d.E(400, 292, 38, 26, 'light') + d.E(400, 282, 12, 9, 'ink') + d.eye(368, 245, 13) + d.eye(432, 245, 13) +
    d.P('M290 412 Q300 330 380 358 Q440 318 500 358 Q560 318 620 358 Q700 330 710 412 Q500 442 290 412 Z') +
    d.P('M300 400 Q160 560 210 760 Q255 900 500 900 Q745 900 790 760 Q840 560 700 400 Z') +
    d.R(295, 395, 410, 50, 25, 'dark') +
    d.face(500, 650, 230));

  A.add('chimney', 'Chimney', { main: R, light: W, roof: B, smoke: GR, pink: P }, d =>
    d.C(565, 215, 45, 'smoke') + d.C(640, 155, 55, 'smoke') + d.C(745, 110, 60, 'smoke') +
    d.R(330, 330, 340, 600, 10) +
    d.Lt('M330 430 L392 430 M330 530 L392 530 M330 630 L392 630 M362 430 L362 530 M608 470 L670 470 M608 570 L670 570 M608 670 L670 670 M638 470 L638 570') +
    d.R(300, 300, 400, 80, 16) +
    d.P('M300 322 Q300 262 360 266 Q400 232 450 262 Q500 232 550 262 Q600 232 650 266 Q700 262 700 322 Z', 'light') +
    d.P('M40 935 L40 840 L500 700 L960 840 L960 935 Z', 'roof') + d.Lt('M40 885 L960 885') +
    d.face(500, 515, 220));

  A.add('letter-to-santa', 'Letter to Santa', { main: W, env: R, env2: '#ff8a8a', accent: R, pink: P }, d =>
    d.R(270, 150, 460, 430, 20, 'main') +
    d.Lt('M330 230 L670 230 M330 295 L670 295 M330 360 L590 360') +
    d.R(170, 420, 660, 440, 30, 'env') +
    d.P('M172 452 L500 650 L828 452 L828 830 Q828 858 800 858 L200 858 Q172 858 172 830 Z', 'env2') +
    d.P('M500 702 C430 652 440 592 480 600 Q495 605 500 622 Q505 605 520 600 C560 592 570 652 500 702 Z', 'accent') +
    d.face(500, 762, 180));

  // ---------------- cozy things ----------------
  A.add('polar-bear', 'Polar Bear', { main: W, light: W, accent: R, pink: P }, d =>
    d.C(330, 225, 70) + d.C(670, 225, 70) + d.C(330, 225, 34, 'pink') + d.C(670, 225, 34, 'pink') +
    d.E(290, 620, 70, 115, 'main', 30) + d.E(710, 620, 70, 115, 'main', -30) +
    d.E(500, 680, 215, 200) +
    d.E(375, 850, 90, 62) + d.E(625, 850, 90, 62) +
    d.C(500, 360, 175) + d.E(500, 430, 85, 60, 'light') + d.E(500, 400, 26, 18, 'ink') +
    d.eye(435, 320, 22) + d.eye(565, 320, 22) + d.smile(500, 445, 32, 20) +
    d.C(390, 395, 22, 'pink') + d.C(610, 395, 22, 'pink') +
    d.R(560, 520, 70, 190, 28, 'accent') + d.R(330, 505, 340, 70, 35, 'accent'));

  A.add('snow-globe', 'Snow Globe', { main: ICE, accent: R, dark: DB, accent2: G, wood: BR, pink: P }, d =>
    d.C(500, 430, 300) +
    d.R(478, 452, 44, 60, 6, 'dark') +
    d.poly([[500, 205], [590, 335], [555, 335], [625, 460], [375, 460], [445, 335], [410, 335]], 'accent2') +
    d.L('M222 540 Q500 470 778 540') +
    flake(d, 360, 290) + flake(d, 655, 290) + flake(d, 700, 420) + flake(d, 300, 430) + flake(d, 590, 190, 16) +
    d.Lt('M262 410 Q250 300 330 225') +
    d.P('M280 700 L720 700 L800 890 L200 890 Z', 'accent') +
    d.R(240, 660, 520, 70, 35, 'wood') +
    d.face(500, 800, 150));

  A.add('gingerbread-house', 'Gingerbread House', { main: BR, light: W, accent: R, accent2: G, dark: DB, pink: P }, d =>
    d.R(630, 210, 80, 180, 8, 'dark') + d.R(615, 185, 110, 45, 22, 'light') +
    d.R(250, 440, 500, 420, 20) +
    d.P('M160 480 L500 170 L840 480 Z', 'dark') +
    d.P('M180 480' + ' q32 50 64 0'.repeat(10) + ' Z', 'light') +
    d.C(500, 300, 30, 'accent2') + d.C(420, 400, 26, 'accent') + d.C(580, 400, 26, 'accent') +
    d.P('M430 860 L430 720 Q430 650 500 650 Q570 650 570 720 L570 860 Z', 'accent') + d.dot(540, 760, 12) +
    d.C(320, 790, 40, 'accent') + d.C(680, 790, 40, 'accent') + d.Lt('M292 790 L348 790 M320 762 L320 818 M652 790 L708 790 M680 762 L680 818') +
    d.face(500, 565, 200));

  A.add('candle', 'Candle', { main: R, light: W, accent: Y, flame2: O, plate: GOLD, pink: P }, d =>
    d.L('M500 390 L500 330') +
    d.P('M500 140 Q600 260 568 315 Q540 360 500 360 Q460 360 432 315 Q400 260 500 140 Z', 'accent') +
    d.P('M500 232 Q545 292 530 316 Q517 336 500 336 Q483 336 470 316 Q455 292 500 232 Z', 'flame2') +
    d.E(500, 840, 270, 70, 'plate') +
    d.R(390, 380, 220, 460, 30) +
    d.P('M392 395 L608 395 L608 440 Q590 470 572 440 Q560 425 540 445 L540 500 Q520 530 500 500 L500 450 Q470 420 440 455 Q415 480 392 450 Z', 'light') +
    d.face(500, 625, 190));

  A.add('holly', 'Holly', { leaf: G, accent: R, pink: P }, d =>
    holly(d, 500, 300, 360, 105, -90) +
    holly(d, 320, 420, 400, 115, 200) + holly(d, 680, 420, 400, 115, -20) +
    d.C(380, 655, 80, 'accent') + d.C(620, 655, 80, 'accent') +
    d.C(500, 615, 115, 'accent') +
    d.face(500, 610, 170));

  A.add('christmas-lights', 'Christmas Lights', { b1: R, b2: Y, b3: G, dark: '#9e9e9e', pink: P }, d => {
    const bulb = (x, y, k, z = 1.15) => {
      const q = (dx, dy) => `${f(x + dx * z)} ${f(y + dy * z)}`;
      return d.P(`M${q(0, 330)} Q${q(-120, 230)} ${q(-85, 120)} Q${q(-60, 55)} ${q(0, 55)} Q${q(60, 55)} ${q(85, 120)} Q${q(120, 230)} ${q(0, 330)} Z`, k) +
        d.R(f(x - 42 * z), f(y - 5 * z), f(84 * z), f(70 * z), 12, 'dark') + d.face(x, f(y + 178 * z), 135);
    };
    return d.L('M50 330 Q275 560 500 400 Q725 240 950 420') +
      bulb(210, 444, 'b1') + bulb(500, 400, 'b2') + bulb(790, 335, 'b3');
  });

  A.add('hot-cocoa', 'Hot Cocoa', { main: R, dark: DB, light: W, pink: P }, d =>
    d.Lt('M400 300 q-35 -40 0 -80 q35 -40 0 -80 M530 300 q-35 -40 0 -80 q35 -40 0 -80') +
    tube(d, ['M640 470 Q790 470 790 600 Q790 730 640 730'], 'main', 80) +
    d.P('M230 390 L670 390 L650 780 Q645 850 575 850 L325 850 Q255 850 250 780 Z') +
    d.E(450, 395, 215, 42, 'dark') +
    d.R(355, 340, 70, 56, 12, 'light') + d.R(465, 330, 70, 56, 12, 'light') +
    d.face(450, 600, 230));

  A.add('milk-and-cookies', 'Milk & Cookies', { main: W, cookie: TAN, dark: DB, plate: B, pink: P }, d =>
    d.P('M120 290 L330 290 L310 770 Q307 800 277 800 L173 800 Q143 800 140 770 Z') +
    d.Lt('M128 380 L322 380') +
    d.E(620, 800, 300, 75, 'plate') +
    d.C(780, 670, 115, 'cookie') + d.C(820, 610, 16, 'dark') + d.C(850, 700, 16, 'dark') + d.C(790, 750, 16, 'dark') +
    d.C(590, 650, 160, 'cookie') + d.C(520, 540, 16, 'dark') + d.C(665, 545, 16, 'dark') + d.C(590, 762, 16, 'dark') +
    d.face(590, 630, 190));

  A.add('bow', 'Bow', { main: R, pink: P }, d =>
    d.poly([[470, 560], [330, 830], [395, 810], [425, 865], [500, 600]]) +
    d.poly([[530, 560], [670, 830], [605, 810], [575, 865], [500, 600]]) +
    d.P('M500 470 Q330 250 210 340 Q130 420 210 540 Q300 650 500 540 Z') +
    d.P('M500 470 Q670 250 790 340 Q870 420 790 540 Q700 650 500 540 Z') +
    d.E(500, 515, 105, 115) +
    d.face(500, 505, 150));

  A.add('nutcracker', 'Nutcracker', { main: R, dark: '#555', accent: GOLD, accent2: B, skin: SKIN, hat: NAVY, pink: P }, d =>
    d.R(395, 720, 90, 170, 20, 'accent2') + d.R(515, 720, 90, 170, 20, 'accent2') +
    d.R(375, 850, 130, 60, 30, 'dark') + d.R(495, 850, 130, 60, 30, 'dark') +
    d.R(300, 500, 80, 210, 40) + d.R(620, 500, 80, 210, 40) +
    d.R(370, 480, 260, 270, 40) +
    d.R(365, 680, 270, 50, 20, 'dark') + d.R(470, 678, 60, 54, 10, 'accent') +
    d.C(500, 560, 16, 'accent') + d.C(500, 625, 16, 'accent') +
    d.C(340, 720, 40, 'skin') + d.C(660, 720, 40, 'skin') +
    d.E(340, 490, 70, 35, 'accent') + d.E(660, 490, 70, 35, 'accent') +
    d.R(390, 300, 220, 200, 60, 'skin') +
    d.R(380, 110, 240, 200, 24, 'hat') + d.R(365, 280, 270, 46, 23, 'accent') +
    star(d, 500, 195, 50, 'accent') +
    d.face(500, 395, 170));

  A.add('christmas-sweater', 'Christmas Sweater', { main: R, accent: W, accent2: Y, tree: G, dark: DB, pink: P }, d =>
    d.poly([[420, 190], [580, 190], [690, 215], [860, 470], [770, 530], [700, 420], [700, 850], [300, 850], [300, 420], [230, 530], [140, 470], [310, 215]]) +
    d.poly([[818, 408], [860, 470], [770, 530], [730, 467]], 'accent') + d.poly([[182, 408], [140, 470], [230, 530], [270, 467]], 'accent') +
    d.R(290, 780, 420, 80, 20, 'accent') +
    d.P('M405 186 Q500 300 595 186 L555 182 Q500 245 445 182 Z', 'accent') +
    d.R(475, 590, 50, 50, 6, 'dark') +
    d.poly([[500, 330], [590, 460], [555, 460], [625, 595], [375, 595], [445, 460], [410, 460]], 'tree') +
    star(d, 500, 322, 42, 'accent2') +
    flake(d, 375, 380, 24) + flake(d, 625, 380, 24) + flake(d, 365, 690, 24) + flake(d, 635, 690, 24) +
    d.face(500, 520, 120));

  A.add('pinecone', 'Pinecone', { main: BR, leaf: G, berry: R, pink: P }, d => {
    // the cone's right edge, sampled, gives the width of each row of scales
    const cub = (a, b, c, e, t) => [0, 1].map(i => (1 - t) ** 3 * a[i] + 3 * (1 - t) ** 2 * t * b[i] + 3 * (1 - t) * t * t * c[i] + t ** 3 * e[i]);
    const edge = [];
    for (let i = 0; i <= 100; i++) edge.push(cub([500, 225], [690, 225], [735, 420], [705, 580], i / 100), cub([705, 580], [675, 740], [570, 860], [500, 870], i / 100));
    const hw = y => edge.reduce((m, p) => Math.abs(p[1] - y) < Math.abs(m[1] - y) ? p : m)[0] - 500;
    const row = (y, i) => {
      let n = Math.floor((2 * hw(y + 20) - 40) / 70); if (n % 2 !== i % 2) n -= 1;
      return n > 0 ? d.Lt(`M${500 - n * 35} ${y}` + ' q35 40 70 0'.repeat(n)) : '';
    };
    return d.P('M500 225 C690 225 735 420 705 580 C675 740 570 860 500 870 C430 860 325 740 295 580 C265 420 310 225 500 225 Z') +
      row(290, 1) + row(350, 0) + row(410, 1) + row(615, 0) + row(680, 1) + row(745, 0) + row(805, 1) +
      holly(d, 400, 215, 200, 62, 200) + holly(d, 600, 215, 200, 62, -20) +
      d.C(470, 228, 28, 'berry') + d.C(530, 228, 28, 'berry') + d.C(500, 186, 28, 'berry') +
      d.face(500, 515, 200);
  });

  A.add('earmuffs', 'Earmuffs', { main: PU, band: B, pink: P }, d =>
    tube(d, ['M255 520 Q255 170 500 170 Q745 170 745 520'], 'band', 80) +
    d.scallop(255, 580, 120, 12, 45) + d.scallop(745, 580, 120, 12, 45) +
    d.face(255, 585, 150) + d.face(745, 585, 150));

  A.add('poinsettia', 'Poinsettia', { main: R, leaf: G, accent: Y, pink: P }, d => {
    const petal = (ang, len, w, k) => group(
      d.P(`M500 500 Q${500 + len * 0.45} ${500 - w} ${500 + len} 500 Q${500 + len * 0.45} ${500 + w} 500 500 Z`, k) +
      d.Lt(`M${500 + 120} 500 L${500 + len * 0.78} 500`), ang);
    let s = '';
    for (let i = 0; i < 5; i++) s += petal(-54 + i * 72, 400, 105, 'leaf');
    for (let i = 0; i < 5; i++) s += petal(-90 + i * 72, 385, 125, 'main');
    return s + d.C(500, 500, 110, 'accent') + d.face(500, 500, 160);
  });
})();
