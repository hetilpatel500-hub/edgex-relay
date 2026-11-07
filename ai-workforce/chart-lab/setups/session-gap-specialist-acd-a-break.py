"""Mark Fisher's ACD "A up / A down": opening range 30 minutes plus a fixed A value.
Added 2026-10-02 by session-gap-specialist: research queue held only tape items, so this run took the
documented ACD method (Fisher; NexusFi Academy and clever-trading-strategies.com primers): the opening
range high plus the A value is "A up", the low minus the A value is "A down". Fisher leaves the A value
unstandardized, so it was fixed BEFORE testing at 10% of yesterday's high-low range and never tuned.
Distinct from orb15/orb30_min_range (no A buffer, no prior-range scaling).
"""


def acd_a_break(s):
    """Opening range = first 30 minutes (6 bars). A = 10% of yesterday's high-low range. The first 5-minute
    close above OR high + A (below OR low - A) between 10:00 and 14:30 leans with the break. One per session."""
    p = s.prior
    b = s.bars
    if p is None or len(b) < 8:
        return
    a = 0.10 * (p.hi - p.lo)
    if a <= 0:
        return
    hi = max(x.h for x in b[:6])
    lo = min(x.l for x in b[:6])
    for i in range(6, len(b)):
        if b[i].m >= 870:
            break
        if b[i].c > hi + a:
            yield i, 1
            return
        if b[i].c < lo - a:
            yield i, -1
            return


SETUPS = [
    dict(id='acd_a_break', name='ACD A-up / A-down break', family='opening range', detect=acd_a_break,
         rules="Opening range is the first 30 minutes. A is 10% of yesterday's high-low range. The first 5-minute "
               "close above the opening-range high plus A (below the low minus A) between 10:00 and 14:30 leans "
               "with the break. One signal per session."),
]
