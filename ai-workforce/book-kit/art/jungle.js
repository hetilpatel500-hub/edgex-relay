// "My First Jungle & Safari": 30 friendly jungle and safari animals and things, for ages 2-5.
// Drawn from scratch: no brands, logos, vehicle makers or characters. Animals already drawn in
// other books of the series (lion, elephant, giraffe, monkey, panda, parrot, toucan, flamingo,
// peacock, ostrich, snake, lizard, frog, bat, butterfly) and things already drawn (palm tree,
// coconut, banana, binoculars, map, compass, backpack, tent, sun hat) are left out.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', DGR = '#90a4ae', W = '#ffffff', CREAM = '#fff3d6', TAN = '#e8b97a', CHOC = '#7a4a2e', PURPLE = '#b39ddb', TEAL = '#4dd0c4',
    KHAKI = '#c9b77a', OLIVE = '#a1a86b', CHAR = '#5f6b73';

  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (tails, arms, branches): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  // four legs with hooves or paws for side-on animals
  const legs = (d, xs, top, bot, w = 46, foot = 'dark') => xs.map(x =>
    d.R(x, top, w, bot - top, 20) + d.R(x - 5, bot - 40, w + 10, 46, 16, foot)).join('');
  // a small muzzle: two cheeks, a nose and a smile
  const muzzle = (d, x, y, s = 1, nose = 'pink') =>
    d.E(x - 42 * s, y, 50 * s, 40 * s, 'light') + d.E(x + 42 * s, y, 50 * s, 40 * s, 'light') +
    d.P(`M${x - 28 * s} ${y - 36 * s} L${x + 28 * s} ${y - 36 * s} L${x} ${y - 6 * s} Z`, nose);

  // ---------------- jungle animals ----------------
  A.add('tiger', 'Tiger', { main: O, dark: CHOC, light: W, pink: P }, d =>
    d.C(325, 300, 75) + d.C(675, 300, 75) + d.C(325, 300, 38, 'light') + d.C(675, 300, 38, 'light') +
    d.P('M300 450 L205 500 L285 545 L210 600 L305 630 Z') + d.P('M700 450 L795 500 L715 545 L790 600 L695 630 Z') +
    d.C(500, 490, 225) +
    d.P('M500 266 Q474 305 500 360 Q526 305 500 266 Z', 'dark') +
    d.P('M432 278 Q420 312 446 346 Q458 306 458 272 Z', 'dark') + d.P('M568 278 Q580 312 554 346 Q542 306 542 272 Z', 'dark') +
    d.P('M277 445 Q330 450 362 472 Q322 484 280 488 Z', 'dark') +
    d.P('M723 445 Q670 450 638 472 Q678 484 720 488 Z', 'dark') +
    muzzle(d, 500, 600, 1.15) +
    d.smile(500, 668, 30, 16) + d.C(360, 552, 24, 'pink') + d.C(640, 552, 24, 'pink') +
    d.eye(420, 460, 26) + d.eye(580, 460, 26));

  A.add('jaguar', 'Jaguar', { main: Y, dark: CHOC, light: CREAM, branch: BR, leaf: G, pink: P }, d => {
    const ros = (x, y) => d.C(x, y, 26, 'light') + d.dot(x, y, 9);
    return tube(d, ['M255 610 Q190 720 235 840'], 'main', 64) + d.C(238, 846, 30, 'dark') +
      d.R(70, 650, 860, 70, 35, 'branch') +
      d.P('M120 650 Q90 590 140 560 Q170 610 150 650 Z', 'leaf') + d.P('M880 650 Q910 590 860 560 Q830 610 850 650 Z', 'leaf') +
      d.R(360, 600, 56, 210, 26) + d.R(560, 600, 56, 210, 26) +
      d.E(460, 590, 230, 92) +
      ros(330, 570) + ros(420, 545) + ros(510, 565) + ros(390, 615) + ros(480, 620) +
      d.C(630, 380, 38) + d.C(790, 380, 38) + d.C(630, 380, 18, 'pink') + d.C(790, 380, 18, 'pink') +
      d.C(710, 480, 125) +
      d.C(640, 425, 12, 'dark') + d.C(780, 425, 12, 'dark') + d.C(710, 395, 12, 'dark') +
      muzzle(d, 710, 540, 0.85) +
      d.smile(710, 585, 24, 12) +
      d.eye(665, 470, 21) + d.eye(755, 470, 21);
  });

  A.add('gorilla', 'Gorilla', { main: '#78909c', dark: '#546e7a', light: '#cfd8dc', pink: P }, d =>
    d.E(500, 720, 250, 200) +
    d.E(500, 730, 140, 150, 'light') +
    d.E(275, 700, 80, 175) + d.E(725, 700, 80, 175) +
    d.E(275, 865, 82, 48, 'dark') + d.E(725, 865, 82, 48, 'dark') +
    d.E(420, 905, 80, 38, 'dark') + d.E(580, 905, 80, 38, 'dark') +
    d.C(340, 380, 40, 'light') + d.C(660, 380, 40, 'light') +
    d.C(500, 370, 170) +
    d.P('M400 350 Q450 318 500 348 Q550 318 600 350 Q640 420 600 495 Q500 545 400 495 Q360 420 400 350 Z', 'light') +
    d.E(500, 445, 52, 30, 'dark') + d.dot(482, 446, 9) + d.dot(518, 446, 9) +
    d.smile(500, 482, 40, 22) + d.C(410, 450, 20, 'pink') + d.C(590, 450, 20, 'pink') +
    d.eye(450, 375, 22) + d.eye(550, 375, 22));

  A.add('orangutan', 'Orangutan', { main: O, dark: '#e07b2a', light: '#f6c99a', branch: BR, pink: P }, d =>
    d.R(80, 140, 840, 62, 31, 'branch') +
    tube(d, ['M410 560 Q330 400 360 175', 'M590 560 Q670 400 640 175'], 'main', 84) +
    d.C(360, 168, 46) + d.C(640, 168, 46) +
    d.E(420, 850, 62, 75) + d.E(580, 850, 62, 75) +
    d.E(500, 680, 165, 190) +
    d.E(500, 710, 95, 120, 'light') +
    d.P('M400 380 Q390 300 450 300 Q470 260 510 285 Q550 262 570 300 Q620 300 605 380 Z', 'dark') +
    d.C(500, 440, 125) +
    d.E(500, 470, 92, 82, 'light') +
    d.dot(485, 478, 8) + d.dot(515, 478, 8) + d.smile(500, 505, 34, 20) +
    d.C(430, 490, 16, 'pink') + d.C(570, 490, 16, 'pink') +
    d.eye(462, 440, 19) + d.eye(538, 440, 19));

  A.add('sloth', 'Sloth', { main: TAN, dark: BR, light: CREAM, branch: DB, leaf: G, pink: P }, d =>
    d.R(70, 200, 860, 64, 32, 'branch') +
    d.P('M170 264 Q150 330 190 360 Q220 310 210 264 Z', 'leaf') + d.P('M820 264 Q850 330 810 360 Q780 310 790 264 Z', 'leaf') +
    tube(d, ['M400 480 Q340 360 350 232', 'M600 480 Q660 360 650 232'], 'main', 76) +
    d.L('M325 218 Q330 190 352 186 M352 214 Q360 188 382 188 M625 218 Q630 190 652 186 M652 214 Q660 188 682 188') +
    d.E(420, 760, 60, 70) + d.E(580, 760, 60, 70) +
    d.E(500, 570, 175, 195) +
    d.E(500, 520, 118, 95, 'light') +
    d.E(452, 512, 40, 24, 'dark', -22) + d.E(548, 512, 40, 24, 'dark', 22) +
    d.eye(455, 512, 15) + d.eye(545, 512, 15) +
    d.E(500, 545, 20, 14, 'ink') + d.smile(500, 568, 30, 16) +
    d.C(410, 560, 16, 'pink') + d.C(590, 560, 16, 'pink'));

  A.add('lemur', 'Lemur', { main: GR, dark: CHAR, light: W, pink: P }, d => {
    let tail = d.E(700, 480, 330, 62);
    for (let x = 425; x < 1025; x += 110) tail += d.band(700, 480, 330, 62, x, x + 55, 'dark');
    return group(tail, -65, 700, 480) +
      d.E(450, 690, 150, 175) +
      d.E(450, 720, 88, 125, 'light') +
      d.E(385, 865, 62, 28) + d.E(515, 865, 62, 28) +
      d.P('M360 320 L345 230 L420 290 Z') + d.P('M540 320 L555 230 L480 290 Z') +
      d.C(450, 400, 120) +
      d.E(450, 430, 86, 90, 'light') +
      d.P('M372 402 Q410 370 440 410 Q410 446 372 402 Z', 'dark') + d.P('M528 402 Q490 370 460 410 Q490 446 528 402 Z', 'dark') +
      d.P('M430 470 L470 470 L450 500 Z', 'dark') +
      d.smile(450, 512, 22, 12) + d.C(380, 470, 16, 'pink') + d.C(520, 470, 16, 'pink') +
      d.eye(410, 410, 17) + d.eye(490, 410, 17);
  });

  A.add('chameleon', 'Chameleon', { main: G, dark: DG, accent: Y, light: W, branch: BR, pink: P }, d =>
    tube(d, ['M330 600 Q190 600 180 680 Q175 750 250 750 Q310 748 305 690 Q300 650 262 660'], 'main', 60) +
    d.R(80, 760, 840, 60, 30, 'branch') +
    tube(d, ['M440 640 L420 770', 'M620 640 L640 770'], 'main', 48) +
    d.E(415, 785, 40, 22) + d.E(645, 785, 40, 22) +
    d.E(520, 570, 215, 130) +
    d.band(520, 570, 215, 130, 400, 440, 'accent') + d.band(520, 570, 215, 130, 490, 530, 'accent') + d.band(520, 570, 215, 130, 580, 620, 'accent') +
    d.P('M330 470 Q360 420 400 445 Q430 410 470 440 Q510 405 545 438 Q590 408 620 445 Q640 450 650 470 Z', 'dark') +
    d.P('M660 480 Q800 470 860 560 Q860 640 760 650 Q690 650 660 640 Z') +
    d.C(740, 540, 50, 'light') + d.eye(746, 540, 20) +
    d.L('M760 610 Q810 615 852 590') + d.C(800, 575, 18, 'pink'));

  A.add('anteater', 'Anteater', { main: '#bcaaa4', dark: '#5d4037', light: CREAM, pink: P }, d =>
    d.P('M300 560 Q90 570 100 330 Q170 290 230 350 Q300 420 335 500 Z', 'dark') + d.Lt('M150 380 Q200 430 250 470 M130 460 Q190 500 250 520') +
    legs(d, [330, 400, 520, 590], 640, 860, 54) +
    d.E(460, 600, 230, 120) +
    d.P('M600 520 Q480 560 330 690 L300 660 Q440 530 580 495 Z', 'dark') +
    d.P('M620 530 Q720 520 910 610 Q918 636 892 642 Q720 650 620 660 Z') +
    d.E(655, 505, 26, 34) +
    d.eye(705, 565, 15) + d.C(700, 605, 16, 'pink') +
    d.smile(830, 628, 26, 10));

  A.add('capybara', 'Capybara', { main: BR, dark: DB, light: TAN, accent: O, leaf: G, pink: P }, d =>
    d.E(500, 665, 270, 180) +
    d.E(375, 850, 58, 40, 'dark') + d.E(625, 850, 58, 40, 'dark') +
    d.C(392, 322, 28) + d.C(608, 322, 28) +
    d.R(360, 315, 280, 265, 80) +
    d.E(500, 510, 90, 55, 'dark') + d.dot(470, 505, 10) + d.dot(530, 505, 10) +
    d.smile(500, 548, 30, 14) + d.C(405, 480, 20, 'pink') + d.C(595, 480, 20, 'pink') +
    d.eye(445, 420, 22) + d.eye(555, 420, 22) +
    d.C(500, 270, 52, 'accent') + d.P('M500 218 Q520 170 570 180 Q550 225 500 218 Z', 'leaf') +
    d.grass(890));

  A.add('crocodile', 'Crocodile', { main: G, dark: DG, light: '#e8f5c8', tooth: W, pink: P }, d => {
    let bumps = '';
    for (let x = 290; x <= 610; x += 80) bumps += d.C(x, 535, 30, 'dark');
    return d.R(340, 650, 54, 140, 22) + d.R(560, 650, 54, 140, 22) +
      d.P('M260 590 Q140 600 50 700 Q170 700 270 680 Z') +
      bumps +
      d.E(450, 620, 230, 100) +
      d.P('M300 660 Q450 720 600 660 Q450 700 300 660 Z', 'light') +
      d.R(600, 560, 340, 112, 56) +
      d.C(690, 545, 40) + d.C(690, 545, 26, 'light') + d.dot(694, 545, 11) +
      d.P('M720 640 L740 662 L760 640 Z', 'tooth') + d.P('M790 642 L810 664 L830 642 Z', 'tooth') + d.P('M860 638 L880 660 L900 636 Z', 'tooth') +
      d.L('M690 640 Q820 650 930 628') +
      d.dot(905, 585, 9) + d.C(740, 610, 18, 'pink') +
      d.water(870);
  });

  A.add('hornbill', 'Hornbill', { main: '#455a64', light: W, accent: Y, accent2: O, branch: BR, pink: P }, d =>
    d.P('M380 640 L300 900 L400 910 L450 660 Z') +
    d.R(130, 760, 740, 58, 29, 'branch') +
    d.E(440, 580, 150, 200) +
    d.E(470, 640, 90, 130, 'light') +
    d.E(380, 590, 70, 150, 'main', 12) +
    d.E(430, 790, 34, 18, 'accent2') + d.E(500, 790, 34, 18, 'accent2') +
    d.C(520, 330, 100) +
    d.P('M590 285 Q790 290 880 430 Q770 385 600 380 Z', 'accent') +
    d.P('M560 255 Q690 205 790 290 Q690 280 590 288 Z', 'accent2') +
    d.eye(535, 320, 19) + d.C(530, 365, 18, 'pink') + d.smile(590, 352, 18, 10));

  // ---------------- safari animals ----------------
  A.add('zebra', 'Zebra', { main: W, dark: '#37474f', light: GR, pink: P }, d =>
    tube(d, ['M230 520 Q180 600 200 680'], 'main', 30) + d.E(200, 700, 22, 34, 'dark') +
    legs(d, [300, 380, 490, 570], 630, 870, 50) +
    d.E(440, 560, 225, 125) +
    d.band(440, 560, 225, 125, 260, 290, 'dark') + d.band(440, 560, 225, 125, 335, 365, 'dark') +
    d.band(440, 560, 225, 125, 410, 440, 'dark') + d.band(440, 560, 225, 125, 485, 515, 'dark') +
    d.P('M592 330 L548 338 L578 372 L530 390 L566 425 L518 445 L556 478 L510 500 L548 520 L520 545 Z', 'dark') +
    d.P('M520 560 Q540 420 580 320 L710 320 Q680 440 680 560 Z') +
    d.P('M545 470 Q620 455 668 490 Q610 488 540 505 Z', 'dark') +
    d.P('M562 390 Q635 375 684 405 Q628 405 556 425 Z', 'dark') +
    d.P('M580 200 L560 110 L620 170 Z') + d.P('M720 200 L740 110 L680 170 Z') +
    d.E(650, 260, 108, 112) +
    d.E(650, 340, 72, 50, 'light') + d.dot(626, 336, 9) + d.dot(674, 336, 9) +
    d.smile(650, 360, 22, 10) +
    d.eye(605, 255, 20) + d.eye(695, 255, 20));

  A.add('hippo', 'Hippo', { main: PURPLE, dark: '#9575cd', light: '#e1d5f5', tooth: W, pink: P }, d =>
    d.E(500, 730, 290, 190) +
    d.E(350, 895, 78, 42, 'dark') + d.E(650, 895, 78, 42, 'dark') +
    d.E(370, 250, 34, 26) + d.E(630, 250, 34, 26) + d.E(370, 250, 16, 12, 'pink') + d.E(630, 250, 16, 12, 'pink') +
    d.C(405, 320, 56) + d.C(595, 320, 56) +
    d.E(500, 420, 205, 150) +
    d.E(500, 560, 250, 135) +
    d.E(430, 500, 22, 16, 'dark') + d.E(570, 500, 22, 16, 'dark') +
    d.P('M380 590 Q500 680 620 590') +
    d.R(445, 608, 28, 34, 8, 'tooth') + d.R(527, 608, 28, 34, 8, 'tooth') +
    d.L('M380 590 Q500 680 620 590') +
    d.C(300, 560, 28, 'pink') + d.C(700, 560, 28, 'pink') +
    d.eye(405, 330, 24) + d.eye(595, 330, 24));

  A.add('rhino', 'Rhino', { main: GR, dark: DGR, light: '#eceff1', pink: P }, d =>
    legs(d, [250, 340, 470, 560], 620, 860, 70) +
    d.Lt('M190 540 Q160 560 170 600') +
    d.E(420, 570, 240, 150) +
    d.Lt('M330 460 Q350 560 330 680 M520 450 Q540 560 520 690') +
    d.P('M640 450 L628 362 L692 425 Z') +
    d.E(720, 530, 150, 115, 'main', 12) +
    d.P('M800 470 Q850 360 830 290 Q890 380 880 500 Z', 'light') +
    d.P('M745 450 Q770 400 765 370 Q800 410 795 460 Z', 'light') +
    d.eye(700, 500, 18) + d.C(720, 560, 20, 'pink') +
    d.smile(810, 590, 30, 14) + d.dot(855, 545, 8));

  A.add('cheetah', 'Cheetah', { main: Y, dark: CHOC, light: CREAM, pink: P }, d =>
    tube(d, ['M600 850 Q770 860 780 730 Q785 640 715 650'], 'main', 52) + d.C(712, 650, 28, 'dark') +
    d.E(500, 690, 150, 200) +
    d.E(500, 720, 85, 140, 'light') +
    d.dot(410, 620, 13) + d.dot(590, 620, 13) + d.dot(400, 720, 13) + d.dot(600, 720, 13) + d.dot(430, 800, 12) + d.dot(570, 800, 12) +
    d.R(425, 740, 56, 160, 26) + d.R(519, 740, 56, 160, 26) +
    d.E(450, 900, 48, 26) + d.E(550, 900, 48, 26) +
    d.C(410, 270, 36) + d.C(590, 270, 36) + d.C(410, 270, 17, 'pink') + d.C(590, 270, 17, 'pink') +
    d.C(500, 370, 130) +
    d.dot(450, 290, 9) + d.dot(550, 290, 9) + d.dot(500, 275, 9) +
    d.L('M446 386 Q412 398 398 440 M554 386 Q588 398 602 440') +
    muzzle(d, 500, 430, 0.85) +
    d.smile(500, 472, 22, 12) +
    d.eye(452, 365, 20) + d.eye(548, 365, 20));

  A.add('meerkat', 'Meerkat', { main: TAN, dark: '#6d4c41', light: CREAM, mound: BR, pink: P }, d =>
    d.E(500, 900, 300, 60, 'mound') +
    tube(d, ['M570 820 Q660 880 740 860'], 'main', 40) + d.C(745, 858, 20, 'dark') +
    d.E(500, 640, 125, 235) +
    d.E(500, 670, 72, 175, 'light') +
    d.E(455, 520, 32, 62, 'main', -20) + d.E(545, 520, 32, 62, 'main', 20) +
    d.E(450, 875, 62, 26) + d.E(550, 875, 62, 26) +
    d.C(405, 300, 26, 'dark') + d.C(595, 300, 26, 'dark') +
    d.E(500, 330, 100, 90) +
    d.E(500, 385, 50, 34, 'light') +
    d.E(458, 318, 30, 24, 'dark') + d.E(542, 318, 30, 24, 'dark') +
    d.eye(458, 318, 15) + d.eye(542, 318, 15) +
    d.E(500, 368, 14, 10, 'ink') + d.smile(500, 392, 20, 10) +
    d.C(430, 365, 14, 'pink') + d.C(570, 365, 14, 'pink'));

  A.add('warthog', 'Warthog', { main: '#a1887f', dark: '#5d4037', light: '#d7ccc8', tusk: W, pink: P }, d =>
    d.E(500, 790, 230, 130) +
    d.E(400, 905, 60, 30, 'dark') + d.E(600, 905, 60, 30, 'dark') +
    d.P('M330 380 L290 260 L400 320 Z') + d.P('M670 380 L710 260 L600 320 Z') +
    d.P('M440 300 L455 220 L480 280 L500 205 L520 280 L545 220 L560 300 Z', 'dark') +
    d.E(500, 470, 200, 175) +
        d.P('M425 612 Q378 592 382 535 Q402 575 438 588 Z', 'tusk') + d.P('M575 612 Q622 592 618 535 Q598 575 562 588 Z', 'tusk') +
    d.E(500, 600, 105, 75, 'light') +
    d.E(475, 595, 14, 20, 'ink') + d.E(525, 595, 14, 20, 'ink') +
    d.smile(500, 640, 34, 14) + d.C(355, 505, 22, 'pink') + d.C(645, 505, 22, 'pink') +
    d.eye(440, 435, 21) + d.eye(560, 435, 21));

  A.add('gazelle', 'Gazelle', { main: TAN, dark: DB, light: W, horn: '#6d4c41', pink: P }, d =>
    tube(d, ['M605 210 Q560 120 605 45', 'M695 210 Q740 120 695 45'], 'horn', 42) +
    d.Lt('M570 150 L600 150 M572 110 L602 110 M700 150 L730 150 M698 110 L728 110') +
    legs(d, [320, 390, 490, 560], 620, 880, 34) +
    d.E(240, 520, 24, 40, 'dark') +
    d.E(440, 560, 225, 125) +
    d.P('M555 575 Q560 430 610 320 L695 320 Q675 450 690 560 Z') +
    d.E(560, 200, 60, 24, 'main', -30) + d.E(740, 200, 60, 24, 'main', 30) +
    d.E(650, 290, 105, 100) +
    d.face(650, 285, 135));

  A.add('buffalo', 'Buffalo', { main: '#78909c', dark: '#455a64', light: '#cfd8dc', horn: '#efe6d8', pink: P }, d =>
    d.E(500, 810, 260, 120) +
    d.E(330, 470, 60, 30, 'main', 20) + d.E(670, 470, 60, 30, 'main', -20) +
    d.E(500, 530, 160, 200) +
    d.P('M500 340 Q330 290 220 360 Q170 420 225 480 Q240 410 330 400 Q420 395 500 420 Z', 'horn') +
    d.P('M500 340 Q670 290 780 360 Q830 420 775 480 Q760 410 670 400 Q580 395 500 420 Z', 'horn') +
    d.E(500, 660, 110, 80, 'light') +
    d.E(470, 650, 14, 20, 'ink') + d.E(530, 650, 14, 20, 'ink') +
    d.smile(500, 695, 30, 14) + d.C(400, 575, 22, 'pink') + d.C(600, 575, 22, 'pink') +
    d.eye(440, 515, 22) + d.eye(560, 515, 22));

  A.add('baboon', 'Baboon', { main: OLIVE, dark: '#7c8350', light: '#f3c4b8', pink: P }, d =>
    tube(d, ['M640 800 Q780 760 790 640'], 'main', 50) +
    tube(d, ['M400 600 Q350 720 380 860', 'M600 600 Q650 720 620 860'], 'main', 70) +
    d.E(500, 700, 160, 190) +
    d.E(500, 730, 90, 130, 'light') +
    d.E(380, 870, 56, 32, 'dark') + d.E(620, 870, 56, 32, 'dark') +
    d.C(385, 360, 32, 'light') + d.C(615, 360, 32, 'light') +
    d.C(500, 400, 125) +
    d.Lt('M400 335 Q432 318 470 338 M530 338 Q568 318 600 335') +
    d.R(452, 385, 96, 175, 48, 'light') +
    d.dot(484, 528, 8) + d.dot(516, 528, 8) +
    d.smile(500, 540, 20, 9) + d.C(415, 445, 18, 'pink') + d.C(585, 445, 18, 'pink') +
    d.eye(432, 372, 19) + d.eye(568, 372, 19));

  A.add('hyena', 'Hyena', { main: TAN, dark: DB, light: CREAM, pink: P }, d =>
    tube(d, ['M220 540 Q170 600 180 680'], 'main', 36) + d.E(180, 700, 24, 36, 'dark') +
    legs(d, [280, 350, 480, 550], 620, 860, 50) +
    group(d.E(420, 560, 220, 115), -10, 420, 560) +
    d.dot(330, 560, 13) + d.dot(400, 520, 13) + d.dot(380, 610, 13) + d.dot(470, 560, 13) + d.dot(300, 620, 12) +
    d.P('M430 460 L450 415 L472 452 L497 405 L520 448 L545 400 L565 455 Z', 'dark') +
    d.C(590, 350, 44) + d.C(750, 350, 44) + d.C(590, 350, 22, 'pink') + d.C(750, 350, 22, 'pink') +
    d.E(670, 445, 115, 100) +
    d.E(670, 510, 62, 40, 'light') + d.E(670, 490, 22, 14, 'ink') +
    d.smile(670, 515, 24, 12) +
    d.C(592, 480, 16, 'pink') + d.C(748, 480, 16, 'pink') +
    d.eye(625, 435, 18) + d.eye(715, 435, 18));

  A.add('pangolin', 'Pangolin', { main: BR, dark: DB, light: TAN, pink: P }, d => {
    let scales = '';
    for (const y of [470, 530, 590, 650]) {
      const half = 230 * Math.sqrt(1 - ((y + 20 - 580) / 170) ** 2) - 30;
      for (let x = 460 - half; x + 64 <= 460 + half; x += 64) scales += d.Lt(`M${x.toFixed(0)} ${y} q32 38 64 0`);
    }
    return d.P('M290 600 Q140 640 120 760 Q140 860 260 850 Q200 780 250 720 Q300 680 360 680 Z') +
      d.Lt('M160 700 q30 22 56 0 M150 770 q28 22 54 0 M200 830 q26 18 50 0') +
      d.E(370, 760, 40, 50, 'dark') + d.E(580, 760, 40, 50, 'dark') +
      d.E(460, 580, 230, 170) + scales +
      d.P('M670 560 Q790 560 890 660 Q800 700 670 690 Z', 'light') +
      d.eye(752, 612, 15) + d.C(740, 648, 15, 'pink') +
      d.smile(840, 665, 18, 8) +
      d.grass(880);
  });

  // ---------------- safari things ----------------
  A.add('safari-truck', 'Safari Truck', { main: KHAKI, dark: '#6d6a4f', light: B, accent: Y, tire: '#546e7a', hub: GR, pink: P }, d =>
    d.C(130, 560, 72, 'tire') + d.C(130, 560, 30, 'hub') +
    tube(d, ['M280 470 L310 320 L520 320 L545 470'], 'dark', 40) +
    d.P('M630 470 L670 320 L705 320 L668 470 Z', 'light') +
    d.R(150, 460, 720, 230, 60) +
    d.R(150, 600, 720, 30, 10, 'dark') +
    d.C(845, 535, 26, 'accent') +
    d.C(300, 720, 95, 'tire') + d.C(300, 720, 40, 'hub') + d.C(720, 720, 95, 'tire') + d.C(720, 720, 40, 'hub') +
    d.face(510, 525, 150));

  A.add('camera', 'Camera', { main: GR, dark: '#455a64', light: '#b3e5fc', accent: R, pink: P }, d =>
    d.R(270, 250, 160, 90, 24, 'dark') + d.R(640, 270, 90, 70, 18, 'accent') +
    d.R(140, 320, 720, 470, 70) +
    d.R(140, 420, 720, 40, 10, 'dark') +
    d.C(500, 560, 190, 'dark') + d.C(500, 560, 140, 'light') +
    d.C(425, 485, 22, 'main') +
    d.R(720, 360, 90, 40, 14, 'light') +
    d.face(500, 580, 150));

  A.add('hot-air-balloon', 'Hot Air Balloon', { main: R, accent: Y, accent2: B, dark: BR, pink: P }, d =>
    d.L('M415 640 L430 765 M585 640 L570 765') +
    d.R(400, 760, 200, 140, 22, 'dark') + d.Lt('M400 805 L600 805 M400 850 L600 850 M465 760 L465 900 M535 760 L535 900') +
    d.P('M500 100 Q770 100 770 370 Q770 520 590 650 L410 650 Q230 520 230 370 Q230 100 500 100 Z') +
    d.P('M500 100 Q300 120 250 300 Q240 470 410 650 L450 650 Q330 470 360 300 Q390 170 500 100 Z', 'accent') +
    d.P('M500 100 Q700 120 750 300 Q760 470 590 650 L550 650 Q670 470 640 300 Q610 170 500 100 Z', 'accent2') +
    d.R(395, 630, 210, 40, 16, 'dark') +
    d.face(500, 380, 180));

  A.add('acacia-tree', 'Acacia Tree', { main: G, dark: DG, trunk: BR, pink: P }, d =>
    tube(d, ['M500 890 L500 610 Q470 500 360 430', 'M500 640 Q560 510 650 440', 'M500 560 L500 430'], 'trunk', 70) +
    d.E(500, 390, 360, 70) +
    d.C(230, 345, 85) + d.C(370, 300, 100) + d.C(530, 285, 110) + d.C(690, 305, 100) + d.C(790, 350, 80) +
    `<ellipse cx="500" cy="355" rx="330" ry="72" fill="${col(d, 'main')}"/>` +
    d.grass(890) +
    d.face(500, 330, 170));

  A.add('waterfall', 'Waterfall', { main: B, light: '#e1f5fe', rock: DGR, leaf: G, pink: P }, d =>
    d.P('M60 880 L70 320 Q80 240 160 250 Q200 170 280 200 Q340 160 400 220 L400 790 Q240 820 60 880 Z', 'rock') +
    d.P('M940 880 L930 320 Q920 240 840 250 Q800 170 720 200 Q660 160 600 220 L600 790 Q760 820 940 880 Z', 'rock') +
    d.Lt('M120 450 Q170 430 220 460 M150 620 Q210 600 260 630 M880 450 Q830 430 780 460 M850 620 Q790 600 740 630') +
    d.P('M150 255 Q150 170 220 160 Q215 230 150 255 Z', 'leaf') + d.P('M850 255 Q850 170 780 160 Q785 230 850 255 Z', 'leaf') +
    d.R(370, 160, 260, 620, 30) +
    d.Lt('M420 590 Q435 650 420 720 M580 590 Q565 650 580 720 M500 640 Q512 690 500 750') +
    d.E(500, 830, 380, 90) +
    d.C(380, 790, 46, 'light') + d.C(450, 770, 52, 'light') + d.C(550, 770, 52, 'light') + d.C(620, 790, 46, 'light') +
    d.E(170, 850, 80, 50, 'rock') + d.E(830, 850, 80, 50, 'rock') +
    d.Lt('M300 860 q30 -16 60 0 M640 860 q30 -16 60 0') +
    d.face(500, 400, 170));

  A.add('jungle-leaf', 'Jungle Leaf', { main: G, dark: DG, pink: P }, d => {
    // a split jungle leaf: the outline is sampled from three curves per side, with open notches cut to the middle
    const q = (a, c, b, t) => [(1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]];
    const segs = [[[500, 820], [230, 800], [150, 580]], [[150, 580], [100, 380], [250, 250]], [[250, 250], [380, 150], [500, 220]]];
    const notches = [[0, 0.70, 0.82, [385, 655]], [1, 0.20, 0.34, [365, 540]], [1, 0.66, 0.80, [390, 395]]];
    const left = [];
    segs.forEach((sg, k) => {
      for (let t = 0; t <= 1.0001; t += 0.02) {
        const n = notches.find(m => m[0] === k && t > m[1] && t < m[2]);
        if (n) { if (Math.abs(t - n[1] - 0.02) < 0.011) { left.push(q(...sg, n[1]), n[3], q(...sg, n[2])); } continue; }
        left.push(q(...sg, t));
      }
    });
    const right = left.slice().reverse().map(([x, y]) => [1000 - x, y]);
    return tube(d, ['M500 900 Q490 840 500 780'], 'dark', 44) +
      d.poly(left.concat(right)) +
      d.L('M500 800 L500 600') +
      d.face(500, 460, 160);
  });

  A.add('hibiscus', 'Hibiscus', { main: R, dark: '#e05555', accent: Y, leaf: G, pink: P }, d => {
    let petals = '';
    for (let i = 0; i < 5; i++) {
      const a = (i * 72 - 90) * Math.PI / 180;
      petals += d.E(500 + 205 * Math.cos(a), 500 + 205 * Math.sin(a), 165, 140, 'main', i * 72);
    }
    return d.P('M200 760 Q120 640 230 590 Q290 700 200 760 Z', 'leaf') + d.P('M800 760 Q880 640 770 590 Q710 700 800 760 Z', 'leaf') +
      petals +
      [0, 1, 2, 3, 4].map(i => { const t = (i * 72 - 90) * Math.PI / 180; return d.Lt(`M${500 + 150 * Math.cos(t)} ${500 + 150 * Math.sin(t)} L${500 + 290 * Math.cos(t)} ${500 + 290 * Math.sin(t)}`); }).join('') +
      d.C(500, 500, 130, 'dark') +
      tube(d, ['M560 395 Q600 300 660 250'], 'accent', 34) +
      d.C(660, 240, 22, 'accent') + d.C(700, 260, 18, 'accent') + d.C(680, 205, 18, 'accent') +
      d.face(500, 505, 120);
  });

  A.add('tree-house', 'Tree House', { main: TAN, dark: BR, roof: R, light: B, leaf: G, wood: DB, pink: P }, d =>
    d.C(260, 300, 150, 'leaf') + d.C(740, 300, 150, 'leaf') + d.C(500, 190, 170, 'leaf') + d.C(360, 160, 110, 'leaf') + d.C(640, 160, 110, 'leaf') +
    d.R(440, 520, 120, 390, 30, 'wood') +
    d.R(230, 500, 540, 44, 16, 'dark') +
    d.R(300, 330, 400, 175, 20) +
    d.poly([[270, 340], [500, 210], [730, 340]], 'roof') +
    d.R(600, 395, 70, 110, 14, 'dark') + d.C(615, 455, 7, 'ink') +
    d.L('M300 545 L300 900 M380 545 L380 900') + d.Lt('M300 610 L380 610 M300 680 L380 680 M300 750 L380 750 M300 820 L380 820') +
    d.grass(905) +
    d.face(440, 405, 140));
})();
