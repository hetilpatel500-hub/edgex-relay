"""Developing day-range midpoint (equilibrium) hold on 5-minute bars.
Added 2026-09-30 by session-gap-specialist: the research queue was fully coded,
so this run used WebSearch (edgeful.com, luxalgo.com and others describing the
session range midpoint as equilibrium: above it is premium, below it discount,
with midpoint retests used for entry location). Untested here. Distinct from
orb_retest / ib_retest (they retest a range edge, not the developing 50%).
"""


def range_midpoint_hold(s):
    """Once the session range is at least 2 ATR wide and the extreme that made
    it is on one side, a pullback whose wick tags the developing range midpoint
    (within 0.1 ATR) and closes back on the extreme's side, in that direction,
    leans with the trend. The high must have come after the low for a long (low
    after high for a short). One signal per side per session, 10:30 to 14:30."""
    b = s.bars
    hi, lo = b[0].h, b[0].l
    hi_i = lo_i = 0
    fired = set()
    for i in range(1, len(b)):
        x = b[i]
        mid = (hi + lo) / 2            # range known before this bar
        atr = s.atr[i]
        if 630 <= x.m < 870 and atr and hi - lo >= 2 * atr:
            if hi_i > lo_i and 1 not in fired and x.l <= mid + 0.1 * atr and x.c > mid and x.c > x.o:
                fired.add(1)
                yield i, 1
            elif lo_i > hi_i and -1 not in fired and x.h >= mid - 0.1 * atr and x.c < mid and x.c < x.o:
                fired.add(-1)
                yield i, -1
        if x.h > hi:
            hi, hi_i = x.h, i
        if x.l < lo:
            lo, lo_i = x.l, i


SETUPS = [
    dict(id='range_midpoint_hold', name='Developing day-range midpoint hold', family='session',
         detect=range_midpoint_hold,
         rules="When the day's range is at least 2 ATR wide and the high came after the low, a bar that wicks "
               "down to the range midpoint (within 0.1 ATR) and closes back above it on an up bar leans long; "
               "the mirror image leans short. One signal per side per session, 10:30 to 14:30."),
]
