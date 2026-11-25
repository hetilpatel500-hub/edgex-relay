"""Linear regression standard-error channel fade, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (LuxAlgo Standard-error Channel and Linear-regression
Channel library pages, Gilbert Raff's regression channel as summarised on TradingView and therighttrader.com: a
least-squares line with parallel bands at a multiple of the standard error; sources say a flat channel is the regime
where fading the outer band toward the midline makes sense, and give no intraday statistics). Untested adaptation.
Parameters fixed BEFORE any P&L was seen: 30-bar window of closes, bands at +/-2 standard errors of the fit, channel
counts as flat when the fitted drift across the window is under 2 standard errors. Long at the close of the first bar
between 10:30 and 14:30 ET that closes back inside the channel after the previous close was below the lower band
(mirror for short above the upper band). One signal per session.
"""
import math


def _fit(y):
    n = len(y)
    xm = (n - 1) / 2
    ym = sum(y) / n
    sxx = sum((i - xm) ** 2 for i in range(n))
    sl = sum((i - xm) * (v - ym) for i, v in enumerate(y)) / sxx
    ic = ym - sl * xm
    res = [v - (ic + sl * i) for i, v in enumerate(y)]
    se = math.sqrt(sum(r * r for r in res) / (n - 2))
    return sl, ic, se


def reg_channel_fade(s):
    b = s.bars
    c = [x.c for x in b]
    W = 30
    for i in range(W + 1, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        sl, ic, se = _fit(c[i - W:i])  # window ends at the previous bar
        if se <= 0 or abs(sl * (W - 1)) >= 2 * se:
            continue
        mid_prev = ic + sl * (W - 1)
        mid_now = ic + sl * W
        if c[i - 1] < mid_prev - 2 * se and c[i] >= mid_now - 2 * se:
            yield i, 1
            return
        if c[i - 1] > mid_prev + 2 * se and c[i] <= mid_now + 2 * se:
            yield i, -1
            return


SETUPS = [
    dict(id='reg_channel_fade', name='Flat regression channel band fade', family='trend',
         detect=reg_channel_fade,
         rules="Fit a straight line through the last 30 closes and draw bands 2 standard errors either side. When "
               "the channel is flat (drift across the window under 2 standard errors) and, between 10:30 and 14:30, "
               "price closes back inside after the prior close was outside a band, it leans back toward the middle: "
               "long from below, short from above. One signal per session; tested with and against."),
]
