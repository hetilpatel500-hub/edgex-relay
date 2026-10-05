"""Morning / evening star at a stretched VWAP band.
Added 2026-10-05 by candlestick-specialist: candlestick family, a new idea (single-candle and engulfing
patterns at levels are covered; the three-candle star is not). Sources: standard morning/evening star
definition (StockCharts ChartSchool, Investopedia) combined with the VWAP 1-sigma band already in core.
Parameters fixed BEFORE any P&L was seen: bar i-2 has a body of at least 0.8 ATR in the trend direction;
bar i-1 has a body of at most 0.3 of bar i-2's body and its range touches beyond VWAP +/- 1 sigma on the
stretched side; bar i closes past the midpoint of bar i-2's body in the opposite direction. 10:00 to 15:00
ET, first star per session. The lab tests it with and against.
"""


def star_at_vwap_band(s):
    b = s.bars
    for i in range(14, len(b) - 1):
        if b[i].m < 600 or b[i].m >= 900:
            continue
        a = s.atr[i]
        if not a:
            continue
        x, y, z = b[i - 2], b[i - 1], b[i]
        body = abs(x.c - x.o)
        if body < 0.8 * a or abs(y.c - y.o) > 0.3 * body:
            continue
        sd = s.vsd[i - 1]
        v = s.vwap[i - 1]
        mid = (x.o + x.c) / 2
        if x.c > x.o and y.h >= v + sd and z.c < z.o and z.c < mid:
            yield i, -1
            return
        if x.c < x.o and y.l <= v - sd and z.c > z.o and z.c > mid:
            yield i, 1
            return


SETUPS = [
    dict(id='star_at_vwap_band', name='Morning / evening star at the VWAP 1-sigma band',
         family='candlestick', detect=star_at_vwap_band,
         rules="A big candle (0.8 ATR body), a small-bodied candle (under 30% of it) that reaches the VWAP +/- 1 "
               "sigma band on the stretched side, then a candle closing back past the first candle's midpoint is a "
               "three-candle star reversal. 10:00 to 15:00 ET, first one a session."),
]
