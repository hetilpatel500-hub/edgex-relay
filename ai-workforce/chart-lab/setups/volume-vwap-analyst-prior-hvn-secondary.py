"""Yesterday's secondary high volume node (HVN) first-touch rejection.
Added 2026-10-01 by volume-vwap-analyst, from a WebSearch run (trader-dale.com
High-Volume Node pullback guide; tradezella.com volume profile strategy): a
bimodal prior-day profile leaves a second acceptance zone away from the POC,
and a first return to it should react. Distinct from prior_poc_rejection (the
POC itself) and prior_lvn_rejection (the thin node). Rules fixed before any P&L
was seen; everything is known at the signal bar's close.
"""


def _hvn(bars, bps=5.0):
    import statistics as st
    px = st.median(x.c for x in bars)
    step = px * bps / 1e4
    vol = {}
    for x in bars:
        lo, hi = int(x.l // step), int(x.h // step)
        share = x.v / (hi - lo + 1)
        for k in range(lo, hi + 1):
            vol[k] = vol.get(k, 0) + share
    poc = max(vol, key=vol.get)
    best = None
    for k, v in vol.items():
        if abs(k - poc) < 6 or v < 0.7 * vol[poc]:
            continue
        if all(v >= vol.get(k + j, 0) for j in range(-2, 3)):
            if best is None or v > vol[best]:
                best = k
    return None if best is None else (best + 0.5) * step


def prior_hvn_secondary(s):
    p = s.prior
    if p is None:
        return
    hvn = _hvn(p.bars)
    if hvn is None:
        return
    b = s.bars
    side = 0
    for i in range(3, len(b)):
        if b[i].m >= 840:
            return
        if side == 0:
            if b[i - 1].l > hvn:
                side = 1
            elif b[i - 1].h < hvn:
                side = -1
        if side == 1 and b[i].l <= hvn and b[i].c > hvn:
            yield i, 1; return
        if side == -1 and b[i].h >= hvn and b[i].c < hvn:
            yield i, -1; return
        if side == 1 and b[i].c < hvn or side == -1 and b[i].c > hvn:
            return


SETUPS = [
    dict(id='prior_hvn_secondary', name="Yesterday's secondary high volume node first-touch rejection", family='volume profile',
         detect=prior_hvn_secondary,
         rules="Yesterday's profile (5 bps bins): a second peak at least 6 bins from the POC, with at least 70% "
               "of the POC's bin volume and the highest volume within 2 bins either side, is the secondary HVN. "
               "Today, price trades on one side; the first bar before 14:00 that wicks to the HVN but closes "
               "back on the approach side leans in the approach direction. Tested with and against; one signal "
               "per session, cancelled if a bar closes through the HVN first."),
]
