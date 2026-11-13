// "My First Farmyard": 30 friendly farm animals, buildings and farm things, for ages 2-5.
// Drawn from scratch: no brands, logos, tractor makes or characters. Farm subjects already
// drawn in other books of the series (cow, pig, sheep, horse, pony, chicken, hen, rooster,
// chick, duck, goose, turkey, rabbit, beehive, watering can, mailbox, pumpkin, corn, carrot,
// sunflower, overalls, sun hat, cowboy boot, tree, pond) are left out. The animals here are
// drawn side-on with the whole body, unlike the head-only animals in "My First Animals".
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', DGR = '#90a4ae', W = '#ffffff', CREAM = '#fff3d6', HAY = '#f6d365', BARN = '#e8524a', SKIN = '#ffd7b5', DEN = '#7fa7e0', PINKPIG = '#ffc2d1';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (ropes, handles, straps): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const star = (d, cx, cy, r, k = 'accent') => d.poly([...Array(10)].map((_, i) => {
    const a = (-90 + i * 36) * Math.PI / 180, rr = i % 2 ? r * 0.45 : r; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  }), k);
  // four legs with hooves for the side-on animals
  const legs = (d, xs, top, bot, w = 58, hoof = 'dark') => xs.map(x =>
    d.R(x, top, w, bot - top, 24) + d.R(x - 5, bot - 46, w + 10, 52, 18, hoof)).join('');
  // eyes, rosy cheeks and a smile for a face with a muzzle below it
  const eyesCheeks = (d, x, y, gap, r = 22) => d.eye(x - gap, y, r) + d.eye(x + gap, y, r) +
    d.C(x - gap - 20, y + 52, 20, 'pink') + d.C(x + gap + 20, y + 52, 20, 'pink');

  // ---------------- farm animals ----------------
  A.add('goat', 'Goat', { main: W, dark: DGR, light: CREAM, pink: P }, d =>
    legs(d, [300, 390, 545, 630], 600, 880) +
    d.P('M262 480 Q205 410 240 372 Q275 420 300 470 Z') +
    d.E(460, 560, 235, 150) +
    d.P('M662 470 L702 615 L742 470 Z', 'light') +
    d.P('M640 290 Q596 180 646 128 Q652 200 690 272 Z', 'dark') + d.P('M760 290 Q804 180 754 128 Q748 200 710 272 Z', 'dark') +
    d.E(572, 365, 72, 30, 'main', -25) + d.E(828, 365, 72, 30, 'main', 25) +
    d.E(700, 395, 122, 132) +
    d.face(700, 405, 170));

  A.add('donkey', 'Donkey', { main: GR, dark: DGR, light: W, pink: P }, d =>
    legs(d, [300, 390, 545, 630], 610, 880) +
    d.L('M245 520 Q200 600 215 680') + d.E(214, 705, 24, 42, 'dark') +
    d.E(460, 570, 235, 148) +
    d.E(645, 215, 34, 108, 'main', -14) + d.E(755, 215, 34, 108, 'main', 14) +
    d.E(645, 222, 15, 70, 'light', -14) + d.E(755, 222, 15, 70, 'light', 14) +
    d.C(668, 290, 34, 'dark') + d.C(700, 278, 36, 'dark') + d.C(732, 290, 34, 'dark') +
    d.E(700, 410, 118, 140) +
    d.E(700, 492, 98, 62, 'light') + d.E(668, 482, 11, 16, 'ink') + d.E(732, 482, 11, 16, 'ink') +
    d.smile(700, 512, 36, 20) +
    eyesCheeks(d, 700, 385, 48, 21));

  A.add('llama', 'Llama', { main: CREAM, light: W, accent: R, accent2: Y, pink: P }, d =>
    legs(d, [275, 355, 495, 565], 640, 880, 52, 'main') +
    d.C(222, 580, 42) +
    d.R(590, 250, 118, 400, 56) +
    d.E(420, 620, 215, 128) +
    d.E(605, 140, 26, 72, 'main', -12) + d.E(695, 140, 26, 72, 'main', 12) +
    d.E(650, 270, 100, 112) +
    d.C(612, 172, 30, 'light') + d.C(650, 160, 32, 'light') + d.C(688, 172, 30, 'light') +
    d.R(320, 505, 210, 88, 26, 'accent') + d.R(320, 593, 210, 26, 10, 'accent2') +
    d.face(650, 282, 140));

  A.add('lamb', 'Lamb', { main: W, dark: DGR, light: W, pink: P }, d =>
    legs(d, [330, 410, 520, 600], 650, 880, 52) +
    d.scallop(450, 520, 160, 12, 72, 'light') +
    d.E(590, 440, 60, 26, 'main', -25) + d.E(820, 440, 60, 26, 'main', 25) +
    d.E(705, 455, 98, 112) +
    d.C(668, 352, 34, 'light') + d.C(705, 340, 38, 'light') + d.C(742, 352, 34, 'light') +
    d.face(705, 470, 140));

  A.add('calf', 'Calf', { main: W, dark: '#6d6d6d', light: '#f3e2c7', pink: P }, d =>
    legs(d, [295, 385, 540, 625], 600, 880) +
    d.L('M240 540 Q195 620 210 690') + d.E(210, 712, 20, 36, 'dark') +
    d.E(455, 565, 228, 145) +
    d.E(375, 520, 62, 46, 'dark', -10) + d.E(540, 625, 52, 38, 'dark', 12) + d.E(300, 615, 34, 28, 'dark') +
    d.E(585, 380, 70, 30, 'main', -20) + d.E(815, 380, 70, 30, 'main', 20) +
    d.E(700, 410, 118, 115) +
    d.E(700, 488, 98, 60, 'pink') + d.E(668, 482, 12, 17, 'ink') + d.E(732, 482, 12, 17, 'ink') +
    d.smile(700, 510, 36, 18) +
    eyesCheeks(d, 700, 392, 48, 21));

  A.add('piglet', 'Piglet', { main: PINKPIG, pink: '#ff8fab', dark: DB, light: W }, d =>
    d.R(345, 650, 54, 180, 24) + d.R(420, 665, 54, 165, 24) + d.R(540, 665, 54, 165, 24) + d.R(610, 650, 54, 180, 24) +
    d.E(480, 845, 380, 58, 'dark') +
    d.C(232, 836, 20, 'dark') + d.C(790, 812, 15, 'dark') + d.C(830, 850, 11, 'dark') +
    d.L('M268 530 Q222 526 220 490 Q220 458 250 464 Q274 472 256 498') +
    d.E(470, 570, 205, 140) +
    d.P('M604 372 Q578 300 596 270 Q646 292 668 334 Z') + d.P('M796 372 Q822 300 804 270 Q754 292 732 334 Z') +
    d.C(700, 455, 125) +
    d.E(700, 505, 56, 40, 'pink') + d.E(682, 505, 10, 15, 'ink') + d.E(718, 505, 10, 15, 'ink') +
    d.smile(700, 552, 34, 16) +
    eyesCheeks(d, 700, 425, 54, 21));

  // ---------------- buildings and big things ----------------
  A.add('barn', 'Barn', { main: BARN, light: W, accent: '#b23a32', pink: P }, d =>
    d.poly([[200, 500], [280, 330], [500, 230], [720, 330], [800, 500], [800, 880], [200, 880]]) +
    d.poly([[178, 512], [262, 318], [500, 208], [738, 318], [822, 512], [782, 512], [708, 352], [500, 256], [292, 352], [218, 512]], 'light') +
    d.R(455, 318, 90, 82, 10, 'light') + d.L('M500 318 L500 400 M455 359 L545 359') +
    d.R(370, 612, 260, 268, 6, 'light') + d.L('M370 612 L630 880 M630 612 L370 880') +
    d.face(500, 500, 165));

  A.add('silo', 'Silo', { main: GR, accent: BARN, dark: DGR, pink: P }, d =>
    d.R(360, 300, 280, 570, 0) +
    d.P('M352 312 Q352 140 500 140 Q648 140 648 312 Z', 'accent') +
    d.L('M360 440 L640 440 M360 610 L640 610 M360 750 L640 750') +
    d.R(338, 852, 324, 36, 12, 'dark') +
    d.face(500, 515, 170));

  A.add('windmill', 'Windmill', { main: CREAM, accent: R, light: W, dark: BR, pink: P }, d => {
    const blade = rot => group(d.R(472, 96, 56, 250, 8, 'light') + d.Lt('M500 112 L500 330 M478 170 L522 170 M478 250 L522 250'), rot, 500, 360);
    return d.poly([[390, 880], [610, 880], [580, 380], [420, 380]]) +
      d.P('M460 880 L460 815 Q460 775 500 775 Q540 775 540 815 L540 880 Z', 'dark') +
      d.P('M404 392 Q404 288 500 288 Q596 288 596 392 Z', 'accent') +
      blade(45) + blade(135) + blade(225) + blade(315) +
      d.C(500, 360, 34, 'accent') +
      d.face(500, 620, 160);
  });

  A.add('chicken-coop', 'Chicken Coop', { main: Y, accent: R, dark: BR, light: CREAM, pink: P }, d =>
    d.R(300, 690, 40, 190, 10, 'dark') + d.R(660, 690, 40, 190, 10, 'dark') +
    d.R(270, 380, 460, 330, 20) +
    d.poly([[228, 405], [500, 200], [772, 405]], 'accent') +
    d.P('M435 710 L435 642 Q435 578 500 578 Q565 578 565 642 L565 710 Z', 'dark') +
    d.poly([[445, 706], [555, 706], [700, 880], [602, 880]], 'light') +
    d.Lt('M498 760 L578 760 M540 806 L618 806 M578 852 L656 852') +
    d.face(500, 470, 150));

  A.add('farm-stand', 'Farm Stand', { main: BR, light: CREAM, accent: R, accent2: O, dark: DG, pink: P }, d => {
    let sc = '';
    for (let i = 0; i < 7; i++) sc += d.C(260 + i * 80, 346, 40, i % 2 ? 'light' : 'accent');
    return d.R(258, 300, 40, 290, 12) + d.R(702, 300, 40, 290, 12) +
      sc + d.R(220, 250, 560, 96, 20, 'accent') +
      d.C(330, 520, 42, 'accent') + d.C(400, 525, 42, 'accent') + d.C(365, 470, 42, 'accent') +
      d.E(640, 505, 82, 62, 'accent2') + d.L('M640 445 Q636 420 650 405') + d.E(600, 452, 34, 16, 'dark', -20) +
      d.R(240, 560, 520, 300, 16, 'light') +
      d.face(500, 690, 175);
  });

  A.add('scarecrow', 'Scarecrow', { main: B, accent: R, accent2: HAY, dark: BR, skin: CREAM, light: HAY, pink: P }, d =>
    d.R(470, 250, 60, 630, 10, 'dark') +
    d.R(200, 445, 600, 46, 20, 'dark') +
    d.P('M222 432 L168 404 L194 462 L160 500 L222 504 Z', 'light') + d.P('M778 432 L832 404 L806 462 L840 500 L778 504 Z', 'light') +
    d.R(215, 425, 180, 82, 32) + d.R(605, 425, 180, 82, 32) +
    d.P('M396 712 L372 790 L420 740 L452 800 L476 726 L524 726 L548 800 L580 740 L628 790 L604 712 Z', 'light') +
    d.P('M380 425 L620 425 L640 725 L360 725 Z') +
    d.R(420, 575, 72, 72, 8, 'accent') + d.Lt('M432 588 L480 634 M480 588 L432 634') +
    d.C(500, 335, 112, 'skin') +
    d.E(500, 238, 175, 38, 'accent2') +
    d.P('M408 244 Q418 128 500 128 Q582 128 592 244 Z', 'accent2') + d.R(412, 202, 176, 34, 8, 'accent') +
    d.face(500, 350, 150));

  // toy-style primary colours on purpose: no maker's colour scheme (e.g. green with yellow wheels)
  A.add('tractor', 'Tractor', { main: '#5c7cfa', accent: Y, accent2: R, dark: '#555', tire: '#555', light: '#d6f0ff', pink: P }, d =>
    d.R(650, 360, 34, 140, 10, 'dark') +
    d.R(230, 280, 250, 300, 20) + d.R(270, 320, 170, 150, 14, 'light') + d.R(206, 258, 298, 42, 14, 'accent2') +
    d.R(440, 482, 352, 190, 40) +
    d.C(720, 772, 110, 'tire') + d.C(720, 772, 42, 'accent') +
    d.C(330, 690, 192, 'tire') + d.C(330, 690, 76, 'accent') + d.C(330, 690, 22, 'dark') +
    d.face(615, 572, 160));

  A.add('hay-wagon', 'Hay Wagon', { main: R, light: HAY, accent: Y, dark: BR, pink: P }, d =>
    d.L('M818 600 L918 646') + d.C(930, 652, 20, 'accent') +
    d.P('M212 520 Q226 342 392 330 Q470 240 600 300 Q762 300 788 520 Z', 'light') +
    d.Lt('M268 476 L290 436 M732 476 L710 436 M330 380 L346 346 M676 380 L660 346 M560 296 L572 270') +
    d.R(180, 500, 640, 150, 16) +
    d.C(300, 705, 95, 'dark') + d.C(700, 705, 95, 'dark') +
    d.Lt('M300 615 L300 795 M210 705 L390 705 M700 615 L700 795 M610 705 L790 705') +
    d.C(300, 705, 30, 'accent') + d.C(700, 705, 30, 'accent') +
    d.face(500, 420, 150));

  A.add('wheelbarrow', 'Wheelbarrow', { main: R, accent: Y, dark: '#555', light: GR, pink: P }, d =>
    tube(d, ['M600 548 L905 455'], 'dark', 58) +
    d.R(600, 590, 40, 260, 12, 'dark') + d.R(580, 836, 80, 40, 14, 'dark') +
    d.C(268, 735, 110, 'dark') + d.C(268, 735, 34, 'accent') +
    d.poly([[180, 400], [730, 400], [650, 640], [290, 640]]) +
    d.R(158, 378, 594, 48, 22, 'accent') +
    d.face(455, 515, 165));

  A.add('water-trough', 'Water Trough', { main: GR, light: B, accent: R, dark: DGR, pink: P }, d =>
    d.R(250, 740, 52, 140, 12, 'dark') + d.R(698, 740, 52, 140, 12, 'dark') +
    tube(d, ['M162 262 L80 190'], 'accent', 50) +
    d.R(128, 240, 84, 420, 28, 'accent') + d.R(190, 280, 112, 46, 18, 'accent') +
    d.P('M282 338 Q304 372 282 388 Q260 372 282 338 Z', 'light') + d.P('M282 408 Q304 442 282 458 Q260 442 282 408 Z', 'light') +
    d.P('M180 480 L820 480 L760 760 L240 760 Z') +
    d.E(500, 482, 322, 40, 'light') + d.Lt('M380 482 Q420 470 460 482 M560 486 Q600 474 640 486') +
    d.face(505, 610, 170));

  // ---------------- farm things ----------------
  A.add('hay-bale', 'Hay Bale', { main: HAY, light: '#fbe7a1', dark: '#e0b441', accent: R, pink: P }, d =>
    d.poly([[192, 420], [302, 330], [832, 330], [712, 420]], 'light') +
    d.poly([[712, 420], [832, 330], [832, 712], [712, 800]], 'dark') +
    d.R(180, 420, 532, 380, 30) +
    d.L('M330 420 L330 800 M560 420 L560 800 M330 420 L442 330 M560 420 L672 330') +
    d.Lt('M212 460 L240 470 M212 760 L240 750 M680 460 L652 470 M680 760 L652 750 M760 420 L780 440 M790 640 L808 660') +
    d.face(445, 612, 160));

  A.add('wheat', 'Wheat', { main: HAY, accent: R, dark: '#e0b441', pink: P }, d => {
    const head = (x, y, rot) => group(d.E(x, y, 38, 92) +
      d.Lt(`M${x - 22} ${y - 40} L${x} ${y - 22} L${x + 22} ${y - 40} M${x - 22} ${y} L${x} ${y + 18} L${x + 22} ${y}`), rot, x, y);
    return d.L('M450 690 L400 880 M482 690 L470 880 M518 690 L530 880 M550 690 L600 880') +
      d.L('M452 612 L330 372 M476 612 L420 342 M500 612 L500 332 M524 612 L580 342 M548 612 L670 372') +
      head(318, 300, -26) + head(415, 262, -10) + head(500, 244, 0) + head(585, 262, 10) + head(682, 300, 26) +
      d.R(400, 600, 200, 110, 40, 'accent') +
      d.face(500, 642, 120);
  });

  A.add('milk-can', 'Milk Can', { main: GR, accent: B, light: W, pink: P }, d =>
    d.C(318, 482, 40, 'none') + d.C(682, 482, 40, 'none') +
    d.R(320, 500, 360, 380, 40) +
    d.P('M330 530 Q340 422 420 402 L580 402 Q660 422 670 530 Z') +
    d.R(420, 300, 160, 112, 10) +
    d.E(500, 296, 106, 32, 'accent') + d.C(500, 262, 24, 'accent') +
    d.R(310, 600, 380, 40, 10, 'accent') + d.R(310, 822, 380, 40, 10, 'accent') +
    d.face(500, 718, 160));

  A.add('egg-basket', 'Egg Basket', { main: BR, accent: '#a86f42', light: W, accent2: CREAM, pink: P }, d =>
    tube(d, ['M292 522 Q292 222 500 222 Q708 222 708 522'], 'main', 60) +
    d.E(378, 512, 70, 92, 'light', -12) + d.E(500, 482, 72, 96, 'accent2') + d.E(622, 512, 70, 92, 'light', 12) +
    d.P('M232 530 L768 530 L702 858 Q500 892 298 858 Z') +
    d.R(208, 500, 584, 62, 30, 'accent') +
    d.Lt('M270 600 L300 620 M262 660 L294 680 M730 600 L700 620 M738 660 L706 680') +
    d.face(500, 700, 170));

  A.add('cowbell', 'Cowbell', { main: Y, dark: BR, accent: O, light: CREAM, pink: P }, d =>
    d.P('M160 250 Q500 352 840 250 L840 322 Q500 424 160 322 Z', 'dark') +
    d.R(464, 330, 72, 72, 20, 'accent') +
    d.P('M392 372 L608 372 Q632 372 640 402 L702 788 Q500 830 298 788 L360 402 Q368 372 392 372 Z') +
    d.E(500, 792, 202, 40, 'light') +
    d.C(500, 832, 30, 'accent') +
    d.face(500, 585, 180));

  A.add('horseshoe', 'Horseshoe', { main: GR, accent: Y, pink: P }, d => {
    let holes = '';
    for (const y of [300, 400, 500]) holes += d.R(325, y, 30, 46, 12, 'ink') + d.R(645, y, 30, 46, 12, 'ink');
    return d.P('M260 262 L260 520 Q260 822 500 822 Q740 822 740 520 L740 262 Q740 222 700 222 L620 222 Q580 222 580 262 L580 520 Q580 662 500 662 Q420 662 420 520 L420 262 Q420 222 380 222 L300 222 Q260 222 260 262 Z') +
      holes +
      star(d, 160, 160, 44, 'accent') + star(d, 840, 160, 44, 'accent') + star(d, 840, 820, 32, 'accent') + star(d, 160, 820, 32, 'accent') +
      d.face(500, 735, 118);
  });

  A.add('apple-crate', 'Apple Crate', { main: BR, dark: DB, accent: R, accent2: DG, pink: P }, d => {
    const apple = (x, y, r, leaf) => (leaf ? d.L(`M${x} ${y - r + 8} Q${x + 4} ${y - r - 24} ${x + 16} ${y - r - 34}`) +
      d.E(x + 34, y - r - 18, 26, 13, 'accent2', -25) : '') + d.C(x, y, r, 'accent');
    return apple(360, 455, 58, 1) + apple(480, 440, 60, 1) + apple(600, 455, 58, 1) +
      apple(290, 525, 62) + apple(420, 510, 64) + apple(550, 512, 64) + apple(680, 525, 62) +
      d.R(220, 540, 560, 320, 16) +
      d.L('M220 625 L780 625 M220 780 L780 780') +
      d.R(262, 564, 82, 30, 15, 'dark') + d.R(656, 564, 82, 30, 15, 'dark') +
      d.Lt('M300 808 L300 836 M700 808 L700 836') +
      d.face(500, 690, 140);
  });

  A.add('lantern', 'Lantern', { main: R, light: '#fff8d6', accent: O, accent2: Y, pink: P }, d =>
    d.L('M410 430 Q410 250 500 250 Q590 250 590 430') +
    d.E(500, 590, 140, 182, 'light') +
    d.P('M500 448 Q556 510 500 570 Q444 510 500 448 Z', 'accent') +
    d.L('M412 450 Q376 590 412 740 M588 450 Q624 590 588 740') +
    d.P('M392 470 L608 470 L570 398 L430 398 Z') + d.C(500, 392, 26) +
    d.R(370, 740, 260, 110, 36) +
    d.Lt('M300 520 L262 506 M700 520 L738 506 M300 640 L262 650 M700 640 L738 650') +
    d.face(500, 660, 140));

  A.add('weather-vane', 'Weather Vane', { main: R, accent: Y, accent2: O, dark: '#555', light: W, pink: P }, d =>
    d.R(488, 280, 24, 300, 10, 'dark') +
    d.R(330, 462, 340, 20, 8, 'dark') + d.C(322, 472, 24, 'accent') + d.C(678, 472, 24, 'accent') +
    d.R(220, 318, 560, 24, 10, 'dark') +
    d.poly([[776, 276], [886, 330], [776, 384]], 'accent') +
    d.poly([[118, 262], [262, 300], [262, 360], [118, 398], [168, 330]], 'accent') +
    d.Lt('M462 292 L452 318 M512 292 L522 318') +
    d.poly([[400, 230], [312, 132], [352, 236], [306, 210], [384, 270]], 'accent2') +
    d.E(470, 236, 102, 60, 'light') +
    d.C(574, 176, 44, 'light') +
    d.C(562, 126, 16, 'accent2') + d.C(586, 122, 16, 'accent2') + d.C(606, 136, 14, 'accent2') +
    d.poly([[614, 168], [652, 182], [614, 196]], 'accent') + d.dot(584, 168, 9) +
    d.R(380, 650, 240, 210, 16) +
    d.poly([[348, 662], [500, 552], [652, 662]], 'accent') +
    d.face(500, 752, 150));

  A.add('farm-gate', 'Farm Gate', { main: BR, dark: DB, accent: Y, light: CREAM, pink: P }, d =>
    d.R(170, 300, 70, 580, 14, 'dark') + d.R(760, 300, 70, 580, 14, 'dark') +
    d.poly([[162, 304], [205, 252], [248, 304]], 'dark') + d.poly([[752, 304], [795, 252], [838, 304]], 'dark') +
    d.poly([[296, 786], [346, 786], [704, 620], [654, 620]], 'light') +
    d.R(240, 360, 520, 62, 12) + d.R(240, 480, 520, 140, 16) + d.R(240, 780, 520, 62, 12) +
    d.R(240, 340, 52, 520, 10) + d.R(708, 340, 52, 520, 10) +
    d.R(226, 378, 40, 26, 8, 'accent') + d.R(226, 800, 40, 26, 8, 'accent') +
    d.face(500, 538, 130));

  A.add('seed-packet', 'Seed Packet', { main: G, light: W, accent: Y, accent2: BR, dark: DG, pink: P }, d =>
    d.poly([[300, 210], [340, 180], [380, 210], [420, 180], [460, 210], [500, 180], [540, 210], [580, 180], [620, 210], [660, 180], [700, 210], [700, 810], [300, 810]]) +
    d.R(345, 250, 310, 270, 22, 'light') +
    d.L('M500 505 L500 400') + d.E(462, 450, 34, 16, 'dark', -30) + d.E(538, 450, 34, 16, 'dark', 30) +
    d.scallop(500, 352, 34, 10, 24, 'accent') + d.C(500, 352, 30, 'accent2') +
    d.face(500, 640, 165) +
    d.E(390, 868, 16, 24, 'accent2', -30) + d.E(470, 880, 16, 24, 'accent2', 20) + d.E(560, 872, 16, 24, 'accent2', -10) + d.E(640, 884, 16, 24, 'accent2', 30));

  A.add('feed-sack', 'Feed Sack', { main: '#e8d3a8', accent: R, accent2: HAY, light: W, pink: P }, d =>
    d.P('M362 382 Q332 262 402 232 L598 232 Q668 262 638 382 Z') +
    d.Lt('M440 250 L452 360 M500 244 L500 360 M560 250 L548 360') +
    d.P('M300 862 Q250 600 332 382 L668 382 Q750 600 700 862 Q500 902 300 862 Z') +
    d.R(348, 352, 304, 52, 22, 'accent') +
    d.E(720, 868, 22, 14, 'accent2') + d.E(770, 852, 22, 14, 'accent2', 20) + d.E(812, 874, 22, 14, 'accent2', -15) + d.E(760, 888, 22, 14, 'accent2') +
    d.face(500, 622, 190));

  A.add('farmer', 'Farmer', { main: DEN, accent: R, accent2: HAY, skin: SKIN, dark: DB, light: Y, pink: P }, d =>
    d.R(420, 780, 72, 90, 22) + d.R(508, 780, 72, 90, 22) +
    d.R(398, 846, 104, 52, 24, 'dark') + d.R(498, 846, 104, 52, 24, 'dark') +
    d.E(368, 625, 38, 98, 'accent', 16) + d.E(632, 625, 38, 98, 'accent', -16) +
    d.C(346, 712, 34, 'skin') + d.C(654, 712, 34, 'skin') +
    d.R(392, 492, 216, 230, 60, 'accent') +
    d.R(400, 660, 200, 160, 30) + d.R(432, 560, 136, 120, 14) +
    d.L('M440 562 L420 500 M560 562 L580 500') + d.C(448, 584, 12, 'light') + d.C(552, 584, 12, 'light') +
    d.R(470, 610, 60, 40, 8, 'light') +
    d.C(500, 368, 128, 'skin') +
    d.E(500, 268, 192, 40, 'accent2') +
    d.P('M398 274 Q408 146 500 146 Q592 146 602 274 Z', 'accent2') + d.R(403, 232, 194, 34, 8, 'accent') +
    d.face(500, 388, 168));

  A.add('tire-swing', 'Tire Swing', { main: '#78909c', dark: BR, accent: G, light: W, rope: HAY, pink: P }, d =>
    d.R(110, 190, 120, 690, 30, 'dark') +
    d.P('M216 220 L880 188 Q912 200 900 232 L216 290 Z', 'dark') +
    d.C(150, 180, 88, 'accent') + d.C(270, 148, 90, 'accent') + d.C(382, 182, 74, 'accent') +
    tube(d, ['M620 256 L620 470'], 'rope', 48) +
    d.E(620, 640, 212, 192) + d.E(620, 598, 92, 70, 'light') +
    d.grass(890) +
    d.face(620, 752, 128));
})();
