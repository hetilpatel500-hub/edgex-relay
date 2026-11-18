// "My First Helpers": 30 friendly people who help us and the things they use, for ages 2-5.
// Drawn from scratch: no real uniforms, agencies, logos, badges with words, or characters. Medical pictures carry a
// heart, never a red cross or star of life (both are protected emblems). Badges are plain stars and shields.
// Helpers already drawn in other books of the series (farmer, astronaut, knight) are left out, and so are the
// vehicles (police car, ambulance, school bus and the trucks book). People share one body so the book feels like a set;
// each helper is told apart by a hat, an outfit and one big thing they hold. Hair styles vary from page to page.
(function () {
  const A = (typeof window !== 'undefined' ? window : globalThis).ART;
  const Y = '#ffd23f', O = '#ff9f43', R = '#ff6b6b', P = '#ffb3c7', B = '#6ec6ff', G = '#7bd389', DG = '#43a36b', BR = '#c68b59',
    GR = '#cfd8dc', DGR = '#90a4ae', W = '#ffffff', CREAM = '#fff3d6', PURPLE = '#b39ddb', NAVY = '#5c6bc0', TEAL = '#4dd0c4',
    DB = '#8d6e63', DEN = '#7e9cd8', LB = '#bfe6ff', GLASS = '#d6f0ff';
  // a few skin and hair colours for the cover, so the helpers don't all look alike
  const SK = ['#f6c9a8', '#e8b48c', '#c68642', '#8d5524'], HR = ['#5d4037', '#212121', '#ffb74d', '#8d6e63', '#3e2723'];

  const col = (d, k) => /fill="([^"]+)"/.exec(d.C(0, 0, 1, k))[1];
  // thick tubes (hoses, handles, straps): a black stroke, then a coloured stroke on top
  const tube = (d, paths, k = 'dark', w = 46) => {
    const c = col(d, k);
    return paths.map(p => `<path d="${p}" fill="none" stroke="#111" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`).join('') +
      paths.map(p => `<path d="${p}" fill="none" stroke="${c}" stroke-width="${w - 26}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
  };
  const star = (d, cx, cy, r, k = 'accent2') => {
    const pts = [];
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
    return d.poly(pts, k);
  };
  const heart = (d, x, y, s, k = 'accent') =>
    d.P(`M${x} ${y + s * 0.9} C${x - s * 1.25} ${y + s * 0.05} ${x - s * 0.75} ${y - s * 0.85} ${x} ${y - s * 0.3} C${x + s * 0.75} ${y - s * 0.85} ${x + s * 1.25} ${y + s * 0.05} ${x} ${y + s * 0.9} Z`, k);

  // ---- hair (drawn around the head) ----
  const HAIR = {
    // back pieces go behind the head and body
    back: {
      long: d => d.P('M370 360 Q352 590 404 640 L596 640 Q648 590 630 360 Z', 'hair'),
      bun: d => d.C(500, 228, 56, 'hair'),
      pony: d => d.E(648, 410, 44, 92, 'hair', -22),
      curly: d => [200, 225, 250, 270, 290, 315, 340].map(a => {
        const t = a * Math.PI / 180; return d.C(500 + 128 * Math.cos(t), 368 + 128 * Math.sin(t), 52, 'hair');
      }).join(''),
      braids: d => d.E(372, 470, 30, 70, 'hair', 10) + d.E(628, 470, 30, 70, 'hair', -10),
      none: () => '',
    },
    // front pieces sit on top of the head (under any hat)
    front: {
      short: d => d.P('M374 372 Q364 238 500 236 Q636 238 626 372 Q608 302 500 298 Q392 302 374 372 Z', 'hair'),
      long: d => d.P('M374 372 Q364 238 500 236 Q636 238 626 372 Q598 292 500 290 Q402 292 374 372 Z', 'hair'),
      none: () => '',
    },
  };

  // ---- one shared body ----
  // o.hb / o.hf: hair back / front style; o.hat: hat drawing; o.top: torso extras; o.item: thing held (drawn on top);
  // o.raise: 'r' or 'l' lifts that arm (hand ends up near 704,392 or 296,392); o.back: anything behind the person
  function person(d, o) {
    let s = (o.back ? o.back(d) : '') + HAIR.back[o.hb || 'none'](d);
    s += d.R(420, 780, 72, 90, 22, 'dark') + d.R(508, 780, 72, 90, 22, 'dark');
    s += d.R(398, 846, 104, 52, 24, 'shoe') + d.R(498, 846, 104, 52, 24, 'shoe');
    const aL = o.raise === 'l' ? d.E(342, 462, 38, 98, 'main', -38) : d.E(368, 625, 38, 98, 'main', 16);
    const aR = o.raise === 'r' ? d.E(658, 462, 38, 98, 'main', 38) : d.E(632, 625, 38, 98, 'main', -16);
    s += aL + aR;
    s += d.R(392, 492, 216, 300, 60, 'main');
    s += o.top ? o.top(d) : '';
    s += d.C(500, 368, 128, 'skin');
    s += HAIR.front[o.hf || 'none'](d);
    s += o.hat ? o.hat(d) : '';
    s += d.face(500, 392, 168);
    // hands go on last so they hold whatever is in front
    const hL = o.raise === 'l' ? [296, 392] : [346, 712], hR = o.raise === 'r' ? [704, 392] : [654, 712];
    s += o.item ? o.item(d, hL, hR) : '';
    if (!o.noHands) s += d.C(hL[0], hL[1], 34, 'skin') + d.C(hR[0], hR[1], 34, 'skin');
    return s;
  }
  const pal = (i, extra) => Object.assign({ skin: SK[i % SK.length], hair: HR[i % HR.length], shoe: '#6d4c41', pink: P }, extra);

  // ---- helpers ----
  A.add('firefighter', 'Firefighter', pal(0, { main: Y, dark: Y, accent: R, accent2: '#e0e0e0', light: GR, shoe: '#424242' }), d =>
    person(d, {
      hf: 'short',
      top: d => d.R(392, 690, 216, 34, 8, 'accent2') + d.R(392, 600, 216, 34, 8, 'accent2') + d.L('M500 500 L500 790'),
      hat: d => d.E(500, 268, 196, 44, 'accent') + d.P('M384 272 Q392 138 500 138 Q608 138 616 272 Z', 'accent') +
        d.L('M500 142 L500 266') + d.P('M462 172 L538 172 L548 214 Q500 252 452 214 Z', 'accent2'),
      item: (d, l, r) => tube(d, ['M654 712 Q760 760 820 900'], 'light', 50) +
        d.P('M626 716 L640 590 L690 590 L686 716 Z', 'accent2') + d.R(640, 540, 50, 56, 12, 'accent'),
    }));

  A.add('police-officer', 'Police Officer', pal(2, { main: NAVY, dark: NAVY, accent: '#3949ab', accent2: Y, light: LB }), d =>
    person(d, {
      hf: 'short',
      top: d => d.L('M500 500 L500 790') + star(d, 450, 572, 34) + d.R(522, 556, 60, 44, 10, 'light'),
      hat: d => d.E(500, 274, 150, 34, 'accent') + d.P('M366 266 Q350 186 500 176 Q650 186 634 266 Z', 'main') +
        d.R(374, 238, 252, 36, 10, 'accent') + star(d, 500, 214, 26),
    }));

  A.add('doctor', 'Doctor', pal(1, { main: W, dark: DEN, accent: R, accent2: GR, light: B }), d =>
    person(d, {
      hb: 'none', hf: 'short',
      top: d => d.R(442, 492, 116, 120, 30, 'light') + d.L('M442 500 L500 600 L558 500') +
        d.L('M500 600 L500 790') + d.R(526, 650, 58, 50, 10) + heart(d, 555, 676, 18) +
        d.L('M450 500 Q440 610 470 640') + d.L('M550 500 Q560 610 530 640') + d.L('M470 640 Q500 680 530 640') +
        d.C(500, 706, 30, 'accent2'),
    }));

  A.add('nurse', 'Nurse', pal(3, { main: TEAL, dark: TEAL, accent: R, accent2: W, light: CREAM }), d =>
    person(d, {
      hb: 'bun', hf: 'long',
      top: d => d.L('M452 500 L500 560 L548 500') + d.R(526, 600, 62, 52, 10, 'accent2'),
      item: (d, l, r) => d.R(560, 600, 150, 190, 18, 'light') + d.R(600, 588, 70, 30, 8, 'accent2') +
        heart(d, 626, 654, 30),
    }));

  A.add('teacher', 'Teacher', pal(0, { main: PURPLE, dark: DEN, accent: G, accent2: Y, light: '#455a64' }), d =>
    person(d, {
      hb: 'long', hf: 'long', raise: 'l',
      back: d => d.R(40, 470, 300, 230, 16, 'accent2') + d.R(62, 492, 256, 186, 8, 'light') +
        d.L('M96 640 L124 540 L152 640 M108 604 L140 604') +
        d.L('M182 540 L182 640 M182 540 Q232 545 212 588 Q240 600 214 636 Q200 642 182 640 M182 588 L210 588') +
        d.L('M300 552 Q260 532 250 588 Q252 646 300 628'),
      top: d => d.L('M452 500 Q500 560 548 500'),
    }));

  A.add('mail-carrier', 'Mail Carrier', pal(2, { main: B, dark: NAVY, accent: '#3949ab', accent2: BR, light: W }), d =>
    person(d, {
      hf: 'short',
      top: d => tube(d, ['M430 500 L600 700'], 'accent2', 40),
      hat: d => d.E(500, 272, 150, 30, 'accent') + d.P('M372 268 Q362 196 500 190 Q638 196 628 268 Z', 'main'),
      item: (d, l, r) => d.R(560, 640, 180, 150, 22, 'accent2') + d.P('M560 662 Q650 740 740 662 L740 640 L560 640 Z', 'accent2') +
        d.R(240, 640, 130, 92, 8, 'light') + d.L('M240 640 L305 694 L370 640') + heart(d, 305, 700, 14),
    }));

  A.add('chef', 'Chef', pal(1, { main: W, dark: '#78909c', accent: R, accent2: GR, light: W }), d =>
    person(d, {
      hf: 'none',
      top: d => d.P('M448 494 L552 494 L500 560 Z', 'accent') + d.dot(470, 610, 12) + d.dot(530, 610, 12) +
        d.dot(470, 680, 12) + d.dot(530, 680, 12),
      hat: d => d.C(430, 170, 62, 'light') + d.C(500, 140, 70, 'light') + d.C(570, 170, 62, 'light') +
        d.R(410, 170, 180, 70, 10, 'light') + d.R(400, 228, 200, 44, 14, 'light'),
      item: (d, l, r) => tube(d, ['M654 712 L654 560'], 'accent2', 34) + d.E(654, 500, 46, 70, 'accent2'),
    }));

  A.add('delivery-driver', 'Delivery Driver', pal(3, { main: O, dark: BR, accent: '#ef6c00', accent2: CREAM, light: CREAM }), d =>
    person(d, {
      hf: 'short', noHands: true,
      hat: d => d.E(560, 276, 120, 28, 'accent') + d.P('M372 272 Q366 196 500 190 Q634 196 628 272 Z', 'main'),
      item: (d) => d.R(376, 590, 248, 200, 12, 'accent2') + d.L('M376 640 L624 640') + d.R(466, 590, 68, 50, 4, 'accent2') +
        d.C(372, 690, 34, 'skin') + d.C(628, 690, 34, 'skin'),
    }));

  A.add('builder', 'Builder', pal(2, { main: DEN, dark: DEN, accent: Y, accent2: O, light: '#e0e0e0' }), d =>
    person(d, {
      hf: 'short', raise: 'r',
      top: d => d.P('M392 552 L452 494 L452 792 L392 792 Z', 'accent2') + d.P('M608 552 L548 494 L548 792 L608 792 Z', 'accent2') +
        d.R(392, 690, 60, 26, 4, 'light') + d.R(548, 690, 60, 26, 4, 'light'),
      hat: d => d.E(500, 266, 180, 34, 'accent') + d.P('M384 268 Q390 150 500 150 Q610 150 616 268 Z', 'accent') +
        d.R(474, 150, 52, 118, 20, 'accent'),
      item: (d, l, r) => tube(d, ['M704 392 L722 196'], 'accent2', 40) + d.R(640, 132, 160, 66, 14, 'light') +
        d.P('M800 140 Q850 150 860 200 L836 200 Q826 172 800 176 Z', 'light'),
    }));

  A.add('pilot', 'Pilot', pal(4, { main: NAVY, dark: NAVY, accent: Y, accent2: W, light: '#3949ab' }), d =>
    person(d, {
      hf: 'short',
      top: d => d.R(450, 492, 100, 70, 10, 'accent2') + d.P('M482 520 L518 520 L512 640 L500 660 L488 640 Z', 'light') +
        d.P('M396 598 Q440 576 472 598 L462 616 Q430 604 396 598 Z', 'accent') + d.P('M604 598 Q560 576 528 598 L538 616 Q570 604 604 598 Z', 'accent') +
        d.R(392, 740, 216, 22, 6, 'accent'),
      hat: d => d.E(500, 272, 150, 30, 'dark') + d.P('M368 266 Q354 188 500 178 Q646 188 632 266 Z', 'accent2') +
        d.R(376, 238, 248, 34, 10, 'dark') + d.P('M450 208 Q480 196 500 214 Q520 196 550 208 L536 220 Q518 212 500 224 Q482 212 464 220 Z', 'accent'),
    }));

  A.add('vet', 'Vet', pal(0, { main: G, dark: DEN, accent: BR, accent2: CREAM, light: W }), d =>
    person(d, {
      hb: 'pony', hf: 'long',
      top: d => d.L('M452 500 L500 560 L548 500'),
      item: (d, l, r) => d.E(420, 640, 46, 82, 'accent', 20) + d.E(580, 640, 46, 82, 'accent', -20) +
        d.C(500, 650, 92, 'accent2') + d.E(500, 690, 40, 28, 'accent2') + d.dot(500, 676, 14) + d.face(500, 636, 110),
    }));

  A.add('dentist', 'Dentist', pal(3, { main: LB, dark: DEN, accent: TEAL, accent2: W, light: W }), d =>
    person(d, {
      hf: 'short', raise: 'r',
      top: d => d.L('M452 500 L500 560 L548 500'),
      item: (d, l, r) => tube(d, ['M704 392 L800 180'], 'accent', 44) + d.R(756, 120, 76, 70, 18, 'accent2') +
        d.L('M770 132 L770 176 M794 128 L794 176 M818 132 L818 176') +
        d.P('M230 610 Q230 548 290 552 Q320 556 330 574 Q340 556 370 552 Q430 548 430 610 Q430 690 410 760 Q400 790 386 760 L366 700 Q330 680 294 700 L274 760 Q260 790 250 760 Q230 690 230 610 Z', 'accent2') +
        d.face(330, 632, 90),
    }));

  A.add('librarian', 'Librarian', pal(1, { main: '#f48fb1', dark: '#6d4c41', accent: R, accent2: B, light: Y }), d =>
    person(d, {
      hb: 'curly', hf: 'none', noHands: true,
      top: d => d.L('M452 500 Q500 560 548 500'),
      item: (d) => d.R(390, 704, 220, 60, 10, 'accent') + d.R(410, 646, 190, 58, 10, 'accent2') + d.R(380, 588, 210, 58, 10, 'light') +
        d.L('M410 618 L560 618 M440 676 L580 676 M420 734 L580 734') +
        d.C(372, 690, 34, 'skin') + d.C(628, 690, 34, 'skin'),
    }));

  A.add('scientist', 'Scientist', pal(2, { main: W, dark: PURPLE, accent: G, accent2: B, light: GR }), d =>
    person(d, {
      hb: 'braids', hf: 'short',
      top: d => d.L('M442 500 L500 600 L558 500') + d.L('M500 600 L500 790'),
      hat: d => d.R(380, 278, 240, 30, 14, 'light') + d.C(450, 290, 42, 'accent2') + d.C(550, 290, 42, 'accent2'),
      item: (d, l, r) => d.P('M630 540 L678 540 L678 600 L740 720 Q752 760 712 760 L596 760 Q556 760 568 720 L630 600 Z', 'accent2') +
        d.P('M586 690 L722 690 L740 726 Q752 760 712 760 L596 760 Q556 760 570 726 Z', 'accent') +
        d.R(620, 526, 68, 26, 8, 'light') + d.C(640, 480, 18, 'accent2') + d.C(676, 440, 13, 'accent2'),
    }));

  A.add('painter', 'Painter', pal(4, { main: W, dark: W, accent: B, accent2: R, light: Y }), d =>
    person(d, {
      hf: 'short', raise: 'r',
      top: d => d.R(430, 600, 140, 120, 16, 'main') + d.L('M430 610 L400 500 M570 610 L600 500') +
        d.C(460, 740, 16, 'accent') + d.C(540, 760, 12, 'accent2') + d.C(520, 650, 12, 'light'),
      hat: d => d.P('M372 276 L500 168 L628 276 Z', 'light') + d.R(368, 262, 264, 30, 10, 'light'),
      item: (d, l, r) => tube(d, ['M704 392 L704 300 L790 300 L790 220'], 'light', 34) + d.R(726, 126, 150, 96, 30, 'accent') +
        d.R(180, 770, 150, 120, 14, 'accent2') + d.E(255, 770, 75, 22, 'accent2') + d.L('M190 790 Q255 740 320 790'),
    }));

  A.add('lifeguard', 'Lifeguard', pal(3, { main: R, dark: R, accent: Y, accent2: W, light: W }), d =>
    person(d, {
      hb: 'pony', hf: 'long',
      top: d => d.L('M440 494 Q500 600 560 494') + d.R(486, 590, 28, 40, 8, 'accent'),
      hat: d => d.E(560, 266, 140, 30, 'accent') + d.P('M376 272 Q378 230 500 228 Q622 230 624 272 Z', 'accent'),
      item: (d, l, r) => d.C(720, 690, 112, 'accent2') + d.C(720, 690, 54, 'light') +
        d.band(720, 690, 112, 112, 604, 650, 'accent') + d.band(720, 690, 112, 112, 790, 836, 'accent'),
    }));

  A.add('crossing-guard', 'Crossing Guard', pal(1, { main: '#a1887f', dark: '#6d4c41', accent: O, accent2: Y, light: R }), d =>
    person(d, {
      hb: 'long', hf: 'long', raise: 'r',
      top: d => d.P('M392 552 L452 494 L452 792 L392 792 Z', 'accent') + d.P('M608 552 L548 494 L548 792 L608 792 Z', 'accent') +
        d.R(392, 680, 60, 24, 4, 'accent2') + d.R(548, 680, 60, 24, 4, 'accent2'),
      item: (d, l, r) => {
        const pts = []; for (let i = 0; i < 8; i++) { const a = Math.PI / 8 + i * Math.PI / 4; pts.push([790 + 140 * Math.cos(a), 190 + 140 * Math.sin(a)]); }
        return tube(d, ['M704 392 L760 320'], 'dark', 40) + d.poly(pts, 'light') +
          d.L('M712 162 Q682 150 680 172 Q680 190 704 194 Q726 200 724 220 Q720 236 690 228') +
          d.L('M742 152 L782 152 M762 152 L762 232') + d.E(812, 192, 22, 40) + d.L('M858 232 L858 152 Q894 152 894 174 Q894 196 858 196');
      },
    }));

  A.add('mechanic', 'Mechanic', pal(0, { main: '#78909c', dark: '#78909c', accent: R, accent2: GR, light: W }), d =>
    person(d, {
      hf: 'short', raise: 'l',
      top: d => d.L('M500 500 L500 790') + d.R(522, 560, 64, 48, 10, 'accent') + d.R(392, 700, 216, 26, 6, 'dark'),
      hat: d => d.E(440, 276, 130, 28, 'accent') + d.P('M372 272 Q366 196 500 190 Q634 196 628 272 Z', 'accent'),
      item: (d, l, r) => tube(d, ['M296 392 L220 210'], 'accent2', 50) +
        d.P('M168 190 Q170 120 230 112 L230 160 L262 172 L282 140 Q300 200 262 232 Q220 250 190 230 Z', 'accent2'),
    }));

  A.add('gardener', 'Gardener', pal(4, { main: G, dark: DEN, accent: Y, accent2: BR, light: R }), d =>
    person(d, {
      hb: 'braids', hf: 'long',
      top: d => d.R(430, 560, 140, 232, 20, 'accent2') + d.L('M430 570 L400 500 M570 570 L600 500') + d.R(460, 640, 80, 50, 10, 'accent2'),
      hat: d => d.E(500, 262, 210, 44, 'accent') + d.P('M392 268 Q398 176 500 176 Q602 176 608 268 Z', 'accent') +
        d.R(396, 230, 208, 30, 8, 'light'),
      item: (d, l, r) => tube(d, ['M654 712 L700 180'], 'accent2', 40) + d.R(624, 140, 160, 40, 12, 'dark') +
        d.L('M640 180 L640 230 M672 180 L672 230 M704 180 L704 230 M736 180 L736 230 M768 180 L768 230'),
    }));

  A.add('bus-driver', 'Bus Driver', pal(2, { main: B, dark: NAVY, accent: '#3949ab', accent2: GR, light: Y }), d =>
    person(d, {
      hf: 'short', noHands: true,
      hat: d => d.E(500, 274, 150, 30, 'accent') + d.P('M368 266 Q354 190 500 182 Q646 190 632 266 Z', 'main') + d.R(376, 238, 248, 32, 10, 'accent'),
      item: (d) => d.C(500, 690, 150, 'accent2') + d.C(500, 690, 106, 'main') + d.C(500, 690, 40, 'accent2') +
        tube(d, ['M410 690 L460 690 M540 690 L590 690 M500 730 L500 790'], 'accent2', 40) + d.C(500, 690, 40, 'accent2') +
        d.C(360, 640, 34, 'skin') + d.C(640, 640, 34, 'skin'),
    }));

  A.add('recycling-worker', 'Recycling Worker', pal(3, { main: G, dark: DG, accent: Y, accent2: B, light: '#e0e0e0' }), d =>
    person(d, {
      hf: 'short',
      top: d => d.R(392, 640, 216, 30, 6, 'accent') + d.R(392, 720, 216, 30, 6, 'accent'),
      hat: d => d.E(560, 276, 120, 28, 'dark') + d.P('M372 272 Q366 196 500 190 Q634 196 628 272 Z', 'dark'),
      item: (d, l, r) => d.P('M640 560 L860 560 L836 880 L664 880 Z', 'accent2') + d.R(624, 520, 252, 50, 14, 'accent2') +
        d.L('M720 620 L720 820 M780 620 L780 820') + d.C(700, 890, 22, 'light') + d.C(800, 890, 22, 'light'),
    }));

  A.add('hairdresser', 'Hairdresser', pal(1, { main: '#f48fb1', dark: '#424242', accent: GR, accent2: Y, light: W }), d =>
    person(d, {
      hb: 'curly', hf: 'none',
      top: d => d.L('M452 500 L500 560 L548 500') + d.R(522, 600, 60, 50, 10, 'accent2'),
      item: (d, l, r) =>
        d.P('M700 700 L852 452 L868 470 L728 712 Z', 'accent') + d.P('M820 700 L668 452 L652 470 L792 712 Z', 'accent') +
        d.C(760, 594, 14, 'accent2') + d.C(704, 740, 40, 'accent2') + d.C(816, 740, 40, 'accent2') +
        d.C(704, 740, 16, 'light') + d.C(816, 740, 16, 'light') +
        d.R(230, 600, 50, 190, 10, 'accent') + d.L('M280 620 L310 620 M280 650 L310 650 M280 680 L310 680 M280 710 L310 710 M280 740 L310 740'),
    }));

  // ---- things helpers use ----
  A.add('fire-hydrant', 'Fire Hydrant', { main: R, dark: '#c62828', accent: Y, light: GR, pink: P }, d =>
    d.R(300, 830, 400, 60, 20, 'dark') +
    d.R(370, 360, 260, 480, 40) +
    d.R(250, 500, 140, 110, 30, 'light') + d.R(610, 500, 140, 110, 30, 'light') +
    d.C(225, 555, 40, 'accent') + d.C(775, 555, 40, 'accent') +
    d.P('M350 380 Q350 230 500 222 Q650 230 650 380 Z') + d.R(340, 360, 320, 46, 20, 'dark') +
    d.R(470, 180, 60, 60, 14, 'accent') +
    d.face(500, 620, 200));

  A.add('first-aid-kit', 'First Aid Kit', { main: W, dark: R, accent: R, light: GR, pink: P }, d =>
    d.R(390, 230, 220, 120, 40, 'dark') + d.R(430, 268, 140, 120, 20, 'light') +
    d.R(170, 330, 660, 520, 60) + d.R(170, 450, 660, 30, 8, 'light') +
    heart(d, 500, 360, 70) + d.face(500, 660, 220));

  A.add('toolbox', 'Toolbox', { main: R, dark: '#c62828', accent: GR, light: Y, accent2: BR, pink: P }, d =>
    d.R(380, 230, 240, 140, 40, 'dark') + d.R(420, 270, 160, 120, 20, 'light') +
    tube(d, ['M250 420 L330 220'], 'accent2', 44) + d.R(250, 170, 140, 70, 14, 'accent') +
    tube(d, ['M700 420 L760 230'], 'light', 44) + d.P('M734 236 L786 236 L770 170 L750 170 Z', 'accent') +
    d.R(150, 380, 700, 470, 50) + d.R(150, 380, 700, 120, 40, 'dark') + d.R(440, 470, 120, 60, 14, 'accent') +
    d.face(500, 680, 220));

  A.add('traffic-cone', 'Traffic Cone', { main: O, dark: '#e65100', accent: W, light: GR, pink: P }, d =>
    d.R(200, 820, 600, 70, 24, 'dark') +
    d.P('M440 160 Q500 130 560 160 L720 830 L280 830 Z') +
    d.P('M396 330 L604 330 L636 450 L364 450 Z', 'accent') + d.P('M322 640 L678 640 L706 756 L294 756 Z', 'accent') +
    d.face(500, 535, 160));

  A.add('stethoscope', 'Stethoscope', { main: '#90a4ae', dark: DGR, accent: B, light: GR, pink: P }, d =>
    tube(d, ['M330 170 Q300 420 500 470 Q700 420 670 170', 'M500 470 L500 600 Q500 700 600 720'], 'dark', 46) +
    d.C(330, 160, 34, 'accent') + d.C(670, 160, 34, 'accent') +
    d.C(650, 760, 150) + d.C(650, 760, 110, 'light') + d.face(650, 760, 120));

  A.add('hard-hat', 'Hard Hat', { main: Y, dark: '#f9a825', accent: O, light: W, pink: P }, d =>
    d.E(500, 720, 390, 90, 'dark') +
    d.P('M190 720 Q190 300 500 290 Q810 300 810 720 Z') +
    d.R(450, 290, 100, 180, 40, 'accent') +
    d.face(500, 585, 200));

  A.add('envelope', 'Letter', { main: W, dark: CREAM, accent: R, light: B, pink: P }, d =>
    d.R(140, 260, 720, 500, 40) +
    d.L('M150 280 L500 560 L850 280') + d.L('M160 740 L400 480 M840 740 L600 480') +
    heart(d, 500, 560, 60) + d.face(500, 380, 150));

  A.add('doctor-bag', "Doctor's Bag", { main: BR, dark: '#6d4c41', accent: R, light: Y, pink: P }, d =>
    tube(d, ['M380 330 Q380 190 500 190 Q620 190 620 330'], 'dark', 50) +
    d.P('M180 400 Q180 320 260 320 L740 320 Q820 320 820 400 L840 820 Q840 860 800 860 L200 860 Q160 860 160 820 Z') +
    d.R(180, 420, 640, 40, 10, 'dark') + d.R(460, 400, 80, 80, 14, 'light') +
    heart(d, 500, 590, 70) + d.face(500, 740, 170));
})();
