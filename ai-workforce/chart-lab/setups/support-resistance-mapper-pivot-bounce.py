"""Classic floor pivot point (R1/S1) bounce.
Added 2026-09-28 by support-resistance-mapper: research queue in
ai-workforce/chart-lab/README.md was exhausted down to the "waiting for
tape" order-flow lines (tape/ holds 0 sessions, so those stay blocked), so
this run added a new, documented line -- classic floor pivots, the
support-resistance-mapper's own family (session levels, pivots, round
numbers) -- and coded it the same hour.
https://www.luxalgo.com/library/concept/floor-pivots/ and
https://daytradingz.com/pivot-points/ describe the standard floor-trader
formula (pivot P = (H+L+C)/3, R1 = 2P-L, S1 = 2P-H) and the "bounce"
reading: fade a probe of R1/S1 that fails to close through, back toward
the pivot.
"""


def pivot_bounce(s):
    """Classic floor pivots from yesterday's session high/low/close: pivot
    P = (H+L+C)/3, R1 = 2P-L, S1 = 2P-H. A bar that trades up into R1 and
    closes back below it leans down (fade back toward the pivot); a bar
    that trades down into S1 and closes back above it leans up. One signal
    per side per session, before 15:00."""
    p = s.prior
    if p is None:
        return
    P = (p.hi + p.lo + p.close) / 3
    r1, s1 = 2 * P - p.lo, 2 * P - p.hi
    b = s.bars
    up_done = dn_done = False
    for i in range(len(b)):
        if b[i].m >= 900:
            break
        x = b[i]
        if not up_done and x.h >= r1 and x.c < r1:
            up_done = True
            yield i, -1
        if not dn_done and x.l <= s1 and x.c > s1:
            dn_done = True
            yield i, 1


SETUPS = [
    dict(id='pivot_bounce', name="Classic pivot R1/S1 bounce", family='support/resistance',
         detect=pivot_bounce,
         rules="Classic floor pivot P = (H+L+C)/3 from yesterday's session; R1 = 2P-L, S1 = 2P-H. "
               "A probe of R1 that closes back below it leans down toward the pivot; a probe of S1 "
               "that closes back above it leans up toward the pivot. One signal per side per session, "
               "before 15:00."),
]
