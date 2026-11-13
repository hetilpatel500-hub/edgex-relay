"""Open inside yesterday's range, lean toward the nearer prior-day extreme.

Based on the widely quoted statistic that SPY, opening inside the prior
day's range, tags the prior high or low in most sessions
(tradethatswing.com, "high probability stock market statistics"). At the
10:00 bar close, if price is still inside yesterday's range and has touched
neither extreme, lean toward the nearer one (at least 0.5 ATR away).

Snapshot from the Edgex chart lab (12 US symbols, 2026-05-15 to 2026-10-23,
OOS from 2026-09-09): validated WITH the lean, ppoc filter, 2 ATR stop /
4 ATR target: 60 OOS trades, 53% win, +0.31R avg, PF 1.68, t 1.83.
Re-test on your own data before relying on it.
"""


def prior_range_tag(s):
    p = s.prior
    if p is None:
        return
    b = s.bars
    if not (p.lo < s.open < p.hi) or len(b) < 8:
        return
    i = 5
    if b[i].m != 595:
        return
    if max(x.h for x in b[:i + 1]) >= p.hi or min(x.l for x in b[:i + 1]) <= p.lo:
        return
    c = b[i].c
    up, dn = p.hi - c, c - p.lo
    atr = s.atr[i]
    if not atr or min(up, dn) < 0.5 * atr or up == dn:
        return
    yield i, (1 if up < dn else -1)


SETUPS = [
    dict(id='prior_range_tag', name="Open inside yesterday's range, lean to the nearer extreme",
         family='session', detect=prior_range_tag,
         rules="When the session opens inside yesterday's high-low and, at the 10:00 close, has touched "
               "neither extreme, lean toward whichever of yesterday's high or low is nearer (at least "
               "0.5 ATR away). Tested with and against; one signal per session."),
]
