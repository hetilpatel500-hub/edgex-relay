"""Variance-ratio regime gate on a VWAP 1.5-sigma stretch, 5-minute session bars.
Added 2026-10-15 by volatility-analyst via WebSearch-free idea from Lo & MacKinlay (1988) variance-ratio test: VR(q) =
Var(q-bar return) / (q * Var(1-bar return)); below 1 means returns mean-revert at that horizon, above 1 means they
trend. The lab has a Hurst-gated Donchian (hurst_donchian) and a Kaufman-ER-gated VWAP 2-sigma fade, but no
variance-ratio gate.
Parameters fixed BEFORE any P&L was seen: VR(4) on the last 30 one-bar log returns of the session (overlapping 4-bar
sums, no bias correction), threshold 0.8, stretch = prior bar closed beyond VWAP +/- 1.5 session stdev, signal = first
bar closing back inside the band, 12:00 to 14:30 ET, one per side per session. No tuning of any number.
"""
import math


def _vr(c, i, n=30, q=4):
    if i < n:
        return None
    r = [math.log(c[k] / c[k - 1]) for k in range(i - n + 1, i + 1)]
    m = sum(r) / n
    v1 = sum((x - m) ** 2 for x in r) / (n - 1)
    if v1 <= 0:
        return None
    rq = [sum(r[k:k + q]) for k in range(n - q + 1)]
    mq = sum(rq) / len(rq)
    vq = sum((x - mq) ** 2 for x in rq) / (len(rq) - 1)
    return vq / (q * v1)


def vr_vwap_fade(s):
    b = s.bars
    c = [x.c for x in b]
    done = {1: False, -1: False}
    for i in range(31, len(b)):
        if b[i].m < 720 or b[i].m + 5 > 870:
            continue
        sd = s.vsd[i - 1]
        if not sd:
            continue
        vr = _vr(c, i)
        if vr is None or vr >= 0.8:
            continue
        up, dn = s.vwap[i - 1] + 1.5 * sd, s.vwap[i - 1] - 1.5 * sd
        if not done[-1] and b[i - 1].c > up and b[i].c <= s.vwap[i] + 1.5 * s.vsd[i]:
            done[-1] = True; yield i, -1
        elif not done[1] and b[i - 1].c < dn and b[i].c >= s.vwap[i] - 1.5 * s.vsd[i]:
            done[1] = True; yield i, 1


SETUPS = [
    dict(id='vr_vwap_fade', name='Mean-reverting tape (variance ratio < 0.8): VWAP 1.5-sigma stretch snaps back', family='volatility',
         detect=vr_vwap_fade,
         rules="Between 12:00 and 14:30, when the variance ratio of the last 30 five-minute returns at a 4-bar horizon "
               "is below 0.8 (price has been mean-reverting rather than trending), a bar that closed beyond VWAP +/- 1.5 "
               "standard deviations and is followed by a bar closing back inside the band leans back toward VWAP "
               "(stretched high: short). One signal per side per session; tested with and against."),
]
