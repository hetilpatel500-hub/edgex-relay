"""Bollinger band touch confirmed by normalized Intraday Intensity (II%21), 5-minute bars.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (luxalgo.com Intraday Intensity page, StockSharp Intraday
Intensity Index page: David Bostian's volume-pressure gauge popularized by John Bollinger; CLV = (2C-H-L)/(H-L) x
volume, normalized II%21 = 100 x sum21(CLV x V) / sum21(V); vendor rule: a lower-band tag with positive intensity
flags a reversion candidate, an upper-band tag with negative intensity the mirror). Vendor rules only, no
backtests found. Distinct from clv_delta_divergence (no bands) and cmf_zero_cross_vwap (zero cross, no bands).
Rules fixed BEFORE any P&L was seen: Bollinger(20, 2) on 5-minute closes within the session (needs 21 bars);
at the close of the first bar between 10:30 and 15:00 ET whose close is at or below the lower band while II%21 > 0
go long; at or above the upper band while II%21 < 0 go short. One signal per session.
"""


def intensity_bb(s):
    b = s.bars
    n = len(b)
    clv = []
    for x in b:
        r = x.h - x.l
        clv.append((2 * x.c - x.h - x.l) / r if r > 0 else 0.0)
    for i in range(20, n - 1):
        x = b[i]
        if x.m < 630 or x.m > 900:
            continue
        w = [y.c for y in b[i - 19:i + 1]]
        mu = sum(w) / 20
        sd = (sum((c - mu) ** 2 for c in w) / 20) ** 0.5
        if sd <= 0:
            continue
        vs = sum(b[j].v for j in range(i - 20, i + 1))
        if vs <= 0:
            continue
        ii = 100 * sum(clv[j] * b[j].v for j in range(i - 20, i + 1)) / vs
        if x.c <= mu - 2 * sd and ii > 0:
            yield i, 1
            return
        if x.c >= mu + 2 * sd and ii < 0:
            yield i, -1
            return


SETUPS = [
    dict(id='intensity_bb', name='Bollinger tag confirmed by normalized Intraday Intensity', family='volume',
         detect=intensity_bb,
         rules="Intraday Intensity weighs each 5-minute bar's volume by where it closed in its range and sums the "
               "last 21 bars. Between 10:30 and 15:00, if price closes at or below the lower Bollinger band while "
               "that buying/selling pressure reading is still positive, it leans long (a reversion); at or above "
               "the upper band with a negative reading it leans short. One signal per session; tested with and "
               "against."),
]
