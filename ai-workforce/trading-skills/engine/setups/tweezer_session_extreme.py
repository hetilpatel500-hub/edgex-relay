"""Tweezer bottom/top at the session extreme (5-minute bars).

Two consecutive candles of opposite color whose lows (tweezer bottom: first
down, second up) or highs (tweezer top: first up, second down) match within
0.05 ATR, at the session's lowest low (highest high) so far. The bottom
leans long and the top leans short at the second candle's close. 10:00 to
14:30 ET, one signal per side per session.

Snapshot from the Edgex chart lab (12 US symbols, 107 sessions, 2026-05-15
to 2026-10-23, out-of-sample from 2026-09-09): validated when FADED (traded
against the lean) with the rvol filter and a 2 ATR stop / 4 ATR target:
38 OOS trades, 61% win, +0.36R avg, PF 2.01, t 1.91. Re-test on your own
data with the backtester before relying on it.
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
