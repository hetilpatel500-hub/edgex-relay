"""Late-day close at the extreme of the day's range.
Added 2026-10-06 by risk-manager: the queue's non-tape lines are all coded and
a WebSearch for new ORB/VWAP rules came back with ideas the lab already tests,
so this tests the old "strong close" observation (stocks closing in the top or
bottom of the day's range keep going into the close). Rules fixed before any
P&L. Distinct from power_hour_range_break (needs a break of a range) and
trend_day_vote (morning information only).
"""


def late_day_extreme_close(s):
    """First bar at or after 14:00 whose close sits in the top (bottom) 10% of
    the day's range so far, with the day's range at least 8 ATR(14) of
    5-minute bars and the close on the same side of VWAP. One signal a day."""
    b = s.bars
    hi = lo = None
    for i, x in enumerate(b):
        hi = x.h if hi is None else max(hi, x.h)
        lo = x.l if lo is None else min(lo, x.l)
        if x.m < 840:
            continue
        atr = s.atr[i]
        rng = hi - lo
        if not atr or rng < 8 * atr:
            return
        pos = (x.c - lo) / rng
        if pos >= 0.9 and x.c > s.vwap[i]:
            yield i, 1
        elif pos <= 0.1 and x.c < s.vwap[i]:
            yield i, -1
        return


SETUPS = [
    dict(id='late_day_extreme_close', name='Late-day close at the day extreme', family='time',
         detect=late_day_extreme_close,
         rules="At the first 5-minute close at or after 14:00 ET, if the day's range is at least 8 ATR "
               "and the close sits in the top 10% of the range and above VWAP, lean long (bottom 10% "
               "and below VWAP, lean short). One signal a day. Tested with and against the signal."),
]
