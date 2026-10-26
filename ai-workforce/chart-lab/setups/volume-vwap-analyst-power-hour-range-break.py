"""Power-hour range breakout.
Added 2026-09-30 by volume-vwap-analyst after a WebSearch (trademomentum.org,
luxalgo.com power-hour pages): the documented late-day setup is a 30-120 minute
tight consolidation that breaks when volume returns around 15:00. Different from
lunch_range_break (11:30-12:30). Rules and thresholds fixed before any P&L.
"""


def power_hour_range_break(s):
    """Range = high/low of the 5-minute bars 14:00-15:00 ET. Skipped unless it is at most
    a third of the day's range so far (a real contraction). The first bar from 15:00 to
    15:40 that closes beyond the range, with relative volume at least 1.2 when known,
    leans with the break; one signal per session."""
    b = s.bars
    idx = [i for i in range(len(b)) if 840 <= b[i].m < 900]
    if len(idx) < 10:
        return
    hi = max(b[i].h for i in idx)
    lo = min(b[i].l for i in idx)
    day = max(x.h for x in b[:idx[-1] + 1]) - min(x.l for x in b[:idx[-1] + 1])
    if hi - lo > day / 3:
        return
    for i in range(idx[-1] + 1, len(b)):
        if b[i].m >= 940:
            return
        rv = s.rvol[i]
        if rv is not None and rv < 1.2:
            continue
        if b[i].c > hi:
            yield i, 1
            return
        if b[i].c < lo:
            yield i, -1
            return


SETUPS = [
    dict(id='power_hour_range_break', name='Power-hour range breakout', family='session time',
         detect=power_hour_range_break,
         rules="Mark the 14:00-15:00 ET range. If it is at most a third of the day's range so far, the first 5-minute "
               "close beyond it between 15:00 and 15:40 on at least 1.2x normal volume leans with the break. "
               "Tested with and against."),
]
