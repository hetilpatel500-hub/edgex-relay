"""Ichimoku Kijun-sen (26) pullback bounce in a trend, with VWAP agreement, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ichimoku write-ups treat the Kijun as the pullback
support/resistance in a trend; sources give no 5-minute backtest numbers, so thresholds are this lab's fixed reading).
Parameters fixed BEFORE any P&L was seen: Kijun = midpoint of the last 26 bars' high/low inside the session, Tenkan = 9.
Long at the close of bar i (bar 27 to 15:00 ET) when Tenkan > Kijun, Kijun is higher than 6 bars ago, the bar's low
reached within 0.1 ATR of the Kijun (or below it), the bar closes above the Kijun, closes above its open, and closes
above session VWAP. Mirror for short. At most one signal per side per session.
"""


def kijun_bounce(s):
    b = s.bars

    def mid(i, n):
        return (max(x.h for x in b[i - n + 1:i + 1]) + min(x.l for x in b[i - n + 1:i + 1])) / 2

    cnt = {1: 0, -1: 0}
    for i in range(32, len(b) - 1):
        if b[i].m >= 900:
            return
        k, t, k6 = mid(i, 26), mid(i, 9), mid(i - 6, 26)
        tol = 0.1 * s.atr[i]
        x = b[i]
        if t > k and k > k6 and x.l <= k + tol and x.c > k and x.c > x.o and x.c > s.vwap[i] and cnt[1] < 1:
            cnt[1] += 1
            yield i, 1
        elif t < k and k < k6 and x.h >= k - tol and x.c < k and x.c < x.o and x.c < s.vwap[i] and cnt[-1] < 1:
            cnt[-1] += 1
            yield i, -1


SETUPS = [
    dict(id='kijun_bounce', name='Ichimoku Kijun pullback bounce with VWAP', family='trend', detect=kijun_bounce,
         rules="In an uptrend (Tenkan above Kijun, Kijun higher than 6 bars ago) a 5-minute bar dips to within 0.1 ATR "
               "of the 26-bar Kijun midpoint, closes back above it on an up bar and above VWAP: leans long (mirror "
               "for short). From bar 33 to 15:00 ET, one signal per side per session; tested with and against."),
]
