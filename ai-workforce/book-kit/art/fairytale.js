// "My First Fairy Tale": 30 friendly fairy-tale and magical things, for ages 2-5.
// Generic, public-domain fairy-tale ideas drawn from scratch: no film or TV designs,
// no licensed characters (no studio princesses, no named genies or film dragons),
// no brands or logos.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', PU = '#b39ddb', LPU = '#e1d5ff', W = '#ffffff', CREAM = '#fff3d6', GOLD = '#f6c945', SKIN = '#ffd9b8', ICE = '#d7f0ff',
    TEAL = '#5ccfc4', HAIR = '#a86b3c', HAIR2 = '#f2c46d', STONE = '#d7ccc8', SLATE = '#9fa8da', MINT = '#b9f3e4';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (stalks, handles, ropes): a black stroke, then a coloured stroke on
  // top, so where tubes meet the joints merge cleanly
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const star = (d, cx, cy, r, k = 'accent') => d.poly([...Array(10)].map((_, i) => {
    const a = (-90 + i * 36) * Math.PI / 180, rr = i % 2 ? r * 0.45 : r; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  }), k);
  // a four-point sparkle
  const sparkle = (d, cx, cy, r, k = 'accent2') => d.poly([...Array(8)].map((_, i) => {
    const a = (-90 + i * 45) * Math.PI / 180, rr = i % 2 ? r * 0.3 : r; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  }), k);
  // a horizontal stripe across a circle between y1 and y2, following its edge
  const hband = (d, cx, cy, r, y1, y2, k) => {
    const pts = [];
    for (let i = 0; i <= 12; i++) { const y = y1 + (y2 - y1) * i / 12; pts.push([cx + Math.sqrt(Math.max(0, r * r - (y - cy) ** 2)), y]); }
    for (let i = 12; i >= 0; i--) { const y = y1 + (y2 - y1) * i / 12; pts.push([cx - Math.sqrt(Math.max(0, r * r - (y - cy) ** 2)), y]); }
    return d.poly(pts, k);
  };
  // a small crown sitting on y (its base), centred on cx, width w
  const crown = (d, cx, y, w, k = 'accent2') => {
    const h = w * 0.62, s = w / 2;
    return d.P(`M${f(cx - s)} ${y} L${f(cx - s - w * 0.04)} ${f(y - h)} L${f(cx - s * 0.45)} ${f(y - h * 0.5)} L${cx} ${f(y - h * 1.12)} L${f(cx + s * 0.45)} ${f(y - h * 0.5)} L${f(cx + s + w * 0.04)} ${f(y - h)} L${f(cx + s)} ${y} Z`, k);
  };
  // a leaf from its base x,y, length L, turned by ang (0 points right)
  const leaf = (d, x, y, L, w, ang, k = 'leaf') =>
    group(d.P(`M${x} ${y} Q${f(x + L * 0.45)} ${f(y - w)} ${x + L} ${y} Q${f(x + L * 0.45)} ${f(y + w)} ${x} ${y} Z`, k) +
      d.Lt(`M${x + 18} ${y} L${f(x + L * 0.7)} ${y}`), ang, x, y);
  // a chibi head: hair behind, skin circle, a fringe, and a cute face
  const head = (d, cx, cy, r, hair = 'hair') =>
    d.C(cx, cy - r * 0.08, r * 1.16, hair) +
    d.C(cx, cy, r, 'skin') +
    d.P(`M${f(cx - r * 1.02)} ${f(cy - r * 0.05)} Q${f(cx - r * 0.9)} ${f(cy - r * 1.1)} ${cx} ${f(cy - r * 1.1)} Q${f(cx + r * 0.9)} ${f(cy - r * 1.1)} ${f(cx + r * 1.02)} ${f(cy - r * 0.05)} Q${f(cx + r * 0.7)} ${f(cy - r * 0.55)} ${f(cx + r * 0.3)} ${f(cy - r * 0.42)} Q${cx} ${f(cy - r * 0.72)} ${f(cx - r * 0.3)} ${f(cy - r * 0.42)} Q${f(cx - r * 0.7)} ${f(cy - r * 0.55)} ${f(cx - r * 1.02)} ${f(cy - r * 0.05)} Z`, hair) +
    d.face(cx, cy + r * 0.12, r * 1.25);

  // ---------------- castles and crowns ----------------
  A.add('castle', 'Castle', { main: GR, accent: PU, accent2: R, dark: DB, light: B, pink: P }, d =>
    d.L('M245 170 L245 80') + d.poly([[245, 80], [325, 105], [245, 132]], 'accent2') +
    d.L('M755 170 L755 80') + d.poly([[755, 80], [835, 105], [755, 132]], 'accent2') +
    d.R(150, 380, 190, 520, 10) + d.R(660, 380, 190, 520, 10) +
    d.poly([[125, 395], [245, 165], [365, 395]], 'accent') + d.poly([[635, 395], [755, 165], [875, 395]], 'accent') +
    d.P('M215 600 L215 520 Q245 470 275 520 L275 600 Z', 'light') + d.P('M725 600 L725 520 Q755 470 785 520 L785 600 Z', 'light') +
    d.P('M300 900 L300 400 L365 400 L365 455 L435 455 L435 400 L565 400 L565 455 L635 455 L635 400 L700 400 L700 900 Z') +
    d.P('M425 900 L425 770 Q500 680 575 770 L575 900 Z', 'dark') +
    d.face(500, 580, 200));

  A.add('crown', 'Crown', { main: GOLD, accent: R, accent2: B, pink: P }, d =>
    d.P('M220 720 L180 330 L345 520 L500 260 L655 520 L820 330 L780 720 Z') +
    d.C(180, 320, 42, 'accent') + d.C(500, 250, 48, 'accent') + d.C(820, 320, 42, 'accent') +
    d.R(195, 680, 610, 140, 36) +
    d.C(330, 750, 34, 'accent2') + d.E(500, 750, 48, 40, 'accent') + d.C(670, 750, 34, 'accent2') +
    d.face(500, 560, 210));

  A.add('throne', 'Throne', { main: GOLD, accent: R, accent2: B, dark: DB, pink: P }, d =>
    d.P('M290 610 L290 260 Q290 130 500 110 Q710 130 710 260 L710 610 Z') +
    d.P('M350 600 L350 280 Q350 190 500 178 Q650 190 650 280 L650 600 Z', 'accent') +
    d.C(500, 100, 48, 'accent2') +
    d.R(300, 690, 70, 210, 20) + d.R(630, 690, 70, 210, 20) +
    d.R(215, 470, 110, 250, 46) + d.R(675, 470, 110, 250, 46) +
    d.R(250, 590, 500, 120, 46, 'accent') +
    d.C(270, 500, 22, 'accent2') + d.C(730, 500, 22, 'accent2') +
    d.face(500, 380, 210));

  A.add('tower', 'Tower', { main: STONE, accent: PU, accent2: Y, dark: DB, light: B, leaf: G, flower: P, pink: P }, d =>
    d.L('M500 85 L500 20') + d.poly([[500, 20], [575, 42], [500, 66]], 'accent2') +
    d.R(350, 300, 300, 600, 20) +
    d.poly([[305, 320], [500, 75], [695, 320]], 'accent') +
    d.P('M455 440 L455 380 Q500 320 545 380 L545 440 Z', 'light') +
    d.P('M445 900 L445 805 Q500 745 555 805 L555 900 Z', 'dark') +
    d.R(372, 510, 60, 34, 8) + d.R(568, 510, 60, 34, 8) + d.R(372, 710, 60, 34, 8) + d.R(568, 710, 60, 34, 8) +
    d.C(305, 845, 60, 'leaf') + d.C(370, 868, 44, 'leaf') + d.C(695, 845, 60, 'leaf') + d.C(630, 868, 44, 'leaf') +
    d.face(500, 610, 210));

  A.add('shield', 'Shield', { main: B, light: W, accent2: Y, pink: P }, d =>
    d.P('M210 190 L790 190 L790 450 Q790 760 500 890 Q210 760 210 450 Z') +
    d.P('M275 250 L725 250 L725 455 Q725 715 500 820 Q275 715 275 455 Z', 'light') +
    star(d, 500, 485, 190, 'accent2') +
    d.face(500, 510, 170));

  // ---------------- fairy-tale friends ----------------
  A.add('princess', 'Princess', { main: LPU, skin: SKIN, hair: HAIR, accent: R, accent2: GOLD, light: W, pink: P }, d =>
    d.P('M345 330 Q320 560 380 620 L620 620 Q680 560 655 330 Z', 'hair') +
    d.P('M445 560 Q300 700 250 890 Q500 940 750 890 Q700 700 555 560 Z') +
    d.E(345, 650, 34, 80, 'skin', 30) + d.E(655, 650, 34, 80, 'skin', -30) +
    d.R(420, 500, 160, 130, 46) +
    d.L('M290 835 Q500 880 710 835') +
    head(d, 500, 350, 135) +
    crown(d, 500, 228, 160));

  A.add('prince', 'Prince', { main: B, skin: SKIN, hair: DB, accent: R, accent2: GOLD, dark: '#5c6bc0', boot: DB, pink: P }, d =>
    d.P('M395 520 L295 885 L705 885 L605 520 Z', 'accent') +
    d.R(435, 760, 55, 110, 20, 'dark') + d.R(510, 760, 55, 110, 20, 'dark') +
    d.R(415, 845, 85, 55, 24, 'boot') + d.R(500, 845, 85, 55, 24, 'boot') +
    d.E(375, 640, 36, 90, 'main', 20) + d.E(625, 640, 36, 90, 'main', -20) +
    d.C(352, 720, 34, 'skin') + d.C(648, 720, 34, 'skin') +
    d.R(400, 500, 200, 290, 60) +
    d.R(400, 680, 200, 42, 12, 'dark') + d.R(478, 670, 44, 62, 10, 'accent2') +
    d.C(500, 340, 140, 'skin') +
    d.P('M362 345 Q355 185 500 185 Q645 185 638 345 Q610 270 500 268 Q390 270 362 345 Z', 'hair') +
    d.face(500, 375, 175) +
    crown(d, 500, 215, 170));

  A.add('fairy', 'Fairy', { main: G, skin: SKIN, hair: O, light: ICE, accent: P, accent2: Y, pink: P }, d =>
    d.E(330, 500, 140, 95, 'light', -30) + d.E(670, 500, 140, 95, 'light', 30) +
    d.E(370, 645, 95, 62, 'light', 30) + d.E(630, 645, 95, 62, 'light', -30) +
    d.R(442, 810, 40, 80, 20, 'skin') + d.R(518, 810, 40, 80, 20, 'skin') +
    d.E(455, 892, 46, 24, 'accent') + d.E(545, 892, 46, 24, 'accent') +
    d.P('M425 520 L320 835 Q500 875 680 835 L575 520 Z') +
    d.E(385, 610, 30, 70, 'skin', 35) +
    d.L('M640 640 L745 450') + star(d, 760, 425, 62, 'accent2') +
    d.E(615, 615, 30, 70, 'skin', -35) +
    head(d, 500, 350, 135) +
    d.C(415, 230, 30, 'accent') + d.C(445, 205, 30, 'accent') + d.C(430, 220, 14, 'accent2'));

  A.add('knight', 'Knight', { main: GR, skin: SKIN, accent: R, accent2: Y, dark: '#78909c', pink: P }, d =>
    d.E(500, 140, 52, 90, 'accent') +
    d.R(410, 760, 75, 125, 28) + d.R(515, 760, 75, 125, 28) +
    d.R(395, 860, 100, 45, 22, 'dark') + d.R(505, 860, 100, 45, 22, 'dark') +
    d.R(300, 540, 85, 210, 42) + d.R(615, 540, 85, 210, 42) +
    d.R(375, 520, 250, 270, 70) +
    d.P('M500 700 Q430 650 440 610 Q450 575 500 600 Q550 575 560 610 Q570 650 500 700 Z', 'accent') +
    d.R(325, 190, 350, 360, 150) +
    d.R(385, 300, 230, 195, 80, 'skin') +
    d.R(355, 255, 290, 50, 25) +
    d.face(500, 395, 175));

  A.add('frog-prince', 'Frog Prince', { main: G, light: '#d4f5c9', leaf: DG, accent2: GOLD, pink: P }, d =>
    d.E(500, 850, 340, 80, 'leaf') + d.L('M500 850 L560 780') +
    d.E(300, 760, 110, 70, 'main', -20) + d.E(700, 760, 110, 70, 'main', 20) +
    d.E(500, 650, 210, 190) +
    d.E(500, 700, 130, 120, 'light') +
    d.E(405, 830, 62, 30) + d.E(595, 830, 62, 30) +
    d.C(375, 265, 82) + d.C(625, 265, 82) +
    d.E(500, 440, 235, 165) +
    d.eye(375, 258, 34) + d.eye(625, 258, 34) +
    crown(d, 500, 300, 150) +
    d.smile(500, 465, 95, 45) +
    d.C(345, 455, 26, 'pink') + d.C(655, 455, 26, 'pink'));

  A.add('gnome', 'Gnome', { main: B, accent: R, light: W, skin: SKIN, dark: DB, pink: P }, d =>
    d.E(410, 890, 75, 35, 'dark') + d.E(590, 890, 75, 35, 'dark') +
    d.P('M345 590 L300 880 L700 880 L655 590 Z') +
    d.C(320, 705, 42, 'skin') + d.C(680, 705, 42, 'skin') +
    d.R(355, 400, 290, 170, 60, 'skin') +
    d.P('M330 505 Q310 735 500 815 Q690 735 670 505 Q610 590 500 590 Q390 590 330 505 Z', 'light') +
    d.P('M290 440 Q380 200 530 45 Q570 240 710 440 Q500 480 290 440 Z', 'accent') +
    d.eye(437, 492, 23) + d.eye(563, 492, 23) +
    d.C(372, 535, 20, 'pink') + d.C(628, 535, 20, 'pink') +
    d.P('M500 590 Q455 630 395 605 Q440 565 500 580 Q560 565 605 605 Q545 630 500 590 Z', 'light') +
    d.C(500, 548, 42, 'pink'));

  A.add('mermaid', 'Mermaid', { main: PU, skin: SKIN, hair: HAIR, accent: P, accent2: Y, pink: P }, d =>
    d.P('M340 320 Q300 600 400 650 L600 650 Q700 600 660 320 Z', 'hair') +
    d.P('M500 790 Q395 815 320 905 Q430 925 500 860 Q570 925 680 905 Q605 815 500 790 Z') +
    d.P('M415 560 Q395 700 470 815 L530 815 Q605 700 585 560 Z') +
    d.Lt('M450 640 Q470 665 490 640 M510 640 Q530 665 550 640 M470 700 Q490 725 510 700 M490 760 L500 772 L510 760') +
    d.E(380, 600, 30, 75, 'skin', 25) + d.E(620, 600, 30, 75, 'skin', -25) +
    d.R(420, 455, 160, 130, 50, 'skin') +
    d.E(458, 510, 45, 34, 'accent') + d.E(542, 510, 45, 34, 'accent') +
    head(d, 500, 335, 135) +
    star(d, 600, 225, 42, 'accent2'));

  A.add('wolf', 'Wolf', { main: GR, light: W, dark: '#78909c', pink: P }, d =>
    d.P('M620 835 Q870 880 890 690 Q895 590 820 540 Q850 650 770 705 Q700 740 640 745 Z') +
    d.P('M820 540 Q895 590 890 690 Q860 660 845 610 Z', 'light') +
    d.poly([[345, 285], [325, 90], [455, 200]]) + d.poly([[655, 285], [675, 90], [545, 200]]) +
    d.poly([[365, 240], [355, 145], [420, 205]], 'pink') + d.poly([[635, 240], [645, 145], [580, 205]], 'pink') +
    d.R(395, 740, 65, 140, 30) + d.R(540, 740, 65, 140, 30) +
    d.E(500, 690, 185, 195) +
    d.E(500, 730, 105, 140, 'light') +
    d.E(425, 880, 62, 34) + d.E(575, 880, 62, 34) +
    d.poly([[340, 330], [270, 440], [360, 430], [330, 500], [400, 470]]) + d.poly([[660, 330], [730, 440], [640, 430], [670, 500], [600, 470]]) +
    d.C(500, 360, 170) +
    d.E(500, 462, 105, 78, 'light') +
    d.E(500, 420, 36, 26, 'ink') + d.Lt('M500 446 L500 476') + d.smile(500, 476, 36, 20) +
    d.eye(432, 345, 24) + d.eye(568, 345, 24) +
    d.C(380, 415, 22, 'pink') + d.C(620, 415, 22, 'pink'));

  // ---------------- magical creatures ----------------
  A.add('dragon', 'Dragon', { main: G, light: '#e8f9c8', accent: TEAL, accent2: Y, pink: P }, d =>
    d.P('M640 760 Q860 780 880 610 L845 590 Q835 690 650 700 Z') + d.poly([[845, 590], [900, 520], [915, 615]], 'accent2') +
    d.P('M385 520 Q230 310 160 430 Q225 435 225 490 Q280 480 300 540 Z', 'accent') +
    d.P('M615 520 Q770 310 840 430 Q775 435 775 490 Q720 480 700 540 Z', 'accent') +
    d.poly([[425, 250], [395, 140], [478, 220]], 'accent2') + d.poly([[575, 250], [605, 140], [522, 220]], 'accent2') +
    d.E(500, 690, 200, 190) +
    d.E(500, 720, 120, 140, 'light') +
    d.Lt('M410 650 Q500 670 590 650 M400 720 Q500 740 600 720 M415 790 Q500 810 585 790') +
    d.E(400, 870, 82, 45) + d.E(600, 870, 82, 45) +
    d.E(330, 650, 40, 72, 'main', 30) + d.E(670, 650, 40, 72, 'main', -30) +
    d.C(500, 375, 165) +
    d.E(500, 445, 98, 62, 'light') + d.dot(468, 432, 10) + d.dot(532, 432, 10) +
    d.smile(500, 468, 36, 20) +
    d.eye(438, 345, 26) + d.eye(562, 345, 26) +
    d.C(372, 410, 22, 'pink') + d.C(628, 410, 22, 'pink'));

  A.add('baby-dragon', 'Baby Dragon', { main: PU, light: W, accent: Y, accent2: TEAL, spot: B, pink: P }, d =>
    d.P('M330 420 Q220 300 190 400 Q240 410 250 450 Z', 'accent2') + d.P('M670 420 Q780 300 810 400 Q760 410 750 450 Z', 'accent2') +
    d.poly([[430, 255], [410, 160], [480, 230]], 'accent') + d.poly([[570, 255], [590, 160], [520, 230]], 'accent') +
    d.C(500, 400, 170) +
    d.E(500, 470, 92, 58, 'light') + d.dot(470, 458, 9) + d.dot(530, 458, 9) +
    d.smile(500, 490, 32, 18) +
    d.eye(438, 375, 25) + d.eye(562, 375, 25) +
    d.C(372, 440, 21, 'pink') + d.C(628, 440, 21, 'pink') +
    d.P('M235 575 L300 530 L365 590 L432 530 L500 590 L568 530 L635 590 L700 530 L765 575 Q790 880 500 900 Q210 880 235 575 Z', 'light') +
    d.C(360, 730, 34, 'spot') + d.C(620, 690, 28, 'spot') + d.C(540, 820, 30, 'spot') +
    d.E(330, 565, 52, 36) + d.E(670, 565, 52, 36));

  A.add('unicorn', 'Unicorn', { main: W, mane: P, mane2: PU, accent: GOLD, light: '#ffe4ec', pink: P }, d =>
    d.C(330, 330, 82, 'mane') + d.C(300, 470, 84, 'mane2') + d.C(325, 610, 82, 'mane') + d.C(390, 225, 70, 'mane2') +
    d.P('M375 590 Q345 790 300 900 L700 900 Q655 790 625 590 Z') +
    d.poly([[385, 265], [365, 120], [455, 205]]) + d.poly([[615, 265], [635, 120], [545, 205]]) +
    d.poly([[398, 238], [388, 160], [432, 205]], 'light') + d.poly([[602, 238], [612, 160], [568, 205]], 'light') +
    d.E(500, 430, 170, 190) +
    d.poly([[462, 225], [500, 40], [538, 225]], 'accent') +
    d.Lt('M474 180 L526 166 M482 130 L518 120 M490 86 L510 80') +
    d.E(500, 560, 122, 86, 'light') +
    d.E(458, 548, 15, 11, 'ink') + d.E(542, 548, 15, 11, 'ink') +
    d.smile(500, 592, 36, 18) +
    d.eye(430, 420, 26) + d.eye(570, 420, 26) +
    d.C(365, 480, 22, 'pink') + d.C(635, 480, 22, 'pink'));

  A.add('pegasus', 'Pegasus', { main: W, mane: B, light: ICE, dark: '#90a4ae', muzzle: '#ffe4ec', pink: P }, d =>
    d.P('M265 520 Q140 560 160 720 Q215 650 290 610 Z', 'mane') +
    d.R(305, 630, 62, 215, 30) + d.R(620, 630, 62, 215, 30) +
    d.R(300, 815, 72, 55, 18, 'dark') + d.R(615, 815, 72, 55, 18, 'dark') +
    d.E(480, 590, 235, 140) +
    d.R(395, 650, 62, 205, 30) + d.R(530, 650, 62, 205, 30) +
    d.R(390, 825, 72, 55, 18, 'dark') + d.R(525, 825, 72, 55, 18, 'dark') +
    d.P('M560 560 Q600 430 640 350 L760 395 Q700 520 690 600 Z') +
    d.C(625, 335, 48, 'mane') + d.C(600, 410, 48, 'mane') + d.C(585, 485, 46, 'mane') +
    d.poly([[690, 270], [700, 190], [742, 262]]) +
    d.E(725, 330, 122, 96) +
    d.E(812, 372, 66, 56, 'muzzle') + d.dot(835, 362, 10) + d.smile(812, 402, 26, 14) +
    d.eye(722, 308, 24) + d.C(696, 368, 19, 'pink') +
    d.P('M530 535 Q480 300 215 175 Q245 260 300 295 Q270 335 325 380 Q305 430 370 465 Q365 525 425 560 Z', 'light') +
    d.Lt('M470 470 Q420 410 330 335 M500 410 Q440 330 300 250'));

  // ---------------- Cinderella's ball and Jack's beanstalk ----------------
  A.add('pumpkin-coach', 'Pumpkin Coach', { main: O, dark: DB, light: B, leaf: G, wheel: Y, pink: P }, d =>
    d.R(270, 725, 460, 40, 20, 'dark') +
    d.C(295, 780, 110, 'wheel') + d.C(705, 780, 110, 'wheel') +
    d.Lt('M295 680 L295 880 M195 780 L395 780 M225 710 L365 850 M365 710 L225 850 M705 680 L705 880 M605 780 L805 780 M635 710 L775 850 M775 710 L635 850') +
    d.C(295, 780, 34, 'dark') + d.C(705, 780, 34, 'dark') +
    d.R(470, 215, 60, 75, 16, 'leaf') + d.L('M530 250 Q610 190 650 245 Q670 290 625 298') +
    d.E(500, 500, 300, 235) +
    d.Lt('M370 290 Q300 500 370 715 M630 290 Q700 500 630 715') +
    d.R(420, 345, 160, 140, 60, 'light') + d.Lt('M500 345 L500 485 M420 415 L580 415') +
    d.face(500, 590, 190));

  A.add('glass-slipper', 'Glass Slipper', { main: ICE, accent: P, accent2: Y, light: W, pink: P }, d =>
    d.P('M175 705 Q165 610 275 600 L470 625 Q600 545 755 440 Q825 410 835 490 L840 640 L805 870 L752 870 L735 670 Q640 705 565 770 L255 785 Q180 780 175 705 Z') +
    d.P('M480 628 Q610 560 760 462 Q800 450 805 488 Q780 560 645 630 Q560 655 480 628 Z', 'light') +
    d.E(268, 600, 48, 30, 'accent', -20) + d.E(352, 600, 48, 30, 'accent', 20) + d.C(310, 605, 23, 'accent') +
    d.face(470, 702, 150) +
    sparkle(d, 620, 330, 58) + sparkle(d, 250, 440, 42) + sparkle(d, 850, 260, 40));

  A.add('beanstalk', 'Beanstalk', { main: G, leaf: DG, light: W, dark: DB, pink: P }, d =>
    d.E(500, 895, 210, 45, 'dark') +
    tube(d, ['M500 885 Q370 760 500 640 Q630 520 500 400 Q390 300 500 230'], 'main', 74) +
    leaf(d, 445, 770, 210, 100, -165) + leaf(d, 560, 615, 210, 100, -15) +
    leaf(d, 440, 480, 190, 90, -165) + leaf(d, 548, 340, 175, 82, -20) +
    d.scallop(500, 170, 105, 9, 66, 'light') +
    d.face(500, 175, 150));

  A.add('magic-beans', 'Magic Beans', { main: G, accent2: Y, pink: P }, d => {
    const bean = (cx, cy, s, rot) => group(
      d.P(`M${cx - 140 * s} ${cy} Q${cx - 140 * s} ${cy - 95 * s} ${cx - 60 * s} ${cy - 90 * s} Q${cx} ${cy - 60 * s} ${cx + 60 * s} ${cy - 90 * s} Q${cx + 140 * s} ${cy - 95 * s} ${cx + 140 * s} ${cy} Q${cx + 140 * s} ${cy + 95 * s} ${cx} ${cy + 100 * s} Q${cx - 140 * s} ${cy + 95 * s} ${cx - 140 * s} ${cy} Z`) +
      d.face(cx, cy + 5 * s, 150 * s), rot, cx, cy);
    return bean(500, 340, 1.25, 0) + bean(300, 680, 1.1, -14) + bean(700, 680, 1.1, 14) +
      sparkle(d, 200, 300, 50) + sparkle(d, 810, 330, 46) + sparkle(d, 500, 860, 44);
  });

  // ---------------- magic things ----------------
  A.add('magic-wand', 'Magic Wand', { main: Y, dark: PU, accent: P, accent2: B, pink: P }, d =>
    group(d.R(468, 470, 64, 430, 32, 'dark') + d.R(458, 520, 84, 46, 20, 'accent'), 18, 500, 500) +
    star(d, 470, 330, 225) +
    d.face(470, 345, 160) +
    sparkle(d, 780, 220, 52) + sparkle(d, 200, 600, 46) + sparkle(d, 760, 560, 38, 'accent'));

  A.add('magic-lamp', 'Magic Lamp', { main: GOLD, accent: R, light: W, accent2: PU, pink: P }, d =>
    tube(d, ['M285 585 Q175 585 185 490 Q195 410 290 445'], 'main', 62) +
    d.P('M640 520 Q760 520 845 420 Q872 405 880 430 Q825 565 690 625 Z') +
    d.P('M405 670 L375 755 L585 755 L555 670 Z') + d.R(330, 745, 300, 52, 24) +
    d.E(480, 585, 225, 125) +
    d.E(480, 468, 125, 42, 'accent') + d.C(480, 418, 34, 'accent') +
    d.C(885, 355, 40, 'light') + d.C(840, 290, 52, 'light') + d.C(900, 228, 42, 'light') +
    sparkle(d, 760, 200, 40, 'accent2') +
    d.face(470, 600, 175));

  A.add('flying-carpet', 'Flying Carpet', { main: R, accent: Y, accent2: PU, light: B, pink: P }, d =>
    d.Lt('M60 430 L160 430 M40 500 L120 500') +
    d.L('M150 545 L100 530 M150 600 L100 600 M150 660 L100 675 M850 525 L900 510 M850 585 L900 585 M850 645 L900 660') +
    d.P('M150 520 Q320 440 500 520 Q680 600 850 500 L850 680 Q680 780 500 700 Q320 620 150 700 Z') +
    d.P('M195 555 Q330 490 500 560 Q670 635 805 550 L805 640 Q670 730 500 660 Q330 590 195 650 Z', 'accent') +
    sparkle(d, 330, 300, 48, 'accent2') + sparkle(d, 700, 300, 40, 'accent2') +
    d.face(500, 610, 170));

  A.add('crystal-ball', 'Crystal Ball', { main: LPU, dark: DB, light: W, accent2: Y, accent: P, pink: P }, d =>
    d.P('M325 800 L380 690 L620 690 L675 800 Z', 'dark') + d.R(285, 790, 430, 70, 30, 'dark') +
    d.C(500, 450, 275) +
    d.P('M320 380 Q340 270 440 230 Q385 320 385 400 Z', 'light') +
    star(d, 630, 300, 42, 'accent2') + sparkle(d, 380, 560, 30, 'accent2') + sparkle(d, 650, 560, 26, 'accent') +
    d.face(505, 470, 210));

  A.add('potion', 'Potion', { main: P, glass: ICE, cork: BR, light: W, accent2: Y, pink: P }, d =>
    d.C(590, 70, 24, 'light') + d.C(640, 120, 16, 'light') +
    d.R(445, 120, 110, 100, 26, 'cork') +
    d.R(425, 190, 150, 190, 24, 'glass') +
    d.C(500, 590, 265, 'glass') +
    d.R(405, 195, 190, 50, 25, 'glass') +
    hband(d, 500, 590, 265, 500, 854, 'main') +
    d.C(385, 595, 22, 'light') + d.C(610, 760, 18, 'light') + d.C(640, 560, 14, 'light') +
    d.face(500, 690, 200));

  A.add('spell-book', 'Spell Book', { main: PU, light: W, accent2: Y, accent: P, pink: P }, d =>
    d.P('M115 725 L500 800 L885 725 L885 775 L500 852 L115 775 Z') +
    d.P('M135 385 Q330 330 500 415 L500 785 Q330 705 135 745 Z', 'light') +
    d.P('M865 385 Q670 330 500 415 L500 785 Q670 705 865 745 Z', 'light') +
    d.Lt('M205 470 Q300 445 430 485 M205 545 Q300 520 430 560 M205 620 Q300 595 430 635 M570 485 Q700 445 795 470 M570 560 Q700 520 795 545 M570 635 Q700 595 795 620') +
    d.L('M500 405 Q430 330 500 280') +
    star(d, 500, 200, 92, 'accent2') + d.face(500, 210, 70) +
    sparkle(d, 330, 250, 36, 'accent') + sparkle(d, 680, 255, 40, 'accent'));

  A.add('wizard-hat', 'Wizard Hat', { main: '#7986cb', accent: Y, accent2: Y, light: '#9fa8da', pink: P }, d =>
    d.E(500, 810, 335, 82) +
    d.P('M275 795 L470 240 Q505 150 610 125 Q565 205 565 265 L725 795 Q500 840 275 795 Z') +
    d.P('M305 705 Q500 745 695 705 L720 775 Q500 822 280 775 Z', 'accent') +
    star(d, 440, 455, 46, 'accent2') + star(d, 560, 350, 34, 'accent2') +
    d.face(500, 595, 175));

  A.add('mushroom-house', 'Mushroom House', { main: R, light: W, stem: CREAM, dark: DB, accent2: Y, pink: P }, d =>
    d.P('M345 520 L320 880 L680 880 L655 520 Z', 'stem') +
    d.P('M440 880 L440 750 Q500 690 560 750 L560 880 Z', 'dark') + d.dot(540, 815, 10) +
    d.C(390, 650, 42, 'accent2') + d.Lt('M390 608 L390 692 M348 650 L432 650') +
    d.C(612, 650, 42, 'accent2') + d.Lt('M612 608 L612 692 M570 650 L654 650') +
    d.P('M145 565 Q145 225 500 200 Q855 225 855 565 Q500 615 145 565 Z') +
    d.C(255, 455, 40, 'light') + d.C(745, 455, 40, 'light') + d.C(345, 300, 36, 'light') + d.C(655, 300, 36, 'light') +
    d.face(500, 420, 200));

  A.add('wishing-well', 'Wishing Well', { main: STONE, roof: R, wood: BR, water: B, pink: P }, d =>
    d.R(280, 315, 50, 330, 10, 'wood') + d.R(670, 315, 50, 330, 10, 'wood') +
    d.poly([[215, 335], [500, 140], [785, 335]], 'roof') +
    d.L('M330 405 L670 405') + d.L('M500 405 L500 505') +
    d.L('M450 525 Q500 470 550 525') +
    d.P('M435 520 L565 520 L550 610 L450 610 Z', 'wood') +
    d.R(230, 620, 540, 270, 40) +
    d.R(205, 585, 590, 75, 36) +
    d.Lt('M230 730 L300 730 M700 730 L770 730 M265 730 L265 800 M735 730 L735 800 M230 810 L300 810 M700 810 L770 810') +
    d.face(500, 765, 200));
})();
