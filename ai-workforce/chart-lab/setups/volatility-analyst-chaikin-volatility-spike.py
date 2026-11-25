"""Chaikin Volatility spike at a stretched VWAP side, 5-minute session bars.
Added 2026-10-14 by volatility-analyst via WebSearch (Chaikin's own reading, as summarised by TA-Lib, Barchart and
IncredibleCharts: a fast rise in Chaikin Volatility marks panic and a nearby bottom; it measures range, not direction,
so Chaikin pairs it with a band system). The lab has ATR expansion, wide-range bars and BB squeezes but not this
EMA-of-range rate-of-change. Parameters fixed BEFORE any P&L was seen: CV = 100 * (EMA10(high-low) - EMA10 ten bars
earlier) / EMA10 ten bars earlier, restarted each session (first value at bar 19). Trigger: CV crosses up through +40
(prior bar <= 40). Long if that bar is a down bar closing below VWAP minus 1 VWAP stdev (panic low); short if it is an
up bar closing above VWAP plus 1 stdev (blow-off high). 10:00 to 14:30 ET, one per side per session.
"""


def chaikin_volatility_spike(s):
    b = s.bars
    n = len(b)
    if n < 21:
        return
    k = 2 / 11
    ema = []
    for x in b:
        r = x.h - x.l
        ema.append(r if not ema else ema[-1] + k * (r - ema[-1]))
    cv = [None] * n
    for i in range(19, n):
        if ema[i - 10] > 0:
            cv[i] = 100 * (ema[i] - ema[i - 10]) / ema[i - 10]
    done = {1: False, -1: False}
    for i in range(20, n):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if cv[i] is None or cv[i - 1] is None or not (cv[i - 1] <= 40 < cv[i]):
            continue
        sd = s.vsd[i]
        if sd <= 0:
            continue
        if not done[1] and b[i].c < b[i].o and b[i].c < s.vwap[i] - sd:
            done[1] = True; yield i, 1
        elif not done[-1] and b[i].c > b[i].o and b[i].c > s.vwap[i] + sd:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='chaikin_volatility_spike', name='Chaikin Volatility spike beyond 1 VWAP stdev', family='volatility',
         detect=chaikin_volatility_spike,
         rules="Chaikin Volatility (10-bar EMA of the bar range, rate of change over 10 bars) crossing up through +40 "
               "on a bar that closes more than one VWAP standard deviation from VWAP in the direction of the bar. "
               "Chaikin's reading is a panic low or blow-off high, so the setup leans long after a down spike and "
               "short after an up spike, 10:00 to 14:30 ET, one per side per session. Tested with and against."),
]
