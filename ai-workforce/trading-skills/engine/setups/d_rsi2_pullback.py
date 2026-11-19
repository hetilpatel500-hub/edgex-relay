"""RSI(2) pullback in a trend (daily bars).

Larry Connors' classic: above the 200-day average with RSI(2) under 10
leans long (a short, sharp pullback in an uptrend); below the 200-day
average with RSI(2) over 90 leans short. Known at the daily close; the
simulated entry is the next day's open.

Snapshot from the Edgex chart lab (12 US symbols, daily bars 2021-12-14 to
2026-10-22, OOS from 2025-05-09): validated WITH the lean, no filter, 2 ATR
stop held up to 10 days: 397 OOS trades, 54% win, +0.15R avg, PF 1.41,
t 2.78. Its forward test since freezing is FADING (23 trades, -0.53R avg,
hurt by the Oct 22 2026 selloff). Re-test on your own data first.
"""


def rsi2_pullback(ser):
    for i in range(200, len(ser.c)):
        m, r = ser.sma200[i], ser.rsi2[i]
        if m is None or r is None:
            continue
        if ser.c[i] > m and r < 10:
            yield i, 1
        elif ser.c[i] < m and r > 90:
            yield i, -1


SETUPS = [
    dict(id='d_rsi2_pullback', tf='D', name='RSI(2) pullback in trend', family='mean reversion (daily)',
         detect=rsi2_pullback,
         rules='Above the 200-day average with RSI(2) under 10 (or below it with RSI(2) over 90).'),
]
