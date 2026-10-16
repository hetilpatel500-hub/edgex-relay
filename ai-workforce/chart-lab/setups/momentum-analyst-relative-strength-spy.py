"""Relative strength vs SPY continuation on 5-minute bars.
Added 2026-09-30 by momentum-analyst: the research queue is fully coded, so this
run used WebSearch (tradezella.com / tradingsim.com style "trade the strongest
name in a strong tape" guides) for an untested idea: a stock that has pulled
well away from SPY since the open keeps going. Thresholds were fixed before any
P&L was seen. Skipped for SPY itself.
"""
import core

_spy = {}


def _spy_day(day):
    if not _spy:
        for x in core.sessions('SPY'):
            _spy[x.day] = x
    return _spy.get(day)


def rel_strength_spy(s):
    """Between 10:00 and 13:00, when the stock's move from the open minus SPY's
    move from the open, in percent, is at least 4 times the stock's own ATR
    in percent, and price is on the same side of the stock's VWAP and closes in
    that direction (up bar for long), lean with the leader (long) or laggard
    (short). One signal per side per session. SPY is skipped."""
    if s.sym == 'SPY':
        return
    p = _spy_day(s.day)
    if p is None:
        return
    b = s.bars
    fired = set()
    for i in range(6, len(b)):
        x = b[i]
        if not (600 <= x.m < 780) or i >= len(p.bars):
            continue
        atr = s.atr[i]
        if not atr:
            continue
        rs = (x.c / s.open - 1) - (p.bars[i].c / p.open - 1)
        unit = atr / s.open
        if rs >= 4 * unit and x.c > s.vwap[i] and x.c > x.o and 1 not in fired:
            fired.add(1)
            yield i, 1
        elif rs <= -4 * unit and x.c < s.vwap[i] and x.c < x.o and -1 not in fired:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='rel_strength_spy', name='Relative strength vs SPY continuation', family='momentum',
         detect=rel_strength_spy,
         rules="Between 10:00 and 13:00, a stock that has outrun SPY since the open by at least four of its own "
               "5-minute ATRs (in percent), trading on the same side of its VWAP, leans with the leader on an up bar "
               "(long) or the laggard on a down bar (short). One signal per side per session; SPY itself is skipped."),
]
