"""Ehlers Center of Gravity oscillator trigger cross at the edge of its envelope, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ehlers' Center of Gravity oscillator, Rocket Science for
Traders 2001, as described by LuxAlgo, cTrader help and TradingView scripts: the trigger is the CG delayed one bar; a cross
up through it is a cycle-trough cue, down through it a crest cue, strongest near the edge of the recent envelope; sources
give no intraday backtest and disagree on defaults).
Parameters fixed BEFORE any P&L was seen: price = (high + low) / 2, window N = 10, CG = -sum(k * p[i-k+1]) / sum(p) for
k = 1..N (newest bar weighted 1, oldest N), trigger = CG one bar earlier, the series restarts each session. Long at the
close of the first bar between 10:00 and 14:30 ET where CG turns up through its trigger while CG sits in the lowest 20% of
its own range over the last 20 bars (mirror short: highest 20%, turning down). One signal per side per session. No VWAP
or volume filter.
"""

N, ENV, EDGE = 10, 20, 0.2


def ehlers_cg(s):
    b = s.bars
    n = len(b)
    p = [(x.h + x.l) / 2 for x in b]
    cg = [None] * n
    for i in range(N - 1, n):
        den = sum(p[i - N + 1:i + 1])
        num = sum(k * p[i - k + 1] for k in range(1, N + 1))
        cg[i] = -num / den if den else 0.0
    done = {1: False, -1: False}
    for i in range(N + ENV, n - 1):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        win = cg[i - ENV + 1:i + 1]
        lo, hi = min(win), max(win)
        if hi - lo <= 0:
            continue
        pos = (cg[i] - lo) / (hi - lo)
        if not done[1] and cg[i - 1] <= cg[i - 2] and cg[i] > cg[i - 1] and pos <= EDGE:
            done[1] = True; yield i, 1
        elif not done[-1] and cg[i - 1] >= cg[i - 2] and cg[i] < cg[i - 1] and pos >= 1 - EDGE:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='ehlers_cg', name='Ehlers Center of Gravity trigger cross at envelope edge', family='trend',
         detect=ehlers_cg,
         rules="Ehlers' Center of Gravity is a 10-bar weighted balance point of the bar midpoints; its trigger is the "
               "same line one bar later. Between 10:00 and 14:30 the first turn up through the trigger while the line "
               "is in the lowest fifth of its 20-bar range leans long, the first turn down in the highest fifth "
               "leans short. One signal per side per session; tested with and against."),
]
