"""Failed high/low-of-day break on dying volume with the 9/20 EMAs rolling over.
Added 2026-10-05 by price-structure-analyst via WebSearch (Brooks Trading Course and the TradeBook
"failed breakout" write-up: breakouts at extremes often fail, window 09:50-12:50, dying volume into
the break, 9 and 20 EMA rolling over). Distinct from turtle_soup (rolling 20-bar extreme) and
ib_break_fail: this is the running session extreme. Parameters fixed BEFORE any P&L was seen.
"""


def failed_hod_break(s):
    """From 09:50 to 12:50 a bar whose high breaks the running session high (set at least 6 bars
    earlier) by no more than 0.5 ATR, with relative volume below 1.0, closes back under that old
    high while EMA9 < EMA20 (closes) leans short; the mirror at the session low with EMA9 > EMA20
    leans long. One signal per side per session."""
    b = s.bars
    e9 = e20 = None
    fired = set()
    hi, hi_i, lo, lo_i = b[0].h, 0, b[0].l, 0
    for i, x in enumerate(b):
        e9 = x.c if e9 is None else e9 + (x.c - e9) * 2 / 10
        e20 = x.c if e20 is None else e20 + (x.c - e20) * 2 / 21
        if i > 0 and 590 <= x.m <= 770:
            atr, rv = s.atr[i], s.rvol[i]
            if atr and rv is not None and rv < 1.0:
                if -1 not in fired and x.h > hi and x.h - hi <= 0.5 * atr and x.c < hi and i - hi_i >= 6 and e9 < e20:
                    fired.add(-1)
                    yield i, -1
                elif 1 not in fired and x.l < lo and lo - x.l <= 0.5 * atr and x.c > lo and i - lo_i >= 6 and e9 > e20:
                    fired.add(1)
                    yield i, 1
        if x.h > hi:
            hi, hi_i = x.h, i
        if x.l < lo:
            lo, lo_i = x.l, i


SETUPS = [
    dict(id='failed_hod_break', name='Failed high/low-of-day break on dying volume', family='price-structure',
         detect=failed_hod_break,
         rules="Between 09:50 and 12:50, a bar that pokes through the running session high (set at least 6 bars "
               "earlier) by no more than 0.5 ATR on below-average volume, then closes back under it with the 9 EMA "
               "below the 20 EMA, leans short; the mirror at the session low leans long. One signal per side per session."),
]
