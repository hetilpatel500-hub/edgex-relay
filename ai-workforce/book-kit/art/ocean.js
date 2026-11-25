// "My First Ocean": 30 friendly sea animals and seaside things for ages 2-5.
// Original drawings only: no licensed characters (a plain striped clownfish,
// not a film character).
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', G = '#7bd389', Y = '#ffd23f', O = '#ff9f43', B = '#6ec6ff', PU = '#b39ddb', P = '#ffb3c7', BR = '#c68b59', T = '#4db6ac', W = '#ffffff', LB = '#e3f4ff', GR = '#b0bec5', SA = '#ffe0b2';

  const f1 = v => v.toFixed(1);
  // a pac-man claw: circle with a notch opening toward angle `a` (degrees)
  const claw = (d, cx, cy, r, a, k) => {
    const t1 = (a - 22) * Math.PI / 180, t2 = (a + 22) * Math.PI / 180;
    return d.P(`M${cx} ${cy} L${f1(cx + r * Math.cos(t2))} ${f1(cy + r * Math.sin(t2))} A${r} ${r} 0 1 1 ${f1(cx + r * Math.cos(t1))} ${f1(cy + r * Math.sin(t1))} Z`, k);
  };
  const bubbles = (d, pts) => pts.map(([x, y, r]) => d.C(x, y, r, 'light')).join('');
  // a side-view fish body facing right, with tail and fins
  const fishBody = (d, cx, cy, rx, ry, k = 'main') =>
    d.P(`M${cx - rx + 30} ${cy} L${cx - rx - 130} ${cy - 140} Q${cx - rx - 90} ${cy} ${cx - rx - 130} ${cy + 140} Z`, k) +
    d.P(`M${cx - 110} ${cy - ry + 20} Q${cx - 20} ${cy - ry - 110} ${cx + 90} ${cy - ry + 25} Z`, k) +
    d.P(`M${cx - 60} ${cy + ry - 15} Q${cx - 10} ${cy + ry + 80} ${cx + 60} ${cy + ry - 15} Z`, k) +
    d.E(cx, cy, rx, ry, k);

  A.add('fish', 'Fish', { main: O, accent: Y, light: LB, pink: P }, d =>
    fishBody(d, 520, 500, 270, 190) + d.band(520, 500, 270, 190, 400, 450, 'accent') + d.band(520, 500, 270, 190, 520, 570, 'accent') +
    d.eye(680, 450, 30) + d.smile(730, 530, 38, 32) + d.C(660, 520, 24, 'pink') +
    bubbles(d, [[860, 300, 32], [910, 210, 20], [840, 150, 14]]));

  A.add('whale', 'Whale', { main: B, light: LB, pink: P }, d =>
    d.water(880) +
    d.P('M720 560 Q820 480 840 390 L890 405 Q870 520 770 620 Z') +
    d.E(820, 350, 85, 40, 'main', -25) + d.E(915, 395, 85, 40, 'main', 50) +
    d.P('M150 560 Q150 330 430 330 Q690 330 790 520 Q820 620 740 660 Q590 730 340 710 Q150 695 150 560 Z') +
    d.L('M190 620 Q420 720 700 650') + d.Lt('M330 690 L345 640 M430 700 L440 650 M530 695 L535 645') +
    d.L('M400 330 Q380 240 330 200 M420 325 Q420 230 420 170 M440 330 Q470 240 520 200') +
    d.eye(300, 470, 30) + d.smile(335, 560, 52, 34) + d.C(250, 545, 26, 'pink'));

  A.add('dolphin', 'Dolphin', { main: '#90caf9', light: LB, pink: P }, d =>
    d.water(880) +
    d.E(150, 610, 85, 38, 'main', 35) + d.E(165, 690, 85, 38, 'main', -40) +
    d.P('M410 400 Q450 240 560 240 Q510 320 530 400 Z') +
    d.E(800, 445, 95, 42, 'main', -12) +
    d.E(470, 520, 320, 150, 'main', -12) +
    d.P('M470 600 Q470 710 390 730 Q420 650 430 590 Z') +
    d.eye(690, 440, 28) + d.smile(745, 485, 35, 22) + d.C(650, 490, 22, 'pink'));

  A.add('octopus', 'Octopus', { main: PU, light: P, pink: P }, d => {
    let s = '';
    for (let i = 0; i < 8; i++) {
      const cx = 200 + i * 86, cy = 700, rot = -(i - 3.5) * 13, t = rot * Math.PI / 180;
      s += d.E(cx, cy, 44, 175, 'main', rot);
    }
    for (let i = 0; i < 8; i++) {
      const cx = 200 + i * 86, cy = 700, rot = -(i - 3.5) * 13, t = rot * Math.PI / 180;
      s += d.C(cx - 175 * Math.sin(t), cy + 175 * Math.cos(t), 34, 'main');
    }
    return s + d.C(500, 400, 235) + d.face(500, 430, 230);
  });

  A.add('crab', 'Crab', { main: R, light: W, pink: '#ffcdd2' }, d =>
    d.L('M300 470 Q220 420 230 350 M700 470 Q780 420 770 350') +
    claw(d, 225, 285, 95, -90) + claw(d, 775, 285, 95, -90) +
    d.L('M290 600 L160 640 L130 720 M300 660 L190 730 L180 800 M340 700 L270 790 L270 850') +
    d.L('M710 600 L840 640 L870 720 M700 660 L810 730 L820 800 M660 700 L730 790 L730 850') +
    d.L('M440 420 L420 300 M560 420 L580 300') + d.C(420, 290, 44, 'light') + d.C(580, 290, 44, 'light') + d.eye(420, 290, 20) + d.eye(580, 290, 20) +
    d.E(500, 580, 260, 175) + d.smile(500, 600, 70, 55) + d.C(380, 610, 30, 'pink') + d.C(620, 610, 30, 'pink'));

  A.add('sea-turtle', 'Sea Turtle', { main: G, accent: LG(), pink: P }, d => {
    const hex = [[590, 540], [545, 618], [455, 618], [410, 540], [455, 462], [545, 462]];
    const rim = [[725, 540], [615, 774], [385, 774], [275, 540], [385, 306], [615, 306]];
    return d.E(270, 380, 115, 52, 'main', -35) + d.E(730, 380, 115, 52, 'main', 35) + d.E(305, 725, 85, 45, 'main', 35) + d.E(695, 725, 85, 45, 'main', -35) +
      d.P('M480 810 L500 880 L520 810 Z') + d.C(500, 195, 105) +
      d.E(500, 540, 230, 270, 'accent') + d.poly(hex, 'main') + hex.map((p, i) => d.L(`M${p[0]} ${p[1]} L${rim[i][0]} ${rim[i][1]}`)).join('') +
      d.face(500, 185, 125);
  });

  A.add('starfish', 'Starfish', { main: O, light: Y, pink: P }, d => {
    const cx = 500, cy = 520, pt = (r, a) => [cx + r * Math.cos(a * Math.PI / 180), cy + r * Math.sin(a * Math.PI / 180)];
    let p = '';
    for (let i = 0; i < 5; i++) {
      const a = -90 + 72 * i, inA = pt(175, a - 36), tip = pt(600, a), inB = pt(175, a + 36);
      p += (i ? '' : `M${f1(inA[0])} ${f1(inA[1])} `) + `Q${f1(tip[0])} ${f1(tip[1])} ${f1(inB[0])} ${f1(inB[1])} `;
    }
    let dots = '';
    for (let i = 0; i < 5; i++) { const a = -90 + 72 * i, q = pt(290, a); dots += d.C(q[0], q[1], 22, 'light'); }
    return d.P(p + 'Z') + dots + d.face(500, 530, 190);
  });

  A.add('seahorse', 'Seahorse', { main: Y, accent: O, pink: P }, d =>
    d.C(430, 790, 75) + d.C(430, 790, 28, 'accent') +
    d.E(470, 690, 72, 120, 'main', -20) +
    d.P('M370 400 Q250 470 360 580 Z', 'accent') +
    d.E(500, 510, 150, 195, 'main', 10) +
    d.Lt('M470 440 Q530 455 580 430 M455 515 Q525 535 600 505 M465 590 Q525 610 585 585') +
    d.P('M500 200 Q540 130 600 180 Z', 'accent') +
    d.R(600, 285, 170, 56, 28, 'main', 0) + d.E(560, 280, 110, 95, 'main', -10) +
    d.eye(560, 262, 26) + d.C(595, 318, 20, 'pink') + d.L('M745 300 L745 326'));

  A.add('jellyfish', 'Jellyfish', { main: '#f8bbd0', light: '#fce4ec', pink: '#ff8fab' }, d => {
    let s = '';
    for (let x = 300; x <= 700; x += 100) s += d.L(`M${x} 540 q35 60 0 120 t0 120 t0 110`);
    s += d.P('M230 520 Q230 200 500 200 Q770 200 770 520 Z');
    for (let x = 260; x <= 740; x += 60) s += d.C(x, 520, 36, 'light');
    return s + d.face(500, 380, 220);
  });

  A.add('shark', 'Shark', { main: GR, light: W, pink: P }, d =>
    d.E(160, 430, 115, 45, 'main', -50) + d.E(170, 640, 95, 40, 'main', 40) +
    d.P('M400 400 Q440 230 560 250 Q500 320 520 400 Z') +
    d.E(490, 540, 330, 160) +
    d.L('M210 600 Q450 710 700 610') +
    d.P('M520 640 Q560 740 470 760 Q480 690 470 640 Z') +
    d.L('M640 480 Q628 520 640 560 M598 485 Q586 520 598 555') +
    d.eye(720, 480, 28) + d.smile(765, 545, 40, 26) + d.C(705, 555, 22, 'pink'));

  A.add('clownfish', 'Clownfish', { main: O, light: W, pink: P }, d =>
    fishBody(d, 520, 500, 260, 180) + d.band(520, 500, 260, 180, 330, 380, 'light') + d.band(520, 500, 260, 180, 470, 530, 'light') + d.band(520, 500, 260, 180, 640, 680, 'light') +
    d.eye(700, 450, 28) + d.smile(740, 525, 30, 26) + d.C(705, 520, 18, 'pink') +
    bubbles(d, [[860, 290, 28], [900, 200, 18]]));

  A.add('pufferfish', 'Pufferfish', { main: Y, light: LB, pink: P }, d => {
    let s = d.E(215, 500, 60, 95, 'main');
    for (let i = 0; i < 16; i++) {
      const a = i / 16 * 2 * Math.PI + 0.2, c = Math.cos(a), sn = Math.sin(a), px = -sn, py = c;
      s += d.poly([[500 + 225 * c + 22 * px, 500 + 225 * sn + 22 * py], [500 + 300 * c, 500 + 300 * sn], [500 + 225 * c - 22 * px, 500 + 225 * sn - 22 * py]]);
    }
    return s + d.C(500, 500, 240) + d.face(540, 470, 230) + bubbles(d, [[850, 180, 26], [900, 110, 16]]);
  });

  A.add('seal', 'Seal', { main: GR, light: '#d7ccc8', dark: '#555', pink: P }, d =>
    d.E(200, 790, 95, 40, 'main', -25) + d.E(230, 850, 95, 40, 'main', 15) +
    d.P('M260 810 Q190 580 390 480 Q520 420 610 470 L660 700 Q610 820 430 830 Q310 830 260 810 Z') +
    d.E(560, 710, 95, 40, 'main', 60) +
    d.C(640, 370, 155) +
    d.R(150, 820, 700, 100, 50, 'light') +
    d.face(640, 350, 190) + d.E(640, 385, 30, 20, 'dark') +
    d.Lt('M560 405 L480 390 M560 420 L480 430 M720 405 L800 390 M720 420 L800 430'));

  A.add('penguin', 'Penguin', { main: '#455a64', light: W, accent: O, pink: P }, d =>
    d.E(430, 860, 70, 30, 'accent') + d.E(570, 860, 70, 30, 'accent') +
    d.E(290, 590, 50, 160, 'main', 20) + d.E(710, 590, 50, 160, 'main', -20) +
    d.E(500, 560, 220, 300) + d.E(500, 620, 160, 225, 'light') + d.E(500, 360, 135, 110, 'light') +
    d.eye(450, 350, 22) + d.eye(550, 350, 22) + d.P('M465 395 L535 395 L500 440 Z', 'accent') +
    d.C(415, 405, 22, 'pink') + d.C(585, 405, 22, 'pink'));

  A.add('lobster', 'Lobster', { main: R, light: '#ffcdd2', pink: '#ffcdd2' }, d =>
    d.L('M430 250 Q350 120 250 90 M570 250 Q650 120 750 90') +
    d.L('M410 450 L300 500 M410 500 L310 570 M590 450 L700 500 M590 500 L690 570') +
    d.L('M420 360 Q320 330 300 250 M580 360 Q680 330 700 250') +
    claw(d, 290, 200, 90, -90) + claw(d, 710, 200, 90, -90) +
    d.E(420, 880, 60, 38, 'main', -30) + d.E(500, 890, 55, 40, 'main') + d.E(580, 880, 60, 38, 'main', 30) +
    d.E(500, 790, 75, 42) + d.E(500, 725, 85, 45) + d.E(500, 655, 95, 50) +
    d.E(500, 440, 115, 165) + d.face(500, 410, 170));

  A.add('stingray', 'Stingray', { main: T, light: '#b2dfdb', pink: P }, d =>
    d.L('M500 690 Q530 820 470 930') +
    d.P('M500 250 Q700 390 880 520 Q700 610 500 700 Q300 610 120 520 Q300 390 500 250 Z') +
    d.C(330, 480, 26, 'light') + d.C(670, 480, 26, 'light') + d.C(420, 610, 20, 'light') + d.C(580, 610, 20, 'light') +
    d.face(500, 470, 190));

  A.add('walrus', 'Walrus', { main: BR, light: '#fff3e0', dark: '#5d4037', pink: P }, d =>
    d.E(500, 650, 300, 210) + d.E(250, 800, 100, 45, 'main', -20) + d.E(750, 800, 100, 45, 'main', 20) +
    d.C(500, 380, 175) +
    d.R(430, 470, 34, 170, 17, 'light') + d.R(536, 470, 34, 170, 17, 'light') +
    d.C(445, 450, 72, 'light') + d.C(555, 450, 72, 'light') + d.E(500, 405, 42, 28, 'dark') +
    d.dot(420, 450, 8) + d.dot(450, 480, 8) + d.dot(470, 440, 8) + d.dot(530, 440, 8) + d.dot(550, 480, 8) + d.dot(580, 450, 8) +
    d.eye(430, 320, 24) + d.eye(570, 320, 24) + d.C(380, 370, 22, 'pink') + d.C(620, 370, 22, 'pink'));

  A.add('sea-otter', 'Sea Otter', { main: BR, light: '#d7ccc8', accent: '#ffd180', dark: '#5d4037', pink: P }, d =>
    d.water(640) +
    d.E(820, 470, 50, 72, 'main', 20) + d.E(760, 500, 50, 72, 'main', -10) +
    d.E(520, 560, 320, 140) +
    d.C(230, 470, 125) + d.C(150, 380, 32) + d.C(300, 370, 32) + d.C(230, 470, 125) +
    d.C(230, 505, 55, 'light') + d.E(230, 480, 22, 15, 'dark') +
    d.eye(185, 430, 20) + d.eye(275, 430, 20) + d.smile(230, 510, 25, 20) +
    d.E(515, 430, 75, 48, 'accent') + d.Lt('M470 415 Q515 395 560 415 M470 440 Q515 420 560 440') +
    d.C(455, 460, 42) + d.C(575, 460, 42));

  A.add('narwhal', 'Narwhal', { main: '#b3e5fc', light: LB, accent: Y, pink: P }, d =>
    d.water(880) +
    d.poly([[215, 405], [55, 215], [250, 380]], 'accent') + d.Lt('M185 375 L215 360 M150 330 L175 318 M115 285 L135 275') +
    d.P('M720 560 Q820 480 840 390 L890 405 Q870 520 770 620 Z') +
    d.E(820, 350, 85, 40, 'main', -25) + d.E(915, 395, 85, 40, 'main', 50) +
    d.P('M150 560 Q150 330 430 330 Q690 330 790 520 Q820 620 740 660 Q590 730 340 710 Q150 695 150 560 Z') +
    d.C(400, 450, 20, 'light') + d.C(480, 420, 16, 'light') + d.C(540, 470, 22, 'light') +
    d.L('M190 620 Q420 720 700 650') +
    d.eye(300, 470, 30) + d.smile(335, 560, 52, 34) + d.C(250, 545, 26, 'pink'));

  A.add('clam', 'Clam & Pearl', { main: P, light: W, pink: '#ff8fab' }, d =>
    d.P('M200 520 Q500 150 800 520 Z') + d.L('M500 520 L500 355 M500 520 L400 375 M500 520 L600 375 M500 520 L310 440 M500 520 L690 440') +
    d.C(500, 530, 95, 'light') + d.face(500, 525, 100) +
    d.P('M190 560 Q500 900 810 560 Z') + d.L('M500 580 L500 760 M420 580 L380 730 M580 580 L620 730 M320 580 L270 680 M680 580 L730 680'));

  A.add('seashell', 'Seashell', { main: '#ffccbc', accent: O, pink: P }, d =>
    d.R(420, 740, 160, 90, 25, 'accent') +
    d.P('M500 780 L210 440 Q220 200 500 190 Q780 200 790 440 Z') +
    d.L('M500 780 L290 290 M500 780 L390 220 M500 780 L500 195 M500 780 L610 220 M500 780 L710 290') +
    d.face(500, 470, 150));

  A.add('coral', 'Coral', { main: '#ff8a80', light: SA, pink: P }, d =>
    d.E(310, 420, 45, 125, 'main', -10) + d.E(690, 420, 45, 125, 'main', 10) + d.E(575, 360, 45, 135, 'main', 15) + d.E(430, 380, 42, 120, 'main', -15) +
    d.E(385, 570, 55, 175, 'main', -30) + d.E(615, 570, 55, 175, 'main', 30) +
    d.E(500, 640, 70, 230) +
    d.E(500, 860, 290, 65, 'light') + d.face(500, 690, 120));

  A.add('seaweed', 'Seaweed', { main: G, light: SA, pink: P }, d =>
    d.P('M330 880 Q240 700 330 540 Q420 380 330 200 Q460 380 380 560 Q310 720 400 880 Z') +
    d.P('M560 880 Q470 660 560 480 Q650 300 580 130 Q720 300 620 490 Q540 680 630 880 Z') +
    d.P('M720 880 Q670 740 730 620 Q790 500 740 380 Q850 520 790 640 Q740 760 780 880 Z') +
    d.E(530, 890, 330, 55, 'light') +
    bubbles(d, [[210, 330, 26], [190, 230, 16], [820, 260, 22]]));

  A.add('submarine', 'Submarine', { main: Y, light: B, accent: O, pink: P }, d =>
    d.E(150, 560, 32, 90, 'accent') + d.R(160, 540, 60, 40, 15, 'main') +
    d.L('M510 300 L510 190 L590 190') + d.R(580, 170, 40, 40, 10, 'accent') +
    d.R(420, 290, 180, 150, 35) +
    d.E(500, 560, 330, 170) + d.P('M250 650 L200 740 L320 720 Z', 'accent') +
    d.C(360, 560, 55, 'light') + d.C(500, 560, 55, 'light') + d.C(640, 560, 55, 'light') +
    bubbles(d, [[860, 300, 30], [900, 210, 18], [830, 150, 14]]));

  A.add('sailboat', 'Sailboat', { main: R, light: W, accent: Y, dark: BR, pink: P }, d =>
    d.water(860) +
    d.R(490, 170, 22, 480, 10, 'dark') + d.P('M512 175 L600 200 L512 225 Z', 'accent') +
    d.P('M530 240 L530 610 L790 610 Z', 'light') + d.P('M470 280 L470 610 L250 610 Z', 'light') +
    d.P('M160 640 L840 640 L730 790 L270 790 Z') + d.C(380, 710, 28, 'light') + d.C(500, 710, 28, 'light') + d.C(620, 710, 28, 'light'));

  A.add('anchor', 'Anchor', { main: GR, light: W, pink: P }, d =>
    d.C(500, 210, 78) + d.C(500, 210, 34, 'light') +
    d.R(465, 280, 70, 500, 30) + d.R(320, 330, 360, 64, 32) +
    d.P('M150 600 L260 560 L240 640 Q300 800 500 810 Q700 800 760 640 L740 560 L850 600 L790 700 L770 670 Q720 880 500 885 Q280 880 230 670 L210 700 Z') +
    d.C(500, 810, 60));

  A.add('lighthouse', 'Lighthouse', { main: W, accent: R, light: Y, dark: '#bcaaa4', pink: P }, d => {
    const xl = y => 400 - (y - 330) * 60 / 490, xr = y => 600 + (y - 330) * 60 / 490;
    const stripe = (y1, y2) => d.poly([[xl(y1), y1], [xr(y1), y1], [xr(y2), y2], [xl(y2), y2]], 'accent');
    return d.Lt('M380 250 L200 190 M380 280 L190 310 M620 250 L800 190 M620 280 L810 310') +
      d.P('M400 330 L600 330 L660 820 L340 820 Z') + stripe(450, 530) + stripe(630, 710) +
      d.R(460, 730, 80, 90, 40, 'dark') +
      d.R(410, 200, 180, 130, 20, 'light') + d.Lt('M470 200 L470 330 M530 200 L530 330') +
      d.P('M380 210 L500 110 L620 210 Z', 'accent') + d.R(370, 320, 260, 32, 12) +
      d.E(500, 850, 290, 60, 'dark');
  });

  A.add('treasure-chest', 'Treasure Chest', { main: BR, accent: Y, accent2: Y, light: Y, pink: P }, d =>
    d.C(170, 820, 48, 'light') + d.C(840, 830, 42, 'light') + d.C(790, 870, 36, 'light') +
    d.R(230, 460, 540, 330, 30) +
    d.P('M230 470 L230 380 Q500 250 770 380 L770 470 Z') +
    d.R(290, 330, 50, 460, 12, 'accent') + d.R(660, 330, 50, 460, 12, 'accent') + d.L('M230 470 L770 470') +
    d.R(455, 430, 90, 110, 22, 'accent2') + d.dot(500, 470, 14) + d.Lt('M500 480 L500 510'));

  A.add('sandcastle', 'Sandcastle', { main: SA, accent: R, dark: BR, pink: P }, d => {
    const cren = (x, y, w) => { let s = ''; for (let i = 0; i < 3; i++) s += d.R(x + i * (w / 3) + 6, y - 45, w / 3 - 12, 60, 8); return s; };
    return d.L('M500 280 L500 160') + d.P('M500 160 L590 185 L500 210 Z', 'accent') +
      cren(410, 300, 180) + d.R(410, 290, 180, 330, 10) +
      cren(200, 440, 150) + cren(650, 440, 150) + d.R(200, 430, 150, 430, 10) + d.R(650, 430, 150, 430, 10) +
      d.R(330, 560, 340, 300, 10) + d.P('M440 860 L440 750 Q500 680 560 750 L560 860 Z', 'dark') +
      d.R(470, 380, 60, 80, 30, 'dark') + d.R(245, 540, 60, 70, 28, 'dark') + d.R(695, 540, 60, 70, 28, 'dark') +
      d.L('M80 860 L920 860');
  });

  A.add('beach-bucket', 'Beach Bucket', { main: B, accent: Y, light: R, pink: P }, d =>
    d.poly([[770, 180], [815, 190], [760, 700], [715, 690]], 'accent') + d.P('M700 670 L780 685 L820 850 Q740 900 660 850 Z', 'accent') +
    d.L('M310 430 Q500 170 690 430') +
    d.P('M300 420 L700 420 L650 830 L350 830 Z') +
    d.poly([[300 + 50 * 150 / 410, 570], [700 - 50 * 150 / 410, 570], [700 - 50 * 220 / 410, 640], [300 + 50 * 220 / 410, 640]], 'light') +
    d.R(270, 380, 460, 70, 30) + d.face(500, 700, 140));

  function LG() { return '#c5e1a5'; }
})();
