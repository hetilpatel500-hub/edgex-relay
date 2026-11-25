// "My First Yummy Food": 30 smiling foods and treats for ages 2-5.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', Y = '#ffd23f', O = '#ff9f43', P = '#ffb3c7', BR = '#c68b59', LBR = '#f1c27d', CR = '#fff3c4',
    G = '#7bd389', B = '#74c0fc', PU = '#b39ddb', CH = '#8d5a3b', W = '#ffffff';
  // a wavy band (lettuce, frosting) from x1 to x2 with its top bumps at yTop and its flat bottom at yBot
  const wave = (d, x1, x2, yTop, yBot, n, k) => {
    const w = (x2 - x1) / n;
    let p = `M${x1} ${yBot} L${x1} ${yTop + 25}`;
    for (let i = 0; i < n; i++) p += ` Q${x1 + w * (i + 0.5)} ${yTop - 25} ${x1 + w * (i + 1)} ${yTop + 25}`;
    return d.P(p + ` L${x2} ${yBot} Z`, k);
  };

  A.add('pancakes', 'Pancakes', { main: LBR, light: W, accent2: Y, pink: P }, d =>
    d.E(500, 840, 400, 70, 'light') +
    d.R(190, 650, 620, 150, 75) + d.R(210, 505, 580, 150, 75) + d.R(230, 360, 540, 150, 75) +
    d.R(440, 300, 120, 80, 16, 'accent2') +
    d.face(500, 428, 170));

  A.add('pizza', 'Pizza', { main: Y, dark: LBR, accent: R, pink: P }, d =>
    d.P('M180 220 Q500 140 820 220 L500 880 Z') +
    d.P('M180 220 Q500 140 820 220 Q835 290 790 300 Q500 230 210 300 Q165 290 180 220 Z', 'dark') +
    d.C(350, 365, 36, 'accent') + d.C(650, 365, 36, 'accent') + d.C(500, 660, 40, 'accent') + d.C(425, 585, 24, 'accent') +
    d.face(500, 440, 180));

  A.add('cupcake', 'Cupcake', { main: P, accent: B, dark: R, pink: '#ff8fab' }, d =>
    d.P('M290 560 L710 560 L650 870 L350 870 Z', 'accent') +
    d.Lt('M410 590 L425 845 M500 590 L500 845 M590 590 L575 845') +
    d.P('M245 585 Q235 470 330 450 Q330 330 450 320 Q500 250 550 320 Q670 330 670 450 Q765 470 755 585 Z') +
    d.L('M500 235 Q510 190 545 170') + d.C(500, 240, 42, 'dark') +
    d.face(500, 470, 190));

  A.add('ice-cream', 'Ice Cream', { main: P, accent: LBR, dark: R, pink: '#ff8fab' }, d =>
    d.P('M360 520 L640 520 L500 900 Z', 'accent') +
    d.Lt('M420 590 L540 740 M500 560 L585 680 M580 590 L460 740') +
    d.P('M300 520 Q260 460 300 400 Q300 220 500 210 Q700 220 700 400 Q740 460 700 520 Q650 560 600 520 Q550 570 500 525 Q450 570 400 525 Q350 565 300 520 Z') +
    d.L('M500 165 Q510 120 545 100') + d.C(500, 180, 40, 'dark') +
    d.face(500, 385, 200));

  A.add('donut', 'Donut', { main: P, light: LBR, accent: B, accent2: Y, pink: '#ff8fab' }, d => {
    const pts = [];
    for (let i = 0; i < 64; i++) { const a = i / 64 * 2 * Math.PI, r = 285 + 20 * Math.sin(8 * a); pts.push([500 + r * Math.cos(a), 500 + r * Math.sin(a)]); }
    const sp = [[330, 380, 30], [670, 370, -30], [300, 560, 70], [700, 560, -70], [420, 290, -20], [590, 290, 25]];
    return d.C(500, 500, 330, 'light') + d.poly(pts) + d.C(500, 470, 92, 'hole') +
      sp.map(([x, y, r], i) => d.E(x, y, 28, 10, i % 2 ? 'accent' : 'accent2', r)).join('') +
      d.face(500, 680, 170);
  });

  A.add('sandwich', 'Sandwich', { main: CR, light: CR, accent: G, accent2: Y, pink: P }, d =>
    d.R(200, 600, 600, 170, 60, 'light') +
    wave(d, 180, 820, 565, 620, 8, 'accent') +
    d.P('M190 520 L810 520 L810 560 L700 560 L660 615 L620 560 L190 560 Z', 'accent2') +
    d.P('M200 525 Q170 300 330 300 Q380 220 500 230 Q620 220 670 300 Q830 300 800 525 Z') +
    d.face(500, 410, 200));

  A.add('taco', 'Taco', { main: Y, accent: G, accent2: R, pink: P }, d =>
    d.P('M190 640 Q200 380 360 300 Q380 250 440 270 Q480 220 540 260 Q600 240 630 290 Q700 300 720 360 Q790 400 810 640 Z', 'accent') +
    d.C(330, 370, 36, 'accent2') + d.C(665, 380, 34, 'accent2') + d.C(500, 300, 30, 'accent2') +
    d.P('M150 730 C150 420 850 420 850 730 Z') +
    d.dot(260, 680, 8) + d.dot(740, 680, 8) + d.dot(320, 590, 8) + d.dot(680, 590, 8) +
    d.face(500, 610, 180));

  A.add('cookie', 'Cookie', { main: LBR, dark: CH, pink: P }, d =>
    d.C(500, 500, 320) +
    [[330, 340, 20], [670, 330, -30], [300, 600, 10], [690, 620, 40], [500, 270, 0], [420, 760, -20], [600, 760, 30]]
      .map(([x, y, r]) => d.E(x, y, 30, 22, 'dark', r)).join('') +
    d.face(500, 510, 230));

  A.add('muffin', 'Muffin', { main: LBR, accent: G, dark: PU, pink: P }, d =>
    d.P('M290 560 L710 560 L660 870 L340 870 Z', 'accent') +
    d.Lt('M410 590 L425 845 M500 590 L500 845 M590 590 L575 845') +
    d.P('M240 580 Q215 300 500 280 Q785 300 760 580 Z') +
    d.C(300, 470, 26, 'dark') + d.C(700, 470, 26, 'dark') + d.C(560, 335, 24, 'dark') + d.C(430, 345, 22, 'dark') +
    d.face(500, 450, 200));

  A.add('bread', 'Bread', { main: LBR, pink: P }, d =>
    d.P('M180 500 Q160 300 320 300 Q400 230 500 240 Q600 230 680 300 Q840 300 820 500 L800 820 L200 820 Z') +
    d.Lt('M330 330 L380 380 M480 290 L520 340 M620 320 L670 370') +
    d.face(500, 580, 230));

  A.add('cheese', 'Cheese', { main: Y, light: '#fff2a8', dark: O, pink: P }, d =>
    d.P('M150 450 L620 260 L850 450 Z', 'light') + d.E(610, 380, 34, 18, 'dark') +
    d.R(150, 450, 700, 330, 30) +
    d.E(270, 560, 40, 30, 'dark') + d.E(730, 700, 45, 32, 'dark') + d.E(770, 530, 28, 20, 'dark') + d.E(250, 710, 26, 20, 'dark') +
    d.face(490, 620, 220));

  A.add('egg', 'Egg', { main: Y, light: W, pink: P }, d =>
    d.P('M220 420 Q180 220 400 230 Q520 120 650 230 Q850 230 820 430 Q900 600 760 720 Q680 860 500 800 Q300 860 230 700 Q100 560 220 420 Z', 'light') +
    d.C(520, 490, 160) + d.face(520, 495, 180));

  A.add('milk', 'Milk', { main: W, light: B, accent: B, pink: P }, d =>
    d.R(420, 190, 160, 60, 8, 'light') +
    d.P('M310 380 L500 240 L690 380 Z', 'light') +
    d.R(310, 380, 380, 480, 20) +
    d.R(345, 650, 310, 150, 50, 'accent') +
    d.face(500, 480, 200));

  A.add('juice-box', 'Juice Box', { main: G, accent: R, accent2: O, light: W, pink: P }, d =>
    d.R(560, 140, 40, 220, 15, 'accent') +
    d.R(300, 330, 400, 520, 30) +
    d.C(500, 720, 100, 'accent2') + d.E(560, 615, 40, 20, 'main', -25) +
    d.face(500, 480, 200));

  A.add('cereal', 'Cereal', { main: B, accent: Y, accent2: R, light: W, pink: P }, d =>
    [[255, 475], [355, 455], [455, 445], [555, 445], [655, 455], [750, 475]].map(([x, y], i) =>
      d.C(x, y, 50, i % 2 ? 'accent2' : 'accent') + d.C(x, y, 17, 'light')).join('') +
    d.P('M160 500 L840 500 Q820 800 500 830 Q180 800 160 500 Z') +
    d.face(500, 640, 220));

  A.add('pie', 'Pie', { main: R, dark: LBR, pink: P }, d =>
    d.P('M170 600 L830 600 L770 850 L230 850 Z', 'dark') +
    d.E(500, 600, 330, 110) +
    d.Lt('M330 540 L470 660 M450 520 L620 660 M590 520 L700 610') +
    d.face(500, 765, 150));

  A.add('spaghetti', 'Spaghetti', { main: Y, light: W, dark: CH, pink: P }, d =>
    d.E(500, 730, 390, 110, 'light') +
    d.P('M200 700 Q190 520 330 480 Q380 380 500 390 Q620 380 670 480 Q810 520 800 700 Z') +
    d.C(410, 450, 46, 'dark') + d.C(570, 430, 50, 'dark') +
    d.Lt('M250 650 Q290 610 330 650 M670 650 Q710 610 750 650') +
    d.face(500, 590, 190));

  A.add('burger', 'Burger', { main: LBR, dark: CH, accent: G, accent2: Y, light: CR, pink: P }, d =>
    d.R(220, 690, 560, 130, 60) +
    d.R(200, 600, 600, 110, 55, 'dark') +
    d.P('M210 600 L790 600 L790 635 L690 635 L650 690 L610 635 L210 635 Z', 'accent2') +
    wave(d, 190, 810, 565, 610, 8, 'accent') +
    d.P('M210 565 Q200 300 500 290 Q800 300 790 565 Z') +
    [[360, 365, -20], [640, 365, 20], [500, 335, 0], [290, 470, -40], [710, 470, 40]].map(([x, y, r]) => d.E(x, y, 18, 10, 'light', r)).join('') +
    d.face(500, 455, 200));

  A.add('hot-dog', 'Hot Dog', { main: LBR, dark: R, accent: Y, pink: P }, d =>
    d.R(180, 330, 640, 180, 90) +
    d.R(90, 450, 820, 120, 60, 'dark') +
    d.Lt('M250 492 L290 472 L330 492 L370 472 L410 492 L450 472 L490 492 L530 472 L570 492 L610 472 L650 492 L690 472 L730 492 L770 472') +
    d.R(180, 510, 640, 210, 100) +
    d.face(500, 610, 180));

  A.add('jelly', 'Jelly', { main: R, light: W, dark: '#e63946', pink: P }, d =>
    d.E(500, 800, 340, 70, 'light') +
    d.P('M260 790 L300 380 Q300 300 380 300 L620 300 Q700 300 700 380 L740 790 Q500 840 260 790 Z') +
    d.P('M290 335 Q300 235 380 255 Q420 185 500 215 Q580 185 620 255 Q700 235 710 335 Z', 'light') +
    d.L('M500 175 Q510 130 545 110') + d.C(500, 185, 38, 'dark') +
    d.face(500, 560, 220));

  A.add('popcorn', 'Popcorn', { main: W, light: CR, accent: R, pink: P }, d => {
    const kern = [[350, 250, 60], [470, 220, 65], [580, 230, 60], [660, 285, 55], [300, 400, 70], [400, 340, 75], [500, 315, 80], [600, 340, 75], [700, 400, 70]];
    const stripe = (f1, f2) => d.poly([[260 + 480 * f1, 420], [260 + 480 * f2, 420], [320 + 360 * f2, 880], [320 + 360 * f1, 880]], 'accent');
    return kern.map(([x, y, r]) => d.C(x, y, r, 'light')).join('') +
      d.P('M260 420 L740 420 L680 880 L320 880 Z') + stripe(0.05, 0.18) + stripe(0.82, 0.95) +
      d.face(500, 640, 200);
  });

  A.add('lollipop', 'Lollipop', { main: P, light: W, accent: B, pink: '#ff8fab' }, d =>
    d.R(480, 560, 40, 340, 18, 'light') +
    d.C(500, 400, 240) +
    d.Lt('M290 330 A220 220 0 0 1 430 190 M570 190 A220 220 0 0 1 710 330 M710 470 A220 220 0 0 1 570 610 M430 610 A220 220 0 0 1 290 470') +
    d.P('M500 690 L400 640 L400 740 Z', 'accent') + d.P('M500 690 L600 640 L600 740 Z', 'accent') + d.C(500, 690, 26, 'accent') +
    d.face(500, 410, 210));

  A.add('birthday-cake', 'Birthday Cake', { main: P, light: W, accent: B, accent2: Y, pink: '#ff8fab' }, d =>
    [400, 485, 570].map(x => d.R(x, 240, 30, 150, 10, 'accent')).join('') +
    [415, 500, 585].map(x => d.P(`M${x} 160 Q${x + 30} 200 ${x} 230 Q${x - 30} 200 ${x} 160 Z`, 'accent2')).join('') +
    d.R(320, 380, 360, 200, 40, 'light') +
    d.R(220, 560, 560, 290, 40) +
    wave(d, 220, 780, 575, 620, 7, 'light') +
    d.dot(390, 470, 10) + d.dot(500, 450, 10) + d.dot(610, 470, 10) +
    d.face(500, 720, 210));

  A.add('waffle', 'Waffle', { main: LBR, light: Y, pink: P }, d => {
    let sq = '';
    [255, 380, 505, 630].forEach((x, i) => [255, 380, 505, 630].forEach((y, j) => {
      if ((i === 1 || i === 2) && (j === 1 || j === 2)) return;
      sq += d.R(x, y, 95, 95, 12, 'light');
    }));
    return d.R(220, 220, 560, 560, 90) + sq + d.face(500, 500, 220);
  });

  A.add('toast', 'Toast', { main: CR, dark: LBR, accent: Y, pink: P }, d =>
    d.P('M220 820 L220 420 Q160 380 180 300 Q210 190 340 210 Q420 150 500 170 Q580 150 660 210 Q790 190 820 300 Q840 380 780 420 L780 820 Z', 'dark') +
    d.P('M260 780 L260 400 Q215 370 225 310 Q245 235 345 250 Q420 200 500 215 Q580 200 655 250 Q755 235 775 310 Q785 370 740 400 L740 780 Z') +
    d.R(430, 380, 140, 100, 16, 'accent') +
    d.face(500, 620, 230));

  A.add('croissant', 'Croissant', { main: LBR, pink: P }, d =>
    d.E(190, 650, 70, 100, 'main', -55) + d.E(810, 650, 70, 100, 'main', 55) +
    d.E(320, 570, 110, 150, 'main', -35) + d.E(680, 570, 110, 150, 'main', 35) +
    d.E(500, 520, 150, 200) +
    d.face(500, 520, 170));

  A.add('ice-pop', 'Ice Pop', { main: O, light: LBR, accent: R, pink: P }, d =>
    d.R(460, 700, 80, 220, 40, 'light') +
    d.R(300, 180, 400, 580, 180) +
    d.face(500, 450, 230));

  A.add('honey', 'Honey', { main: Y, dark: O, accent: O, pink: P }, d =>
    d.E(500, 610, 290, 250) +
    d.R(360, 330, 280, 80, 30) +
    d.E(500, 330, 170, 40, 'dark') +
    d.P('M380 405 L620 405 L620 445 Q605 510 585 450 Q560 470 545 445 Q525 530 500 450 Q470 470 455 445 Q435 500 415 450 L380 450 Z', 'accent') +
    d.face(500, 650, 240));

  A.add('yogurt', 'Yogurt', { main: W, light: P, accent: PU, pink: '#ff8fab' }, d =>
    d.P('M690 375 Q780 335 790 270 L730 260 Q720 320 670 350 Z', 'accent') +
    d.P('M300 380 L700 380 L650 850 L350 850 Z', 'light') +
    d.E(500, 380, 210, 50, 'accent') +
    d.face(500, 600, 220));

  A.add('fries', 'French Fries', { main: R, accent: Y, pink: P }, d =>
    [[310, 300], [370, 240], [430, 280], [490, 210], [550, 260], [610, 230], [670, 290]].map(([x, y]) => d.R(x - 25, y, 50, 400, 10, 'accent')).join('') +
    d.P('M260 480 L740 480 L690 860 L310 860 Z') +
    d.face(500, 660, 210));
})();
