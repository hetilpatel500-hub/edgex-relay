"""30-minute opening range breakout with a minimum range filter.
Added 2026-09-30 by session-gap-specialist via WebSearch (QuantifiedStrategies
and tradersmastermind ORB guides: test 5/15/30-minute ranges and require the
range to be at least 0.2% of price). orb15 tests the 15-minute range without a
size filter; this is the 30-minute range with the guides' 0.2% floor.
Parameters (30 minutes, 0.2%, break before 11:30, one per day) were fixed
before any P&L was seen.
"""


def orb30_min_range(s):
    """After the 9:30-10:00 range closes, the first 5-minute close (10:00-11:30)
    beyond the range leans with the break, but only when the range is at least
    0.2% of the open. One per day."""
    b = s.bars
    r = [x for x in b if x.m < 600]
    if len(r) < 6:
        return
    hi, lo = max(x.h for x in r), min(x.l for x in r)
    if (hi - lo) < 0.002 * s.open:
        return
    for i in range(len(r), len(b)):
        if b[i].m < 600:
            continue
        if b[i].m + 5 > 690:
            return
        if b[i].c > hi:
            yield i, 1
            return
        if b[i].c < lo:
            yield i, -1
            return


SETUPS = [
    dict(id='orb30_min_range', name='30-minute opening range break (range >= 0.2%)', family='opening range',
         detect=orb30_min_range,
         rules="After the first 30 minutes (9:30-10:00), the first 5-minute close beyond that range before 11:30 "
               "leans with the break, only when the 30-minute range is at least 0.2% of the open. One per day."),
]
