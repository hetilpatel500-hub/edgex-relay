"""Inventory retracement bar (IRB) in a 20/40 EMA trend.
Added 2026-10-05 by trend-moving-average-analyst: new idea from the Rob Hoffman
inventory-retracement method (documented intraday technique, not on the queue
yet). Rules fixed before testing; nothing tuned.
"""


def _ema(closes, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for c in closes:
        prev = c if prev is None else c * k + prev * (1 - k)
        out.append(prev)
    return out


def inventory_retracement_bar(s):
    """Trend: price above EMA20 above EMA40 (below/below for down) and EMA20
    sloping that way over 5 bars. An IRB is a bar whose wick against the trend
    is at least 45% of its range and which closes in the trend's half. The
    signal is the first later bar (within 3 bars) that closes beyond the IRB's
    extreme in the trend direction."""
    b = s.bars
    closes = [x.c for x in b]
    e20, e40 = _ema(closes, 20), _ema(closes, 40)
    fired = 0
    for i in range(41, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        for k in (1, 2, 3):
            j = i - k
            rng = b[j].h - b[j].l
            if rng <= 0:
                continue
            up = b[j].c > e20[j] > e40[j] and e20[j] > e20[j - 5]
            dn = b[j].c < e20[j] < e40[j] and e20[j] < e20[j - 5]
            mid = (b[j].h + b[j].l) / 2
            if up and (min(b[j].o, b[j].c) - b[j].l) >= 0.45 * rng and b[j].c >= mid and b[i].c > b[j].h \
                    and all(b[x].c <= b[j].h for x in range(j + 1, i)):
                fired += 1
                yield i, 1
                break
            if dn and (b[j].h - max(b[j].o, b[j].c)) >= 0.45 * rng and b[j].c <= mid and b[i].c < b[j].l \
                    and all(b[x].c >= b[j].l for x in range(j + 1, i)):
                fired += 1
                yield i, -1
                break


SETUPS = [
    dict(id='inventory_retracement_bar', name='Inventory retracement bar in a 20/40 EMA trend', family='trend',
         detect=inventory_retracement_bar,
         rules="Price above EMA20 above EMA40 with EMA20 rising (mirror for down) is the trend. A bar with a wick "
               "against the trend of at least 45% of its range that closes in the trend's half is the inventory "
               "retracement bar; the first close beyond its high (low) within the next 3 bars is the signal, "
               "before 15:00."),
]
