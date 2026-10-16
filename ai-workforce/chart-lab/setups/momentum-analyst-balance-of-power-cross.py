"""Balance of Power zero-line cross with VWAP agreement on 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (Igor Livshin's Balance of Power as described in broker indicator
guides: BoP = (close - open) / (high - low), smoothed with a 14-bar moving average; above zero buyers dominate, below
zero sellers dominate, and a zero-line cross is the sentiment-shift signal. The sources give no intraday evidence).
Untested intraday adaptation.
Parameters fixed BEFORE any P&L was seen: SMA(14) of BoP; cross through zero at a bar close between 10:30 and 14:30 ET,
only when that close is on the same side of session VWAP as the cross direction. One signal per session.
"""


def bop_cross(s):
    b = s.bars
    n = 14
    raw = [(x.c - x.o) / (x.h - x.l) if x.h > x.l else 0.0 for x in b]
    sm = [None] * len(b)
    for i in range(n - 1, len(b)):
        sm[i] = sum(raw[i - n + 1:i + 1]) / n
    for i in range(n, len(b) - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if sm[i] > 0 >= sm[i - 1] and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if sm[i] < 0 <= sm[i - 1] and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='bop_cross', name='Balance of Power zero cross with VWAP', family='momentum',
         detect=bop_cross,
         rules="Balance of Power scores each 5-minute bar by how far it closed from its open as a share of its "
               "range (+1 all buyers, -1 all sellers), averaged over 14 bars. Between 10:30 and 14:30 the first "
               "cross of that average up through zero while price is above VWAP leans long, the first cross down "
               "through zero while price is below VWAP leans short. One signal per session; tested with and "
               "against."),
]
