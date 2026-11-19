"""ABC pullback after an impulse leg.
Added by elliott-wave-analyst: Elliott-wave family, next open line of the
research queue in ai-workforce/chart-lab/README.md.
"""


def _add_pivot(pivots, k, price, typ):
    """Keep a strict alternating zigzag: a new pivot of the same type as the
    last one replaces it only if more extreme; a new pivot of the opposite
    type is appended."""
    if pivots and pivots[-1][2] == typ:
        if (typ == 'H' and price > pivots[-1][1]) or (typ == 'L' and price < pivots[-1][1]):
            pivots[-1] = (k, price, typ)
    else:
        pivots.append((k, price, typ))


def abc_pullback(s):
    """An impulse leg (P0 -> P1, a swing pivot to pivot move >= 1.5 ATR) is
    followed by a three-swing ABC correction: A (against the impulse), B (a
    bounce with the impulse, staying inside P1), C (against the impulse again,
    retracing 38.2%-78.6% of the impulse and holding above/below P0). The
    first close back beyond B, in the impulse's own direction, confirms the
    correction finished and the impulse is resuming."""
    b = s.bars
    n = len(b)
    pivots = []
    used = set()
    fired = 0
    for i in range(4, n):
        if b[i].m >= 900 or fired >= 2:
            break
        k = i - 2
        if k >= 2:
            if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
                _add_pivot(pivots, k, b[k].h, 'H')
            if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
                _add_pivot(pivots, k, b[k].l, 'L')
        if len(pivots) < 5:
            continue
        p0, p1, a, bb, c = pivots[-5:]
        if c[0] in used:
            continue
        atr = s.atr[p1[0]]
        if not atr:
            continue
        if p1[2] == 'H':
            d = 1
            rng = p1[1] - p0[1]
            if rng < 1.5 * atr or bb[1] >= p1[1] or c[1] <= p0[1]:
                continue
            retr = (p1[1] - c[1]) / rng
            if not (0.382 <= retr <= 0.786):
                continue
            if b[i].c > bb[1]:
                used.add(c[0]); fired += 1; yield i, 1
        else:
            d = -1
            rng = p0[1] - p1[1]
            if rng < 1.5 * atr or bb[1] <= p1[1] or c[1] >= p0[1]:
                continue
            retr = (c[1] - p1[1]) / rng
            if not (0.382 <= retr <= 0.786):
                continue
            if b[i].c < bb[1]:
                used.add(c[0]); fired += 1; yield i, -1


SETUPS = [
    dict(id='abc_pullback', name='ABC pullback after an impulse leg', family='elliott wave', detect=abc_pullback,
         rules="A swing-to-swing impulse leg of at least 1.5 ATR is followed by a three-swing ABC correction "
               "(A against the impulse, B a bounce staying inside the impulse extreme, C retracing 38.2%-78.6% "
               "of the impulse and holding beyond the impulse's start). The first close back beyond B in the "
               "impulse's direction leans with the impulse resuming, before 15:00."),
]
