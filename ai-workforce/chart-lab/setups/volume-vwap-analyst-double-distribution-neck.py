"""Double-distribution neck: two fat volume regions joined by a thin neck (Dalton, Mind Over Markets).
Added 2026-10-07 by volume-vwap-analyst. Lab tests it with and against.
Parameters fixed BEFORE any P&L was seen: first check at the 12:00 bar (bar 30), then every bar to 14:00;
profile of bars so far in 5 bp bins; peaks = the two highest bins at least 1.5 ATR apart; each peak must hold
at least 60% of the POC bin volume; the thinnest bin between them must hold under 35% of the smaller peak;
signal when the close is above (below) the neck zone by at least 0.25 ATR, direction = side of the neck
price is on; one per session.
"""
import statistics as st


def double_dist_neck(s):
    b = s.bars
    if len(b) < 31:
        return
    px = st.median(x.c for x in b)
    step = px * 5.0 / 1e4
    for i in range(30, min(len(b), 66)):
        vol = {}
        for x in b[:i + 1]:
            lo, hi = int(x.l // step), int(x.h // step)
            sh = x.v / (hi - lo + 1)
            for k in range(lo, hi + 1):
                vol[k] = vol.get(k, 0) + sh
        ks = sorted(vol)
        top = max(vol.values())
        a = s.atr[i]
        if not a:
            continue
        gap = max(1, int(1.5 * a / step))
        # local maxima (strictly above both neighbours, 3-bin smoothing)
        sm = {k: (vol.get(k - 1, 0) + vol[k] + vol.get(k + 1, 0)) / 3 for k in ks}
        peaks = [k for k in ks if sm[k] >= 0.6 * top and sm[k] >= sm.get(k - 1, 0) and sm[k] >= sm.get(k + 1, 0)]
        peaks.sort(key=lambda k: -sm[k])
        found = None
        for p in peaks:
            for q in peaks:
                if q > p and q - p >= gap:
                    found = (p, q); break
            if found: break
        if not found:
            continue
        p1, p2 = sorted(found)
        valley = min(sm.get(k, 0) for k in range(p1 + 1, p2))
        if valley >= 0.35 * min(sm[p1], sm[p2]):
            continue
        neck = (min(range(p1 + 1, p2), key=lambda k: sm.get(k, 0)) + 0.5) * step
        c = b[i].c
        if c > neck + 0.25 * a and c > (p1 + 0.5) * step:
            yield i, 1; return
        if c < neck - 0.25 * a and c < (p2 + 0.5) * step:
            yield i, -1; return


SETUPS = [
    dict(id='double_distribution_neck', name='Double-distribution neck', family='volume profile',
         detect=double_dist_neck,
         rules="From 12:00 to 14:00, if the session's volume profile shows two separate fat regions at least 1.5 ATR "
               "apart (each at least 60% of the heaviest price) joined by a thin neck (under 35% of the smaller "
               "region), the first close at least 0.25 ATR above (below) the neck marks which distribution price "
               "has settled in. One signal per session; tested with and against."),
]
