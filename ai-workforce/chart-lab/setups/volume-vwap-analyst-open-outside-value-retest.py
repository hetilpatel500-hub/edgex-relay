"""Open outside yesterday's value area: first pullback to the VAH / VAL.
Added 2026-10-04 by volume-vwap-analyst: volume profile family, from a WebSearch of the
"open above / below value" rule (open above yesterday's VAH is strength; the first pullback to the VAH
is expected to flip resistance to support, mirrored below the VAL). Parameters fixed BEFORE any P&L was seen:
the first bar opens beyond the prior VAH (or VAL) and its close is still beyond it; the signal is the first
bar before 14:00 that trades back to within the level and closes back beyond it (wick test held);
cancelled if a bar closes back through the level first. One signal per session. The lab tests it with
and against (against = the "failed auction" reading).
"""


def open_outside_value_retest(s):
    p = s.prior
    if p is None or not p.vah or not p.val:
        return
    b = s.bars
    if b[0].o > p.vah:
        d, lvl = 1, p.vah
    elif b[0].o < p.val:
        d, lvl = -1, p.val
    else:
        return
    for i in range(1, len(b) - 1):
        if b[i].m >= 840:
            return
        if d * (b[i].c - lvl) <= 0:
            return
        if (b[i].l <= lvl) if d == 1 else (b[i].h >= lvl):
            yield i, d
            return


SETUPS = [
    dict(id='open_outside_value_retest', name="Open outside prior value: first pullback to VAH/VAL", family='volume profile',
         detect=open_outside_value_retest,
         rules="The session opens above yesterday's value area high (or below the value area low). The first "
               "bar before 14:00 that wicks back to that level and closes beyond it again leans with the "
               "opening direction; cancelled if a bar closes back through the level first. Once per session, "
               "tested with and against."),
]
