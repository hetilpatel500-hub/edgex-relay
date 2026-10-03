// "My First Dinosaurs": 30 friendly dinosaurs and dino things for ages 2-5.
// Three body plans (two-legged, four-legged, long-necked) plus each
// species' own features, all facing right.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const G = '#7bd389', DG = '#4caf50', O = '#ff9f43', Y = '#ffd23f', B = '#6ec6ff', PU = '#b39ddb', R = '#ff6b6b', P = '#ffb3c7', BR = '#c68b59', T = '#4db6ac';

  function sideFace(d, x, y, s = 1) {
    return d.eye(x, y, 22 * s) + `<circle cx="${x - 10 * s}" cy="${y + 48 * s}" r="${16 * s}" fill="${'#fff'}" stroke="#111" stroke-width="8"/>`;
  }
  // two-legged (T. rex style)
  function biped(d, o = {}) {
    const hx = o.hx || 690, hy = o.hy || 360, hrx = o.hrx || 150, hry = o.hry || 100, bry = o.bry || 150;
    const tip = o.tip || [60, 690];
    return (o.before ? o.before(d) : '') +
      d.P(`M430 540 C300 530 ${tip[0] + 110} ${tip[1] - 90} ${tip[0]} ${tip[1]} C${tip[0] + 130} ${tip[1]} 330 660 440 640 Z`) +
      d.E(440, 690, 70, 100) + d.R(410, 720, 55, 150, 25) + d.E(450, 880, 62, 24) +
      d.E(510, 670, 95, 125) + d.R(475, 700, 70, 165, 30) + d.E(525, 880, 80, 30) +
      d.E(530, 550, 175, bry, 'main', -25) +
      d.E(660, 600, 45, 18, 'main', 35) +
      (o.neck ? o.neck(d) : '') +
      d.E(hx, hy, hrx, hry, 'main', -5) +
      d.L(`M${hx - hrx * 0.75} ${hy + hry * 0.4} Q${hx} ${hy + hry * 0.62} ${hx + hrx * 0.9} ${hy + hry * 0.3}`) +
      d.eye(hx + 5, hy - hry * 0.38, 22) + d.dot(hx + hrx * 0.82, hy - hry * 0.15) +
      (o.after ? o.after(d, hx, hy, hrx, hry) : '');
  }
  // four-legged, low (Triceratops style)
  function quad(d, o = {}) {
    const hx = o.hx || 760, hy = o.hy || 560, hrx = o.hrx || 110, hry = o.hry || 80, bry = o.bry || 150;
    return (o.tail || d.P('M340 560 C240 560 130 610 50 640 C140 660 240 655 350 630 Z')) +
      d.R(330, 640, 62, o.leg || 200, 22) + d.R(600, 640, 62, o.leg || 200, 22) +
      (o.before ? o.before(d) : '') +
      d.R(385, 650, 72, (o.leg || 200) + 10, 26) + d.R(555, 650, 72, (o.leg || 200) + 10, 26) +
      d.E(470, 580, 230, bry) +
      (o.mid ? o.mid(d) : '') +
      (o.behindHead ? o.behindHead(d, hx, hy) : '') +
      d.E(hx, hy, hrx, hry) +
      d.eye(hx + 10, hy - hry * 0.3, 20) + d.smile(hx + hrx * 0.45, hy + hry * 0.3, 32, 18) +
      (o.after ? o.after(d, hx, hy, hrx, hry) : '');
  }
  // long neck (Brachiosaurus style)
  function longneck(d, o = {}) {
    const n = o.neck || 'M560 560 C600 450 620 330 650 250 L730 270 C700 350 680 470 660 600 Z';
    const h = o.head || [720, 240, 90, 55];
    return d.P(o.tail || 'M360 560 C250 560 150 620 70 600 C150 640 260 660 360 650 Z') +
      d.R(330, 620, 66, 250, 24) + d.R(600, 620, 66, 250, 24) +
      d.R(390, 640, 72, 240, 26) + d.R(545, 640, 72, 240, 26) +
      d.P(n) + d.E(480, 600, o.brx || 210, o.bry || 140) +
      d.E(h[0], h[1], h[2], h[3]) + d.eye(h[0] + 10, h[1] - 12, 18) + d.smile(h[0] + 45, h[1] + 18, 26, 14) +
      d.dot(h[0] + 70, h[1] - 20, 7) + (o.after ? o.after(d) : '');
  }
  const tri = (d, x1, y1, x2, y2, x3, y3, k = 'accent') => d.P(`M${x1} ${y1} L${x2} ${y2} L${x3} ${y3} Z`, k);

  A.add('trex', 'T. rex', { main: G, light: '#d8f5c8', pink: P }, d => biped(d));
  A.add('triceratops', 'Triceratops', { main: O, accent: Y, light: W(), pink: P }, d => quad(d, {
    behindHead: (d, x, y) => d.C(x - 75, y - 60, 135, 'accent') + [-150, -110, -70, -30, 10].map(a => { const r = a * Math.PI / 180; return d.C(x - 75 + 135 * Math.cos(r), y - 60 + 135 * Math.sin(r), 16, 'main'); }).join(''),
    after: (d, x, y) => tri(d, x - 25, y - 55, x + 120, y - 200, x + 25, y - 70, 'light') + tri(d, x + 25, y - 50, x + 170, y - 170, x + 70, y - 55, 'light') + tri(d, x + 80, y - 25, x + 130, y - 95, x + 108, y - 15, 'light'),
  }));
  A.add('stegosaurus', 'Stegosaurus', { main: G, accent: O, pink: P }, d => quad(d, {
    hx: 735, hy: 610, hrx: 80, hry: 55,
    before: d => [[270, 520, 60], [340, 450, 75], [430, 420, 85], [520, 420, 85], [610, 450, 70], [670, 510, 50]].map(([x, y, s]) => d.P(`M${x - s * 0.6} ${y + s * 0.5} L${x} ${y - s} L${x + s * 0.6} ${y + s * 0.5} Z`, 'accent')).join('') +
      tri(d, 90, 610, 40, 540, 110, 600) + tri(d, 130, 610, 110, 530, 150, 600),
  }));
  A.add('brachiosaurus', 'Brachiosaurus', { main: B, light: '#e0f4ff' }, d => longneck(d));
  A.add('diplodocus', 'Diplodocus', { main: PU, light: '#ece6f7' }, d => longneck(d, {
    neck: 'M620 520 C700 470 780 400 850 360 L880 420 C810 450 740 520 670 600 Z', head: [860, 380, 80, 50],
    tail: 'M300 560 C200 560 100 560 20 500 C110 600 200 650 320 650 Z', brx: 200, bry: 120,
  }));
  A.add('ankylosaurus', 'Ankylosaurus', { main: BR, light: '#f1d3b3', accent: '#8d5a3b', pink: P }, d => quad(d, {
    bry: 125, leg: 170, hx: 740, hy: 600, hrx: 95, hry: 65,
    tail: d.P('M320 580 C220 580 150 610 110 620 C150 650 230 650 330 640 Z') + d.C(80, 625, 55, 'accent'),
    mid: d => [[340, 520], [420, 480], [500, 470], [580, 490], [650, 530], [380, 590], [470, 570], [560, 580]].map(([x, y]) => d.C(x, y, 22, 'accent')).join(''),
  }));
  A.add('pteranodon', 'Pteranodon', { main: T, accent: '#b2dfdb', pink: P }, d =>
    d.P('M470 480 C360 380 200 330 60 380 C170 430 250 520 330 620 C390 560 440 530 470 540 Z', 'accent') +
    d.P('M530 480 C640 380 800 330 940 380 C830 430 750 520 670 620 C610 560 560 530 530 540 Z', 'accent') +
    d.E(500, 560, 70, 150) + d.L('M470 700 L440 780 M530 700 L560 780') +
    d.P('M470 360 L360 330 L470 400 Z') + d.C(500, 380, 70) + d.P('M540 360 L720 420 L545 420 Z', 'main') +
    d.eye(510, 365, 16) + d.C(480, 405, 12, 'pink'));
  A.add('spinosaurus', 'Spinosaurus', { main: T, accent: O, light: '#d2f2ee', pink: P }, d => biped(d, {
    hx: 720, hy: 380, hrx: 170, hry: 72,
    before: d => d.P('M370 470 C400 220 640 200 690 440 Z', 'accent') + d.Lt('M450 440 L470 280 M530 440 L550 250 M610 440 L620 290'),
  }));
  A.add('parasaurolophus', 'Parasaurolophus', { main: Y, accent: O, light: '#fff3d6', pink: P }, d => biped(d, {
    hx: 700, hy: 380, hrx: 130, hry: 80,
    after: (d, x, y) => d.P(`M${x - 60} ${y - 55} Q${x - 160} ${y - 170} ${x - 250} ${y - 190} L${x - 262} ${y - 158} Q${x - 170} ${y - 130} ${x - 90} ${y - 20} Z`, 'accent'),
  }));
  A.add('velociraptor', 'Velociraptor', { main: '#ffab91', light: '#ffe0d6', pink: P }, d => biped(d, {
    hx: 710, hy: 390, hrx: 130, hry: 70, bry: 115, tip: [30, 560],
    after: () => d.P('M555 875 Q575 820 610 830 Q585 850 575 880 Z', 'main'),
  }));
  A.add('pachycephalosaurus', 'Pachycephalosaurus', { main: G, accent: BR, light: '#d8f5c8', pink: P }, d => biped(d, {
    hx: 690, hy: 390, hrx: 120, hry: 90,
    after: (d, x, y) => d.P(`M${x - 95} ${y - 30} C${x - 90} ${y - 170} ${x + 90} ${y - 170} ${x + 95} ${y - 30} Q${x} ${y - 55} ${x - 95} ${y - 30} Z`, 'accent') +
      [[-100, -20], [-70, -80], [70, -80], [100, -20]].map(([dx, dy]) => d.C(x + dx, y + dy, 14, 'main')).join('') + d.eye(x + 5, y - 20, 20),
  }));
  A.add('iguanodon', 'Iguanodon', { main: '#aed581', light: '#e8f5d0', pink: P }, d => quad(d, {
    hx: 770, hy: 520, hrx: 115, hry: 70,
    after: () => tri(d, 600, 850, 650, 790, 640, 860, 'light'),
  }));
  A.add('dino-egg', 'Dino Egg', { main: '#fff3d6', accent: G, pink: P }, d =>
    d.P('M500 200 C680 200 780 480 780 620 C780 790 660 880 500 880 C340 880 220 790 220 620 C220 480 320 200 500 200 Z') +
    [[400, 380, 40], [590, 330, 30], [620, 520, 50], [380, 620, 45], [540, 720, 40], [470, 480, 25]].map(([x, y, r]) => d.C(x, y, r, 'accent')).join('') +
    d.grass(930));
  A.add('baby-dino', 'Baby Dino', { main: G, light: '#fff3d6', pink: P }, d =>
    d.C(500, 400, 170) + d.face(500, 420, 200) + d.E(390, 530, 40, 25, 'main', -30) + d.E(610, 530, 40, 25, 'main', 30) +
    d.P('M250 520 L320 470 L380 540 L440 470 L500 540 L560 470 L620 540 L680 470 L750 520 C780 700 690 850 500 850 C310 850 220 700 250 520 Z', 'light') +
    d.C(380, 690, 30, 'pink') + d.C(620, 720, 24, 'pink'));
  A.add('plesiosaurus', 'Plesiosaurus', { main: B, light: '#e0f4ff', pink: P }, d =>
    d.E(330, 700, 90, 35, 'main', 25) + d.E(620, 710, 90, 35, 'main', -25) +
    d.P('M660 580 C720 480 700 330 740 250 L800 270 C770 350 780 500 720 610 Z') +
    d.E(450, 620, 230, 110) + d.P('M230 610 C150 620 100 650 60 690 C130 690 190 670 240 650 Z') +
    d.E(380, 740, 90, 35, 'main', 25) + d.E(560, 750, 90, 35, 'main', -25) +
    d.E(790, 245, 75, 50) + d.eye(800, 232, 16) + d.smile(830, 262, 22, 12) + d.water(900));
  A.add('dimetrodon', 'Dimetrodon', { main: PU, accent: '#f8bbd0', pink: P }, d => quad(d, {
    bry: 110, leg: 150, hx: 750, hy: 590, hrx: 105, hry: 65,
    before: d => d.P('M280 560 C280 300 650 300 660 560 Z', 'accent') + d.Lt('M360 540 L360 380 M440 540 L445 340 M520 540 L525 340 M600 540 L595 400'),
  }));
  A.add('allosaurus', 'Allosaurus', { main: '#ffcc80', light: '#fff0d9', pink: P }, d => biped(d, {
    after: (d, x, y) => tri(d, x - 10, y - 88, x + 10, y - 135, x + 30, y - 90, 'main') + d.Lt('M470 480 L500 520 M520 470 L550 510 M570 470 L590 505'),
  }));
  A.add('protoceratops', 'Protoceratops', { main: '#ffe082', accent: O, pink: P }, d => quad(d, {
    bry: 130, leg: 170, hx: 750, hy: 580, hrx: 100, hry: 75,
    behindHead: (d, x, y) => d.C(x - 70, y - 60, 100, 'accent'),
    after: (d, x, y) => d.P(`M${x + 80} ${y - 20} Q${x + 130} ${y + 10} ${x + 95} ${y + 45} Z`, 'main'),
  }));
  A.add('styracosaurus', 'Styracosaurus', { main: G, accent: Y, light: W(), pink: P }, d => quad(d, {
    behindHead: (d, x, y) => [-60, -30, 0, 30, 60].map(a => { const r = (a - 90) * Math.PI / 180, cx = x - 80, cy = y - 70; return tri(d, cx + 90 * Math.cos(r - 0.18), cy + 90 * Math.sin(r - 0.18), cx + 190 * Math.cos(r), cy + 190 * Math.sin(r), cx + 90 * Math.cos(r + 0.18), cy + 90 * Math.sin(r + 0.18), 'light'); }).join('') + d.C(x - 80, y - 70, 110, 'accent'),
    after: (d, x, y) => tri(d, x + 60, y - 50, x + 110, y - 190, x + 105, y - 45, 'light'),
  }));
  A.add('baby-trex', 'Baby T. rex', { main: '#80cbc4', light: '#e0f2f1', pink: P }, d => biped(d, { hx: 690, hy: 380, hrx: 175, hry: 135, bry: 130 }));
  A.add('volcano', 'Volcano', { main: BR, accent: R, light: '#eceff1' }, d =>
    d.C(420, 190, 60, 'light') + d.C(500, 160, 75, 'light') + d.C(590, 195, 60, 'light') +
    d.P('M150 880 L400 330 L600 330 L850 880 Z') +
    d.P('M400 330 L600 330 L590 380 Q560 460 540 400 Q520 520 490 410 Q460 470 440 390 Q420 430 410 360 Z', 'accent') +
    d.E(500, 330, 100, 24, 'accent') + d.grass(900));
  A.add('footprint', 'Dino Footprint', { main: '#d7ccc8' }, d =>
    d.P('M500 880 C360 880 300 760 330 640 C350 560 420 520 500 520 C580 520 650 560 670 640 C700 760 640 880 500 880 Z') +
    d.P('M400 560 C300 460 260 330 300 260 C340 230 380 280 390 340 C400 420 450 480 460 530 Z') +
    d.P('M600 560 C700 460 740 330 700 260 C660 230 620 280 610 340 C600 420 550 480 540 530 Z') +
    d.P('M470 520 C450 380 450 220 500 170 C550 220 550 380 530 520 Z'));
  A.add('fossil', 'Fossil', { main: '#ffe0b2', light: '#d7ccc8' }, d =>
    d.C(500, 520, 280, 'light') + d.C(500, 520, 250) +
    d.L('M500 520 m30 0 a30 30 0 1 1 -60 0 a60 60 0 1 1 120 0 a90 90 0 1 1 -180 0 a120 120 0 1 1 240 0 a150 150 0 1 1 -300 0') +
    d.Lt('M500 400 L500 360 M620 520 L660 520 M500 640 L500 690 M380 520 L340 520'));
  A.add('dino-nest', 'Dino Nest', { main: '#fff3d6', dark: BR, accent: G }, d =>
    d.E(360, 520, 95, 125) + d.E(640, 520, 95, 125) + d.E(500, 480, 105, 140) +
    d.C(330, 470, 22, 'accent') + d.C(520, 420, 26, 'accent') + d.C(650, 480, 22, 'accent') +
    d.P('M160 560 Q500 640 840 560 Q820 820 500 850 Q180 820 160 560 Z', 'dark') +
    d.Lt('M220 640 L380 700 M320 620 L520 700 M500 620 L700 690 M620 620 L780 660 M260 740 L460 780 M520 760 L720 740'));
  A.add('palm-tree', 'Palm Tree', { main: BR, accent: G }, d =>
    d.P('M470 360 C460 520 450 700 420 880 L530 880 C540 700 540 520 530 360 Z') +
    d.Lt('M455 450 L535 450 M450 560 L538 560 M442 670 L538 670 M432 780 L535 780') +
    [[-1, -20], [1, -20], [-1, 25], [1, 25], [0, -60]].map(([sx, dy]) => d.P(`M500 360 Q${500 + sx * 180} ${280 + dy} ${500 + sx * 330} ${400 + dy} Q${500 + sx * 200} ${340 + dy} 500 380 Z`, 'accent')).join('') +
    d.C(470, 400, 30, 'main') + d.C(530, 400, 30, 'main') + d.grass(900));
  A.add('archaeopteryx', 'Archaeopteryx', { main: '#90caf9', accent: '#ce93d8', light: '#e3f2fd', pink: P }, d =>
    d.P('M380 560 C260 600 160 640 70 620 C120 660 150 690 110 740 C200 720 300 680 400 640 Z', 'accent') +
    d.L('M470 700 L450 820 M540 700 L560 820 M420 830 L450 820 L470 840 M540 840 L560 820 L590 830') +
    d.E(480, 580, 140, 130) +
    d.P('M430 520 C520 440 680 470 700 560 C620 540 560 600 470 640 Z', 'accent') +
    d.C(620, 380, 90) + d.P('M690 370 L790 395 L690 410 Z', 'light') +
    d.eye(630, 360, 18) + d.C(600, 405, 14, 'pink'));
  A.add('brontosaurus', 'Brontosaurus', { main: '#aed581', light: '#e8f5d0' }, d => longneck(d, {
    neck: 'M580 540 C650 470 700 380 740 320 L800 350 C760 410 720 500 670 590 Z', head: [790, 330, 80, 50], brx: 230, bry: 155,
  }));
  A.add('carnotaurus', 'Carnotaurus', { main: R, light: '#ffd6d6', pink: '#ffe0e6' }, d => biped(d, {
    hry: 90,
    after: (d, x, y) => d.P(`M${x - 40} ${y - 70} Q${x - 70} ${y - 150} ${x - 10} ${y - 150} Q${x - 30} ${y - 110} ${x - 10} ${y - 80} Z`, 'light') +
      d.P(`M${x + 30} ${y - 75} Q${x + 20} ${y - 160} ${x + 80} ${y - 150} Q${x + 50} ${y - 115} ${x + 55} ${y - 80} Z`, 'light'),
  }));
  A.add('kentrosaurus', 'Kentrosaurus', { main: '#ffcc80', accent: '#fff3d6', pink: P }, d => quad(d, {
    hx: 735, hy: 610, hrx: 80, hry: 55,
    before: d => [[300, 500], [370, 450], [450, 425], [530, 425], [610, 450], [120, 590], [180, 580], [240, 560]].map(([x, y]) => tri(d, x - 22, y + 30, x, y - 70, x + 22, y + 30, 'accent')).join(''),
  }));
  A.add('maiasaura', 'Maiasaura', { main: '#b39ddb', light: '#ede7f6', pink: P }, d => quad(d, {
    hx: 770, hy: 520, hrx: 120, hry: 70,
    after: (d, x, y) => d.P(`M${x + 70} ${y - 10} Q${x + 170} ${y} ${x + 160} ${y + 40} Q${x + 110} ${y + 60} ${x + 70} ${y + 40} Z`, 'light'),
  }));

  function W() { return '#ffffff'; }
})();
