// "My First Toys": 30 friendly toys for ages 2-5. Generic toys only: no
// brands or licensed characters (plain stacking blocks, not branded bricks).
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
  // a cube seen from the front-right: front square, top and side faces
  const cube = (d, x, y, w, k = 'main') =>
    d.P(`M${x} ${y} L${x + 50} ${y - 50} L${x + w + 50} ${y - 50} L${x + w} ${y} Z`, 'light') +
    d.P(`M${x + w} ${y} L${x + w + 50} ${y - 50} L${x + w + 50} ${y + w - 50} L${x + w} ${y + w} Z`, 'dark') +
    d.R(x, y, w, w, 16, k);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;

  A.add('teddy-bear', 'Teddy Bear', { main: BR, light: '#f3d9b8', pink: P }, d =>
    d.C(330, 240, 72) + d.C(670, 240, 72) + d.C(330, 240, 36, 'light') + d.C(670, 240, 36, 'light') +
    d.E(290, 600, 70, 115, 'main', 30) + d.E(710, 600, 70, 115, 'main', -30) +
    d.E(500, 650, 215, 205) + d.E(500, 690, 120, 110, 'light') +
    d.E(375, 835, 90, 68) + d.E(625, 835, 90, 68) + d.E(375, 845, 45, 32, 'light') + d.E(625, 845, 45, 32, 'light') +
    d.C(500, 360, 175) + d.E(500, 430, 80, 58, 'light') + d.E(500, 402, 24, 16, 'ink') +
    d.eye(435, 320, 22) + d.eye(565, 320, 22) + d.smile(500, 440, 32, 20) +
    d.C(395, 390, 22, 'pink') + d.C(605, 390, 22, 'pink'));

  A.add('ball', 'Ball', { main: R, accent: Y, accent2: B, pink: P }, d =>
    d.C(500, 520, 300) +
    d.P('M500 220 A300 300 0 0 0 500 820 C330 710 330 330 500 220 Z', 'accent') +
    d.P('M500 220 A300 300 0 0 1 500 820 C670 710 670 330 500 220 Z', 'accent2') +
    d.face(500, 540, 230));

  A.add('blocks', 'Blocks', { main: R, light: '#ffe7a8', dark: O, accent: Y, accent2: B, pink: P }, d =>
    cube(d, 170, 590, 260, 'main') + cube(d, 480, 590, 260, 'accent2') + cube(d, 330, 330, 260, 'accent') +
    star(d, 300, 720, 80, 'light') + heart(d, 610, 725, 70, 'light') + d.C(460, 460, 70, 'light'));

  A.add('toy-car', 'Toy Car', { main: R, light: '#ffe7a8', accent: B, accent2: Y, pink: P }, d =>
    d.P('M320 505 L395 360 L620 360 L705 505 Z', 'light') +
    d.P('M355 495 L412 385 L495 385 L495 495 Z', 'accent') + d.P('M525 495 L525 385 L605 385 L665 495 Z', 'accent') +
    d.R(165, 495, 670, 200, 70) + d.C(805, 560, 24, 'accent2') + d.R(150, 600, 40, 40, 12, 'accent2') +
    d.C(320, 705, 92) + d.C(680, 705, 92) + d.C(320, 705, 36, 'light') + d.C(680, 705, 36, 'light') +
    d.face(500, 575, 170));

  A.add('rocking-horse', 'Rocking Horse', { main: '#f3d9b8', accent: BR, accent2: R, dark: B, pink: P }, d =>
    d.P('M270 520 C170 500 145 630 180 700 C200 620 230 590 270 585 Z', 'accent') +
    d.R(310, 600, 55, 240, 22) + d.R(600, 600, 55, 240, 22) +
    d.E(480, 560, 235, 115) + d.P('M395 455 Q470 425 545 455 L555 545 Q470 570 385 545 Z', 'accent2') +
    d.C(655, 300, 40, 'accent') + d.C(625, 360, 40, 'accent') + d.C(600, 425, 40, 'accent') +
    d.P('M600 545 C640 440 660 380 690 330 L785 365 C755 425 735 485 725 560 Z') +
    d.P('M695 255 L715 180 L755 250 Z') + d.E(770, 320, 125, 78, 'main', -22) +
    d.eye(770, 295, 20) + d.dot(860, 330, 8) + d.smile(815, 360, 28, 14) +
    d.P('M150 815 Q500 935 850 815 L850 850 Q500 975 150 850 Z', 'dark'));

  A.add('kite', 'Kite', { main: R, accent: Y, light: W, accent2: B, pink: P }, d => {
    const bow = (x, y) => d.P(`M${x} ${y} L${x - 45} ${y - 30} L${x - 45} ${y + 30} Z`, 'accent2') + d.P(`M${x} ${y} L${x + 45} ${y - 30} L${x + 45} ${y + 30} Z`, 'accent2');
    return d.L('M500 700 Q430 770 500 830 Q570 890 510 940') + bow(468, 772) + bow(532, 860) +
      d.poly([[500, 110], [720, 400], [500, 400]], 'main') + d.poly([[720, 400], [500, 700], [500, 400]], 'accent') +
      d.poly([[500, 700], [280, 400], [500, 400]], 'main') + d.poly([[280, 400], [500, 110], [500, 400]], 'accent') +
      d.C(500, 400, 100, 'light') + d.face(500, 410, 150);
  });

  A.add('yo-yo', 'Yo-Yo', { main: B, light: '#d7f0ff', pink: P }, d =>
    d.L('M500 240 Q530 160 500 110') + d.C(500, 95, 26) +
    d.C(500, 520, 280) + d.C(500, 520, 195, 'light') + d.face(500, 530, 250));

  A.add('rubber-duck', 'Rubber Duck', { main: Y, accent: O, pink: P }, d =>
    d.P('M240 610 L160 505 L310 560 Z') + d.E(520, 660, 300, 170) +
    d.E(470, 650, 135, 72, 'main', -8) +
    d.C(645, 400, 150) + d.P('M760 395 Q880 385 868 440 Q810 475 760 452 Z', 'accent') +
    d.eye(665, 370, 22) + d.C(615, 445, 26, 'pink') + d.water(880));

  A.add('doll', 'Doll', { main: R, light: '#fde3c8', accent: BR, accent2: Y, pink: P }, d =>
    d.C(310, 340, 72, 'accent') + d.C(690, 340, 72, 'accent') +
    d.E(330, 570, 45, 105, 'light', 25) + d.E(670, 570, 45, 105, 'light', -25) +
    d.R(405, 780, 55, 110, 25, 'light') + d.R(540, 780, 55, 110, 25, 'light') +
    d.E(430, 895, 55, 26, 'accent2') + d.E(570, 895, 55, 26, 'accent2') +
    d.P('M420 470 L580 470 L725 800 L275 800 Z') +
    d.C(430, 640, 20, 'accent2') + d.C(570, 640, 20, 'accent2') + d.C(500, 720, 20, 'accent2') + d.C(360, 740, 20, 'accent2') + d.C(640, 740, 20, 'accent2') +
    d.C(500, 320, 160, 'light') + d.P('M345 290 Q500 160 655 290 Q580 225 500 248 Q420 225 345 290 Z', 'accent') +
    d.face(500, 350, 210));

  A.add('drum', 'Drum', { main: R, light: '#fff3d6', accent: Y, accent2: BR, pink: P }, d =>
    d.P('M260 440 L260 745 Q500 835 740 745 L740 440 Z') +
    d.P('M260 700 Q500 790 740 700 L740 745 Q500 835 260 745 Z', 'accent') +
    d.E(500, 440, 240, 72, 'light') +
    d.poly([[560, 400], [760, 200], [785, 225], [585, 425]], 'accent2') + d.C(780, 195, 32, 'accent') +
    d.poly([[440, 400], [240, 200], [215, 225], [415, 425]], 'accent2') + d.C(220, 195, 32, 'accent') +
    d.face(500, 590, 230));

  A.add('train', 'Toy Train', { main: B, light: '#e3f4ff', accent: R, accent2: Y, dark: PU, pink: P }, d =>
    d.C(300, 300, 40, 'light') + d.C(360, 235, 50, 'light') + d.C(445, 180, 58, 'light') +
    d.R(255, 395, 70, 120, 15, 'accent') + d.P('M225 385 L355 385 L335 435 L245 435 Z', 'accent') +
    d.R(195, 500, 350, 170, 45) + d.R(520, 380, 225, 290, 22) + d.R(560, 420, 145, 110, 16, 'light') +
    d.P('M740 380 L760 350 L505 350 L525 380 Z', 'accent') +
    d.R(175, 650, 590, 60, 22, 'dark') + d.P('M180 650 L115 725 L205 712 Z', 'accent2') +
    d.C(285, 745, 70) + d.C(470, 745, 70) + d.C(660, 750, 62) +
    d.C(285, 745, 22, 'accent2') + d.C(470, 745, 22, 'accent2') + d.C(660, 750, 20, 'accent2') +
    d.face(365, 585, 165));

  A.add('robot', 'Robot', { main: '#cfd8dc', light: '#eef3f5', dark: '#90a4ae', accent: R, accent2: Y, pink: P }, d =>
    d.L('M500 205 L500 135') + d.C(500, 118, 30, 'accent') +
    d.R(215, 480, 90, 205, 40) + d.R(695, 480, 90, 205, 40) + d.C(260, 705, 46, 'accent') + d.C(740, 705, 46, 'accent') +
    d.R(370, 755, 90, 115, 20) + d.R(540, 755, 90, 115, 20) + d.R(340, 855, 150, 50, 20, 'dark') + d.R(510, 855, 150, 50, 20, 'dark') +
    d.R(320, 260, 40, 95, 15, 'accent') + d.R(640, 260, 40, 95, 15, 'accent') +
    d.R(460, 415, 80, 50, 10, 'dark') + d.R(310, 455, 380, 305, 40) +
    d.R(400, 510, 200, 110, 20, 'light') + d.C(445, 565, 18, 'accent') + d.C(500, 565, 18, 'accent2') + d.C(555, 565, 18, 'accent') +
    heart(d, 500, 685, 34, 'accent') +
    d.R(360, 200, 280, 225, 40) + d.face(500, 305, 230));

  A.add('spinning-top', 'Spinning Top', { main: PU, light: '#ede7f6', accent: Y, accent2: R, pink: P }, d =>
    d.P('M275 585 Q500 700 725 585 L500 860 Z', 'accent2') +
    d.R(470, 290, 60, 140, 22, 'accent') + d.C(500, 285, 42, 'accent') +
    d.P('M300 480 Q500 380 700 480 L760 560 Q500 690 240 560 Z') +
    d.face(500, 535, 200) + d.Lt('M380 895 Q500 925 620 895'));

  A.add('balloon', 'Balloon', { main: R, light: W, pink: P }, d =>
    d.L('M500 700 Q450 780 520 850 Q580 905 505 955') +
    d.P('M478 665 L522 665 L538 702 L462 702 Z') +
    d.E(500, 400, 235, 272) + d.E(395, 285, 38, 68, 'light', -25) + d.face(500, 440, 260));

  A.add('jack-in-the-box', 'Jack-in-the-Box', { main: B, light: '#e3f4ff', dark: PU, accent: R, accent2: Y, pink: P }, d =>
    d.P('M260 560 L330 500 L730 500 L660 560 Z', 'light') +
    d.P('M660 560 L730 500 L730 815 L660 880 Z', 'dark') +
    d.R(260, 560, 400, 320, 20) + star(d, 460, 720, 90, 'accent2') +
    d.L('M760 650 L815 650 L815 600') + d.C(815, 590, 22, 'accent') +
    d.L('M480 525 L430 495 L530 465 L430 435 L520 410') +
    d.scallop(475, 400, 70, 9, 34, 'accent2') +
    d.C(475, 290, 120, 'light') + d.P('M390 215 L475 85 L560 215 Z', 'accent') + d.C(475, 85, 25, 'accent2') +
    d.face(475, 300, 190));

  A.add('rocket', 'Toy Rocket', { main: W, light: '#d7f0ff', accent: R, accent2: Y, pink: P }, d =>
    d.P('M420 700 Q500 905 580 700 Z', 'accent2') +
    d.P('M385 560 L270 745 L395 705 Z', 'accent') + d.P('M615 560 L730 745 L605 705 Z', 'accent') +
    d.P('M500 145 C620 275 645 500 620 705 L380 705 C355 500 380 275 500 145 Z') +
    d.P('M500 145 C560 210 590 265 606 318 L394 318 C410 265 440 210 500 145 Z', 'accent') +
    d.C(500, 440, 88, 'light') + d.face(500, 448, 140) + d.R(430, 600, 140, 40, 18, 'accent'));

  A.add('xylophone', 'Xylophone', { main: R, accent: O, accent2: Y, light: G, dark: B, pink: PU }, d => {
    const keys = ['main', 'accent', 'accent2', 'light', 'dark', 'pink'];
    let s = d.P('M150 430 L850 480 L850 515 L150 465 Z', 'accent2') + d.P('M150 720 L850 660 L850 695 L150 755 Z', 'accent2');
    keys.forEach((k, i) => {
      const x = 175 + i * 110, h = 430 - i * 38, y = 590 - h / 2 + i * 6;
      s += d.R(x, y, 90, h, 16, k) + d.dot(x + 45, y + 32, 10) + d.dot(x + 45, y + h - 32, 10);
    });
    return s + d.poly([[640, 330], [800, 170], [822, 192], [662, 352]], 'accent') + d.C(810, 175, 42, 'accent2');
  });

  A.add('puzzle', 'Puzzle', { main: G, pink: P }, d =>
    d.P('M250 300 L440 300 A75 75 0 1 1 560 300 L750 300 L750 490 A75 75 0 1 1 750 610 L750 800 L560 800 A75 75 0 1 0 440 800 L250 800 L250 610 A75 75 0 1 0 250 490 Z') +
    d.face(500, 560, 270));

  A.add('pail-shovel', 'Pail & Shovel', { main: B, accent: Y, accent2: R, light: '#fff3d6', pink: P }, d =>
    d.L('M290 455 Q470 200 670 455') +
    d.P('M295 465 L665 465 L615 850 L345 850 Z') + d.R(270, 430, 420, 60, 26, 'accent') +
    d.face(480, 650, 230) +
    d.R(760, 330, 40, 360, 18, 'accent2') + d.R(735, 285, 90, 60, 22, 'accent2') +
    d.P('M728 670 L832 670 L822 805 Q780 860 738 805 Z', 'light'));

  A.add('toy-boat', 'Toy Boat', { main: R, light: W, accent: Y, accent2: B, pink: P }, d =>
    d.L('M500 620 L500 195') + d.P('M500 195 L585 222 L500 250 Z', 'accent2') +
    d.P('M515 230 L515 585 L765 585 Z', 'light') + d.P('M485 270 L485 585 L290 585 Z', 'accent') +
    d.P('M170 615 L830 615 L735 775 L265 775 Z') + d.face(500, 690, 160) + d.water(860));

  A.add('toy-plane', 'Toy Plane', { main: Y, accent: R, accent2: B, dark: '#90a4ae', pink: P }, d =>
    d.P('M420 470 L330 290 L425 290 L540 470 Z', 'accent') +
    d.P('M205 470 L150 320 L245 330 L305 470 Z', 'accent') +
    d.E(500, 520, 330, 108) +
    d.P('M420 570 L330 750 L425 750 L540 570 Z', 'accent') +
    d.E(858, 520, 22, 120, 'accent2') + d.C(838, 520, 26, 'dark') +
    d.face(655, 505, 150));

  A.add('stacking-rings', 'Stacking Rings', { main: R, accent: O, accent2: Y, pink: G, light: '#fff3d6', dark: B }, d =>
    d.R(470, 360, 60, 420, 25, 'light') + d.P('M300 770 L700 770 L660 870 L340 870 Z', 'dark') +
    d.E(500, 710, 205, 58) + d.E(500, 620, 172, 52, 'accent') + d.E(500, 535, 142, 46, 'accent2') + d.E(500, 455, 112, 40, 'pink') +
    d.C(500, 340, 92, 'light') + d.face(500, 348, 140));

  A.add('pinwheel', 'Pinwheel', { main: R, accent: Y, accent2: B, light: G, pink: P }, d => {
    const c = [500, 400], b = [[[0, 0], [0, -255], [185, -130], 'main'], [[0, 0], [255, 0], [130, 185], 'accent'], [[0, 0], [0, 255], [-185, 130], 'accent2'], [[0, 0], [-255, 0], [-130, -185], 'light']];
    return d.R(485, 480, 30, 440, 14, 'accent') +
      b.map(([p1, p2, p3, k]) => d.poly([p1, p2, p3].map(([x, y]) => [c[0] + x, c[1] + y]), k)).join('') +
      d.C(500, 400, 34, 'accent');
  });

  A.add('rattle', 'Rattle', { main: Y, accent: PU, accent2: R, pink: P }, d =>
    d.Lt('M245 250 Q222 200 252 158 M755 250 Q778 200 748 158') +
    d.R(470, 560, 60, 300, 30, 'accent') + d.C(500, 880, 48, 'accent') +
    d.E(500, 590, 72, 26, 'accent2') + d.C(500, 380, 210) + d.face(500, 395, 260));

  A.add('toy-box', 'Toy Box', { main: BR, dark: '#a8744a', accent: R, accent2: Y, light: B, pink: P }, d =>
    d.P('M200 480 L245 270 L755 270 L800 480 Z', 'dark') +
    d.C(335, 445, 92, 'accent') + d.R(480, 350, 140, 140, 16, 'accent2') + star(d, 690, 420, 75, 'light') +
    d.R(200, 470, 600, 390, 30) + d.R(200, 545, 600, 52, 0, 'accent2') +
    d.face(500, 720, 250));

  A.add('jump-rope', 'Jump Rope', { main: R, accent: Y, pink: P }, d =>
    d.P('M250 705 C250 170 750 170 750 705 L728 705 C728 205 272 205 272 705 Z') +
    d.R(222, 700, 78, 200, 34, 'accent') + d.R(700, 700, 78, 200, 34, 'accent') +
    heart(d, 500, 520, 90, 'main') + d.face(500, 510, 120));

  A.add('scooter', 'Scooter', { main: G, accent: R, light: '#fff3d6', pink: P }, d =>
    d.P('M640 780 L715 290 L760 298 L690 790 Z') +
    d.R(245, 755, 470, 55, 26) + d.R(640, 255, 210, 48, 24, 'accent') +
    d.C(310, 840, 72) + d.C(700, 840, 72) + d.C(310, 840, 26, 'light') + d.C(700, 840, 26, 'light'));

  A.add('tricycle', 'Tricycle', { main: R, accent: Y, accent2: B, light: '#fff3d6', pink: P }, d =>
    d.C(280, 780, 92) + d.C(280, 780, 30, 'light') +
    d.P('M290 765 L640 690 L652 725 L302 800 Z') +
    d.R(368, 575, 26, 205, 10) + d.E(382, 560, 95, 32, 'accent') +
    d.P('M630 420 L672 420 L672 700 L630 700 Z') +
    d.C(650, 700, 170) + d.Lt('M650 540 L650 860 M490 700 L810 700 M537 587 L763 813 M537 813 L763 587') +
    d.C(650, 700, 36, 'accent') + d.R(555, 395, 210, 42, 21, 'accent2'));

  A.add('crayons', 'Crayons', { main: R, accent: B, accent2: Y, light: W, pink: P }, d => {
    const crayon = (x, y, k) => d.P(`M${x} ${y} L${x + 45} ${y - 95} L${x + 90} ${y} Z`, k) + d.R(x, y, 90, 500, 12, k) + d.R(x, y + 150, 90, 190, 0, 'light');
    return group(crayon(260, 320, 'main'), -12, 305, 570) + crayon(455, 260, 'accent') + group(crayon(650, 320, 'accent2'), 12, 695, 570);
  });

  A.add('bubbles', 'Bubbles', { main: '#d7f0ff', accent: PU, light: W, pink: P }, d =>
    d.R(630, 570, 40, 360, 18, 'accent') + d.C(650, 480, 100, 'none') + d.C(650, 480, 80, 'none') +
    d.C(330, 310, 125) + d.C(575, 190, 72) + d.C(250, 590, 66) + d.C(450, 500, 52) + d.C(780, 300, 48) +
    d.Lt('M250 250 Q270 215 305 205 M548 158 Q560 145 580 142 M225 560 Q235 545 252 540') +
    d.face(330, 325, 170));
})();
