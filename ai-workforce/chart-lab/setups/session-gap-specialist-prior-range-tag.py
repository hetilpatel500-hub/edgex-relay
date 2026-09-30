"""Open inside yesterday's range, lean toward the nearer prior-day extreme.
Added 2026-09-29 by session-gap-specialist: WebSearch found the documented
statistic that SPY, opening inside the prior day's range, tags the prior high
or low most sessions (tradethatswing.com, "high probability stock market
statistics"). The claim says "either", so this run tests the direction rule
of leaning to the nearer extreme, with and against.
"""


def prior_range_tag(s):
    """Session opens inside yesterday's high-low. At the 10:00 bar close
    (30 minutes in), if price is still inside that range and has not yet
    touched either extreme, lean toward the nearer one: long if yesterday's
    high is nearer, short if yesterday's low is nearer. Needs the target at
    least 0.5 ATR away. One signal per session."""
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
    dict(id='prior_range_tag', name='Open inside yesterday\'s range, lean to the nearer extreme',
         family='session', detect=prior_range_tag,
         rules="When the session opens inside yesterday's high-low and, at the 10:00 close, has touched "
               "neither extreme, lean toward whichever of yesterday's high or low is nearer (at least "
               "0.5 ATR away). Tested with and against; one signal per session."),
]
