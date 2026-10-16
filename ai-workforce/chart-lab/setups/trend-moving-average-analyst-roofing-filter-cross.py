"""Ehlers Roofing Filter zero-line cross with VWAP agreement, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ehlers' Roofing Filter: a two-pole high-pass at 48 bars
feeding a two-pole SuperSmoother at 10 bars; sources describe zero crossings as cycle-scale swing shifts, the 48/10 defaults
come from Ehlers' daily examples and no source gives an intraday rule or backtest).
Parameters fixed BEFORE any P&L was seen: Ehlers' published 48/10 coefficients applied to closes, the series restarts each
session (first two bars seeded at zero), signal on the close where the filter crosses zero (up = long, down = short) and the
close is on the same side of VWAP, 11:00 to 14:30 ET (48-bar high-pass needs time to settle), at most 2 signals per side
per session.
"""
import math

HP_N, SS_N = 48, 10


def roofing_cross(s):
    b = s.bars
    n = len(b)
    a = (math.cos(0.707 * 2 * math.pi / HP_N) + math.sin(0.707 * 2 * math.pi / HP_N) - 1) / math.cos(0.707 * 2 * math.pi / HP_N)
    k1 = (1 - a / 2) ** 2
    a1 = math.exp(-1.414 * math.pi / SS_N)
    c2 = 2 * a1 * math.cos(1.414 * math.pi / SS_N)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    hp, f = [0.0] * n, [0.0] * n
    for i in range(2, n):
        hp[i] = k1 * (b[i].c - 2 * b[i - 1].c + b[i - 2].c) + 2 * (1 - a) * hp[i - 1] - (1 - a) ** 2 * hp[i - 2]
        f[i] = c1 * (hp[i] + hp[i - 1]) / 2 + c2 * f[i - 1] + c3 * f[i - 2]
    cnt = {1: 0, -1: 0}
    for i in range(3, n):
        if b[i].m < 660 or b[i].m + 5 > 870:
            continue
        if f[i] > 0 >= f[i - 1] and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif f[i] < 0 <= f[i - 1] and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='roofing_cross_vwap', name='Ehlers Roofing Filter zero cross with VWAP', family='trend',
         detect=roofing_cross,
         rules="Ehlers' Roofing Filter (48-bar high-pass into a 10-bar SuperSmoother, restarted each session): the "
               "filter crossing above zero with the close above VWAP leans long; crossing below zero with the close "
               "below VWAP leans short. 11:00 to 14:30 ET, at most two signals per side per session; tested with and against."),
]
