"""Tweezer bottom / top at the session extreme, 5-minute bars.
Added 2026-10-14 by candlestick-specialist via WebSearch (Elder-ray/Triple Screen search surfaced no untested 5-minute
rule; the pattern itself is the classic two-candle tweezer from Nison's Japanese candlestick texts: two consecutive
candles with matching extremes and opposite colors). Not covered by engulfing_hammer, star_at_vwap_band, pin bars or
three soldiers/crows. Rules fixed BEFORE any P&L was seen: lows (highs) of bars i-1 and i within 0.05 ATR of each other,
bar i-1 closes down (up) and bar i closes up (down), and the shared low (high) is the lowest low (highest high) of the
session so far, 10:00 to 14:30 ET, at most one signal per side per session.
"""


def tweezer_extreme(s):
    b = s.bars
    n = len(b)
    seen = {1: False, -1: False}
    lo_so_far = b[0].l
    hi_so_far = b[0].h
    for i in range(1, n):
        x, p = b[i], b[i - 1]
        tol = 0.05 * s.atr[i]
        lo_prev, hi_prev = lo_so_far, hi_so_far
        lo_so_far, hi_so_far = min(lo_so_far, x.l), max(hi_so_far, x.h)
        if x.m < 600 or x.m + 5 > 870:
            continue
        # tweezer bottom: shared low is the session low through bar i
        if (not seen[1] and p.c < p.o and x.c > x.o and abs(x.l - p.l) <= tol
                and min(x.l, p.l) <= min(lo_prev, p.l) and min(x.l, p.l) <= lo_so_far):
            seen[1] = True
            yield i, 1
        elif (not seen[-1] and p.c > p.o and x.c < x.o and abs(x.h - p.h) <= tol
                and max(x.h, p.h) >= max(hi_prev, p.h) and max(x.h, p.h) >= hi_so_far):
            seen[-1] = True
            yield i, -1


SETUPS = [
    dict(id='tweezer_session_extreme', name='Tweezer bottom/top at the session extreme', family='candlestick',
         detect=tweezer_extreme,
         rules="Two consecutive 5-minute candles of opposite color whose lows (tweezer bottom: first down, second up) "
               "or highs (tweezer top: first up, second down) match within 0.05 ATR, with that price being the "
               "session's lowest low (highest high) so far. The bottom leans long and the top leans short at the "
               "second candle's close. 10:00 to 14:30 ET, one signal per side per session; tested with and against."),
]
