"""Raschke's Holy Grail: first pullback to the 20 EMA while ADX(14) is above 30 and rising.
Added 2026-09-28 by trend-moving-average-analyst: the research queue's non-tape
lines are all coded, so this run used WebSearch (capital.com, tradersmastermind.com,
investingpaths.com) for a documented, untested trend technique. Distinct from
ema9_20_pullback: it needs a strong-trend filter (ADX) and only the first touch.
"""


def _ema(xs, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for c in xs:
        prev = c if prev is None else c * k + prev * (1 - k)
        out.append(prev)
    return out


def _adx(b, n=14):
    """Wilder ADX with +DI/-DI, seeded from the session's first bars."""
    m = len(b)
    tr, pdm, mdm = [0.0] * m, [0.0] * m, [0.0] * m
    for i in range(1, m):
        up, dn = b[i].h - b[i - 1].h, b[i - 1].l - b[i].l
        pdm[i] = up if up > dn and up > 0 else 0.0
        mdm[i] = dn if dn > up and dn > 0 else 0.0
        tr[i] = max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c))
    adx, pdi, mdi = [None] * m, [0.0] * m, [0.0] * m
    if m <= 2 * n:
        return adx, pdi, mdi
    a_tr, a_p, a_m = sum(tr[1:n + 1]), sum(pdm[1:n + 1]), sum(mdm[1:n + 1])
    dx = []
    for i in range(n, m):
        if i > n:
            a_tr = a_tr - a_tr / n + tr[i]
            a_p = a_p - a_p / n + pdm[i]
            a_m = a_m - a_m / n + mdm[i]
        pdi[i] = 100 * a_p / a_tr if a_tr else 0.0
        mdi[i] = 100 * a_m / a_tr if a_tr else 0.0
        s = pdi[i] + mdi[i]
        dx.append(100 * abs(pdi[i] - mdi[i]) / s if s else 0.0)
        if len(dx) == n:
            adx[i] = sum(dx) / n
        elif len(dx) > n:
            adx[i] = (adx[i - 1] * (n - 1) + dx[-1]) / n
    return adx, pdi, mdi


def holy_grail(s):
    """While ADX(14) > 30 and rising, with +DI over -DI (or under), the first bar
    whose low (high) tags EMA20 after the trend was established (ADX still above 30 on
    that bar, rising not required since pullbacks flatten it), and which still
    closes on the trend side of EMA20, leans with the trend. One signal per side
    per session, before 14:30."""
    b = s.bars
    ema = _ema([x.c for x in b], 20)
    adx, pdi, mdi = _adx(b)
    started = {1: None, -1: None}
    fired = set()
    for i in range(29, len(b)):
        if b[i].m >= 870:
            break
        if adx[i] is None or adx[i - 1] is None:
            continue
        strong = adx[i] > 30 and adx[i] > adx[i - 1]
        for d in (1, -1):
            if started[d] is None:
                if strong and (pdi[i] > mdi[i]) == (d == 1) and ((b[i].c > ema[i]) == (d == 1)):
                    started[d] = i
                continue
            if d in fired:
                continue
            tag = b[i].l <= ema[i] if d == 1 else b[i].h >= ema[i]
            if tag and i > started[d]:
                fired.add(d)
                if adx[i] > 30 and ((b[i].c > ema[i]) == (d == 1)):
                    yield i, d


SETUPS = [
    dict(id='holy_grail', name="Holy Grail: first pullback to the 20 EMA in a strong ADX trend", family='trend',
         detect=holy_grail,
         rules="After ADX(14) on 5-minute bars is above 30 and rising (the push) with +DI over -DI (or under) and price on the "
               "trend side of EMA20, the first bar that tags EMA20 while ADX is still above 30 and still closes on the trend side of it leans "
               "with the trend. Only the first touch counts; one signal per side per session, before 14:30."),
]
