"""Yesterday's close location, confirmed by the first hour.
Added 2026-09-30 by session-gap-specialist via WebSearch (internal bar strength
and prior-day range bias write-ups). Thresholds (close in outer 20% of
yesterday's range, decision at the 10:30 close) were fixed before any P&L was seen.
"""


def prior_close_location(s):
    """Yesterday closed in the top (bottom) fifth of its high-low range. At the
    10:30 bar close (first hour done), if price is above (below) both
    yesterday's close and VWAP, lean with yesterday's closing strength.
    One signal per session."""
    p = s.prior
    if p is None or p.hi <= p.lo:
        return
    b = s.bars
    i = 11
    if len(b) <= i or b[i].m != 625:
        return
    loc = (p.close - p.lo) / (p.hi - p.lo)
    c = b[i].c
    if loc >= 0.8 and c > p.close and c > s.vwap[i]:
        yield i, 1
    elif loc <= 0.2 and c < p.close and c < s.vwap[i]:
        yield i, -1


SETUPS = [
    dict(id='prior_close_location', name="Yesterday's close near its extreme, first hour agrees",
         family='session', detect=prior_close_location,
         rules="When yesterday closed in the top (bottom) fifth of its high-low range and, at the 10:30 close, "
               "price is above (below) both yesterday's close and VWAP, lean with that direction. "
               "Tested with and against; one signal per session."),
]
