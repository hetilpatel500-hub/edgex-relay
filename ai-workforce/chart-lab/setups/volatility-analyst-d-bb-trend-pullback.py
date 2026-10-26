"""Daily close outside the 20-day Bollinger band against the 200-day trend.
Added 2026-10-06 by volatility-analyst via the queue's volatility family (Bollinger band-touch reversion,
distinct from the intraday bb_failed_break / bb_squeeze_expansion and from d_rsi2_pullback, which reads RSI).
Parameters fixed BEFORE any P&L was seen: Bollinger(20 days, 2 population standard deviations) on closes;
200-day SMA as the trend filter; signal at the daily close, one per day.
"""
import math


def bb_trend_pullback(ser):
    c = ser.c
    for i in range(200, len(c)):
        m200 = ser.sma200[i]
        if m200 is None:
            continue
        w = c[i - 19:i + 1]
        mu = sum(w) / 20
        sd = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
        if sd <= 0:
            continue
        if c[i] > m200 and c[i] < mu - 2 * sd:
            yield i, 1
        elif c[i] < m200 and c[i] > mu + 2 * sd:
            yield i, -1


SETUPS = [
    dict(id='d_bb_trend_pullback', tf='D', name='Daily Bollinger band tag against the 200-day trend',
         family='mean reversion (daily)', detect=bb_trend_pullback,
         rules="In an uptrend (close above the 200-day average) a daily close below the lower Bollinger band "
               "(20 days, 2 standard deviations) leans long for a snap back; in a downtrend a close above the "
               "upper band leans short. Tested with and against."),
]
