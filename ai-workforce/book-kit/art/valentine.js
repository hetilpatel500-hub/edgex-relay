// "My First Valentine's Day": 30 friendly hearts, treats, cards and animal friends for ages 2-5.
// Generic subjects only: no brands, logos, candy trademarks or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const W = '#ffffff', R = '#ff5a6e', P = '#ffb3c7', LP = '#ffe0ea', RO = '#e8436a', Y = '#ffd23f', O = '#ff9f43',
    G = '#7bd389', B = '#8fd3ff', PU = '#c9a7ff', BR = '#c68b59', DB = '#8d5a3b', TAN = '#e8b98a', GR = '#cfd8dc', NV = '#3d4a5c', K = '#4a4a4a';

  const f = v => v.toFixed(1);
  const g = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // a heart centred on x,y, half-width s (about 1.7 s tall)
  const hp = (x, y, s) =>
    `M${f(x)} ${f(y + 0.85 * s)} C${f(x - 0.15 * s)} ${f(y + 0.7 * s)} ${f(x - s)} ${f(y + 0.2 * s)} ${f(x - s)} ${f(y - 0.25 * s)} ` +
    `C${f(x - s)} ${f(y - 0.75 * s)} ${f(x - 0.35 * s)} ${f(y - 0.95 * s)} ${f(x)} ${f(y - 0.45 * s)} ` +
    `C${f(x + 0.35 * s)} ${f(y - 0.95 * s)} ${f(x + s)} ${f(y - 0.75 * s)} ${f(x + s)} ${f(y - 0.25 * s)} ` +
    `C${f(x + s)} ${f(y + 0.2 * s)} ${f(x + 0.15 * s)} ${f(y + 0.7 * s)} ${f(x)} ${f(y + 0.85 * s)} Z`;
  const heart = (d, x, y, s, k = 'main', rot = 0) => rot ? g(d.P(hp(x, y, s), k), rot, x, y) : d.P(hp(x, y, s), k);
  // a ribbon bow centred on x,y
  const bow = (d, x, y, s = 1, k = 'accent') =>
    d.P(`M${x} ${y} Q${f(x - 60 * s)} ${f(y - 70 * s)} ${f(x - 105 * s)} ${f(y - 30 * s)} Q${f(x - 120 * s)} ${f(y + 30 * s)} ${x} ${y} Z`, k) +
    d.P(`M${x} ${y} Q${f(x + 60 * s)} ${f(y - 70 * s)} ${f(x + 105 * s)} ${f(y - 30 * s)} Q${f(x + 120 * s)} ${f(y + 30 * s)} ${x} ${y} Z`, k) +
    d.poly([[x - 12 * s, y + 5 * s], [x - 55 * s, y + 85 * s], [x - 22 * s, y + 80 * s]], k) +
    d.poly([[x + 12 * s, y + 5 * s], [x + 55 * s, y + 85 * s], [x + 22 * s, y + 80 * s]], k) +
    d.C(x, y, 24 * s, k);
  // a puffy cloud w wide, centred on cx,cy
  const cloud = (d, cx, cy, w, k = 'light') => {
    const p = (x, y) => `${f(cx + x * w)} ${f(cy + y * w)}`;
    return d.P(`M${p(-0.46, 0.19)} A1 1 0 0 1 ${p(-0.33, -0.05)} A1 1 0 0 1 ${p(-0.02, -0.28)} A1 1 0 0 1 ${p(0.3, -0.1)} A1 1 0 0 1 ${p(0.46, 0.19)} Q${p(0, 0.27)} ${p(-0.46, 0.19)} Z`, k);
  };
  // an animal sitting and hugging a big heart: tail, body, ears, head, face, heart, paws
  const sitter = (d, o) =>
    (o.tail ? o.tail(d) : '') +
    d.E(500, 690, 195, 200) +
    d.E(400, 878, 80, 44, o.paw || 'main') + d.E(600, 878, 80, 44, o.paw || 'main') +
    (o.back ? o.back(d) : '') +
    d.C(500, 330, 165) +
    (o.front ? o.front(d) : '') +
    o.face(d) +
    heart(d, 500, 692, 122, 'accent') +
    d.E(386, 650, 52, 46, o.paw || 'main') + d.E(614, 650, 52, 46, o.paw || 'main');

  // ---------------- hearts ----------------
  A.add('heart', 'Heart', { main: R, light: P, pink: P }, d =>
    heart(d, 185, 205, 58, 'light', -15) + heart(d, 815, 205, 58, 'light', 15) + heart(d, 860, 820, 45, 'light', 10) + heart(d, 140, 800, 45, 'light', -10) +
    heart(d, 500, 520, 320) + d.face(500, 520, 210));

  A.add('heart-balloons', 'Heart Balloons', { main: R, light: PU, accent: Y, accent2: B, pink: P }, d =>
    d.L('M314 528 L488 832 M500 425 L500 832 M686 528 L512 832') +
    heart(d, 290, 420, 138, 'light', -12) + heart(d, 710, 420, 138, 'accent2', 12) +
    heart(d, 500, 290, 165) +
    d.face(290, 425, 105) + d.face(710, 425, 105) + d.face(500, 290, 140) +
    bow(d, 500, 838, 0.8, 'accent'));

  A.add('heart-kite', 'Heart Kite', { main: R, accent: Y, light: P, pink: P }, d =>
    d.L('M440 400 Q700 520 900 930') +
    d.L('M496 552 Q580 650 505 735 Q430 820 470 915') +
    heart(d, 545, 650, 34, 'accent', 20) + heart(d, 475, 775, 34, 'accent', -20) + heart(d, 470, 905, 34, 'accent', 0) +
    heart(d, 430, 370, 235, 'main', -20) + d.face(430, 370, 180) +
    cloud(d, 805, 230, 250, 'light'));

  A.add('heart-glasses', 'Heart Glasses', { main: Y, accent: O, accent2: RO, light: P, pink: '#ff8fab' }, d => {
    let s = '';
    for (let i = 0; i < 12; i++) {
      const a = i * Math.PI / 6 + Math.PI / 12, q = (r, da) => [500 + Math.cos(a + da) * r, 520 + Math.sin(a + da) * r];
      s += d.poly([q(285, -0.13), q(410, 0), q(285, 0.13)], 'accent');
    }
    return s + d.C(500, 520, 300) +
      d.L('M215 455 L200 440 M785 455 L800 440') + d.L('M478 438 Q500 418 522 438') +
      heart(d, 355, 470, 140, 'accent2') + heart(d, 645, 470, 140, 'accent2') +
      heart(d, 355, 474, 102, 'light') + heart(d, 645, 474, 102, 'light') +
      d.Lt('M300 420 Q318 398 345 395 M590 420 Q608 398 635 395') +
      d.smile(500, 640, 95, 75) + d.C(330, 650, 32, 'pink') + d.C(670, 650, 32, 'pink');
  });

  A.add('heart-tree', 'Heart Tree', { main: G, dark: BR, accent: R, light: P, pink: P }, d =>
    d.grass(905) +
    d.P('M445 900 Q450 760 455 560 L545 560 Q550 760 555 900 Q610 905 640 925 L360 925 Q390 905 445 900 Z', 'dark') +
    heart(d, 500, 380, 310) +
    heart(d, 350, 330, 46, 'accent', -10) + heart(d, 650, 330, 46, 'accent', 10) + heart(d, 500, 360, 46, 'accent') +
    heart(d, 405, 470, 40, 'accent', -15) + heart(d, 595, 470, 40, 'accent', 15) + heart(d, 500, 560, 34, 'accent') +
    heart(d, 150, 700, 42, 'light', -15) + heart(d, 860, 640, 42, 'light', 15) + heart(d, 800, 820, 34, 'light', 5));

  A.add('rainbow', 'Rainbow', { main: R, accent: O, accent2: Y, dark: G, light: W, pink: P }, d => {
    const band = (R1, r, k) => d.P(`M${500 - R1} 720 A${R1} ${R1} 0 0 1 ${500 + R1} 720 L${500 + r} 720 A${r} ${r} 0 0 0 ${500 - r} 720 Z`, k);
    return band(400, 340, 'main') + band(340, 280, 'accent') + band(280, 220, 'accent2') + band(220, 160, 'dark') +
      cloud(d, 180, 740, 340) + cloud(d, 820, 740, 340) +
      heart(d, 500, 640, 95, 'main') + d.face(500, 632, 112);
  });

  // ---------------- sweet treats ----------------
  A.add('heart-cookie', 'Heart Cookie', { main: TAN, light: P, accent: R, accent2: Y, pink: '#ff8fab' }, d => {
    let s = heart(d, 500, 500, 330) + heart(d, 500, 505, 265, 'light') + d.face(500, 515, 180);
    [[330, 420, 30], [415, 345, -40], [585, 345, 40], [670, 420, -30], [360, 585, 60], [640, 585, -60], [500, 680, 0]].forEach(([x, y, a]) => {
      const c = Math.cos(a * Math.PI / 180) * 22, sn = Math.sin(a * Math.PI / 180) * 22;
      s += d.Lt(`M${f(x - c)} ${f(y - sn)} L${f(x + c)} ${f(y + sn)}`);
    });
    return s;
  });

  A.add('cupcake', 'Cupcake', { main: P, accent: PU, accent2: R, light: W, pink: '#ff8fab' }, d =>
    d.poly([[290, 610], [710, 610], [655, 890], [345, 890]], 'accent') +
    d.Lt('M400 625 L420 880 M500 625 L500 880 M600 625 L580 880') +
    d.P('M265 615 Q230 520 320 495 Q315 385 440 390 Q470 330 500 335 Q530 330 560 390 Q685 385 680 495 Q770 520 735 615 Z') +
    d.face(500, 520, 160) +
    heart(d, 500, 305, 72, 'accent2'));

  A.add('chocolates', 'Box of Chocolates', { main: R, light: P, dark: DB, accent: Y, pink: P }, d =>
    heart(d, 500, 540, 360) + heart(d, 500, 548, 292, 'light') +
    d.C(385, 450, 52, 'dark') + d.C(615, 450, 52, 'dark') + d.C(500, 545, 52, 'dark') + d.C(410, 645, 48, 'dark') + d.C(590, 645, 48, 'dark') +
    d.Lt('M360 445 Q385 425 410 445 M590 445 Q615 425 640 445 M475 540 Q500 520 525 540 M388 640 Q410 622 432 640 M568 640 Q590 622 612 640') +
    bow(d, 500, 355, 1, 'accent'));

  A.add('candy-hearts', 'Candy Hearts', { main: P, light: B, accent: Y, accent2: PU, pink: '#ff8fab' }, d =>
    heart(d, 180, 300, 42, 'accent2', -15) + heart(d, 820, 300, 42, 'accent', 15) +
    heart(d, 320, 640, 175, 'light', -14) + heart(d, 680, 640, 175, 'accent', 14) +
    heart(d, 500, 390, 175) +
    d.face(320, 650, 150) + d.face(680, 650, 150) + d.face(500, 390, 150));

  A.add('lollipop', 'Lollipop', { main: R, light: P, accent: Y, dark: W, pink: P }, d =>
    d.R(478, 560, 44, 360, 22, 'dark') +
    heart(d, 500, 380, 265) + heart(d, 500, 385, 205, 'light') + d.face(500, 395, 175) +
    bow(d, 500, 700, 0.85, 'accent'));

  A.add('heart-pizza', 'Heart Pizza', { main: Y, dark: TAN, accent: R, pink: P }, d =>
    heart(d, 500, 500, 340, 'dark') + heart(d, 500, 510, 285) +
    d.C(360, 410, 45, 'accent') + d.C(640, 410, 45, 'accent') + d.C(340, 560, 40, 'accent') + d.C(660, 560, 40, 'accent') + d.C(500, 660, 34, 'accent') +
    d.face(500, 515, 170));

  A.add('milkshake', 'Milkshake', { main: P, light: W, accent: R, accent2: B, dark: G, pink: '#ff8fab' }, d =>
    g(d.R(640, 110, 40, 270, 16, 'accent2'), 20, 660, 245) +
    d.P('M330 420 L670 420 L615 850 Q500 885 385 850 Z') +
    d.P('M305 435 Q290 335 395 340 Q415 255 500 262 Q585 255 605 340 Q710 335 695 435 Z', 'light') +
    d.L('M555 225 Q560 170 600 150') + d.C(555, 240, 40, 'accent') +
    d.face(500, 610, 170));

  // ---------------- cards and gifts ----------------
  A.add('valentine-card', 'Valentine Card', { main: W, light: P, accent: R, accent2: PU, pink: P }, d =>
    g(d.R(300, 180, 480, 620, 30, 'light'), 8, 540, 490) +
    g(d.R(220, 190, 500, 640, 30) +
      heart(d, 470, 470, 175, 'accent') + d.face(470, 470, 150) +
      heart(d, 290, 265, 34, 'accent2') + heart(d, 650, 265, 34, 'accent2') + heart(d, 290, 755, 34, 'accent2') + heart(d, 650, 755, 34, 'accent2'),
      -6, 470, 510));

  A.add('love-letter', 'Love Letter', { main: W, light: P, accent: R, accent2: PU, pink: P }, d =>
    heart(d, 320, 215, 46, 'accent2', -15) + heart(d, 500, 165, 58, 'accent') + heart(d, 680, 215, 46, 'accent2', 15) +
    d.R(170, 320, 660, 440, 30) +
    d.L('M178 752 L500 545 L822 752') +
    d.poly([[175, 328], [825, 328], [500, 585]], 'light') +
    heart(d, 500, 575, 82, 'accent'));

  A.add('present', 'Present', { main: P, light: W, accent: R, pink: P }, d =>
    d.R(235, 470, 530, 410, 22) + d.R(462, 470, 76, 410, 0, 'accent') +
    heart(d, 345, 680, 62, 'light') + heart(d, 655, 680, 62, 'light') +
    d.R(200, 380, 600, 110, 22) + d.R(462, 380, 76, 110, 0, 'accent') +
    heart(d, 405, 300, 90, 'accent', -55) + heart(d, 595, 300, 90, 'accent', 55) + d.C(500, 360, 38, 'accent'));

  A.add('flowers', 'Flowers', { main: P, accent: Y, accent2: R, dark: G, light: PU, pink: P }, d =>
    d.L('M330 420 L480 800 M500 300 L500 800 M670 420 L520 800') +
    d.E(290, 560, 85, 36, 'dark', -35) + d.E(710, 560, 85, 36, 'dark', 35) +
    d.scallop(330, 415, 68, 8, 44, 'light') + d.C(330, 415, 40, 'accent') +
    d.scallop(670, 415, 68, 8, 44, 'accent2') + d.C(670, 415, 40, 'accent') +
    d.scallop(500, 290, 72, 8, 46) + d.C(500, 290, 42, 'accent') +
    d.poly([[310, 530], [690, 530], [545, 905], [455, 905]], 'light') +
    heart(d, 500, 650, 62, 'accent2') +
    bow(d, 500, 775, 0.75, 'accent2'));

  A.add('rose', 'Rose', { main: R, dark: G, pink: P }, d =>
    d.R(482, 520, 36, 390, 18, 'dark') +
    d.P('M500 770 Q400 660 290 700 Q380 800 500 770 Z', 'dark') + d.P('M500 680 Q600 590 715 620 Q630 720 500 680 Z', 'dark') +
    d.Lt('M490 765 Q400 715 330 708 M510 676 Q600 635 680 625') +
    d.C(500, 350, 180) +
    d.P('M320 340 Q330 560 500 585 Q670 560 680 340 Q610 440 500 440 Q390 440 320 340 Z') +
    d.Lt('M500 395 Q425 380 432 315 Q445 245 520 250 Q590 262 580 330 Q570 375 515 362 Q478 352 487 318') +
    d.Lt('M360 300 Q390 230 450 205 M640 300 Q610 230 550 205'));

  A.add('teddy-bear', 'Teddy Bear', { main: BR, light: TAN, accent: R, pink: P }, d =>
    d.C(345, 200, 68) + d.C(655, 200, 68) + d.C(345, 200, 36, 'light') + d.C(655, 200, 36, 'light') +
    d.E(500, 690, 200, 205) + d.E(390, 880, 85, 48) + d.E(610, 880, 85, 48) +
    d.E(390, 885, 42, 26, 'light') + d.E(610, 885, 42, 26, 'light') +
    d.C(500, 330, 168) +
    d.E(500, 395, 78, 58, 'light') + d.E(500, 370, 28, 19, 'ink') + d.L('M500 390 L500 410 M466 410 Q500 436 534 410') +
    d.eye(435, 310) + d.eye(565, 310) +
    heart(d, 500, 692, 125, 'accent') +
    d.E(384, 650, 52, 46) + d.E(616, 650, 52, 46));

  A.add('balloon-ride', 'Hot Air Balloon', { main: R, accent: Y, dark: BR, light: W, pink: P }, d =>
    d.L('M430 520 L436 760 M570 520 L564 760') +
    d.R(405, 755, 190, 140, 22, 'dark') + d.Lt('M405 802 L595 802 M405 848 L595 848 M468 755 L468 895 M532 755 L532 895') +
    heart(d, 500, 330, 300) + d.face(500, 330, 200) +
    cloud(d, 150, 640, 210) + cloud(d, 860, 520, 210));

  // ---------------- animal friends ----------------
  A.add('puppy', 'Puppy', { main: TAN, dark: DB, light: W, accent: R, pink: P }, d => sitter(d, {
    tail: d => d.P('M660 760 Q800 720 790 600 Q770 585 755 605 Q760 690 650 715 Z'),
    front: d => d.E(318, 335, 58, 122, 'dark', 15) + d.E(682, 335, 58, 122, 'dark', -15),
    face: d => d.E(500, 398, 80, 58, 'light') + d.E(500, 372, 28, 19, 'ink') + d.L('M500 391 L500 410 M466 412 Q500 438 534 412') +
      d.eye(438, 312) + d.eye(562, 312),
  }));

  A.add('kitty', 'Kitty', { main: '#ffc38a', light: W, accent: R, pink: P }, d => sitter(d, {
    tail: d => d.P('M680 800 Q860 780 840 600 Q835 545 800 548 Q782 552 790 600 Q800 735 668 752 Z'),
    back: d => d.poly([[360, 250], [345, 95], [468, 188]]) + d.poly([[640, 250], [655, 95], [532, 188]]) +
      d.poly([[372, 215], [365, 135], [425, 182]], 'pink') + d.poly([[628, 215], [635, 135], [575, 182]], 'pink'),
    face: d => d.eye(435, 318) + d.eye(565, 318) +
      d.poly([[478, 372], [522, 372], [500, 395]], 'pink') +
      d.L('M500 395 Q488 420 462 408 M500 395 Q512 420 538 408') +
      d.L('M418 382 L300 362 M418 404 L305 420 M582 382 L700 362 M582 404 L695 420'),
  }));

  A.add('bunny', 'Bunny', { main: W, light: P, accent: R, pink: P }, d => sitter(d, {
    tail: d => d.C(692, 830, 48),
    back: d => d.E(428, 165, 50, 125) + d.E(572, 165, 50, 125) + d.E(428, 180, 24, 85, 'light') + d.E(572, 180, 24, 85, 'light'),
    face: d => d.eye(440, 318) + d.eye(560, 318) +
      heart(d, 500, 372, 22, 'pink') +
      d.L('M500 390 L500 405 M470 410 Q485 428 500 405 Q515 428 530 410') +
      d.C(405, 390, 24, 'pink') + d.C(595, 390, 24, 'pink'),
  }));

  A.add('panda', 'Panda', { main: W, dark: K, accent: R, pink: P }, d => sitter(d, {
    paw: 'dark',
    back: d => d.C(368, 198, 60, 'dark') + d.C(632, 198, 60, 'dark'),
    face: d => d.E(432, 328, 46, 62, 'dark', 30) + d.E(568, 328, 46, 62, 'dark', -30) +
      d.C(440, 320, 21, 'light') + d.C(560, 320, 21, 'light') + d.eye(440, 322, 15) + d.eye(560, 322, 15) +
      d.E(500, 390, 26, 18, 'ink') + d.L('M500 405 L500 420 M468 420 Q500 444 532 420'),
  }));

  A.add('mouse', 'Mouse', { main: GR, light: P, accent: R, pink: P }, d => sitter(d, {
    tail: d => d.L('M672 820 Q830 860 850 760 Q862 690 800 690'),
    back: d => d.C(340, 200, 95) + d.C(660, 200, 95) + d.C(340, 200, 58, 'light') + d.C(660, 200, 58, 'light'),
    face: d => d.eye(440, 322) + d.eye(560, 322) +
      d.C(500, 388, 22, 'pink') + d.L('M500 410 Q485 428 465 418 M500 410 Q515 428 535 418') +
      d.L('M430 392 L320 376 M430 410 L325 428 M570 392 L680 376 M570 410 L675 428'),
  }));

  A.add('lovebirds', 'Lovebirds', { main: G, light: Y, accent: R, accent2: O, dark: BR, pink: P }, d => {
    const bird = (m) => {
      const X = x => m ? 1000 - x : x;
      return d.L(`M${X(305)} 672 L${X(300)} 720 M${X(355)} 676 L${X(358)} 720`) +
        d.poly([[X(215), 585], [X(105), 545], [X(125), 640]]) +
        d.E(X(320), 580, 140, 112) + d.E(X(290), 592, 78, 48, 'light', m ? 20 : -20) +
        d.C(X(398), 450, 88) +
        d.poly([[X(472), 432], [X(492), 452], [X(472), 472]], 'accent2') +
        d.eye(X(418), 430, 18) + d.C(X(380), 480, 18, 'pink');
    };
    return d.P('M70 720 Q500 690 930 720 Q935 750 900 755 Q500 735 100 755 Q65 750 70 720 Z', 'dark') +
      d.E(180, 760, 50, 22, 'main', 25) + d.E(820, 760, 50, 22, 'main', -25) +
      bird(false) + bird(true) +
      heart(d, 500, 250, 95, 'accent') + heart(d, 380, 205, 36, 'accent', -15) + heart(d, 620, 205, 36, 'accent', 15);
  });

  A.add('penguins', 'Penguins', { main: NV, light: W, accent: R, accent2: O, pink: P }, d => {
    const peng = (x, m) =>
      d.E(x - 50, 800, 48, 24, 'accent2') + d.E(x + 50, 800, 48, 24, 'accent2') +
      d.E(x, 560, 150, 235) + d.E(x, 600, 108, 192, 'light') +
      d.E(x + (m ? 150 : -150), 600, 32, 90, 'main', m ? -20 : 20) +
      d.eye(x - 38, 455, 20) + d.eye(x + 38, 455, 20) +
      d.poly([[x - 24, 490], [x + 24, 490], [x, 520]], 'accent2') +
      d.C(x - 70, 500, 18, 'pink') + d.C(x + 70, 500, 18, 'pink');
    return peng(315, false) + peng(685, true) +
      heart(d, 500, 640, 108, 'accent');
  });

  A.add('ladybug', 'Ladybug', { main: R, dark: K, accent: K, light: P, pink: P }, d =>
    d.L('M290 520 L170 470 M280 650 L150 660 M310 780 L200 850 M710 520 L830 470 M720 650 L850 660 M690 780 L800 850') +
    d.L('M450 205 Q420 120 360 100 M550 205 Q580 120 640 100') + heart(d, 350, 95, 38, 'main', -15) + heart(d, 650, 95, 38, 'main', 15) +
    d.C(500, 600, 285) + d.L('M500 340 L500 880') +
    heart(d, 385, 500, 58, 'accent', -10) + heart(d, 615, 500, 58, 'accent', 10) +
    heart(d, 360, 690, 52, 'accent', -10) + heart(d, 640, 690, 52, 'accent', 10) +
    heart(d, 425, 815, 36, 'accent') + heart(d, 575, 815, 36, 'accent') +
    d.C(500, 300, 135, 'light') + d.face(500, 305, 135));

  A.add('octopus', 'Octopus', { main: PU, light: P, accent: R, pink: P }, d => {
    let s = '';
    const arm = i => { const cx = 215 + i * 114, rot = -(i - 2.5) * 16, t = rot * Math.PI / 180; return { cx, rot, tx: cx - 185 * Math.sin(t), ty: 690 + 185 * Math.cos(t) }; };
    for (let i = 0; i < 6; i++) { const a = arm(i); s += d.E(a.cx, 690, 52, 185, 'main', a.rot); }
    for (let i = 0; i < 6; i++) { const a = arm(i); s += d.C(a.tx, a.ty, 40); }
    const L0 = arm(0), L5 = arm(5);
    return s + heart(d, L0.tx - 20, L0.ty - 95, 60, 'accent', -15) + heart(d, L5.tx + 20, L5.ty - 95, 60, 'accent', 15) +
      d.C(500, 380, 245) + d.face(500, 420, 230) + heart(d, 500, 225, 45, 'light');
  });

  A.add('elephant', 'Elephant', { main: GR, light: P, accent: R, accent2: PU, pink: P }, d =>
    d.L('M845 580 Q905 620 885 690') + d.poly([[870, 680], [905, 700], [880, 730]]) +
    d.R(410, 690, 85, 200, 30) + d.R(525, 700, 85, 190, 30) + d.R(655, 700, 85, 190, 30) + d.R(765, 690, 85, 200, 30) +
    d.E(610, 600, 250, 190) +
    d.P('M235 505 Q95 475 110 300 Q140 280 170 300 Q165 395 240 440 Z') +
    d.C(330, 420, 150) +
    d.E(400, 435, 92, 125, 'light', -10) +
    d.eye(262, 392, 20) + d.L('M250 500 Q278 522 305 505') + d.C(230, 448, 18, 'pink') +
    heart(d, 640, 585, 82, 'accent') +
    d.L('M140 292 Q115 255 195 222') + heart(d, 205, 150, 82, 'accent2', 10) + d.face(205, 150, 75));
})();
