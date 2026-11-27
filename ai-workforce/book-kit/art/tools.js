// "My First Tools": 30 tools and fix-it things for ages 2-5.
// Generic subjects only: no brands, product names, brand colour schemes or licensed characters.
// Friendly, chunky shapes: no knives, axes or sparks.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const W = '#ffffff', P = '#ffb3c7', PU = '#c9a7ff', Y = '#ffd23f', LY = '#fff1a8', O = '#ff9f43',
    G = '#7bd389', LG = '#c8f0cf', B = '#8fd3ff', LB = '#d4efff', BR = '#c68b59', DB = '#8d5a3b', TAN = '#e8b98a',
    GR = '#cfd8dc', DG = '#90a4ae', R = '#ff7b8a', MT = '#a8e6cf';

  const f = v => (+v).toFixed(1);
  const g = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${f(cx)} ${f(cy)})">${s}</g>`;
  // a regular polygon (n sides) centred on x,y with radius r, rotated by a0 degrees
  const ngon = (d, x, y, r, n, a0 = 0, k = 'main') => {
    const pts = [];
    for (let i = 0; i < n; i++) {
      const t = (a0 + i * 360 / n) * Math.PI / 180;
      pts.push([x + Math.cos(t) * r, y + Math.sin(t) * r]);
    }
    return d.poly(pts, k);
  };
  // an arch handle on top, between x1 and x2 at height y, rising to top, thickness t
  const handleTop = (d, x1, x2, y, top, t, k = 'dark') => {
    const m = (x1 + x2) / 2;
    return d.P(`M${x1} ${y} Q${x1} ${top} ${m} ${top} Q${x2} ${top} ${x2} ${y} L${x2 - t} ${y} Q${x2 - t} ${top + t} ${m} ${top + t} Q${x1 + t} ${top + t} ${x1 + t} ${y} Z`, k);
  };
  // short tick marks along a line (x from x1 to x2 every step), long every `every`
  const ticks = (d, x1, x2, y, step, short, long, every) => {
    let s = '';
    for (let x = x1, i = 0; x <= x2; x += step, i++) s += d.Lt(`M${x} ${y} L${x} ${y + (i % every ? short : long)}`);
    return s;
  };

  // ---------------- Hand tools ----------------
  A.add('hammer', 'Hammer', { main: DG, dark: DB, light: GR, accent: TAN, pink: P }, d =>
    g(d.R(445, 360, 110, 540, 50, 'accent') +
      d.P('M690 225 Q800 215 850 300 Q860 330 830 330 Q790 290 690 330 Z', 'main') +
      d.R(250, 200, 460, 170, 55) +
      d.R(180, 190, 100, 190, 30, 'dark') +
      d.face(470, 270, 150), -20, 500, 500));

  A.add('screwdriver', 'Screwdriver', { main: R, dark: DG, light: GR, accent: Y, pink: P }, d =>
    g(d.R(478, 520, 44, 300, 14, 'light') +
      d.P('M478 818 L522 818 L514 885 L486 885 Z', 'light') +
      d.R(440, 480, 120, 56, 14, 'dark') +
      d.R(390, 110, 220, 390, 95) +
      d.Lt('M435 150 L435 210') + d.Lt('M565 150 L565 210') +
      d.face(500, 330, 160), 30, 500, 500));

  A.add('wrench', 'Wrench', { main: B, dark: DG, light: W, accent: Y, pink: P }, d =>
    g(d.R(425, 300, 150, 420, 50) +
      d.P('M455 98 L455 205 L545 205 L545 98 A130 130 0 1 1 455 98 Z') +
      d.C(500, 790, 125) + d.C(500, 790, 55, 'light') +
      d.face(500, 500, 130), 35, 500, 500));

  A.add('pliers', 'Pliers', { main: DG, dark: DB, light: GR, accent: R, pink: P }, d =>
    d.P('M445 470 Q370 660 280 870 Q320 915 365 885 Q455 690 520 480 Z', 'accent') +
    d.P('M555 470 Q630 660 720 870 Q680 915 635 885 Q545 690 480 480 Z', 'accent') +
    d.P('M410 420 Q395 230 455 110 Q500 85 500 150 L500 420 Z') +
    d.P('M590 420 Q605 230 545 110 Q500 85 500 150 L500 420 Z') +
    d.Lt('M470 190 L500 190') + d.Lt('M465 250 L500 250') + d.Lt('M530 190 L500 190') + d.Lt('M535 250 L500 250') +
    d.C(500, 430, 105, 'light') +
    d.face(500, 425, 140));

  A.add('saw', 'Saw', { main: R, dark: DB, light: GR, accent: Y, pink: P }, d => {
    // blade: top edge (360,330)-(880,420), rounded teeth along the bottom edge (880,500)-(360,600)
    const pts = [[360, 330], [880, 420], [880, 500]];
    const n = 13;
    for (let i = 0; i < n; i++) {
      const x0 = 880 - i * 40, y0 = 500 + i * 100 / n;
      pts.push([x0 - 20, y0 + 100 / n / 2 + 34], [x0 - 40, y0 + 100 / n]);
    }
    pts.push([360, 600]);
    return d.poly(pts, 'light') +
      d.R(130, 270, 280, 390, 100) +
      d.E(270, 470, 55, 100, 'none') +
      d.C(395, 400, 16, 'dark') + d.C(395, 540, 16, 'dark') +
      d.face(630, 460, 140);
  });

  A.add('drill', 'Drill', { main: G, dark: DG, light: GR, accent: Y, pink: P }, d =>
    d.R(380, 820, 260, 90, 30, 'dark') +
    g(d.R(410, 440, 170, 400, 60), 8, 495, 640) +
    d.R(560, 480, 50, 90, 20, 'accent') +
    d.P('M780 395 L900 405 L935 420 L900 435 L780 445 Z', 'light') +
    d.R(690, 350, 110, 140, 25, 'dark') +
    d.R(200, 290, 520, 230, 100) +
    d.face(440, 405, 160));

  A.add('toolbox', 'Toolbox', { main: R, dark: DG, light: GR, accent: Y, pink: P }, d =>
    handleTop(d, 380, 620, 330, 160, 50) +
    d.R(140, 320, 720, 500, 50) +
    d.L('M140 450 L860 450') +
    d.R(250, 420, 90, 70, 18, 'accent') + d.R(660, 420, 90, 70, 18, 'accent') +
    d.face(500, 630, 250));

  A.add('tape-measure', 'Tape Measure', { main: Y, dark: DG, light: W, accent: LY, pink: P }, d =>
    d.R(560, 640, 330, 70, 8, 'accent') +
    ticks(d, 600, 860, 640, 26, 18, 34, 4) +
    d.R(880, 615, 40, 120, 10, 'dark') +
    d.R(170, 250, 470, 470, 110) +
    d.R(330, 690, 140, 60, 20, 'dark') +
    d.C(405, 485, 150, 'light') +
    d.face(405, 480, 190));

  A.add('level', 'Level', { main: G, dark: DG, light: LY, accent: LB, pink: P }, d =>
    d.R(80, 390, 840, 220, 50) +
    d.R(140, 445, 170, 110, 45, 'light') + d.E(225, 500, 38, 28, 'accent') +
    d.L('M180 455 L180 545') + d.L('M270 455 L270 545') +
    d.R(760, 430, 100, 140, 40, 'light') + d.C(810, 500, 26, 'accent') +
    d.face(530, 495, 170));

  A.add('mallet', 'Mallet', { main: BR, dark: DB, light: TAN, accent: TAN, pink: P }, d =>
    d.R(450, 430, 100, 470, 45, 'accent') +
    d.R(200, 170, 600, 280, 100) +
    d.E(215, 310, 45, 135, 'light') + d.E(785, 310, 45, 135, 'light') +
    d.face(500, 305, 200));

  A.add('clamp', 'Clamp', { main: B, dark: DG, light: GR, accent: R, pink: P }, d =>
    d.R(565, 560, 70, 320, 12, 'light') +
    d.Lt('M570 640 L630 625') + d.Lt('M570 700 L630 685') + d.Lt('M570 760 L630 745') +
    d.R(440, 860, 320, 56, 28, 'accent') +
    d.P('M680 170 L380 170 Q190 170 190 360 L190 640 Q190 830 380 830 L680 830 L680 700 L430 700 Q360 700 360 630 L360 370 Q360 300 430 300 L680 300 Z') +
    d.R(530, 520, 140, 48, 16, 'dark') +
    d.R(610, 300, 90, 46, 14, 'dark') +
    d.face(275, 500, 150));

  A.add('ruler', 'Ruler', { main: Y, dark: DG, light: W, accent: O, pink: P }, d =>
    d.R(80, 370, 840, 260, 30) +
    ticks(d, 130, 870, 370, 37, 40, 75, 5) +
    d.face(500, 530, 160));

  A.add('pencil', 'Pencil', { main: O, dark: DG, light: GR, accent: TAN, pink: P }, d =>
    g(d.P('M760 390 L940 500 L760 610 Z', 'accent') +
      d.P('M880 463 L940 500 L880 537 Z', 'dark') +
      d.R(250, 390, 520, 220, 24) +
      d.R(70, 390, 150, 220, 50, 'pink') +
      d.R(195, 378, 75, 244, 14, 'light') +
      d.face(510, 495, 170), -25, 500, 500));

  // ---------------- Power and fix-it ----------------
  A.add('paint-roller', 'Paint Roller', { main: B, dark: DG, light: LB, accent: R, pink: P }, d =>
    d.R(760, 250, 120, 40, 20, 'dark') + d.R(840, 250, 40, 240, 20, 'dark') +
    d.R(480, 450, 400, 40, 20, 'dark') + d.R(480, 450, 40, 160, 20, 'dark') +
    d.R(440, 590, 120, 320, 55, 'accent') +
    d.R(140, 160, 640, 220, 100) +
    d.face(460, 265, 170));

  A.add('ladder', 'Ladder', { main: O, dark: DB, light: LY, accent: Y, pink: P }, d =>
    d.R(275, 200, 70, 700, 30) + d.R(655, 200, 70, 700, 30) +
    d.R(330, 400, 340, 52, 22, 'light') + d.R(330, 560, 340, 52, 22, 'light') + d.R(330, 720, 340, 52, 22, 'light') +
    d.R(240, 110, 520, 220, 60, 'accent') +
    d.face(500, 215, 170));

  A.add('light-bulb', 'Light Bulb', { main: Y, dark: DG, light: GR, accent: LY, pink: P }, d =>
    d.Lt('M500 60 L500 105') + d.Lt('M250 160 L285 195') + d.Lt('M750 160 L715 195') +
    d.Lt('M160 390 L205 390') + d.Lt('M840 390 L795 390') +
    d.R(390, 640, 220, 160, 30, 'light') +
    d.L('M392 690 L608 690') + d.L('M392 745 L608 745') +
    d.P('M440 798 L560 798 L540 860 L460 860 Z', 'dark') +
    d.P('M390 650 Q390 590 330 540 Q250 470 250 380 Q250 150 500 150 Q750 150 750 380 Q750 470 670 540 Q610 590 610 650 Z') +
    d.face(500, 390, 230));

  A.add('magnet', 'Magnet', { main: R, dark: DG, light: GR, accent: Y, pink: P }, d =>
    d.Lt('M260 110 L230 60') + d.Lt('M310 100 L310 45') + d.Lt('M690 100 L690 45') + d.Lt('M740 110 L770 60') +
    d.P('M200 230 L200 540 Q200 880 500 880 Q800 880 800 540 L800 230 L610 230 L610 540 Q610 690 500 690 Q390 690 390 540 L390 230 Z') +
    d.R(200, 140, 190, 130, 20, 'light') + d.R(610, 140, 190, 130, 20, 'light') +
    d.face(500, 775, 140));

  A.add('nails', 'Nails', { main: GR, dark: DG, light: W, accent: GR, pink: P }, d =>
    d.R(260, 270, 150, 520, 25) + d.P('M260 788 L410 788 L335 900 Z') + d.E(335, 260, 160, 50, 'dark') +
    d.R(600, 390, 150, 400, 25) + d.P('M600 788 L750 788 L675 900 Z') + d.E(675, 380, 160, 50, 'dark') +
    d.face(335, 450, 120) + d.face(675, 540, 120));

  A.add('nut-and-bolt', 'Nut & Bolt', { main: DG, dark: DB, light: GR, accent: GR, pink: P }, d =>
    d.R(330, 340, 120, 520, 18, 'light') +
    d.Lt('M335 420 L445 395') + d.Lt('M335 490 L445 465') + d.Lt('M335 560 L445 535') + d.Lt('M335 630 L445 605') + d.Lt('M335 700 L445 675') + d.Lt('M335 770 L445 745') +
    ngon(d, 390, 240, 165, 6, 0, 'main') +
    d.face(390, 235, 170) +
    ngon(d, 700, 640, 160, 6, 30, 'accent') + d.C(700, 640, 62, 'light'));

  A.add('tape', 'Tape', { main: LB, dark: DG, light: W, accent: GR, pink: P }, d =>
    d.P('M700 600 L900 640 L880 760 L690 700 Z', 'main') +
    d.C(450, 500, 330) + d.C(450, 500, 150, 'light') +
    d.face(450, 500, 170));

  // ---------------- Safety gear ----------------
  A.add('hard-hat', 'Hard Hat', { main: Y, dark: DG, light: LY, accent: Y, pink: P }, d =>
    d.E(500, 680, 360, 80, 'main') +
    d.P('M200 680 Q200 260 500 250 Q800 260 800 680 Z') +
    d.R(470, 235, 60, 150, 28, 'light') +
    d.face(500, 510, 220));

  A.add('safety-goggles', 'Safety Goggles', { main: B, dark: DG, light: W, accent: LB, pink: P }, d =>
    d.R(60, 440, 880, 110, 50, 'dark') +
    d.R(170, 320, 300, 330, 120, 'main') + d.R(530, 320, 300, 330, 120, 'main') +
    d.R(205, 355, 230, 260, 95, 'accent') + d.R(565, 355, 230, 260, 95, 'accent') +
    d.R(440, 430, 120, 80, 35, 'main') +
    d.eye(320, 485, 42) + d.eye(680, 485, 42) +
    d.smile(500, 760, 90, 60) +
    d.C(250, 720, 40, 'pink') + d.C(750, 720, 40, 'pink'));

  A.add('work-gloves', 'Work Gloves', { main: Y, dark: DB, light: TAN, accent: O, pink: P }, d =>
    d.R(320, 190, 80, 330, 40) + d.R(410, 140, 80, 360, 40) + d.R(500, 150, 80, 350, 40) + d.R(590, 210, 80, 300, 40) +
    g(d.R(220, 430, 100, 250, 50), -40, 270, 555) +
    d.R(310, 400, 370, 370, 90) +
    d.R(290, 740, 410, 160, 40, 'accent') +
    d.face(495, 585, 190));

  A.add('tool-belt', 'Tool Belt', { main: BR, dark: DB, light: TAN, accent: Y, pink: P }, d =>
    d.R(345, 200, 40, 200, 18, 'light') + d.R(285, 160, 160, 70, 24, 'dark') +
    d.R(205, 150, 70, 150, 32, 'accent') + d.R(228, 290, 24, 110, 10, 'light') +
    d.R(50, 300, 900, 90, 35, 'dark') +
    d.R(440, 280, 120, 130, 24, 'accent') + d.R(475, 315, 50, 60, 12, 'dark') +
    d.R(130, 380, 330, 380, 60) + d.L('M130 480 L460 480') +
    d.R(540, 380, 330, 380, 60) +
    d.face(705, 590, 190));

  A.add('traffic-cone', 'Traffic Cone', { main: O, dark: DG, light: W, accent: O, pink: P }, d =>
    d.R(200, 800, 600, 90, 30, 'dark') +
    d.P('M440 150 L560 150 L730 815 L270 815 Z') +
    d.P('M410 270 L590 270 L615 370 L385 370 Z', 'light') +
    d.P('M335 650 L665 650 L690 750 L310 750 Z', 'light') +
    d.face(500, 500, 170));

  // ---------------- Workshop and yard ----------------
  A.add('workbench', 'Workbench', { main: BR, dark: DB, light: TAN, accent: R, pink: P }, d =>
    d.R(170, 560, 80, 340, 15, 'dark') + d.R(750, 560, 80, 340, 15, 'dark') +
    d.R(200, 760, 600, 50, 15, 'light') +
    d.R(600, 240, 180, 100, 20, 'accent') + handleTop(d, 640, 740, 245, 190, 22) +
    d.R(80, 330, 840, 240, 30) + d.L('M80 400 L920 400') +
    d.face(500, 480, 170));

  A.add('sawhorse', 'Sawhorse', { main: TAN, dark: DB, light: BR, accent: TAN, pink: P }, d =>
    g(d.R(225, 380, 70, 520, 25, 'light'), 14, 260, 380) + g(d.R(705, 380, 70, 520, 25, 'light'), -14, 740, 380) +
    d.R(270, 700, 460, 50, 20, 'light') +
    d.R(100, 290, 800, 170, 40) +
    d.face(500, 370, 150));

  A.add('rake', 'Rake', { main: G, dark: DB, light: LG, accent: TAN, pink: P }, d => {
    let tines = '';
    for (let i = 0; i < 8; i++) tines += d.R(255 + i * 62, 700, 36, 170, 18);
    return d.R(470, 70, 60, 560, 30, 'accent') + tines + d.R(220, 600, 560, 130, 55) + d.face(500, 655, 120);
  });

  A.add('shovel', 'Shovel', { main: R, dark: DB, light: GR, accent: TAN, pink: P }, d =>
    handleTop(d, 400, 600, 250, 100, 48, 'dark') + d.R(400, 225, 200, 48, 22, 'dark') +
    d.R(465, 260, 70, 330, 25, 'accent') +
    d.P('M310 560 L690 560 L690 760 Q690 900 500 920 Q310 900 310 760 Z') +
    d.face(500, 720, 200));

  A.add('bucket', 'Bucket', { main: B, dark: DG, light: LB, accent: Y, pink: P }, d =>
    handleTop(d, 220, 780, 330, 110, 34) +
    d.P('M210 330 L790 330 L730 860 L270 860 Z') +
    d.R(180, 300, 640, 75, 37, 'light') +
    d.face(500, 590, 230));
})();
