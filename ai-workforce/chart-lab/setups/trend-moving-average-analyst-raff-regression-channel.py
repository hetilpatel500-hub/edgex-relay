"""Raff regression channel: lower/upper band touch inside a high-R2 trend, 5-minute bars.
Added 2026-10-15 by trend-moving-average-analyst via WebSearch (Gilbert Raff's regression channel: a least-squares line
through recent closes with bands set by the widest deviation; trend-quality is judged by R-squared). The lab already
has a flat regression-channel band fade; this is the trending counterpart. Rules fixed BEFORE any P&L was seen:
OLS line through the last 24 closes (bars i-23..i); R-squared >= 0.80 and the fitted move across the window at least
1.5 ATR. Bands sit 1.5 residual standard deviations from the line. In an up-trend, a bar whose low reaches the lower
band and closes back above it signals long; in a down-trend, a bar whose high reaches the upper band and closes back
below it signals short. 10:30 to 15:00 ET, at most one signal per side per 12 bars.
"""
import math

W = 24


def _fit(c):
    n = len(c)
    xm = (n - 1) / 2
    ym = sum(c) / n
    sxx = sum((k - xm) ** 2 for k in range(n))
    sxy = sum((k - xm) * (c[k] - ym) for k in range(n))
    slope = sxy / sxx
    icpt = ym - slope * xm
    sst = sum((v - ym) ** 2 for v in c)
    sse = sum((c[k] - (icpt + slope * k)) ** 2 for k in range(n))
    r2 = 1 - sse / sst if sst > 0 else 0
    return slope, icpt, r2, math.sqrt(sse / n)


def raff_touch(s):
    b = s.bars
    closes = [x.c for x in b]
    last = {1: -99, -1: -99}
    for i in range(W - 1, len(b)):
        x = b[i]
        if x.m < 630 or x.m + 5 > 900:
            continue
        slope, icpt, r2, sd = _fit(closes[i - W + 1:i + 1])
        if r2 < 0.80 or abs(slope) * (W - 1) < 1.5 * s.atr[i] or sd <= 0:
            continue
        line_now = icpt + slope * (W - 1)
        if slope > 0 and last[1] + 12 <= i and x.l <= line_now - 1.5 * sd and x.c > line_now - 1.5 * sd:
            last[1] = i
            yield i, 1
        elif slope < 0 and last[-1] + 12 <= i and x.h >= line_now + 1.5 * sd and x.c < line_now + 1.5 * sd:
            last[-1] = i
            yield i, -1


SETUPS = [
    dict(id='raff_regression_touch', name='Raff regression channel band touch in a high-R2 trend', family='trend',
         detect=raff_touch,
         rules="Least-squares line through the last 24 five-minute closes with R-squared of at least 0.80 and a fitted "
               "move of at least 1.5 ATR. Bands are 1.5 residual standard deviations from the line. In an up-trend a "
               "bar that reaches the lower band and closes back above it leans long; in a down-trend a bar that "
               "reaches the upper band and closes back below leans short. 10:30 to 14:55 ET, one signal per side per "
               "12 bars; tested with and against."),
]
