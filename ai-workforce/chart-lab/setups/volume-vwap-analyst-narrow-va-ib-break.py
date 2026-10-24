"""Narrow prior-day value area -> IB breakout in the break's direction.
Added 2026-10-01 by volume-vwap-analyst, from a WebSearch run (breakingtrade.com
market profile day types; daytradingtoolkit.com inside-day breakout): the
contraction/expansion premise says a tight value area yesterday tends to be
followed by a trending day. Threshold fixed before any P&L was seen:
yesterday's 70% value area no wider than 0.30% of yesterday's close.
Everything is known at the signal bar's close.
"""


def narrow_va_ib_break(s):
    p = s.prior
    if p is None or not p.close:
        return
    if (p.vah - p.val) / p.close > 0.003:
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
    dict(id='narrow_va_ib_break', name='Narrow prior value area, IB breakout', family='volume profile',
         detect=narrow_va_ib_break,
         rules="If yesterday's 70% value area (VAH-VAL) was no wider than 0.30% of yesterday's close, the first "
               "5-minute close beyond today's initial balance (first hour) before 14:00 leans in the break "
               "direction. Tested with and against; one signal per session."),
]
