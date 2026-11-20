// "My First Winter": 30 friendly snow-day things and winter animals for ages 2-5.
// Generic subjects only: no brands, logos or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const W = '#ffffff', LB = '#d7f0ff', B = '#6ec6ff', R = '#ff6b6b', Y = '#ffd23f', O = '#ff9f43', G = '#7bd389',
    BR = '#c68b59', DB = '#8d5a3b', GR = '#cfd8dc', SL = '#90a4ae', P = '#ffb3c7', PU = '#b39ddb', NV = '#3d4a5c', T = '#4db6ac';

  const f = v => v.toFixed(1);
  const g = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // a six-armed snowflake of radius s with a little disc in the middle
  const flake = (d, x, y, s) => {
    let p = '';
    for (let i = 0; i < 3; i++) {
      const a = i * Math.PI / 3 + Math.PI / 2, c = Math.cos(a) * s, sn = Math.sin(a) * s;
      p += `M${f(x - c)} ${f(y - sn)} L${f(x + c)} ${f(y + sn)} `;
    }
    for (let i = 0; i < 6; i++) {
      const a = i * Math.PI / 3 + Math.PI / 2, bx = x + Math.cos(a) * s * 0.6, by = y + Math.sin(a) * s * 0.6;
      const tip = (da) => `${f(bx + Math.cos(a + da) * s * 0.3)} ${f(by + Math.sin(a + da) * s * 0.3)}`;
      p += `M${tip(2.4)} L${f(bx)} ${f(by)} L${tip(-2.4)} `;
    }
    return d.Lt(p) + d.C(x, y, s * 0.16, 'light');
  };
  // a puffy cloud w wide, centred on cx,cy
  const cloud = (d, cx, cy, w, k = 'main') => {
    const p = (x, y) => `${f(cx + x * w)} ${f(cy + y * w)}`;
    return d.P(`M${p(-0.46, 0.19)} A1 1 0 0 1 ${p(-0.33, -0.05)} A1 1 0 0 1 ${p(-0.02, -0.28)} A1 1 0 0 1 ${p(0.3, -0.1)} A1 1 0 0 1 ${p(0.46, 0.19)} Q${p(0, 0.27)} ${p(-0.46, 0.19)} Z`, k);
  };
  // a soft snow mound along the bottom
  const snowGround = (d, y = 880, k = 'light') => d.P(`M60 940 L60 ${y} Q280 ${y - 50} 500 ${y} Q720 ${y + 40} 940 ${y - 10} L940 940 Z`, k);

  // ---------------- snow play ----------------
  A.add('snowman', 'Snowman', { main: W, accent: R, accent2: O, dark: B, light: Y, pink: P }, d =>
    d.L('M360 520 L190 420 M240 450 L215 370 M240 450 L170 455') + d.L('M640 520 L810 420 M760 450 L785 370 M760 450 L830 455') +
    d.C(500, 745, 195) + d.C(500, 490, 150) +
    d.C(500, 450, 17, 'ink') + d.C(500, 520, 17, 'ink') + d.C(500, 590, 17, 'ink') +
    d.C(500, 270, 120) +
    d.R(385, 365, 230, 50, 25, 'accent') + d.R(545, 380, 52, 130, 22, 'accent') +
    d.P('M392 225 Q392 120 500 116 Q608 120 608 225 Z', 'dark') + d.R(380, 205, 240, 48, 22, 'dark') + d.C(500, 108, 36, 'light') +
    d.eye(455, 282, 19) + d.eye(545, 282, 19) +
    d.poly([[492, 300], [598, 318], [492, 336]], 'accent2') +
    d.dot(450, 350, 9) + d.dot(478, 360, 9) + d.dot(522, 360, 9) + d.dot(550, 350, 9));

  A.add('igloo', 'Igloo', { main: W, dark: NV, light: LB, pink: P }, d =>
    d.L('M70 800 L930 800') +
    d.P('M150 800 A350 350 0 0 1 850 800 Z') +
    d.Lt('M165 720 L835 720 M220 590 L780 590') +
    d.Lt('M300 720 L300 800 M470 720 L470 800 M260 590 L260 720 M560 590 L560 720 M400 450 L400 590 M610 470 L610 590') +
    d.P('M610 800 L610 700 A70 70 0 0 1 750 700 L750 800 Z', 'dark') +
    d.face(400, 640, 150));

  A.add('snowballs', 'Snowballs', { main: W, pink: P }, d =>
    snowGround(d, 870) +
    d.C(330, 700, 150) + d.C(670, 700, 150) + d.C(500, 470, 150) +
    d.face(330, 700, 140) + d.face(670, 700, 140) + d.face(500, 470, 150));

  A.add('snow-fort', 'Snow Fort', { main: W, accent: R, dark: BR, light: LB, pink: P }, d =>
    d.L('M775 400 L775 225') + d.poly([[775, 225], [880, 262], [775, 300]], 'accent') +
    d.R(150, 390, 150, 120, 16) + d.R(425, 390, 150, 120, 16) + d.R(700, 390, 150, 120, 16) +
    d.R(150, 470, 700, 380, 24) +
    d.Lt('M150 560 L330 560 M670 560 L850 560 M150 760 L850 760 M150 660 L330 660 M670 660 L850 660') +
    d.Lt('M240 470 L240 560 M760 470 L760 560 M300 760 L300 850 M500 760 L500 850 M700 760 L700 850 M240 560 L240 660 M760 560 L760 660') +
    d.face(500, 620, 210) +
    d.C(160, 885, 48, 'light') + d.C(255, 895, 40, 'light') + d.C(205, 835, 40, 'light'));

  A.add('snow-angel', 'Snow Angel', { main: B, accent: R, dark: NV, light: LB, accent2: Y, skin: '#f1d3b3', pink: P }, d =>
    d.E(290, 400, 185, 115, 'light', -30) + d.E(710, 400, 185, 115, 'light', 30) +
    d.P('M310 905 L690 905 L570 560 L430 560 Z', 'light') +
    d.E(445, 735, 42, 120, 'main', 12) + d.E(555, 735, 42, 120, 'main', -12) +
    d.E(425, 850, 58, 36, 'dark') + d.E(575, 850, 58, 36, 'dark') +
    d.E(335, 395, 120, 42, 'main', 32) + d.E(665, 395, 120, 42, 'main', -32) +
    d.C(230, 330, 42, 'accent') + d.C(770, 330, 42, 'accent') +
    d.R(410, 430, 180, 250, 70) +
    d.C(500, 340, 95, 'skin') +
    d.P('M408 305 Q408 225 500 222 Q592 225 592 305 Z', 'accent') + d.R(398, 290, 204, 38, 19, 'accent2') + d.C(500, 212, 26, 'accent2') +
    d.face(500, 365, 120));

  // ---------------- sliding and gliding ----------------
  A.add('skis', 'Skis', { main: R, accent: B, dark: NV, light: Y, pink: P }, d => {
    const ski = (x) => d.P(`M${x} 880 L${x} 230 Q${x} 120 ${x + 60} 110 Q${x + 120} 120 ${x + 120} 230 L${x + 120} 880 Q${x + 120} 900 ${x + 100} 900 L${x + 20} 900 Q${x} 900 ${x} 880 Z`) +
      d.R(x - 12, 560, 144, 70, 20, 'dark') + d.face(x + 60, 330, 100);
    const pole = (x1, x2) => d.L(`M${x1} 160 L${x2} 880`) + d.R(x1 - 22, 110, 44, 110, 20, 'light') + d.C(x2 - 2, 830, 34, 'accent');
    return pole(195, 225) + pole(805, 775) + ski(300) + ski(580);
  });

  A.add('snowboard', 'Snowboard', { main: PU, accent: Y, dark: NV, pink: P }, d =>
    g(d.R(150, 410, 700, 180, 90) + d.Lt('M235 440 L235 560 M765 440 L765 560') +
      d.R(275, 445, 90, 110, 22, 'dark') + d.R(635, 445, 90, 110, 22, 'dark') + d.face(500, 490, 160), -25) +
    flake(d, 230, 230, 70) + flake(d, 780, 770, 60));

  A.add('snow-tube', 'Snow Tube', { main: B, accent: Y, light: LB, pink: P }, d =>
    snowGround(d, 880) +
    d.P('M150 540 Q90 540 95 470 Q100 420 160 430') + d.P('M850 540 Q910 540 905 470 Q900 420 840 430') +
    d.E(500, 580, 370, 240) + d.E(500, 500, 165, 75, 'light') +
    d.Lt('M190 520 Q230 470 300 450 M810 520 Q770 470 700 450') +
    d.face(500, 690, 190));

  A.add('ski-lift', 'Ski Lift', { main: Y, accent: R, dark: NV, light: B, pink: P }, d =>
    d.L('M60 200 L940 120') +
    d.P('M60 940 L60 860 Q260 760 500 850 Q720 930 940 820 L940 940 Z', 'light') +
    d.R(470, 140, 60, 60, 14, 'dark') + d.L('M500 200 L500 400') +
    d.L('M330 460 L330 400 L670 400 L670 460') +
    d.R(320, 420, 360, 210, 34) + d.R(290, 610, 420, 70, 30, 'accent') +
    d.L('M330 680 L330 760 L670 760 L670 680') +
    d.face(500, 510, 170));

  A.add('snowmobile', 'Snowmobile', { main: R, accent: NV, dark: SL, light: LB, pink: P }, d =>
    d.L('M60 875 L940 875') +
    d.R(220, 720, 480, 125, 62, 'dark') +
    d.C(290, 782, 40, W) + d.C(405, 782, 40, W) + d.C(520, 782, 40, W) + d.C(635, 782, 40, W) +
    d.L('M600 500 L690 470') +
    d.P('M610 565 L655 410 L735 430 L715 565 Z', 'light') +
    d.R(760, 730, 28, 110, 10, 'accent') + d.L('M640 850 L880 850 Q950 850 935 790') +
    d.P('M190 750 L190 640 Q205 560 320 560 L620 560 Q770 560 870 680 Q890 745 820 750 Z') +
    d.R(250, 505, 280, 75, 37, 'accent') +
    d.face(470, 655, 170));

  // ---------------- clearing snow ----------------
  A.add('snowplow', 'Snowplow', { main: Y, accent: O, accent2: R, dark: NV, light: LB, pink: P }, d =>
    d.L('M60 840 L940 840') +
    d.R(580, 345, 140, 38, 16, 'accent2') +
    d.R(520, 375, 265, 330, 30, 'accent') + d.R(560, 415, 165, 120, 20, 'light') +
    d.R(130, 460, 400, 245, 30) +
    d.R(780, 630, 60, 40, 10, 'dark') +
    d.P('M820 500 Q895 600 870 800 L940 810 Q965 640 870 485 Z', 'dark') +
    d.C(300, 760, 82, 'dark') + d.C(300, 760, 32, W) + d.C(660, 760, 82, 'dark') + d.C(660, 760, 32, W) +
    d.face(330, 570, 190));

  A.add('snow-shovel', 'Snow Shovel', { main: B, dark: BR, light: W, pink: P }, d =>
    d.R(470, 150, 60, 480, 28, 'dark') +
    d.R(395, 80, 210, 100, 46, 'dark') + d.R(440, 108, 120, 44, 22, 'light') +
    d.P('M250 640 L750 640 L790 900 Q500 950 210 900 Z') +
    d.R(435, 605, 130, 70, 22, 'dark') +
    d.face(500, 790, 190));

  A.add('icicles', 'Icicles', { main: LB, dark: BR, light: W, pink: P }, d => {
    const ice = (x1, x2, tip) => d.P(`M${x1} 255 L${(x1 + x2) / 2} ${tip} L${x2} 255 Z`);
    return d.P('M70 175 Q150 95 250 150 Q350 85 450 150 Q550 85 650 150 Q750 85 850 150 Q935 110 930 200 L70 200 Z', 'light') +
      d.R(70, 190, 860, 80, 20, 'dark') +
      ice(110, 230, 520) + ice(250, 360, 680) + ice(380, 620, 920) + ice(640, 750, 700) + ice(770, 890, 540) +
      d.face(500, 395, 160);
  });

  A.add('snow-cloud', 'Snow Cloud', { main: GR, light: LB, pink: P }, d =>
    flake(d, 260, 720, 62) + flake(d, 500, 800, 70) + flake(d, 740, 720, 62) + flake(d, 380, 900, 45) + flake(d, 620, 900, 45) +
    cloud(d, 500, 390, 700) + d.face(500, 410, 210));

  A.add('thermometer', 'Thermometer', { main: W, accent: R, light: LB, pink: P }, d =>
    d.R(430, 120, 140, 620, 70) +
    d.Lt('M570 220 L615 220 M570 300 L600 300 M570 380 L615 380 M570 460 L600 460 M570 540 L615 540') +
    d.R(470, 560, 60, 200, 30, 'accent') +
    d.C(500, 765, 135, 'accent') + d.face(500, 770, 175) +
    flake(d, 245, 300, 85) + flake(d, 780, 640, 70));

  // ---------------- warm and cozy ----------------
  A.add('snow-boots', 'Snow Boots', { main: BR, accent: W, dark: NV, pink: P }, d => {
    const boot = x0 => d.P(`M${x0} 300 L${x0 + 170} 300 L${x0 + 170} 600 Q${x0 + 170} 640 ${x0 + 215} 650 Q${x0 + 320} 670 ${x0 + 320} 760 L${x0 + 320} 800 Q${x0 + 320} 830 ${x0 + 290} 830 L${x0 + 30} 830 Q${x0} 830 ${x0} 800 Z`) +
      d.R(x0 - 6, 790, 332, 58, 24, 'dark') +
      d.C(x0 + 5, 290, 42, 'accent') + d.C(x0 + 60, 275, 42, 'accent') + d.C(x0 + 115, 275, 42, 'accent') + d.C(x0 + 168, 290, 42, 'accent') +
      d.R(x0 - 12, 280, 194, 50, 25, 'accent') +
      d.face(x0 + 85, 450, 120) + d.Lt(`M${x0 + 175} 690 L${x0 + 215} 670 M${x0 + 195} 720 L${x0 + 245} 700`);
    return boot(130) + boot(520);
  });

  A.add('snowsuit', 'Snowsuit', { main: T, accent: R, dark: NV, light: W, skin: '#f1d3b3', pink: P }, d =>
    d.R(330, 640, 160, 240, 60) + d.R(510, 640, 160, 240, 60) +
    d.Lt('M335 730 Q410 750 485 730 M515 730 Q590 750 665 730') +
    d.R(300, 840, 200, 80, 40, 'dark') + d.R(500, 840, 200, 80, 40, 'dark') +
    d.E(250, 500, 70, 190, 'main', 25) + d.E(750, 500, 70, 190, 'main', -25) +
    d.C(175, 672, 55, 'accent') + d.C(825, 672, 55, 'accent') +
    d.P('M330 330 Q500 300 670 330 L705 700 Q500 735 295 700 Z') +
    d.Lt('M305 560 Q400 580 470 565 M530 565 Q600 580 695 560') +
    d.C(500, 230, 135) + d.scallop(500, 232, 98, 12, 38, 'light') + d.C(500, 236, 84, 'skin') +
    d.face(500, 245, 112) +
    d.Lt('M500 380 L500 700') + d.R(487, 400, 26, 38, 8, 'accent'));

  A.add('blanket', 'Cozy Blanket', { main: R, accent: B, light: Y, pink: P }, d =>
    d.P('M170 600 L760 600 Q830 600 830 685 Q830 770 760 770 L170 770 Z', 'accent') +
    d.Lt('M300 615 L300 770 M420 615 L420 770 M540 615 L540 770 M660 615 L660 770') +
    d.Lt('M170 640 L130 640 M170 690 L130 690 M170 740 L130 740') +
    d.P('M150 400 L770 400 Q850 400 850 505 Q850 610 770 610 L150 610 Z') +
    d.C(240, 455, 18, 'light') + d.C(240, 560, 18, 'light') + d.C(320, 505, 18, 'light') + d.C(655, 455, 18, 'light') + d.C(655, 560, 18, 'light') + d.C(745, 505, 18, 'light') +
    d.Lt('M150 430 L110 430 M150 480 L110 480 M150 530 L110 530 M150 580 L110 580') +
    d.face(480, 500, 180));

  A.add('fireplace', 'Fireplace', { main: R, dark: BR, accent: Y, accent2: O, light: SL, pink: P }, d =>
    d.R(180, 270, 640, 600, 20) +
    d.Lt('M180 350 L820 350 M180 520 L300 520 M700 520 L820 520 M180 690 L300 690 M700 690 L820 690') +
    d.Lt('M330 270 L330 350 M500 270 L500 350 M670 270 L670 350 M240 350 L240 520 M760 350 L760 520 M240 690 L240 870 M760 690 L760 870') +
    d.P('M300 870 L300 570 Q300 430 500 430 Q700 430 700 570 L700 870 Z', 'light') +
    d.R(350, 830, 300, 45, 22, 'dark') +
    d.P('M380 820 Q330 720 380 640 Q400 700 430 700 Z', 'accent2') + d.P('M620 820 Q670 720 620 640 Q600 700 570 700 Z', 'accent2') +
    d.P('M500 500 C410 610 360 700 380 780 C400 845 600 845 620 780 C640 700 590 610 500 500 Z', 'accent') +
    d.face(500, 735, 140) +
    d.R(140, 200, 720, 80, 20, 'dark'));

  A.add('hot-soup', 'Hot Soup', { main: B, accent: Y, accent2: O, dark: SL, light: W, pink: P }, d =>
    d.L('M380 400 Q340 340 380 290 Q420 240 380 180 M500 400 Q460 330 500 270 Q540 210 500 140 M620 400 Q580 340 620 290 Q660 240 620 180') +
    d.R(400, 790, 200, 55, 22) +
    d.P('M190 520 Q205 810 500 830 Q795 810 810 520 Z') +
    d.E(500, 520, 310, 72, 'accent') + d.C(400, 515, 22, 'accent2') + d.C(470, 540, 18, 'accent2') + d.C(560, 505, 20, 'accent2') + d.C(650, 530, 18, 'accent2') +
    d.R(615, 400, 50, 140, 22, 'dark') +
    d.face(500, 650, 200));

  A.add('bird-feeder', 'Bird Feeder', { main: R, dark: BR, accent: Y, light: W, pink: P }, d =>
    d.L('M500 60 L500 200') +
    d.R(340, 320, 320, 360, 20) +
    d.R(400, 560, 200, 85, 20, 'light') + d.dot(445, 610, 10) + d.dot(480, 595, 10) + d.dot(520, 615, 10) + d.dot(555, 600, 10) +
    d.poly([[270, 340], [500, 180], [730, 340]], 'dark') +
    d.P('M290 330 Q330 270 400 290 Q450 230 520 265 Q580 225 640 280 Q700 270 712 330 Z', 'light') +
    d.R(290, 670, 420, 55, 22, 'dark') +
    d.L('M500 725 L500 820') + d.L('M420 820 L580 820') +
    d.face(500, 440, 180));

  // ---------------- winter animals ----------------
  A.add('chickadee', 'Chickadee', { main: SL, dark: NV, light: '#fff3d6', accent: O, branch: BR, snow: W, pink: P }, d =>
    d.R(100, 805, 800, 50, 25, 'branch') + d.P('M110 810 Q200 760 300 805 Q420 770 520 805 Q650 765 760 805 Q850 780 890 810 Z', 'snow') +
    d.L('M450 780 L440 830 M550 780 L560 830') +
    d.P('M700 660 L880 690 Q892 720 872 748 L695 738 Z', 'main') +
    d.C(500, 560, 240, 'light') +
    d.P('M278 470 A240 240 0 0 1 722 470 Q500 420 278 470 Z', 'dark') +
    d.E(285, 620, 55, 130, 'main', 15) + d.E(715, 620, 55, 130, 'main', -15) +
    d.P('M430 640 Q500 730 570 640 Q500 615 430 640 Z', 'dark') +
    d.eye(430, 530, 26) + d.eye(570, 530, 26) + d.P('M478 575 L522 575 L500 610 Z', 'accent') +
    d.C(375, 585, 22, 'pink') + d.C(625, 585, 22, 'pink'));

  A.add('snowy-owl', 'Snowy Owl', { main: W, dark: NV, accent: Y, light: LB, pink: P }, d =>
    d.P('M140 900 Q500 760 860 900 Z', 'light') +
    d.E(500, 560, 245, 300) +
    d.E(285, 620, 60, 160, 'main', 12) + d.E(715, 620, 60, 160, 'main', -12) +
    d.Lt('M245 560 L265 575 L285 560 M250 650 L270 665 L290 650 M715 560 L735 575 L755 560 M710 650 L730 665 L750 650') +
    d.Lt('M420 660 L440 675 L460 660 M540 660 L560 675 L580 660 M470 740 L490 755 L510 740 M420 800 L440 815 L460 800 M540 800 L560 815 L580 800') +
    d.C(410, 430, 78, 'accent') + d.C(590, 430, 78, 'accent') + d.eye(410, 435, 40) + d.eye(590, 435, 40) +
    d.P('M472 500 L528 500 L500 552 Z', 'dark') +
    d.C(430, 855, 28) + d.C(475, 862, 28) + d.C(525, 862, 28) + d.C(570, 855, 28));

  A.add('arctic-fox', 'Arctic Fox', { main: W, light: LB, pink: P }, d =>
    d.P('M610 820 Q930 810 900 560 Q880 470 790 520 Q830 700 610 700 Z') +
    d.E(500, 795, 170, 125) + d.E(440, 905, 52, 30) + d.E(560, 905, 52, 30) +
    d.P('M425 640 Q450 730 500 705 Q550 730 575 640 Z', 'light') +
    d.E(355, 300, 60, 80, 'main', -22) + d.E(645, 300, 60, 80, 'main', 22) +
    d.E(360, 310, 28, 45, 'pink', -22) + d.E(640, 310, 28, 45, 'pink', 22) +
    d.P('M290 400 Q320 580 500 660 Q680 580 710 400 Q500 300 290 400 Z') +
    d.E(500, 615, 30, 22, 'ink') + d.L('M500 637 L500 652 M470 650 Q485 665 500 652 Q515 665 530 650') +
    d.eye(425, 470) + d.eye(575, 470) + d.C(375, 545, 24, 'pink') + d.C(625, 545, 24, 'pink'));

  A.add('snowshoe-hare', 'Snowshoe Hare', { main: W, dark: SL, light: LB, pink: P }, d =>
    d.P('M120 930 Q500 840 880 930 Z', 'light') +
    d.E(420, 230, 58, 175, 'main', -10) + d.E(580, 230, 58, 175, 'main', 10) +
    d.E(405, 95, 36, 42, 'dark', -10) + d.E(595, 95, 36, 42, 'dark', 10) +
    d.E(420, 250, 26, 115, 'pink', -10) + d.E(580, 250, 26, 115, 'pink', 10) +
    d.E(500, 770, 180, 140) + d.E(370, 890, 105, 42) + d.E(630, 890, 105, 42) +
    d.C(500, 490, 195) +
    d.C(385, 555, 26, 'pink') + d.C(615, 555, 26, 'pink') +
    d.P('M484 520 L516 520 L500 540 Z', 'pink') +
    d.L('M500 540 L500 566 M466 566 Q483 582 500 566 Q517 582 534 566') +
    d.eye(432, 460) + d.eye(568, 460));

  A.add('husky', 'Husky', { main: SL, light: W, accent: R, pink: P }, d =>
    d.E(500, 860, 210, 110, 'light') +
    d.poly([[300, 390], [315, 160], [445, 300]]) + d.poly([[700, 390], [685, 160], [555, 300]]) +
    d.poly([[330, 340], [338, 225], [405, 300]], 'pink') + d.poly([[670, 340], [662, 225], [595, 300]], 'pink') +
    d.C(500, 500, 230) +
    d.P('M290 480 Q300 370 400 385 Q460 395 500 470 Q540 395 600 385 Q700 370 710 480 Q720 650 500 720 Q280 650 290 480 Z', 'light') +
    d.R(380, 715, 240, 50, 25, 'accent') +
    d.E(500, 600, 92, 70, 'light') + d.E(500, 565, 36, 26, 'ink') +
    d.L('M500 590 L500 615 M462 612 Q500 642 538 612') +
    d.eye(415, 480) + d.eye(585, 480));

  A.add('snow-leopard', 'Snow Leopard', { main: GR, light: W, dark: NV, pink: P }, d =>
    d.P('M640 830 Q910 830 890 600 Q880 510 800 530 Q825 560 825 620 Q835 760 640 760 Z') +
    d.C(860, 610, 16, 'dark') + d.C(830, 700, 16, 'dark') + d.C(760, 780, 16, 'dark') +
    d.E(500, 800, 185, 125) + d.E(440, 910, 52, 30) + d.E(560, 910, 52, 30) +
    d.C(370, 790, 16, 'dark') + d.C(630, 790, 16, 'dark') + d.C(400, 860, 14, 'dark') + d.C(600, 860, 14, 'dark') +
    d.C(335, 300, 58) + d.C(665, 300, 58) + d.C(335, 300, 28, 'pink') + d.C(665, 300, 28, 'pink') +
    d.C(500, 470, 210) +
    d.E(500, 575, 95, 70, 'light') + d.P('M475 540 L525 540 L500 565 Z', 'pink') +
    d.L('M500 565 L500 590 M465 590 Q482 606 500 590 Q518 606 535 590') +
    d.Lt('M400 575 L320 560 M400 595 L320 610 M600 575 L680 560 M600 595 L680 610') +
    d.C(500, 335, 16, 'dark') + d.C(450, 360, 13, 'dark') + d.C(550, 360, 13, 'dark') + d.C(330, 470, 14, 'dark') + d.C(670, 470, 14, 'dark') +
    d.eye(425, 450) + d.eye(575, 450));

  A.add('beluga', 'Beluga Whale', { main: W, light: LB, accent: B, pink: P }, d =>
    d.P('M60 940 L60 860 Q115 830 170 860 T280 860 T390 860 T500 860 T610 860 T720 860 T830 860 T940 860 L940 940 Z', 'accent') +
    d.P('M150 560 Q150 360 330 360 Q440 360 470 420 Q560 470 680 520 Q770 560 820 520 L880 450 Q920 540 870 600 L920 680 Q840 690 790 640 Q690 720 450 730 Q150 740 150 560 Z') +
    d.E(470, 700, 75, 38, 'main', 30) +
    d.eye(320, 500, 30) + d.smile(270, 590, 60, 36) + d.C(230, 560, 26, 'pink') +
    d.Lt('M560 600 Q620 640 690 620'));

  A.add('sleepy-bear', 'Sleepy Bear', { main: BR, dark: SL, light: NV, accent: '#f1d3b3', snow: W, pink: P }, d =>
    d.P('M80 900 L80 600 Q100 250 500 220 Q900 250 920 600 L920 900 Z', 'dark') +
    d.P('M150 390 Q300 200 500 212 Q700 200 850 390 Q760 330 660 360 Q560 300 460 350 Q340 300 150 390 Z', 'snow') +
    d.P('M200 900 L200 640 Q220 380 500 360 Q780 380 800 640 L800 900 Z', 'light') +
    d.L('M560 560 L600 560 L560 600 L600 600 M625 495 L655 495 L625 525 L655 525 M670 445 L692 445 L670 467 L692 467') +
    d.E(560, 770, 225, 130) + d.E(700, 870, 70, 35) +
    d.C(300, 640, 38) + d.C(430, 625, 38) + d.C(370, 730, 112) +
    d.E(330, 775, 52, 38, 'accent') + d.E(312, 758, 18, 12, 'ink') +
    d.L('M335 700 Q350 715 365 700 M395 700 Q410 715 425 700') + d.L('M320 795 Q335 805 350 795') +
    d.C(300, 735, 18, 'pink') + d.C(445, 735, 18, 'pink'));

  A.add('ice-fishing', 'Ice Fishing', { main: O, accent: B, light: LB, dark: BR, pink: P }, d =>
    d.P('M60 940 L60 770 Q500 640 940 770 L940 940 Z', 'light') +
    d.E(470, 790, 190, 58, 'accent') +
    d.L('M890 900 L760 330') + d.C(855, 760, 26, 'dark') + d.Lt('M760 330 Q690 420 620 780') +
    d.P('M330 560 L230 470 L250 600 L230 690 Z') +
    d.E(480, 580, 175, 110, 'main', -15) +
    d.Lt('M560 500 Q590 560 560 640') +
    d.eye(560, 545, 24) + d.smile(600, 610, 34, 24) +
    d.P('M440 470 Q480 400 540 450', 'main') +
    d.Lt('M320 760 L300 720 M640 760 L670 720 M300 820 L260 830'));
})();
