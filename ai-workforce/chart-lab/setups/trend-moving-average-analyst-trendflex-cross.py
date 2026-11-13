"""Ehlers Trendflex (20) zero-line cross with VWAP agreement, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ehlers 2020 Trendflex: SuperSmoother of closes, summed deviation of
the current smoothed value from its last N values, divided by its own RMS; secondary sources (TradingView, LuxAlgo, ProRealCode)
describe sustained readings above/below zero as trend persistence and one gives a fast/slow cross, none gives an intraday rule or backtest).
Rules fixed BEFORE any P&L was seen: N=20, SuperSmoother period N/2=10, RMS smoothing 0.04, series restarts each session,
signal on the close where Trendflex crosses zero (up = long, down = short) with the close on the same side of VWAP,
10:30 to 14:30 ET (needs 20 bars to settle), at most 2 signals per side per session.
"""
import math

N = 20


def trendflex_cross(s):
    b = s.bars
    n = len(b)
    p = N / 2
    a1 = math.exp(-1.414 * math.pi / p)
    c2 = 2 * a1 * math.cos(1.414 * math.pi / p)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    f = [b[0].c, b[1].c if n > 1 else b[0].c] + [0.0] * max(n - 2, 0)
    for i in range(2, n):
        f[i] = c1 * (b[i].c + b[i - 1].c) / 2 + c2 * f[i - 1] + c3 * f[i - 2]
    ms = 0.0
    tf = [0.0] * n
    for i in range(N, n):
        tot = sum(f[i] - f[i - k] for k in range(1, N + 1)) / N
        ms = 0.04 * tot * tot + 0.96 * ms
        tf[i] = tot / math.sqrt(ms) if ms > 0 else 0.0
    cnt = {1: 0, -1: 0}
    for i in range(N + 1, n):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        if tf[i] > 0 >= tf[i - 1] and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif tf[i] < 0 <= tf[i - 1] and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='trendflex_cross_vwap', name='Ehlers Trendflex (20) zero cross with VWAP', family='trend',
         detect=trendflex_cross,
         rules="Ehlers' Trendflex (20-bar deviation of a 10-bar SuperSmoother from its recent values, normalised by its "
               "RMS, restarted each session): crossing above zero with the close above VWAP leans long; crossing below "
               "zero with the close below VWAP leans short. 10:30 to 14:30 ET, at most two signals per side per "
               "session; tested with and against."),
]
