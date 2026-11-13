"""Qstick zero-line cross with VWAP agreement, 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (Chande and Kroll, The New Technical Trader 1994, as described by LuxAlgo
and TradingView community scripts: Qstick is the moving average of the candle body, close minus open; a cross of the zero
line is the main signal). Parameters fixed BEFORE any P&L was seen: LuxAlgo's 8-bar simple average. Long at the close of
the first bar between 10:30 and 14:30 ET where Qstick(8) crosses from at or below zero to above zero and the close is above
session VWAP (mirror for short). One signal per session.
"""


def qstick_zero_cross(s):
    b = s.bars
    body = [x.c - x.o for x in b]
    q = [None] * len(b)
    for i in range(7, len(b)):
        q[i] = sum(body[i - 7:i + 1]) / 8
    for i in range(9, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        if q[i - 1] is None:
            continue
        if q[i - 1] <= 0 < q[i] and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if q[i - 1] >= 0 > q[i] and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='qstick_zero_cross', name='Qstick zero-line cross with VWAP', family='momentum',
         detect=qstick_zero_cross,
         rules="Qstick is the 8-bar average of candle bodies (close minus open). Between 10:30 and 14:30, when it "
               "turns from negative to positive and price closes above VWAP, it leans long; the mirror (positive to "
               "negative, price under VWAP) leans short. One signal per session; tested with and against."),
]
