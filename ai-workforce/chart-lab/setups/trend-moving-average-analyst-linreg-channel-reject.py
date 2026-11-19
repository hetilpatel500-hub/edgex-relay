"""Linear-regression channel edge rejection (Raff channel style).
Added 2026-10-02 by trend-moving-average-analyst: the research queue's open lines were already covered, so this run
took the regression channel, which the lab had not tested.
Rules fixed BEFORE any P&L was seen: 24-bar least-squares line of closes inside the session, band = +/-2 standard
deviations of the residuals, 10:30-14:30, one signal per side per session.
"""
import math


def linreg_reject(s):
    b = s.bars
    n = 24
    up_done = dn_done = False
    xs = list(range(n))
    xm = (n - 1) / 2
    sxx = sum((x - xm) ** 2 for x in xs)
    for i in range(n - 1, len(b)):
        if b[i].m >= 870:
            return
        if b[i].m < 630:
            continue
        ys = [b[k].c for k in range(i - n + 1, i + 1)]
        ym = sum(ys) / n
        slope = sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / sxx
        res = [y - (ym + slope * (x - xm)) for x, y in zip(xs, ys)]
        sd = math.sqrt(sum(r * r for r in res) / n)
        if sd <= 0:
            continue
        fit = ym + slope * (n - 1 - xm)
        hi, lo = fit + 2 * sd, fit - 2 * sd
        if not dn_done and b[i].h > hi and b[i].c < hi:
            dn_done = True; yield i, -1
        elif not up_done and b[i].l < lo and b[i].c > lo:
            up_done = True; yield i, 1


SETUPS = [
    dict(id='linreg_channel_reject', name='Regression channel edge rejection', family='trend',
         detect=linreg_reject,
         rules="Fit a straight line through the last 24 five-minute closes and draw bands 2 standard deviations of the "
               "residuals above and below. A bar that pokes above the upper band but closes back inside it leans "
               "short; one that pokes below the lower band and closes back inside leans long. 10:30-14:30, one per "
               "side per session. Tested with and against, like every setup."),
]
