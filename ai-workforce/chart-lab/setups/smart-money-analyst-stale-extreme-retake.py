"""Stale day-extreme retake after the afternoon lull.
Added 2026-10-05 by smart-money-analyst: the open queue was empty, so this run took the "stale high/low
liquidity" idea (resting stops above/below an extreme set hours earlier get taken when the afternoon
session returns to it). Rules fixed BEFORE any P&L was seen. Distinct from power_hour_range_break
(14:00-15:00 box) and equal_hl_sweep (equal highs/lows): this one needs the day's extreme to be old.
"""


def stale_extreme_retake(s):
    """From 14:00 to 15:30 ET, the first 5-minute close beyond the day's high (or low) so far, where that
    extreme was set before 12:00 ET, leans with the break. One signal per session."""
    b = s.bars
    hi = lo = None
    hi_m = lo_m = 0
    for i, x in enumerate(b):
        if 840 <= x.m < 930 and hi is not None:
            if x.c > hi and hi_m < 720:
                yield i, 1
                return
            if x.c < lo and lo_m < 720:
                yield i, -1
                return
        if hi is None or x.h > hi:
            hi, hi_m = x.h, x.m
        if lo is None or x.l < lo:
            lo, lo_m = x.l, x.m


SETUPS = [
    dict(id='stale_extreme_retake', name='Stale day-extreme retake after 14:00', family='smart money',
         detect=stale_extreme_retake,
         rules="From 14:00 to 15:30 ET, the first 5-minute close beyond the day's high (or low) so far, where that "
               "extreme was set before 12:00 ET, leans with the break. Tested with and against; one signal per session."),
]
