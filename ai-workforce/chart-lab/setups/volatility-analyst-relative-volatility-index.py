"""Relative Volatility Index 50-line cross with VWAP agreement on 5-minute bars.
Added 2026-10-11 by volatility-analyst via WebSearch (Donald Dorsey's 1993 RVI as documented by TA-Lib, LuxAlgo,
TrendSpider, Infront and MotiveWave: RSI arithmetic applied to a rolling standard deviation of closes, routed to an
up bucket on up closes and a down bucket on down closes, smoothed, RVI = 100 * up / (up + down); Dorsey intended it as
a confirmation filter, long only while above 50, short only while below). The sources give no intraday evidence.
Untested adaptation. Parameters fixed BEFORE any P&L was seen: stdev(close, 10), Wilder smoothing 14, computed inside
the session only (starts after 10 bars of stdev), 50-line cross at a bar close between 10:30 and 14:30 ET, only when
that close is on the same side of session VWAP as the cross direction. One signal per session.
"""
import math


def rvi_cross(s):
    b = s.bars
    n = len(b)
    c = [x.c for x in b]
    sd = [None] * n
    for i in range(9, n):
        w = c[i - 9:i + 1]
        mu = sum(w) / 10
        sd[i] = math.sqrt(sum((v - mu) ** 2 for v in w) / 10)
    up = dn = None
    rvi = [None] * n
    for i in range(10, n):
        u = sd[i] if c[i] > c[i - 1] else 0.0
        d = sd[i] if c[i] < c[i - 1] else 0.0
        up = u if up is None else (up * 13 + u) / 14
        dn = d if dn is None else (dn * 13 + d) / 14
        rvi[i] = 100 * up / (up + dn) if up + dn > 0 else 50.0
    for i in range(12, n - 1):
        m = b[i].m
        if m < 630 or m > 870 or rvi[i - 1] is None:
            continue
        if rvi[i] > 50 >= rvi[i - 1] and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if rvi[i] < 50 <= rvi[i - 1] and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='rvi_dorsey_cross', name='Relative Volatility Index 50 cross with VWAP', family='volatility',
         detect=rvi_cross,
         rules="The Relative Volatility Index measures whether the recent size of price swings (10-bar standard "
               "deviation of closes) is coming on up bars or down bars, smoothed over 14 bars and scaled 0-100. "
               "Between 10:30 and 14:30 the first cross up through 50 while price is above VWAP leans long, the "
               "first cross down through 50 while price is below VWAP leans short. One signal per session; "
               "tested with and against."),
]
