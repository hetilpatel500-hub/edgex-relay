"""Pin bar rejection at yesterday's high or low.
Added 2026-10-07 by candlestick-specialist via the lab queue (classic price-action pin bar; the existing
candlestick setups test candles only at VWAP, POC and IB extremes, never at yesterday's high/low).
Parameters fixed BEFORE any P&L was seen: a 5-minute bar between 9:45 and 14:30 ET with range at least 1.0 ATR,
whose low pierces yesterday's low (high pierces yesterday's high) and whose close is back inside yesterday's
range, with the rejecting wick at least 60% of the bar's range and at least twice the body. Long at the low,
short at the high; one per side per session.
"""


def pin_bar_prior_extreme(s):
    p = s.prior
    if p is None:
        return
    b = s.bars
    done = set()
    for i in range(3, len(b)):
        x = b[i]
        if x.m < 585 or x.m > 870 or not s.atr[i]:
            continue
        rng = x.h - x.l
        if rng < s.atr[i]:
            continue
        body = abs(x.c - x.o)
        if x.l < p.lo and x.c > p.lo and (min(x.o, x.c) - x.l) >= 0.6 * rng and (min(x.o, x.c) - x.l) >= 2 * body \
                and 1 not in done:
            done.add(1)
            yield i, 1
        elif x.h > p.hi and x.c < p.hi and (x.h - max(x.o, x.c)) >= 0.6 * rng and (x.h - max(x.o, x.c)) >= 2 * body \
                and -1 not in done:
            done.add(-1)
            yield i, -1


SETUPS = [
    dict(id='pin_bar_prior_extreme', name="Pin bar rejection at yesterday's high/low", family='candlestick',
         detect=pin_bar_prior_extreme,
         rules="A 5-minute bar (9:45-14:30, range at least 1 ATR) that wicks through yesterday's low and closes back "
               "above it, with the lower wick at least 60% of the range and twice the body, leans long; the mirror "
               "at yesterday's high leans short. One per side per session; tested with and against."),
]
