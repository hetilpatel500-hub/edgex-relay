"""Trend-day vote at 10:30, then the first morning pullback to VWAP, lean with the day.
Added 2026-10-05 by session-gap-specialist via WebSearch (trend-day classification write-ups: a day is called a
trend day when 4 of 5 conditions agree). Parameters fixed BEFORE any P&L was seen: the five votes below, a
threshold of 4, entry window 10:30 to 13:30, pullback within 0.25 ATR of VWAP. The lab tests it with and against.
"""


def trend_day_vote(s):
    """At 10:30 (12 bars) vote for a direction d: (1) at least 9 of the 12 closes on the d side of VWAP, (2) the
    12th close beyond the 15-minute opening range in d, (3) the open within 25% of the initial-balance range from
    the opposite extreme, (4) first-hour relative volume averaging at least 1.2, (5) the first-hour close at the
    d-side 25% of the IB range. With 4 or more votes, the first bar from 10:30 to 13:30 whose range comes within
    0.25 ATR of VWAP and which closes on the d side of VWAP gives the signal. One signal per session."""
    b = s.bars
    if len(b) < 40:
        return
    rng = s.ib_hi - s.ib_lo
    if rng <= 0:
        return
    rv = [x for x in s.rvol[:12] if x is not None]
    for d in (1, -1):
        v = 0
        v += sum(1 for k in range(12) if d * (b[k].c - s.vwap[k]) > 0) >= 9
        v += d * (b[11].c - (s.or_hi if d == 1 else s.or_lo)) > 0
        v += (d * (s.open - (s.ib_lo if d == 1 else s.ib_hi)) >= 0 and
              abs(s.open - (s.ib_lo if d == 1 else s.ib_hi)) <= 0.25 * rng)
        v += bool(rv) and sum(rv) / len(rv) >= 1.2
        v += abs(b[11].c - (s.ib_hi if d == 1 else s.ib_lo)) <= 0.25 * rng
        if v < 4:
            continue
        for k in range(12, len(b) - 1):
            if b[k].m >= 810:
                return
            near = (b[k].l if d == 1 else b[k].h)
            if abs(near - s.vwap[k]) <= 0.25 * s.atr[k] or (b[k].l <= s.vwap[k] <= b[k].h):
                if d * (b[k].c - s.vwap[k]) > 0:
                    yield k, d
                    return
        return


SETUPS = [
    dict(id='trend_day_vote', name='Trend-day vote, first VWAP pullback', family='session',
         detect=trend_day_vote,
         rules="At 10:30, a day earns a vote each for: 9 of 12 closes on one side of VWAP; the 10:30 close beyond "
               "the 15-minute opening range; the open within 25% of the IB range of the opposite extreme; first-hour "
               "relative volume at least 1.2; the 10:30 close in the outer 25% of the IB range. With 4 or more "
               "votes, the first bar to 13:30 that comes within 0.25 ATR of VWAP and closes on the trend side "
               "leans with the day. Tested with and against; one signal per session."),
]
