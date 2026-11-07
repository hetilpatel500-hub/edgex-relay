"""DeMarker oscillator re-entry from 0.30 / 0.70 on 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (Capital.com and MQL5 DeMarker guides, SuperMoney overview: DeMarker =
SMA(DeMax) / (SMA(DeMax) + SMA(DeMin)) with DeMax = max(high - prior high, 0) and DeMin = max(prior low - low, 0);
the quoted range rule is long when it falls below 0.30 and climbs back above it, short when it rises above 0.70 and
falls back under it. The sources give no intraday evidence). Untested intraday adaptation.
Parameters fixed BEFORE any P&L was seen: n = 14; first cross back through 0.30 / 0.70 at a bar close between 10:30
and 14:30 ET. No VWAP or candle filter. One signal per session.
"""


def demarker_reentry(s):
    b = s.bars
    n = 14
    dmax = [max(b[i].h - b[i - 1].h, 0) if i else 0 for i in range(len(b))]
    dmin = [max(b[i - 1].l - b[i].l, 0) if i else 0 for i in range(len(b))]
    dem = [None] * len(b)
    for i in range(n, len(b)):
        u, d = sum(dmax[i - n + 1:i + 1]), sum(dmin[i - n + 1:i + 1])
        dem[i] = u / (u + d) if u + d else 0.5
    for i in range(n + 1, len(b) - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if dem[i] > 0.30 and dem[i - 1] <= 0.30:
            yield i, 1
            return
        if dem[i] < 0.70 and dem[i - 1] >= 0.70:
            yield i, -1
            return


SETUPS = [
    dict(id='demarker_reentry', name='DeMarker re-entry from 0.30 / 0.70', family='momentum',
         detect=demarker_reentry,
         rules="The DeMarker oscillator compares how much each 5-minute bar's high exceeds the previous high with "
               "how much its low undercuts the previous low, over 14 bars (0 to 1). Between 10:30 and 14:30 the "
               "first cross back up through 0.30 leans long and the first cross back down through 0.70 leans "
               "short. One signal per session; tested with and against."),
]
