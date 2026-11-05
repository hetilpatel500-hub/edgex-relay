// "My First Music": 30 friendly instruments and music things for ages 2-5.
// Generic subjects only: no brands, logos or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', BR = '#c68b59', DB = '#8d5a3b',
    TAN = '#e8b27a', GR = '#cfd8dc', PU = '#b39ddb', T = '#4db6ac', W = '#ffffff', CREAM = '#fff3d6', GOLD = '#f6c945';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // a capsule (stick, tube, handle) from x1,y1 to x2,y2 with radius r, as one closed outline
  const cap = (d, x1, y1, x2, y2, r, k = 'main') => {
    const L = Math.hypot(x2 - x1, y2 - y1), nx = -(y2 - y1) / L * r, ny = (x2 - x1) / L * r;
    return d.P(`M${f(x1 + nx)} ${f(y1 + ny)} L${f(x2 + nx)} ${f(y2 + ny)} A${r} ${r} 0 0 0 ${f(x2 - nx)} ${f(y2 - ny)} L${f(x1 - nx)} ${f(y1 - ny)} A${r} ${r} 0 0 0 ${f(x1 + nx)} ${f(y1 + ny)} Z`, k);
  };
  // a drumstick or mallet: a stick with a ball at the far end
  const mallet = (d, x1, y1, x2, y2, k = 'dark', ball = 'accent') => cap(d, x1, y1, x2, y2, 16, k) + d.C(x2, y2, 42, ball);
  // a single music note: a tilted oval head, a stem and a flag; s = 1 is about 170 tall
  const note = (d, x, y, s = 1, k = 'main') =>
    d.P(`M${f(x + 34 * s)} ${f(y)} L${f(x + 34 * s)} ${f(y - 150 * s)} Q${f(x + 70 * s)} ${f(y - 120 * s)} ${f(x + 92 * s)} ${f(y - 70 * s)} Q${f(x + 70 * s)} ${f(y - 95 * s)} ${f(x + 54 * s)} ${f(y - 98 * s)} L${f(x + 54 * s)} ${f(y)} Z`, k) +
    d.E(x, y, 46 * s, 33 * s, k, -22);
  const heart = (d, cx, cy, s, k = 'main') =>
    d.P(`M${cx} ${f(cy + s * 0.9)} C${f(cx - s * 1.4)} ${cy} ${f(cx - s * 0.9)} ${f(cy - s * 1.1)} ${cx} ${f(cy - s * 0.45)} C${f(cx + s * 0.9)} ${f(cy - s * 1.1)} ${f(cx + s * 1.4)} ${cy} ${cx} ${f(cy + s * 0.9)} Z`, k);
  // an unstroked patch in a fill colour: hides lines left inside a shape built from overlapping parts
  const patch = (d, cx, cy, r, k = 'main') => d.scallop(cx, cy, r, 0, 0, k);
  // guitar-like body: two overlapping round bouts with the inner arcs hidden
  // The patch is centred a little below where the two circles cross and reaches
  // just short of the crossing points, so it hides both inner arcs but not the waist.
  const bouts = (d, x, yTop, rTop, yBot, rBot, k = 'main') => {
    const D = yBot - yTop, a = (D * D + rTop * rTop - rBot * rBot) / (2 * D), h = Math.sqrt(rTop * rTop - a * a);
    const yi = yTop + a, yc = yi + 0.4 * h, r = Math.hypot(h, yc - yi) - 10;
    return d.C(x, yTop, rTop, k) + d.C(x, yBot, rBot, k) + patch(d, x, f(yc), f(r), k);
  };

  // ---------------- instruments ----------------
  A.add('drum', 'Drum', { main: R, light: CREAM, accent: Y, dark: DB, pink: P }, d =>
    mallet(d, 640, 420, 830, 170, 'dark', 'accent') + mallet(d, 360, 420, 170, 170, 'dark', 'accent') +
    d.P('M220 430 L220 790 Q500 880 780 790 L780 430 Z') +
    d.P('M220 750 Q500 840 780 750 L780 800 Q500 890 220 800 Z', 'accent') +
    d.P('M220 430 Q500 520 780 430 L780 485 Q500 575 220 485 Z', 'accent') +
    d.E(500, 430, 280, 85, 'light') +
    d.face(500, 650, 230));

  A.add('guitar', 'Guitar', { main: O, dark: DB, light: CREAM, accent: Y, pink: P }, d =>
    d.R(468, 110, 64, 360, 12, 'dark') + d.R(440, 60, 120, 110, 24, 'dark') +
    d.C(425, 85, 18, 'accent') + d.C(425, 140, 18, 'accent') + d.C(575, 85, 18, 'accent') + d.C(575, 140, 18, 'accent') +
    d.Lt('M486 170 L486 380 M500 170 L500 380 M514 170 L514 380') +
    bouts(d, 500, 490, 160, 700, 215) +
    d.C(500, 555, 58, 'dark') +
    d.R(420, 840, 160, 34, 14, 'dark') +
    d.face(500, 715, 210));

  A.add('piano', 'Piano', { main: R, dark: DB, light: W, accent: Y, pink: P }, d => {
    let keys = '';
    for (let i = 1; i < 10; i++) keys += `M${200 + i * 60} 600 L${200 + i * 60} 720 `;
    let black = '';
    [0, 1, 3, 4, 5, 7, 8].forEach(i => { black += d.R(242 + i * 60, 600, 36, 70, 6, 'ink'); });
    return d.R(220, 780, 60, 120, 14, 'dark') + d.R(720, 780, 60, 120, 14, 'dark') +
      d.R(170, 260, 660, 540, 34) + d.R(150, 230, 700, 60, 24, 'dark') +
      d.R(200, 600, 600, 120, 10, 'light') + d.Lt(keys) + black +
      d.R(360, 330, 280, 60, 14, 'accent') + d.face(500, 480, 200);
  });

  A.add('trumpet', 'Trumpet', { main: GOLD, light: CREAM, accent: O, dark: DB, pink: P }, d =>
    d.P('M270 470 L270 590 Q270 640 320 640 L560 640 Q610 640 610 590 L610 470 L570 470 L570 580 Q570 600 550 600 L330 600 Q310 600 310 580 L310 470 Z') +
    d.R(130, 435, 90, 40, 18, 'dark') + d.R(200, 425, 420, 60, 30) +
    d.R(330, 330, 44, 110, 12, 'light') + d.R(400, 330, 44, 110, 12, 'light') + d.R(470, 330, 44, 110, 12, 'light') +
    d.C(352, 320, 30, 'accent') + d.C(422, 320, 30, 'accent') + d.C(492, 320, 30, 'accent') +
    d.P('M590 420 L840 300 Q900 455 840 610 L590 490 Z') + d.E(850, 455, 45, 155, 'light') +
    d.face(705, 455, 140));

  A.add('violin', 'Violin', { main: BR, dark: DB, light: CREAM, accent: Y, pink: P }, d =>
    cap(d, 150, 800, 760, 170, 12, 'light') + d.R(735, 150, 40, 70, 12, 'dark', 0) +
    group(
      d.R(478, 120, 44, 330, 10, 'dark') + d.C(500, 105, 42, 'dark') + d.C(500, 105, 18, 'accent') +
      bouts(d, 500, 500, 150, 690, 185) +
      d.P('M375 590 Q350 595 352 620 Q355 645 378 640 Z', 'light') + d.P('M625 590 Q650 595 648 620 Q645 645 622 640 Z', 'light') +
      d.R(445, 790, 110, 26, 12, 'dark') +
      d.face(500, 690, 190), -18, 500, 520));

  const maraca = (d, rot, cx, cy) => group(
    cap(d, cx, cy + 120, cx, cy + 400, 34, 'dark') + d.E(cx, cy, 150, 175) +
    d.band(cx, cy, 150, 175, cx - 150, cx - 95, 'accent') + d.band(cx, cy, 150, 175, cx + 95, cx + 150, 'accent') +
    d.face(cx, cy + 10, 170), rot, cx, cy + 200);
  A.add('maracas', 'Maracas', { main: G, dark: DB, accent: Y, pink: P }, d =>
    maraca(d, -18, 330, 380) + maraca(d, 18, 670, 380));

  A.add('xylophone', 'Xylophone', { main: R, dark: DB, light: W, accent: Y, accent2: G, pink: P }, d => {
    const cols = ['main', 'accent', 'accent2', 'light', 'pink', 'main'];
    let bars = '';
    for (let i = 0; i < 6; i++) {
      const x = 200 + i * 105, h = 340 - i * 34, y = 520 - h / 2;
      bars += d.R(x, y, 80, h, 18, cols[i]) + d.C(x + 40, y + 28, 12, 'dark') + d.C(x + 40, y + h - 28, 12, 'dark');
    }
    return d.P('M160 400 L850 440 L850 470 L160 450 Z', 'dark') + d.P('M160 600 L850 580 L850 610 L160 650 Z', 'dark') + bars +
      mallet(d, 360, 880, 560, 700, 'dark', 'accent') + mallet(d, 640, 880, 780, 690, 'dark', 'accent2');
  });

  A.add('tambourine', 'Tambourine', { main: PU, light: CREAM, accent: Y, accent2: GR, pink: P }, d => {
    let j = '';
    for (let i = 0; i < 8; i++) {
      const a = i / 8 * 2 * Math.PI + Math.PI / 8, x = f(500 + 300 * Math.cos(a)), y = f(500 + 300 * Math.sin(a));
      j += d.E(x, y, 48, 30, 'accent2', f(a * 180 / Math.PI + 90));
    }
    return d.C(500, 500, 330) + j + d.C(500, 500, 240, 'light') + d.face(500, 510, 260);
  });

  A.add('recorder', 'Recorder', { main: B, dark: '#3d8fd1', light: CREAM, accent: Y, pink: P }, d => {
    const holes = [300, 380, 460, 540, 620, 700].map(y => d.C(500, y, 18, 'ink')).join('');
    return note(d, 700, 300, 1.1, 'accent') + note(d, 250, 420, 0.9, 'pink') +
      d.P('M455 140 L545 140 L560 820 Q560 900 500 900 Q440 900 440 820 Z') +
      d.R(445, 90, 110, 90, 30, 'light') + d.P('M470 200 L530 200 L522 240 L478 240 Z', 'ink') +
      d.R(440, 760, 120, 36, 16, 'dark') + d.R(445, 250, 110, 26, 12, 'dark') + holes;
  });

  A.add('saxophone', 'Saxophone', { main: GOLD, light: CREAM, accent: O, dark: DB, pink: P }, d =>
    d.P('M405 265 Q395 165 300 150 L292 192 Q362 205 452 265 Z', 'dark') + d.R(250, 140, 70, 50, 16, 'light') +
    d.P('M395 260 L395 680 Q395 845 560 845 Q725 845 725 680 L725 560 L800 455 L580 455 L650 560 L650 680 Q650 770 560 770 Q475 770 475 680 L475 260 Z') +
    d.E(690, 455, 112, 34, 'light') +
    d.C(435, 340, 22, 'accent') + d.C(435, 410, 22, 'accent') + d.C(435, 480, 22, 'accent') + d.C(435, 550, 22, 'accent') +
    d.C(688, 640, 20, 'accent') + d.C(688, 700, 20, 'accent') +
    note(d, 840, 330, 0.9, 'accent') + note(d, 620, 230, 0.75, 'pink'));

  A.add('harp', 'Harp', { main: GOLD, dark: DB, light: CREAM, accent: R, pink: P }, d => {
    let s = '';
    for (let x = 330; x <= 690; x += 45) {
      const yt = 262 - (x - 290) * 0.1, yb = 215 + (715 - x) * (605 / 415);
      if (yb - yt > 60) s += `M${x} ${f(yt + 12)} L${x} ${f(yb - 14)} `;
    }
    return d.P('M200 880 L200 230 Q200 150 290 160 Q420 190 530 150 Q660 105 790 170 L820 215 L340 890 Z') +
      d.P('M290 820 L290 250 Q420 275 530 235 Q640 195 715 215 L300 830 Z', 'light') + d.Lt(s) +
      d.R(170, 860, 220, 50, 20, 'dark') + d.C(245, 200, 26, 'accent') + heart(d, 245, 560, 34, 'accent');
  });

  A.add('accordion', 'Accordion', { main: R, light: W, dark: DB, accent: Y, pink: P }, d => {
    let folds = '';
    for (let i = 1; i < 8; i++) folds += `M${320 + i * 45} 345 L${320 + i * 45} 655 `;
    let keys = '';
    for (let i = 1; i < 6; i++) keys += `M700 ${310 + i * 62} L800 ${310 + i * 62} `;
    return d.R(320, 330, 360, 340, 6, 'light') + d.Lt(folds) +
      d.R(170, 290, 160, 420, 30) + d.R(670, 290, 160, 420, 30) +
      d.R(695, 320, 110, 360, 10, 'light') + d.Lt(keys) +
      d.C(215, 380, 20, 'accent') + d.C(285, 380, 20, 'accent') + d.C(215, 450, 20, 'accent') + d.C(285, 450, 20, 'accent') +
      d.C(215, 520, 20, 'accent') + d.C(285, 520, 20, 'accent') + d.C(215, 590, 20, 'accent') + d.C(285, 590, 20, 'accent') +
      d.R(440, 296, 120, 36, 16, 'dark');
  });

  A.add('cymbals', 'Cymbals', { main: GOLD, light: CREAM, dark: DB, pink: P }, d =>
    group(d.E(330, 420, 230, 70) + d.E(330, 395, 70, 42, 'light') + d.R(312, 300, 36, 70, 14, 'dark'), -20, 330, 420) +
    group(d.E(670, 600, 230, 70) + d.E(670, 575, 70, 42, 'light') + d.R(652, 480, 36, 70, 14, 'dark'), 20, 670, 600) +
    d.L('M520 470 L560 430 M545 520 L610 505 M480 560 L455 610 M760 380 L800 345 M180 650 L140 690'));

  A.add('bell', 'Bell', { main: GOLD, dark: DB, light: CREAM, accent: R, pink: P }, d =>
    d.R(468, 150, 64, 170, 24, 'dark') + d.C(500, 140, 52, 'dark') +
    d.C(500, 795, 48, 'dark') +
    d.P('M300 700 Q290 330 500 300 Q710 330 700 700 Q770 735 775 765 L225 765 Q230 735 300 700 Z') +
    d.P('M290 690 Q500 730 710 690 L725 740 Q500 785 275 740 Z', 'light') +
    d.face(500, 540, 240));

  A.add('triangle', 'Triangle', { main: GR, dark: DB, accent: R, pink: P }, d =>
    d.L('M500 90 L500 190') + d.C(500, 80, 22, 'accent') +
    d.poly([[500, 190], [830, 790], [170, 790]]) + d.poly([[500, 290], [745, 735], [255, 735]], 'pink') +
    cap(d, 640, 880, 880, 600, 16, 'dark') +
    d.L('M860 420 L910 380 M880 480 L940 470 M120 420 L80 380'));

  A.add('banjo', 'Banjo', { main: T, dark: DB, light: CREAM, accent: Y, pink: P }, d => {
    let bolts = '';
    for (let i = 0; i < 12; i++) {
      const a = i / 12 * 2 * Math.PI;
      bolts += d.C(f(500 + 228 * Math.cos(a)), f(650 + 228 * Math.sin(a)), 13, 'accent');
    }
    return d.R(468, 110, 64, 330, 12, 'dark') + d.R(440, 55, 120, 110, 24, 'dark') +
      d.C(425, 80, 18, 'accent') + d.C(425, 135, 18, 'accent') + d.C(575, 80, 18, 'accent') + d.C(575, 135, 18, 'accent') +
      d.Lt('M486 165 L486 400 M500 165 L500 400 M514 165 L514 400') +
      d.C(500, 650, 255) + bolts + d.C(500, 650, 200, 'light') +
      d.R(445, 785, 110, 26, 12, 'dark') + d.face(500, 630, 220);
  });

  A.add('ukulele', 'Ukulele', { main: PU, dark: DB, light: CREAM, accent: Y, accent2: R, pink: P }, d =>
    group(
      d.R(472, 170, 56, 300, 12, 'dark') + d.R(445, 115, 110, 100, 24, 'dark') +
      d.C(430, 140, 16, 'accent') + d.C(430, 190, 16, 'accent') + d.C(570, 140, 16, 'accent') + d.C(570, 190, 16, 'accent') +
      d.Lt('M490 215 L490 410 M510 215 L510 410') +
      bouts(d, 500, 520, 135, 690, 175) +
      d.C(500, 580, 48, 'dark') + d.R(440, 795, 120, 28, 12, 'dark') +
      d.face(500, 705, 170), 22, 500, 520) +
    d.C(200, 840, 40, 'accent2') + d.C(155, 795, 40, 'accent2') + d.C(200, 750, 40, 'accent2') + d.C(245, 795, 40, 'accent2') +
    d.C(200, 795, 30, 'accent'));

  A.add('microphone', 'Microphone', { main: GR, light: W, dark: '#546e7a', accent: R, pink: P }, d =>
    d.L('M500 860 Q500 930 600 920 Q700 910 700 830 Q700 770 760 770') +
    d.P('M410 540 L450 850 Q500 885 550 850 L590 540 Z', 'dark') +
    d.R(380, 500, 240, 60, 24, 'accent') +
    d.C(500, 330, 190, 'light') + d.face(500, 345, 240) +
    note(d, 780, 260, 0.9, 'accent') + note(d, 200, 230, 0.75, 'pink'));

  A.add('headphones', 'Headphones', { main: B, dark: '#3d8fd1', light: CREAM, accent: R, pink: P }, d =>
    d.P('M200 560 Q200 160 500 160 Q800 160 800 560 L740 560 Q740 230 500 230 Q260 230 260 560 Z') +
    d.R(140, 480, 160, 280, 70, 'accent') + d.R(700, 480, 160, 280, 70, 'accent') +
    d.R(270, 510, 50, 220, 25, 'dark') + d.R(680, 510, 50, 220, 25, 'dark') +
    note(d, 470, 650, 1.6, 'main'));

  A.add('radio', 'Radio', { main: T, light: CREAM, dark: DB, accent: Y, accent2: R, pink: P }, d => {
    let ticks = '';
    for (let i = 1; i < 8; i++) ticks += `M${575 + i * 26} 455 L${575 + i * 26} ${i % 2 ? 480 : 495} `;
    return d.L('M690 330 L820 120') + d.C(820, 110, 24, 'accent2') +
      d.P('M330 330 Q330 230 500 230 Q670 230 670 330 L620 330 Q620 280 500 280 Q380 280 380 330 Z', 'dark') +
      d.R(200, 760, 70, 50, 14, 'dark') + d.R(730, 760, 70, 50, 14, 'dark') +
      d.R(160, 320, 680, 460, 60) +
      d.C(370, 560, 160, 'light') + d.face(370, 560, 190) +
      d.R(560, 420, 230, 100, 22, 'light') + d.Lt(ticks) + d.L('M670 440 L670 505') +
      d.C(610, 650, 46, 'accent') + d.C(740, 650, 46, 'accent');
  });

  A.add('music-notes', 'Music Notes', { main: PU, light: CREAM, pink: P }, d =>
    d.R(440, 250, 44, 480, 22) + d.R(760, 170, 44, 480, 22) +
    d.poly([[440, 250], [804, 160], [804, 260], [440, 350]]) +
    d.E(330, 720, 140, 102, 'main', -20) + d.E(650, 640, 140, 102, 'main', -20) +
    d.face(330, 720, 120) + d.face(650, 640, 120));

  A.add('trombone', 'Trombone', { main: GOLD, light: CREAM, dark: DB, accent: O, pink: P }, d =>
    d.P('M300 520 L800 520 Q880 520 880 590 Q880 660 800 660 L300 660 L300 620 L800 620 Q840 620 840 590 Q840 560 800 560 L300 560 Z') +
    d.R(300, 372, 30, 260, 12, 'dark') + d.R(640, 372, 30, 270, 12, 'dark') +
    d.R(260, 360, 470, 44, 22) + d.R(710, 365, 100, 34, 16, 'accent') +
    d.P('M300 340 L130 245 Q80 380 130 515 L300 420 Z') + d.E(125, 380, 42, 138, 'light') +
    d.face(215, 380, 120));

  A.add('tuba', 'Tuba', { main: GOLD, light: CREAM, dark: DB, accent: O, pink: P }, d =>
    d.P('M420 400 L320 130 L680 130 L580 400 Z') + d.E(500, 132, 182, 42, 'light') +
    d.P('M290 560 Q190 560 190 470 L230 470 Q230 520 290 520 Z', 'dark') + d.R(160, 440, 90, 40, 16, 'accent') +
    d.E(500, 640, 245, 255) +
    d.R(410, 430, 44, 120, 12, 'light') + d.R(478, 430, 44, 120, 12, 'light') + d.R(546, 430, 44, 120, 12, 'light') +
    d.C(432, 420, 28, 'accent') + d.C(500, 420, 28, 'accent') + d.C(568, 420, 28, 'accent') +
    d.face(500, 700, 230));

  const bongo = (d, x, w, top, k) =>
    d.P(`M${x - w} ${top} L${x - w * 0.78} 820 L${x + w * 0.78} 820 L${x + w} ${top} Z`, k) +
    d.P(`M${x - w * 0.97} ${top + 40} L${x + w * 0.97} ${top + 40} L${x + w * 0.95} ${top + 80} L${x - w * 0.95} ${top + 80} Z`, 'accent') +
    d.E(x, top, w, w * 0.28, 'light') + d.face(x, top + 230, w * 1.1);
  A.add('bongos', 'Bongos', { main: O, dark: R, light: CREAM, accent: Y, pink: P }, d =>
    d.R(420, 560, 160, 60, 20, 'accent') + bongo(d, 300, 165, 380, 'main') + bongo(d, 700, 135, 440, 'dark'));

  A.add('harmonica', 'Harmonica', { main: B, light: GR, dark: '#3d8fd1', pink: P, accent: Y }, d => {
    let holes = '';
    for (let i = 0; i < 9; i++) holes += d.R(205 + i * 66, 485, 40, 60, 8, 'ink');
    return note(d, 300, 300, 0.9, 'accent') + note(d, 560, 240, 1.1, 'pink') + note(d, 780, 320, 0.8, 'accent') +
      d.R(150, 400, 700, 230, 40, 'light') + d.R(150, 400, 700, 70, 34) + d.R(150, 560, 700, 70, 34) + holes;
  });

  A.add('keyboard', 'Keyboard', { main: '#455a64', light: W, dark: DB, accent: R, accent2: Y, pink: P }, d => {
    let keys = '';
    for (let i = 1; i < 12; i++) keys += `M${150 + i * 58} 480 L${150 + i * 58} 610 `;
    let black = '';
    [0, 1, 3, 4, 5, 7, 8, 10].forEach(i => { black += d.R(187 + i * 58, 480, 34, 75, 6, 'ink'); });
    return cap(d, 300, 640, 720, 900, 18, 'dark') + cap(d, 700, 640, 280, 900, 18, 'dark') +
      d.R(120, 360, 760, 280, 30) + d.R(150, 480, 700, 130, 10, 'light') + d.Lt(keys) + black +
      d.R(180, 395, 150, 50, 10, 'accent2') + d.C(400, 420, 24, 'accent') + d.C(470, 420, 24, 'accent') +
      d.C(700, 420, 22, 'light') + d.C(770, 420, 22, 'light');
  });

  A.add('music-box', 'Music Box', { main: P, dark: DB, light: CREAM, accent: Y, accent2: R, pink: '#ff8fab' }, d =>
    note(d, 420, 190, 1, 'accent') + note(d, 600, 130, 0.85, 'accent2') +
    d.P('M250 470 L310 260 L750 260 L800 470 Z', 'light') + d.P('M300 470 L345 300 L715 300 L755 470 Z', 'pink') +
    d.R(790, 600, 100, 34, 16, 'dark') + d.C(890, 617, 36, 'accent') +
    d.R(200, 460, 600, 360, 30) + d.R(200, 460, 600, 50, 20, 'accent') +
    d.face(500, 640, 230) + heart(d, 500, 770, 30, 'accent2'));

  A.add('rattle', 'Rattle', { main: Y, dark: O, light: W, accent: B, accent2: R, pink: P }, d =>
    cap(d, 500, 560, 500, 790, 40, 'accent') + d.C(500, 860, 80, 'accent2') + d.C(500, 860, 38, 'light') +
    d.C(500, 360, 225) + d.band(500, 360, 225, 225, 275, 330, 'dark') + d.band(500, 360, 225, 225, 670, 725, 'dark') +
    d.face(500, 370, 250));

  A.add('whistle', 'Whistle', { main: R, dark: DB, light: CREAM, accent: Y, pink: P }, d =>
    d.L('M650 360 Q760 180 880 260 Q960 330 860 420') +
    d.R(140, 400, 380, 130, 34, 'main') + d.R(140, 400, 120, 130, 30, 'dark') +
    d.C(600, 560, 210) + patch(d, 470, 470, 60) +
    d.R(420, 395, 120, 40, 14, 'light') + d.C(660, 380, 28, 'accent') +
    d.face(610, 590, 230));

  A.add('singing-bird', 'Singing Bird', { main: B, dark: '#3d8fd1', light: CREAM, accent: O, accent2: Y, pink: P }, d =>
    d.R(120, 800, 760, 44, 22, 'dark') + d.E(270, 790, 70, 30, 'accent2', -20) +
    d.L('M440 750 L440 805 M520 750 L520 805') +
    d.poly([[260, 600], [120, 520], [150, 640]], 'dark') +
    d.E(470, 600, 230, 180) + d.E(450, 640, 140, 90, 'light') +
    d.E(380, 590, 110, 70, 'dark', 20) +
    d.C(610, 420, 135) +
    d.poly([[720, 390], [800, 360], [730, 425]], 'accent') + d.poly([[730, 435], [800, 470], [722, 455]], 'accent') +
    d.eye(625, 395, 24) + d.C(585, 460, 22, 'pink') +
    note(d, 820, 280, 0.8, 'accent2') + note(d, 700, 200, 0.65, 'pink'));
})();
