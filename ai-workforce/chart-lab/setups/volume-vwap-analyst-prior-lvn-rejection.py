"""Yesterday's low volume node (LVN) first-touch rejection.
Added 2026-10-01 by volume-vwap-analyst, from a WebSearch run (tradezella.com
Low Volume Node strategy; internationaltradinginstitute.com volume profile
acceptance vs rejection): an LVN is a price the market crossed quickly with
little volume, so a first return to it should react. Rules and thresholds were
fixed before any P&L was seen; everything is known at the signal bar's close.
"""
import statistics as st


def _lvn(bars, bps=5.0):
    px = st.median(x.c for x in bars)
    step = px * bps / 1e4
    vol = {}
    for x in bars:
        lo, hi = int(x.l // step), int(x.h // step)
        share = x.v / (hi - lo + 1)
        for k in range(lo, hi + 1):
            vol[k] = vol.get(k, 0) + share
    poc = max(vol, key=vol.get)
    total = sum(vol.values())
    lo = hi = poc
    acc = vol[poc]
    while acc < 0.7 * total:
        up, dn = vol.get(hi + 1, 0), vol.get(lo - 1, 0)
        if up == 0 and dn == 0:
            break
        if up >= dn:
            hi += 1; acc += up
        else:
            lo -= 1; acc += dn
    inner = [k for k in range(lo + 1, hi) if abs(k - poc) >= 3]
    if not inner:
        return None
    mean_va = sum(vol.get(k, 0) for k in range(lo, hi + 1)) / (hi - lo + 1)
    k = min(inner, key=lambda j: vol.get(j, 0))
    if vol.get(k, 0) > 0.6 * mean_va:
        return None
    return (k + 0.5) * step


def prior_lvn_rejection(s):
    p = s.prior
    if p is None:
        return
    lvn = _lvn(p.bars)
    if lvn is None:
        return
    b = s.bars
    side = 0
    for i in range(3, len(b)):
        if b[i].m >= 840:
            return
        if side == 0:
            if b[i - 1].l > lvn:
                side = 1
            elif b[i - 1].h < lvn:
                side = -1
        if side == 1 and b[i].l <= lvn and b[i].c > lvn:
            yield i, 1; return
        if side == -1 and b[i].h >= lvn and b[i].c < lvn:
            yield i, -1; return
        if side == 1 and b[i].c < lvn or side == -1 and b[i].c > lvn:
            return


SETUPS = [
    dict(id='prior_lvn_rejection', name="Yesterday's low volume node first-touch rejection", family='volume profile',
         detect=prior_lvn_rejection,
         rules="Yesterday's profile (5 bps bins): the lowest-volume bin inside the value area, at least 3 bins "
               "from the POC and at most 60% of the value area's mean bin volume, is the LVN. Today, price "
               "trades on one side; the first bar before 14:00 that wicks to the LVN but closes back on the "
               "approach side leans in the approach direction. Tested with and against; one signal per "
               "session, cancelled if a bar closes through the LVN first."),
]
