// "My First Birds": 30 big, simple birds for ages 2-5.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#b8c2cc', DG = '#6b7785', W = '#ffffff', PU = '#b39ddb', BK = '#4a4a5a', TE = '#4dd0c4', RD = '#e53950';

  // little helpers
  const legs = (d, xs, y, len = 70) => d.L(xs.map(x => `M${x} ${y} L${x} ${y + len} M${x - 32} ${y + len + 22} L${x} ${y + len} L${x + 32} ${y + len + 22} M${x} ${y + len} L${x + 2} ${y + len + 28}`).join(' '));
  const beakR = (d, x, y, len, h, k = 'accent') => d.P(`M${x} ${y - h} L${x + len} ${y} L${x} ${y + h} Z`, k);
  const beakDown = (d, x, y, w, h, k = 'accent') => d.P(`M${x - w} ${y} L${x + w} ${y} L${x} ${y + h} Z`, k);
  const cheeks = (d, x1, x2, y, r = 26) => d.C(x1, y, r, 'pink') + d.C(x2, y, r, 'pink');
  const branch = (d, y = 880) => d.R(110, y, 780, 56, 28, 'dark') + d.Lt(`M200 ${y + 28} L260 ${y + 28} M640 ${y + 28} L720 ${y + 28}`);

  A.add('owl', 'Owl', { main: BR, dark: DB, light: '#f3e2c7', accent: O, pink: P }, d =>
    branch(d, 880) +
    d.P('M300 330 L300 170 L410 270 Z') + d.P('M700 330 L700 170 L590 270 Z') +
    d.E(500, 570, 260, 320) + d.E(500, 660, 165, 190, 'light') +
    d.C(405, 420, 100, 'light') + d.C(595, 420, 100, 'light') +
    d.eye(405, 420, 36) + d.eye(595, 420, 36) + beakDown(d, 500, 470, 34, 58) +
    d.E(262, 610, 58, 165, 'dark', 12) + d.E(738, 610, 58, 165, 'dark', -12) +
    d.Lt('M440 640 q30 24 60 0 q30 24 60 0 M410 720 q30 24 60 0 q30 24 60 0 q30 24 60 0') +
    d.E(430, 885, 44, 24, 'accent') + d.E(570, 885, 44, 24, 'accent'));

  A.add('chick', 'Chick', { main: Y, accent: O, pink: P }, d =>
    legs(d, [440, 560], 790, 70) +
    d.C(500, 560, 250) + d.L('M470 320 Q470 250 500 305 Q520 240 540 315') +
    d.E(262, 590, 52, 100, 'main', 28) + d.E(738, 590, 52, 100, 'main', -28) +
    d.eye(425, 500, 28) + d.eye(575, 500, 28) +
    d.P('M455 565 L500 540 L545 565 L500 610 Z', 'accent') + d.L('M460 566 L540 566') +
    cheeks(d, 365, 635, 580, 30) + d.grass(950));

  A.add('duck', 'Duck', { main: Y, accent: O, light: W, pink: P }, d =>
    d.water(880) +
    d.P('M220 600 L130 480 L280 540 Z') +
    d.E(605, 510, 80, 100) +
    d.E(440, 650, 260, 170) +
    d.C(640, 390, 135) +
    d.P('M745 375 Q860 365 875 410 Q860 450 750 440 Z', 'accent') + d.L('M760 410 L860 410') +
    d.eye(660, 360, 26) + d.C(610, 430, 26, 'pink') +
    d.P('M280 610 Q420 520 570 610 Q440 730 280 610 Z') + d.Lt('M360 620 Q420 650 480 625'));

  A.add('hen', 'Hen', { main: W, accent: Y, accent2: R, dark: BR, pink: P }, d =>
    legs(d, [420, 520], 790, 80) +
    d.P('M280 570 Q150 480 205 380 Q255 430 290 470 Q235 360 320 330 Q345 420 345 530 Z') +
    d.E(615, 470, 80, 110) + d.E(470, 620, 240, 190) +
    d.P('M590 300 Q600 225 635 268 Q655 210 680 270 Q712 232 718 300 Z', 'accent2') +
    d.C(650, 385, 108) +
    d.P('M705 440 Q730 510 695 510 Q668 478 688 440 Z', 'accent2') +
    beakR(d, 748, 385, 62, 24) + d.eye(672, 360, 24) +
    d.E(450, 620, 135, 88, 'main', -10) + d.Lt('M360 615 Q450 650 540 610 M380 660 Q450 690 520 655'));

  A.add('rooster', 'Rooster', { main: O, dark: '#2f6f5f', accent: '#5aa469', accent2: R, light: Y, pink: P }, d =>
    legs(d, [450, 550], 790, 85) +
    d.P('M310 600 Q110 520 150 270 Q250 400 330 500 Z', 'dark') +
    d.P('M300 560 Q190 400 270 190 Q330 350 350 480 Z', 'accent') +
    d.P('M340 520 Q310 340 410 240 Q410 390 390 500 Z', 'dark') +
    d.E(630, 470, 80, 110, 'light') + d.E(500, 630, 220, 180) +
    d.P('M585 300 Q590 200 630 250 Q650 175 680 250 Q720 190 730 275 Q760 250 745 320 Z', 'accent2') +
    d.C(660, 385, 105, 'light') +
    d.P('M712 445 Q745 530 702 528 Q672 488 692 445 Z', 'accent2') +
    beakR(d, 758, 385, 62, 24, 'light') + d.eye(680, 360, 24) +
    d.E(490, 630, 125, 85, 'accent2', -12));

  A.add('penguin', 'Penguin', { main: BK, light: W, accent: O, pink: P }, d =>
    d.L('M110 905 L890 905') +
    d.E(500, 560, 240, 330) +
    d.E(500, 645, 165, 225, 'light') + d.E(500, 395, 150, 112, 'light') +
    d.eye(440, 380, 28) + d.eye(560, 380, 28) + beakDown(d, 500, 425, 34, 50) + cheeks(d, 405, 595, 445, 22) +
    d.E(268, 580, 50, 165, 'main', 20) + d.E(732, 580, 50, 165, 'main', -20) +
    d.E(425, 890, 64, 26, 'accent') + d.E(575, 890, 64, 26, 'accent'));

  A.add('parrot', 'Parrot', { main: R, accent: Y, accent2: B, light: W, dark: BR, pink: P }, d =>
    d.P('M440 740 L395 965 L470 958 L510 760 Z', 'accent2') +
    branch(d, 780) +
    d.E(500, 560, 150, 235, 'main', 8) +
    d.E(450, 590, 90, 180, 'accent', 14) + d.Lt('M420 640 L480 700 M420 560 L480 620') +
    d.C(545, 320, 125) +
    d.P('M640 290 Q735 290 712 400 Q690 360 645 368 Z', 'light') +
    d.C(565, 300, 42, 'light') + d.eye(568, 300, 20) +
    d.E(470, 795, 34, 20, 'dark') + d.E(545, 795, 34, 20, 'dark'));

  A.add('flamingo', 'Flamingo', { main: '#ff8fb1', light: P, dark: BK, pink: P }, d =>
    d.water(940) +
    d.L('M510 640 L510 925 M510 925 L455 940') + d.L('M560 640 L640 760 L545 780') +
    d.P('M330 560 L230 510 L310 610 Z') +
    d.E(500, 570, 205, 125, 'main', -8) +
    d.P('M620 545 Q735 430 655 330 Q600 260 650 190 L712 212 Q672 268 718 330 Q810 450 690 575 Z') +
    d.C(680, 195, 62) +
    d.P('M735 182 Q812 192 800 255 Q780 232 738 220 Z', 'dark') +
    d.eye(676, 182, 16) +
    d.P('M380 560 Q500 470 610 555 Q500 625 380 560 Z', 'light'));

  A.add('peacock', 'Peacock', { main: TE, accent: G, accent2: B, dark: '#2f6f5f', light: Y, pink: P }, d => {
    let s = '';
    for (let i = 0; i < 9; i++) {
      const a = (195 + i * 18.75) * Math.PI / 180, x = 500 + 285 * Math.cos(a), y = 610 + 285 * Math.sin(a);
      s += d.E(x, y, 72, 140, 'accent', (a * 180 / Math.PI) + 90) + d.C(x + 30 * Math.cos(a), y + 30 * Math.sin(a), 38, 'main') + d.C(x + 30 * Math.cos(a), y + 30 * Math.sin(a), 15, 'dark');
    }
    return s + legs(d, [465, 535], 760, 90) +
      d.E(500, 620, 95, 165, 'accent2') +
      d.Lt('M480 335 L462 268 M500 330 L500 258 M520 335 L538 268') + d.C(462, 262, 13, 'main') + d.C(500, 250, 13, 'main') + d.C(538, 262, 13, 'main') +
      d.C(500, 405, 72, 'accent2') + d.eye(474, 395, 15) + d.eye(526, 395, 15) + beakDown(d, 500, 425, 18, 32, 'light') + d.grass(965);
  });

  A.add('toucan', 'Toucan', { main: BK, light: W, accent: O, accent2: Y, dark: BR, pink: P }, d =>
    d.R(425, 760, 80, 190, 30, 'main') +
    branch(d, 760) +
    d.E(470, 560, 150, 230, 'main', 6) +
    d.Lt('M400 500 Q440 590 410 680') +
    d.C(500, 320, 112) + d.E(505, 425, 92, 70, 'light') +
    d.P('M560 270 Q800 250 855 375 Q765 400 570 392 Z', 'accent') + d.P('M760 266 Q830 290 855 375 Q805 386 770 388 Z', 'accent2') +
    d.C(522, 305, 36, 'accent2') + d.eye(524, 305, 18) +
    d.E(455, 775, 32, 20, 'dark') + d.E(525, 775, 32, 20, 'dark'));

  A.add('swan', 'Swan', { main: W, accent: O, dark: BK, pink: P }, d =>
    d.water(865) +
    d.E(420, 705, 285, 145) +
    d.P('M600 700 Q712 600 646 470 Q594 362 654 280 L724 302 Q674 372 718 462 Q790 616 682 728 Z') +
    d.E(702, 272, 72, 56) +
    d.P('M762 254 L852 292 L762 302 Z', 'accent') + d.eye(708, 260, 16) +
    d.P('M190 690 Q230 470 470 515 Q610 555 630 700 Q420 760 190 690 Z') + d.Lt('M300 640 Q400 600 500 640 M330 690 Q420 660 520 690'));

  A.add('goose', 'Goose', { main: GR, dark: BK, light: W, accent: '#555', pink: P }, d =>
    legs(d, [410, 510], 740, 110) +
    d.P('M230 560 L130 520 L240 640 Z', 'dark') +
    d.P('M545 560 Q585 420 600 285 L692 292 Q690 440 670 590 Z', 'dark') +
    d.E(450, 600, 235, 160) +
    d.E(655, 275, 88, 72, 'dark') + d.P('M620 290 Q650 345 700 320 Q690 290 650 278 Z', 'light') +
    d.P('M732 262 L830 282 L732 312 Z', 'accent') + d.eye(670, 258, 18) +
    d.P('M290 590 Q420 500 560 585 Q440 690 290 590 Z') + d.Lt('M360 600 Q420 630 490 600'));

  A.add('eagle', 'Eagle', { main: BR, light: W, accent: Y, dark: DB, pink: P }, d =>
    d.P('M440 715 L560 715 L610 870 L390 870 Z', 'light') + d.Lt('M450 760 L440 850 M500 760 L500 860 M550 760 L560 850') +
    d.P('M445 460 Q260 300 95 360 Q150 420 115 470 Q205 470 190 525 Q285 515 300 565 Q380 525 455 570 Z') +
    d.P('M555 460 Q740 300 905 360 Q850 420 885 470 Q795 470 810 525 Q715 515 700 565 Q620 525 545 570 Z') +
    d.E(500, 570, 112, 190) +
    d.C(500, 335, 96, 'light') +
    d.P('M466 362 Q500 350 534 362 Q536 432 496 444 Q508 402 470 396 Z', 'accent') +
    d.eye(462, 318, 17) + d.eye(538, 318, 17) +
    d.E(460, 760, 30, 18, 'accent') + d.E(540, 760, 30, 18, 'accent'));

  A.add('robin', 'Robin', { main: BR, accent: O, light: Y, pink: P }, d =>
    legs(d, [450, 550], 790, 70) +
    d.C(500, 560, 245) + d.C(500, 640, 160, 'accent') +
    d.E(270, 600, 52, 130, 'main', 18) + d.E(730, 600, 52, 130, 'main', -18) +
    d.eye(430, 470, 28) + d.eye(570, 470, 28) + d.P('M465 520 L535 520 L500 575 Z', 'light') + cheeks(d, 380, 620, 540, 24) + d.grass(950));

  A.add('bluebird', 'Bluebird', { main: B, accent: O, light: Y, dark: BR, leaf: G, pink: P }, d =>
    branch(d, 800) + d.E(220, 780, 70, 34, 'main', -20) + d.E(790, 780, 70, 34, 'main', 20) +
    d.P('M290 610 L130 560 L180 650 L110 700 L300 680 Z') +
    d.E(470, 610, 220, 170) + d.E(530, 670, 140, 95, 'accent') +
    d.C(630, 450, 122) +
    beakR(d, 745, 450, 66, 24, 'light') + d.eye(660, 425, 24) + d.C(615, 495, 24, 'pink') +
    d.P('M310 600 Q430 520 560 600 Q440 710 310 600 Z') + d.Lt('M380 610 Q440 640 500 612') +
    d.E(450, 800, 30, 18, 'dark') + d.E(540, 800, 30, 18, 'dark'));

  A.add('cardinal', 'Cardinal', { main: RD, dark: BK, accent: O, light: BR, pink: P }, d =>
    branch(d, 820) +
    d.P('M300 640 L120 700 L160 760 L300 700 Z') +
    d.E(460, 620, 205, 175) +
    d.P('M545 345 L565 195 L660 330 Z') +
    d.C(605, 430, 118) +
    d.E(690, 455, 62, 48, 'dark') + beakR(d, 712, 445, 72, 28, 'accent') +
    d.eye(640, 400, 24) +
    d.P('M300 620 Q420 540 545 625 Q430 730 300 620 Z') + d.Lt('M370 630 Q430 660 490 632') +
    d.E(450, 820, 30, 18, 'light') + d.E(530, 820, 30, 18, 'light'));

  A.add('hummingbird', 'Hummingbird', { main: G, light: '#c8f0ff', accent: RD, accent2: PU, leaf: G, pink: P }, d =>
    d.L('M820 470 L820 930') + d.E(760, 700, 70, 32, 'main', -30) + d.E(880, 780, 70, 32, 'main', 30) +
    d.P('M760 470 Q770 330 820 320 Q870 330 880 470 Q820 500 760 470 Z', 'accent2') + d.L('M790 330 L800 440 M850 330 L840 440') +
    d.E(370, 300, 62, 155, 'light', -32) + d.E(310, 340, 52, 130, 'light', -58) +
    d.P('M280 520 L160 610 L260 470 Z') +
    d.E(400, 460, 155, 82, 'main', -25) +
    d.C(530, 380, 72) + d.E(525, 430, 45, 30, 'accent') +
    d.P('M592 362 L770 330 L594 388 Z', 'ink') + d.eye(548, 365, 16));

  A.add('pelican', 'Pelican', { main: W, accent: Y, accent2: O, dark: GR, pink: P }, d =>
    d.water(880) +
    d.E(560, 470, 62, 130) +
    d.P('M220 640 L130 600 L210 700 Z') +
    d.E(420, 660, 235, 165) +
    d.C(600, 330, 85) +
    d.P('M650 360 Q780 480 905 380 L652 352 Z', 'accent2') + d.P('M642 308 L905 380 L652 352 Z', 'accent') +
    d.eye(612, 312, 18) +
    d.P('M260 640 Q400 540 560 630 Q420 740 260 640 Z', 'dark') + d.Lt('M330 650 Q410 680 490 650'));

  A.add('ostrich', 'Ostrich', { main: BK, light: '#f3e2c7', accent: '#e8b27a', pink: P }, d =>
    d.P('M410 580 L385 880 L432 880 L462 580 Z', 'light') + d.P('M505 580 L530 880 L577 880 L552 580 Z', 'light') +
    d.L('M385 880 L350 905 M432 880 L455 905 M530 880 L505 905 M577 880 L610 905') +
    d.scallop(270, 460, 70, 7, 40) +
    d.E(470, 480, 225, 150) +
    d.P('M585 420 Q600 300 600 170 L652 170 Q650 300 640 440 Z', 'light') +
    d.E(632, 160, 66, 50, 'light') +
    d.P('M690 150 L770 172 L690 190 Z', 'accent') + d.eye(640, 145, 20) + d.Lt('M626 124 L620 110 M640 122 L640 106 M654 124 L660 110') +
    d.P('M380 470 Q470 400 570 470 Q480 560 380 470 Z') + d.grass(925));

  A.add('stork', 'Stork', { main: W, dark: BK, accent: RD, pink: P }, d =>
    d.L('M450 560 L440 880 M440 880 L405 905 M440 880 L470 905 M520 560 L530 880 M530 880 L495 905 M530 880 L565 905') +
    d.P('M285 470 L150 430 L205 520 Z', 'dark') +
    d.E(460, 480, 205, 115, 'main', -8) +
    d.P('M560 440 Q620 330 600 230 L660 220 Q690 340 620 460 Z') +
    d.C(640, 220, 58) +
    d.P('M690 210 L890 268 L690 240 Z', 'accent') + d.eye(648, 206, 16) +
    d.P('M330 470 Q460 400 590 460 Q470 540 330 470 Z', 'dark') + d.Lt('M380 470 Q460 500 540 470') + d.grass(925));

  A.add('puffin', 'Puffin', { main: BK, light: W, accent: O, accent2: RD, pink: P }, d =>
    d.L('M110 905 L890 905') +
    d.E(500, 580, 225, 305) + d.E(500, 650, 150, 215, 'light') +
    d.E(500, 380, 135, 112, 'light') +
    d.eye(448, 365, 24) + d.eye(552, 365, 24) +
    d.P('M452 405 L548 405 L500 515 Z', 'accent') + d.P('M462 405 L538 405 L520 448 L480 448 Z', 'accent2') +
    cheeks(d, 410, 590, 430, 20) +
    d.E(285, 600, 50, 160, 'main', 18) + d.E(715, 600, 50, 160, 'main', -18) +
    d.E(430, 890, 60, 26, 'accent') + d.E(570, 890, 60, 26, 'accent'));

  A.add('seagull', 'Seagull', { main: GR, light: W, accent: Y, accent2: R, dark: BR, pink: P }, d =>
    d.R(380, 720, 210, 250, 22, 'dark') + d.Lt('M430 780 L430 940 M540 780 L540 940') +
    d.L('M440 640 L440 722 M520 640 L520 722') +
    d.P('M280 560 L150 520 L230 610 Z', 'light') +
    d.E(470, 560, 215, 120, 'light') +
    d.C(645, 420, 88, 'light') +
    beakR(d, 725, 430, 80, 22, 'accent') + d.C(778, 438, 10, 'accent2') + d.eye(660, 400, 20) +
    d.P('M290 540 Q430 450 580 530 Q460 620 290 540 Z'));

  A.add('crow', 'Crow', { main: BK, accent: GR, dark: DG, pink: P }, d =>
    legs(d, [440, 530], 760, 90) +
    d.P('M280 620 L120 680 L170 730 L300 690 Z') +
    d.E(460, 600, 220, 155, 'main', -8) +
    d.C(635, 410, 108) +
    d.P('M720 380 Q820 400 835 430 Q800 450 720 450 Z', 'accent') + d.L('M725 415 L830 430') + d.eye(655, 385, 24) +
    d.P('M300 590 Q430 500 570 590 Q440 700 300 590 Z') + d.Lt('M370 600 Q430 630 500 600') + d.grass(960));

  A.add('woodpecker', 'Woodpecker', { main: BK, light: W, accent: RD, dark: BR, accent2: GR, pink: P }, d =>
    d.R(620, 40, 250, 920, 40, 'dark') + d.Lt('M680 120 L680 260 M800 300 L800 450 M690 640 L690 820 M810 760 L810 900') + d.E(760, 610, 38, 54, 'ink') +
    d.P('M420 700 L400 900 L470 900 L500 720 Z') +
    d.E(495, 530, 112, 205, 'main', -8) + d.E(520, 570, 62, 150, 'light', -8) +
    d.C(530, 310, 92, 'light') +
    d.P('M450 285 Q462 200 556 206 Q622 226 612 292 Q540 250 450 285 Z', 'accent') +
    d.P('M612 300 L686 312 L612 332 Z', 'accent2') + d.eye(560, 300, 20) +
    d.E(600, 650, 26, 16, 'accent2') + d.E(600, 720, 26, 16, 'accent2'));

  A.add('turkey', 'Turkey', { main: BR, light: '#e8b27a', accent: O, accent2: Y, dark: DB, red: R, pink: P }, d => {
    let s = '';
    const ks = ['accent', 'accent2', 'dark', 'accent', 'accent2', 'dark', 'accent', 'accent2', 'dark'];
    for (let i = 0; i < 9; i++) {
      const a = (190 + i * 20) * Math.PI / 180;
      s += d.E(500 + 250 * Math.cos(a), 600 + 250 * Math.sin(a), 70, 150, ks[i], (a * 180 / Math.PI) + 90);
    }
    return s + legs(d, [455, 545], 800, 80) +
      d.E(500, 630, 170, 195) +
      d.C(500, 385, 82, 'light') +
      beakDown(d, 500, 405, 22, 38, 'accent2') + d.P('M512 430 Q545 500 515 520 Q492 490 500 430 Z', 'accent') +
      d.eye(470, 370, 17) + d.eye(530, 370, 17) +
      d.Lt('M430 620 q35 26 70 0 q35 26 70 0 M445 700 q28 22 55 0 q28 22 55 0') + d.grass(960);
  });

  A.add('kiwi', 'Kiwi', { main: BR, accent: '#e8b27a', light: '#f3e2c7', pink: P }, d =>
    d.P('M400 720 L385 860 L430 860 L445 720 Z', 'accent') + d.P('M530 720 L545 860 L590 860 L575 720 Z', 'accent') +
    d.L('M385 860 L350 885 M430 860 L455 885 M545 860 L520 885 M590 860 L622 885') +
    d.E(460, 560, 255, 200) +
    d.C(670, 470, 95) +
    d.P('M752 470 Q860 560 872 730 L850 734 Q830 590 744 505 Z', 'accent') +
    d.eye(690, 445, 20) + d.C(650, 505, 22, 'pink') +
    d.Lt('M300 500 L330 520 M380 450 L410 470 M300 600 L330 620 M420 560 L450 580 M520 470 L550 490 M500 640 L530 660 M360 690 L390 710') + d.grass(910));

  A.add('dove', 'Dove', { main: W, accent: '#f7a8b8', leaf: G, dark: GR, pink: P }, d =>
    d.P('M420 470 Q360 250 520 140 Q545 330 565 470 Z') +
    d.P('M300 540 L130 500 L160 560 L110 610 L290 600 Z') +
    d.E(470, 530, 205, 112, 'main', -10) +
    d.C(655, 430, 82) +
    beakR(d, 728, 440, 52, 18, 'accent') + d.eye(668, 410, 18) +
    d.L('M772 450 Q820 520 800 600') + d.E(760, 520, 34, 16, 'main', 60) + d.E(838, 545, 34, 16, 'main', -50) + d.E(782, 585, 34, 16, 'main', 70) +
    d.P('M330 520 Q340 330 520 260 Q560 400 560 520 Q450 580 330 520 Z') + d.Lt('M400 470 Q450 400 520 380 M420 510 Q470 460 530 450'));

  A.add('bird-nest', 'Bird Nest', { main: BR, dark: DB, light: '#cfe9ff', accent: '#9ad1ff', pink: P }, d =>
    d.R(110, 800, 780, 56, 28, 'dark') +
    d.E(500, 520, 300, 90, 'dark') +
    d.E(395, 500, 70, 92, 'light', -15) + d.E(500, 470, 72, 98, 'accent') + d.E(605, 500, 70, 92, 'light', 15) +
    d.P('M200 520 Q210 770 500 790 Q790 770 800 520 Q650 600 500 600 Q350 600 200 520 Z') +
    d.Lt('M240 600 Q500 700 760 600 M270 680 Q500 760 730 680 M330 560 L380 760 M500 610 L500 780 M670 560 L620 760'));

  A.add('birdhouse', 'Birdhouse', { main: '#ffe08a', accent: R, dark: BR, light: B, pink: P }, d =>
    d.R(460, 640, 80, 290, 10, 'dark') +
    d.R(300, 330, 400, 330, 20) +
    d.P('M255 350 L500 145 L745 350 Z', 'accent') + d.Lt('M330 290 L670 290') +
    d.C(500, 450, 62, 'ink') +
    d.L('M500 560 L500 600') + d.C(500, 560, 10, 'ink') +
    d.E(640, 225, 52, 40, 'light') + d.C(672, 195, 34, 'light') + beakR(d, 702, 196, 28, 10, 'main') + d.eye(680, 188, 9) +
    d.grass(950));

  A.add('hatching-chick', 'Hatching Chick', { main: Y, light: W, accent: O, pink: P }, d =>
    d.C(500, 470, 175) +
    d.P('M375 330 Q500 230 625 330 L595 362 L555 322 L500 365 L445 322 L405 362 Z', 'light') +
    d.eye(440, 425, 26) + d.eye(560, 425, 26) +
    d.P('M462 465 L500 445 L538 465 L500 505 Z', 'accent') + cheeks(d, 392, 608, 478, 22) +
    d.P('M250 570 L320 510 L390 580 L460 510 L530 580 L600 510 L670 580 L750 520 Q770 885 500 885 Q230 885 250 570 Z', 'light') +
    d.grass(950));
})();
