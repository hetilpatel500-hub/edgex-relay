"""Wide Central Pivot Range: R1/S1 touch rejected.
Added 2026-10-02 by support-resistance-mapper: queue empty apart from tape
items, so WebSearch found the CPR guidance (groww.in "Central Pivot Range":
a wide CPR hints at a range day, trade reversals at the support/resistance
zones). Complements narrow_cpr_break. Parameters (width >= 0.2 x prior range,
10:00-14:00, one per session) were fixed before testing and are not tuned.
"""


def wide_cpr_r1s1_fade(s):
    """Pivot P=(H+L+C)/3, BC=(H+L)/2, TC=2P-BC, R1=2P-L, S1=2P-H from
    yesterday. If |TC-BC| >= 0.2 x yesterday's range, the first 5-minute bar
    between 10:00 and 14:00 that trades to R1 (S1) and closes back below
    (above) it fires against the touch. One signal per session."""
    p = s.prior
    if p is None:
        return
    r = p.hi - p.lo
    if r <= 0:
        return
    piv = (p.hi + p.lo + p.close) / 3
    bc = (p.hi + p.lo) / 2
    tc = 2 * piv - bc
    if abs(tc - bc) < 0.2 * r:
        return
    r1, s1 = 2 * piv - p.lo, 2 * piv - p.hi
    for i in range(6, len(s.bars)):
        b = s.bars[i]
        if b.m >= 840:
            return
        if b.h >= r1 and b.c < r1:
            yield i, -1
            return
        if b.l <= s1 and b.c > s1:
            yield i, 1
            return


SETUPS = [
    dict(id='wide_cpr_r1s1_fade', name='Wide CPR: R1/S1 touch rejected', family='levels',
         detect=wide_cpr_r1s1_fade,
         rules="When yesterday's central pivot range (BC to TC) is at least 20% of yesterday's range, the "
               "first 5-minute bar from 10:00 to 14:00 that trades to the classic R1 (S1) and closes back "
               "below (above) it leans against the touch."),
]
