// "My First Weather & Nature": 30 friendly weather and outdoor things for ages 2-5.
// Generic subjects only: no brands, logos or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', G = '#7bd389', Y = '#ffd23f', O = '#ff9f43', B = '#6ec6ff', PU = '#b39ddb', P = '#ffb3c7', BR = '#c68b59', T = '#4db6ac', W = '#ffffff', GR = '#cfd8dc', DG = '#4caf50';

  const f = v => v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // a puffy cloud w wide, centred on cx,cy: four round bumps and a soft flat bottom
  const cloud = (d, cx, cy, w, k = 'main') => {
    const p = (x, y) => `${f(cx + x * w)} ${f(cy + y * w)}`;
    return d.P(`M${p(-0.46, 0.19)} A1 1 0 0 1 ${p(-0.33, -0.05)} A1 1 0 0 1 ${p(-0.02, -0.28)} A1 1 0 0 1 ${p(0.3, -0.1)} A1 1 0 0 1 ${p(0.46, 0.19)} Q${p(0, 0.27)} ${p(-0.46, 0.19)} Z`, k);
  };
  // a raindrop with its tip s above y and a round bottom
  const drop = (d, x, y, s, k = 'accent') =>
    d.P(`M${x} ${y - s} C${x + 0.35 * s} ${y - 0.55 * s} ${x + 0.55 * s} ${y - 0.1 * s} ${x + 0.55 * s} ${y + 0.35 * s} A${0.55 * s} ${0.55 * s} 0 0 1 ${x - 0.55 * s} ${y + 0.35 * s} C${x - 0.55 * s} ${y - 0.1 * s} ${x - 0.35 * s} ${y - 0.55 * s} ${x} ${y - s} Z`, k);
  // sun rays: n pointed triangles around a disc of radius r (the disc goes on top)
  const rays = (d, cx, cy, r, n = 12, k = 'accent') => {
    let s = '';
    for (let i = 0; i < n; i++) {
      const a = i / n * 2 * Math.PI, w = Math.PI / n * 0.62;
      s += d.poly([[cx + r * 0.9 * Math.cos(a - w), cy + r * 0.9 * Math.sin(a - w)], [cx + r * 1.5 * Math.cos(a), cy + r * 1.5 * Math.sin(a)], [cx + r * 0.9 * Math.cos(a + w), cy + r * 0.9 * Math.sin(a + w)]], k);
    }
    return s;
  };
  const heart = (d, cx, cy, s, k = 'main') =>
    d.P(`M${cx} ${cy + s * 0.9} C${cx - s * 1.4} ${cy} ${cx - s * 0.9} ${cy - s * 1.1} ${cx} ${cy - s * 0.45} C${cx + s * 0.9} ${cy - s * 1.1} ${cx + s * 1.4} ${cy} ${cx} ${cy + s * 0.9} Z`, k);
  const flower = (d, cx, cy, r, k = 'accent', c = 'accent2') => {
    let s = '';
    for (let i = 0; i < 6; i++) { const a = i / 6 * 2 * Math.PI; s += d.C(cx + r * Math.cos(a), cy + r * Math.sin(a), r * 0.68, k); }
    return s + d.C(cx, cy, r * 0.75, c);
  };

  // ---------------- weather ----------------
  A.add('sun', 'Sun', { main: Y, accent: O, pink: P }, d =>
    rays(d, 500, 500, 265) + d.C(500, 500, 250) + d.face(500, 490, 270));

  A.add('cloud', 'Cloud', { main: W, pink: P }, d =>
    cloud(d, 500, 520, 760) + d.face(500, 540, 240));

  A.add('sun-cloud', 'Sun and Cloud', { main: W, accent: Y, accent2: O, pink: P }, d =>
    rays(d, 640, 320, 165, 12, 'accent2') + d.C(640, 320, 160, 'accent') + d.face(640, 300, 140) +
    cloud(d, 430, 620, 640) + d.face(430, 640, 190));

  A.add('rain-cloud', 'Rain Cloud', { main: GR, accent: B, pink: P }, d =>
    drop(d, 290, 700, 62) + drop(d, 500, 770, 62) + drop(d, 710, 700, 62) +
    drop(d, 395, 885, 48) + drop(d, 605, 885, 48) +
    cloud(d, 500, 380, 680) + d.face(500, 400, 200));

  A.add('raindrop', 'Raindrop', { main: B, pink: P }, d =>
    drop(d, 500, 520, 400, 'main') + d.face(500, 650, 220) +
    d.Lt('M380 470 Q395 420 425 385'));

  A.add('storm-cloud', 'Storm Cloud', { main: GR, accent: Y, accent2: B, pink: P }, d =>
    d.poly([[540, 560], [430, 760], [510, 760], [450, 930], [640, 700], [555, 700], [620, 560]], 'accent') +
    drop(d, 280, 720, 55, 'accent2') + drop(d, 740, 720, 55, 'accent2') +
    cloud(d, 500, 400, 660) + d.face(500, 420, 200));

  A.add('rainbow', 'Rainbow', { main: R, dark: O, accent: Y, accent2: G, light: B, pink: P }, d => {
    const arc = (r, k) => d.P(`M${500 - r} 720 A${r} ${r} 0 0 1 ${500 + r} 720 Z`, k);
    return arc(390, 'main') + arc(330, 'dark') + arc(270, 'accent') + arc(210, 'accent2') + arc(150, 'light') +
      arc(90, 'sky') +
      cloud(d, 225, 745, 330, 'sky') + d.face(225, 752, 100) +
      cloud(d, 775, 745, 330, 'sky') + d.face(775, 752, 100);
  });

  A.add('wind', 'Wind', { main: W, light: '#e3f4ff', accent: O, pink: P }, d =>
    d.L('M610 390 L800 390 Q870 390 870 330 Q870 280 820 280 Q780 280 785 320') +
    d.L('M640 500 L880 500') +
    d.L('M610 610 L780 610 Q850 610 850 670 Q850 720 800 720 Q760 720 765 680') +
    d.E(780, 840, 65, 32, 'accent', -25) + d.Lt('M730 862 L830 818') +
    cloud(d, 360, 500, 560) + d.face(360, 505, 175));

  A.add('snowflake', 'Snowflake', { main: '#e3f4ff', light: W, pink: P }, d => {
    let br = '', arms = '';
    for (let i = 0; i < 6; i++) {
      const a = i * 60;
      br += group(group(d.R(472, 165, 56, 125, 28), 45, 500, 280) + group(d.R(472, 165, 56, 125, 28), -45, 500, 280), a);
      arms += group(d.R(468, 110, 64, 400, 32), a);
    }
    return br + arms + d.C(500, 500, 135, 'light') + d.face(500, 495, 165);
  });

  A.add('snowman', 'Snowman', { main: W, accent: R, accent2: Y, dark: '#555', pink: P }, d =>
    d.L('M340 480 L160 370 M215 404 L195 320') + d.L('M660 480 L840 370 M785 404 L805 320') +
    d.C(500, 730, 210) + d.C(500, 470, 160) +
    d.C(500, 440, 20, 'accent2') + d.C(500, 510, 20, 'accent2') + d.C(500, 580, 20, 'accent2') +
    d.C(500, 250, 120) + d.face(500, 240, 150) +
    d.R(568, 375, 55, 135, 25, 'accent') + d.R(372, 352, 256, 55, 27, 'accent') +
    d.R(410, 28, 180, 125, 16, 'dark') + d.R(375, 138, 250, 38, 19, 'dark'));

  A.add('rain-boots', 'Rain Boots', { main: Y, accent: O, dark: '#555', pink: P }, d => {
    const boot = x0 => d.P(`M${x0} 255 Q${x0} 240 ${x0 + 15} 240 L${x0 + 155} 240 Q${x0 + 170} 240 ${x0 + 170} 255 L${x0 + 170} 600 Q${x0 + 170} 640 ${x0 + 215} 650 Q${x0 + 320} 670 ${x0 + 320} 760 L${x0 + 320} 800 Q${x0 + 320} 830 ${x0 + 290} 830 L${x0 + 30} 830 Q${x0} 830 ${x0} 800 Z`) +
      d.R(x0 - 6, 790, 332, 58, 24, 'dark') + d.R(x0 - 16, 222, 202, 62, 26, 'accent') + d.face(x0 + 85, 440, 120);
    return boot(130) + boot(520);
  });

  A.add('raincoat', 'Raincoat', { main: Y, light: '#fff3d6', accent: R, pink: P }, d =>
    d.P('M352 360 L212 640 Q218 690 272 690 L392 480 Z') + d.P('M648 360 L788 640 Q782 690 728 690 L608 480 Z') +
    d.P('M340 340 L660 340 L750 820 Q500 870 250 820 Z') +
    d.Lt('M500 400 L500 845') +
    d.C(500, 480, 18, 'accent') + d.C(500, 590, 18, 'accent') + d.C(500, 700, 18, 'accent') +
    d.R(312, 640, 118, 90, 20, 'accent') + d.R(570, 640, 118, 90, 20, 'accent') +
    d.E(500, 250, 165, 140) + d.E(500, 265, 105, 95, 'light') + d.face(500, 262, 150));

  A.add('mittens', 'Mittens', { main: R, accent: W, pink: P }, d => {
    const mit = (x, sd) => d.E(x + sd * 112, 480, 50, 92, 'main', sd * 25) +
      d.R(x - 115, 240, 230, 430, 115) + d.R(x - 125, 640, 250, 120, 35, 'accent') + d.face(x, 425, 150);
    return d.L('M320 760 Q500 905 680 760') + mit(320, 1) + mit(680, -1);
  });

  A.add('winter-hat', 'Winter Hat', { main: B, accent: W, accent2: R, pink: P }, d =>
    d.P('M220 640 Q220 300 500 280 Q780 300 780 640 Z') +
    d.scallop(500, 235, 55, 10, 42, 'accent2') +
    d.R(190, 600, 620, 150, 40, 'accent') +
    d.face(500, 465, 190));

  A.add('sled', 'Sled', { main: R, dark: BR, accent: Y, pink: P }, d =>
    d.R(300, 540, 40, 115, 10, 'dark') + d.R(640, 540, 40, 115, 10, 'dark') +
    d.L('M180 660 L760 660 Q850 660 850 580') +
    d.Lt('M800 470 Q880 430 905 505') +
    d.R(170, 430, 630, 125, 40) + d.face(485, 488, 120) +
    d.grass(760));

  A.add('puddle', 'Puddle', { main: B, accent: '#d7f0ff', pink: P }, d =>
    drop(d, 330, 360, 72) + drop(d, 500, 275, 82) + drop(d, 670, 360, 72) +
    d.L('M165 620 L120 570') + d.L('M835 620 L880 570') +
    d.E(500, 700, 340, 150) + d.face(500, 690, 180));

  A.add('sunglasses', 'Sunglasses', { main: PU, light: '#e3f4ff', dark: '#555', accent: Y, accent2: O, pink: P }, d =>
    rays(d, 500, 175, 72, 10, 'accent2') + d.C(500, 175, 72, 'accent') +
    d.L('M178 445 L95 360') + d.L('M822 445 L905 360') +
    d.R(160, 400, 300, 240, 100, 'main') + d.R(540, 400, 300, 240, 100, 'main') +
    d.R(188, 428, 244, 184, 78, 'light') + d.R(568, 428, 244, 184, 78, 'light') +
    d.P('M452 470 Q500 430 548 470 L548 502 Q500 466 452 502 Z', 'main') +
    d.Lt('M245 500 L300 465') + d.Lt('M625 500 L680 465'));

  // ---------------- nature ----------------
  A.add('tree', 'Tree', { main: G, dark: BR, accent: R, pink: P }, d =>
    d.R(440, 560, 120, 330, 30, 'dark') +
    d.scallop(500, 400, 200, 9, 105) + d.face(500, 420, 220) +
    d.C(360, 320, 28, 'accent') + d.C(655, 300, 28, 'accent') + d.C(660, 520, 28, 'accent') +
    d.grass(890));

  A.add('pine-tree', 'Pine Tree', { main: DG, dark: BR, pink: P }, d => {
    const tier = (y0, y1, hw) => d.P(`M500 ${y0} L${500 + hw} ${y1} Q${500 + hw + 12} ${y1 + 28} ${500 + hw - 22} ${y1 + 28} L${500 - hw + 22} ${y1 + 28} Q${500 - hw - 12} ${y1 + 28} ${500 - hw} ${y1} Z`);
    return d.R(450, 790, 100, 120, 16, 'dark') + tier(520, 780, 300) + tier(330, 590, 230) + tier(150, 410, 160) + d.face(500, 690, 170);
  });

  A.add('acorn', 'Acorn', { main: O, dark: BR, pink: P }, d =>
    d.R(478, 185, 44, 90, 16, 'dark') +
    d.P('M305 450 Q300 790 500 865 Q700 790 695 450 Z') +
    d.P('M258 470 Q262 262 500 250 Q738 262 742 470 Q500 525 258 470 Z', 'dark') +
    d.Lt('M310 400 Q500 360 690 400') +
    d.face(500, 650, 190));

  A.add('bush', 'Bush', { main: G, accent: PU, pink: P }, d =>
    d.scallop(500, 540, 220, 10, 115) + d.face(500, 560, 220) +
    d.C(330, 400, 26, 'accent') + d.C(680, 410, 26, 'accent') + d.C(300, 650, 26, 'accent') + d.C(705, 655, 26, 'accent') + d.C(560, 320, 26, 'accent') +
    d.grass(890));

  A.add('maple-leaf', 'Maple Leaf', { main: O, dark: BR, pink: P }, d => {
    const rt = [[500, 110], [565, 250], [650, 215], [625, 345], [770, 290], [730, 420], [870, 440], [745, 540], [790, 625], [620, 600], [540, 690], [515, 700]];
    const lf = rt.slice(1, -1).reverse().map(([x, y]) => [1000 - x, y]);
    return d.R(488, 680, 24, 220, 10, 'dark') + d.poly(rt.concat([[485, 700]], lf)) + d.face(500, 455, 190);
  });

  A.add('clover', 'Clover', { main: G, light: W, pink: P }, d =>
    d.L('M500 480 Q470 700 560 905') +
    group(heart(d, 500, 330, 140), 120, 500, 480) + group(heart(d, 500, 330, 140), -120, 500, 480) +
    heart(d, 500, 330, 140) + d.C(500, 480, 30, 'light') + d.face(500, 300, 140));

  A.add('cactus', 'Cactus', { main: G, accent: O, accent2: P, light: Y, pink: P }, d =>
    d.P('M460 590 L330 590 Q250 590 250 510 L250 380 A50 50 0 0 1 350 380 L350 470 Q350 490 370 490 L460 490 Z') +
    d.P('M540 510 L670 510 Q750 510 750 430 L750 300 A50 50 0 0 0 650 300 L650 390 Q650 410 630 410 L540 410 Z') +
    d.R(400, 190, 200, 620, 100) + flower(d, 500, 200, 28, 'accent2', 'light') +
    d.P('M330 830 L670 830 L630 940 L370 940 Z', 'accent') + d.R(300, 770, 400, 72, 25, 'accent') +
    d.face(500, 430, 170));

  A.add('mountain', 'Mountain', { main: PU, dark: '#9575cd', light: W, pink: P }, d =>
    cloud(d, 200, 225, 230, 'light') +
    d.P('M500 860 L720 400 Q740 365 760 400 L960 860 Z', 'dark') +
    d.P('M120 860 L460 230 Q500 170 540 230 L880 860 Z') +
    d.P('M405 330 L460 230 Q500 170 540 230 L595 330 L555 300 L520 345 L480 300 L445 345 Z', 'light') +
    d.face(500, 600, 200) + d.grass(870));

  A.add('rock', 'Rock', { main: GR, dark: '#b0bec5', pink: P }, d =>
    d.P('M80 810 Q85 725 160 720 Q235 725 240 810 Z', 'dark') +
    d.P('M200 810 Q160 560 330 460 Q500 360 680 450 Q850 540 820 810 Z') +
    d.Lt('M845 810 L835 745 M865 810 L875 735 M885 810 L912 755') +
    d.face(500, 640, 200));

  A.add('tree-stump', 'Tree Stump', { main: BR, light: '#f3d9b8', pink: P }, d =>
    d.P('M260 420 L260 760 Q200 800 170 845 L830 845 Q800 800 740 760 L740 420 Z') +
    d.E(500, 420, 240, 80, 'light') + d.E(500, 420, 150, 46, 'none') + d.E(500, 420, 70, 20, 'none') +
    d.Lt('M320 490 L320 640') + d.Lt('M680 510 L680 690') +
    d.face(500, 600, 190));

  A.add('pond', 'Pond', { main: B, light: G, accent: P, accent2: Y, dark: BR, pink: P }, d =>
    d.L('M800 520 L800 300') + d.L('M860 540 L860 340') +
    d.R(780, 230, 40, 110, 20, 'dark') + d.R(840, 270, 40, 110, 20, 'dark') +
    d.E(500, 650, 410, 200) +
    d.P('M360 610 L510 610 A150 75 0 1 1 482.9 567 Z', 'light') +
    flower(d, 345, 600, 30, 'accent', 'accent2') +
    d.Lt('M175 760 Q225 740 275 760') +
    d.face(640, 690, 170));

  A.add('sprout', 'Sprout', { main: G, dark: BR, pink: P }, d =>
    d.L('M500 760 Q488 590 500 430') +
    d.E(395, 410, 112, 52, 'main', -25) + d.E(605, 390, 112, 52, 'main', 25) +
    d.P('M150 880 Q500 555 850 880 Z', 'dark') + d.face(500, 790, 140));

  A.add('dandelion', 'Dandelion', { main: W, accent: G, light: Y, pink: P }, d => {
    let s = d.L('M500 455 Q470 700 520 905') +
      d.E(400, 830, 115, 40, 'accent', -35) + d.E(625, 830, 115, 40, 'accent', 35);
    for (let i = 0; i < 12; i++) {
      if (i === 3) continue; // the stem takes the place of the bottom seed
      const a = i / 12 * 2 * Math.PI, c = Math.cos(a), n = Math.sin(a);
      s += d.L(`M${f(500 + 95 * c)} ${f(360 + 95 * n)} L${f(500 + 255 * c)} ${f(360 + 255 * n)}`) + d.C(500 + 280 * c, 360 + 280 * n, 24);
    }
    return s + d.Lt('M780 220 L815 185') + d.C(828, 172, 16) + d.Lt('M850 330 L885 300') + d.C(898, 288, 16) +
      d.C(500, 360, 100, 'light') + d.face(500, 355, 150);
  });
})();
