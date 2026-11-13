"""Chande Momentum Oscillator (CMO) re-entry from +/-50, 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (Incredible Charts, LuxAlgo, Capital.com CMO descriptions: CMO =
100 * (sum of up closes - sum of down closes) / (sum of both) over n bars, bounded -100..+100; +/-50 are the quoted
overbought/oversold levels and Chande's own rule is counter-trend at those levels. The sources are indicator
descriptions with no intraday evidence and say extremes can persist in trends). Untested intraday adaptation.
Parameters fixed BEFORE any P&L was seen: n = 14; short at the close of the first bar between 10:30 and 14:30 ET where
CMO crosses back down through +50 (mirror: back up through -50 for long). No VWAP or candle filter. One signal per
session.
"""


def cmo_extreme_reentry(s):
    b = s.bars
    n = 14
    up = [max(b[i].c - b[i - 1].c, 0) if i else 0 for i in range(len(b))]
    dn = [max(b[i - 1].c - b[i].c, 0) if i else 0 for i in range(len(b))]
    cmo = [None] * len(b)
    for i in range(n, len(b)):
        u, d = sum(up[i - n + 1:i + 1]), sum(dn[i - n + 1:i + 1])
        cmo[i] = 100 * (u - d) / (u + d) if u + d else 0
    for i in range(n + 1, len(b) - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if cmo[i] > -50 and cmo[i - 1] <= -50:
            yield i, 1
            return
        if cmo[i] < 50 and cmo[i - 1] >= 50:
            yield i, -1
            return


SETUPS = [
    dict(id='cmo_extreme_reentry', name='Chande Momentum Oscillator re-entry from +/-50', family='momentum',
         detect=cmo_extreme_reentry,
         rules="The Chande Momentum Oscillator compares the sum of up closes with the sum of down closes over 14 "
               "5-minute bars, from -100 to +100. Between 10:30 and 14:30 the first cross back up through -50 leans "
               "long and the first cross back down through +50 leans short. One signal per session; tested with and "
               "against."),
]
