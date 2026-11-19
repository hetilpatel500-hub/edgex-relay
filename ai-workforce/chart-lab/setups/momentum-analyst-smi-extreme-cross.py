"""Stochastic Momentum Index (Blau 10,3,3) signal cross out of the +/-40 zones, 5-minute session bars.
Added 2026-10-11 by momentum-analyst via WebSearch (luxalgo.com SMI library, tc2000 help, ta-lib.org SMI: Blau 1993;
close vs range midpoint, double EMA smoothing, +/-40 overbought/oversold, signal = EMA3). Intraday use is an untested
adaptation; parameters fixed before any P&L was seen. rel = close - (HH10+LL10)/2, rng = HH10-LL10 (over the session's own
bars only); SMI = 100 * EMA3(EMA3(rel)) / (0.5 * EMA3(EMA3(rng))); signal = EMA3(SMI).
Long at the close of the first bar between 10:30 and 14:30 ET where SMI crosses above its signal while SMI < -40
(mirror short: cross below while SMI > +40). One signal per session.
"""


def smi_extreme_cross(s):
    b = s.bars
    k = 2 / 4
    e1r = e2r = e1g = e2g = sig = None
    prev = None
    for i, x in enumerate(b):
        if i < 9:
            continue
        w = b[i - 9:i + 1]
        hh = max(y.h for y in w)
        ll = min(y.l for y in w)
        rel, rng = x.c - (hh + ll) / 2, hh - ll
        if e1r is None:
            e1r, e2r, e1g, e2g = rel, rel, rng, rng
        else:
            e1r += k * (rel - e1r)
            e2r += k * (e1r - e2r)
            e1g += k * (rng - e1g)
            e2g += k * (e1g - e2g)
        smi = 100 * e2r / (0.5 * e2g) if e2g else 0.0
        osig = sig
        sig = smi if sig is None else sig + k * (smi - sig)
        pv, prev = prev, (smi, osig)
        if pv is None or osig is None or i < 20 or x.m < 630 or x.m > 870 or i + 1 >= len(b):
            continue
        if pv[0] <= pv[1] and smi > sig and smi < -40:
            yield i, 1
            return
        if pv[0] >= pv[1] and smi < sig and smi > 40:
            yield i, -1
            return


SETUPS = [
    dict(id='smi_extreme_cross', name='Stochastic Momentum Index cross out of +/-40', family='momentum',
         detect=smi_extreme_cross,
         rules="Blau's Stochastic Momentum Index (10,3,3) measures where price closes relative to the middle of its "
               "recent 10-bar range. Between 10:30 and 14:30, when it crosses above its 3-bar signal line while "
               "still below -40 (oversold) it leans long; crossing below the signal while above +40 (overbought) "
               "leans short. One signal per session; tested with and against."),
]
