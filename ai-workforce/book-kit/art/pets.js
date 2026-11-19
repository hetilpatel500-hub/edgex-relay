// "My First Pets": 30 friendly pets and pet things for ages 2-5.
// Generic subjects only: no brands, logos, breeds' trade names or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', BR = '#c68b59', DB = '#8d5a3b', TAN = '#e8b27a', GR = '#cfd8dc', PU = '#b39ddb', T = '#4db6ac', W = '#ffffff', CREAM = '#fff3d6';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the same pen with some colour keys swapped, so a pet inside a scene keeps its own colours
  const remap = (d, m) => {
    const k = x => m[x || 'main'] || x || 'main';
    return Object.assign({}, d, {
      E: (cx, cy, rx, ry, kk, rot) => d.E(cx, cy, rx, ry, k(kk), rot), C: (cx, cy, r, kk) => d.C(cx, cy, r, k(kk)),
      P: (path, kk) => d.P(path, k(kk)), R: (x, y, w, h, rx, kk) => d.R(x, y, w, h, rx, k(kk)), poly: (pts, kk) => d.poly(pts, k(kk)),
    });
  };

  // a puppy head centred on x,y; s scales it (s = 1 is 400 wide)
  const pupHead = (d, x, y, s = 1, spot = false) =>
    d.E(x, y, 200 * s, 180 * s) +
    (spot ? d.E(f(x + 72 * s), f(y - 28 * s), 62 * s, 52 * s, 'dark') : '') +
    d.E(f(x - 190 * s), f(y + 20 * s), 60 * s, 130 * s, 'dark', 15) + d.E(f(x + 190 * s), f(y + 20 * s), 60 * s, 130 * s, 'dark', -15) +
    d.E(x, f(y + 75 * s), 100 * s, 72 * s, 'light') + d.E(x, f(y + 45 * s), 36 * s, 24 * s, 'ink') +
    d.L(`M${x} ${f(y + 69 * s)} L${x} ${f(y + 95 * s)} M${f(x - 42 * s)} ${f(y + 90 * s)} Q${f(x - 21 * s)} ${f(y + 118 * s)} ${x} ${f(y + 95 * s)} Q${f(x + 21 * s)} ${f(y + 118 * s)} ${f(x + 42 * s)} ${f(y + 90 * s)}`) +
    d.eye(f(x - 70 * s), f(y - 20 * s), 24 * s) + d.eye(f(x + 70 * s), f(y - 20 * s), 24 * s);

  // a kitten head of radius r centred on x,y: pointy ears, pink nose, whiskers
  const catHead = (d, x, y, r, sleepy = false) => {
    const p = (a, b) => `${f(x + a * r)} ${f(y + b * r)}`;
    const eyes = sleepy
      ? d.L(`M${p(-0.55, -0.02)} Q${p(-0.4, 0.12)} ${p(-0.25, -0.02)} M${p(0.25, -0.02)} Q${p(0.4, 0.12)} ${p(0.55, -0.02)}`)
      : d.eye(f(x - 0.4 * r), f(y - 0.05 * r), 0.14 * r) + d.eye(f(x + 0.4 * r), f(y - 0.05 * r), 0.14 * r);
    return d.P(`M${p(-0.89, -0.28)} L${p(-0.72, -1.2)} L${p(-0.11, -0.83)} Z`) + d.P(`M${p(0.89, -0.28)} L${p(0.72, -1.2)} L${p(0.11, -0.83)} Z`) +
      d.P(`M${p(-0.7, -0.78)} L${p(-0.66, -1.04)} L${p(-0.38, -0.88)} Z`, 'pink') + d.P(`M${p(0.7, -0.78)} L${p(0.66, -1.04)} L${p(0.38, -0.88)} Z`, 'pink') +
      d.C(x, y, r) + eyes +
      d.P(`M${p(-0.11, 0.17)} L${p(0.11, 0.17)} L${p(0, 0.3)} Z`, 'pink') +
      d.L(`M${p(0, 0.3)} Q${p(-0.1, 0.47)} ${p(-0.22, 0.38)} M${p(0, 0.3)} Q${p(0.1, 0.47)} ${p(0.22, 0.38)}`) +
      d.Lt(`M${p(-1.12, 0.08)} L${p(-0.55, 0.2)} M${p(-1.1, 0.36)} L${p(-0.55, 0.3)} M${p(1.12, 0.08)} L${p(0.55, 0.2)} M${p(1.1, 0.36)} L${p(0.55, 0.3)}`);
  };

  // a bone: a shaft with two round knobs at each end, as one closed outline
  const bone = (d, cx, cy, L, Wd, k = 'main') => {
    const x1 = cx - L / 2, x2 = cx + L / 2, h = 0.22 * Wd, r = 0.3 * Wd, a = 0.3 * Wd;
    return d.P(`M${f(x1)} ${f(cy - h)} L${f(x2)} ${f(cy - h)} A${f(r)} ${f(r)} 0 1 1 ${f(x2 + a)} ${f(cy)} A${f(r)} ${f(r)} 0 1 1 ${f(x2)} ${f(cy + h)} L${f(x1)} ${f(cy + h)} A${f(r)} ${f(r)} 0 1 1 ${f(x1 - a)} ${f(cy)} A${f(r)} ${f(r)} 0 1 1 ${f(x1)} ${f(cy - h)} Z`, k);
  };
  const heart = (d, cx, cy, s, k = 'main') =>
    d.P(`M${cx} ${f(cy + s * 0.9)} C${f(cx - s * 1.4)} ${cy} ${f(cx - s * 0.9)} ${f(cy - s * 1.1)} ${cx} ${f(cy - s * 0.45)} C${f(cx + s * 0.9)} ${f(cy - s * 1.1)} ${f(cx + s * 1.4)} ${cy} ${cx} ${f(cy + s * 0.9)} Z`, k);
  // a paw print: one big pad and four toes; s = 1 is about 660 wide
  const paw = (d, cx, cy, s = 1, k = 'main') =>
    d.E(f(cx - 230 * s), f(cy - 140 * s), 70 * s, 95 * s, k, -25) + d.E(f(cx - 85 * s), f(cy - 250 * s), 75 * s, 100 * s, k, -8) +
    d.E(f(cx + 85 * s), f(cy - 250 * s), 75 * s, 100 * s, k, 8) + d.E(f(cx + 230 * s), f(cy - 140 * s), 70 * s, 95 * s, k, 25) +
    d.E(cx, f(cy + 80 * s), 200 * s, 160 * s, k);
  // a budgie sitting with its feet at y; s = 1 is about 330 wide
  const budgie = (d, x, y, s = 1) => {
    const q = (a, b) => `${f(x + a * s)} ${f(y + b * s)}`;
    return d.P(`M${q(60, -60)} L${q(200, 170)} L${q(110, 180)} L${q(20, -20)} Z`, 'accent') +
      d.E(x, f(y - 200 * s), 160 * s, 210 * s) +
      d.P(`M${q(60, -290)} Q${q(190, -200)} ${q(120, -10)} Q${q(60, -60)} ${q(40, -200)} Z`, 'dark') +
      d.C(x, f(y - 430 * s), 125 * s, 'light') +
      d.P(`M${q(-25, -400)} Q${q(0, -340)} ${q(25, -400)} Z`, 'accent2') +
      d.eye(f(x - 50 * s), f(y - 440 * s), 20 * s) + d.eye(f(x + 50 * s), f(y - 440 * s), 20 * s) +
      d.C(f(x - 90 * s), f(y - 380 * s), 18 * s, 'accent') + d.C(f(x + 90 * s), f(y - 380 * s), 18 * s, 'accent') +
      d.L(`M${q(-40, -5)} L${q(-50, 35)} M${q(-10, -2)} L${q(-5, 38)} M${q(30, -5)} L${q(25, 35)} M${q(60, -10)} L${q(70, 30)}`);
  };
  // a hamster centred on x,y; s = 1 is about 560 wide
  const hamster = (d, x, y, s = 1) => {
    const X = a => f(x + a * s), Y2 = b => f(y + b * s);
    return d.C(X(-180), Y2(-230), 60 * s) + d.C(X(180), Y2(-230), 60 * s) + d.C(X(-180), Y2(-230), 30 * s, 'pink') + d.C(X(180), Y2(-230), 30 * s, 'pink') +
      d.E(x, y, 280 * s, 250 * s) + d.E(x, Y2(80), 170 * s, 150 * s, 'light') +
      d.E(X(-130), Y2(0), 70 * s, 55 * s, 'light') + d.E(X(130), Y2(0), 70 * s, 55 * s, 'light') +
      d.eye(X(-70), Y2(-90), 22 * s) + d.eye(X(70), Y2(-90), 22 * s) + d.C(x, Y2(-40), 14 * s, 'pink') +
      d.L(`M${x} ${Y2(-26)} L${x} ${Y2(-8)} M${X(-25)} ${Y2(0)} Q${X(-12)} ${Y2(10)} ${x} ${Y2(-8)} Q${X(12)} ${Y2(10)} ${X(25)} ${Y2(0)}`) +
      d.E(x, Y2(130), 32 * s, 50 * s, 'dark') + d.E(X(-45), Y2(140), 32 * s, 26 * s) + d.E(X(45), Y2(140), 32 * s, 26 * s) +
      d.E(X(-100), Y2(245), 60 * s, 30 * s) + d.E(X(100), Y2(245), 60 * s, 30 * s);
  };

  // ---------------- pets ----------------
  A.add('puppy', 'Puppy', { main: TAN, dark: DB, light: W, accent: R, accent2: Y, pink: P }, d =>
    d.P('M640 760 Q800 700 770 560 Q752 545 735 570 Q760 670 630 715 Z') +
    d.E(500, 760, 180, 170) + d.E(500, 795, 85, 100, 'light') +
    d.R(395, 770, 72, 150, 36) + d.R(533, 770, 72, 150, 36) +
    d.E(430, 920, 58, 32) + d.E(570, 920, 58, 32) +
    d.P('M395 600 Q500 660 605 600 L608 640 Q500 705 392 640 Z', 'accent') + d.C(500, 700, 30, 'accent2') +
    pupHead(d, 500, 420, 1, true));

  A.add('kitten', 'Kitten', { main: O, light: W, accent: B, accent2: Y, pink: P }, d =>
    d.P('M640 820 Q830 800 810 640 Q805 600 770 630 Q785 750 640 770 Z') +
    d.E(500, 765, 165, 165) + d.E(500, 800, 80, 95, 'light') +
    d.E(440, 910, 55, 34) + d.E(560, 910, 55, 34) +
    d.P('M390 600 Q500 650 610 600 L612 630 Q500 682 388 630 Z', 'accent') +
    d.C(500, 672, 28, 'accent2') + d.Lt('M484 680 L516 680') +
    catHead(d, 500, 420, 180));

  A.add('bunny', 'Bunny', { main: W, pink: P, light: W, accent: O, accent2: G }, d =>
    d.E(420, 230, 55, 160, 'main', -10) + d.E(580, 230, 55, 160, 'main', 10) +
    d.E(420, 240, 24, 110, 'pink', -10) + d.E(580, 240, 24, 110, 'pink', 10) +
    d.E(500, 760, 175, 150) + d.E(410, 900, 75, 36) + d.E(590, 900, 75, 36) +
    d.E(640, 625, 22, 55, 'accent2', 35) + d.E(672, 655, 22, 55, 'accent2', 70) +
    d.poly([[598, 630], [660, 690], [440, 850]], 'accent') + d.Lt('M560 700 L590 715 M520 750 L550 765') +
    d.E(560, 690, 42, 32) + d.E(470, 790, 42, 32) +
    d.C(500, 450, 165) +
    d.eye(440, 430, 22) + d.eye(560, 430, 22) + d.E(500, 495, 18, 13, 'pink') +
    d.L('M500 508 L500 528 M470 538 Q485 550 500 528 Q515 550 530 538') +
    d.C(410, 500, 20, 'pink') + d.C(590, 500, 20, 'pink'));

  A.add('hamster', 'Hamster', { main: O, light: CREAM, dark: DB, pink: P }, d =>
    hamster(d, 500, 540, 1) + d.grass(900));

  A.add('guinea-pig', 'Guinea Pig', { main: BR, dark: W, light: W, pink: P }, d =>
    d.E(340, 785, 50, 25) + d.E(480, 800, 50, 25) + d.E(700, 795, 50, 25) +
    d.E(530, 600, 320, 210) + d.E(670, 545, 115, 105, 'dark') +
    d.E(320, 430, 55, 42, 'pink') +
    d.E(270, 560, 150, 140) +
    d.eye(250, 530, 22) + d.C(124, 575, 14, 'pink') + d.L('M126 590 Q142 615 168 604') +
    d.C(210, 612, 22, 'pink') + d.grass(880));

  A.add('budgie', 'Budgie', { main: G, dark: '#4caf50', light: Y, accent: B, accent2: O }, d =>
    d.R(170, 760, 660, 40, 20, 'accent2') + d.C(170, 780, 36, 'accent2') + d.C(830, 780, 36, 'accent2') +
    budgie(d, 500, 770, 1.15));

  A.add('tortoise', 'Tortoise', { main: G, dark: '#4caf50', light: TAN, accent: TAN, pink: P }, d =>
    d.R(300, 700, 90, 150, 40, 'light') + d.R(640, 700, 90, 150, 40, 'light') +
    d.poly([[820, 690], [905, 725], [820, 735]], 'light') +
    d.R(150, 525, 140, 70, 35, 'light') + d.C(140, 560, 90, 'light') +
    d.P('M220 720 Q240 300 520 300 Q800 300 830 720 Z') +
    d.poly([[615, 500], [567.5, 582], [472.5, 582], [425, 500], [472.5, 418], [567.5, 418]], 'dark') +
    d.L('M425 500 L255 506 M472 418 L338 367 M568 418 L704 367 M615 500 L790 506 M472 582 L440 690 M568 582 L600 690') +
    d.R(200, 690, 650, 60, 30, 'dark') +
    d.eye(115, 540, 18) + d.smile(105, 592, 32, 18) + d.C(172, 592, 16, 'pink') + d.grass(900));

  A.add('lizard', 'Lizard', { main: G, dark: '#4caf50', pink: P }, d =>
    d.P('M455 680 Q420 870 590 880 Q700 870 690 780 Q680 730 630 740 Q660 790 610 810 Q520 820 545 680 Z') +
    d.C(270, 385, 17) + d.C(285, 355, 17) + d.C(312, 350, 17) + d.C(730, 385, 17) + d.C(715, 355, 17) + d.C(688, 350, 17) +
    d.C(275, 660, 17) + d.C(285, 690, 17) + d.C(310, 700, 17) + d.C(725, 660, 17) + d.C(715, 690, 17) + d.C(690, 700, 17) +
    d.E(380, 430, 95, 32, 'main', -30) + d.E(620, 430, 95, 32, 'main', 30) +
    d.E(385, 620, 95, 32, 'main', 30) + d.E(615, 620, 95, 32, 'main', -30) +
    d.E(500, 520, 100, 200) +
    d.C(500, 470, 22, 'dark') + d.C(470, 560, 18, 'dark') + d.C(530, 620, 18, 'dark') +
    d.E(500, 290, 110, 100) + d.eye(445, 265, 26) + d.eye(555, 265, 26) + d.smile(500, 320, 45, 25));

  A.add('hermit-crab', 'Hermit Crab', { main: Y, dark: O, accent: R, light: W, pink: P }, d =>
    d.C(600, 470, 220) +
    d.L('M600 470 a30 30 0 1 1 60 0 a60 60 0 1 1 -120 0 a100 100 0 1 1 200 0') +
    d.L('M240 780 L190 870 M300 795 L280 885 M380 795 L400 885') +
    d.L('M240 640 L240 500 M330 640 L330 490') +
    d.C(240, 470, 34, 'light') + d.eye(242, 474, 18) + d.C(330, 460, 34, 'light') + d.eye(332, 464, 18) +
    d.E(330, 700, 160, 105, 'accent') + d.E(140, 690, 70, 55, 'accent') + d.L('M75 682 L135 690') +
    d.smile(300, 720, 40, 22) + d.C(230, 730, 16, 'pink') + d.C(375, 730, 16, 'pink') + d.grass(910));

  A.add('snake', 'Snake', { main: G, dark: '#4caf50', accent: R, pink: P }, d =>
    d.P('M780 830 Q880 800 900 740 Q860 790 790 800 Z') +
    d.E(500, 820, 300, 90) + d.C(340, 860, 18, 'dark') + d.C(500, 875, 18, 'dark') + d.C(660, 860, 18, 'dark') +
    d.E(500, 700, 240, 80) + d.C(360, 730, 16, 'dark') + d.C(500, 745, 16, 'dark') + d.C(640, 730, 16, 'dark') +
    d.R(440, 380, 120, 230, 60) +
    d.E(500, 590, 180, 70) + d.C(420, 600, 15, 'dark') + d.C(580, 600, 15, 'dark') +
    d.E(500, 300, 140, 105) + d.eye(450, 280, 24) + d.eye(550, 280, 24) + d.smile(500, 330, 50, 25) +
    d.C(415, 335, 18, 'pink') + d.C(585, 335, 18, 'pink') +
    d.P('M488 345 L488 425 L468 458 L500 438 L532 458 L512 425 L512 345 Z', 'accent'));

  A.add('pony', 'Pony', { main: TAN, dark: DB, light: CREAM }, d =>
    d.P('M730 500 Q870 520 850 730 Q800 640 740 600 Z', 'dark') +
    d.R(330, 620, 60, 250, 25) + d.R(420, 630, 60, 240, 25) + d.R(560, 630, 60, 240, 25) + d.R(650, 620, 60, 250, 25) +
    d.R(323, 835, 74, 45, 15, 'dark') + d.R(413, 835, 74, 45, 15, 'dark') + d.R(553, 835, 74, 45, 15, 'dark') + d.R(643, 835, 74, 45, 15, 'dark') +
    d.P('M290 560 L230 330 L350 270 L440 520 Z') +
    d.C(345, 255, 40, 'dark') + d.C(375, 315, 40, 'dark') + d.C(400, 375, 38, 'dark') + d.C(420, 435, 36, 'dark') +
    d.E(500, 560, 250, 150) +
    d.poly([[290, 225], [318, 140], [345, 235]]) +
    d.E(245, 295, 135, 90, 'main', -35) + d.C(290, 212, 30, 'dark') +
    d.E(168, 355, 66, 54, 'light', -35) + d.dot(158, 352, 9) + d.L('M168 394 Q192 404 216 390') +
    d.eye(265, 268, 20) + d.grass(905));

  A.add('fish-bowl', 'Fish Bowl', { main: B, light: W, accent: G, accent2: O, dark: GR, pink: P }, d =>
    d.P('M320 270 Q120 380 170 620 Q230 880 500 880 Q770 880 830 620 Q880 380 680 270 Z') +
    d.E(500, 270, 185, 38, 'light') +
    d.L('M180 420 Q340 450 500 420 Q660 390 820 420') +
    d.P('M290 800 Q250 700 290 620 Q330 700 330 800 Z', 'accent') + d.P('M700 790 Q740 700 700 640 Q670 700 670 790 Z', 'accent') +
    d.C(380, 820, 36, 'dark') + d.C(450, 835, 34, 'accent2') + d.C(520, 830, 36, 'dark') + d.C(590, 835, 34, 'accent2') + d.C(630, 812, 30, 'dark') +
    d.poly([[630, 590], [725, 520], [725, 660]], 'accent2') +
    d.P('M500 515 Q540 470 590 520 Z', 'accent2') + d.E(520, 590, 130, 90, 'accent2') +
    d.eye(460, 570, 20) + d.smile(430, 615, 22, 14) + d.C(500, 625, 14, 'pink') +
    d.C(400, 475, 16, 'light') + d.C(420, 445, 10, 'light'));

  A.add('spotty-dog', 'Spotty Dog', { main: W, dark: '#444', light: W, accent: R }, d =>
    d.P('M710 500 Q800 420 790 330 Q770 320 760 345 Q760 420 700 460 Z') +
    d.R(320, 600, 65, 230, 30) + d.R(400, 610, 65, 220, 30) + d.R(580, 610, 65, 220, 30) + d.R(660, 600, 65, 230, 30) +
    d.E(500, 560, 230, 130) +
    d.C(470, 540, 40, 'dark') + d.C(590, 600, 34, 'dark') + d.C(630, 505, 26, 'dark') + d.C(380, 620, 22, 'dark') +
    d.E(310, 410, 130, 115) + d.E(395, 395, 50, 95, 'dark', -15) +
    d.E(210, 455, 75, 55, 'light') + d.E(148, 440, 24, 18, 'ink') + d.L('M152 472 Q190 497 226 480') +
    d.eye(275, 385, 24) + d.C(250, 330, 22, 'dark') + d.grass(860));

  A.add('sleepy-cat', 'Sleepy Cat', { main: GR, light: W, accent: PU, pink: P }, d =>
    d.E(520, 820, 390, 75, 'accent') +
    d.P('M800 640 Q900 760 760 850 Q600 880 330 860 Q270 855 275 820 Q285 795 330 805 Q600 830 740 790 Q820 740 780 650 Z') +
    d.E(560, 620, 290, 170) +
    catHead(d, 330, 560, 150, true) +
    d.L('M640 300 L700 300 L640 360 L700 360 M740 210 L780 210 L740 250 L780 250'));

  // ---------------- pet scenes ----------------
  A.add('bath-time', 'Bath Time', { main: B, light: W, dark: DB, pup: TAN, accent: TAN, pink: P }, d =>
    d.C(260, 860, 35, 'light') + d.C(740, 860, 35, 'light') +
    d.P('M150 540 L850 540 Q850 820 640 845 L360 845 Q150 820 150 540 Z') +
    pupHead(remap(d, { main: 'pup' }), 500, 360, 0.8) +
    d.R(120, 510, 760, 60, 30, 'light') +
    d.C(230, 500, 55, 'light') + d.C(320, 478, 58, 'light') + d.C(680, 478, 58, 'light') + d.C(770, 500, 55, 'light') +
    d.E(380, 525, 45, 32, 'pup') + d.E(620, 525, 45, 32, 'pup') +
    d.C(160, 330, 40, 'light') + d.C(845, 300, 34, 'light') + d.C(790, 195, 24, 'light') + d.C(205, 210, 22, 'light'));

  A.add('kitten-box', 'Kitten in a Box', { main: BR, dark: TAN, light: Y, cat: O, pink: P }, d =>
    catHead(remap(d, { main: 'cat' }), 500, 400, 150) +
    d.R(230, 520, 540, 380, 12) +
    d.poly([[230, 522], [130, 400], [200, 370], [320, 522]], 'dark') + d.poly([[770, 522], [870, 400], [800, 370], [680, 522]], 'dark') +
    d.R(460, 522, 80, 110, 6, 'light') +
    d.E(420, 525, 45, 30, 'cat') + d.E(580, 525, 45, 30, 'cat'));

  A.add('dog-house', 'Dog House', { main: R, accent: B, light: W, dark: DB, accent2: Y, pup: TAN, pink: P }, d =>
    d.R(200, 400, 600, 470, 0) +
    d.poly([[120, 430], [500, 140], [880, 430]], 'accent') +
    bone(d, 500, 335, 150, 70, 'accent2') +
    d.P('M380 870 L380 640 A120 120 0 0 1 620 640 L620 870 Z', 'light') +
    pupHead(remap(d, { main: 'pup' }), 500, 735, 0.55) + d.grass(900));

  A.add('birdcage', 'Birdcage', { main: Y, light: W, dark: BR, accent: B, accent2: O, bud: G, budw: '#4caf50', budh: Y }, d =>
    d.C(500, 140, 32, 'none') +
    d.P('M220 780 L220 420 Q220 180 500 180 Q780 180 780 420 L780 780 Z', 'light') +
    d.L('M290 240 L290 780 M360 201 L360 780 M430 184 L430 780 M500 180 L500 780 M570 184 L570 780 M640 201 L640 780 M710 240 L710 780') +
    d.E(500, 182, 60, 26) +
    d.R(330, 600, 340, 28, 14, 'dark') +
    budgie(remap(d, { main: 'bud', dark: 'budw', light: 'budh' }), 500, 605, 0.62) +
    d.R(180, 780, 640, 80, 20));

  A.add('best-friends', 'Best Friends', { main: TAN, dark: DB, light: W, accent: R, cat: O, pink: P }, d =>
    heart(d, 505, 200, 70, 'accent') +
    d.E(320, 750, 140, 160) + d.E(270, 900, 48, 28) + d.E(370, 900, 48, 28) +
    pupHead(d, 320, 470, 0.72) +
    d.P('M780 850 Q900 820 880 700 Q875 670 850 690 Q860 780 780 800 Z', 'cat') +
    d.E(690, 765, 130, 135, 'cat') + d.E(640, 890, 45, 26, 'cat') + d.E(740, 890, 45, 26, 'cat') +
    catHead(remap(d, { main: 'cat' }), 690, 500, 140));

  // ---------------- pet things ----------------
  A.add('bone', 'Bone', { main: CREAM, pink: P }, d =>
    group(bone(d, 500, 500, 520, 260) + d.face(500, 488, 150), -20));

  A.add('food-bowl', 'Food Bowl', { main: R, dark: DB, light: W, accent: BR }, d =>
    d.E(500, 560, 300, 70, 'dark') +
    d.C(380, 545, 32, 'accent') + d.C(450, 525, 32, 'accent') + d.C(520, 535, 32, 'accent') + d.C(600, 545, 32, 'accent') +
    d.C(420, 492, 30, 'accent') + d.C(490, 482, 30, 'accent') + d.C(560, 497, 30, 'accent') + d.C(485, 440, 28, 'accent') +
    d.P('M200 560 Q500 650 800 560 L730 820 Q500 870 270 820 Z') +
    paw(d, 500, 740, 0.2, 'light'));

  A.add('collar', 'Collar', { main: B, light: W, accent2: Y }, d =>
    d.E(500, 430, 330, 210) + d.E(500, 415, 255, 140, 'light') +
    d.R(140, 375, 95, 115, 16, 'accent2') + d.R(166, 402, 43, 61, 8, 'light') +
    d.C(330, 575, 14, 'accent2') + d.C(420, 598, 14, 'accent2') + d.C(580, 598, 14, 'accent2') + d.C(670, 575, 14, 'accent2') +
    d.C(500, 665, 24, 'none') +
    heart(d, 500, 770, 80, 'accent2'));

  A.add('yarn', 'Ball of Yarn', { main: PU, accent: '#9575cd' }, d =>
    d.L('M700 653 Q800 760 700 830 Q600 900 780 930') +
    d.C(480, 480, 280) +
    d.L('M250 320 Q480 400 710 320 M201 460 Q480 560 759 460 M238 620 Q480 690 722 620') +
    d.Lt('M390 215 Q320 480 390 745 M580 218 Q650 480 580 742'));

  A.add('toy-mouse', 'Toy Mouse', { main: GR, pink: P, light: W }, d =>
    d.L('M828 650 Q940 700 900 800 Q860 880 940 920') +
    d.C(520, 405, 80) + d.C(645, 415, 70) + d.C(520, 405, 40, 'pink') + d.C(645, 415, 34, 'pink') +
    d.P('M150 650 Q320 380 620 420 Q840 450 830 640 Q820 740 620 740 L300 740 Q180 730 150 650 Z') +
    d.eye(330, 560, 22) + d.C(152, 650, 22, 'pink') +
    d.Lt('M150 632 L72 600 M150 662 L70 672') +
    d.Lt('M330 700 L360 700 M400 700 L430 700 M470 700 L500 700 M540 700 L570 700 M610 700 L640 700'));

  A.add('pet-bed', 'Pet Bed', { main: B, light: Y, accent: W, pink: P }, d =>
    d.E(500, 640, 390, 210) + d.E(500, 600, 285, 120, 'light') +
    bone(d, 500, 585, 220, 100, 'accent') +
    paw(d, 500, 790, 0.13, 'accent'));

  A.add('hamster-wheel', 'Hamster Wheel', { main: B, light: W, dark: PU, accent: O, accent2: Y, pink: P }, d =>
    d.P('M470 450 L280 890 L340 890 L490 470 Z', 'dark') + d.P('M530 450 L720 890 L660 890 L510 470 Z', 'dark') +
    d.C(500, 450, 300) + d.C(500, 450, 250, 'light') +
    [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map(a => {
      const r = a * Math.PI / 180;
      return d.Lt(`M${f(500 + 250 * Math.cos(r))} ${f(450 + 250 * Math.sin(r))} L${f(500 + 300 * Math.cos(r))} ${f(450 + 300 * Math.sin(r))}`);
    }).join('') +
    d.Lt('M500 410 L500 200 M465 430 L283 325 M535 430 L717 325') +
    d.C(500, 450, 40, 'accent2') +
    hamster(remap(d, { main: 'accent' }), 500, 600, 0.38) +
    d.R(220, 885, 560, 40, 20, 'dark'));

  A.add('scratching-post', 'Scratching Post', { main: TAN, dark: PU, accent: R, light: W }, d =>
    d.R(420, 300, 160, 510, 20) +
    d.Lt('M420 345 L580 345 M420 395 L580 395 M420 445 L580 445 M420 495 L580 495 M420 545 L580 545 M420 595 L580 595 M420 645 L580 645 M420 695 L580 695 M420 745 L580 745') +
    d.R(230, 800, 540, 90, 20, 'dark') +
    d.R(300, 240, 400, 70, 25, 'dark') +
    d.L('M650 310 L650 520') + d.C(650, 560, 42, 'accent') + d.Lt('M620 545 Q650 525 680 545'));

  A.add('pet-carrier', 'Pet Carrier', { main: T, dark: DB, light: W, accent: O, pink: P }, d =>
    d.P('M400 390 L400 330 Q400 280 450 280 L550 280 Q600 280 600 330 L600 390 L560 390 L560 335 Q560 320 545 320 L455 320 Q440 320 440 335 L440 390 Z', 'dark') +
    d.R(170, 380, 660, 440, 60) +
    d.R(215, 470, 50, 18, 9, 'light') + d.R(215, 530, 50, 18, 9, 'light') + d.R(215, 590, 50, 18, 9, 'light') +
    d.R(735, 470, 50, 18, 9, 'light') + d.R(735, 530, 50, 18, 9, 'light') + d.R(735, 590, 50, 18, 9, 'light') +
    d.C(500, 590, 165, 'light') +
    catHead(remap(d, { main: 'accent' }), 500, 625, 100));

  A.add('paw-print', 'Paw Print', { main: P, accent: R }, d =>
    paw(d, 500, 560, 1) + heart(d, 500, 650, 60, 'accent'));

  A.add('treat-jar', 'Treat Jar', { main: CREAM, light: W, accent: R, pink: P }, d =>
    d.R(270, 330, 460, 520, 70, 'light') +
    group(bone(d, 450, 560, 200, 90), -25, 450, 560) +
    group(bone(d, 570, 680, 160, 90), 20, 570, 680) +
    group(bone(d, 450, 765, 180, 90), -10, 450, 765) +
    d.C(500, 210, 40, 'accent') + d.R(240, 230, 520, 110, 30, 'accent'));
})();
