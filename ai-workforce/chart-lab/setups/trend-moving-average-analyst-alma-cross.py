"""Arnaud Legoux Moving Average (9, offset 0.85, sigma 6) close-cross with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (ALMA: Gaussian-weighted average, weight peak at
offset*(n-1), spread n/sigma, weights normalised; defaults window 9, offset 0.85, sigma 6 per LuxAlgo/StockSharp;
TrendSpider reads price crossing the line as an early trend-change sign; sources advise combining with other tools).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: window 9, offset 0.85, sigma 6, built inside the session
(needs 9 bars), signal when the close crosses the line and sits on the same side of VWAP, 10:30 to 14:30 ET,
at most 2 signals per side per session.
"""
import math


def alma_cross(s):
    b = s.bars
    n, off, sg = 9, 0.85, 6.0
    m, sd = off * (n - 1), n / sg
    w = [math.exp(-((k - m) ** 2) / (2 * sd * sd)) for k in range(n)]
    tot = sum(w)
    al = [None] * len(b)
    for i in range(n - 1, len(b)):
        al[i] = sum(w[k] * b[i - n + 1 + k].c for k in range(n)) / tot
    cnt = {1: 0, -1: 0}
    for i in range(n, len(b)):
        if b[i].m < 630 or b[i].m >= 870:
            continue
        up = b[i].c > al[i] and b[i - 1].c <= al[i - 1]
        dn = b[i].c < al[i] and b[i - 1].c >= al[i - 1]
        if up and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='alma9_cross_vwap', name='ALMA (9, 0.85, 6) cross with VWAP', family='trend',
         detect=alma_cross,
         rules="Arnaud Legoux Moving Average (window 9, offset 0.85, sigma 6): a 5-minute close crossing above it "
               "with the close above VWAP leans long; crossing below it with the close below VWAP leans short. "
               "10:30 to 14:30 ET, at most two signals per side per session; tested with and against."),
]
