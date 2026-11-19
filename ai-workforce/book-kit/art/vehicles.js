// "My First Cars, Trains & Planes": 30 friendly vehicles that go on roads, rails, in the air and on the water, for ages 2-5.
// Drawn from scratch: no car makers, logos, badges, liveries or characters. The ambulance carries a heart, not a
// red cross or star of life (both are protected emblems). Vehicles already drawn in other books of the series
// (toy car, toy train, toy plane, toy boat, bicycle, scooter, tricycle, skateboard, sailboat, submarine, rocket,
// hot air balloon, safari truck, camper, tractor, canoe, sled) are left out, and so are trucks (the owner's own book).
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59',
    GR = '#cfd8dc', DGR = '#90a4ae', W = '#ffffff', CREAM = '#fff3d6', PURPLE = '#b39ddb', NAVY = '#5c6bc0', TEAL = '#4dd0c4',
    GLASS = '#d6f0ff', TIRE = '#546e7a';

  // the fill colour core.js gives a palette key (white in coloring mode)
  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (masts, poles, oars): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'dark', w = 50) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 28}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const wheel = (d, x, y, r = 85) => d.C(x, y, r, 'tire') + d.C(x, y, r * 0.42, 'hub');
  const wheels = (d, xs, y, r) => xs.map(x => wheel(d, x, y, r)).join('');
  // a car body: cabin with two windows on top of a long rounded body
  const carBody = (d, k = 'main') =>
    d.P('M270 492 L350 335 Q368 300 410 300 L600 300 Q642 300 660 335 L740 492 Z', k) +
    d.P('M330 474 L392 352 Q402 335 420 335 L486 335 L486 474 Z', 'light') +
    d.P('M524 474 L524 335 L590 335 Q608 335 618 352 L680 474 Z', 'light') +
    d.R(120, 480, 760, 200, 80, k);

  // ---------------- on the road ----------------
  A.add('car', 'Car', { main: R, light: GLASS, accent: Y, tire: TIRE, hub: GR, pink: P }, d =>
    carBody(d) +
    d.E(852, 548, 26, 34, 'accent') + d.R(108, 540, 40, 50, 14, 'accent') +
    wheels(d, [300, 700], 690, 88) +
    d.face(500, 572, 150));

  A.add('race-car', 'Race Car', { main: Y, dark: NAVY, accent: R, light: GLASS, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(118, 450, 40, 120, 12, 'dark') + d.R(80, 420, 170, 46, 14, 'accent') +
    d.C(530, 470, 78, 'accent') + d.P('M470 455 Q530 420 590 455 L590 480 L470 480 Z', 'light') +
    d.P('M110 655 Q110 565 200 552 L420 545 Q445 488 530 488 Q615 488 640 545 L830 560 Q915 572 915 645 Q915 695 865 695 L155 695 Q110 695 110 655 Z') +
    d.C(400, 618, 44, 'light') +
    wheels(d, [260, 760], 700, 82) +
    d.face(560, 612, 110));

  A.add('bus', 'Bus', { main: B, light: GLASS, accent: Y, dark: NAVY, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(110, 290, 780, 430, 60) +
    [140, 275, 410, 545].map(x => d.R(x, 345, 110, 130, 18, 'light')).join('') +
    d.R(700, 345, 150, 330, 16, 'light') + d.Lt('M775 355 L775 665') +
    d.R(110, 515, 590, 34, 0, 'accent') +
    d.E(668, 690, 18, 14, 'accent') +
    wheels(d, [250, 610], 725, 80) +
    d.face(420, 615, 120));

  A.add('school-bus', 'School Bus', { main: Y, light: GLASS, dark: '#555', accent: R, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(690, 470, 220, 250, 40) + d.R(885, 540, 40, 60, 14, 'light') +
    d.R(100, 290, 640, 430, 46) +
    [140, 290, 440].map(x => d.R(x, 340, 115, 125, 18, 'light')).join('') +
    d.R(590, 340, 110, 300, 14, 'light') + d.Lt('M645 350 L645 630') +
    d.Lt('M110 520 L585 520 M110 556 L585 556') +
    wheels(d, [250, 790], 725, 80) +
    d.face(400, 640, 115));

  A.add('taxi', 'Taxi', { main: Y, light: GLASS, dark: '#555', accent: O, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(430, 240, 140, 70, 16, 'accent') +
    carBody(d) +
    Array.from({ length: 10 }, (_, i) => d.R(190 + i * 62, 506, 62, 32, 0, i % 2 ? 'dark' : 'main')).join('') +
    d.E(852, 560, 26, 34, 'accent') +
    wheels(d, [300, 700], 690, 88) +
    d.face(500, 600, 130));

  A.add('police-car', 'Police Car', { main: W, dark: NAVY, light: GLASS, accent: B, accent2: R, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(420, 248, 80, 60, 18, 'accent') + d.R(500, 248, 80, 60, 18, 'accent2') +
    carBody(d) +
    d.R(120, 498, 760, 40, 0, 'dark') +
    d.poly(Array.from({ length: 10 }, (_, i) => { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? 22 : 50; return [445 + r * Math.cos(a), 600 + r * Math.sin(a)]; }), 'accent') +
    wheels(d, [300, 700], 690, 88) +
    d.face(612, 604, 108));

  A.add('ambulance', 'Ambulance', { main: W, accent: R, accent2: Y, light: GLASS, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(310, 230, 110, 56, 18, 'accent') +
    d.R(100, 275, 570, 430, 40) +
    d.P('M660 705 L660 385 Q660 352 692 352 L776 352 Q808 352 826 390 L890 520 Q902 545 902 575 L902 665 Q902 705 862 705 Z') +
    d.P('M694 386 L772 386 L834 500 L694 500 Z', 'light') +
    d.R(100, 560, 570, 34, 0, 'accent') +
    d.P('M250 482 C140 405 182 318 250 368 C318 318 360 405 250 482 Z', 'accent') +
    d.E(880, 600, 18, 26, 'accent2') +
    wheels(d, [260, 740], 712, 80) +
    d.face(500, 425, 135));

  A.add('motorcycle', 'Motorcycle', { main: O, dark: '#555', light: GR, accent: Y, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(220, 600, 330, 44, 22, 'light') +
    tube(d, ['M650 470 L770 700', 'M650 470 L615 360', 'M570 360 L665 360'], 'dark', 44) +
    d.C(722, 470, 34, 'accent') +
    d.R(285, 438, 240, 56, 28, 'dark') +
    d.P('M300 572 Q320 478 420 470 L640 462 Q706 466 716 525 L688 606 L332 624 Z') +
    wheel(d, 230, 700, 118) + wheel(d, 770, 700, 118) +
    d.face(512, 540, 110));

  A.add('ice-cream-van', 'Ice Cream Van', { main: W, accent: P, accent2: B, light: GLASS, cone: '#e8b97a', tire: TIRE, hub: GR, pink: P }, d =>
    d.poly([[398, 178], [542, 178], [470, 300]], 'cone') + d.Lt('M430 210 L506 262 M510 210 L446 254') + d.C(470, 140, 74, 'accent') +
    d.R(100, 275, 570, 430, 40) +
    d.P('M660 705 L660 385 Q660 352 692 352 L776 352 Q808 352 826 390 L890 520 Q902 545 902 575 L902 665 Q902 705 862 705 Z') +
    d.P('M694 386 L772 386 L834 500 L694 500 Z', 'light') +
    d.R(190, 380, 340, 150, 18, 'light') +
    d.R(170, 335, 380, 50, 10, 'accent2') +
    [0, 1, 2, 3, 4].map(i => d.P(`M${170 + i * 76} 385 A38 38 0 0 0 ${246 + i * 76} 385 Z`, 'accent2')).join('') +
    wheels(d, [260, 740], 712, 80) +
    d.face(380, 615, 120));

  // ---------------- on the rails ----------------
  A.add('steam-train', 'Steam Train', { main: R, dark: '#555', light: GLASS, smoke: W, accent: Y, tire: TIRE, hub: GR, pink: P }, d =>
    d.C(400, 190, 42, 'smoke') + d.C(470, 135, 54, 'smoke') + d.C(570, 100, 44, 'smoke') +
    d.P('M340 390 L325 245 L425 245 L410 390 Z', 'dark') +
    d.R(600, 265, 240, 380, 26) + d.R(580, 235, 280, 50, 20, 'dark') + d.R(655, 310, 130, 110, 18, 'light') +
    d.R(290, 380, 420, 220, 70) +
    d.C(310, 490, 34, 'accent') +
    d.poly([[300, 600], [215, 690], [330, 690]], 'dark') +
    d.R(255, 590, 610, 50, 20, 'dark') +
    wheel(d, 400, 690, 72) + wheel(d, 560, 690, 72) + wheel(d, 750, 680, 88) +
    d.face(490, 492, 130));

  A.add('train-engine', 'Train Engine', { main: G, dark: '#555', light: GLASS, accent: Y, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(250, 285, 400, 60, 20, 'dark') +
    d.R(140, 640, 300, 50, 20, 'dark') + d.R(560, 640, 300, 50, 20, 'dark') +
    d.R(110, 330, 780, 330, 50) +
    d.R(170, 385, 120, 100, 16, 'light') + d.R(330, 385, 120, 100, 16, 'light') +
    d.R(725, 385, 125, 120, 20, 'light') +
    d.R(110, 560, 780, 34, 0, 'accent') +
    d.E(870, 620, 16, 20, 'accent') +
    wheels(d, [210, 370, 630, 790], 705, 50) +
    d.face(590, 450, 115));

  A.add('high-speed-train', 'High-Speed Train', { main: W, accent: B, accent2: R, light: GLASS, tire: TIRE, hub: GR, pink: P }, d =>
    d.P('M110 360 L600 360 Q760 360 880 560 Q905 605 860 640 L110 640 Z') +
    d.P('M640 382 Q735 392 800 484 L640 484 Z', 'light') +
    [160, 290, 420].map(x => d.R(x, 405, 100, 72, 14, 'light')).join('') +
    d.P('M110 590 L870 590 Q878 610 860 625 L110 625 Z', 'accent') +
    wheels(d, [200, 320, 620, 740], 665, 40) +
    d.face(580, 528, 112));

  A.add('caboose', 'Caboose', { main: R, dark: '#555', light: GLASS, accent: Y, tire: TIRE, hub: GR, pink: P }, d =>
    d.R(370, 268, 260, 42, 16, 'dark') + d.R(390, 296, 220, 104, 16) + d.R(448, 318, 104, 56, 12, 'light') +
    d.L('M200 500 L132 500 L132 650 M800 500 L868 500 L868 650') +
    d.R(200, 400, 600, 260, 30) +
    d.R(168, 378, 664, 48, 20, 'dark') +
    d.R(250, 460, 115, 100, 16, 'light') + d.R(635, 460, 115, 100, 16, 'light') +
    d.R(150, 650, 700, 40, 16, 'dark') +
    wheels(d, [300, 700], 712, 60) +
    d.face(500, 532, 140));

  A.add('tram', 'Tram', { main: O, dark: '#555', light: GLASS, accent: Y, tire: TIRE, hub: GR, pink: P }, d =>
    d.L('M500 270 L440 190 L560 145') + d.R(450, 118, 160, 26, 12, 'dark') +
    d.R(220, 262, 560, 46, 20, 'dark') +
    d.R(160, 290, 680, 425, 60) +
    [215, 425, 635].map(x => d.R(x, 350, 150, 140, 20, 'light')).join('') +
    d.R(160, 545, 680, 36, 0, 'accent') +
    d.L('M90 772 L910 772') +
    wheels(d, [290, 710], 722, 50) +
    d.face(500, 640, 120));

  A.add('cable-car', 'Cable Car', { main: R, dark: '#555', light: GLASS, accent: Y, pink: P }, d =>
    d.L('M70 165 L930 95') +
    tube(d, ['M500 150 L500 300'], 'dark', 46) +
    d.R(420, 100, 160, 56, 22, 'dark') +
    d.R(235, 275, 530, 60, 30, 'dark') +
    d.R(260, 300, 480, 420, 70) +
    d.R(305, 360, 175, 160, 24, 'light') + d.R(520, 360, 175, 160, 24, 'light') +
    d.face(500, 620, 140));

  // ---------------- in the air ----------------
  A.add('airplane', 'Airplane', { main: W, accent: B, accent2: R, light: GLASS, pink: P }, d =>
    d.P('M160 445 L110 250 L235 250 L330 445 Z', 'accent2') +
    d.P('M90 525 Q92 440 205 432 L760 432 Q900 442 922 525 Q900 606 760 614 L205 614 Q92 606 90 525 Z') +
    [290, 360, 430, 500, 570, 640].map(x => d.C(x, 490, 18, 'light')).join('') +
    d.P('M792 468 Q852 470 884 502 L792 502 Z', 'light') +
    d.P('M410 550 L560 550 L470 770 L385 770 Z', 'accent') +
    d.face(720, 556, 108));

  A.add('propeller-plane', 'Propeller Plane', { main: Y, accent: R, dark: '#555', light: GLASS, pink: P }, d =>
    d.R(130, 410, 740, 140, 60, 'accent') +
    d.R(330, 765, 340, 72, 32, 'accent') +
    d.P('M500 168 Q592 200 592 420 L578 790 Q560 850 500 856 Q440 850 422 790 L408 420 Q408 200 500 168 Z') +
    d.E(500, 145, 150, 24, 'dark') + d.C(500, 160, 28, 'dark') +
    d.E(500, 340, 52, 66, 'light') +
    d.face(500, 560, 110));

  A.add('biplane', 'Biplane', { main: R, accent: Y, dark: '#555', light: GLASS, tire: TIRE, hub: GR, pink: P }, d =>
    d.L('M330 345 L330 565 M670 345 L670 565') +
    d.R(255, 296, 490, 52, 24, 'accent') +
    d.P('M150 450 L118 300 L232 300 L292 425 Z') +
    d.P('M120 472 Q140 410 262 402 L742 410 Q832 420 842 472 Q832 522 742 532 L262 542 Q140 534 120 472 Z') +
    d.L('M450 545 L420 680 M600 540 L630 680') +
    d.R(255, 560, 490, 52, 24, 'accent') +
    d.C(852, 472, 26, 'dark') + d.E(880, 472, 20, 120, 'light') +
    wheel(d, 420, 705, 42) + wheel(d, 630, 705, 42) +
    d.face(560, 468, 108));

  A.add('seaplane', 'Seaplane', { main: TEAL, accent: Y, dark: '#555', light: GLASS, float: W, pink: P }, d =>
    d.P('M170 462 L140 300 L250 300 L320 432 Z', 'accent') +
    d.L('M420 588 L400 672 M660 588 L680 672') +
    d.P('M150 505 Q160 422 300 420 L700 420 Q800 430 820 505 Q800 580 700 590 L300 590 Q160 582 150 505 Z') +
    d.R(330, 382, 340, 42, 20, 'accent') +
    d.P('M540 430 Q640 430 690 482 L540 482 Z', 'light') +
    d.C(830, 505, 28, 'dark') + d.E(856, 505, 20, 122, 'light') +
    d.P('M280 668 L760 668 Q820 668 820 700 Q820 726 760 726 L300 726 Q260 726 260 700 Z', 'float') +
    d.water(800) +
    d.face(400, 515, 112));

  A.add('helicopter', 'Helicopter', { main: Y, accent: R, dark: '#555', light: GLASS, pink: P }, d =>
    tube(d, ['M660 470 L885 418'], 'main', 64) +
    d.C(895, 408, 52, 'accent') + d.Lt('M895 362 L895 454 M850 408 L940 408') +
    d.L('M370 690 L345 768 M600 690 L625 768') + d.R(250, 755, 470, 32, 16, 'dark') +
    d.R(450, 290, 44, 70, 12, 'dark') + d.R(150, 262, 650, 38, 19, 'accent') +
    d.E(470, 525, 250, 190) +
    d.P('M300 430 Q330 360 452 350 L452 560 L282 560 Q262 500 300 430 Z', 'light') +
    d.face(582, 545, 118));

  A.add('blimp', 'Blimp', { main: B, accent: Y, dark: '#555', light: GLASS, pink: P }, d =>
    d.P('M190 400 L110 285 L270 335 Z', 'accent') + d.P('M190 500 L110 615 L270 565 Z', 'accent') +
    d.R(395, 600, 210, 92, 26) + d.R(425, 625, 60, 42, 10, 'light') + d.R(515, 625, 60, 42, 10, 'light') +
    d.E(500, 450, 360, 190) +
    d.band(500, 450, 360, 190, 230, 290, 'accent') +
    d.face(560, 450, 170));

  A.add('jet', 'Jet', { main: W, accent: B, accent2: R, light: GLASS, pink: P }, d =>
    d.poly([[440, 420], [130, 650], [140, 712], [440, 610]], 'accent') +
    d.poly([[560, 420], [870, 650], [860, 712], [560, 610]], 'accent') +
    d.poly([[445, 745], [318, 846], [328, 888], [445, 836]], 'accent2') +
    d.poly([[555, 745], [682, 846], [672, 888], [555, 836]], 'accent2') +
    d.P('M500 115 Q565 220 565 400 L565 770 Q565 830 500 850 Q435 830 435 770 L435 400 Q435 220 500 115 Z') +
    d.E(500, 300, 40, 80, 'light') +
    d.face(500, 520, 100));

  // ---------------- on the water ----------------
  A.add('tugboat', 'Tugboat', { main: R, dark: '#555', light: GLASS, accent: Y, hull: B, pink: P }, d =>
    d.R(450, 245, 90, 150, 16, 'accent') + d.R(450, 275, 90, 32, 0, 'dark') +
    d.R(370, 400, 320, 210, 24) + d.R(350, 380, 360, 42, 16, 'dark') +
    d.R(405, 442, 110, 80, 14, 'light') + d.R(545, 442, 110, 80, 14, 'light') +
    d.P('M110 600 L890 600 L820 742 L180 742 Z', 'hull') +
    d.C(230, 650, 28, 'dark') + d.C(770, 650, 28, 'dark') +
    d.water(805) +
    d.face(500, 665, 112));

  A.add('ferry', 'Ferry', { main: W, accent: R, dark: '#555', light: GLASS, hull: B, pink: P }, d =>
    d.R(565, 215, 72, 120, 14, 'accent') +
    d.R(300, 322, 400, 110, 20) +
    [335, 435, 535, 615].map(x => d.R(x, 350, 60, 50, 10, 'light')).join('') +
    d.R(165, 420, 670, 150, 20) +
    [205, 310, 415, 520, 625, 730].map(x => d.R(x, 458, 66, 60, 12, 'light')).join('') +
    d.P('M90 560 L910 560 L860 702 L140 702 Z', 'hull') +
    d.water(770) +
    d.face(500, 624, 110));

  A.add('cruise-ship', 'Cruise Ship', { main: W, accent: R, dark: '#555', light: GLASS, hull: NAVY, pink: P }, d =>
    d.P('M560 265 L580 160 L690 160 L670 265 Z', 'accent') +
    d.R(360, 255, 310, 104, 16) +
    [400, 490, 580].map(x => d.R(x, 286, 56, 42, 10, 'light')).join('') +
    d.R(250, 348, 530, 112, 16) +
    [290, 380, 470, 560, 650].map(x => d.R(x, 382, 56, 42, 10, 'light')).join('') +
    d.R(160, 450, 710, 122, 16) +
    Array.from({ length: 8 }, (_, i) => d.R(195 + i * 80, 488, 50, 42, 10, 'light')).join('') +
    d.P('M80 562 L920 562 Q920 640 860 702 L160 702 Q80 640 80 562 Z', 'hull') +
    d.water(770) +
    d.face(500, 624, 110));

  A.add('speedboat', 'Speedboat', { main: R, accent: Y, dark: '#555', light: GLASS, pink: P }, d =>
    d.Lt('M50 610 L14 586 M50 660 L8 676') +
    d.R(48, 512, 66, 150, 16, 'dark') +
    d.P('M560 520 L615 395 L735 395 L715 520 Z', 'light') +
    d.P('M100 512 L830 512 Q950 512 912 600 L862 692 Q850 712 822 712 L172 712 Q138 712 128 686 L100 512 Z') +
    d.P('M118 640 L878 640 L860 670 L124 670 Z', 'accent') +
    d.water(790) +
    d.face(420, 572, 118));

  A.add('fishing-boat', 'Fishing Boat', { main: G, accent: R, dark: '#555', light: GLASS, hull: O, pink: P }, d =>
    tube(d, ['M300 585 L300 250', 'M300 320 L170 480'], 'dark', 40) +
    d.P('M300 250 L392 282 L300 314 Z', 'accent') +
    d.R(540, 390, 260, 38, 14, 'dark') + d.R(560, 410, 220, 190, 20) + d.R(600, 452, 140, 72, 12, 'light') +
    d.P('M120 580 L880 580 L800 722 L200 722 Z', 'hull') +
    d.water(785) +
    d.face(450, 645, 108));

  A.add('rowboat', 'Rowboat', { main: BR, dark: '#7a4a2e', light: CREAM, accent: Y, pink: P }, d =>
    tube(d, ['M180 410 L355 745', 'M820 410 L645 745'], 'dark', 44) +
    d.E(368, 775, 34, 64, 'light', -28) + d.E(632, 775, 34, 64, 'light', 28) +
    d.P('M100 520 Q500 600 900 520 Q860 712 500 722 Q140 712 100 520 Z') +
    d.Lt('M160 600 Q500 660 840 600') +
    d.water(830) +
    d.face(500, 664, 104));

  A.add('kayak', 'Kayak', { main: Y, dark: '#555', accent: R, light: GR, pink: P }, d =>
    tube(d, ['M255 300 L745 800'], 'dark', 40) +
    d.E(225, 268, 46, 90, 'accent', -45) + d.E(775, 832, 46, 90, 'accent', -45) +
    d.P('M70 540 Q500 380 930 540 Q500 720 70 540 Z') +
    d.E(500, 494, 110, 26, 'dark') +
    d.face(500, 572, 100));

  A.add('hovercraft', 'Hovercraft', { main: O, dark: '#555', light: GLASS, accent: Y, skirt: GR, pink: P }, d =>
    d.C(800, 400, 112, 'accent') + d.C(800, 400, 72, 'light') + d.Lt('M800 336 L800 464 M736 400 L864 400') +
    d.P('M120 642 Q120 562 200 562 L800 562 Q880 562 880 642 Q880 722 800 722 L200 722 Q120 722 120 642 Z', 'skirt') +
    d.R(215, 400, 525, 180, 40) +
    d.R(265, 438, 115, 82, 16, 'light') + d.R(410, 438, 115, 82, 16, 'light') +
    d.water(792) +
    d.face(632, 488, 108));
})();
