"""Intraday bar-to-bar gap (inefficiency) that holds into its own close.
Added 2026-10-06 by smart-money-analyst: new idea from outside the queue (the
queue's non-tape lines are coded). Tests whether a 5-minute bar that opens at
least 0.4 ATR away from the prior bar's close, and then closes beyond its own
open in the gap's direction (gap not being filled), continues. Rules fixed
before any P&L. Distinct from fvg_retest (3-bar imbalance, waits for retest)
and gap_* setups (overnight gap).
"""


def intrabar_gap_close(s):
    """Between 10:00 and 15:00 ET, a bar opening >= 0.4 ATR above the prior
    bar's close and closing at or above its open (below/below for the mirror),
    with the gap's far edge (prior close) unfilled by the bar's range. Up to
    two signals a day."""
    b = s.bars
    fired = 0
    for i in range(1, len(b)):
        x = b[i]
        if x.m < 600 or x.m >= 900 or fired >= 2:
            continue
        atr = s.atr[i]
        if not atr:
            continue
        pc = b[i - 1].c
        if x.o - pc >= 0.4 * atr and x.c >= x.o and x.l > pc:
            fired += 1
            yield i, 1
        elif pc - x.o >= 0.4 * atr and x.c <= x.o and x.h < pc:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='intrabar_gap_close', name='Intrabar gap holding into the close', family='smart money',
         detect=intrabar_gap_close,
         rules="Between 10:00 and 15:00 ET, a 5-minute bar that opens at least 0.4 ATR above the prior "
               "bar's close, closes at or above its own open and never trades back to the prior close "
               "leans long (mirror for a gap down). Up to two signals a day. Tested with and against."),
]
