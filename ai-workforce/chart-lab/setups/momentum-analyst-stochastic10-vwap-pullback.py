"""Stochastic(10,1,3) pullback cross with VWAP side agreement, 5-minute session bars.
Added 2026-10-12 by momentum-analyst via WebSearch: John Kepka's TASC V.3:1 "Day Trading With Stochastics"
(store.traders.com/-v03-c01-day-pdf.html) used a 10-period stochastic on 5-minute bars because the textbook 5-period
setting is too whippy; the published patterns carry no backtest. The 14/3/3 cross out of 20/80 was already tested, so this
variant is different: raw %K (10 bars) crossing its 3-bar average %D from the pullback zone while price sits on the
trend side of VWAP. Parameters fixed before any P&L was seen.
Long at the close of the first bar between 10:00 and 14:30 ET where %K crosses above %D, both were below 30 on the prior
bar, and the close is above VWAP (mirror short: crosses below, both above 70, close below VWAP). One per side per session.
"""


def stoch10_vwap_pullback(s):
    b = s.bars
    k = [None] * len(b)
    for i in range(9, len(b)):
        hh = max(x.h for x in b[i - 9:i + 1])
        ll = min(x.l for x in b[i - 9:i + 1])
        k[i] = 50.0 if hh == ll else 100 * (b[i].c - ll) / (hh - ll)
    d = [None] * len(b)
    for i in range(11, len(b)):
        d[i] = sum(k[i - 2:i + 1]) / 3
    done = {1: False, -1: False}
    for i in range(12, len(b)):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if k[i - 1] is None or d[i - 1] is None:
            continue
        if not done[1] and k[i - 1] <= d[i - 1] and k[i] > d[i] and max(k[i - 1], d[i - 1]) < 30 and b[i].c > s.vwap[i]:
            done[1] = True; yield i, 1
        elif not done[-1] and k[i - 1] >= d[i - 1] and k[i] < d[i] and min(k[i - 1], d[i - 1]) > 70 and b[i].c < s.vwap[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='stoch10_vwap_pullback', name='Stochastic(10) pullback cross on the VWAP side', family='momentum',
         detect=stoch10_vwap_pullback,
         rules="Raw 10-bar stochastic %K crosses its 3-bar average %D upward after both sat below 30, while the "
               "bar closes above VWAP (mirror: crosses down from above 70 below VWAP), between 10:00 and 14:30. "
               "Tested with and against; one signal per side per session."),
]
