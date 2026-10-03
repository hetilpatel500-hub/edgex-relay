// "My First Space": 30 friendly space things for ages 2-5.
// Original drawings only: no agency logos, no national flags, no licensed
// characters (the alien, robot and space pets are our own).
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', G = '#7bd389', Y = '#ffd23f', O = '#ff9f43', B = '#6ec6ff', PU = '#b39ddb', P = '#ffb3c7', BR = '#c68b59', W = '#ffffff', LB = '#e3f4ff', GR = '#b0bec5', DG = '#90a4ae', CR = '#fff3c4';

  const f1 = v => v.toFixed(1);
  const rad = a => a * Math.PI / 180;
  // five-point star polygon centred on cx,cy
  const starPts = (cx, cy, Ro, Ri, rot = -90) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const r = i % 2 ? Ri : Ro, a = rad(rot + i * 36);
      pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
    return pts;
  };
  const star = (d, cx, cy, Ro, Ri, k = 'accent') => d.poly(starPts(cx, cy, Ro, Ri || Ro * 0.45), k);
  const sparkles = (d, pts, k = 'accent') => pts.map(([x, y, r]) => star(d, x, y, r, r * 0.45, k)).join('');
  // a horizontal stripe across a circle between y1 and y2
  const hband = (d, cx, cy, Rr, y1, y2, k) => {
    const left = [], right = [];
    for (let i = 0; i <= 12; i++) {
      const y = y1 + (y2 - y1) * i / 12, w = Math.sqrt(Math.max(0, Rr * Rr - (y - cy) ** 2));
      right.push([cx + w, y]); left.unshift([cx - w, y]);
    }
    return d.poly(right.concat(left), k);
  };
  // a classic rocket centred on x, nose at top `y`, scale s
  const rocket = (d, x, y, s) => {
    const X = v => f1(x + v * s), Y = v => f1(y + v * s);
    return d.P(`M${X(-100)} ${Y(560)} Q${X(-80)} ${Y(700)} ${X(0)} ${Y(780)} Q${X(80)} ${Y(700)} ${X(100)} ${Y(560)} Z`, 'accent2') +
      d.P(`M${X(-140)} ${Y(400)} L${X(-260)} ${Y(560)} L${X(-260)} ${Y(640)} L${X(-140)} ${Y(590)} Z`, 'accent') +
      d.P(`M${X(140)} ${Y(400)} L${X(260)} ${Y(560)} L${X(260)} ${Y(640)} L${X(140)} ${Y(590)} Z`, 'accent') +
      d.P(`M${X(0)} ${Y(0)} Q${X(140)} ${Y(130)} ${X(140)} ${Y(400)} L${X(140)} ${Y(580)} L${X(-140)} ${Y(580)} L${X(-140)} ${Y(400)} Q${X(-140)} ${Y(130)} ${X(0)} ${Y(0)} Z`) +
      d.P(`M${X(-70)} ${Y(65)} Q${X(0)} ${Y(-10)} ${X(70)} ${Y(65)} Z`, 'accent') +
      d.R(+X(-110), +Y(560), 220 * s, 50 * s, 15 * s, 'dark') +
      d.C(+X(0), +Y(290), 85 * s, 'light');
  };

  A.add('rocket', 'Rocket', { main: W, accent: R, accent2: O, dark: GR, light: B, pink: P }, d =>
    rocket(d, 500, 90, 1) + d.face(500, 375, 120) +
    sparkles(d, [[180, 220, 50], [830, 260, 40], [150, 640, 34], [850, 700, 46]]));

  A.add('astronaut', 'Astronaut', { main: W, dark: GR, light: LB, accent: R, pink: P }, d =>
    d.R(330, 400, 340, 300, 40, 'dark') +
    d.R(395, 700, 90, 160, 40) + d.R(515, 700, 90, 160, 40) +
    d.E(430, 870, 75, 38, 'dark') + d.E(570, 870, 75, 38, 'dark') +
    d.E(305, 580, 58, 130, 'main', 35) + d.E(695, 580, 58, 130, 'main', -35) +
    d.C(250, 670, 48, 'dark') + d.C(750, 670, 48, 'dark') +
    d.R(355, 470, 290, 270, 90) +
    d.R(445, 540, 110, 80, 15, 'accent') + d.dot(475, 580, 12) + d.dot(525, 580, 12) +
    d.C(500, 300, 175) + d.C(500, 310, 130, 'light') + d.face(500, 300, 150));

  A.add('moon', 'Moon', { main: CR, dark: '#ffe082', pink: P }, d =>
    d.C(500, 500, 330) +
    d.C(370, 320, 48, 'dark') + d.C(660, 330, 38, 'dark') + d.C(660, 690, 58, 'dark') + d.C(300, 610, 34, 'dark') + d.C(460, 740, 28, 'dark') +
    d.face(500, 500, 260));

  A.add('crescent-moon', 'Sleepy Moon', { main: Y, accent: Y, pink: P }, d =>
    d.P('M600 140 A360 360 0 1 0 600 860 A500 500 0 0 1 600 140 Z') +
    d.L('M300 440 Q335 470 370 440') + d.L('M330 560 Q365 595 405 560') +
    d.C(300, 515, 22, 'pink') +
    d.Lt('M620 330 L700 330 L620 410 L700 410 M740 230 L800 230 L740 290 L800 290') +
    sparkles(d, [[760, 600, 55], [640, 760, 36], [860, 440, 30]]));

  A.add('sun', 'Sun', { main: Y, accent: O, pink: P }, d => {
    let rays = '';
    for (let i = 0; i < 12; i++) {
      const a = rad(i * 30), b1 = rad(i * 30 - 9), b2 = rad(i * 30 + 9);
      rays += d.poly([[500 + 255 * Math.cos(b1), 500 + 255 * Math.sin(b1)], [500 + 420 * Math.cos(a), 500 + 420 * Math.sin(a)], [500 + 255 * Math.cos(b2), 500 + 255 * Math.sin(b2)]], 'accent');
    }
    return rays + d.C(500, 500, 250) + d.face(500, 500, 230);
  });

  A.add('star', 'Star', { main: Y, accent: Y, pink: P }, d =>
    star(d, 500, 530, 400, 185, 'main') + d.face(500, 560, 170) +
    sparkles(d, [[140, 160, 40], [860, 150, 34], [880, 860, 38]]));

  A.add('earth', 'Earth', { main: B, accent: G, pink: P }, d =>
    d.C(500, 500, 330) +
    d.P('M245 340 Q320 250 420 290 Q445 360 360 400 Q280 425 245 340 Z', 'accent') +
    d.P('M640 245 Q760 300 785 420 Q700 435 650 360 Q620 300 640 245 Z', 'accent') +
    d.P('M350 700 Q430 675 490 750 Q440 810 360 785 Q320 740 350 700 Z', 'accent') +
    d.P('M690 640 Q760 620 770 680 Q730 730 690 700 Z', 'accent') +
    d.face(500, 520, 240));

  A.add('saturn', 'Saturn', { main: Y, accent: O, pink: P }, d =>
    d.P('M70 560 A430 115 0 0 1 930 560 L795 560 A295 62 0 0 0 205 560 Z', 'accent') +
    d.C(500, 490, 235) +
    d.P('M70 560 A430 115 0 0 0 930 560 L795 560 A295 62 0 0 1 205 560 Z', 'accent') +
    d.face(500, 450, 200) +
    sparkles(d, [[150, 180, 40], [850, 210, 32], [820, 820, 38]], 'main'));

  A.add('jupiter', 'Jupiter', { main: '#ffcc80', accent: O, dark: R, pink: P }, d =>
    d.C(500, 500, 320) +
    hband(d, 500, 500, 320, 270, 325, 'accent') + hband(d, 500, 500, 320, 680, 740, 'accent') +
    d.E(700, 610, 62, 38, 'dark') +
    d.face(470, 470, 230));

  A.add('mars', 'Mars', { main: R, light: W, dark: '#e57373', pink: '#ffcdd2' }, d =>
    d.C(500, 500, 300) +
    d.P('M330 255 Q500 170 670 255 Q590 300 500 285 Q410 300 330 255 Z', 'light') +
    d.C(330, 470, 34, 'dark') + d.C(690, 470, 42, 'dark') + d.C(620, 700, 30, 'dark') + d.C(390, 690, 24, 'dark') +
    d.face(500, 520, 210));

  A.add('alien', 'Friendly Alien', { main: G, accent: Y, light: W, pink: P }, d =>
    d.L('M420 250 L370 120 M580 250 L630 120') + d.C(365, 105, 38, 'accent') + d.C(635, 105, 38, 'accent') +
    d.R(410, 760, 70, 120, 30) + d.R(520, 760, 70, 120, 30) +
    d.E(355, 650, 45, 115, 'main', 40) + d.E(645, 650, 45, 115, 'main', -40) +
    d.R(390, 560, 220, 260, 90) + d.C(500, 690, 40, 'accent') +
    d.E(500, 390, 240, 190) +
    d.E(415, 380, 62, 72, 'light') + d.E(585, 380, 62, 72, 'light') + d.eye(420, 390, 34) + d.eye(580, 390, 34) +
    d.smile(500, 470, 55, 40) + d.C(330, 455, 26, 'pink') + d.C(670, 455, 26, 'pink'));

  A.add('flying-saucer', 'Flying Saucer', { main: GR, light: LB, accent: Y, accent2: '#fff59d', pink: P }, d =>
    d.P('M400 610 L320 880 L680 880 L600 610 Z', 'accent2') +
    d.E(500, 540, 380, 115) +
    d.P('M320 500 Q320 250 500 250 Q680 250 680 500 Z', 'light') + d.face(500, 395, 160) +
    d.C(260, 560, 26, 'accent') + d.C(390, 600, 26, 'accent') + d.C(610, 600, 26, 'accent') + d.C(740, 560, 26, 'accent') +
    sparkles(d, [[140, 200, 40], [860, 230, 34]]));

  A.add('comet', 'Comet', { main: Y, accent: B, accent2: LB, pink: P }, d =>
    d.P('M610 230 Q380 320 120 560 Q420 420 630 390 Z', 'accent2') +
    d.P('M620 330 Q380 480 180 800 Q450 600 680 440 Z', 'accent') +
    d.P('M720 440 Q600 640 470 900 Q660 700 800 450 Z', 'accent2') +
    d.C(700, 330, 150) + d.face(700, 330, 150) +
    sparkles(d, [[860, 130, 34], [230, 220, 30]], 'main'));

  A.add('shooting-star', 'Shooting Star', { main: Y, accent: Y, pink: P }, d =>
    d.L('M470 520 L130 740') + d.L('M520 600 L240 880') + d.L('M420 450 L90 590') +
    star(d, 640, 380, 260, 120, 'main') + d.face(640, 405, 130) +
    sparkles(d, [[160, 180, 36], [880, 760, 40]]));

  A.add('telescope', 'Telescope', { main: B, dark: GR, light: LB, accent: Y, pink: P }, d =>
    d.L('M470 520 L320 880 M470 520 L640 880 M470 520 L480 880') +
    d.poly([[190, 600], [700, 270], [770, 380], [260, 710]]) +
    d.poly([[140, 640], [205, 600], [250, 670], [185, 715]], 'dark') +
    d.R(330, 480, 120, 60, 20, 'accent') +
    d.E(735, 325, 45, 68, 'light', -33) +
    d.C(470, 520, 34, 'dark') +
    sparkles(d, [[830, 150, 46], [640, 120, 30], [900, 520, 32]]));

  A.add('satellite', 'Satellite', { main: '#ffe082', accent: B, light: W, dark: GR, pink: P }, d =>
    d.L('M330 500 L420 500 M580 500 L670 500') +
    d.R(100, 440, 240, 120, 10, 'accent') + d.Lt('M180 440 L180 560 M260 440 L260 560 M100 500 L340 500') +
    d.R(660, 440, 240, 120, 10, 'accent') + d.Lt('M740 440 L740 560 M820 440 L820 560 M660 500 L900 500') +
    d.L('M500 410 L500 300') + d.P('M410 300 Q500 360 590 300 Z', 'light') + d.C(500, 270, 18, 'dark') +
    d.R(410, 410, 180, 190, 30) + d.face(500, 500, 130));

  A.add('moon-rover', 'Moon Rover', { main: W, accent: Y, dark: GR, light: LB, pink: P }, d =>
    d.L('M60 745 Q280 720 500 745 T 940 745') +
    d.L('M650 440 L650 300') + d.E(650, 285, 75, 28, 'light', -15) +
    d.R(220, 430, 560, 170, 40) + d.R(260, 460, 140, 70, 15, 'light') +
    d.C(300, 660, 82, 'accent') + d.C(500, 660, 82, 'accent') + d.C(700, 660, 82, 'accent') +
    d.C(300, 660, 30, 'dark') + d.C(500, 660, 30, 'dark') + d.C(700, 660, 30, 'dark') +
    d.face(580, 510, 120));

  A.add('space-helmet', 'Space Helmet', { main: W, light: LB, accent: R, pink: P }, d =>
    d.R(280, 700, 440, 110, 45, 'accent') +
    d.C(500, 450, 300) +
    d.C(200, 450, 42, 'accent') + d.C(800, 450, 42, 'accent') +
    d.E(500, 450, 210, 175, 'light') +
    d.Lt('M370 360 Q410 315 470 305') + d.Lt('M350 410 Q355 395 362 385'));

  A.add('asteroid', 'Space Rock', { main: '#bcaaa4', dark: '#a1887f', pink: P }, d =>
    d.P('M260 420 Q300 230 480 240 Q640 200 740 320 Q830 450 760 600 Q700 760 520 770 Q330 790 250 660 Q190 540 260 420 Z') +
    d.C(340, 360, 36, 'dark') + d.C(650, 330, 30, 'dark') + d.C(690, 620, 44, 'dark') + d.C(300, 600, 26, 'dark') +
    d.face(500, 510, 220) +
    sparkles(d, [[140, 180, 36], [870, 820, 40], [860, 170, 28]], 'main'));

  A.add('space-shuttle', 'Space Shuttle', { main: W, accent: GR, dark: DG, light: LB, accent2: O, pink: P }, d =>
    d.P('M195 470 L255 290 L340 290 L340 470 Z', 'accent') +
    d.P('M150 465 L70 440 Q40 485 70 530 L150 505 Z', 'accent2') +
    d.R(120, 460, 80, 40, 10, 'dark') + d.R(120, 510, 80, 40, 10, 'dark') +
    d.P('M180 465 L640 440 Q820 440 890 500 Q820 560 640 560 L180 545 Z') +
    d.P('M320 545 L600 545 L470 700 L280 700 Z', 'accent') +
    d.C(735, 475, 20, 'light') + d.C(790, 482, 20, 'light') +
    sparkles(d, [[860, 220, 42], [520, 220, 30], [180, 800, 34], [800, 780, 40]], 'light'));

  A.add('lunar-lander', 'Moon Lander', { main: W, accent: Y, dark: GR, light: LB, pink: P }, d =>
    d.L('M60 860 L940 860') +
    d.L('M370 610 L230 830 M630 610 L770 830 M430 640 L380 840 M570 640 L620 840') +
    d.E(230, 835, 60, 20, 'dark') + d.E(770, 835, 60, 20, 'dark') +
    d.P('M330 530 L670 530 L640 660 L360 660 Z', 'accent') +
    d.L('M560 330 L630 220') + d.C(635, 210, 24, 'accent') +
    d.R(370, 320, 260, 220, 40) + d.C(500, 420, 62, 'light') + d.face(500, 420, 80));

  A.add('robot', 'Robot', { main: GR, light: LB, accent: R, accent2: Y, pink: P }, d =>
    d.L('M500 175 L500 100') + d.C(500, 90, 28, 'accent') +
    d.R(400, 760, 80, 120, 25) + d.R(520, 760, 80, 120, 25) +
    d.R(240, 470, 90, 220, 40) + d.R(670, 470, 90, 220, 40) +
    d.C(285, 715, 45, 'accent2') + d.C(715, 715, 45, 'accent2') +
    d.R(330, 440, 340, 340, 40) + d.R(410, 520, 180, 140, 20, 'light') +
    d.C(455, 590, 22, 'accent') + d.C(545, 590, 22, 'accent2') +
    d.R(350, 175, 300, 240, 50) +
    d.C(430, 280, 46, 'light') + d.C(570, 280, 46, 'light') + d.eye(430, 285, 24) + d.eye(570, 285, 24) +
    d.smile(500, 345, 50, 30));

  A.add('space-dog', 'Space Puppy', { main: W, light: LB, dark: BR, accent: R, accent2: '#ffe0b2', pink: P }, d =>
    d.R(320, 610, 360, 260, 100) + d.R(450, 680, 100, 70, 15, 'accent') +
    d.C(500, 420, 260, 'light') +
    d.E(375, 340, 52, 105, 'dark', 25) + d.E(625, 340, 52, 105, 'dark', -25) +
    d.E(500, 440, 150, 135, 'accent2') +
    d.eye(445, 410, 22) + d.eye(555, 410, 22) +
    d.E(500, 470, 32, 22, 'ink') + d.L('M500 492 L500 512') + d.smile(500, 512, 40, 26) +
    d.R(310, 640, 380, 50, 25, 'accent') +
    d.Lt('M330 270 Q370 220 430 200'));

  A.add('space-cat', 'Space Kitty', { main: W, light: LB, accent: PU, accent2: '#ffcc80', pink: P }, d =>
    d.R(320, 610, 360, 260, 100) + d.R(450, 680, 100, 70, 15, 'accent') +
    d.C(500, 420, 260, 'light') +
    d.poly([[380, 380], [400, 250], [470, 330]], 'accent2') + d.poly([[620, 380], [600, 250], [530, 330]], 'accent2') +
    d.E(500, 445, 150, 130, 'accent2') +
    d.eye(445, 420, 22) + d.eye(555, 420, 22) +
    d.poly([[485, 465], [515, 465], [500, 482]], 'pink') + d.smile(500, 495, 36, 22) +
    d.Lt('M410 470 L330 455 M410 490 L330 500 M590 470 L670 455 M590 490 L670 500') +
    d.R(310, 640, 380, 50, 25, 'accent') +
    d.Lt('M330 270 Q370 220 430 200'));

  A.add('big-dipper', 'Star Picture', { main: Y, accent: Y, pink: P }, d => {
    const s = [[150, 300], [320, 270], [470, 340], [600, 440], [640, 660], [860, 660], [840, 430]];
    const path = 'M' + s.slice(0, 7).map(p => p.join(' ')).join(' L') + ' L600 440';
    return d.L(path) + s.map(([x, y], i) => star(d, x, y, i === 3 ? 95 : 78, i === 3 ? 44 : 36, 'main')).join('');
  });

  A.add('space-station', 'Space Station', { main: W, accent: B, dark: GR, light: LB, pink: P }, d =>
    d.R(110, 485, 780, 30, 10, 'dark') +
    d.L('M210 470 L210 380 M210 530 L210 620 M790 470 L790 380 M790 530 L790 620') +
    d.R(130, 230, 160, 160, 10, 'accent') + d.R(130, 610, 160, 160, 10, 'accent') +
    d.R(710, 230, 160, 160, 10, 'accent') + d.R(710, 610, 160, 160, 10, 'accent') +
    d.Lt('M210 230 L210 390 M130 310 L290 310 M210 610 L210 770 M130 690 L290 690 M790 230 L790 390 M710 310 L870 310 M790 610 L790 770 M710 690 L870 690') +
    d.R(400, 400, 200, 200, 40) + d.C(500, 300, 70, 'light') + d.R(470, 360, 60, 50, 10) +
    d.face(500, 500, 120));

  A.add('rocket-launch', 'Blast Off', { main: W, accent: R, accent2: O, dark: GR, light: B, pink: P }, d =>
    d.R(750, 200, 50, 640, 10, 'dark') + d.Lt('M750 300 L800 360 M800 300 L750 360 M750 460 L800 520 M800 460 L750 520 M750 620 L800 680 M800 620 L750 680') +
    d.L('M750 400 L620 400') +
    rocket(d, 470, 110, 0.82) + d.face(470, 345, 100) +
    d.R(180, 820, 640, 50, 15, 'dark') +
    d.C(240, 800, 75, 'main') + d.C(340, 840, 80, 'main') + d.C(600, 840, 80, 'main') + d.C(700, 800, 75, 'main') +
    sparkles(d, [[150, 200, 40], [880, 120, 30]], 'accent'));

  A.add('moon-flag', 'Flag on the Moon', { main: CR, dark: '#ffe082', accent: R, accent2: Y, light: B, pink: P }, d =>
    d.C(210, 230, 85, 'light') + d.P('M170 190 Q220 170 240 210 Q200 240 170 190 Z', 'dark') +
    d.R(490, 230, 22, 470, 10, 'dark') +
    d.P('M512 245 L790 245 L790 420 L512 420 Z', 'accent') + star(d, 650, 335, 62, 28, 'accent2') +
    d.P('M60 680 Q300 620 500 660 Q720 700 940 640 L940 900 L60 900 Z') +
    d.E(250, 770, 80, 28, 'dark') + d.E(700, 800, 100, 32, 'dark') + d.E(480, 850, 55, 20, 'dark') +
    sparkles(d, [[860, 150, 36], [380, 140, 30]], 'accent2'));

  A.add('observatory', 'Star Watching House', { main: W, light: LB, dark: GR, accent: Y, pink: P }, d =>
    d.poly([[540, 300], [760, 160], [800, 220], [580, 370]], 'dark') +
    d.P('M290 540 Q290 270 500 270 Q710 270 710 540 Z', 'light') +
    d.R(470, 285, 60, 230, 25, 'dark') +
    d.R(300, 530, 400, 320, 20) + d.L('M300 540 L700 540') +
    d.P('M445 850 L445 730 Q500 670 555 730 L555 850 Z', 'dark') +
    d.C(370, 640, 38, 'light') + d.C(630, 640, 38, 'light') +
    d.L('M60 850 L940 850') +
    sparkles(d, [[160, 200, 44], [880, 420, 36], [150, 470, 30]], 'accent'));

  A.add('galaxy', 'Galaxy', { main: PU, accent: B, light: Y, pink: P }, d => {
    const rot = (x, y, a) => { const c = Math.cos(rad(a)), s = Math.sin(rad(a)); return [500 + (x - 500) * c - (y - 500) * s, 500 + (x - 500) * s + (y - 500) * c]; };
    let arms = '';
    for (let i = 0; i < 3; i++) {
      const a = i * 120, p1 = rot(560, 430, a), c1 = rot(760, 260, a), p2 = rot(890, 470, a), c2 = rot(780, 380, a), p3 = rot(600, 560, a);
      arms += d.P(`M${f1(p1[0])} ${f1(p1[1])} Q${f1(c1[0])} ${f1(c1[1])} ${f1(p2[0])} ${f1(p2[1])} Q${f1(c2[0])} ${f1(c2[1])} ${f1(p3[0])} ${f1(p3[1])} Z`, i % 2 ? 'accent' : 'main');
    }
    return arms + d.C(500, 500, 165, 'light') + d.face(500, 500, 160) +
      sparkles(d, [[150, 150, 34], [870, 840, 38], [140, 860, 30]], 'light');
  });
})();
