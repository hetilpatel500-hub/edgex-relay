"""Vertical Horizontal Filter trend-start cross with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (Adam White 1991, as described by LuxAlgo, TrendSpider
and StockDoctor: VHF = (highest close - lowest close over N bars) / sum of absolute bar-to-bar close changes, default
N = 28; higher means more directional). Parameters fixed BEFORE any P&L was seen: N = 28 and the 0.30 'strong trend'
level from the TrendSpider guide. Long at the close of the first bar between 11:50 and 14:30 ET where VHF crosses
from at or below 0.30 to above it, the close is above its close 28 bars earlier and above session VWAP (mirror for
short). One signal per session.
"""

N = 28
LEVEL = 0.30


def vhf_trend_start(s):
    b = s.bars
    c = [x.c for x in b]
    v = [None] * len(b)
    for i in range(N, len(b)):
        w = c[i - N:i + 1]
        tot = sum(abs(w[k] - w[k - 1]) for k in range(1, len(w)))
        v[i] = (max(w) - min(w)) / tot if tot > 0 else 0.0
    for i in range(N + 1, len(b) - 1):
        if b[i].m < 710 or b[i].m > 870:
            continue
        if v[i - 1] is None or v[i] is None:
            continue
        if v[i - 1] <= LEVEL < v[i]:
            if c[i] > c[i - N] and c[i] > s.vwap[i]:
                yield i, 1
                return
            if c[i] < c[i - N] and c[i] < s.vwap[i]:
                yield i, -1
                return


SETUPS = [
    dict(id='vhf_trend_start', name='Vertical Horizontal Filter trend start with VWAP', family='trend',
         detect=vhf_trend_start,
         rules="VHF compares the 28-bar high-to-low close range with the total distance price travelled; above 0.30 "
               "the market is moving in one direction. Between 11:50 and 14:30, when VHF crosses up through 0.30, "
               "price is above its close 28 bars ago and above VWAP, it leans long; the mirror leans short. One "
               "signal per session; tested with and against."),
]
