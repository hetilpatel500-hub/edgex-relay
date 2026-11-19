// "My First Robots": 30 friendly robots and robot things, for ages 2-5.
// Drawn from scratch out of big boxes, circles and tubes: no robots from films, shows, toys or games, no logos,
// and nothing that looks like a weapon. The one robot already in Space and the one in Toys are left out.
// Robots come in four groups so the book feels like a set: robot shapes, robot animals, robots with a job,
// and robot things (battery, gear, remote control).
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59',
    GR = '#cfd8dc', DGR = '#90a4ae', W = '#ffffff', PURPLE = '#b39ddb', NAVY = '#5c6bc0', TEAL = '#4dd0c4', LB = '#bfe6ff',
    LG = '#c8f0d4', LY = '#fff1b8', LP = '#e6defa', LT = '#c9f3ee', LO = '#ffe0c2';

  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (arms, springs, handles): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'dark', w = 60) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 26}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const heart = (d, x, y, s, k = 'accent') =>
    d.P(`M${x} ${y + s * 0.9} C${x - s * 1.25} ${y + s * 0.05} ${x - s * 0.75} ${y - s * 0.85} ${x} ${y - s * 0.3} C${x + s * 0.75} ${y - s * 0.85} ${x + s * 1.25} ${y + s * 0.05} ${x} ${y + s * 0.9} Z`, k);
  // an antenna: a stalk from (x, y) up by h with a ball on top
  const ant = (d, x, y, h, k = 'accent') => d.L(`M${x} ${y} L${x} ${y - h}`) + d.C(x, y - h - 24, 28, k);
  // a screen with a cute face on it, centred on x, y
  const screen = (d, x, y, w, h, s) => d.R(x - w / 2, y - h / 2, w, h, Math.min(40, h * 0.25), 'light') + d.face(x, y - s * 0.12, s);
  // two legs and two feet under a body, centred on x
  const legs = (d, x, top, gap = 80, len = 100, k = 'dark') =>
    d.R(x - gap - 35, top, 70, len, 20, k) + d.R(x + gap - 35, top, 70, len, 20, k) +
    d.R(x - gap - 75, top + len - 20, 140, 56, 24) + d.R(x + gap - 65, top + len - 20, 140, 56, 24);
  const stars = (d, pts, k = 'accent2') => pts.map(([cx, cy, r]) => {
    const p = [];
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; p.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
    return d.poly(p, k);
  }).join('');

  // ---------- robot shapes ----------
  A.add('robot', 'Robot', { main: GR, dark: DGR, light: LB, accent: R, accent2: Y, pink: P }, d =>
    ant(d, 500, 150, 60, 'accent') +
    d.R(280, 225, 56, 110, 18, 'accent') + d.R(664, 225, 56, 110, 18, 'accent') +
    tube(d, ['M300 500 L230 690', 'M700 500 L770 690'], 'main', 84) +
    d.C(226, 712, 50, 'accent2') + d.C(774, 712, 50, 'accent2') +
    legs(d, 500, 760, 85, 105) +
    d.R(450, 390, 100, 70, 12, 'dark') +
    d.R(290, 440, 420, 340, 50) +
    d.R(370, 495, 260, 140, 26, 'light') + d.C(430, 565, 26, 'accent') + d.C(500, 565, 26, 'accent2') + d.C(570, 565, 26, 'accent') +
    d.R(400, 675, 200, 50, 20, 'dark') +
    d.R(320, 150, 360, 250, 54) + screen(d, 500, 275, 270, 170, 200));

  A.add('round-robot', 'Round Robot', { main: B, dark: NAVY, light: LB, accent: Y, accent2: R, pink: P }, d =>
    d.L('M430 250 L385 135') + d.C(378, 112, 28, 'accent') + d.L('M570 250 L615 135') + d.C(622, 112, 28, 'accent2') +
    d.R(140, 520, 160, 80, 40, 'dark') + d.R(700, 520, 160, 80, 40, 'dark') + d.C(150, 560, 50, 'accent') + d.C(850, 560, 50, 'accent') +
    d.E(400, 870, 95, 45, 'dark') + d.E(600, 870, 95, 45, 'dark') +
    d.C(500, 560, 320) +
    d.C(500, 480, 175, 'light') + d.face(500, 462, 230) +
    d.C(420, 730, 26, 'accent2') + d.C(500, 752, 26, 'accent') + d.C(580, 730, 26, 'accent2'));

  A.add('tall-robot', 'Tall Robot', { main: G, dark: DG, light: LG, accent: Y, accent2: O, pink: P }, d =>
    d.R(450, 48, 100, 46, 18, 'accent2') +
    tube(d, ['M395 330 L320 610', 'M605 330 L680 610'], 'main', 74) +
    d.C(316, 640, 44, 'dark') + d.C(684, 640, 44, 'dark') +
    d.R(410, 690, 70, 180, 24, 'dark') + d.R(520, 690, 70, 180, 24, 'dark') +
    d.R(365, 850, 130, 54, 24) + d.R(505, 850, 130, 54, 24) +
    d.R(468, 240, 64, 50, 10, 'dark') +
    d.R(380, 280, 240, 430, 44) +
    d.R(415, 335, 170, 60, 18, 'accent') + d.R(415, 425, 170, 60, 18, 'accent2') + d.R(415, 515, 170, 60, 18, 'accent') +
    d.C(500, 640, 28, 'light') +
    d.R(395, 85, 210, 170, 44) + screen(d, 500, 170, 160, 120, 130));

  A.add('balloon-robot', 'Robot with a Balloon', { main: PURPLE, dark: '#7e57c2', light: LP, accent: R, accent2: Y, pink: P }, d =>
    d.L('M735 385 Q700 420 712 452') +
    d.E(740, 225, 125, 155, 'accent') + d.P('M722 378 L758 378 L740 402 Z', 'accent') +
    tube(d, ['M330 520 L262 690'], 'main', 74) + d.C(258, 712, 42, 'accent2') +
    tube(d, ['M575 520 L700 455'], 'main', 74) + d.C(712, 452, 42, 'accent2') +
    legs(d, 450, 700, 62, 100) +
    d.R(420, 425, 60, 50, 10, 'dark') +
    d.R(310, 455, 280, 270, 44) + heart(d, 450, 585, 60, 'accent') +
    ant(d, 450, 230, 52, 'accent2') +
    d.R(320, 230, 260, 210, 50) + screen(d, 450, 335, 196, 140, 160));

  A.add('wheel-robot', 'Robot on Wheels', { main: O, dark: '#e67e22', light: LB, accent: Y, accent2: R, pink: P }, d =>
    ant(d, 500, 175, 52, 'accent2') +
    tube(d, ['M310 470 Q215 490 200 585'], 'dark', 62) + d.C(198, 602, 40, 'accent') +
    tube(d, ['M690 470 Q785 490 800 585'], 'dark', 62) + d.C(802, 602, 40, 'accent') +
    d.R(310, 650, 380, 76, 34, 'dark') +
    d.C(350, 780, 100, 'dark') + d.C(350, 780, 40, 'light') + d.C(650, 780, 100, 'dark') + d.C(650, 780, 40, 'light') +
    d.P('M340 400 Q340 175 500 175 Q660 175 660 400 Z', 'light') + d.face(500, 290, 190) +
    d.R(300, 395, 400, 280, 50) +
    d.R(380, 455, 240, 110, 24, 'accent') + d.C(450, 510, 24, 'accent2') + d.C(550, 510, 24, 'accent2') +
    d.R(420, 600, 160, 40, 16, 'dark'));

  A.add('track-robot', 'Robot with Tracks', { main: '#9ccc65', dark: DGR, light: LG, accent: R, accent2: Y, pink: P }, d =>
    tube(d, ['M345 480 L245 580'], 'main', 70) + d.C(238, 590, 42, 'accent2') +
    tube(d, ['M655 480 L755 580'], 'main', 70) + d.C(762, 590, 42, 'accent2') +
    d.R(470, 380, 60, 60, 10, 'dark') +
    d.R(330, 420, 340, 310, 44) + d.C(430, 520, 30, 'accent') + d.C(500, 520, 30, 'accent2') + d.C(570, 520, 30, 'accent') +
    heart(d, 500, 625, 46, 'accent') +
    d.R(220, 690, 560, 190, 95, 'dark') +
    d.C(320, 785, 52, 'light') + d.C(440, 785, 52, 'light') + d.C(560, 785, 52, 'light') + d.C(680, 785, 52, 'light') +
    d.L('M400 175 L370 120') + d.C(364, 104, 24, 'accent2') + d.L('M600 175 L630 120') + d.C(636, 104, 24, 'accent2') +
    d.R(330, 170, 340, 220, 110) + screen(d, 500, 285, 240, 140, 170));

  A.add('flying-robot', 'Flying Robot', { main: TEAL, dark: '#26a69a', light: LT, accent: Y, accent2: O, pink: P, sky: W }, d =>
    d.R(484, 112, 32, 70, 10, 'dark') +
    d.E(395, 108, 115, 30, 'accent') + d.E(605, 108, 115, 30, 'accent') + d.C(500, 110, 30, 'dark') +
    tube(d, ['M350 410 L215 340', 'M650 410 L785 340'], 'main', 70) +
    d.C(205, 334, 42, 'accent2') + d.C(795, 334, 42, 'accent2') +
    d.E(445, 600, 42, 32, 'dark') + d.E(555, 600, 42, 32, 'dark') +
    d.R(340, 170, 320, 420, 150) + screen(d, 500, 315, 240, 160, 180) +
    d.C(440, 480, 24, 'accent2') + d.C(500, 495, 24, 'accent') + d.C(560, 480, 24, 'accent2') +
    d.P('M220 880 Q180 800 260 790 Q280 715 370 735 Q420 670 500 720 Q580 670 630 735 Q720 715 740 790 Q820 800 780 880 Z', 'sky'));

  A.add('jetpack-robot', 'Jet Pack Robot', { main: R, dark: DGR, light: LB, accent: O, accent2: Y, pink: P }, d =>
    d.P('M285 690 Q325 900 365 690 Z', 'accent') + d.P('M303 690 Q325 820 347 690 Z', 'accent2') +
    d.P('M635 690 Q675 900 715 690 Z', 'accent') + d.P('M653 690 Q675 820 697 690 Z', 'accent2') +
    d.R(275, 400, 100, 300, 44, 'dark') + d.R(625, 400, 100, 300, 44, 'dark') +
    tube(d, ['M360 400 L230 270'], 'main', 68) + d.C(222, 258, 44, 'accent2') +
    tube(d, ['M640 400 L770 270'], 'main', 68) + d.C(778, 258, 44, 'accent2') +
    d.R(405, 650, 66, 110, 20, 'dark') + d.R(529, 650, 66, 110, 20, 'dark') +
    d.R(385, 740, 100, 50, 20) + d.R(515, 740, 100, 50, 20) +
    d.R(340, 355, 320, 310, 50) + d.R(400, 420, 200, 110, 24, 'light') + d.C(455, 475, 22, 'accent') + d.C(545, 475, 22, 'accent2') +
    d.R(420, 580, 160, 40, 16, 'dark') +
    d.R(360, 120, 280, 230, 50) + screen(d, 500, 238, 210, 150, 170));

  A.add('bouncy-robot', 'Bouncy Robot', { main: P, dark: '#f48fb1', light: '#fde4ec', accent: B, accent2: Y, pink: '#ff8fb1' }, d =>
    d.E(500, 875, 135, 38, 'accent') +
    tube(d, ['M500 650 L410 690 L590 730 L410 770 L590 810 L500 850'], 'dark', 46) +
    tube(d, ['M345 450 L250 360'], 'main', 66) + d.C(242, 350, 42, 'accent2') +
    tube(d, ['M655 450 L750 360'], 'main', 66) + d.C(758, 350, 42, 'accent2') +
    d.R(330, 390, 340, 280, 64) + heart(d, 500, 520, 70, 'accent') +
    ant(d, 500, 160, 46, 'accent2') +
    d.R(355, 160, 290, 225, 64) + screen(d, 500, 272, 220, 150, 170) +
    d.L('M200 480 L140 470') + d.L('M210 540 L150 560') + d.L('M800 480 L860 470') + d.L('M790 540 L850 560'));

  // ---------- robot animals ----------
  A.add('robot-dog', 'Robot Dog', { main: GR, dark: DGR, light: LB, accent: R, accent2: Y, pink: P }, d =>
    d.L('M300 500 Q215 440 232 345') + d.C(234, 322, 32, 'accent2') +
    d.R(305, 630, 70, 180, 24, 'dark') + d.R(405, 630, 70, 180, 24, 'dark') +
    d.R(565, 630, 70, 180, 24, 'dark') + d.R(665, 630, 70, 180, 24, 'dark') +
    d.R(290, 790, 100, 50, 20) + d.R(395, 790, 100, 50, 20) + d.R(550, 790, 100, 50, 20) + d.R(655, 790, 100, 50, 20) +
    d.R(280, 440, 470, 220, 90) + d.R(400, 500, 180, 90, 24, 'light') + d.C(445, 545, 20, 'accent') + d.C(535, 545, 20, 'accent2') +
    d.R(615, 185, 66, 120, 24, 'accent') + d.R(775, 185, 66, 120, 24, 'accent') +
    d.R(600, 245, 260, 230, 70) + screen(d, 730, 365, 200, 150, 150));

  A.add('robot-cat', 'Robot Cat', { main: Y, dark: '#f9a825', light: LY, accent: O, accent2: R, pink: P }, d =>
    tube(d, ['M630 730 Q790 730 770 560'], 'dark', 54) + d.C(770, 545, 32, 'accent') +
    d.E(430, 790, 64, 38, 'dark') + d.E(570, 790, 64, 38, 'dark') +
    d.R(360, 440, 280, 340, 70) + d.R(420, 520, 160, 120, 26, 'light') + d.C(465, 580, 22, 'accent') + d.C(535, 580, 22, 'accent2') +
    d.poly([[345, 260], [372, 108], [482, 215]], 'accent') + d.poly([[655, 260], [628, 108], [518, 215]], 'accent') +
    d.R(330, 195, 340, 270, 84) + d.face(500, 325, 210) + d.P('M482 362 L518 362 L500 382 Z', 'accent2') +
    d.L('M370 360 L270 340 M370 395 L270 410 M630 360 L730 340 M630 395 L730 410'));

  A.add('robot-bunny', 'Robot Bunny', { main: W, dark: DGR, light: LB, accent: B, accent2: Y, pink: P }, d =>
    d.R(365, 50, 84, 230, 42) + d.R(387, 85, 40, 160, 20, 'pink') +
    d.R(551, 50, 84, 230, 42) + d.R(573, 85, 40, 160, 20, 'pink') +
    d.E(328, 590, 44, 76, 'dark', 12) + d.E(672, 590, 44, 76, 'dark', -12) +
    d.E(405, 805, 95, 46, 'dark') + d.E(595, 805, 95, 46, 'dark') +
    d.R(350, 470, 300, 320, 84) + d.R(415, 540, 170, 130, 28, 'light') + heart(d, 500, 605, 42, 'accent') +
    d.R(325, 225, 350, 260, 96) + d.face(500, 345, 210) + d.C(500, 395, 18, 'accent'));

  A.add('robot-bird', 'Robot Bird', { main: B, dark: NAVY, light: LB, accent: Y, accent2: O, pink: P }, d =>
    d.poly([[290, 480], [130, 390], [165, 480], [130, 580]], 'accent') +
    d.L('M420 710 L420 820 M380 830 L420 820 L460 830') + d.L('M560 710 L560 820 M520 830 L560 820 L600 830') +
    d.poly([[692, 445], [815, 480], [692, 520]], 'accent2') +
    ant(d, 480, 272, 60, 'accent') +
    d.C(480, 500, 230) + d.face(530, 420, 180) +
    d.E(400, 610, 120, 72, 'light', 18) + d.C(360, 600, 16, 'dark') + d.C(415, 620, 16, 'dark'));

  A.add('robot-fish', 'Robot Fish', { main: O, dark: '#e67e22', light: LB, accent: Y, accent2: R, pink: P, bubble: W }, d =>
    d.poly([[235, 520], [90, 370], [90, 670]], 'accent') +
    d.P('M400 335 Q480 195 600 320 Z', 'accent2') + d.P('M430 700 Q490 800 560 705 Z', 'accent2') +
    d.E(500, 520, 300, 210) +
    d.C(370, 470, 22, 'dark') + d.C(370, 560, 22, 'dark') + d.R(430, 420, 40, 200, 18, 'accent') +
    d.C(640, 470, 88, 'light') + d.eye(652, 470, 38) + d.smile(665, 590, 52, 30) +
    d.C(860, 385, 34, 'bubble') + d.C(895, 290, 24, 'bubble') + d.C(850, 215, 17, 'bubble'));

  A.add('robot-dinosaur', 'Robot Dinosaur', { main: G, dark: DG, light: LG, accent: Y, accent2: O, pink: P }, d =>
    d.P('M260 520 Q140 560 60 740 Q210 680 300 660 Z') +
    d.poly([[255, 470], [290, 380], [340, 440]], 'accent') + d.poly([[340, 420], [385, 320], [440, 400]], 'accent') +
    d.poly([[440, 395], [490, 300], [540, 395]], 'accent') +
    d.R(330, 680, 90, 170, 30, 'dark') + d.R(470, 680, 90, 170, 30, 'dark') +
    d.R(305, 830, 140, 52, 24) + d.R(445, 830, 140, 52, 24) +
    d.R(545, 300, 150, 300, 60) +
    d.E(430, 580, 250, 170) + d.R(330, 560, 180, 80, 22, 'light') + d.C(375, 600, 18, 'accent2') + d.C(465, 600, 18, 'accent') +
    tube(d, ['M640 580 L720 630'], 'dark', 46) +
    d.R(530, 160, 330, 220, 80) + d.face(700, 255, 170));

  A.add('robot-owl', 'Robot Owl', { main: BR, dark: '#8d6e63', light: LY, accent: O, accent2: Y, pink: P }, d =>
    d.R(180, 866, 640, 44, 22, 'dark') +
    d.poly([[288, 320], [292, 165], [405, 262]], 'accent') + d.poly([[712, 320], [708, 165], [595, 262]], 'accent') +
    d.E(262, 600, 62, 150, 'dark', 10) + d.E(738, 600, 62, 150, 'dark', -10) +
    d.E(500, 545, 262, 320) +
    d.C(400, 420, 100, 'light') + d.C(600, 420, 100, 'light') + d.eye(400, 420, 46) + d.eye(600, 420, 46) +
    d.poly([[470, 500], [530, 500], [500, 560]], 'accent2') +
    d.smile(500, 578, 46, 26) +
    d.R(415, 615, 170, 160, 40, 'light') + d.C(460, 695, 22, 'accent') + d.C(540, 695, 22, 'accent') +
    d.E(430, 862, 52, 26, 'accent2') + d.E(570, 862, 52, 26, 'accent2'));

  A.add('robot-turtle', 'Robot Turtle', { main: TEAL, dark: '#26a69a', light: LT, accent: Y, accent2: R, pink: P }, d =>
    d.poly([[175, 640], [90, 680], [180, 700]], 'dark') +
    d.C(300, 720, 74, 'dark') + d.C(300, 720, 28, 'light') + d.C(690, 720, 74, 'dark') + d.C(690, 720, 28, 'light') +
    ant(d, 480, 300, 58, 'accent2') +
    d.P('M190 645 Q190 300 480 300 Q770 300 770 645 Z') +
    d.C(360, 500, 42, 'accent') + d.C(480, 430, 42, 'accent2') + d.C(600, 500, 42, 'accent') +
    d.R(160, 620, 640, 72, 36, 'light') +
    d.R(760, 440, 185, 175, 64) + d.face(852, 515, 120));

  // ---------- robots with a job ----------
  A.add('chef-robot', 'Chef Robot', { main: GR, dark: DGR, light: LB, accent: W, accent2: O, pink: P }, d =>
    d.C(420, 140, 78, 'accent') + d.C(500, 108, 90, 'accent') + d.C(580, 140, 78, 'accent') +
    d.R(385, 160, 230, 92, 22, 'accent') +
    d.R(758, 210, 32, 250, 16, 'accent2') + d.E(774, 210, 56, 76, 'accent2') +
    tube(d, ['M670 545 L770 470'], 'main', 70) + d.C(774, 466, 44) +
    tube(d, ['M330 545 L250 670'], 'main', 70) + d.C(245, 682, 44) +
    legs(d, 500, 775, 85, 100) +
    d.R(455, 455, 90, 50, 10, 'dark') +
    d.R(320, 490, 360, 300, 50) + d.P('M400 520 L600 520 L620 760 L380 760 Z', 'accent') + d.C(500, 640, 26, 'accent2') +
    d.R(345, 250, 310, 220, 50) + screen(d, 500, 360, 230, 150, 170));

  A.add('painter-robot', 'Painter Robot', { main: LB, dark: '#4fa3d8', light: W, accent: R, accent2: Y, pink: P, paint: G }, d =>
    d.R(752, 235, 34, 220, 16, 'accent2') + d.P('M738 240 L800 240 L812 170 Q769 120 726 170 Z', 'dark') +
    d.P('M769 96 Q790 70 769 40 Q748 70 769 96 Z', 'accent') +
    tube(d, ['M670 545 L765 460'], 'main', 70) + d.C(770, 456, 44) +
    tube(d, ['M330 545 L250 640'], 'main', 70) +
    d.P('M90 610 Q110 500 240 520 Q350 535 330 640 Q310 720 220 690 Q170 670 170 720 Q150 760 105 720 Q70 680 90 610 Z', 'light') +
    d.C(160, 590, 24, 'accent') + d.C(230, 570, 24, 'accent2') + d.C(290, 610, 24, 'paint') + d.C(254, 650, 40) +
    legs(d, 500, 775, 85, 100) +
    d.R(455, 455, 90, 50, 10, 'dark') +
    d.R(320, 490, 360, 300, 50) + d.R(390, 555, 220, 130, 26, 'light') + d.C(450, 620, 26, 'accent') + d.C(550, 620, 26, 'paint') +
    d.E(470, 248, 175, 60, 'accent', -6) + d.C(468, 186, 22, 'accent') +
    d.R(345, 250, 310, 220, 50) + screen(d, 500, 362, 230, 150, 170));

  A.add('music-robot', 'Music Robot', { main: PURPLE, dark: '#7e57c2', light: LP, accent: R, accent2: Y, pink: P }, d =>
    d.E(165, 300, 46, 34, 'accent2', -20) + d.L('M205 292 L205 150 Q245 180 240 230') +
    d.E(825, 220, 42, 31, 'accent2', -20) + d.L('M862 213 L862 85 Q900 112 895 158') +
    legs(d, 500, 770, 85, 100) +
    d.R(455, 400, 90, 50, 10, 'dark') +
    d.R(320, 430, 360, 360, 50) +
    tube(d, ['M335 480 L265 420'], 'main', 68) + tube(d, ['M665 480 L735 420'], 'main', 68) +
    d.L('M270 410 L400 300') + d.C(408, 292, 26, 'accent2') + d.L('M730 410 L600 300') + d.C(592, 292, 26, 'accent2') +
    d.C(265, 418, 42) + d.C(735, 418, 42) +
    d.R(360, 560, 280, 200, 26, 'accent') + d.E(500, 560, 140, 38, 'light') +
    d.L('M362 640 L430 740 L500 640 L570 740 L638 640') +
    d.R(345, 180, 310, 230, 50) + screen(d, 500, 295, 230, 150, 170));

  A.add('garden-robot', 'Garden Robot', { main: G, dark: DG, light: LG, accent: B, accent2: Y, pink: P, petal: P }, d =>
    d.L('M800 880 L800 720') + d.E(755, 815, 45, 22, 'dark', -30) + d.E(845, 815, 45, 22, 'dark', 30) +
    d.scallop(800, 690, 52, 6, 40, 'petal') + d.C(800, 690, 40, 'accent2') +
    d.C(880, 560, 14, 'accent') + d.C(905, 615, 14, 'accent') + d.C(860, 615, 14, 'accent') +
    tube(d, ['M705 505 L870 440'], 'accent', 40) +
    d.P('M600 470 Q600 400 660 400 Q720 400 720 470', 'none') +
    d.R(560, 460, 170, 140, 30, 'accent') +
    tube(d, ['M555 520 L590 530'], 'main', 66) +
    tube(d, ['M255 520 L175 640'], 'main', 66) + d.C(170, 652, 42) +
    legs(d, 400, 770, 80, 100) +
    d.R(360, 400, 80, 50, 10, 'dark') +
    d.R(240, 430, 320, 360, 50) + d.R(300, 500, 200, 120, 26, 'light') + d.C(400, 560, 26, 'accent2') +
    d.R(255, 185, 290, 225, 50) + screen(d, 400, 300, 220, 150, 165));

  A.add('cleaning-robot', 'Cleaning Robot', { main: GR, dark: DGR, light: LB, accent: G, accent2: B, pink: P }, d =>
    d.P('M180 560 L180 660 A320 130 0 0 0 820 660 L820 560 Z', 'dark') +
    d.E(500, 560, 320, 130) +
    d.E(500, 560, 230, 88, 'light') + d.face(500, 545, 180) +
    d.C(500, 448, 26, 'accent') +
    stars(d, [[170, 330, 46], [830, 300, 40], [700, 190, 30], [300, 200, 30]]));

  A.add('builder-robot', 'Builder Robot', { main: O, dark: '#e67e22', light: LO, accent: Y, accent2: BR, pink: P, brick: R }, d =>
    d.R(80, 760, 150, 90, 12, 'brick') + d.R(230, 760, 150, 90, 12, 'brick') + d.R(150, 670, 150, 90, 12, 'brick') +
    d.R(758, 300, 40, 240, 18, 'accent2') + d.R(700, 230, 160, 90, 22, 'dark') +
    tube(d, ['M670 545 L770 470'], 'main', 70) + d.C(776, 462, 44) +
    tube(d, ['M340 545 L300 650'], 'main', 70) + d.C(296, 664, 44) +
    legs(d, 520, 775, 85, 100) +
    d.R(475, 455, 90, 50, 10, 'dark') +
    d.R(340, 490, 360, 300, 50) + d.R(410, 555, 220, 130, 26, 'light') + d.C(470, 620, 26, 'accent') + d.C(570, 620, 26, 'brick') +
    d.R(365, 250, 310, 220, 50) + screen(d, 520, 362, 230, 150, 170) +
    d.P('M360 255 Q360 130 520 130 Q680 130 680 255 Z', 'accent') + d.R(330, 235, 380, 40, 18, 'accent'));

  A.add('delivery-robot', 'Delivery Robot', { main: W, dark: DGR, light: LB, accent: R, accent2: Y, pink: P, box: BR }, d =>
    d.L('M730 365 L730 150') + d.P('M730 150 L850 190 L730 230 Z', 'accent') +
    d.R(380, 245, 240, 130, 12, 'box') + d.L('M500 245 L500 375') + d.R(470, 245, 60, 130, 6, 'accent2') +
    d.R(220, 400, 560, 320, 60) + d.R(240, 360, 520, 70, 30, 'accent') +
    screen(d, 500, 560, 400, 170, 200) +
    d.C(310, 765, 70, 'dark') + d.C(310, 765, 25, 'light') + d.C(500, 765, 70, 'dark') + d.C(500, 765, 25, 'light') +
    d.C(690, 765, 70, 'dark') + d.C(690, 765, 25, 'light'));

  // ---------- robot things ----------
  A.add('robot-arm', 'Robot Arm', { main: Y, dark: DGR, light: LB, accent: O, accent2: R, pink: P }, d =>
    tube(d, ['M500 740 L350 450'], 'main', 110) +
    tube(d, ['M350 450 L610 280'], 'main', 96) +
    d.C(770, 185, 64, 'accent2') +
    tube(d, ['M655 245 Q690 150 760 110', 'M668 300 Q760 305 820 240'], 'dark', 44) +
    d.C(350, 450, 72, 'accent') + d.C(625, 270, 56, 'accent') +
    d.C(500, 740, 74, 'accent') +
    d.R(250, 760, 500, 140, 40, 'dark') + screen(d, 500, 830, 330, 100, 130));

  A.add('wind-up-robot', 'Wind-Up Robot', { main: R, dark: '#c62828', light: '#ffe5e5', accent: Y, accent2: B, pink: P }, d =>
    d.R(640, 560, 100, 38, 12, 'dark') + d.E(762, 518, 36, 62, 'accent') + d.E(762, 640, 36, 62, 'accent') + d.C(752, 579, 26, 'dark') +
    tube(d, ['M330 470 L240 345'], 'main', 68) + d.C(232, 332, 42, 'accent2') +
    tube(d, ['M630 470 L720 345'], 'main', 68) + d.C(728, 332, 42, 'accent2') +
    legs(d, 480, 710, 75, 105) +
    d.R(310, 420, 340, 300, 30) +
    d.C(400, 520, 40, 'light') + d.L('M400 520 L400 492') + d.C(480, 520, 40, 'light') + d.L('M480 520 L503 503') +
    d.C(560, 520, 40, 'light') + d.L('M560 520 L588 520') +
    d.R(370, 610, 220, 60, 16, 'accent2') +
    d.L('M380 170 L350 110') + d.C(345, 95, 22, 'accent') + d.L('M580 170 L610 110') + d.C(615, 95, 22, 'accent') +
    d.R(330, 170, 300, 240, 30) + d.face(480, 270, 200));

  A.add('robot-friends', 'Robot Friends', { main: B, dark: NAVY, light: LB, accent: R, accent2: Y, pink: P, two: G }, d =>
    heart(d, 500, 150, 62, 'accent') +
    tube(d, ['M395 530 L500 600'], 'main', 60) + tube(d, ['M605 530 L500 600'], 'two', 60) + d.C(500, 604, 40, 'accent2') +
    tube(d, ['M215 530 L160 650'], 'main', 60) + tube(d, ['M785 530 L840 650'], 'two', 60) +
    d.C(156, 664, 36, 'accent2') + d.C(844, 664, 36, 'accent2') +
    legs(d, 305, 735, 55, 95) + legs(d, 695, 735, 55, 95) +
    d.R(200, 470, 210, 280, 44) + d.C(305, 560, 24, 'accent') + d.C(305, 640, 24, 'accent2') +
    d.R(590, 470, 210, 280, 44, 'two') + heart(d, 695, 590, 40, 'accent') +
    ant(d, 305, 225, 40, 'accent2') + d.C(305, 335, 120) + d.face(305, 322, 150) +
    d.L('M640 240 L620 190') + d.L('M750 240 L770 190') + d.C(618, 176, 18, 'accent') + d.C(772, 176, 18, 'accent') +
    d.R(575, 230, 240, 210, 44, 'two') + d.face(695, 322, 150));

  A.add('battery', 'Battery', { main: G, dark: DGR, light: LG, accent: '#43a36b', accent2: Y, pink: P }, d =>
    d.R(440, 160, 120, 90, 22, 'dark') +
    d.R(330, 225, 340, 620, 64) +
    d.R(346, 600, 308, 229, 50, 'accent') +
    d.P('M480 270 L520 270 L520 310 L560 310 L560 350 L520 350 L520 390 L480 390 L480 350 L440 350 L440 310 L480 310 Z', 'accent2') +
    d.R(450, 725, 100, 34, 12, 'light') +
    d.face(500, 470, 210));

  A.add('gear', 'Gear', { main: GR, dark: DGR, light: LY, accent: O, accent2: Y, pink: P }, d => {
    const N = 10, pts = [];
    for (let k = 0; k < N; k++) {
      const a = k * 2 * Math.PI / N;
      [[-0.17, 300], [-0.11, 375], [0.11, 375], [0.17, 300]].forEach(([o, r]) => pts.push([500 + r * Math.cos(a + o * 1.7), 500 + r * Math.sin(a + o * 1.7)]));
    }
    return d.poly(pts) + d.C(500, 500, 225, 'light') + d.face(500, 470, 260);
  });

  A.add('remote-control', 'Remote Control', { main: B, dark: NAVY, light: LB, accent: R, accent2: Y, pink: P }, d =>
    d.L('M650 345 L725 130') + d.C(730, 110, 30, 'accent') +
    d.R(240, 330, 520, 440, 90) +
    d.C(380, 470, 66, 'dark') + d.C(380, 470, 28, 'accent2') +
    d.C(620, 420, 34, 'accent') + d.C(680, 480, 34, 'accent2') + d.C(560, 480, 34, 'accent2') + d.C(620, 540, 34, 'accent') +
    d.face(500, 640, 180));
})();
