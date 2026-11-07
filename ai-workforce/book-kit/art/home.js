// "My First At Home": 30 friendly things around the house for ages 2-5.
// Generic household things only: no brands, logos or licensed characters.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', G = '#7bd389', Y = '#ffd23f', O = '#ff9f43', B = '#6ec6ff', PU = '#b39ddb', P = '#ffb3c7', BR = '#c68b59', T = '#4db6ac', W = '#ffffff';

  const star = (d, cx, cy, r, k = 'accent') => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r;
      pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]);
    }
    return d.poly(pts, k);
  };
  const heart = (d, cx, cy, s, k = 'accent') =>
    d.P(`M${cx} ${cy + s * 0.9} C${cx - s * 1.4} ${cy} ${cx - s * 0.9} ${cy - s * 1.1} ${cx} ${cy - s * 0.45} C${cx + s * 0.9} ${cy - s * 1.1} ${cx + s * 1.4} ${cy} ${cx} ${cy + s * 0.9} Z`, k);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  // a flower: petals in a ring, then a centre disc
  const flower = (d, cx, cy, r, k = 'accent', c = 'accent2') => {
    let s = '';
    for (let i = 0; i < 6; i++) { const a = i / 6 * 2 * Math.PI; s += d.C(cx + r * Math.cos(a), cy + r * Math.sin(a), r * 0.68, k); }
    return s + d.C(cx, cy, r * 0.75, c);
  };

  A.add('house', 'House', { main: Y, accent: R, accent2: R, light: B, dark: BR, pink: P }, d =>
    d.R(615, 200, 85, 190, 10, 'dark') +
    d.R(230, 470, 540, 400, 12) +
    d.P('M150 480 L500 185 L850 480 Q850 505 822 505 L178 505 Q150 505 150 480 Z', 'accent') +
    d.face(500, 395, 165) +
    d.R(275, 570, 120, 110, 12, 'light') + d.Lt('M335 570 L335 680 M275 625 L395 625') +
    d.R(605, 570, 120, 110, 12, 'light') + d.Lt('M665 570 L665 680 M605 625 L725 625') +
    d.P('M440 870 L440 725 A60 60 0 0 1 560 725 L560 870 Z', 'dark') + d.dot(535, 800, 11) +
    d.grass(905));

  A.add('door', 'Door', { main: R, dark: BR, light: '#ffe0e0', accent: Y, accent2: G, pink: P }, d =>
    d.R(255, 110, 490, 790, 36, 'dark') +
    d.R(300, 150, 400, 730, 30) +
    d.R(350, 205, 300, 230, 22, 'light') + d.R(350, 480, 300, 330, 22, 'light') +
    d.face(500, 315, 200) + heart(d, 500, 640, 60, 'accent') +
    d.C(645, 560, 26, 'accent') +
    d.R(215, 875, 570, 55, 22, 'accent2'));

  A.add('window', 'Window', { main: W, light: '#d7f0ff', accent: R, accent2: Y, dark: BR, pink: P }, d =>
    d.R(240, 190, 520, 560, 30, 'dark') +
    d.R(280, 230, 205, 225, 12, 'light') + d.R(515, 230, 205, 225, 12, 'light') +
    d.R(280, 485, 205, 225, 12, 'light') + d.R(515, 485, 205, 225, 12, 'light') +
    d.C(612, 342, 72, 'accent2') + d.face(612, 348, 120) +
    d.P('M180 150 L305 150 Q300 320 255 455 Q300 600 305 790 L180 790 Z', 'accent') +
    d.P('M820 150 L695 150 Q700 320 745 455 Q700 600 695 790 L820 790 Z', 'accent') +
    d.E(245, 455, 48, 20, 'accent2') + d.E(755, 455, 48, 20, 'accent2') +
    d.R(150, 120, 700, 42, 21, 'dark') +
    d.R(170, 750, 660, 50, 20, 'dark'));

  A.add('bed', 'Bed', { main: B, light: W, accent: BR, accent2: Y, dark: '#a8744a', pink: P }, d =>
    d.R(140, 300, 125, 560, 50, 'accent') + d.R(755, 480, 105, 380, 40, 'accent') +
    d.R(215, 580, 600, 110, 30, 'light') +
    d.E(320, 545, 115, 70, 'light') + d.face(320, 540, 125) +
    d.P('M420 545 L840 545 L840 715 L420 715 Q385 630 420 545 Z') +
    d.C(540, 630, 20, 'accent2') + d.C(650, 600, 20, 'accent2') + d.C(760, 645, 20, 'accent2') +
    d.R(200, 690, 620, 60, 20, 'dark'));

  A.add('pillow', 'Pillow', { main: '#d7f0ff', accent: Y, pink: P }, d =>
    d.P('M195 285 Q500 225 805 285 Q865 500 805 715 Q500 775 195 715 Q135 500 195 285 Z') +
    d.face(500, 500, 270) +
    star(d, 300, 640, 38) + star(d, 700, 640, 38));

  A.add('chair', 'Chair', { main: R, light: '#fff3d6', accent: Y, dark: BR, pink: P }, d =>
    d.R(320, 220, 50, 640, 20, 'dark') + d.R(630, 220, 50, 640, 20, 'dark') +
    d.R(290, 190, 420, 270, 50) + d.face(500, 310, 210) +
    d.R(235, 520, 530, 80, 26, 'accent') +
    d.R(260, 595, 55, 300, 20, 'dark') + d.R(685, 595, 55, 300, 20, 'dark'));

  A.add('table', 'Table', { main: BR, light: '#e3f4ff', accent: PU, accent2: Y, dark: '#a8744a', pink: R }, d =>
    d.L('M500 300 L500 205') + d.E(445, 255, 42, 18, 'none', -30) +
    flower(d, 500, 170, 40, 'pink', 'accent2') +
    d.P('M455 420 Q415 345 462 300 L538 300 Q585 345 545 420 Z', 'accent') +
    d.R(185, 540, 60, 345, 22, 'dark') + d.R(755, 540, 60, 345, 22, 'dark') +
    d.P('M110 410 L890 410 L865 565 Q500 610 135 565 Z', 'light') +
    d.face(500, 485, 170));

  A.add('sofa', 'Sofa', { main: G, light: '#e8f7ec', dark: T, accent: BR, pink: P }, d =>
    d.R(210, 765, 40, 75, 10, 'accent') + d.R(750, 765, 40, 75, 10, 'accent') +
    d.R(170, 320, 660, 270, 70) + d.face(500, 430, 220) +
    d.R(195, 660, 610, 120, 24) +
    d.R(245, 560, 255, 125, 30, 'light') + d.R(500, 560, 255, 125, 30, 'light') +
    d.R(105, 440, 150, 340, 60, 'dark') + d.R(745, 440, 150, 340, 60, 'dark'));

  A.add('lamp', 'Lamp', { main: Y, light: '#fff3d6', accent: R, dark: BR, pink: P }, d =>
    d.R(475, 460, 50, 300, 20, 'dark') +
    d.E(500, 780, 175, 58, 'accent') +
    d.P('M335 190 L665 190 Q690 190 698 214 L770 455 Q775 480 748 480 L252 480 Q225 480 230 455 L302 214 Q310 190 335 190 Z') +
    d.face(500, 330, 230) +
    d.R(560, 480, 16, 110, 8, 'dark') + d.C(568, 600, 16, 'accent'));

  A.add('clock', 'Clock', { main: R, light: W, accent: Y, dark: BR, pink: P }, d =>
    d.C(305, 245, 82, 'accent') + d.C(695, 245, 82, 'accent') +
    d.P('M345 755 L295 870 L345 870 L395 785 Z', 'dark') + d.P('M655 755 L705 870 L655 870 L605 785 Z', 'dark') +
    d.C(500, 520, 262) + d.C(500, 520, 205, 'light') +
    d.Lt('M500 330 L500 365 M500 675 L500 710 M310 520 L345 520 M655 520 L690 520') +
    d.L('M500 470 L440 420') + d.L('M500 470 L500 370') + d.dot(500, 470, 16) +
    d.face(500, 560, 190));

  A.add('cup', 'Cup', { main: B, light: '#e3f4ff', dark: BR, accent: Y, pink: P }, d =>
    d.Lt('M420 280 Q390 230 420 190 Q450 150 420 110 M560 280 Q530 230 560 190 Q590 150 560 110') +
    d.E(485, 830, 300, 50, 'accent') +
    d.P('M700 420 C870 420 870 710 700 710 L700 645 C800 645 800 485 700 485 Z') +
    d.R(260, 330, 450, 470, 60) +
    d.E(485, 335, 225, 40, 'dark') +
    d.face(485, 560, 250));

  A.add('teapot', 'Teapot', { main: PU, light: '#ede7f6', accent: Y, accent2: P, pink: P }, d =>
    d.P('M690 560 L835 410 Q860 395 870 420 L760 640 Z') +
    d.P('M275 470 C120 470 120 710 275 710 L275 650 C185 650 185 530 275 530 Z') +
    d.C(480, 345, 32, 'accent') +
    d.E(480, 590, 245, 205) +
    d.E(480, 395, 115, 32, 'accent') +
    d.face(480, 600, 240) +
    d.Lt('M868 375 Q845 335 870 300 Q895 265 870 230'));

  A.add('spoon', 'Spoon', { main: '#cfd8dc', light: '#eef3f5', accent: B, pink: P }, d =>
    group(d.P('M478 520 L522 520 Q548 700 555 845 Q500 915 445 845 Q452 700 478 520 Z', 'accent') +
      d.P('M500 105 C625 105 685 225 662 335 C640 455 560 535 500 545 C440 535 360 455 338 335 C315 225 375 105 500 105 Z') +
      d.Lt('M395 230 Q412 185 452 165'), 20) +
    d.face(556, 345, 200));

  A.add('cooking-pot', 'Pot', { main: R, light: '#fff3d6', accent: Y, dark: '#90a4ae', pink: P }, d =>
    d.Lt('M420 255 Q395 215 420 180 Q445 145 420 110 M580 255 Q555 215 580 180 Q605 145 580 110') +
    d.R(135, 480, 110, 60, 30, 'dark') + d.R(755, 480, 110, 60, 30, 'dark') +
    d.C(500, 322, 32, 'accent') +
    d.P('M225 430 Q500 270 775 430 Z', 'light') +
    d.R(220, 420, 560, 380, 60) + d.R(205, 410, 590, 50, 25, 'light') +
    d.face(500, 610, 260));

  A.add('toaster', 'Toaster', { main: '#cfd8dc', light: '#f3d9b8', dark: '#90a4ae', accent: R, pink: P }, d =>
    d.R(320, 225, 150, 230, 50, 'light') + d.R(530, 225, 150, 230, 50, 'light') +
    d.R(270, 780, 70, 50, 15, 'dark') + d.R(660, 780, 70, 50, 15, 'dark') +
    d.R(220, 400, 560, 400, 90) +
    d.R(765, 520, 75, 42, 16, 'accent') +
    d.face(500, 600, 250));

  A.add('fridge', 'Fridge', { main: '#e3f4ff', dark: '#90a4ae', accent: R, accent2: Y, light: G, pink: P }, d =>
    d.R(310, 860, 60, 40, 10, 'dark') + d.R(630, 860, 60, 40, 10, 'dark') +
    d.R(280, 120, 440, 760, 40) + d.L('M280 380 L720 380') +
    d.R(640, 195, 30, 120, 15, 'dark') + d.R(640, 440, 30, 180, 15, 'dark') +
    heart(d, 390, 255, 32, 'accent') + star(d, 520, 260, 42, 'accent2') +
    d.face(470, 610, 230));

  A.add('washing-machine', 'Washing Machine', { main: W, light: '#d7f0ff', dark: '#90a4ae', accent: B, accent2: R, pink: P }, d =>
    d.R(230, 160, 540, 700, 40) + d.L('M230 320 L770 320') +
    d.C(320, 240, 34, 'accent') + d.R(420, 220, 130, 40, 15, 'light') + d.C(640, 240, 16, 'accent2') + d.C(700, 240, 16, 'accent') +
    d.C(500, 590, 205, 'dark') + d.C(500, 590, 150, 'light') +
    d.face(500, 595, 200));

  A.add('broom', 'Broom', { main: Y, dark: R, accent: BR, pink: P }, d =>
    group(d.R(475, 100, 50, 500, 25, 'accent') +
      d.P('M410 610 L590 610 L700 880 Q500 915 300 880 Z') +
      d.R(405, 560, 190, 62, 18, 'dark') +
      d.face(500, 690, 150) +
      d.Lt('M440 790 L410 870 M500 790 L500 885 M560 790 L590 870'), -10));

  A.add('toothbrush', 'Toothbrush', { main: T, light: W, accent: '#d7f0ff', accent2: B, pink: P }, d =>
    d.R(640, 470, 230, 125, 18, 'light') +
    d.Lt('M695 535 L695 590 M745 535 L745 590 M795 535 L795 590 M840 535 L840 590') +
    d.P('M630 485 Q615 425 680 428 Q700 370 760 395 Q805 350 845 400 Q905 400 885 485 Q760 520 630 485 Z', 'accent') +
    d.R(130, 580, 760, 130, 60) +
    d.face(330, 630, 140));

  A.add('bathtub', 'Bathtub', { main: '#e3f4ff', light: W, dark: '#90a4ae', accent: Y, pink: P }, d =>
    d.R(150, 330, 40, 150, 15, 'dark') + d.R(150, 320, 130, 44, 20, 'dark') +
    d.C(330, 420, 60, 'light') + d.C(430, 385, 72, 'light') + d.C(545, 405, 65, 'light') + d.C(655, 380, 72, 'light') + d.C(755, 420, 58, 'light') +
    d.E(260, 800, 45, 32, 'accent') + d.E(740, 800, 45, 32, 'accent') +
    d.P('M160 500 L840 500 Q830 700 720 775 L280 775 Q170 700 160 500 Z') +
    d.R(130, 470, 740, 56, 28, 'light') +
    d.face(500, 630, 230));

  A.add('towel', 'Towel', { main: PU, accent: Y, dark: BR, accent2: R, pink: P }, d =>
    d.R(150, 200, 700, 40, 20, 'dark') + d.C(150, 220, 30, 'accent2') + d.C(850, 220, 30, 'accent2') +
    d.Lt('M320 810 L320 855 M380 810 L380 855 M440 810 L440 855 M500 810 L500 855 M560 810 L560 855 M620 810 L620 855 M680 810 L680 855') +
    d.R(280, 185, 440, 625, 30) +
    d.R(280, 640, 440, 55, 0, 'accent') +
    d.face(500, 420, 240));

  A.add('soap', 'Soap', { main: P, light: '#e3f4ff', accent: B, pink: R }, d =>
    d.C(300, 330, 70, 'light') + d.C(430, 245, 50, 'light') + d.C(650, 320, 85, 'light') + d.C(770, 190, 45, 'light') + d.C(555, 160, 35, 'light') +
    d.Lt('M270 300 Q285 280 310 275 M625 285 Q640 268 665 263') +
    d.E(500, 765, 330, 70, 'accent') +
    d.R(230, 450, 540, 300, 90) +
    d.face(500, 590, 240));

  A.add('potty', 'Potty', { main: B, light: W, accent: Y, pink: P }, d =>
    d.R(300, 250, 400, 240, 80, 'accent') +
    d.P('M262 480 Q275 785 385 825 L615 825 Q725 785 738 480 Z') +
    d.E(500, 480, 272, 70, 'accent') + d.E(500, 480, 190, 40, 'light') +
    d.face(500, 650, 220));

  A.add('key', 'Key', { main: Y, light: W, accent: O, pink: P }, d =>
    d.P('M700 530 L700 625 L750 625 L750 575 L800 575 L800 645 L850 645 L850 530 Z') +
    d.R(480, 470, 400, 70, 30) +
    d.C(330, 500, 200) + d.C(330, 360, 28, 'light') +
    d.face(330, 525, 230));

  A.add('flower-pot', 'Flower Pot', { main: O, accent: R, accent2: Y, light: G, dark: PU, pink: P }, d =>
    d.L('M500 525 L500 300') +
    d.E(420, 430, 72, 30, 'light', -30) + d.E(580, 400, 72, 30, 'light', 30) +
    flower(d, 500, 245, 72, 'dark', 'accent2') +
    d.P('M300 560 L700 560 L650 865 L350 865 Z') +
    d.R(265, 515, 470, 80, 25, 'accent') +
    d.face(500, 715, 200));

  A.add('mailbox', 'Mailbox', { main: B, dark: BR, accent: R, light: W, pink: P }, d =>
    d.R(470, 555, 60, 330, 20, 'dark') +
    d.R(165, 330, 130, 90, 8, 'light') + d.Lt('M165 335 L230 380 L295 335') +
    d.P('M250 565 L250 385 Q250 255 400 255 L600 255 Q750 255 750 385 L750 565 Z') +
    d.R(733, 290, 30, 170, 12, 'accent') + d.P('M748 290 L860 290 L860 355 L748 355 Z', 'accent') +
    d.face(500, 420, 230) + d.grass(900));

  A.add('slippers', 'Slippers', { main: P, light: W, accent: PU, pink: R }, d => {
    const one = (m) => {
      const X = x => (m ? 1000 - x : x);
      const path = pts => pts.replace(/(-?\d+) (-?\d+)/g, (_, x, y) => X(+x) + ' ' + y);
      return d.E(X(300), 265, 30, 78, 'main', m ? 12 : -12) + d.E(X(390), 265, 30, 78, 'main', m ? -12 : 12) +
        d.P(path('M345 320 C465 320 475 480 452 600 C438 720 428 840 345 850 C262 840 252 720 238 600 C215 480 225 320 345 320 Z'), 'light') +
        d.P(path('M345 320 C465 320 475 480 460 545 Q345 585 230 545 C215 480 225 320 345 320 Z'), 'main') +
        d.face(X(345), 440, 135);
    };
    return one(false) + one(true);
  });

  A.add('books', 'Books', { main: R, accent: B, accent2: Y, light: W, dark: G, pink: P }, d => {
    const book = (x, y, w, h, k) => d.R(x, y, w, h, 20, k) + d.R(x + 45, y, 26, h, 0, 'light') + d.R(x + w - 71, y, 26, h, 0, 'light');
    return book(220, 705, 560, 160, 'main') + book(270, 545, 470, 160, 'accent') + book(240, 385, 500, 160, 'accent2') +
      d.face(505, 615, 160);
  });

  A.add('mirror', 'Mirror', { main: PU, light: '#e3f4ff', accent: Y, pink: P }, d =>
    d.R(460, 730, 80, 200, 40) +
    d.E(500, 430, 250, 320) + d.E(500, 430, 195, 265, 'light') +
    d.Lt('M370 280 Q395 240 435 222 M360 340 Q368 320 380 308') +
    heart(d, 500, 800, 26, 'accent') +
    d.face(500, 460, 250));

  A.add('pajamas', 'Pajamas', { main: B, light: '#e3f4ff', accent: Y, accent2: PU, pink: P }, d =>
    d.P('M330 560 L670 560 L685 875 L545 875 L500 650 L455 875 L315 875 Z', 'light') +
    d.P('M330 220 L420 190 Q500 245 580 190 L670 220 L805 335 L740 425 L675 375 L675 580 L325 580 L325 375 L260 425 L195 335 Z') +
    d.L('M420 190 L500 265 L580 190') +
    d.dot(500, 330, 13) + d.dot(500, 420, 13) + d.dot(500, 510, 13) +
    star(d, 405, 455, 42) + star(d, 595, 360, 38) + d.P('M610 470 A50 50 0 1 1 610 545 A38 38 0 1 0 610 470 Z', 'accent') +
    star(d, 395, 760, 30, 'accent2') + star(d, 610, 790, 30, 'accent2'));
})();
