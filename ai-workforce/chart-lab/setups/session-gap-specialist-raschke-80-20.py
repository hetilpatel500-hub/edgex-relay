"""Raschke's 80-20 reversal, on 5-minute bars.
Added 2026-09-30 by session-gap-specialist: from a WebSearch of Street Smarts'
80-20 rules (Connors and Raschke 1995; forex.academy, mql5.com,
tradingliteracy.com). Parameters (20% zones, average-range size filter, 14:30
cutoff) were fixed from the published rules before any P&L was seen.
Distinct from oops_reversal (gap beyond the prior extreme) and pd_sweep
(any sweep): it needs yesterday to be a full-range trend day that opened in
one 20% zone and closed in the other.
"""


def raschke_8020(s):
    """Yesterday opened in the top 20% of its range and closed in the bottom
    20% (range at least the average of up to the prior 10 sessions' ranges).
    Today, once price trades below yesterday's low and a 5-minute bar then
    closes back above that low, lean long. The mirror (opened bottom 20%,
    closed top 20%, trades above yesterday's high, closes back below) leans
    short. One signal per session, before 14:30."""
    p = s.prior
    if p is None or p.hi <= p.lo:
        return
    rng = p.hi - p.lo
    rs, q = [], p.prior
    while q is not None and len(rs) < 10:
        rs.append(q.hi - q.lo)
        q = q.prior
    if len(rs) < 5 or rng < sum(rs) / len(rs):
        return
    op = (p.open - p.lo) / rng
    cl = (p.close - p.lo) / rng
    if op >= 0.8 and cl <= 0.2:
        side, level = 1, p.lo
    elif op <= 0.2 and cl >= 0.8:
        side, level = -1, p.hi
    else:
        return
    broke = False
    for i, x in enumerate(s.bars):
        if x.m >= 870:
            return
        if side == 1:
            if x.l < level:
                broke = True
            if broke and x.c > level:
                yield i, 1
                return
        else:
            if x.h > level:
                broke = True
            if broke and x.c < level:
                yield i, -1
                return


SETUPS = [
    dict(id='raschke_80_20', name="Raschke's 80-20 reversal (prior day opened in one 20% zone, closed in the other)",
         family='gaps', detect=raschke_8020,
         rules="Yesterday opened in the top 20% of its range and closed in the bottom 20% (range at least its "
               "recent average). Today price trades below yesterday's low, then a 5-minute bar closes back "
               "above it: lean long. Mirror for an up-and-reverse day: short. One signal per session, before 14:30 ET."),
]
