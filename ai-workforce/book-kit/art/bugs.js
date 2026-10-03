// "My First Bugs & Butterflies": 30 friendly bugs and garden friends for ages
// 2-5. Original drawings only: no licensed characters (a plain honey jar, not a
// storybook bear's pot).
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', G = '#7bd389', Y = '#ffd23f', O = '#ff9f43', B = '#6ec6ff', PU = '#b39ddb', P = '#ffb3c7', BR = '#c68b59', T = '#4db6ac', W = '#ffffff', LG = '#c5e1a5', GR = '#cfd8dc';

  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // a small flying bee: wings, striped body, head with a face
  const bee = (d, x, y, s = 1) =>
    d.E(x - 18 * s, y - 45 * s, 26 * s, 36 * s, 'light', -20) + d.E(x + 22 * s, y - 45 * s, 26 * s, 36 * s, 'light', 20) +
    d.E(x, y, 62 * s, 42 * s, 'accent') + d.band(x, y, 62 * s, 42 * s, x - 5 * s, x + 18 * s, 'dark') +
    d.C(x - 62 * s, y - 4 * s, 34 * s, 'accent') + d.dot(x - 72 * s, y - 10 * s, 6 * s);
  // a small ant walking right
  const ant = (d, x, y, s = 1) =>
    d.L(`M${x - 5 * s} ${y + 10 * s} L${x - 25 * s} ${y + 45 * s} M${x + 10 * s} ${y + 10 * s} L${x + 25 * s} ${y + 45 * s}`) +
    d.E(x - 45 * s, y, 38 * s, 30 * s, 'dark') + d.E(x, y, 22 * s, 18 * s, 'dark') + d.C(x + 40 * s, y - 8 * s, 26 * s, 'dark') +
    d.dot(x + 48 * s, y - 14 * s, 6 * s) + d.L(`M${x + 45 * s} ${y - 32 * s} Q${x + 55 * s} ${y - 55 * s} ${x + 70 * s} ${y - 60 * s}`);
  // a small ladybug seen from above, head up
  const miniLadybug = (d, x, y, s = 1) =>
    d.C(x, y - 60 * s, 32 * s, 'dark') + d.C(x, y, 62 * s, 'accent2') + d.L(`M${x} ${y - 55 * s} L${x} ${y + 62 * s}`) +
    d.C(x - 30 * s, y - 5 * s, 12 * s, 'dark') + d.C(x + 30 * s, y - 5 * s, 12 * s, 'dark') + d.C(x - 22 * s, y + 32 * s, 10 * s, 'dark') + d.C(x + 22 * s, y + 32 * s, 10 * s, 'dark');
  const petals = (d, cx, cy, n, R0, rx, ry, k) => {
    let s = '';
    for (let i = 0; i < n; i++) { const a = i * 360 / n, t = a * Math.PI / 180; s += d.E(cx + R0 * Math.cos(t), cy + R0 * Math.sin(t), rx, ry, k, a); }
    return s;
  };

  A.add('butterfly', 'Butterfly', { main: PU, accent: B, light: Y, dark: '#f3d9b8', pink: P }, d =>
    d.L('M470 245 Q430 150 385 130') + d.L('M530 245 Q570 150 615 130') + d.C(385, 128, 24, 'light') + d.C(615, 128, 24, 'light') +
    d.E(320, 390, 200, 150, 'main', -25) + d.E(680, 390, 200, 150, 'main', 25) +
    d.E(360, 650, 140, 110, 'accent', 25) + d.E(640, 650, 140, 110, 'accent', -25) +
    d.C(270, 370, 58, 'light') + d.C(730, 370, 58, 'light') + d.C(345, 665, 42, 'light') + d.C(655, 665, 42, 'light') +
    d.E(500, 570, 58, 245, 'dark') + d.C(500, 300, 95, 'dark') + d.face(500, 300, 125));

  A.add('ladybug', 'Ladybug', { main: R, dark: '#555', accent2: R, pink: P, light: '#fde3c8' }, d =>
    d.L('M300 470 L180 420 M290 600 L165 600 M310 730 L190 790 M700 470 L820 420 M710 600 L835 600 M690 730 L810 790') +
    d.L('M450 185 Q420 110 370 95') + d.L('M550 185 Q580 110 630 95') + d.C(370, 95, 20, 'dark') + d.C(630, 95, 20, 'dark') +
    d.C(500, 275, 125, 'light') + d.face(500, 250, 135) +
    d.C(500, 590, 250) + d.L('M500 345 L500 838') +
    d.C(390, 480, 42, 'dark') + d.C(610, 480, 42, 'dark') + d.C(370, 640, 48, 'dark') + d.C(630, 640, 48, 'dark') + d.C(430, 760, 36, 'dark') + d.C(570, 760, 36, 'dark'));

  A.add('bumblebee', 'Bumblebee', { main: Y, dark: '#8d6e63', light: '#e3f4ff', accent: '#fde3c8', pink: P }, d =>
    d.L('M255 410 Q220 310 170 290') + d.C(170, 288, 22, 'dark') +
    d.E(480, 330, 95, 150, 'light', -20) + d.E(640, 330, 95, 150, 'light', 20) +
    d.P('M790 530 L880 560 L790 600 Z', 'dark') +
    d.L('M460 720 L440 800 M560 725 L570 805 M660 705 L690 780') +
    d.E(560, 565, 250, 180) + d.band(560, 565, 250, 180, 540, 610, 'dark') + d.band(560, 565, 250, 180, 690, 750, 'dark') +
    d.C(300, 540, 150, 'accent') + d.face(300, 535, 175));

  A.add('caterpillar', 'Caterpillar', { main: G, accent: Y, light: LG, dark: R, pink: P }, d => {
    const seg = [[190, 640], [290, 610], [390, 640], [490, 610], [590, 640]];
    let s = seg.map(([x, y]) => d.L(`M${x - 20} ${y + 80} L${x - 30} ${y + 130} M${x + 25} ${y + 80} L${x + 30} ${y + 130}`)).join('');
    s += seg.map(([x, y], i) => d.C(x, y, 92, i % 2 ? 'accent' : 'main')).join('');
    s += d.L('M690 390 Q660 290 610 270') + d.L('M770 400 Q800 300 850 285') + d.C(610, 268, 22, 'dark') + d.C(850, 283, 22, 'dark');
    return s + d.C(730, 520, 150, 'main') + d.face(730, 520, 180) + d.grass(890);
  });

  A.add('snail', 'Snail', { main: '#f3d9b8', accent: O, light: Y, pink: P }, d =>
    d.L('M735 450 L700 300') + d.L('M800 455 L845 310') + d.C(700, 295, 26, 'main') + d.C(845, 305, 26, 'main') +
    d.R(150, 690, 660, 120, 60, 'main') + d.E(765, 600, 115, 165, 'main') +
    d.C(430, 500, 235, 'accent') +
    d.L('M430 500 a30 30 0 1 1 60 0 a60 60 0 1 1 -120 0 a95 95 0 1 1 190 0 a130 130 0 1 1 -260 0 a165 165 0 1 1 330 0') +
    d.face(770, 590, 150) + d.grass(890));

  A.add('ant', 'Ant', { main: R, dark: '#8d6e63', light: '#fde3c8', pink: P }, d =>
    d.L('M430 600 L330 760 L290 770 M480 610 L480 790 L445 800 M530 600 L620 760 L660 770') +
    d.L('M690 390 Q670 260 610 220') + d.L('M760 400 Q790 270 850 240') + d.C(610, 218, 22) + d.C(850, 238, 22) +
    d.E(260, 560, 170, 135) + d.E(470, 560, 90, 75) +
    d.C(700, 500, 145) + d.face(700, 500, 170));

  A.add('dragonfly', 'Dragonfly', { main: T, light: '#e3f4ff', accent: B, pink: P }, d =>
    d.E(300, 360, 220, 70, 'light', -18) + d.E(700, 360, 220, 70, 'light', 18) +
    d.E(325, 540, 190, 58, 'light', 20) + d.E(675, 540, 190, 58, 'light', -20) +
    d.R(465, 440, 70, 460, 35) + d.Lt('M470 560 L530 560 M470 660 L530 660 M470 760 L530 760') +
    d.E(500, 440, 78, 95, 'accent') +
    d.C(500, 270, 115) + d.face(500, 270, 150));

  A.add('firefly', 'Firefly', { main: '#8d6e63', dark: '#bcaaa4', accent: Y, light: '#fde3c8', pink: P }, d =>
    d.Lt('M500 850 L500 930 M390 815 L335 875 M610 815 L665 875 M345 720 L260 740 M655 720 L740 740') +
    d.L('M460 185 Q420 110 370 100') + d.L('M540 185 Q580 110 630 100') + d.C(370, 98, 20, 'accent') + d.C(630, 98, 20, 'accent') +
    d.L('M380 520 L270 470 M380 600 L265 620 M620 520 L730 470 M620 600 L735 620') +
    d.C(500, 710, 125, 'accent') +
    d.E(425, 500, 105, 215, 'main', 10) + d.E(575, 500, 105, 215, 'main', -10) +
    d.C(500, 280, 115, 'light') + d.face(500, 280, 145));

  A.add('grasshopper', 'Grasshopper', { main: G, dark: '#558b2f', light: LG, pink: P }, d =>
    d.L('M200 430 Q260 250 420 200') + d.L('M240 440 Q330 280 470 250') +
    d.L('M320 620 L280 760 L240 770 M420 630 L420 770 L385 780') +
    d.E(480, 560, 270, 105, 'main', -6) + d.E(560, 520, 190, 50, 'light', -6) +
    d.P('M690 380 L830 740 L790 755 L650 400 Z', 'dark') +
    d.E(600, 470, 150, 52, 'main', -42) +
    d.E(230, 530, 125, 115) + d.face(225, 535, 150) + d.grass(890));

  A.add('beetle', 'Beetle', { main: B, dark: PU, light: '#e3f4ff', accent: Y, pink: P }, d =>
    d.L('M300 480 L180 430 M285 620 L160 630 M305 760 L200 830 M700 480 L820 430 M715 620 L840 630 M695 760 L800 830') +
    d.P('M470 170 Q500 60 540 170 Z', 'dark') +
    d.C(500, 270, 120, 'dark') + d.face(500, 265, 140) +
    d.E(500, 590, 235, 265) + d.L('M500 350 L500 855') +
    d.E(410, 500, 40, 80, 'light', 15) + d.E(590, 500, 40, 80, 'light', -15));

  A.add('spider', 'Spider', { main: PU, light: '#ede7f6', pink: P }, d =>
    d.L('M500 40 L500 400') +
    d.L('M360 520 Q250 400 170 470') + d.L('M345 580 Q220 540 140 610') + d.L('M350 650 Q240 680 180 770') + d.L('M380 700 Q310 780 290 860') +
    d.L('M640 520 Q750 400 830 470') + d.L('M655 580 Q780 540 860 610') + d.L('M650 650 Q760 680 820 770') + d.L('M620 700 Q690 780 710 860') +
    d.C(500, 590, 195) + d.face(500, 590, 220));

  A.add('worm', 'Worm', { main: P, accent: BR, pink: '#ff8fab' }, d => {
    const pts = [[330, 800], [345, 700], [400, 620], [490, 580], [580, 540], [640, 460], [650, 380]];
    return pts.map(([x, y]) => d.C(x, y, 82)).join('') + d.C(640, 300, 120) + d.face(640, 300, 150) +
      d.P('M110 870 Q500 690 890 870 Z', 'accent') + d.Lt('M300 820 L320 805 M520 790 L545 800 M690 830 L710 815');
  });

  A.add('moth', 'Moth', { main: '#f3d9b8', accent: GR, light: W, dark: BR, pink: P }, d =>
    d.L('M470 240 Q420 150 360 140') + d.Lt('M440 190 L420 160 M415 165 L395 140 M395 150 L380 120') +
    d.L('M530 240 Q580 150 640 140') + d.Lt('M560 190 L580 160 M585 165 L605 140 M605 150 L620 120') +
    d.P('M470 330 Q300 200 150 330 Q180 520 470 560 Z', 'main') + d.P('M530 330 Q700 200 850 330 Q820 520 530 560 Z', 'main') +
    d.P('M470 520 Q300 560 270 720 Q400 780 480 640 Z', 'accent') + d.P('M530 520 Q700 560 730 720 Q600 780 520 640 Z', 'accent') +
    d.C(300, 400, 48, 'light') + d.C(700, 400, 48, 'light') +
    d.E(500, 540, 62, 210, 'dark') + d.C(500, 300, 92, 'main') + d.face(500, 300, 120));

  A.add('cricket', 'Cricket', { main: BR, dark: '#8d6e63', light: '#f3d9b8', accent: Y, pink: P }, d => {
    const note = (x, y) => d.E(x, y, 26, 20, 'accent', -20) + d.L(`M${x + 22} ${y - 8} L${x + 22} ${y - 90} L${x + 55} ${y - 70}`);
    return note(620, 230) + note(760, 170) +
      d.L('M250 430 Q300 240 520 300') + d.L('M280 450 Q380 330 560 360') +
      d.L('M360 640 L320 770 L280 780 M450 650 L450 780 L415 790') + d.L('M745 560 L830 530 M745 590 L835 610') +
      d.E(520, 580, 240, 120) + d.E(560, 545, 170, 55, 'light') +
      d.P('M660 460 L780 760 L740 775 L620 480 Z', 'dark') + d.E(575, 530, 125, 48, 'main', -40) +
      d.C(290, 560, 125, 'light') + d.face(285, 560, 150) + d.grass(890);
  });

  A.add('praying-mantis', 'Praying Mantis', { main: G, light: LG, dark: '#558b2f', pink: P }, d =>
    d.L('M420 190 Q380 100 320 80') + d.L('M520 190 Q560 100 620 80') +
    d.L('M520 660 L420 850 M560 690 L560 880 M600 670 L700 850') +
    d.E(610, 680, 110, 210, 'main', -25) +
    d.R(440, 330, 70, 330, 35, 'main') +
    d.E(395, 440, 90, 32, 'light', 25) + d.E(330, 390, 30, 80, 'light', 10) +
    d.P('M330 190 Q470 140 610 190 Q560 330 470 360 Q380 330 330 190 Z', 'main') + d.face(470, 240, 150));

  A.add('stick-insect', 'Stick Insect', { main: BR, light: '#f3d9b8', accent: G, pink: P }, d =>
    d.L('M300 505 L230 330 L180 320 M430 510 L400 330 L360 300 M560 510 L600 330 L640 300') +
    d.L('M300 525 L230 700 L180 710 M430 525 L400 700 L360 730 M560 525 L600 700 L640 730') +
    d.L('M800 490 Q860 380 930 360') + d.L('M820 520 Q900 470 950 470') +
    d.R(140, 485, 620, 50, 25, 'main') +
    d.C(790, 510, 85, 'light') + d.face(790, 510, 115) + d.grass(890));

  A.add('roly-poly', 'Roly-Poly', { main: GR, dark: '#90a4ae', light: '#eef3f5', pink: P }, d =>
    d.L('M350 700 L335 760 M450 710 L450 770 M550 710 L560 770 M650 700 L670 760') +
    d.L('M215 560 Q150 470 90 460') + d.L('M225 600 Q140 560 80 580') +
    d.P('M200 700 Q210 330 560 330 Q840 330 840 700 Z', 'main') +
    d.L('M330 700 Q340 430 420 360 M460 700 Q470 400 520 340 M590 700 Q610 400 640 345 M720 700 Q740 470 740 420') +
    d.E(250, 620, 110, 95, 'light') + d.face(245, 620, 130) + d.grass(890));

  A.add('tulip', 'Tulip', { main: R, accent: G, light: '#ffe0e6', pink: P }, d =>
    d.R(480, 480, 40, 400, 20, 'accent') +
    d.P('M495 860 Q300 800 270 560 Q420 620 495 760 Z', 'accent') + d.P('M505 820 Q700 760 740 560 Q590 620 505 720 Z', 'accent') +
    d.P('M320 250 L400 330 L500 200 L600 330 L680 250 Q700 480 500 520 Q300 480 320 250 Z') +
    d.face(500, 405, 170) + d.grass(890));

  A.add('chrysalis', 'Chrysalis', { main: G, light: LG, accent: Y, dark: BR, pink: P }, d =>
    d.R(150, 120, 700, 50, 25, 'dark') + d.L('M500 170 L500 230') +
    d.P('M500 230 Q700 330 660 600 Q630 800 500 880 Q370 800 340 600 Q300 330 500 230 Z', 'main') +
    d.Lt('M400 360 Q500 390 600 360 M370 740 Q500 780 630 740') +
    d.face(500, 550, 200));

  A.add('beehive', 'Beehive', { main: Y, light: '#e3f4ff', accent: '#fde3c8', dark: O, pink: P }, d =>
    d.L('M150 110 L850 110') + d.L('M500 110 L500 230') +
    d.E(500, 300, 110, 70) + d.E(500, 390, 165, 75) + d.E(500, 490, 210, 80) + d.E(500, 600, 240, 85) + d.E(500, 715, 250, 85) +
    d.C(500, 730, 55, 'dark') + d.R(230, 790, 540, 60, 25, 'dark') +
    bee(d, 200, 470, 1.1) + bee(d, 830, 380, 1.1));

  A.add('honey-jar', 'Honey Jar', { main: O, accent: BR, light: '#fff3d6', pink: P }, d =>
    d.R(290, 390, 420, 470, 90) +
    d.P('M290 400 L710 400 L710 470 Q680 540 655 470 Q620 560 585 470 Q540 520 500 470 Q450 570 415 470 Q370 530 340 470 Q310 520 290 470 Z') +
    d.R(260, 300, 480, 110, 40, 'accent') +
    d.E(500, 660, 150, 120, 'light') + d.face(500, 660, 180));

  A.add('daisy', 'Daisy', { main: W, accent: Y, dark: G, pink: P }, d =>
    d.R(480, 560, 40, 330, 20, 'dark') + d.P('M495 800 Q330 790 300 640 Q430 660 495 740 Z', 'dark') +
    petals(d, 500, 380, 10, 175, 95, 55, 'main') +
    d.C(500, 380, 130, 'accent') + d.face(500, 380, 160) + d.grass(890));

  A.add('sunflower', 'Sunflower', { main: Y, accent: BR, dark: G, pink: P }, d => {
    let pts = [];
    for (let i = 0; i < 32; i++) { const a = i * Math.PI / 16, r = i % 2 ? 175 : 290; pts.push([500 + r * Math.cos(a), 390 + r * Math.sin(a)]); }
    return d.R(480, 600, 40, 290, 20, 'dark') + d.P('M505 800 Q680 800 720 660 Q590 670 505 740 Z', 'dark') +
      d.poly(pts, 'main') + d.C(500, 390, 165, 'accent') + d.face(500, 390, 200) + d.grass(890);
  });

  A.add('leaf', 'Leaf', { main: G, light: LG, dark: '#558b2f', accent2: R, pink: P }, d =>
    d.P('M150 850 Q140 330 560 170 Q760 100 870 130 Q900 250 830 440 Q680 850 150 850 Z') +
    d.L('M150 850 Q480 520 860 150') + d.Lt('M330 660 L300 460 M450 540 L440 330 M580 420 L600 250 M330 660 L520 700 M450 540 L650 580 M580 420 L760 440') +
    miniLadybug(d, 610, 610, 1.1));

  A.add('mushroom', 'Mushroom', { main: R, light: '#fff3d6', dark: W, pink: P }, d =>
    d.P('M380 520 L360 820 Q500 880 640 820 L620 520 Z', 'light') +
    d.P('M150 540 Q160 170 500 170 Q840 170 850 540 Q500 610 150 540 Z') +
    d.C(330, 400, 50, 'dark') + d.C(500, 290, 58, 'dark') + d.C(670, 400, 50, 'dark') + d.C(470, 460, 34, 'dark') + d.C(620, 280, 30, 'dark') +
    d.face(500, 690, 150) + d.grass(890));

  A.add('anthill', 'Anthill', { main: '#f3d9b8', accent: R, dark: R, light: W, pink: P }, d =>
    d.P('M120 780 Q300 380 500 360 Q700 380 880 780 Z') + d.E(500, 400, 70, 32, 'dark') +
    d.Lt('M300 700 L330 690 M600 640 L630 650 M420 560 L440 575 M700 760 L730 750') +
    ant(d, 230, 860, 1.3) + ant(d, 480, 860, 1.3) + ant(d, 730, 860, 1.3));

  A.add('bug-jar', 'Bug Jar', { main: '#e3f4ff', accent: R, light: W, dark: '#555', accent2: R, pink: P }, d =>
    d.R(260, 290, 480, 580, 90) + d.R(300, 180, 400, 120, 30, 'accent') +
    d.C(380, 240, 14, 'dark') + d.C(500, 240, 14, 'dark') + d.C(620, 240, 14, 'dark') +
    d.P('M320 850 Q330 700 420 640 Q430 760 470 850 Z', 'light') + d.Lt('M340 360 Q330 420 340 480') +
    miniLadybug(d, 560, 560, 1.5));

  A.add('magnifying-glass', 'Magnifying Glass', { main: B, light: '#e3f4ff', accent: R, dark: '#555', accent2: R, pink: P }, d =>
    group(d.R(610, 590, 110, 330, 40, 'main'), -45, 665, 755) +
    d.C(420, 420, 280, 'main') + d.C(420, 420, 225, 'light') +
    miniLadybug(d, 420, 440, 2) + d.face(420, 330, 90));

  A.add('butterfly-net', 'Butterfly Net', { main: W, accent: O, dark: BR, light: Y, pink: P }, d =>
    d.R(470, 520, 55, 400, 25, 'dark') +
    d.P('M290 330 Q300 700 500 700 Q700 700 710 330 Z') + d.Lt('M360 390 Q370 620 460 660 M500 360 L500 690 M640 390 Q630 620 540 660') +
    d.E(500, 330, 215, 70, 'accent') + d.E(500, 330, 170, 42, 'main') +
    d.E(760, 150, 70, 52, 'light', -25) + d.E(860, 150, 70, 52, 'light', 25) + d.E(775, 220, 50, 38, 'accent', 25) + d.E(845, 220, 50, 38, 'accent', -25) +
    d.E(810, 185, 18, 70, 'dark'));

  A.add('watering-can', 'Watering Can', { main: B, accent: Y, light: '#e3f4ff', dark: G, pink: P }, d =>
    d.P('M660 560 L860 330 L900 370 L700 620 Z', 'main') + d.E(880, 345, 40, 60, 'accent', 40) +
    d.P('M320 360 Q180 360 180 500 Q180 640 320 640', 'none') + d.P('M320 380 Q210 380 210 500 Q210 620 320 620', 'none') +
    d.R(300, 380, 400, 420, 60) + d.E(500, 380, 200, 45, 'accent') +
    d.P('M920 420 Q935 450 920 465 Q905 450 920 420 Z', 'light') + d.P('M870 470 Q885 500 870 515 Q855 500 870 470 Z', 'light') +
    d.face(500, 590, 220) + d.grass(890));
})();
