"""Ehlers Instantaneous Trendline trigger cross, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (LuxAlgo library and TradingView scripts crediting Ehlers,
Rocket Science for Traders: trendline plus a lag-reduced trigger, crossings are the entry events, alpha 0.07). Parameters
fixed BEFORE any P&L was seen: alpha 0.07, price = (high+low)/2, built inside the session (first three bars seeded with
the book's (P + 2*P1 + P2)/4). Long at the close of the first bar between 10:30 and 14:30 ET where the trigger
(2*IT - IT two bars earlier) crosses from at or below the trendline to above it; mirror for short. One signal per session.
"""

ALPHA = 0.07


def itrend_cross(s):
    b = s.bars
    p = [(x.h + x.l) / 2 for x in b]
    a = ALPHA
    it = []
    for i in range(len(b)):
        if i < 3:
            it.append((p[i] + 2 * p[i - 1] + p[i - 2]) / 4 if i >= 2 else p[i])
            continue
        it.append((a - a * a / 4) * p[i] + 0.5 * a * a * p[i - 1] - (a - 0.75 * a * a) * p[i - 2]
                  + 2 * (1 - a) * it[i - 1] - (1 - a) ** 2 * it[i - 2])
    trig = [None, None] + [2 * it[i] - it[i - 2] for i in range(2, len(b))]
    for i in range(10, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        if trig[i - 1] is None:
            continue
        if trig[i - 1] <= it[i - 1] and trig[i] > it[i]:
            yield i, 1
            return
        if trig[i - 1] >= it[i - 1] and trig[i] < it[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='ehlers_itrend_cross', name='Ehlers Instantaneous Trendline trigger cross', family='trend',
         detect=itrend_cross,
         rules="Ehlers' Instantaneous Trendline is a very low-lag smoothing of the bar midpoint (alpha 0.07), with a "
               "trigger line that leads it. Between 10:30 and 14:30, when the trigger crosses up through the "
               "trendline it leans long; crossing down leans short. One signal per session; tested with and against."),
]
