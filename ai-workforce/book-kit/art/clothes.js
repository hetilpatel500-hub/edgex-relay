// "My First Clothes": 30 friendly things to wear, for ages 2-5.
// Everyday clothes, shoes, hats and accessories drawn from scratch: no brands, logos,
// characters or designer looks. Items already in other books of the series (rain boots,
// raincoat, mittens, winter hat, sunglasses, pajamas, slippers, sneaker, cap, Santa hat,
// Christmas sweater, earmuffs, wizard hat, crown, glass slipper) are left out.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59', DB = '#8d5a3b',
    GR = '#cfd8dc', PU = '#b39ddb', LPU = '#e1d5ff', W = '#ffffff', CREAM = '#fff3d6', NAVY = '#5c7cfa', DEN = '#7fa7e0', TEAL = '#5ccfc4', MINT = '#b9f3e4';

  const f = v => +v.toFixed(1);
  const group = (s, rot, cx = 500, cy = 500) => `<g transform="rotate(${rot} ${cx} ${cy})">${s}</g>`;
  const tr = (s, dx, dy, sc = 1) => `<g transform="translate(${dx} ${dy}) scale(${sc})">${s}</g>`;
  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (handles, straps, ribbons): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'main', w = 56) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const star = (d, cx, cy, r, k = 'accent') => d.poly([...Array(10)].map((_, i) => {
    const a = (-90 + i * 36) * Math.PI / 180, rr = i % 2 ? r * 0.45 : r; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
  }), k);
  const heart = (d, cx, cy, s, k = 'accent') =>
    d.P(`M${cx} ${f(cy + s * 0.9)} C${f(cx - s * 1.3)} ${f(cy + s * 0.1)} ${f(cx - s * 0.75)} ${f(cy - s * 0.95)} ${cx} ${f(cy - s * 0.35)} C${f(cx + s * 0.75)} ${f(cy - s * 0.95)} ${f(cx + s * 1.3)} ${f(cy + s * 0.1)} ${cx} ${f(cy + s * 0.9)} Z`, k);
  // mirror a path (or an x) across the page centre, for left/right pairs
  const mirP = (p, m) => m ? p.replace(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g, (_, x, y) => f(1000 - x) + ' ' + y) : p;
  const mirX = (x, m, w = 0) => m ? f(1000 - x - w) : x;

  // ---------------- tops ----------------
  A.add('t-shirt', 'T-Shirt', { main: R, accent: Y, pink: P }, d =>
    d.poly([[410, 190], [590, 190], [700, 215], [855, 360], [770, 450], [690, 390], [690, 845], [310, 845], [310, 390], [230, 450], [145, 360], [300, 215]]) +
    d.poly([[790, 300], [855, 360], [770, 450], [710, 392]], 'accent') + d.poly([[210, 300], [145, 360], [230, 450], [290, 392]], 'accent') +
    d.P('M400 188 Q500 305 600 188 L565 184 Q500 258 435 184 Z', 'accent') +
    d.face(500, 560, 250));

  A.add('shirt', 'Shirt', { main: B, accent: W, light: Y, pink: P }, d =>
    d.poly([[400, 200], [600, 200], [700, 225], [835, 650], [745, 690], [690, 430], [690, 860], [310, 860], [310, 430], [255, 690], [165, 650], [300, 225]]) +
    d.poly([[812, 575], [835, 650], [745, 690], [725, 610]], 'accent') + d.poly([[188, 575], [165, 650], [255, 690], [275, 610]], 'accent') +
    d.poly([[395, 196], [500, 292], [425, 345], [365, 225]], 'accent') + d.poly([[605, 196], [500, 292], [575, 345], [635, 225]], 'accent') +
    d.L('M500 600 L500 860') + d.C(500, 640, 17, 'light') + d.C(500, 730, 17, 'light') + d.C(500, 815, 17, 'light') +
    d.face(500, 460, 200));

  A.add('hoodie', 'Hoodie', { main: G, dark: DG, light: W, accent: Y, pink: P }, d =>
    d.P('M330 320 Q290 110 500 100 Q710 110 670 320 Z') + d.E(500, 230, 120, 95, 'light') +
    d.poly([[380, 300], [620, 300], [700, 320], [835, 640], [748, 690], [690, 520], [690, 860], [310, 860], [310, 520], [252, 690], [165, 640], [300, 320]]) +
    d.poly([[812, 585], [835, 640], [748, 690], [728, 632]], 'accent') + d.poly([[188, 585], [165, 640], [252, 690], [272, 632]], 'accent') +
    d.R(300, 815, 400, 60, 20, 'accent') +
    d.P('M375 650 L625 650 L665 800 L335 800 Z', 'light') +
    d.Lt('M455 318 L447 420 M545 318 L553 420') + d.C(447, 432, 15, 'accent') + d.C(553, 432, 15, 'accent') +
    d.face(500, 540, 190));

  A.add('jacket', 'Jacket', { main: O, accent: DB, light: W, dark: BR, pink: P }, d =>
    d.poly([[385, 205], [615, 205], [700, 228], [835, 640], [748, 690], [690, 470], [690, 840], [310, 840], [310, 470], [252, 690], [165, 640], [300, 228]]) +
    d.poly([[812, 585], [835, 640], [748, 690], [728, 632]], 'accent') + d.poly([[188, 585], [165, 640], [252, 690], [272, 632]], 'accent') +
    d.R(300, 790, 400, 62, 22, 'accent') +
    d.P('M380 205 L420 305 L500 335 L580 305 L620 205 L595 180 L500 225 L405 180 Z', 'accent') +
    d.L('M500 335 L500 790') + d.R(486, 345, 28, 64, 9, 'light') +
    d.L('M360 650 L415 555 M640 650 L585 555') +
    d.R(355, 400, 90, 70, 14, 'light') + d.R(555, 400, 90, 70, 14, 'light'));

  A.add('coat', 'Coat', { main: PU, accent: CREAM, light: Y, pink: P }, d =>
    d.poly([[380, 200], [620, 200], [700, 225], [835, 620], [748, 670], [690, 520], [722, 900], [278, 900], [310, 520], [252, 670], [165, 620], [300, 225]]) +
    d.poly([[812, 565], [835, 620], [748, 670], [728, 612]], 'accent') + d.poly([[188, 565], [165, 620], [252, 670], [272, 612]], 'accent') +
    d.P('M380 200 L500 320 L620 200 L665 245 L500 400 L335 245 Z', 'accent') +
    d.C(440, 620, 24, 'light') + d.C(560, 620, 24, 'light') + d.C(440, 720, 24, 'light') + d.C(560, 720, 24, 'light') +
    d.C(440, 820, 24, 'light') + d.C(560, 820, 24, 'light') +
    d.face(500, 480, 160));

  A.add('bathrobe', 'Bathrobe', { main: TEAL, accent: W, accent2: Y, pink: P }, d =>
    d.poly([[380, 190], [620, 190], [720, 230], [860, 560], [760, 610], [700, 480], [722, 885], [278, 885], [300, 480], [240, 610], [140, 560], [280, 230]]) +
    d.poly([[832, 495], [860, 560], [760, 610], [735, 548]], 'accent') + d.poly([[168, 495], [140, 560], [240, 610], [265, 548]], 'accent') +
    d.P('M380 190 L450 190 L500 420 L550 190 L620 190 L525 525 L475 525 Z', 'accent') +
    d.L('M625 575 L655 885') +
    d.P('M560 560 L520 690 L568 700 L588 566 Z', 'accent2') + d.P('M572 562 L630 676 L672 652 L600 552 Z', 'accent2') +
    d.R(290, 505, 420, 62, 26, 'accent2') + d.C(570, 536, 38, 'accent2') +
    d.face(430, 720, 170));

  // ---------------- dresses, skirts and play clothes ----------------
  A.add('dress', 'Dress', { main: P, accent: PU, accent2: Y, light: W, pink: R }, d =>
    d.C(330, 255, 72, 'light') + d.C(670, 255, 72, 'light') +
    d.P('M370 470 L630 470 Q760 690 820 850 Q500 905 180 850 Q240 690 370 470 Z') +
    d.P('M203 800 Q500 852 797 800 L820 850 Q500 905 180 850 Z', 'accent2') +
    d.P('M360 215 Q500 300 640 215 L652 482 L348 482 Z') +
    d.R(342, 455, 316, 52, 22, 'accent') + d.E(455, 481, 45, 28, 'accent') + d.E(545, 481, 45, 28, 'accent') + d.C(500, 481, 22, 'accent') +
    d.face(500, 650, 220));

  A.add('skirt', 'Skirt', { main: Y, accent: R, light: W, pink: P }, d =>
    d.P('M310 320 L690 320 L825 805 Q500 860 175 805 Z') +
    d.R(295, 250, 410, 85, 32, 'accent') + d.C(625, 292, 20, 'light') +
    d.Lt('M360 705 L338 822 M500 715 L500 840 M640 705 L662 822') +
    d.face(500, 510, 240));

  A.add('pants', 'Pants', { main: DEN, accent: BR, light: W, pink: P }, d =>
    d.P('M300 250 L700 250 L732 868 L545 868 L500 470 L455 868 L268 868 Z') +
    d.R(262, 815, 198, 62, 16, 'light') + d.R(540, 815, 198, 62, 16, 'light') +
    d.R(288, 180, 424, 82, 26, 'accent') +
    d.R(360, 175, 26, 92, 8, 'accent') + d.R(614, 175, 26, 92, 8, 'accent') + d.C(500, 221, 20, 'light') +
    d.face(500, 355, 170));

  A.add('shorts', 'Shorts', { main: G, accent: Y, light: W, pink: P }, d =>
    d.P('M280 380 L720 380 L772 722 L545 742 L500 600 L455 742 L228 722 Z') +
    d.R(268, 300, 464, 88, 32, 'accent') + d.C(450, 344, 13, 'light') + d.C(550, 344, 13, 'light') +
    d.face(500, 480, 175));

  A.add('overalls', 'Overalls', { main: DEN, accent: R, light: Y, pink: P }, d =>
    d.R(335, 165, 70, 250, 28, 'accent') + d.R(595, 165, 70, 250, 28, 'accent') +
    d.P('M300 560 L700 560 L722 878 L545 878 L500 690 L455 878 L278 878 Z') +
    d.R(270, 830, 202, 58, 16, 'accent') + d.R(528, 830, 202, 58, 16, 'accent') +
    d.R(338, 330, 324, 260, 34) +
    d.C(370, 365, 24, 'light') + d.C(630, 365, 24, 'light') +
    d.face(500, 460, 190));

  A.add('swimsuit', 'Swimsuit', { main: TEAL, accent: Y, pink: P }, d =>
    d.P('M362 200 L425 200 Q432 330 500 330 Q568 330 575 200 L638 200 Q662 420 640 560 Q702 690 692 762 Q600 742 500 822 Q400 742 308 762 Q298 690 360 560 Q338 420 362 200 Z') +
    d.C(415, 655, 24, 'accent') + d.C(585, 655, 24, 'accent') + d.C(500, 705, 22, 'accent') +
    d.face(500, 465, 195));

  A.add('tutu', 'Tutu', { main: P, accent: PU, accent2: Y, pink: R }, d => {
    const skirt = (x1, x2, yTop, yLo, yHi, k) => {
      const n = 11, pts = [[x1 + 150, yTop]];
      for (let i = 0; i <= 2 * n; i++) {
        const x = x1 + (x2 - x1) * i / (2 * n), bulge = 34 * Math.sin(Math.PI * i / (2 * n));
        pts.push([x, (i % 2 ? yLo : yHi) + bulge]);
      }
      pts.push([x2 - 150, yTop]);
      return d.poly(pts, k);
    };
    return d.P('M372 150 L422 150 L432 230 Q500 262 568 230 L578 150 L628 150 L652 420 L348 420 Z') +
      skirt(150, 850, 430, 695, 640, 'accent') + skirt(210, 790, 430, 625, 585, 'main') +
      d.R(328, 395, 344, 70, 30, 'accent2') + star(d, 500, 430, 30, 'main') +
      d.face(500, 312, 150);
  });

  A.add('apron', 'Apron', { main: R, accent: W, accent2: Y, light: W, pink: P }, d =>
    d.L('M405 232 Q500 100 595 232') +
    d.P('M302 448 Q240 520 200 600 L238 622 Q270 545 318 470 Z', 'accent2') + d.P('M698 448 Q760 520 800 600 L762 622 Q730 545 682 470 Z', 'accent2') +
    d.R(380, 220, 240, 230, 32) + heart(d, 500, 335, 52, 'accent') +
    d.P('M300 440 L700 440 L742 860 Q500 902 258 860 Z') +
    d.R(285, 420, 430, 52, 22, 'accent2') +
    d.R(405, 690, 190, 120, 22, 'light') +
    d.face(500, 565, 190));

  A.add('bib', 'Bib', { main: Y, accent: B, light: W, pink: P }, d =>
    d.P('M378 300 C378 150 622 150 622 300 L572 300 C572 212 428 212 428 300 Z', 'accent') + d.C(600, 205, 18, 'light') +
    d.P('M500 872 C250 872 180 642 220 462 C240 352 330 300 380 300 Q400 402 500 402 Q600 402 620 300 C670 300 760 352 780 462 C820 642 750 872 500 872 Z') +
    d.face(500, 610, 250));

  // ---------------- shoes and socks ----------------
  A.add('socks', 'Socks', { main: W, accent: B, accent2: R, pink: P }, d => {
    const one = m => d.P(mirP('M540 180 L720 180 L720 560 Q720 590 750 605 L820 640 Q890 680 860 745 Q830 800 760 780 L590 735 Q540 715 540 660 Z', m)) +
      d.P(mirP('M800 628 L820 640 Q890 680 860 745 Q845 772 815 783 Q840 700 800 628 Z', m), 'accent2') +
      d.P(mirP('M540 640 L540 660 Q540 715 590 735 L640 748 Q600 680 540 640 Z', m), 'accent2') +
      d.R(mirX(540, m, 180), 515, 180, 42, 0, 'accent') +
      d.R(mirX(524, m, 212), 160, 212, 92, 32, 'accent') +
      d.face(mirX(630, m), 400, 135);
    return one(false) + one(true);
  });

  A.add('shoes', 'Shoes', { main: R, dark: DB, accent: Y, light: W, pink: P }, d => {
    const shoe = d.P('M180 668 Q172 470 330 470 L420 470 Q520 470 600 520 Q800 556 832 668 Z') +
      d.E(372, 476, 82, 22, 'light') +
      d.R(158, 648, 694, 62, 30, 'dark') +
      d.P('M418 476 L468 470 L566 610 L516 628 Z', 'accent') + d.C(542, 606, 22, 'light') +
      d.face(690, 600, 115);
    return tr(shoe, -10, -185) + tr(shoe, 20, 125);
  });

  A.add('sandals', 'Sandals', { main: BR, accent: O, light: Y, pink: P }, d => {
    const one = m => d.P(mirP('M650 190 C760 190 792 300 782 400 C772 500 742 560 752 650 C762 760 722 852 650 852 C578 852 543 760 553 650 C563 560 523 500 518 400 C508 300 540 190 650 190 Z', m)) +
      d.R(mirX(512, m, 276), 300, 276, 62, 26, 'accent') +
      d.R(mirX(520, m, 256), 470, 256, 62, 26, 'accent') + d.R(mirX(732, m, 42), 480, 42, 42, 8, 'light') +
      d.face(mirX(652, m), 715, 125);
    return one(false) + one(true);
  });

  A.add('flip-flops', 'Flip-Flops', { main: Y, accent: B, pink: P }, d => {
    const one = m => d.P(mirP('M650 190 C760 190 792 300 782 400 C772 500 742 560 752 650 C762 760 722 852 650 852 C578 852 543 760 553 650 C563 560 523 500 518 400 C508 300 540 190 650 190 Z', m)) +
      tube(d, [mirP('M650 300 L548 478', m), mirP('M650 300 L752 478', m)], 'accent', 50) +
      d.C(mirX(650, m), 300, 22, 'accent') +
      d.face(mirX(652, m), 690, 125);
    return one(false) + one(true);
  });

  A.add('ballet-shoes', 'Ballet Shoes', { main: P, light: W, accent: PU, pink: R }, d => {
    const shoe = (cx, rot) => group(d.E(cx, 600, 108, 240) + d.E(cx, 500, 66, 112, 'light') + d.face(cx, 708, 120), rot, cx, 600);
    return tube(d, ['M372 470 Q400 330 478 232', 'M628 470 Q600 330 522 232'], 'accent', 44) +
      shoe(372, 14) + shoe(628, -14) +
      d.E(430, 200, 70, 42, 'accent', -20) + d.E(570, 200, 70, 42, 'accent', 20) + d.C(500, 212, 30, 'accent');
  });

  A.add('cowboy-boot', 'Cowboy Boot', { main: BR, dark: DB, accent: Y, pink: P }, d =>
    d.P('M330 760 L462 760 L452 845 L340 845 Z', 'dark') +
    d.P('M330 170 L420 170 L465 232 L510 170 L600 170 L592 560 Q622 600 700 620 L800 650 Q872 672 862 722 Q852 762 790 762 L330 762 Z') +
    d.R(448, 744, 412, 42, 21, 'dark') +
    star(d, 470, 640, 46, 'accent') +
    d.face(465, 420, 185));

  // ---------------- hats ----------------
  A.add('sun-hat', 'Sun Hat', { main: Y, accent: R, accent2: W, light: O, pink: P }, d =>
    d.E(500, 640, 410, 125) +
    d.P('M300 630 Q300 330 500 322 Q700 330 700 630 Z') +
    d.P('M300 560 Q500 610 700 560 L702 628 Q500 680 298 628 Z', 'accent') +
    d.C(600, 600, 22, 'light') + d.C(640, 568, 30, 'accent2') + d.C(668, 610, 30, 'accent2') + d.C(628, 640, 30, 'accent2') + d.C(625, 604, 20, 'light') +
    d.face(500, 450, 190));

  A.add('top-hat', 'Top Hat', { main: GR, accent: R, light: W, pink: P }, d =>
    d.E(500, 790, 335, 82) +
    d.R(320, 230, 360, 560, 24) +
    d.R(320, 640, 360, 85, 0, 'accent') +
    d.face(500, 430, 230));

  A.add('party-hat', 'Party Hat', { main: B, accent: Y, accent2: R, light: W, pink: P }, d => {
    let frill = '';
    for (let i = 0; i < 8; i++) frill += d.C(f(292 + i * 59.4), 800, 36, 'accent2');
    return d.L('M300 800 Q500 920 700 800') +
      d.poly([[500, 190], [720, 795], [280, 795]]) +
      frill + d.R(270, 780, 460, 40, 20, 'accent2') +
      star(d, 430, 720, 26, 'accent') + star(d, 570, 720, 26, 'accent') +
      d.C(500, 180, 58, 'accent') +
      d.face(500, 560, 175);
  });

  // ---------------- warm and dressy things ----------------
  A.add('scarf', 'Scarf', { main: R, accent: W, pink: P }, d =>
    d.P('M380 430 L500 450 L470 830 L340 812 Z') + d.Lt('M352 818 L346 872 M388 823 L384 878 M424 828 L422 882 M458 832 L458 886') +
    d.P('M250 300 Q500 440 750 300 Q792 330 772 400 Q500 560 228 400 Q210 330 250 300 Z') +
    d.P('M540 440 L680 420 L742 832 L602 852 Z') +
    d.poly([[574.3, 674], [714.4, 654], [720.3, 694], [580.2, 714]], 'accent') +
    d.poly([[584.6, 744], [724.8, 724], [729.2, 754], [589, 774]], 'accent') +
    d.Lt('M612 856 L610 908 M648 851 L648 903 M684 846 L686 898 M718 841 L722 893') +
    d.face(628, 555, 120));

  A.add('gloves', 'Gloves', { main: O, accent: Y, pink: P }, d => {
    const one = m => d.E(mirX(578, m), 560, 44, 100, 'main', m ? 35 : -35) +
      d.R(mirX(566, m, 60), 232, 60, 240, 30) + d.R(mirX(631, m, 60), 200, 60, 272, 30) +
      d.R(mirX(696, m, 60), 216, 60, 256, 30) + d.R(mirX(760, m, 58), 262, 58, 210, 29) +
      d.R(mirX(560, m, 260), 400, 260, 300, 70) +
      d.R(mirX(574, m, 232), 680, 232, 120, 32, 'accent') +
      d.face(mirX(690, m), 545, 135);
    return one(false) + one(true);
  });

  A.add('bow-tie', 'Bow Tie', { main: R, accent: Y, accent2: W, pink: P }, d => {
    const wing = m => d.P(mirP('M440 500 Q330 410 210 330 Q150 300 150 380 L150 620 Q150 700 210 670 Q330 590 440 500 Z', m)) +
      d.C(mirX(255, m), 425, 22, 'accent2') + d.C(mirX(250, m), 575, 22, 'accent2') + d.C(mirX(335, m), 500, 22, 'accent2');
    return wing(false) + wing(true) + d.R(415, 410, 170, 180, 50, 'accent') + d.face(500, 492, 130);
  });

  A.add('necktie', 'Necktie', { main: B, accent: NAVY, accent2: Y, pink: P }, d =>
    d.poly([[455, 270], [545, 270], [640, 760], [500, 880], [360, 760]]) +
    d.poly([[381.3, 650], [610.9, 610], [620.6, 660], [371.6, 700]], 'accent2') +
    d.poly([[428, 170], [572, 170], [547, 285], [453, 285]], 'accent') +
    d.face(500, 480, 165));

  // ---------------- bags ----------------
  A.add('backpack', 'Backpack', { main: R, accent: Y, light: W, dark: DB, pink: P }, d =>
    tube(d, ['M296 320 Q212 540 300 790', 'M704 320 Q788 540 700 790'], 'dark', 54) +
    tube(d, ['M430 270 Q430 180 500 180 Q570 180 570 270'], 'dark', 50) +
    d.R(268, 250, 464, 625, 125) +
    d.R(330, 610, 340, 215, 60, 'accent') + d.L('M372 665 L628 665') + d.R(470, 652, 26, 50, 8, 'light') +
    d.face(500, 425, 225));

  A.add('purse', 'Purse', { main: PU, accent: P, light: Y, pink: R }, d =>
    tube(d, ['M335 430 Q335 205 500 205 Q665 205 665 430'], 'accent', 56) +
    d.P('M232 420 L768 420 L828 830 Q500 882 172 830 Z') +
    d.P('M232 420 L768 420 Q758 560 500 602 Q242 560 232 420 Z', 'accent') +
    d.C(500, 600, 30, 'light') +
    d.face(500, 718, 165));
})();
