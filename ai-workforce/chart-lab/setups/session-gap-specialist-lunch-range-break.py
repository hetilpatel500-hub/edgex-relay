"""Lunch-hour range breakout.
Added 2026-09-29 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch (tradethatswing.com, volatilitybox.com
intraday-by-hour research) for a documented, untested idea: price contracts
around the New York lunch hour and the range's break expands. Not the same as
orb15 or ib_break, which use the morning range.
"""


def lunch_range_break(s):
    """The high/low of the 5-minute bars from 11:30 to 12:30 ET (12 bars) is the
    lunch range. The first bar after it (12:30-14:30) that closes beyond the range
    leans with the break; one signal per session. Sessions where the lunch range is
    wider than half the 9:30-11:30 range are skipped (not a contraction). v1 used a 1.5 ATR
    width cap that was mis-scaled (the median lunch hour is 3.4 five-minute ATRs) and fired
    0 signals; v2 was set from range geometry, before seeing any P&L."""
    b = s.bars
    idx = [i for i in range(len(b)) if 690 <= b[i].m < 750]
    if len(idx) < 10:
        return
    hi = max(b[i].h for i in idx)
    lo = min(b[i].l for i in idx)
    last = idx[-1]
    morning = b[:idx[0]]
    if len(morning) < 12:
        return
    if hi - lo > 0.5 * (max(x.h for x in morning) - min(x.l for x in morning)):
        return
    for i in range(last + 1, len(b)):
        if b[i].m >= 870:
            return
        if b[i].c > hi:
            yield i, 1
            return
        if b[i].c < lo:
            yield i, -1
            return


SETUPS = [
    dict(id='lunch_range_break', name='Lunch-hour range breakout', family='session time', detect=lunch_range_break,
         rules="Mark the high and low of 11:30-12:30 ET. If that range is at most half the 9:30-11:30 range (a real contraction), the "
               "first 5-minute close beyond it before 14:30 leans with the break."),
]
