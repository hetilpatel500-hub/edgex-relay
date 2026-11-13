"""Stochastic RSI %K/%D cross inside an extreme zone, with the session VWAP side as the trend filter.
Added 2026-10-11 by momentum-analyst via WebSearch (queue was fully coded): StockSharp's Stochastic RSI Cross
(RSI 14, Stoch 14, %K 3, %D 3 on 5-minute candles, %K crossing %D below 20) and LuxAlgo's note that StochRSI is
noisy alone and wants a trend filter. Neither source reports a verified backtest. Parameters fixed BEFORE any P&L
was seen: RSI(14, Wilder) of closes carried within the session, StochRSI over 14 RSI values, %K = SMA3, %D = SMA3 of
%K, zones 20/80; trend filter = close on the same side of session VWAP as the trade; 10:15-14:30 ET; one per session.
"""


def stochrsi_trend_cross(s):
    b = s.bars
    n = len(b)
    if n < 40:
        return
    rsi = [None] * n
    ag = al = 0.0
    for i in range(1, n):
        ch = b[i].c - b[i - 1].c
        g, l = max(ch, 0), max(-ch, 0)
        if i <= 14:
            ag += g / 14; al += l / 14
            if i < 14:
                continue
        else:
            ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14
        rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    st = [None] * n
    for i in range(27, n):
        w = rsi[i - 13:i + 1]
        if None in w:
            continue
        lo, hi = min(w), max(w)
        st[i] = 50.0 if hi == lo else 100 * (rsi[i] - lo) / (hi - lo)
    k = [None] * n
    for i in range(29, n):
        w = st[i - 2:i + 1]
        if None not in w:
            k[i] = sum(w) / 3
    d = [None] * n
    for i in range(31, n):
        w = k[i - 2:i + 1]
        if None not in w:
            d[i] = sum(w) / 3
    for i in range(32, n - 1):
        x = b[i]
        if x.m < 615 or x.m > 870 or d[i] is None or d[i - 1] is None:
            continue
        if k[i - 1] <= d[i - 1] and k[i] > d[i] and k[i] < 20 and x.c > s.vwap[i]:
            yield i, 1
            return
        if k[i - 1] >= d[i - 1] and k[i] < d[i] and k[i] > 80 and x.c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='stochrsi_trend_cross', name='Stochastic RSI cross in the extreme zone, with VWAP side', family='momentum',
         detect=stochrsi_trend_cross,
         rules="Stochastic RSI (RSI 14, Stochastic 14, %K 3, %D 3) on 5-minute bars, restarted each session. Between "
               "10:15 and 14:30 ET, %K crossing up through %D while %K is still below 20 and the bar closes above "
               "session VWAP: long. %K crossing down through %D above 80 with the close below VWAP: short. One "
               "signal per session; tested with and against."),
]
