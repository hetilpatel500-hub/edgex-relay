"""Bernstein Stochastic Pop (80/20 continuation), slow stochastic (14,3,3) on 5-minute session bars.
Added 2026-10-14 by momentum-analyst via WebSearch (LuxAlgo "Stochastic Pop" library page; TradingView CM Stochastic Pop
descriptions of Jake Bernstein's method): a stochastic surge ABOVE 80 is read as momentum ignition and continuation, not as
overbought. The sources publish no verified backtest. The lab already tests stochastic crosses OUT of 20/80 (fade) and the
stochastic(10) pullback cross; the pop is the opposite reading of the same zone. The 55/50/45 variant was not used (sources
disagree and the PDF was not available).
Parameters fixed BEFORE any P&L was seen: raw %K over 14 bars, smoothed 3, then %K-slow smoothed 3 (standard slow stochastic);
no tuning.
Long at the close of the first bar between 10:00 and 14:30 ET where slow %K crosses from <= 80 to > 80 and the close is above
VWAP (mirror short: crosses from >= 20 to < 20, close below VWAP). One per side per session.
"""


def stochastic_pop(s):
    b = s.bars
    n = len(b)
    raw = [None] * n
    for i in range(13, n):
        hh = max(x.h for x in b[i - 13:i + 1])
        ll = min(x.l for x in b[i - 13:i + 1])
        raw[i] = 50.0 if hh == ll else 100 * (b[i].c - ll) / (hh - ll)
    k = [None] * n
    for i in range(15, n):
        k[i] = sum(raw[i - 2:i + 1]) / 3
    d = [None] * n
    for i in range(17, n):
        d[i] = sum(k[i - 2:i + 1]) / 3
    done = {1: False, -1: False}
    for i in range(18, n):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if d[i] is None or d[i - 1] is None:
            continue
        if not done[1] and d[i - 1] <= 80 < d[i] and b[i].c > s.vwap[i]:
            done[1] = True; yield i, 1
        elif not done[-1] and d[i - 1] >= 20 > d[i] and b[i].c < s.vwap[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='stochastic_pop', name='Stochastic Pop (14,3,3) through 80 / 20 with VWAP side', family='momentum',
         detect=stochastic_pop,
         rules="Slow stochastic (14,3,3) %D line crosses up through 80 while the bar closes above VWAP (mirror: crosses "
               "down through 20 below VWAP) between 10:00 and 14:30. Read as momentum continuation, not overbought. "
               "Tested with and against; one signal per side per session."),
]
