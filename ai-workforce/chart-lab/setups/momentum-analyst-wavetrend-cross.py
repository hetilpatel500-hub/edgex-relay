"""WaveTrend oscillator (LazyBear) cross out of the +/-53 zone, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (LazyBear's TradingView WaveTrend, as documented by LuxAlgo and
ProRealCode). Parameters fixed BEFORE any P&L was seen, the published defaults: HLC3 price, channel 10, average 21,
signal = 4-bar SMA of WT1, zone +/-53. Long at the close of the first bar between 10:30 and 14:30 ET where WT1 crosses
above WT2 while WT1 is at or below -53 (mirror for short above +53). One signal per session.
"""


def _ema(x, n):
    k = 2 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def wavetrend_cross(s):
    b = s.bars
    if len(b) < 40:
        return
    ap = [(x.h + x.l + x.c) / 3 for x in b]
    esa = _ema(ap, 10)
    d = _ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    ci = [(a - e) / (0.015 * dd) if dd else 0.0 for a, e, dd in zip(ap, esa, d)]
    wt1 = _ema(ci, 21)
    wt2 = [None] * len(b)
    for i in range(3, len(b)):
        wt2[i] = sum(wt1[i - 3:i + 1]) / 4
    for i in range(30, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        if wt1[i - 1] <= wt2[i - 1] and wt1[i] > wt2[i] and wt1[i] <= -53:
            yield i, 1
            return
        if wt1[i - 1] >= wt2[i - 1] and wt1[i] < wt2[i] and wt1[i] >= 53:
            yield i, -1
            return


SETUPS = [
    dict(id='wavetrend_cross', name='WaveTrend cross out of the +/-53 zone', family='momentum',
         detect=wavetrend_cross,
         rules="WaveTrend (LazyBear) smooths a CCI-style reading of the typical price. Between 10:30 and 14:30, when "
               "the fast line crosses up through its 4-bar signal line while still at or below -53 (stretched down), "
               "it leans long; the mirror cross down from +53 or higher leans short. One signal per session; "
               "tested with and against."),
]
