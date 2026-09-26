// "My First Fruits & Veggies": 30 smiling fruits and vegetables for ages 2-5.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const R = '#ff6b6b', G = '#7bd389', DG = '#4caf50', Y = '#ffd23f', O = '#ff9f43', P = '#ffb3c7', PU = '#b39ddb', BR = '#c68b59', W = '#ffffff';
  const leaf = (d, x, y, rot = -30, k = 'accent') => d.E(x, y, 70, 34, k, rot);

  A.add('apple', 'Apple', { main: R, accent: G, pink: P }, d =>
    d.L('M500 330 Q490 250 520 190') + d.P('M520 250 Q610 170 690 210 Q620 290 520 250 Z', 'accent') +
    d.P('M500 330 C380 250 200 320 210 520 C220 760 380 880 500 820 C620 880 780 760 790 520 C800 320 620 250 500 330 Z') +
    d.face(500, 560, 280));

  A.add('banana', 'Banana', { main: Y, dark: BR, pink: P }, d =>
    d.P('M262 318 L238 238 L288 230 L302 306 Z', 'dark') +
    d.P('M235 350 Q300 800 780 760 Q845 752 812 700 Q460 690 345 330 Q330 290 285 296 Q238 305 235 350 Z') +
    d.face(480, 610, 200));

  A.add('pear', 'Pear', { main: '#c5e17a', accent: G, pink: P }, d =>
    d.L('M500 262 Q505 200 540 160') + leaf(d, 590, 200, -20) +
    d.P('M500 255 C430 255 420 385 390 455 C250 525 230 830 500 860 C770 830 750 525 610 455 C580 385 570 255 500 255 Z') +
    d.face(500, 660, 260));

  A.add('orange', 'Orange', { main: O, accent: G, pink: P }, d =>
    d.L('M500 262 L505 220') + leaf(d, 565, 225, -20) +
    d.C(500, 545, 285) + d.dot(360, 420, 7) + d.dot(640, 410, 7) + d.dot(620, 700, 7) + d.dot(380, 690, 7) +
    d.face(500, 560, 280));

  A.add('strawberry', 'Strawberry', { main: R, accent: G, pink: P }, d =>
    d.P('M500 865 C300 765 200 525 260 385 C320 305 420 315 500 335 C580 315 680 305 740 385 C800 525 700 765 500 865 Z') +
    d.P('M500 250 L540 320 L630 300 L570 360 L640 410 L540 390 L500 440 L460 390 L360 410 L430 360 L370 300 L460 320 Z', 'accent') +
    [[360, 500], [640, 500], [330, 620], [670, 620], [420, 760], [580, 760], [500, 800]].map(([x, y]) => d.E(x, y, 10, 16, 'light')).join('') +
    d.face(500, 580, 240));

  A.add('cherries', 'Cherries', { main: R, accent: G, pink: P }, d =>
    d.L('M380 560 Q420 340 560 215 M640 560 Q620 380 560 215') + leaf(d, 620, 200, -25) +
    d.C(370, 690, 155) + d.C(640, 700, 155) + d.face(370, 690, 150) + d.face(640, 700, 150));

  A.add('grapes', 'Grapes', { main: PU, accent: G, pink: P }, d => {
    const rows = [[330, 405, 480, 555, 630, 705].slice(0, 0)], pts = [];
    [[4, 360], [3, 480], [2, 600], [1, 720]].forEach(([n, y]) => { for (let i = 0; i < n; i++) pts.push([500 + (i - (n - 1) / 2) * 150, y]); });
    return d.L('M500 290 L500 210') + leaf(d, 580, 230, -15) +
      pts.map(([x, y]) => d.C(x, y, 82)).join('') + d.face(500, 722, 120);
  });

  A.add('pineapple', 'Pineapple', { main: Y, accent: DG, pink: P }, d =>
    [[-60, -20], [-30, -8], [0, 0], [30, 8], [60, 20]].map(([dx, rot]) => d.P(`M${500 + dx * 1.6} 420 L${500 + dx * 3.2} ${170 + Math.abs(dx) * 2} L${500 + dx * 0.4} 400 Z`, 'accent')).join('') +
    d.E(500, 640, 210, 265) +
    d.Lt('M360 500 L420 540 L480 500 L540 540 L600 500 L640 525 M360 790 L420 830 L480 790 L540 830 L600 790 L640 815') +
    d.face(500, 650, 200));

  A.add('watermelon', 'Watermelon', { main: R, dark: DG, light: '#e8ffd6', pink: P }, d =>
    d.P('M150 380 L850 380 A350 350 0 0 1 150 380 Z', 'dark') +
    d.P('M195 390 L805 390 A305 305 0 0 1 195 390 Z', 'light') +
    d.P('M230 395 L770 395 A270 270 0 0 1 230 395 Z') +
    [[320, 470], [680, 470], [390, 600], [610, 600]].map(([x, y]) => d.E(x, y, 12, 20, 'ink')).join('') +
    d.face(500, 500, 180));

  A.add('lemon', 'Lemon', { main: Y, accent: G, pink: P }, d =>
    leaf(d, 640, 330, -35) +
    d.P('M160 545 Q170 495 220 475 C300 325 700 325 780 475 Q830 495 840 545 Q830 595 780 615 C700 765 300 765 220 615 Q170 595 160 545 Z') +
    d.face(500, 540, 260));

  A.add('peach', 'Peach', { main: '#ffc09f', accent: G, pink: '#ff8fab' }, d =>
    d.L('M500 285 L510 235') + leaf(d, 575, 235, -25) +
    d.C(500, 565, 285) + d.L('M500 285 Q430 440 470 620') +
    d.face(560, 600, 230));

  A.add('kiwi', 'Kiwi', { main: '#a0d468', dark: BR, light: '#fffbe6', pink: P }, d =>
    d.C(500, 530, 290, 'dark') + d.C(500, 530, 245) + d.C(500, 530, 105, 'light') +
    Array.from({ length: 14 }, (_, i) => { const a = i / 14 * 2 * Math.PI; return `<ellipse cx="${500 + 150 * Math.cos(a)}" cy="${530 + 150 * Math.sin(a)}" rx="9" ry="17" fill="#111" transform="rotate(${a * 180 / Math.PI + 90} ${500 + 150 * Math.cos(a)} ${530 + 150 * Math.sin(a)})"/>`; }).join('') +
    d.face(500, 520, 120));

  A.add('mango', 'Mango', { main: '#ffb347', accent: G, pink: P }, d =>
    d.L('M430 305 L420 250') + leaf(d, 480, 250, -30) +
    d.P('M300 380 C380 250 650 250 740 400 C820 560 720 800 520 820 C330 840 220 700 240 560 C250 480 250 440 300 380 Z') +
    d.face(500, 560, 250));

  A.add('blueberries', 'Blueberries', { main: '#7aa7e8', pink: P }, d => {
    const star = (x, y) => d.P(`M${x} ${y - 38} L${x + 12} ${y - 12} L${x + 38} ${y - 10} L${x + 18} ${y + 8} L${x + 24} ${y + 34} L${x} ${y + 20} L${x - 24} ${y + 34} L${x - 18} ${y + 8} L${x - 38} ${y - 10} L${x - 12} ${y - 12} Z`, 'main');
    return d.C(500, 420, 145) + star(500, 330) + d.face(500, 450, 130) +
      d.C(355, 650, 150) + star(355, 555) + d.face(355, 680, 135) +
      d.C(645, 650, 150) + star(645, 555) + d.face(645, 680, 135);
  });

  A.add('avocado', 'Avocado', { main: '#e8f5a6', dark: '#5b8c3a', accent2: BR, pink: P }, d =>
    d.P('M500 170 C420 170 380 320 330 420 C220 560 250 870 500 880 C750 870 780 560 670 420 C620 320 580 170 500 170 Z', 'dark') +
    d.P('M500 215 C440 215 410 350 370 440 C280 570 300 830 500 840 C700 830 720 570 630 440 C590 350 560 215 500 215 Z') +
    d.C(500, 680, 115, 'accent2') + d.face(500, 450, 190));

  A.add('carrot', 'Carrot', { main: O, accent: G, pink: P }, d =>
    d.E(450, 240, 42, 110, 'accent', -20) + d.E(500, 220, 42, 120, 'accent') + d.E(550, 240, 42, 110, 'accent', 20) +
    d.P('M370 330 L630 330 Q655 365 630 425 L525 880 Q500 915 475 880 L370 425 Q345 365 370 330 Z') +
    d.Lt('M430 560 L480 560 M520 660 L560 660 M470 760 L505 760') +
    d.face(500, 430, 200));

  A.add('broccoli', 'Broccoli', { main: '#a8d86e', accent: DG, pink: P }, d =>
    d.P('M420 540 L395 850 Q500 890 605 850 L580 540 Z') +
    d.scallop(500, 390, 200, 12, 95, 'accent') + d.face(500, 400, 220));

  A.add('corn', 'Corn', { main: Y, accent: DG, pink: P }, d => {
    let k = '';
    for (let y = 250; y <= 700; y += 55) for (let x = 400; x <= 600; x += 50) {
      const t = 1 - ((y - 480) / 330) ** 2; if (t <= 0) continue;
      if (Math.abs(x - 500) < 150 * Math.sqrt(t) - 30 && !(y > 430 && y < 600)) k += `<circle cx="${x}" cy="${y}" r="9" fill="#111" opacity="0.8"/>`;
    }
    return d.E(500, 480, 150, 330) + k +
      d.P('M500 880 Q240 700 320 360 Q380 610 480 780 Z', 'accent') + d.P('M500 880 Q760 700 680 360 Q620 610 520 780 Z', 'accent') +
      d.face(500, 470, 190);
  });

  A.add('tomato', 'Tomato', { main: R, accent: G, pink: P }, d =>
    d.E(500, 575, 305, 255) +
    d.P('M500 300 L535 350 L610 330 L565 380 L620 420 L540 405 L500 450 L460 405 L380 420 L435 380 L390 330 L465 350 Z', 'accent') +
    d.face(500, 600, 270));

  A.add('cucumber', 'Cucumber', { main: G, pink: P }, d =>
    d.E(500, 530, 165, 380, 'main', -25) +
    [[430, 330], [560, 380], [600, 560], [400, 640], [500, 760], [620, 700], [380, 480]].map(([x, y]) => d.dot(x, y, 6)).join('') +
    d.face(500, 520, 190));

  A.add('pepper', 'Pepper', { main: R, accent: DG, pink: P }, d =>
    d.P('M470 350 Q480 250 560 215 L578 248 Q520 272 532 350 Z', 'accent') +
    d.P('M300 350 C200 380 200 700 330 820 Q420 885 500 840 Q580 885 670 820 C800 700 800 380 700 350 C620 320 560 360 500 350 C440 360 380 320 300 350 Z') +
    d.face(500, 590, 240));

  A.add('eggplant', 'Eggplant', { main: PU, accent: DG, pink: P }, d =>
    d.P('M565 300 C785 360 825 700 645 830 C475 950 245 830 280 650 C300 520 420 470 450 400 Q480 320 565 300 Z') +
    d.P('M520 250 L545 330 L620 300 L585 360 L650 385 L570 395 L560 450 L515 400 L455 430 L480 370 L420 340 L500 330 Z', 'accent') +
    d.face(540, 630, 230));

  A.add('pumpkin', 'Pumpkin', { main: O, accent: G, dark: DG, pink: P }, d =>
    d.R(470, 240, 60, 110, 18, 'dark') + leaf(d, 590, 280, -20) +
    d.E(500, 585, 320, 250) + d.L('M360 355 Q260 585 360 815 M640 355 Q740 585 640 815') + d.face(500, 610, 210));

  A.add('potato', 'Potato', { main: '#e0b27a', pink: P }, d =>
    d.P('M250 460 C260 330 420 300 540 320 C700 330 800 420 790 560 C780 720 620 800 480 790 C320 780 240 640 250 460 Z') +
    d.dot(330, 420, 8) + d.dot(700, 460, 8) + d.dot(650, 700, 8) + d.dot(340, 660, 8) +
    d.face(510, 560, 260));

  A.add('mushroom', 'Mushroom', { main: '#fff3d6', accent: R, light: W, pink: P }, d =>
    d.P('M390 520 L360 830 Q500 880 640 830 L610 520 Z') +
    d.P('M160 520 C160 300 330 210 500 210 C670 210 840 300 840 520 Q500 590 160 520 Z', 'accent') +
    d.C(360, 380, 45, 'light') + d.C(560, 300, 40, 'light') + d.C(680, 440, 50, 'light') + d.C(470, 460, 32, 'light') +
    d.face(500, 670, 190));

  A.add('peas', 'Peas', { main: '#a8d86e', dark: DG, pink: P }, d =>
    d.P('M120 560 C200 380 800 360 890 520 C800 700 220 720 120 560 Z', 'dark') +
    [230, 380, 530, 680].map(x => d.C(x + 20, 540, 72) + d.dot(x + 2, 530, 8) + d.dot(x + 38, 530, 8) + `<path d="M${x + 6} 556 Q${x + 20} 570 ${x + 34} 556" fill="none" stroke="#111" stroke-width="8" stroke-linecap="round"/>`).join('') +
    d.L('M890 520 Q930 470 910 420'));

  A.add('onion', 'Onion', { main: '#e3b5d8', accent: G, pink: P }, d =>
    d.L('M480 250 Q470 160 430 130 M520 250 Q540 160 580 140') +
    d.L('M450 830 L430 890 M500 840 L500 900 M550 830 L570 890') +
    d.P('M500 240 Q520 330 600 400 C780 520 740 820 500 840 C260 820 220 520 400 400 Q480 330 500 240 Z') +
    d.face(500, 610, 230));

  A.add('radish', 'Radish', { main: '#ff7aa2', accent: G, pink: '#ffd1dc' }, d =>
    leaf(d, 440, 250, -60) + leaf(d, 560, 250, -120) + d.E(500, 230, 34, 100, 'accent') +
    d.L('M500 770 Q510 840 480 910') +
    d.C(500, 560, 225) + d.face(500, 580, 220));

  A.add('coconut', 'Coconut', { main: BR, pink: P }, d =>
    d.C(500, 540, 290) + d.C(430, 330, 20, 'ink') + d.C(500, 310, 20, 'ink') + d.C(570, 330, 20, 'ink') +
    d.Lt('M300 420 L330 440 M680 440 L710 420 M300 700 L330 690 M690 700 L720 715') +
    d.face(500, 580, 260));

  A.add('lettuce', 'Lettuce', { main: '#b7e27a', accent: DG, pink: P }, d =>
    d.scallop(500, 560, 250, 14, 90, 'accent') + d.C(500, 560, 250) +
    d.L('M500 360 L500 470 M420 400 L460 470 M580 400 L540 470') + d.face(500, 600, 250));
})();
