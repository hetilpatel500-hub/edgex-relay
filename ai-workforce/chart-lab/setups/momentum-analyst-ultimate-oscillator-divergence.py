"""Williams Ultimate Oscillator divergence with breakout of the interim high, 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (Wikipedia, AmiBroker and Incredible Charts pages on Larry Williams'
rules: UO = 100 * (4*A7 + 2*A14 + A28) / 7 with A_n = sum(buying pressure)/sum(true range); buy on a bullish divergence
(price lower low, oscillator higher low) whose first low dipped below 30, triggered when the oscillator rises above the
highest value it reached between the two lows; mirror for sells with 70). Those sources describe daily charts, so
this is an untested intraday adaptation. Parameters fixed BEFORE any P&L was seen: 7/14/28 bars, swing lows/highs of
2 bars each side, the two swings 6 to 30 bars apart, signal between 10:30 and 14:30 ET, first signal per side per session.
"""


def _uo(b):
    bp, tr = [0.0], [0.0]
    for i in range(1, len(b)):
        lo = min(b[i].l, b[i - 1].c)
        hi = max(b[i].h, b[i - 1].c)
        bp.append(b[i].c - lo)
        tr.append(hi - lo)
    out = [None] * len(b)
    for i in range(28, len(b)):
        def a(n):
            t = sum(tr[i - n + 1:i + 1])
            return sum(bp[i - n + 1:i + 1]) / t if t else 0.5
        out[i] = 100 * (4 * a(7) + 2 * a(14) + a(28)) / 7
    return out


def uo_divergence(s):
    b = s.bars
    u = _uo(b)
    done = {1: False, -1: False}
    lows, highs = [], []
    for i in range(30, len(b) - 1):
        j = i - 2  # swing confirmed two bars later
        if j >= 30:
            if all(b[j].l < b[j + k].l and b[j].l < b[j - k].l for k in (1, 2)):
                lows.append(j)
            if all(b[j].h > b[j + k].h and b[j].h > b[j - k].h for k in (1, 2)):
                highs.append(j)
        if b[i].m < 630 or b[i].m > 870:
            continue
        for d, sw in ((1, lows), (-1, highs)):
            if done[d] or len(sw) < 2:
                continue
            p2, p1 = sw[-1], sw[-2]
            if not 6 <= p2 - p1 <= 30 or i - p2 > 8:
                continue
            if d == 1:
                ok = b[p2].l < b[p1].l and u[p2] > u[p1] and u[p1] < 30
                mid = max(u[p1:p2 + 1])
                trig = u[i] > mid and u[i - 1] <= mid
            else:
                ok = b[p2].h > b[p1].h and u[p2] < u[p1] and u[p1] > 70
                mid = min(u[p1:p2 + 1])
                trig = u[i] < mid and u[i - 1] >= mid
            if ok and trig:
                done[d] = True
                yield i, d


SETUPS = [
    dict(id='uo_divergence', name='Ultimate Oscillator divergence breakout', family='momentum',
         detect=uo_divergence,
         rules="Larry Williams' Ultimate Oscillator blends 7, 14 and 28-bar buying pressure. A bullish signal needs "
               "price to make a lower low while the oscillator makes a higher low, the first low having been below 30; "
               "it triggers when the oscillator rises back above its highest reading between the two lows (mirror "
               "above 70 for bearish). Signals between 10:30 and 14:30, within 8 bars of the second swing, one per "
               "side per session; tested with and against."),
]
