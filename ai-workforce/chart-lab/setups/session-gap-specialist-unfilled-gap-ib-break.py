"""Unfilled gap beyond yesterday's range, then initial balance break.
Added 2026-10-01 by session-gap-specialist: research queue was empty apart from
tape items, so this run took the documented gap-and-go idea (tradezella.com
gap-and-go rules: the gap holds into the first hour, then the break of the
opening range continues) and fixed rules before testing. Distinct from
gap_go_rvol (splits by relative volume) and ib_break (no gap condition).
"""


def unfilled_gap_ib_break(s):
    """The session opens beyond yesterday's high (low) and the whole initial
    balance (first hour) stays beyond it, so the gap was not touched. The first
    5-minute close beyond the IB high (low) in the gap direction, 10:30-14:30,
    leans with the gap. One signal per session."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    if len(b) < 14:
        return
    if s.open > p.hi and s.ib_lo > p.hi:
        d, level = 1, s.ib_hi
    elif s.open < p.lo and s.ib_hi < p.lo:
        d, level = -1, s.ib_lo
    else:
        return
    for i in range(12, len(b)):
        if b[i].m >= 870:
            break
        if d * (b[i].c - level) > 0:
            yield i, d
            return


SETUPS = [
    dict(id='unfilled_gap_ib_break', name='Unfilled gap, then IB break with the gap', family='gap',
         detect=unfilled_gap_ib_break,
         rules="The session opens above yesterday's high (below yesterday's low) and the whole first hour stays "
               "beyond it, so the gap is untouched. The first 5-minute close beyond the initial-balance high (low) "
               "in the gap direction, 10:30 to 14:30, leans with the gap. One signal per session."),
]
