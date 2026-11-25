"""Bill Williams fractal break with the Alligator awake and aligned.
Added 2026-10-05 by trend-moving-average-analyst. Source: Bill Williams, "Trading Chaos" (fractals + Alligator),
a documented technique the lab had not tested (no fractal or Alligator file
exists). Rules were fixed BEFORE any P&L was seen: 5-bar fractals, Alligator = SMMA 13/8/5 of the median price
(the display shifts of 8/5/3 bars are not used, so nothing looks ahead), up to two signals per side per session.
"""


def _smma(vals, n):
    out = [None] * len(vals)
    if len(vals) < n:
        return out
    prev = sum(vals[:n]) / n
    out[n - 1] = prev
    for i in range(n, len(vals)):
        prev = (prev * (n - 1) + vals[i]) / n
        out[i] = prev
    return out


def fractal_alligator(s):
    """A fractal high is a bar whose high is above the two bars on each side (confirmed two bars later); a
    fractal low is the mirror. A close above the latest confirmed fractal high, while the Alligator lines are
    fanned up (lips > teeth > jaw) and the close is above VWAP, leans long; a close below the latest confirmed
    fractal low with lips < teeth < jaw and the close below VWAP leans short. A fractal is used once.
    10:30 to 14:30 ET, at most two signals per side per session."""
    b = s.bars
    n = len(b)
    if n < 20:
        return
    med = [(x.h + x.l) / 2 for x in b]
    jaw, teeth, lips = _smma(med, 13), _smma(med, 8), _smma(med, 5)
    fh = fl = None
    used_h = used_l = None
    cnt = {1: 0, -1: 0}
    for i in range(n):
        k = i - 2
        if k >= 2:
            if b[k].h > max(b[k - 1].h, b[k - 2].h, b[k + 1].h, b[k + 2].h):
                fh = (k, b[k].h)
            if b[k].l < min(b[k - 1].l, b[k - 2].l, b[k + 1].l, b[k + 2].l):
                fl = (k, b[k].l)
        if b[i].m < 630 or b[i].m >= 870 or jaw[i] is None:
            continue
        if fh and fh[0] != used_h and b[i].c > fh[1] and lips[i] > teeth[i] > jaw[i] \
                and b[i].c > s.vwap[i] and cnt[1] < 2:
            used_h = fh[0]; cnt[1] += 1
            yield i, 1
        elif fl and fl[0] != used_l and b[i].c < fl[1] and lips[i] < teeth[i] < jaw[i] \
                and b[i].c < s.vwap[i] and cnt[-1] < 2:
            used_l = fl[0]; cnt[-1] += 1
            yield i, -1


SETUPS = [
    dict(id='williams_fractal_alligator', name='Williams fractal break with Alligator aligned', family='trend',
         detect=fractal_alligator,
         rules="Bill Williams 5-bar fractal highs/lows on 5-minute bars. A close above the latest confirmed "
               "fractal high with the Alligator (SMMA 13/8/5 of median price) fanned up and the close above "
               "VWAP leans long; the mirror below a fractal low leans short. 10:30 to 14:30 ET, each fractal "
               "used once, at most two signals per side per session.")
]
