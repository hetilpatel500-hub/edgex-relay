// "My First Kitchen": 30 kitchen things for ages 2-5.
// Generic subjects only: no brands, product names or licensed characters.
// Nothing sharp: no knives, and no flames on the stove.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const W = '#ffffff', P = '#ffb3c7', LP = '#ffe0ea', PU = '#c9a7ff', Y = '#ffd23f', LY = '#fff1a8', O = '#ff9f43',
    G = '#7bd389', LG = '#c8f0cf', B = '#8fd3ff', LB = '#d4efff', BR = '#c68b59', DB = '#8d5a3b', TAN = '#e8b98a',
    GR = '#cfd8dc', DG = '#90a4ae', R = '#ff7b8a', MT = '#a8e6cf', CR = '#fff3d6';

  const f = v => (+v).toFixed(1);
  const g = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${f(cx)} ${f(cy)})">${s}</g>`;
  // a five-point star centred on x,y, outer radius r (inner radius ri)
  const star = (d, x, y, r, k = 'accent', ri = 0.5) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const t = (i * 36 - 90) * Math.PI / 180, rr = i % 2 ? r * ri : r;
      pts.push([x + Math.cos(t) * rr, y + Math.sin(t) * rr]);
    }
    return d.poly(pts, k);
  };
  // a loop handle on the right of a body: outer bulge to x2, between y1 and y2, thickness t
  const handleR = (d, x1, y1, y2, x2, t, k = 'dark') =>
    d.P(`M${x1} ${y1} C${x2} ${y1} ${x2} ${y2} ${x1} ${y2} L${x1} ${y2 - t} C${x2 - t * 1.6} ${y2 - t} ${x2 - t * 1.6} ${y1 + t} ${x1} ${y1 + t} Z`, k);
  // an arch handle on top, between x1 and x2 at height y, rising to top, thickness t
  const handleTop = (d, x1, x2, y, top, t, k = 'dark') => {
    const m = (x1 + x2) / 2;
    return d.P(`M${x1} ${y} Q${x1} ${top} ${m} ${top} Q${x2} ${top} ${x2} ${y} L${x2 - t} ${y} Q${x2 - t} ${top + t} ${m} ${top + t} Q${x1 + t} ${top + t} ${x1 + t} ${y} Z`, k);
  };

  // ---------------- Cooking ----------------
  A.add('frying-pan', 'Frying Pan', { main: R, dark: DB, light: GR, accent: Y, pink: P }, d =>
    g(d.R(640, 470, 330, 76, 38, 'dark') + d.C(905, 508, 16, 'light'), 22, 640, 508) +
    d.C(420, 500, 320) + d.C(420, 500, 255, 'light') +
    d.face(420, 500, 250));

  A.add('kettle', 'Kettle', { main: B, dark: DB, light: W, accent: Y, pink: P }, d =>
    handleTop(d, 300, 700, 470, 150, 52) +
    d.P('M300 600 L150 430 Q130 405 160 400 L205 398 L345 520 Z') +
    d.P('M240 820 L760 820 Q790 470 500 390 Q210 470 240 820 Z') +
    d.E(500, 400, 125, 32, 'light') + d.C(500, 360, 30, 'accent') +
    d.R(220, 800, 560, 50, 25, 'light') +
    d.Lt('M150 360 Q125 320 150 285 Q175 250 150 215') +
    d.face(500, 610, 240));

  A.add('stove', 'Stove', { main: W, dark: DG, light: LB, accent: R, accent2: Y, pink: P }, d =>
    d.R(245, 860, 70, 45, 12, 'dark') + d.R(685, 860, 70, 45, 12, 'dark') +
    d.R(190, 270, 620, 600, 40) +
    d.R(190, 150, 620, 120, 30, 'dark') +
    d.C(290, 210, 28, 'accent') + d.C(390, 210, 28, 'accent2') + d.C(610, 210, 28, 'accent2') + d.C(710, 210, 28, 'accent') +
    d.R(280, 330, 440, 46, 23, 'dark') +
    d.R(270, 420, 460, 360, 50, 'light') +
    d.face(500, 590, 230));

  A.add('microwave', 'Microwave', { main: W, dark: DG, light: LB, accent: G, accent2: R, pink: P }, d =>
    d.R(220, 760, 70, 40, 12, 'dark') + d.R(710, 760, 70, 40, 12, 'dark') +
    d.R(130, 270, 740, 500, 50) +
    d.R(190, 330, 440, 380, 40, 'light') +
    d.R(670, 340, 140, 60, 18, 'accent') +
    d.C(705, 470, 24, 'dark') + d.C(775, 470, 24, 'dark') + d.C(705, 550, 24, 'dark') + d.C(775, 550, 24, 'dark') +
    d.R(680, 620, 120, 50, 22, 'accent2') +
    d.face(410, 520, 230));

  A.add('blender', 'Blender', { main: LB, dark: DG, light: W, accent: R, accent2: Y, pink: P }, d =>
    handleR(d, 670, 300, 600, 830, 55) +
    d.P('M300 230 L700 230 L645 690 L355 690 Z') +
    d.R(280, 170, 440, 72, 30, 'accent') + d.R(460, 120, 80, 60, 20, 'accent') +
    d.R(320, 680, 360, 200, 45, 'dark') +
    d.C(500, 780, 34, 'accent2') +
    d.face(500, 450, 220));

  // a hand mixer (generic: no stand-mixer shape)
  A.add('mixer', 'Mixer', { main: P, dark: DG, light: GR, accent: Y, accent2: B, pink: R }, d =>
    handleTop(d, 320, 680, 330, 120, 62) +
    d.R(382, 500, 36, 120, 16, 'light') + d.R(582, 500, 36, 120, 16, 'light') +
    d.E(400, 632, 52, 58, 'light') + d.E(600, 632, 52, 58, 'light') + d.Lt('M400 578 L400 686 M600 578 L600 686') +
    d.R(200, 300, 600, 230, 95) +
    d.R(610, 250, 90, 40, 18, 'accent') +
    d.P('M230 700 L770 700 Q760 890 500 890 Q240 890 230 700 Z', 'accent2') +
    d.R(205, 680, 590, 46, 23, 'accent2') +
    d.face(490, 410, 190));

  A.add('kitchen-timer', 'Kitchen Timer', { main: Y, dark: DG, light: W, accent: R, pink: P }, d => {
    let ticks = '';
    for (let i = 0; i < 12; i++) {
      const t = i * 30 * Math.PI / 180;
      ticks += d.Lt(`M${f(500 + Math.sin(t) * 190)} ${f(560 - Math.cos(t) * 190)} L${f(500 + Math.sin(t) * 220)} ${f(560 - Math.cos(t) * 220)}`);
    }
    return d.R(445, 190, 110, 80, 25, 'accent') +
      d.R(330, 840, 80, 50, 15, 'dark') + d.R(590, 840, 80, 50, 15, 'dark') +
      d.C(500, 560, 310) + d.C(500, 560, 245, 'light') + ticks +
      d.face(500, 580, 210);
  });

  // ---------------- Baking ----------------
  A.add('whisk', 'Whisk', { main: GR, dark: DB, light: W, accent: R, pink: P }, d =>
    d.L('M500 640 C260 470 260 130 500 130 C740 130 740 470 500 640') +
    d.L('M500 640 C345 470 345 170 500 170 C655 170 655 470 500 640') +
    d.L('M500 640 C430 470 430 210 500 210 C570 210 570 470 500 640') +
    d.R(410, 600, 180, 56, 22, 'accent') +
    d.R(420, 640, 160, 270, 70, 'dark') +
    d.face(500, 760, 135));

  A.add('spatula', 'Spatula', { main: O, dark: DB, light: W, accent: Y, pink: P }, d =>
    g(d.R(470, 440, 60, 150, 25, 'dark') +
      d.R(430, 570, 140, 330, 70, 'dark') + d.C(500, 850, 18, 'light') +
      d.R(320, 120, 360, 340, 70) +
      d.R(375, 160, 44, 100, 22, 'light') + d.R(478, 160, 44, 100, 22, 'light') + d.R(581, 160, 44, 100, 22, 'light') +
      d.face(500, 345, 170), 14));

  A.add('rolling-pin', 'Rolling Pin', { main: TAN, dark: DB, light: CR, accent: P, pink: P }, d =>
    d.E(500, 790, 360, 80, 'light') +
    g(d.R(70, 470, 210, 80, 40, 'dark') + d.R(720, 470, 210, 80, 40, 'dark') +
      d.R(240, 405, 520, 210, 105) +
      d.face(500, 500, 190), -8));

  A.add('mixing-bowl', 'Mixing Bowl', { main: G, dark: DB, light: CR, accent: Y, pink: P }, d =>
    g(d.R(560, 110, 56, 360, 28, 'dark'), 28, 588, 290) +
    d.R(370, 805, 260, 45, 18, 'accent') +
    d.P('M190 440 Q500 300 810 440 Z', 'light') +
    d.P('M140 440 L860 440 Q850 820 500 830 Q150 820 140 440 Z') +
    d.R(110, 410, 780, 60, 30, 'accent') +
    d.face(500, 620, 250));

  A.add('measuring-cup', 'Measuring Cup', { main: LB, dark: DG, light: W, accent: R, pink: P }, d =>
    handleR(d, 720, 380, 660, 900, 58, 'accent') +
    d.P('M300 330 L215 300 L270 390 Z') +
    d.P('M270 300 L740 300 L700 840 Q500 870 300 840 Z') +
    d.R(250, 280, 510, 50, 25, 'light') +
    d.Lt('M320 430 L380 430 M320 530 L400 530 M325 630 L385 630 M330 730 L410 730') +
    d.face(530, 590, 220));

  A.add('cookie-cutter', 'Cookie Cutter', { main: R, dark: DB, light: CR, accent: TAN, pink: P }, d =>
    d.E(500, 830, 380, 75, 'accent') +
    star(d, 500, 470, 350, 'main', 0.52) +
    star(d, 500, 478, 290, 'light', 0.52) +
    d.face(500, 510, 190));

  A.add('muffin-tin', 'Muffin Tin', { main: TAN, dark: DG, light: W, accent: P, accent2: B, pink: P }, d => {
    const cup = x => d.P(`M${x - 115} 545 L${x + 115} 545 L${x + 95} 700 L${x - 95} 700 Z`, 'accent') +
      d.Lt(`M${x - 50} 565 L${x - 42} 640 M${x} 565 L${x} 640 M${x + 50} 565 L${x + 42} 640`);
    return d.R(50, 650, 110, 60, 25, 'dark') + d.R(840, 650, 110, 60, 25, 'dark') +
      cup(230) + cup(770) +
      d.P('M120 550 Q115 400 230 400 Q345 400 340 550 Z') + d.C(195, 470, 16, 'accent2') + d.C(265, 495, 16, 'accent2') +
      d.P('M660 550 Q655 400 770 400 Q885 400 880 550 Z') + d.C(735, 470, 16, 'accent2') + d.C(805, 495, 16, 'accent2') +
      d.P('M365 545 L635 545 L612 700 L388 700 Z', 'accent') + d.Lt('M440 565 L448 640 M500 565 L500 640 M560 565 L552 640') +
      d.P('M345 555 Q320 290 500 290 Q680 290 655 555 Z') +
      d.R(90, 640, 820, 150, 40, 'dark') +
      d.face(500, 440, 190);
  });

  A.add('cookie-jar', 'Cookie Jar', { main: LB, dark: DB, light: W, accent: R, accent2: TAN, pink: P }, d =>
    d.C(820, 810, 78, 'accent2') + d.dot(795, 790, 11) + d.dot(840, 830, 11) + d.dot(830, 775, 9) +
    d.R(210, 340, 560, 520, 150) +
    d.E(490, 335, 255, 55, 'accent') + d.C(490, 265, 42, 'accent') +
    d.face(490, 600, 260));

  A.add('oven-mitt', 'Oven Mitt', { main: R, dark: DB, light: W, accent: Y, pink: P }, d =>
    d.E(300, 520, 85, 160, 'main', -28) +
    d.P('M330 830 L330 360 Q330 160 525 160 Q715 160 715 360 L715 830 Z') +
    d.R(300, 740, 445, 130, 40, 'accent') +
    d.L('M520 870 Q520 940 470 940') +
    d.face(525, 450, 230));

  A.add('chef-hat', 'Chef Hat', { main: W, dark: DG, light: W, accent: R, pink: P }, d =>
    d.P('M330 540 C170 540 160 320 320 315 C315 160 470 140 500 215 C530 140 685 160 680 315 C840 320 830 540 670 540 Z') +
    d.Lt('M370 420 Q395 380 380 340 M630 420 Q605 380 620 340') +
    d.R(320, 500, 360, 260, 40, 'light') +
    d.face(500, 640, 180));

  // ---------------- Getting food ready ----------------
  A.add('cutting-board', 'Cutting Board', { main: TAN, dark: DB, light: W, accent: O, accent2: G, pink: P }, d =>
    d.R(420, 120, 160, 160, 55) + d.C(500, 190, 30, 'light') +
    d.R(210, 240, 580, 640, 90) +
    d.C(330, 780, 42, 'accent') + d.C(430, 800, 42, 'accent') + d.C(560, 795, 42, 'accent') + d.E(670, 780, 70, 38, 'accent2', -20) +
    d.face(500, 510, 250));

  A.add('grater', 'Grater', { main: GR, dark: DB, light: W, accent: Y, pink: P }, d =>
    handleTop(d, 360, 640, 270, 100, 50) +
    d.P('M320 260 L680 260 L750 860 L250 860 Z') +
    d.E(330, 760, 22, 13, 'light') + d.E(420, 760, 22, 13, 'light') + d.E(500, 760, 22, 13, 'light') + d.E(580, 760, 22, 13, 'light') + d.E(670, 760, 22, 13, 'light') +
    d.E(370, 815, 22, 13, 'light') + d.E(460, 815, 22, 13, 'light') + d.E(540, 815, 22, 13, 'light') + d.E(630, 815, 22, 13, 'light') +
    d.E(410, 330, 18, 11, 'light') + d.E(500, 330, 18, 11, 'light') + d.E(590, 330, 18, 11, 'light') +
    d.face(500, 530, 230));

  A.add('colander', 'Colander', { main: O, dark: DG, light: W, accent: Y, pink: P }, d =>
    d.R(60, 410, 120, 54, 27, 'dark') + d.R(820, 410, 120, 54, 27, 'dark') +
    d.R(380, 780, 240, 44, 18, 'dark') +
    d.P('M170 440 L830 440 Q820 790 500 800 Q180 790 170 440 Z') +
    d.R(140, 410, 720, 60, 30, 'light') +
    d.C(270, 505, 16, 'light') + d.C(380, 510, 16, 'light') + d.C(620, 510, 16, 'light') + d.C(730, 505, 16, 'light') +
    d.C(390, 740, 16, 'light') + d.C(500, 750, 16, 'light') + d.C(610, 740, 16, 'light') +
    d.face(500, 610, 220));

  A.add('ladle', 'Ladle', { main: B, dark: DB, light: W, accent: Y, pink: P }, d =>
    g(d.R(470, 150, 60, 500, 30, 'dark') + d.C(500, 140, 42, 'dark') + d.C(500, 140, 16, 'light') +
      d.P('M260 600 L740 600 Q740 880 500 880 Q260 880 260 600 Z') +
      d.E(500, 600, 240, 48, 'light') +
      d.face(500, 730, 180), -12));

  A.add('spice-jars', 'Spice Jars', { main: Y, dark: DB, light: W, accent: R, accent2: G, pink: P }, d =>
    d.R(110, 760, 780, 56, 24, 'dark') +
    d.R(170, 480, 180, 285, 45, 'light') + d.R(160, 430, 200, 70, 25, 'accent2') +
    d.E(230, 600, 26, 14, 'accent2', -30) + d.E(290, 650, 26, 14, 'accent2', 30) +
    d.R(650, 530, 180, 235, 45, 'light') + d.R(640, 480, 200, 70, 25, 'accent') +
    d.dot(700, 610, 10) + d.dot(760, 640, 10) + d.dot(720, 690, 10) + d.dot(780, 710, 10) +
    d.R(400, 320, 200, 445, 55) + d.R(390, 270, 220, 70, 25, 'accent') +
    d.face(500, 540, 170));

  A.add('salt-and-pepper', 'Salt & Pepper', { main: W, dark: DG, light: LB, accent: GR, accent2: TAN, pink: P }, d =>
    d.R(160, 840, 680, 30, 15, 'dark') +
    d.P('M180 410 Q180 250 320 250 Q460 250 460 410 Z', 'accent') + d.dot(280, 320, 10) + d.dot(320, 300, 10) + d.dot(360, 320, 10) +
    d.R(180, 390, 280, 450, 90, 'main') +
    d.P('M540 410 Q540 250 680 250 Q820 250 820 410 Z', 'accent') + d.dot(640, 320, 10) + d.dot(680, 300, 10) + d.dot(720, 320, 10) +
    d.R(540, 390, 280, 450, 90, 'accent2') +
    d.face(320, 600, 170) + d.face(680, 600, 170));

  // ---------------- Eating and cleaning up ----------------
  A.add('plate', 'Plate', { main: W, dark: DG, light: LB, accent: Y, pink: P }, d =>
    d.R(95, 160, 22, 120, 11, 'dark') + d.R(129, 160, 22, 120, 11, 'dark') + d.R(163, 160, 22, 120, 11, 'dark') +
    d.R(90, 250, 100, 120, 40, 'dark') + d.R(115, 350, 50, 480, 25, 'dark') +
    d.C(560, 500, 320, 'light') + d.C(560, 500, 235) +
    d.face(560, 500, 240));

  A.add('pitcher', 'Pitcher', { main: LY, dark: DG, light: W, accent: Y, accent2: G, pink: P }, d =>
    handleR(d, 700, 340, 660, 880, 58, 'accent2') +
    d.P('M300 300 L200 255 L320 380 Z', 'light') +
    d.P('M300 260 L700 260 Q760 560 720 850 L280 850 Q240 560 300 260 Z') +
    d.E(500, 262, 202, 36, 'light') +
    d.face(500, 530, 240));

  A.add('sippy-cup', 'Sippy Cup', { main: P, dark: DG, light: W, accent: B, pink: R }, d =>
    d.E(215, 570, 78, 125, 'accent') + d.E(215, 570, 30, 72, 'light') +
    d.E(785, 570, 78, 125, 'accent') + d.E(785, 570, 30, 72, 'light') +
    d.P('M420 320 L440 175 Q500 145 560 175 L580 320 Z', 'accent') +
    d.R(270, 360, 460, 490, 110) +
    d.R(250, 300, 500, 90, 40, 'accent') +
    d.face(500, 610, 240));

  A.add('lunch-box', 'Lunch Box', { main: G, dark: DB, light: LG, accent: Y, pink: P }, d =>
    handleTop(d, 380, 620, 335, 190, 48) +
    d.R(160, 320, 680, 500, 60) +
    d.L('M160 460 L840 460') +
    d.R(465, 440, 70, 60, 15, 'accent') +
    d.face(500, 650, 240));

  A.add('high-chair', 'High Chair', { main: Y, dark: DB, light: W, accent: R, pink: P }, d =>
    g(d.R(330, 540, 44, 360, 20, 'dark'), 9, 352, 540) + g(d.R(626, 540, 44, 360, 20, 'dark'), -9, 648, 540) +
    d.R(330, 770, 340, 34, 17, 'dark') +
    d.R(330, 140, 340, 400, 70) +
    d.R(300, 520, 400, 60, 25, 'main') +
    d.R(220, 440, 560, 60, 30, 'light') +
    d.face(500, 290, 210));

  A.add('sink', 'Sink', { main: W, dark: DG, light: LB, accent: B, accent2: R, pink: P }, d =>
    d.R(470, 300, 60, 210, 25, 'dark') + d.R(470, 260, 230, 60, 30, 'dark') + d.R(650, 260, 50, 120, 22, 'dark') +
    d.E(675, 430, 16, 26, 'accent') +
    d.C(370, 470, 34, 'accent') + d.C(630, 470, 34, 'accent2') +
    d.R(90, 500, 820, 90, 25, 'light') +
    d.P('M200 590 L800 590 Q790 850 500 850 Q210 850 200 590 Z') +
    d.face(500, 700, 210));

  A.add('trash-can', 'Trash Can', { main: G, dark: DG, light: LG, accent: Y, pink: P }, d =>
    d.R(430, 225, 140, 70, 30, 'dark') +
    d.P('M270 330 L730 330 L690 860 L310 860 Z') +
    d.R(230, 270, 540, 80, 38, 'light') +
    d.R(390, 820, 220, 55, 22, 'dark') +
    d.face(500, 560, 230));
})();
