"""Ehlers Decycler Oscillator zero cross with VWAP agreement, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ehlers, "Decyclers", TASC Sept 2015: oscillator = fast
decycler minus slow decycler, slow cutoff 1.25x the fast; LuxAlgo and TradingView write-ups call the zero cross a cycle
turn; no source gives an intraday rule or a backtest).
Parameters fixed BEFORE any P&L was seen: one-pole decyclers (price minus Ehlers' high-pass) with cutoffs 30 and 37.5 bars
on closes, restarted each session (seeded at the first close), oscillator as percent of price, signal on the close where it
crosses zero (up = long, down = short) and the close is on the same side of VWAP, 10:30 to 14:30 ET, at most 2 signals per
side per session.
"""
import math

FAST, SLOW = 30.0, 37.5


def _decycle(c, p):
    w = 2 * math.pi / p
    a = (math.cos(w) + math.sin(w) - 1) / math.cos(w)
    out = [c[0]]
    for i in range(1, len(c)):
        out.append(a / 2 * (c[i] + c[i - 1]) + (1 - a) * out[-1])
    return out


def decycler_cross(s):
    b = s.bars
    c = [x.c for x in b]
    if len(c) < 3:
        return
    f, sl = _decycle(c, FAST), _decycle(c, SLOW)
    o = [100 * (f[i] - sl[i]) / c[i] for i in range(len(c))]
    cnt = {1: 0, -1: 0}
    for i in range(2, len(b)):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        if o[i] > 0 >= o[i - 1] and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif o[i] < 0 <= o[i - 1] and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='decycler_osc_vwap', name='Ehlers Decycler Oscillator zero cross with VWAP', family='trend',
         detect=decycler_cross,
         rules="Ehlers' Decycler Oscillator (30-bar decycler minus 37.5-bar decycler, as percent of price, restarted each "
               "session): crossing above zero with the close above VWAP leans long; crossing below zero with the close "
               "below VWAP leans short. 10:30 to 14:30 ET, at most two signals per side per session; tested with and against."),
]
