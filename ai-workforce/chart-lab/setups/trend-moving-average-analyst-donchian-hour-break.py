"""Intraday Donchian one-hour channel break on 5-minute bars.
Added 2026-10-02 by trend-moving-average-analyst: queue was fully coded, so this
run used WebSearch (ORB/VWAP/ADX intraday trend-day guides: breakouts of a
recent range that agree with VWAP side are the documented trend-day entry).
Turtle-style channel break shortened to 12 bars. Thresholds fixed before any
P&L was seen. Distinct from orb15/ib_break (fixed opening windows) and
d_donchian20 (daily bars): the channel here rolls through the whole session.
"""


def donchian_hour_break(s):
    """When a bar closes above the highest high (below the lowest low) of the
    previous 12 bars (one hour) and on the same side of session VWAP, signal
    with the break. One signal per side per session, 10:30 to 15:00."""
    b = s.bars
    fired = set()
    for i in range(12, len(b)):
        x = b[i]
        if not (630 <= x.m < 900):
            continue
        hh = max(y.h for y in b[i - 12:i])
        ll = min(y.l for y in b[i - 12:i])
        if x.c > hh and x.c > s.vwap[i] and 1 not in fired:
            fired.add(1)
            yield i, 1
        elif x.c < ll and x.c < s.vwap[i] and -1 not in fired:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='donchian_hour_break', name='One-hour channel break with VWAP', family='trend',
         detect=donchian_hour_break,
         rules="A 5-minute bar closing above the highest high (below the lowest low) of the previous 12 bars "
               "and on the same side of VWAP leans with the break; first break per side per session, "
               "10:30 to 15:00."),
]
