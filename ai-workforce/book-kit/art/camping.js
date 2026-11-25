// "My First Camping": 30 friendly camping things and woodland animals, for ages 2-5.
// Drawn from scratch: no brands, logos, gear makers or characters. Camping subjects already
// drawn in other books of the series (lantern, backpack, pinecone, acorn, mountain, tree, pine tree,
// tree stump, owl, fox, bear, frog, snail, firefly, bug jar, butterfly net, hot dog, pot, cup,
// sleeping owl, stars, moon, rain boots) are left out.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', DGR = '#90a4ae', W = '#ffffff', CREAM = '#fff3d6', TAN = '#e8b97a', CHOC = '#7a4a2e', PURPLE = '#b39ddb', NAVY = '#5c6bc0', TEAL = '#4dd0c4';

  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (sticks, ropes, handles): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  // four legs with hooves for side-on animals
  const legs = (d, xs, top, bot, w = 46, hoof = 'dark') => xs.map(x =>
    d.R(x, top, w, bot - top, 20) + d.R(x - 5, bot - 40, w + 10, 46, 16, hoof)).join('');

  // ---------------- at the campsite ----------------
  A.add('tent', 'Tent', { main: O, dark: BR, light: CREAM, accent: Y, pink: P }, d =>
    d.R(488, 150, 24, 90, 10, 'dark') +
    d.Lt('M200 850 L110 890 M800 850 L890 890') +
    d.poly([[150, 850], [500, 220], [850, 850]]) +
    d.poly([[400, 850], [500, 600], [600, 850]], 'light') +
    d.L('M500 600 L500 850') +
    d.grass(870) +
    d.face(500, 470, 150));

  A.add('campfire', 'Campfire', { main: O, accent: Y, dark: BR, light: TAN, rock: GR, pink: P }, d => {
    let rocks = '';
    for (let i = 0; i < 7; i++) rocks += d.E(230 + i * 90, 860, 52, 36, 'rock');
    return rocks +
      d.P('M500 200 Q640 360 650 520 Q665 730 500 770 Q335 730 350 520 Q360 360 500 200 Z') +
      d.P('M330 470 Q300 400 330 350 Q360 420 380 450 Z') + d.P('M670 470 Q700 400 670 350 Q640 420 620 450 Z') +
      d.P('M500 430 Q590 540 590 630 Q588 728 500 742 Q412 728 410 630 Q410 540 500 430 Z', 'accent') +
      group(d.R(240, 745, 520, 76, 38, 'dark'), -10, 500, 783) + group(d.R(240, 745, 520, 76, 38, 'dark'), 10, 500, 783) +
      d.face(500, 625, 118);
  });

  A.add('marshmallow', 'Marshmallow', { main: W, dark: BR, light: CREAM, accent: TAN, pink: P }, d =>
    tube(d, ['M170 860 L640 360'], 'dark', 46) +
    group(d.R(520, 180, 300, 280, 90), -18, 670, 320) +
    d.face(670, 335, 150));

  A.add('smores', "S'mores", { main: TAN, dark: CHOC, light: W, pink: P }, d =>
    d.R(240, 640, 520, 120, 26) +
    d.R(280, 600, 440, 66, 14, 'dark') +
    d.P('M262 520 Q250 430 360 440 Q500 410 640 440 Q750 430 738 520 Q750 610 640 600 Q500 625 360 600 Q250 610 262 520 Z', 'light') +
    d.R(240, 330, 520, 120, 26) +
    d.dot(300, 370, 11) + d.dot(300, 410, 11) + d.dot(700, 370, 11) + d.dot(700, 410, 11) +
    d.dot(500, 370, 11) + d.dot(420, 390, 11) + d.dot(580, 390, 11) +
    d.dot(300, 700, 11) + d.dot(700, 700, 11) + d.dot(500, 720, 11) +
    d.face(500, 515, 140));

  A.add('sleeping-bag', 'Sleeping Bag', { main: B, light: CREAM, dark: NAVY, pink: P }, d =>
    d.R(140, 330, 740, 360, 170) +
    d.E(270, 510, 92, 132, 'light') +
    d.L('M380 345 L380 675') +
    d.Lt('M790 360 L790 660') +
    d.R(380, 488, 36, 44, 8, 'dark') +
    d.face(600, 500, 180));

  A.add('flashlight', 'Flashlight', { main: R, accent: GR, accent2: Y, dark: DGR, light: W, pink: P }, d =>
    d.poly([[790, 380], [960, 270], [960, 740], [790, 630]], 'accent2') +
    d.R(300, 395, 80, 50, 14, 'dark') +
    d.R(150, 425, 450, 160, 50) +
    d.poly([[590, 410], [770, 340], [770, 670], [590, 600]], 'accent') +
    d.E(775, 505, 42, 165, 'light') +
    d.face(380, 515, 150));

  A.add('compass', 'Compass', { main: R, light: W, accent: R, dark: DGR, pink: P }, d =>
    d.C(500, 150, 46) + d.C(500, 150, 20, 'light') +
    d.C(500, 500, 330) + d.C(500, 500, 265, 'light') +
    d.L('M500 240 L500 270 M500 730 L500 760 M240 500 L270 500 M730 500 L760 500') +
    d.poly([[500, 280], [545, 430], [455, 430]], 'accent') +
    d.face(500, 565, 170));

  A.add('map', 'Map', { main: CREAM, light: '#fff8e6', accent: G, accent2: R, water: B, dark: BR, pink: P }, d =>
    d.poly([[170, 260], [390, 320], [390, 800], [170, 740]]) +
    d.poly([[610, 260], [830, 320], [830, 800], [610, 740]]) +
    d.poly([[390, 320], [610, 260], [610, 740], [390, 800]], 'light') +
    d.poly([[230, 470], [280, 370], [330, 470]], 'accent') + d.R(270, 470, 20, 34, 4, 'dark') +
    d.E(270, 640, 60, 40, 'water') +
    d.Lt('M680 420 L760 500 M760 420 L680 500') +
    d.Lt('M690 610 l20 -18 M730 650 l18 -20 M770 690 l18 -18') +
    d.face(500, 540, 150));

  A.add('binoculars', 'Binoculars', { main: DG, dark: '#2e7d4f', light: B, accent: GR, pink: P }, d =>
    tube(d, ['M270 330 Q500 120 730 330'], 'accent', 44) +
    d.R(250, 290, 160, 110, 30, 'dark') + d.R(590, 290, 160, 110, 30, 'dark') +
    d.R(210, 380, 240, 420, 80) + d.R(550, 380, 240, 420, 80) +
    d.E(330, 760, 92, 42, 'light') + d.E(670, 760, 92, 42, 'light') +
    d.R(405, 430, 190, 180, 44, 'accent') +
    d.face(500, 505, 128));

  A.add('canoe', 'Canoe', { main: R, light: TAN, water: B, pink: P }, d =>
    d.P('M110 450 Q190 560 500 575 Q810 560 890 450 Q860 720 500 738 Q140 720 110 450 Z') +
    d.P('M150 505 Q500 640 850 505 Q500 600 150 505 Z', 'light') +
    d.water(800) + d.water(860) +
    d.face(500, 660, 140));

  A.add('paddle', 'Paddle', { main: TAN, dark: BR, pink: P }, d =>
    d.R(470, 150, 60, 470, 30, 'dark') +
    d.R(410, 110, 180, 60, 30, 'dark') +
    d.P('M500 560 Q650 600 650 760 Q650 905 500 925 Q350 905 350 760 Q350 600 500 560 Z') +
    d.face(500, 750, 170));

  A.add('life-jacket', 'Life Jacket', { main: O, dark: DGR, light: GR, pink: P }, d =>
    d.P('M300 210 L420 210 Q500 370 580 210 L700 210 Q770 300 785 430 L785 820 Q640 860 500 840 Q360 860 215 820 L215 430 Q230 300 300 210 Z') +
    d.E(232, 400, 34, 90, 'light') + d.E(768, 400, 34, 90, 'light') +
    d.R(215, 640, 570, 46, 8, 'dark') + d.R(215, 735, 570, 46, 8, 'dark') +
    d.R(455, 628, 90, 70, 12, 'light') + d.R(455, 723, 90, 70, 12, 'light') +
    d.face(500, 490, 170));

  A.add('fishing-rod', 'Fishing Rod', { main: W, dark: BR, accent: R, accent2: GR, pink: P }, d =>
    tube(d, ['M180 880 L740 170'], 'dark', 40) +
    d.C(300, 735, 62, 'accent2') + d.C(300, 735, 20, 'dark') + d.L('M300 735 L250 690') +
    d.Lt('M740 170 L760 500') +
    d.R(745, 482, 30, 48, 8, 'accent2') +
    d.C(760, 640, 125) +
    d.P('M635 625 A125 125 0 0 1 885 625 Q760 600 635 625 Z', 'accent') +
    d.face(760, 690, 118));

  A.add('tackle-box', 'Tackle Box', { main: G, dark: DG, accent: Y, light: GR, pink: P }, d =>
    tube(d, ['M410 430 L410 320 L590 320 L590 430'], 'dark', 50) +
    d.R(210, 420, 580, 400, 30) +
    d.L('M210 545 L790 545') +
    d.R(465, 520, 70, 54, 10, 'accent') +
    d.P('M708 690 L752 652 L752 728 Z', 'accent') + d.E(650, 690, 62, 36, 'accent') + d.dot(625, 682, 8) +
    d.face(470, 690, 160));

  A.add('hiking-boot', 'Hiking Boot', { main: BR, light: CREAM, dark: DB, accent: R, pink: P }, d =>
    d.P('M300 230 L560 230 L585 565 Q770 590 805 700 L805 790 L235 790 L235 650 Q265 560 300 230 Z') +
    d.R(280, 200, 300, 64, 30, 'light') +
    d.R(215, 780, 610, 74, 30, 'dark') +
    d.Lt('M480 300 L570 340 M570 300 L480 340 M485 390 L575 430 M575 390 L485 430 M490 480 L580 520 M580 480 L490 520') +
    d.C(530, 290, 10, 'accent') +
    d.face(675, 690, 128));

  A.add('water-bottle', 'Water Bottle', { main: TEAL, accent: GR, light: W, pink: P }, d =>
    d.C(500, 160, 52) + d.C(500, 160, 24, 'light') +
    d.R(400, 195, 200, 120, 26, 'accent') +
    d.R(370, 300, 260, 570, 64) +
    d.R(370, 500, 260, 210, 0, 'light') +
    d.face(500, 595, 145));

  A.add('picnic-basket', 'Picnic Basket', { main: TAN, dark: BR, accent: R, light: W, pink: P }, d =>
    tube(d, ['M300 470 Q500 150 700 470'], 'dark', 62) +
    d.P('M250 460 Q300 380 360 440 Q420 380 480 440 Q540 380 600 440 Q660 380 720 440 Q760 410 760 470 L250 470 Z', 'accent') +
    d.poly([[200, 500], [800, 500], [740, 850], [260, 850]]) +
    d.R(175, 450, 650, 70, 30, 'dark') +
    d.Lt('M240 610 L350 610 M250 700 L360 700 M260 790 L370 790 M650 610 L760 610 M640 700 L750 700 M630 790 L740 790') +
    d.face(500, 660, 180));

  A.add('cabin', 'Cabin', { main: TAN, dark: BR, accent: R, light: B, door: DB, pink: P }, d =>
    d.R(640, 210, 80, 180, 6, 'dark') +
    d.R(220, 450, 560, 400, 0) +
    d.Lt('M220 525 L410 525 M220 600 L410 600 M220 680 L410 680 M220 760 L410 760 M590 525 L780 525 M590 600 L780 600 M590 680 L780 680 M590 760 L780 760') +
    d.poly([[160, 475], [500, 190], [840, 475]], 'accent') +
    d.R(430, 630, 140, 220, 20, 'door') + d.C(545, 745, 10, 'dark') +
    d.R(260, 560, 110, 100, 10, 'light') + d.L('M315 560 L315 660 M260 610 L370 610') +
    d.R(630, 560, 110, 100, 10, 'light') + d.L('M685 560 L685 660 M630 610 L740 610') +
    d.face(500, 365, 150));

  A.add('camper', 'Camper', { main: W, accent: B, dark: DGR, light: '#e3f2fd', stripe: O, pink: P }, d =>
    d.R(300, 285, 170, 60, 14, 'dark') +
    d.R(130, 330, 740, 400, 70) +
    d.P('M760 345 L860 470 L860 530 L760 530 Z', 'light') +
    d.R(200, 400, 160, 120, 20, 'light') + d.R(400, 400, 160, 120, 20, 'light') +
    d.R(130, 560, 740, 40, 0, 'stripe') +
    d.C(300, 760, 82, 'dark') + d.C(300, 760, 30, 'light') +
    d.C(700, 760, 82, 'dark') + d.C(700, 760, 30, 'light') +
    d.face(500, 645, 120));

  A.add('hammock', 'Hammock', { main: R, tree: DG, dark: BR, light: CREAM, pink: P }, d =>
    d.R(110, 260, 90, 620, 20, 'dark') + d.R(800, 260, 90, 620, 20, 'dark') +
    d.C(110, 230, 95, 'tree') + d.C(210, 200, 100, 'tree') + d.C(160, 120, 90, 'tree') +
    d.C(790, 200, 100, 'tree') + d.C(890, 230, 95, 'tree') + d.C(840, 120, 90, 'tree') +
    d.L('M200 430 L280 525 M800 430 L720 525') +
    d.P('M260 520 Q500 700 740 520 Q500 930 260 520 Z') +
    d.grass(890) +
    d.face(500, 655, 118));

  A.add('trail-sign', 'Trail Sign', { main: TAN, light: CREAM, dark: BR, rock: GR, pink: P }, d =>
    d.R(460, 280, 80, 590, 16, 'dark') +
    d.poly([[190, 300], [690, 300], [800, 380], [690, 460], [190, 460]]) +
    d.poly([[300, 530], [800, 530], [800, 660], [300, 660], [215, 595]], 'light') +
    d.E(390, 870, 70, 34, 'rock') + d.E(620, 870, 80, 38, 'rock') +
    d.grass(880) +
    d.face(470, 375, 140));

  A.add('camp-chair', 'Camp Chair', { main: B, dark: NAVY, accent: DGR, pink: P }, d =>
    tube(d, ['M300 870 L700 570', 'M700 870 L300 570'], 'accent', 46) +
    d.R(250, 520, 500, 80, 22, 'dark') +
    d.R(270, 190, 460, 340, 34) +
    d.R(190, 470, 120, 44, 16, 'accent') + d.R(690, 470, 120, 44, 16, 'accent') +
    d.face(500, 355, 180));

  A.add('cooler', 'Cooler', { main: B, light: W, dark: NAVY, pink: P }, d =>
    tube(d, ['M380 350 L380 285 L620 285 L620 350'], 'dark', 46) +
    d.R(165, 560, 70, 130, 22, 'dark') + d.R(765, 560, 70, 130, 22, 'dark') +
    d.R(210, 400, 580, 430, 44) +
    d.R(190, 340, 620, 120, 40, 'light') +
    d.face(500, 640, 190));

  // ---------------- woodland animals ----------------
  A.add('raccoon', 'Raccoon', { main: GR, dark: '#5f6b73', light: W, pink: P }, d => {
    let tail = d.E(750, 630, 235, 88);
    tail += d.band(750, 630, 235, 88, 580, 635, 'dark') + d.band(750, 630, 235, 88, 700, 755, 'dark') + d.band(750, 630, 235, 88, 820, 875, 'dark') + d.band(750, 630, 235, 88, 940, 980, 'dark');
    return group(tail, -62, 750, 630) +
      d.E(470, 700, 190, 185) +
      d.E(470, 735, 112, 128, 'light') +
      d.E(380, 878, 62, 30) + d.E(560, 878, 62, 30) +
      d.P('M335 315 L355 200 L440 270 Z') + d.P('M605 315 L585 200 L500 270 Z') +
      d.C(470, 400, 150) +
      d.E(416, 388, 50, 22, 'dark', -12) + d.E(524, 388, 50, 22, 'dark', 12) +
      d.face(470, 406, 160);
  });

  A.add('deer', 'Deer', { main: BR, light: CREAM, dark: DB, pink: P }, d =>
    legs(d, [315, 395, 500, 580], 630, 865, 54) +
    d.E(235, 500, 32, 44, 'light') +
    d.E(445, 560, 225, 128) +
    d.C(330, 520, 18, 'light') + d.C(390, 500, 18, 'light') + d.C(360, 580, 18, 'light') + d.C(450, 530, 18, 'light') + d.C(420, 610, 18, 'light') +
    d.P('M548 560 Q560 420 596 320 L716 320 Q690 440 690 560 Z') +
    d.E(560, 180, 70, 28, 'main', -30) + d.E(760, 180, 70, 28, 'main', 30) +
    d.E(660, 285, 118, 105) +
    d.face(660, 290, 145));

  A.add('squirrel', 'Squirrel', { main: O, light: CREAM, dark: BR, accent: TAN, pink: P }, d =>
    d.P('M470 830 Q150 820 160 560 Q170 300 330 240 Q480 200 480 360 Q480 460 390 480 Q310 500 320 590 Q330 690 480 710 Z') +
    d.E(575, 660, 145, 175) +
    d.E(595, 700, 82, 120, 'light') +
    d.E(530, 830, 64, 26) + d.E(665, 830, 64, 26) +
    d.P('M535 300 L540 220 L590 275 Z') + d.P('M665 300 L660 220 L610 275 Z') +
    d.C(600, 395, 120) +
    d.face(600, 405, 140));

  A.add('beaver', 'Beaver', { main: BR, dark: DB, light: TAN, tooth: W, pink: P }, d =>
    group(d.E(770, 800, 165, 70, 'dark') + d.Lt('M680 770 L740 830 M740 770 L800 830 M800 770 L860 830 M680 830 L740 770 M740 830 L800 770'), -15, 770, 800) +
    d.E(480, 640, 230, 220) +
    d.E(480, 680, 135, 150, 'light') +
    d.E(380, 865, 70, 32, 'dark') + d.E(580, 865, 70, 32, 'dark') +
    d.C(360, 255, 36) + d.C(600, 255, 36) +
    d.C(480, 380, 150) +
    d.R(457, 448, 22, 38, 6, 'tooth') + d.R(481, 448, 22, 38, 6, 'tooth') +
    d.face(480, 365, 160));

  A.add('moose', 'Moose', { main: DB, dark: '#5d3a26', light: TAN, antler: '#e6c590', pink: P }, d =>
    d.P('M390 280 Q250 300 180 200 Q205 160 238 196 Q238 128 274 128 Q292 186 308 140 Q336 116 356 150 Q350 210 410 228 Z', 'antler') +
    d.P('M610 280 Q750 300 820 200 Q795 160 762 196 Q762 128 726 128 Q708 186 692 140 Q664 116 644 150 Q650 210 590 228 Z', 'antler') +
    d.E(330, 330, 72, 30, 'main', -20) + d.E(670, 330, 72, 30, 'main', 20) +
    d.P('M440 650 Q500 760 560 650 Z', 'dark') +
    d.E(500, 470, 150, 200) +
    d.E(500, 615, 125, 88, 'light') +
    d.E(465, 628, 12, 18, 'ink') + d.E(535, 628, 12, 18, 'ink') +
    d.face(500, 420, 165));

  A.add('bat', 'Bat', { main: PURPLE, dark: '#7e57c2', light: '#ede7f6', pink: P }, d =>
    d.P('M400 470 Q290 300 110 360 Q160 420 150 480 Q215 460 245 520 Q295 480 335 545 Q375 505 410 545 Z', 'dark') +
    d.P('M600 470 Q710 300 890 360 Q840 420 850 480 Q785 460 755 520 Q705 480 665 545 Q625 505 590 545 Z', 'dark') +
    d.P('M395 380 L410 260 L470 340 Z') + d.P('M605 380 L590 260 L530 340 Z') +
    d.C(500, 480, 150) +
    d.E(500, 588, 72, 44, 'light') +
    d.face(500, 455, 170));

  A.add('firewood', 'Firewood', { main: TAN, dark: BR, light: CREAM, pink: P }, d => {
    const log = (x, y, plain) => d.C(x, y, 110) + (plain ? '' : d.C(x, y, 64, 'light') + d.C(x, y, 22, 'dark'));
    return log(500, 380) + log(395, 560) + log(605, 560) + log(290, 740) + log(710, 740) + log(500, 740, true) +
      d.grass(870) +
      d.face(500, 742, 150);
  });
})();
