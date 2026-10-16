"""Supertrend (10, 3.0) flip with VWAP agreement.
Added 2026-09-29 by trend-moving-average-analyst: trend family, found by
WebSearch (mudrex.com/learn/supertrend-indicator, netpicks.com/supertrend-indicator:
intraday ATR 10, multiplier 3, flip confirmed by price vs VWAP). Parameters fixed
before testing.
"""


def supertrend_flip_vwap(s):
    """Supertrend with a 10-bar ATR and multiplier 3 runs over the session's
    5-minute bars (true range from the second bar on, simple average of the
    first 10). When it flips from down to up and the flip bar closes above
    session VWAP, the setup leans long; up to down with a close below VWAP
    leans short."""
    b = s.bars
    n, mult = 10, 3.0
    tr = [b[0].h - b[0].l]
    for i in range(1, len(b)):
        tr.append(max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c)))
    fub = flb = None
    trend = 0
    fired = 0
    for i in range(n - 1, len(b)):
        atr = sum(tr[i - n + 1:i + 1]) / n
        mid = (b[i].h + b[i].l) / 2
        ub, lb = mid + mult * atr, mid - mult * atr
        if fub is None:
            fub, flb, trend = ub, lb, (1 if b[i].c >= mid else -1)
            continue
        fub = ub if (ub < fub or b[i - 1].c > fub) else fub
        flb = lb if (lb > flb or b[i - 1].c < flb) else flb
        prev = trend
        if trend == -1 and b[i].c > fub:
            trend = 1
        elif trend == 1 and b[i].c < flb:
            trend = -1
        if trend == prev:
            continue
        if b[i].m >= 900 or fired >= 3:
            break
        if trend == 1 and b[i].c > s.vwap[i]:
            fired += 1
            yield i, 1
        elif trend == -1 and b[i].c < s.vwap[i]:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='supertrend_flip_vwap', name='Supertrend flip with VWAP agreement', family='trend',
         detect=supertrend_flip_vwap,
         rules="Supertrend (10-bar ATR, multiplier 3) on 5-minute bars flips up and the flip bar closes above "
               "session VWAP: lean long; flips down and closes below VWAP: lean short. Parameters were fixed "
               "from published intraday defaults before testing, up to 3 flips a session, before 15:00."),
]
