"""Ehlers Super Smoother (10) slope turn with VWAP side agreement, 5-minute session bars.
Added 2026-10-14 by trend-moving-average-analyst via WebSearch/Ehlers "Cybernetic Analysis for Stocks and Futures"
(2004): the 2-pole Butterworth Super Smoother removes aliasing noise with little lag. The lab has Ehlers roofing,
decycler, instantaneous trendline and MAMA, but not the plain Super Smoother turn. Parameters fixed BEFORE any P&L was
seen: period 10, a1 = exp(-1.414*pi/10), b1 = 2*a1*cos(1.414*pi/10 rad), c2 = b1, c3 = -a1^2, c1 = 1 - c2 - c3,
SS = c1*(x + x[-1])/2 + c2*SS[-1] + c3*SS[-2], seeded with the first closes, restarted each session.
Long at the close of the first bar between 10:00 and 14:30 ET where SS turns up (SS > SS[-1] after SS[-1] <= SS[-2]) and
the close is above session VWAP (mirror short: turns down, close below VWAP). One per side per session.
"""
import math


def super_smoother_turn(s):
    b = s.bars
    a1 = math.exp(-1.414 * math.pi / 10)
    c2 = 2 * a1 * math.cos(1.414 * math.pi / 10)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    ss = []
    for i, x in enumerate(b):
        if i < 2:
            ss.append(x.c)
        else:
            ss.append(c1 * (x.c + b[i - 1].c) / 2 + c2 * ss[i - 1] + c3 * ss[i - 2])
    done = {1: False, -1: False}
    for i in range(12, len(b)):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if not done[1] and ss[i] > ss[i - 1] and ss[i - 1] <= ss[i - 2] and b[i].c > s.vwap[i]:
            done[1] = True; yield i, 1
        elif not done[-1] and ss[i] < ss[i - 1] and ss[i - 1] >= ss[i - 2] and b[i].c < s.vwap[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='super_smoother_turn', name='Ehlers Super Smoother (10) turn on the VWAP side', family='trend',
         detect=super_smoother_turn,
         rules="Ehlers' 2-pole Super Smoother (period 10) of 5-minute closes turns up while the bar closes above "
               "VWAP (mirror: turns down below VWAP), between 10:00 and 14:30. One signal per side per session; "
               "tested with and against."),
]
