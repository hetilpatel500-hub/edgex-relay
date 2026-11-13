"""Chandelier Exit stop-and-reverse flip, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (MQL5 market page "Chandelier Exit an Stop and Reverse
Trend Filter" documents the 22-bar lookback, 22-period ATR, 3.0 multiplier defaults and the close-based variant: long
stop = highest close of 22 bars - 3.0 x ATR22, short stop = lowest close of 22 bars + 3.0 x ATR22, trend flips when the
close crosses the opposite stop; the page is a vendor description with no intraday evidence). Untested intraday
adaptation. Parameters fixed BEFORE any P&L was seen: 22 / 22 / 3.0, ATR as the simple mean of the true range, all
inside the session (no overnight bars). Signal at the close of the first bar between 10:30 and 14:30 ET where the trend
flips (close above the short stop = long, close below the long stop = short). One signal per session.
"""


def chandelier_exit_flip(s):
    b = s.bars
    n, mult = 22, 3.0
    tr = [b[0].h - b[0].l] + [max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c))
                              for i in range(1, len(b))]
    d = 0
    for i in range(n, len(b) - 1):
        atr = sum(tr[i - n + 1:i + 1]) / n
        win = [x.c for x in b[i - n + 1:i + 1]]
        long_stop = max(win) - mult * atr
        short_stop = min(win) + mult * atr
        prev = d
        if b[i].c > short_stop:
            d = 1
        elif b[i].c < long_stop:
            d = -1
        if d != prev and prev != 0 and 630 <= b[i].m <= 870:
            yield i, d
            return


SETUPS = [
    dict(id='chandelier_exit_flip', name='Chandelier Exit flip', family='trend',
         detect=chandelier_exit_flip,
         rules="The Chandelier Exit trails 3 average true ranges below the highest close of the last 22 bars (or above "
               "the lowest close). When the close breaks through the trailing line the trend flips. Between 10:30 and "
               "14:30 the first flip up leans long and the first flip down leans short. One signal per session; "
               "tested with and against."),
]
