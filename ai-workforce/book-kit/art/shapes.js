// "My First Shapes & Colors": 30 big, simple pages for ages 2-5. The flat
// shapes are named with a colour ("Red Circle"), so children colour each one in
// its colour; then five solid shapes and nine colourful things to colour.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const RED = '#ff6b6b', BLUE = '#5aa9f0', YEL = '#ffd23f', GRN = '#7bd389', ORA = '#ff9f43', PUR = '#b39ddb', PNK = '#ff9ec4',
    P = '#ffc2d6', BR = '#c68b59', W = '#ffffff', GRY = '#9aa5b1', SKY = '#cfe9ff';

  // regular polygon points around cx,cy with radius R, starting at angle a0 (degrees)
  const reg = (cx, cy, R, n, a0) => Array.from({ length: n }, (_, i) => {
    const a = (a0 + i * 360 / n) * Math.PI / 180;
    return [cx + R * Math.cos(a), cy + R * Math.sin(a)];
  });
  const star = (cx, cy, R, r) => Array.from({ length: 10 }, (_, i) => {
    const a = (-90 + i * 36) * Math.PI / 180, q = i % 2 ? r : R;
    return [cx + q * Math.cos(a), cy + q * Math.sin(a)];
  });
  const ground = d => d.grass(925);

  // ---- flat shapes, each with its colour in the name ----
  A.add('circle', 'Red Circle', { main: RED, pink: P }, d =>
    d.C(500, 480, 320) + d.face(500, 470, 270) + ground(d));

  A.add('square', 'Blue Square', { main: BLUE, pink: P }, d =>
    d.R(200, 170, 600, 600, 46) + d.face(500, 460, 270) + ground(d));

  A.add('triangle', 'Yellow Triangle', { main: YEL, pink: P }, d =>
    d.poly([[500, 120], [850, 800], [150, 800]]) + d.face(500, 580, 230) + ground(d));

  A.add('rectangle', 'Green Rectangle', { main: GRN, pink: P }, d =>
    d.R(110, 270, 780, 470, 46) + d.face(500, 490, 270) + ground(d));

  A.add('oval', 'Orange Oval', { main: ORA, pink: P }, d =>
    d.E(500, 480, 250, 350) + d.face(500, 460, 250) + ground(d));

  A.add('star', 'Yellow Star', { main: YEL, pink: P }, d =>
    d.poly(star(500, 500, 400, 170)) + d.face(500, 520, 200) + ground(d));

  A.add('heart', 'Pink Heart', { main: PNK, pink: P }, d =>
    d.P('M500 820 C150 600 90 330 230 230 C340 150 460 200 500 300 C540 200 660 150 770 230 C910 330 850 600 500 820 Z') +
    d.face(500, 450, 240) + ground(d));

  A.add('diamond', 'Purple Diamond', { main: PUR, pink: P }, d =>
    d.poly([[500, 110], [820, 470], [500, 830], [180, 470]]) + d.face(500, 460, 220) + ground(d));

  A.add('pentagon', 'Blue Pentagon', { main: BLUE, pink: P }, d =>
    d.poly(reg(500, 500, 380, 5, -90)) + d.face(500, 520, 250) + ground(d));

  A.add('hexagon', 'Green Hexagon', { main: GRN, pink: P }, d =>
    d.poly(reg(500, 480, 370, 6, 0)) + d.face(500, 470, 260) + ground(d));

  A.add('octagon', 'Red Octagon', { main: RED, pink: P }, d =>
    d.poly(reg(500, 480, 375, 8, 22.5)) + d.face(500, 470, 260) + ground(d));

  A.add('crescent', 'Yellow Crescent', { main: YEL, pink: P }, d =>
    d.P('M560 140 A350 350 0 1 0 560 820 A290 290 0 0 1 560 140 Z') + d.face(330, 470, 170) + ground(d));

  A.add('half-circle', 'Orange Half Circle', { main: ORA, pink: P }, d =>
    d.P('M120 720 A380 380 0 0 1 880 720 Z') + d.face(500, 540, 250) + ground(d));

  A.add('trapezoid', 'Purple Trapezoid', { main: PUR, pink: P }, d =>
    d.poly([[320, 240], [680, 240], [880, 780], [120, 780]]) + d.face(500, 510, 250) + ground(d));

  A.add('plus', 'Pink Plus Sign', { main: PNK, pink: P }, d =>
    d.P('M390 130 L610 130 Q630 130 630 150 L630 360 L840 360 Q860 360 860 380 L860 600 Q860 620 840 620 L630 620 L630 830 Q630 850 610 850 L390 850 Q370 850 370 830 L370 620 L160 620 Q140 620 140 600 L140 380 Q140 360 160 360 L370 360 L370 150 Q370 130 390 130 Z') +
    d.face(500, 480, 210) + ground(d));

  A.add('arrow', 'Orange Arrow', { main: ORA, pink: P }, d =>
    d.poly([[110, 370], [540, 370], [540, 200], [890, 490], [540, 780], [540, 610], [110, 610]]) +
    d.face(430, 470, 175) + ground(d));

  // ---- solid shapes ----
  A.add('cube', 'Cube', { main: RED, light: '#ff9a9a', dark: '#e05050', pink: P }, d =>
    d.poly([[200, 340], [370, 180], [800, 180], [630, 340]], 'light') +
    d.poly([[630, 340], [800, 180], [800, 600], [630, 770]], 'dark') +
    d.R(200, 340, 430, 430, 14) + d.face(415, 540, 230) + ground(d));

  A.add('ball', 'Ball', { main: YEL, accent: RED, accent2: BLUE, light: W, pink: P }, d =>
    d.C(500, 480, 330) +
    d.P('M500 150 Q330 300 330 480 Q330 660 500 810 Q395 650 395 480 Q395 310 500 150 Z', 'accent') +
    d.P('M500 150 Q670 300 670 480 Q670 660 500 810 Q605 650 605 480 Q605 310 500 150 Z', 'accent2') +
    d.E(290, 360, 34, 56, 'light', 25) + ground(d));

  A.add('cone', 'Cone', { main: ORA, light: '#ffc58a', pink: P }, d =>
    d.P('M500 120 L800 760 Q500 880 200 760 Z') + d.face(500, 580, 220) + ground(d));

  A.add('cylinder', 'Cylinder', { main: GRN, light: '#b9ebc4', pink: P }, d =>
    d.P('M250 260 L250 740 A250 80 0 0 0 750 740 L750 260 Z') + d.E(500, 260, 250, 80, 'light') +
    d.face(500, 520, 250));

  A.add('pyramid', 'Pyramid', { main: YEL, dark: '#e6b82e', pink: P }, d =>
    d.poly([[540, 120], [880, 640], [720, 800]], 'dark') +
    d.poly([[540, 120], [720, 800], [140, 800]]) + d.face(470, 610, 200) + ground(d));

  // ---- colourful things ----
  A.add('rainbow', 'Rainbow', { main: RED, accent: ORA, light: YEL, accent2: GRN, dark: BLUE, pink: P }, d =>
    d.P('M110 720 A390 390 0 0 1 890 720 Z', 'main') +
    d.P('M180 720 A320 320 0 0 1 820 720 Z', 'accent') +
    d.P('M250 720 A250 250 0 0 1 750 720 Z', 'light') +
    d.P('M320 720 A180 180 0 0 1 680 720 Z', 'accent2') +
    d.P('M390 720 A110 110 0 0 1 610 720 Z', 'dark') +
    d.C(140, 720, 62, 'light2') + d.C(235, 700, 72, 'light2') + d.C(765, 700, 72, 'light2') + d.C(860, 720, 62, 'light2') +
    d.E(190, 775, 140, 62, 'light2') + d.E(810, 775, 140, 62, 'light2') +
    d.face(500, 650, 120));

  A.add('crayon', 'Crayon', { main: BLUE, light: '#a9d4f8', pink: P }, d =>
    d.P('M370 330 L500 110 L630 330 Z', 'light') + d.P('M458 182 L500 110 L542 182 Z', 'main') +
    d.R(370, 320, 260, 560, 26) +
    d.R(370, 370, 260, 70, 0, 'light') + d.R(370, 760, 260, 70, 0, 'light') +
    d.face(500, 570, 190));

  A.add('paintbrush', 'Paintbrush', { main: BR, light: GRY, accent: PUR, pink: P }, d =>
    d.R(450, 470, 100, 430, 46) +
    d.R(410, 360, 180, 130, 22, 'light') +
    d.P('M415 365 Q400 220 460 150 Q500 100 540 150 Q600 220 585 365 Z', 'accent') +
    d.Lt('M470 230 L470 330 M530 230 L530 330') + d.L('M420 430 L580 430'));

  A.add('paint-palette', 'Paint Palette', { main: '#f0d2a8', accent: RED, accent2: BLUE, light: YEL, dark: GRN, pink: PNK }, d =>
    d.P('M500 170 C780 170 900 330 870 500 C850 620 760 630 690 610 C620 590 600 650 640 720 C680 800 600 840 500 840 C250 840 110 690 120 500 C130 320 280 170 500 170 Z') +
    d.C(740, 470, 40) +
    d.C(320, 360, 58, 'accent') + d.C(470, 290, 58, 'light') + d.C(630, 320, 58, 'accent2') + d.C(250, 530, 58, 'dark') + d.C(320, 690, 58, 'pink') +
    d.face(500, 520, 190));

  A.add('paint-can', 'Paint Can', { main: GRY, accent: PUR, light: '#d9dee3', pink: P }, d =>
    d.L('M290 380 Q500 70 710 380') +
    d.P('M270 380 L270 820 A230 60 0 0 0 730 820 L730 380 Z') +
    d.E(500, 380, 230, 60, 'accent') +
    d.face(520, 620, 220));

  A.add('traffic-light', 'Traffic Light', { main: '#ffcc33', accent: RED, light: YEL, accent2: GRN, dark: GRY, pink: P }, d =>
    d.R(465, 780, 70, 140, 10, 'dark') +
    d.R(330, 110, 340, 680, 70) +
    d.C(500, 230, 92, 'accent') + d.C(500, 450, 92, 'light') + d.C(500, 670, 92, 'accent2') +
    d.L('M300 940 L700 940'));

  A.add('balloon', 'Balloon', { main: RED, pink: P }, d =>
    d.L('M500 690 Q440 780 520 840 Q580 890 500 950') +
    d.P('M470 700 L530 700 L545 735 L455 735 Z') +
    d.E(500, 410, 260, 300) + d.E(400, 270, 46, 76, 'none', 25) + d.face(500, 420, 260));

  A.add('kite', 'Kite', { main: BLUE, accent: YEL, accent2: RED, pink: P }, d =>
    d.L('M500 800 Q420 860 470 900 Q540 940 470 980') +
    d.P('M445 860 L500 880 L445 900 Z', 'accent2') + d.P('M555 860 L500 880 L555 900 Z', 'accent2') +
    d.poly([[500, 90], [780, 400], [500, 800], [220, 400]]) +
    d.face(500, 410, 220));

  A.add('umbrella', 'Umbrella', { main: PUR, dark: BR, pink: P }, d =>
    d.L('M500 520 L500 820 Q500 880 440 880 Q390 880 385 830') +
    d.P('M130 520 Q150 130 500 120 Q850 130 870 520 Q778 460 685 520 Q593 460 500 520 Q407 460 315 520 Q222 460 130 520 Z') +
    d.C(500, 112, 18, 'dark') + d.face(500, 340, 230));
})();
