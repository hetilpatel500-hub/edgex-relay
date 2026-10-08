"""Choppiness Index trend start: CI(14) falls below 38.2 with the close on one side of the 20-bar SMA.
Added 2026-10-06 by trend-moving-average-analyst via WebSearch (StockSharp "Choppiness Index Breakout":
CI period 14, trending threshold 38.2, SMA 20, 5-minute candles). Parameters taken from that source
and fixed BEFORE any P&L was seen; the source's CI-based exit is not used (the lab's exits apply).
"""
import math


def choppiness_trend_start(s):
    """CI = 100 * log10(sum of true range over 14 bars / (highest high - lowest low over 14 bars)) / log10(14).
    Between 10:00 and 14:30, the first bar where CI drops below 38.2 (it was at or above 38.2 on the
    prior bar) and the close is above (below) the 20-bar SMA of closes leans long (short). One signal
    per side per session."""
    b = s.bars
    tr = []
    ci = []
    fired = set()
    for i, x in enumerate(b):
        pc = b[i - 1].c if i else x.o
        tr.append(max(x.h - x.l, abs(x.h - pc), abs(x.l - pc)))
        if i < 19:
            ci.append(None)
            continue
        hh = max(y.h for y in b[i - 13:i + 1])
        ll = min(y.l for y in b[i - 13:i + 1])
        c = 100 * math.log10(sum(tr[i - 13:i + 1]) / (hh - ll)) / math.log10(14) if hh > ll else 100.0
        ci.append(c)
        prev = ci[i - 1]
        if prev is None or not (600 <= x.m <= 870) or not s.atr[i]:
            continue
        if prev >= 38.2 > c:
            sma = sum(y.c for y in b[i - 19:i + 1]) / 20
            d = 1 if x.c > sma else -1 if x.c < sma else 0
            if d and d not in fired:
                fired.add(d)
                yield i, d


SETUPS = [
    dict(id='choppiness_trend_start', name='Choppiness Index trend start (CI14 < 38.2) with SMA20 side',
         family='trend', detect=choppiness_trend_start,
         rules="Between 10:00 and 14:30, the first bar where the 14-bar Choppiness Index drops below 38.2 "
               "(from at or above it) with the close above (below) the 20-bar SMA leans long (short). "
               "One signal per side per session."),
]
