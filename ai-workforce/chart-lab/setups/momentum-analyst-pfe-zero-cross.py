"""Polarized Fractal Efficiency (PFE) zero-line cross with VWAP agreement, 5-minute bars.
Added 2026-10-13 by momentum-analyst via WebSearch (Hans Hannula, Stocks & Commodities 1994, as described by LuxAlgo and
Infront: PFE runs -100..+100 around zero, defaults n=10 and 5-bar EMA smoothing, a zero cross means the net move over the
window flipped sign). Formula used: PFE = 100 * sign(C - C[n]) * sqrt((C - C[n])^2 + n^2) / sum over the last n bars of
sqrt((C[i] - C[i-1])^2 + 1), then EMA(5). Parameters fixed BEFORE any P&L was seen. Long at the close of the first bar
between 10:30 and 14:30 ET where smoothed PFE crosses from at or below zero to above zero and the close is above session
VWAP (mirror for short). One signal per session. Price is in raw dollars, as in the published formula.
"""
import math


def pfe_zero_cross(s):
    b = s.bars
    n, sm = 10, 5
    k = 2 / (sm + 1)
    raw = [None] * len(b)
    for i in range(n, len(b)):
        den = sum(math.sqrt((b[j].c - b[j - 1].c) ** 2 + 1) for j in range(i - n + 1, i + 1))
        d = b[i].c - b[i - n].c
        raw[i] = 100 * (1 if d > 0 else -1 if d < 0 else 0) * math.sqrt(d * d + n * n) / den
    p = [None] * len(b)
    for i in range(n, len(b)):
        p[i] = raw[i] if p[i - 1] is None else p[i - 1] + k * (raw[i] - p[i - 1])
    for i in range(n + 1, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870 or p[i - 1] is None:
            continue
        if p[i - 1] <= 0 < p[i] and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if p[i - 1] >= 0 > p[i] and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='pfe_zero_cross', name='Polarized Fractal Efficiency zero cross with VWAP', family='momentum',
         detect=pfe_zero_cross,
         rules="PFE (10 bars, 5-bar smoothing) measures how straight the last ten bars' path was, signed by direction. "
               "Between 10:30 and 14:30, when it turns from negative to positive and price closes above VWAP, it leans "
               "long; the mirror leans short. One signal per session; tested with and against."),
]
