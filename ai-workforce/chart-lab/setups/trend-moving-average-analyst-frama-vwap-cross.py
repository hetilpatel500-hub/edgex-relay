"""Ehlers Fractal Adaptive Moving Average (FRAMA 16) close-cross with VWAP agreement, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ehlers, "FRAMA", Stocks & Commodities Oct 2005, as coded by
ProRealCode, eSignal and LuxAlgo: alpha = exp(-4.6 * (D - 1)) clamped to [0.01, 1], 16-bar default; sources disagree on small
variants and none give an intraday backtest).
Parameters fixed BEFORE any P&L was seen: price = close, N = 16, D = (log(N1 + N2) - log(N3)) / log 2 with N1, N2 the
(high - low) / 8 of the older and newer 8-bar halves and N3 = (high - low) / 16 of the whole window; the filter restarts each
session at the first close and is only updated from bar 16. Long at the close of the first bar between 10:00 and 14:30 ET
that closes above FRAMA after the prior close was at or below it, while the close is above VWAP (mirror short). One signal
per side per session.
"""
import math

N = 16


def frama_cross(s):
    b = s.bars
    n = len(b)
    f = [None] * n
    for i in range(N - 1, n):
        w = b[i - N + 1:i + 1]
        h = N // 2
        n1 = (max(x.h for x in w[:h]) - min(x.l for x in w[:h])) / h
        n2 = (max(x.h for x in w[h:]) - min(x.l for x in w[h:])) / h
        n3 = (max(x.h for x in w) - min(x.l for x in w)) / N
        if n1 > 0 and n2 > 0 and n3 > 0:
            d = (math.log(n1 + n2) - math.log(n3)) / math.log(2)
        else:
            d = 1.0
        a = min(1.0, max(0.01, math.exp(-4.6 * (d - 1))))
        f[i] = b[i].c if f[i - 1] is None else a * b[i].c + (1 - a) * f[i - 1]
    done = {1: False, -1: False}
    for i in range(N, n - 1):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if not done[1] and b[i].c > f[i] and b[i - 1].c <= f[i - 1] and b[i].c > s.vwap[i]:
            done[1] = True; yield i, 1
        elif not done[-1] and b[i].c < f[i] and b[i - 1].c >= f[i - 1] and b[i].c < s.vwap[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='frama_vwap_cross', name='FRAMA (16) close-cross with VWAP agreement', family='trend',
         detect=frama_cross,
         rules="Ehlers' fractal adaptive moving average over 16 five-minute bars speeds up in clean trends and slows "
               "in chop. Between 10:00 and 14:30 the first close crossing above it while above VWAP leans long, the "
               "first close crossing below it while below VWAP leans short. One signal per side per session; tested "
               "with and against."),
]
