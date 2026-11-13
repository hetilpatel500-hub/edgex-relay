"""Daily-trend-aligned VWAP pullback on 5-minute bars.
Added 2026-10-03 by trend-moving-average-analyst: the research queue had no open
non-tape lines, so this tests a cross-timeframe filter the lab had not tried
as a detector: only take the intraday pullback to VWAP when the daily trend
(from the chained prior-session closes) points the same way. Distinct from
vwap_bounce (needs only an intraday trend) and ema9_20_pullback.
"""


def _daily_trend(s, n=5):
    """+1 / -1 / 0 from prior-session closes: last close vs the mean of the last
    n closes, and that mean vs the mean of the n closes before it. 0 when fewer
    than 2n chained sessions exist."""
    closes, p = [], s.prior
    while p is not None and len(closes) < 2 * n:
        closes.append(p.close)
        p = p.prior
    if len(closes) < 2 * n:
        return 0
    m1, m2 = sum(closes[:n]) / n, sum(closes[n:]) / n
    if closes[0] > m1 > m2:
        return 1
    if closes[0] < m1 < m2:
        return -1
    return 0


def daily_trend_vwap_pullback(s):
    """With the daily trend up (down): earlier today price stood at least 0.5 ATR
    above (below) VWAP; a bar then wicks to VWAP (within 0.1 ATR) and closes back
    on the trend side of VWAP in the trend direction. One signal per session,
    10:00 to 14:30."""
    d = _daily_trend(s)
    if d == 0:
        return
    b = s.bars
    stretched = False
    for i in range(6, len(b)):
        if b[i].m >= 870:
            break
        atr, v = s.atr[i], s.vwap[i]
        if not atr:
            continue
        x = b[i]
        if d * (x.c - v) >= 0.5 * atr:
            stretched = True
        if not stretched or x.m < 600:
            continue
        if d == 1 and x.l <= v + 0.1 * atr and x.c > v and x.c > x.o:
            yield i, 1
            return
        if d == -1 and x.h >= v - 0.1 * atr and x.c < v and x.c < x.o:
            yield i, -1
            return


SETUPS = [
    dict(id='daily_trend_vwap_pullback', name='Daily-trend-aligned VWAP pullback', family='trend',
         detect=daily_trend_vwap_pullback,
         rules="When the prior daily closes trend one way (last close beyond its 5-day average, itself beyond the "
               "average of the 5 days before), wait for price to stretch at least 0.5 ATR from VWAP on that side, "
               "then lean with the trend on the first bar that wicks to VWAP and closes back on the trend side in "
               "the trend direction. One signal per session, 10:00 to 14:30."),
]
