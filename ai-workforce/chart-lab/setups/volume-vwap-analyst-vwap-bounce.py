"""VWAP tag-and-hold bounce in a trending session on 5-minute bars.
Added 2026-09-28 by volume-vwap-analyst: the research queue's non-tape lines
are all coded, so this run used WebSearch (tradezella.com, trademomentum.org)
for a documented, untested VWAP technique: on a trend day, price that pulls
back to VWAP and holds is read as institutions defending their average cost.
Distinct from vwap_reclaim (crossing back through VWAP) and vwap_2sd_revert.
"""


def vwap_bounce(s):
    """Trend session: the prior 6 bars all closed on one side of VWAP and
    VWAP has moved at least 0.5 ATR in that direction over 6 bars. A bar whose
    wick tags VWAP (within 0.1 ATR) yet closes back on the trend side, in the
    trend direction (up bar for long, down bar for short), leans with the
    trend. One signal per side per session, 10:00 to 14:30."""
    b = s.bars
    fired = set()
    for i in range(12, len(b)):
        if b[i].m >= 870:
            break
        atr, v = s.atr[i], s.vwap[i]
        if not atr:
            continue
        prior = b[i - 6:i]
        up = all(x.c > s.vwap[i - 6 + k] for k, x in enumerate(prior)) and v - s.vwap[i - 6] >= 0.5 * atr
        dn = all(x.c < s.vwap[i - 6 + k] for k, x in enumerate(prior)) and s.vwap[i - 6] - v >= 0.5 * atr
        x = b[i]
        if up and 1 not in fired and x.l <= v + 0.1 * atr and x.c > v and x.c > x.o:
            fired.add(1)
            yield i, 1
        elif dn and -1 not in fired and x.h >= v - 0.1 * atr and x.c < v and x.c < x.o:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='vwap_bounce', name='VWAP tag-and-hold in a trending session', family='vwap',
         detect=vwap_bounce,
         rules="After six bars closing on one side of VWAP with VWAP drifting at least 0.5 ATR that way, a bar "
               "that wicks to VWAP and closes back on the trend side in the trend direction leans with the "
               "trend. One signal per side per session, 10:00 to 14:30."),
]
