"""Prior-week high/low sweep and close back inside.
Added 2026-10-02 by smart-money-analyst: the research queue held only tape items, so this run took the
documented "previous period high/low as resting liquidity" idea (WebSearch: sweep of a prior high/low, quick
return inside the range, expansion the other way) at the weekly level, which the lab had not tested (pd_sweep
and equal_hl_sweep use the prior day / equal highs). Rules fixed BEFORE any P&L was seen.
"""


def _prior_week(s):
    """High/low of the previous calendar week's sessions, chained through s.prior (a chain break from a
    half day or gap ends the walk). None if fewer than 3 sessions of that week are available."""
    wk = s.day.isocalendar()[:2]
    p = s.prior
    while p is not None and p.day.isocalendar()[:2] == wk:
        p = p.prior
    if p is None:
        return None
    pwk = p.day.isocalendar()[:2]
    hi, lo, n = p.hi, p.lo, 0
    while p is not None and p.day.isocalendar()[:2] == pwk:
        hi, lo, n = max(hi, p.hi), min(lo, p.lo), n + 1
        p = p.prior
    return (hi, lo) if n >= 3 else None


def prior_week_sweep(s):
    """The first bar before 14:30 that trades above the prior week's high but closes back below it leans
    short; trading below the prior week's low and closing back above it leans long. One signal per session."""
    lv = _prior_week(s)
    if lv is None:
        return
    pwh, pwl = lv
    b = s.bars
    for i in range(len(b)):
        if b[i].m >= 870:
            break
        if b[i].h > pwh and b[i].c < pwh:
            yield i, -1
            return
        if b[i].l < pwl and b[i].c > pwl:
            yield i, 1
            return


SETUPS = [
    dict(id='prior_week_sweep', name='Prior-week high/low sweep, close back inside', family='smart money',
         detect=prior_week_sweep,
         rules="A 5-minute bar before 14:30 that trades above the previous week's high but closes back below it "
               "leans short; one that trades below the previous week's low and closes back above it leans long. "
               "Needs 3+ sessions in the previous week. One signal per session."),
]
