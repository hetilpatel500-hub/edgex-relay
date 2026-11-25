// "My First Bath & Bedtime": 30 bath-time and bedtime things for ages 2-5.
// Generic subjects only: no brands, product names or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const W = '#ffffff', P = '#ffb3c7', LP = '#ffe0ea', PU = '#c9a7ff', LPU = '#e6d9ff', Y = '#ffd23f', LY = '#fff1a8', O = '#ff9f43',
    G = '#7bd389', LG = '#c8f0cf', B = '#8fd3ff', LB = '#d4efff', BR = '#c68b59', DB = '#8d5a3b', TAN = '#e8b98a',
    GR = '#cfd8dc', NV = '#7f8ff0', MT = '#a8e6cf', R = '#ff7b8a';

  const f = v => (+v).toFixed(1);
  const g = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${f(cx)} ${f(cy)})">${s}</g>`;

  // ---------- helpers ----------
  const cheek = (d, x, y, r) => d.C(f(x), f(y), f(r), 'pink').replace('stroke-width="14"', 'stroke-width="8.4"');
  // a sleeping face: closed eyes, a small smile and rosy cheeks, centred on x,y, size s
  const sleepy = (d, x, y, s = 200) => {
    const e = s * 0.34, w = s * 0.14;
    return d.L(`M${f(x - e - w)} ${f(y)} Q${f(x - e)} ${f(y + w * 1.2)} ${f(x - e + w)} ${f(y)} M${f(x + e - w)} ${f(y)} Q${f(x + e)} ${f(y + w * 1.2)} ${f(x + e + w)} ${f(y)}`) +
      `<path d="M${f(x - s * 0.13)} ${f(y + s * 0.22)} Q${f(x)} ${f(y + s * 0.36)} ${f(x + s * 0.13)} ${f(y + s * 0.22)}" fill="none" stroke="#111" stroke-width="11.9" stroke-linecap="round"/>` +
      cheek(d, x - e - s * 0.06, y + s * 0.24, s * 0.09) + cheek(d, x + e + s * 0.06, y + s * 0.24, s * 0.09);
  };
  // a five-point star centred on x,y, outer radius r
  const star = (d, x, y, r, k = 'accent', rot = 0) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const t = (i * 36 - 90 + rot) * Math.PI / 180, rr = i % 2 ? r * 0.5 : r;
      pts.push([x + Math.cos(t) * rr, y + Math.sin(t) * rr]);
    }
    return d.poly(pts, k);
  };
  // a crescent moon: tips at x,y-r and x,y+r, bulging to the left
  const moonP = (x, y, r) =>
    `M${f(x)} ${f(y - r)} C${f(x - 1.35 * r)} ${f(y - r)} ${f(x - 1.35 * r)} ${f(y + r)} ${f(x)} ${f(y + r)} ` +
    `C${f(x - 0.45 * r)} ${f(y + 0.62 * r)} ${f(x - 0.45 * r)} ${f(y - 0.62 * r)} ${f(x)} ${f(y - r)} Z`;
  const moon = (d, x, y, r, k = 'accent') => d.P(moonP(x, y, r), k);
  // a puffy cloud w wide, centred on cx,cy
  const cloud = (d, cx, cy, w, k = 'light') => {
    const p = (x, y) => `${f(cx + x * w)} ${f(cy + y * w)}`;
    return d.P(`M${p(-0.46, 0.19)} A1 1 0 0 1 ${p(-0.33, -0.05)} A1 1 0 0 1 ${p(-0.02, -0.28)} A1 1 0 0 1 ${p(0.3, -0.1)} A1 1 0 0 1 ${p(0.46, 0.19)} Q${p(0, 0.27)} ${p(-0.46, 0.19)} Z`, k);
  };
  // a "Z" of size s with its top-left corner at x,y
  const zed = (d, x, y, s) => d.L(`M${f(x)} ${f(y)} L${f(x + s)} ${f(y)} L${f(x)} ${f(y + s)} L${f(x + s)} ${f(y + s)}`);
  const zzz = (d, x, y, s = 60) => zed(d, x, y, s) + zed(d, x + s * 1.1, y - s * 1.1, s * 0.8) + zed(d, x + s * 2.05, y - s * 2.0, s * 0.6);
  // a heart centred on x,y, half-width w
  const heart = (d, x, y, w, k = 'accent') =>
    d.P(`M${f(x)} ${f(y + 0.95 * w)} C${f(x - 0.4 * w)} ${f(y + 0.6 * w)} ${f(x - 1.05 * w)} ${f(y + 0.15 * w)} ${f(x - 0.95 * w)} ${f(y - 0.35 * w)} ` +
      `C${f(x - 0.85 * w)} ${f(y - 0.85 * w)} ${f(x - 0.15 * w)} ${f(y - 0.9 * w)} ${f(x)} ${f(y - 0.35 * w)} ` +
      `C${f(x + 0.15 * w)} ${f(y - 0.9 * w)} ${f(x + 0.85 * w)} ${f(y - 0.85 * w)} ${f(x + 0.95 * w)} ${f(y - 0.35 * w)} ` +
      `C${f(x + 1.05 * w)} ${f(y + 0.15 * w)} ${f(x + 0.4 * w)} ${f(y + 0.6 * w)} ${f(x)} ${f(y + 0.95 * w)} Z`, k);
  // a music note with its head at x,y
  const note = (d, x, y, s = 1) =>
    d.L(`M${f(x + 26 * s)} ${f(y - 4 * s)} L${f(x + 26 * s)} ${f(y - 120 * s)} Q${f(x + 70 * s)} ${f(y - 100 * s)} ${f(x + 78 * s)} ${f(y - 60 * s)}`) +
    d.E(f(x), f(y), f(32 * s), f(23 * s), 'ink', -20);
  // bubbles: [x, y, r] list
  const bubbles = (d, list, k = 'light') => list.map(([x, y, r]) => d.C(x, y, r, k)).join('');

  // ---------------- Bath time ----------------
  A.add('bathtub', 'Bubble Bath', { main: B, dark: GR, light: W, accent: Y, pink: P }, d =>
    d.L('M80 885 L920 885') +
    d.R(198, 250, 40, 205, 18, 'dark') + d.P('M218 262 Q218 205 280 205 L345 205 L345 250 L282 250 Q262 250 262 262 Z', 'dark') +
    d.E(280, 838, 44, 52, 'dark') + d.E(720, 838, 44, 52, 'dark') +
    bubbles(d, [[392, 415, 62], [492, 385, 78], [600, 410, 66], [700, 420, 52], [320, 300, 30], [660, 290, 38], [780, 230, 26]]) +
    d.P('M150 470 L850 470 Q850 760 680 800 L320 800 Q150 760 150 470 Z') +
    d.R(120, 438, 760, 64, 32, 'light') +
    d.face(500, 610, 170));

  A.add('soap', 'Soap', { main: P, dark: B, light: W, accent: Y, pink: R }, d =>
    d.P('M190 760 Q500 840 810 760 L780 700 L220 700 Z', 'dark') +
    bubbles(d, [[320, 430, 72], [440, 360, 56], [690, 400, 84], [565, 300, 46], [790, 270, 36], [230, 320, 30]]) +
    d.R(250, 450, 500, 290, 95) +
    d.face(500, 585, 185));

  A.add('sponge', 'Sponge', { main: Y, dark: O, light: LY, accent: B, pink: P }, d =>
    bubbles(d, [[230, 255, 44], [790, 240, 56], [835, 410, 32], [180, 420, 26]], 'accent') +
    d.R(250, 300, 500, 440, 70) +
    d.E(330, 372, 26, 18, 'light') + d.E(665, 382, 30, 20, 'light') + d.E(330, 655, 28, 19, 'light') +
    d.E(670, 660, 25, 17, 'light') + d.E(500, 690, 22, 15, 'light') + d.E(410, 350, 16, 11, 'light') + d.E(590, 345, 16, 11, 'light') +
    d.face(500, 515, 190));

  A.add('towel', 'Towel', { main: MT, dark: BR, light: W, accent: B, accent2: Y, pink: P }, d =>
    d.R(170, 195, 34, 105, 12, 'dark') + d.R(796, 195, 34, 105, 12, 'dark') +
    d.R(150, 228, 700, 40, 20, 'dark') +
    d.R(280, 240, 440, 620, 34) +
    d.R(280, 680, 440, 56, 0, 'accent') + d.R(280, 760, 440, 30, 0, 'accent2') +
    d.R(270, 222, 460, 120, 30, 'light') +
    d.Lt('M320 870 L320 900 M380 870 L380 900 M440 870 L440 900 M500 870 L500 900 M560 870 L560 900 M620 870 L620 900 M680 870 L680 900') +
    d.face(500, 480, 170));

  A.add('shampoo', 'Shampoo', { main: PU, dark: NV, light: W, accent: LB, pink: P }, d =>
    bubbles(d, [[230, 300, 46], [770, 255, 62], [810, 430, 36], [205, 480, 30], [700, 160, 26]], 'accent') +
    d.R(415, 250, 170, 125, 22, 'dark') + d.R(460, 200, 80, 60, 14, 'dark') +
    d.R(320, 360, 360, 510, 80) +
    d.R(375, 500, 250, 230, 46, 'light') +
    d.face(500, 595, 165));

  A.add('toothbrush', 'Toothbrush', { main: G, dark: B, light: W, accent: LB, pink: P }, d =>
    g(d.R(120, 545, 620, 80, 40) +
      d.R(690, 430, 210, 70, 14, 'light') +
      d.Lt('M725 440 L725 492 M765 440 L765 492 M805 440 L805 492 M845 440 L845 492 M880 440 L880 492') +
      d.R(680, 495, 230, 110, 40) +
      d.P('M690 432 Q700 360 760 380 Q790 330 830 372 Q880 350 900 432 Z', 'accent') +
      d.C(250, 585, 22, 'dark') + d.C(330, 585, 22, 'dark'), -18) +
    star(d, 230, 230, 55, 'dark') + star(d, 820, 790, 45, 'dark'));

  A.add('toothpaste', 'Toothpaste', { main: LB, dark: B, light: W, accent: G, pink: P }, d =>
    d.P('M250 395 L700 420 L700 600 L250 625 Q228 510 250 395 Z') +
    d.R(195, 380, 70, 260, 14, 'dark') + d.Lt('M212 410 L212 610 M245 410 L245 610') +
    d.R(698, 455, 70, 110, 12, 'light') + d.R(765, 440, 105, 140, 28, 'dark') +
    d.P('M330 455 L640 470 L640 560 L330 575 Z', 'accent') +
    d.face(480, 495, 150) +
    star(d, 520, 250, 55, 'dark') + star(d, 760, 770, 45, 'dark') + star(d, 270, 780, 40, 'dark'));

  A.add('hairbrush', 'Hairbrush', { main: P, dark: DB, light: W, accent: Y, pink: R }, d =>
    d.R(450, 540, 100, 350, 50) +
    d.E(500, 360, 210, 240) + d.E(500, 352, 158, 185, 'light') +
    [[-100, -110], [0, -130], [100, -110], [-120, -20], [-40, -20], [40, -20], [120, -20], [-100, 70], [0, 80], [100, 70], [-50, 150], [50, 150], [-60, -80], [60, -80]]
      .map(([u, v]) => d.dot(500 + u, 352 + v, 14)).join('') +
    heart(d, 500, 720, 34, 'accent'));

  A.add('bathrobe', 'Bathrobe', { main: LB, dark: B, light: W, accent: Y, pink: P }, d =>
    d.P('M330 230 L240 290 L120 520 L215 565 L300 430 L300 870 L700 870 L700 430 L785 565 L880 520 L760 290 L670 230 Z') +
    d.P('M330 230 L500 600 L560 560 L420 230 Z', 'light') +
    d.P('M670 230 L500 640 L440 600 L580 230 Z', 'light') +
    d.R(298, 600, 404, 52, 18, 'accent') +
    d.P('M488 640 L440 790 L480 795 L505 650 Z', 'accent') + d.P('M512 640 L560 790 L520 795 L495 650 Z', 'accent') +
    d.C(500, 626, 34, 'accent') +
    d.R(570, 700, 100, 95, 18, 'light') + heart(d, 620, 748, 26, 'dark'));

  // ---------------- Getting ready for bed ----------------
  A.add('pajamas', 'Pajamas', { main: B, dark: NV, light: W, accent: Y, pink: P }, d =>
    d.P('M330 545 L670 545 L700 900 L540 900 L500 650 L460 900 L300 900 Z') +
    d.R(325, 530, 350, 42, 14, 'light') +
    d.P('M380 160 L250 210 L150 380 L240 430 L300 340 L300 520 L700 520 L700 340 L760 430 L850 380 L750 210 L620 160 Q500 235 380 160 Z') +
    d.C(500, 300, 15, 'light') + d.C(500, 380, 15, 'light') + d.C(500, 460, 15, 'light') +
    star(d, 390, 330, 38) + moon(d, 640, 420, 42) + star(d, 620, 280, 26) + star(d, 380, 450, 26) +
    star(d, 410, 700, 32) + star(d, 600, 760, 32) + moon(d, 580, 640, 34));

  A.add('nightgown', 'Nightgown', { main: LPU, dark: PU, light: W, accent: P, pink: P }, d => {
    let ruffle = '';
    for (let i = 0; i < 8; i++) ruffle += d.C(355 + i * 41.5, 842, 34, 'light');
    return ruffle +
      d.P('M400 180 L320 220 L270 330 L345 365 L382 300 L345 840 Q500 870 655 840 L618 300 L655 365 L730 330 L680 220 L600 180 Q500 250 400 180 Z') +
      d.P('M455 222 Q470 190 500 222 Q530 190 545 222 Q520 262 500 248 Q480 262 455 222 Z', 'accent') +
      heart(d, 430, 470, 30, 'accent') + star(d, 570, 560, 34, 'light') + heart(d, 450, 680, 30, 'accent') + star(d, 580, 760, 30, 'light');
  });

  A.add('slippers', 'Slippers', { main: P, dark: DB, light: W, accent: PU, pink: R }, d => {
    // top view: an oval sole, the toe covered by a rounded upper with a face and a pom-pom
    const slip = (x, y, rot) => g(
      d.E(x, y, 125, 250, 'dark') + d.E(x, y + 25, 92, 200, 'light') +
      d.P(`M${x - 125} ${y - 10} Q${x - 132} ${y - 255} ${x} ${y - 255} Q${x + 132} ${y - 255} ${x + 125} ${y - 10} Q${x} ${y + 40} ${x - 125} ${y - 10} Z`) +
      d.face(x, y - 135, 120) + d.C(x, y + 2, 40, 'accent'), rot, x, y);
    return slip(320, 520, -8) + slip(680, 520, 8);
  });

  A.add('bed', 'Bed', { main: B, dark: BR, light: W, accent: Y, pink: P }, d =>
    d.L('M60 880 L940 880') +
    d.R(150, 300, 120, 580, 50, 'dark') + d.R(770, 500, 90, 380, 40, 'dark') +
    d.R(200, 590, 640, 130, 30, 'light') +
    d.E(330, 560, 110, 60, 'light') + sleepy(d, 330, 548, 120) +
    d.P('M420 560 L840 560 L840 740 Q630 775 420 740 Z') + d.R(420, 545, 420, 60, 26, 'light') +
    star(d, 560, 670, 34) + star(d, 720, 690, 30) +
    moon(d, 700, 300, 90) + star(d, 520, 200, 42) + star(d, 860, 170, 32));

  A.add('bunk-bed', 'Bunk Bed', { main: PU, dark: BR, light: W, accent: Y, accent2: MT, pink: P }, d =>
    d.L('M60 890 L940 890') +
    d.R(225, 375, 550, 75, 20, 'light') + d.E(310, 352, 64, 36, 'light') + d.R(400, 345, 375, 70, 26) +
    d.R(225, 715, 550, 75, 20, 'light') + d.E(310, 692, 64, 36, 'light') + d.R(400, 685, 375, 70, 26, 'accent2') +
    d.R(225, 262, 550, 30, 14, 'dark') + d.R(225, 450, 550, 34, 14, 'dark') + d.R(225, 790, 550, 34, 14, 'dark') +
    d.R(632, 484, 24, 230, 10, 'dark') + d.R(712, 484, 24, 230, 10, 'dark') +
    d.R(640, 540, 90, 20, 8, 'dark') + d.R(640, 620, 90, 20, 8, 'dark') +
    d.R(190, 200, 55, 690, 24, 'dark') + d.R(755, 200, 55, 690, 24, 'dark') +
    star(d, 500, 160, 46));

  A.add('crib', 'Crib', { main: LB, dark: BR, light: W, accent: Y, pink: P }, d => {
    let slats = '';
    for (let x = 235; x <= 745; x += 68) slats += d.R(x, 365, 34, 345, 16, 'light');
    return d.L('M60 890 L940 890') + slats +
      d.R(170, 335, 660, 44, 22) + d.R(170, 700, 660, 44, 22) +
      d.R(145, 270, 56, 620, 28) + d.R(799, 270, 56, 620, 28) +
      d.C(173, 262, 36, 'accent') + d.C(827, 262, 36, 'accent') +
      heart(d, 500, 790, 40, 'accent') + star(d, 330, 180, 42) + moon(d, 690, 180, 70);
  });

  A.add('pillow', 'Pillow', { main: LPU, dark: PU, light: W, accent: Y, pink: P }, d =>
    d.P('M210 340 Q500 280 790 340 Q845 520 790 690 Q500 745 210 690 Q155 520 210 340 Z') +
    d.Lt('M232 362 Q500 308 768 362 Q815 520 768 668 Q500 718 232 668 Q185 520 232 362 Z') +
    sleepy(d, 500, 500, 230) + zzz(d, 690, 200, 54));

  A.add('blanket', 'Blanket', { main: B, dark: NV, light: W, accent: Y, accent2: P, pink: P }, d => {
    let s = d.R(190, 250, 620, 540, 46, 'light');
    const ks = [['main', 'light', 'accent2'], ['light', 'accent', 'light'], ['accent2', 'light', 'main']];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) s += d.R(225 + c * 185, 285 + r * 160, 180, 150, 22, ks[r][c]);
    return d.R(160, 780, 680, 70, 30, 'dark') + s +
      heart(d, 500, 518, 46, 'accent2') + star(d, 315, 360, 44, 'accent') + star(d, 685, 680, 44, 'accent') +
      moon(d, 345, 680, 52, 'accent') + moon(d, 715, 362, 52, 'accent');
  });

  // ---------------- Night-time things ----------------
  A.add('moon', 'Moon', { main: Y, dark: NV, light: LY, accent: LY, pink: P }, d =>
    star(d, 790, 280, 62) + star(d, 820, 640, 46) + star(d, 140, 230, 40) + star(d, 680, 860, 36) +
    moon(d, 590, 500, 330, 'main') + sleepy(d, 344, 500, 150) +
    d.P('M590 170 Q660 70 760 90 Q700 150 690 210 Q640 160 590 170 Z', 'dark') + d.C(770, 92, 30, 'light'));

  A.add('stars', 'Stars', { main: Y, dark: O, light: LY, accent: LY, pink: P }, d =>
    star(d, 500, 460, 250, 'main') + d.face(500, 485, 165) +
    star(d, 190, 790, 110, 'main', 10) + d.face(190, 805, 72) +
    star(d, 810, 790, 110, 'main', -10) + d.face(810, 805, 72) +
    star(d, 150, 170, 40, 'light') + star(d, 860, 180, 46, 'light'));

  A.add('night-light', 'Night Light', { main: LY, dark: PU, light: W, accent: Y, pink: P }, d =>
    d.L('M215 300 L150 260 M195 420 L120 420 M785 300 L850 260 M805 420 L880 420 M230 540 L170 590 M770 540 L830 590') +
    d.R(470, 520, 60, 200, 14, 'dark') + d.R(340, 700, 320, 90, 44, 'dark') +
    d.poly([[345, 230], [655, 230], [745, 530], [255, 530]]) +
    d.face(500, 375, 165) + star(d, 360, 480, 26, 'accent') + star(d, 640, 480, 26, 'accent'));

  A.add('alarm-clock', 'Alarm Clock', { main: R, dark: DB, light: W, accent: Y, pink: P }, d =>
    d.R(335, 760, 50, 115, 22, 'dark') + d.R(615, 760, 50, 115, 22, 'dark') +
    d.C(300, 245, 85, 'accent') + d.C(700, 245, 85, 'accent') + d.R(488, 175, 24, 60, 8, 'dark') + d.C(500, 168, 26, 'dark') +
    d.C(500, 530, 305) + d.C(500, 530, 235, 'light') +
    d.L('M500 318 L500 352 M500 708 L500 742 M288 530 L322 530 M678 530 L712 530') +
    d.L('M500 530 L500 385 M500 530 L615 585') + d.C(500, 530, 20, 'dark'));

  A.add('bedtime-story', 'Bedtime Story', { main: PU, dark: NV, light: W, accent: Y, pink: P }, d =>
    d.P('M500 400 Q340 340 140 380 L140 820 Q340 780 500 840 Q660 780 860 820 L860 380 Q660 340 500 400 Z') +
    d.P('M500 380 Q350 318 175 352 L175 790 Q350 752 500 810 Z', 'light') +
    d.P('M500 380 Q650 318 825 352 L825 790 Q650 752 500 810 Z', 'light') +
    moon(d, 360, 500, 85) + d.Lt('M230 640 L440 650 M230 700 L440 712') +
    star(d, 660, 500, 70) + d.Lt('M560 650 L770 640 M560 712 L770 700') +
    moon(d, 590, 200, 70) + star(d, 360, 190, 40) + star(d, 780, 220, 34));

  A.add('warm-milk', 'Warm Milk', { main: LB, dark: B, light: W, accent: Y, pink: P }, d =>
    d.E(470, 815, 260, 44, 'dark') +
    d.P('M620 470 Q800 470 800 595 Q800 720 620 720 L620 655 Q735 655 735 595 Q735 535 620 535 Z') +
    d.R(300, 380, 340, 430, 64) + d.E(470, 395, 165, 42, 'light') +
    d.face(470, 600, 180) +
    d.L('M400 320 Q370 270 405 230 Q440 190 405 140 M480 310 Q450 260 485 220 Q520 180 485 130 M560 320 Q530 270 565 230 Q600 190 565 140'));

  A.add('baby-mobile', 'Baby Mobile', { main: Y, dark: BR, light: LB, accent: P, pink: P }, d =>
    d.L('M500 130 L500 245 M215 330 Q500 190 785 330 M235 318 L235 520 M400 265 L400 560 M600 265 L600 545 M765 318 L765 500') +
    d.C(500, 120, 22, 'dark') +
    star(d, 235, 590, 88) + cloud(d, 400, 650, 270, 'light') + moon(d, 650, 650, 115, 'main') + heart(d, 765, 570, 72, 'accent') +
    sleepy(d, 400, 655, 100));

  A.add('music-box', 'Music Box', { main: MT, dark: BR, light: W, accent: P, pink: P }, d =>
    note(d, 300, 300, 1) + note(d, 480, 230, 1.1) + note(d, 660, 290, 0.95) +
    d.R(760, 580, 70, 32, 12, 'dark') + d.R(812, 515, 32, 130, 14, 'dark') + d.C(828, 512, 28, 'accent') +
    d.R(240, 440, 520, 400, 44) + d.R(215, 395, 570, 100, 34, 'dark') +
    d.R(300, 560, 400, 210, 30, 'light') + heart(d, 500, 665, 62, 'accent'));

  A.add('rocking-chair', 'Rocking Chair', { main: TAN, dark: BR, light: P, accent: Y, pink: P }, d =>
    d.P('M150 800 Q500 905 850 800 L860 840 Q500 950 140 840 Z', 'dark') +
    d.R(245, 190, 110, 660, 46) + heart(d, 300, 300, 34, 'accent') +
    d.R(615, 590, 55, 245, 22) +
    d.R(250, 560, 450, 64, 26) + d.R(345, 515, 330, 58, 28, 'light') +
    d.R(605, 460, 44, 110, 18, 'dark') + d.R(300, 425, 395, 46, 22, 'dark'));

  // ---------------- Sleepy friends ----------------
  A.add('sleepy-bear', 'Bedtime Bear', { main: TAN, dark: BR, light: CR(), accent: B, accent2: Y, pink: P }, d =>
    d.E(385, 875, 78, 42) + d.E(615, 875, 78, 42) +
    d.E(500, 690, 205, 200) + d.E(500, 725, 115, 115, 'light') +
    d.E(315, 640, 55, 105, 'main', 25) + d.E(685, 640, 55, 105, 'main', -25) +
    d.C(500, 370, 170) + d.E(500, 430, 74, 54, 'light') + d.E(500, 410, 24, 16, 'ink') +
    sleepy(d, 500, 360, 160) +
    d.P('M345 285 Q460 70 730 120 Q815 140 820 270 Q735 205 655 262 Z', 'accent') +
    d.R(330, 255, 340, 54, 27, 'light') + d.C(822, 290, 42, 'accent2') +
    zzz(d, 120, 270, 50));

  A.add('counting-sheep', 'Counting Sheep', { main: W, dark: DB, light: LY, accent: Y, pink: P }, d =>
    star(d, 160, 190, 44) + moon(d, 880, 220, 80, 'accent') +
    d.R(245, 610, 42, 270, 12, 'dark') + d.R(713, 610, 42, 270, 12, 'dark') +
    d.R(195, 670, 610, 38, 14, 'dark') + d.R(195, 770, 610, 38, 14, 'dark') +
    d.L('M80 880 L920 880') +
    d.R(370, 460, 32, 165, 16, 'dark') + d.R(430, 470, 32, 155, 16, 'dark') +
    d.R(555, 455, 32, 160, 16, 'dark') + d.R(612, 445, 32, 160, 16, 'dark') +
    d.scallop(490, 400, 95, 9, 58) + d.E(490, 400, 140, 95) +
    d.E(640, 270, 40, 20, 'light', -30) + d.E(765, 290, 40, 20, 'light', 45) +
    d.E(700, 345, 88, 102, 'light', 15) + sleepy(d, 703, 352, 112));

  A.add('sleepy-kitty', 'Sleepy Kitty', { main: O, dark: DB, light: LB, accent: Y, pink: P }, d =>
    d.R(160, 700, 680, 150, 70, 'light') + d.Lt('M200 775 L800 775') +
    d.E(530, 640, 270, 140) +
    d.P('M780 640 Q860 790 640 785 Q520 782 515 740 Q570 752 640 748 Q790 740 735 660 Z') +
    d.poly([[232, 505], [252, 395], [325, 455]]) + d.poly([[360, 448], [425, 395], [430, 505]]) +
    d.poly([[250, 480], [260, 425], [300, 458]], 'pink') + d.poly([[378, 455], [412, 428], [413, 478]], 'pink') +
    d.C(330, 570, 125) + sleepy(d, 330, 570, 135) + d.E(330, 590, 14, 10, 'pink') +
    d.Lt('M200 585 L150 570 M200 610 L150 618 M460 585 L510 570 M460 610 L510 618') +
    zzz(d, 650, 360, 52));

  A.add('sweet-dreams', 'Sweet Dreams', { main: LB, dark: NV, light: W, accent: Y, pink: P }, d =>
    cloud(d, 500, 560, 740, 'main') + sleepy(d, 500, 560, 230) +
    zzz(d, 640, 250, 64) + star(d, 200, 230, 54) + star(d, 140, 820, 40) + star(d, 860, 830, 46) + moon(d, 420, 220, 70));

  function CR() { return '#fff4e6'; }
})();
