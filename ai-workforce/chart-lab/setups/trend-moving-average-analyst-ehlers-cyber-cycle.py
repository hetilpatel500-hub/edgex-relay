"""Ehlers Cyber Cycle trigger cross from the wrong side of zero, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (Ehlers' Cyber Cycle, Cybernetic Analysis for Stocks and
Futures 2004 ch. 4, as described by LuxAlgo, cTrader help and TradingView scripts: the trigger is the cycle delayed one bar,
the cycle crossing up through it marks a trough, down through it a crest; vendors suggest filtering crossings by a
threshold because they are noisy). The sources are platform docs and community scripts with no intraday backtest.
Parameters fixed BEFORE any P&L was seen: alpha = 0.07 (Ehlers' value), smoothing (p + 2p1 + 2p2 + p3) / 6 on the close,
first 7 bars of the session use Ehlers' start-up formula (p - 2p1 + p2) / 4; the series restarts each session. Long at the
close of the first bar between 10:00 and 14:30 ET where the cycle crosses up through its trigger while the cycle is below
zero (mirror short: down through, cycle above zero). One signal per side per session. No VWAP or volume filter.
"""


def cyber_cycle(s):
    b = s.bars
    a = 0.07
    n = len(b)
    p = [x.c for x in b]
    sm = [0.0] * n
    cy = [0.0] * n
    for i in range(n):
        if i >= 3:
            sm[i] = (p[i] + 2 * p[i - 1] + 2 * p[i - 2] + p[i - 3]) / 6
        else:
            sm[i] = p[i]
        if i < 7:
            cy[i] = (p[i] - 2 * p[i - 1] + p[i - 2]) / 4 if i >= 2 else 0.0
        else:
            cy[i] = ((1 - 0.5 * a) ** 2 * (sm[i] - 2 * sm[i - 1] + sm[i - 2])
                     + 2 * (1 - a) * cy[i - 1] - (1 - a) ** 2 * cy[i - 2])
    done = {1: False, -1: False}
    for i in range(9, n - 1):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if not done[1] and cy[i - 1] <= cy[i - 2] and cy[i] > cy[i - 1] and cy[i] < 0:
            done[1] = True; yield i, 1
        elif not done[-1] and cy[i - 1] >= cy[i - 2] and cy[i] < cy[i - 1] and cy[i] > 0:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='ehlers_cyber_cycle', name="Ehlers Cyber Cycle trigger cross", family='trend',
         detect=cyber_cycle,
         rules="Ehlers' Cyber Cycle is a smoothed, detrended price wave (alpha 0.07); its trigger is the same wave one "
               "bar later. Between 10:00 and 14:30 the first upturn through the trigger while the wave is below zero "
               "leans long, the first downturn while above zero leans short. One signal per side per session; "
               "tested with and against."),
]
