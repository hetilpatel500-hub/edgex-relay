"""Initial balance built entirely inside yesterday's value area, first break out of it.
Added 2026-10-08 by volume-vwap-analyst (value-area / initial-balance work: a
first hour that never leaves yesterday's accepted value is a day still inside
the old auction, so the first move out of the IB is either a real departure or
a probe that returns). Rule fixed before any P&L was seen; everything is known
at the signal bar's close.
"""


def ib_inside_value_break(s):
    p = s.prior
    if p is None or p.vah <= p.val:
        return
    if s.ib_hi > p.vah or s.ib_lo < p.val:
        return
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if b[i].c > s.ib_hi:
            yield i, 1; return
        if b[i].c < s.ib_lo:
            yield i, -1; return


SETUPS = [
    dict(id='ib_inside_value_break', name="Initial balance inside yesterday's value, first break",
         family='volume profile', detect=ib_inside_value_break,
         rules="When the first hour's high and low both sit inside yesterday's 70% value area, the first "
               "5-minute close beyond the initial balance (before 14:00) leans in the break direction. "
               "Tested with and against; one signal per session."),
]
