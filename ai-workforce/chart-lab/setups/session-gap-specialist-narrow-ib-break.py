"""Narrow initial balance breakout.
Added 2026-09-30 by session-gap-specialist: initial balance family. Market
profile teaching (Steidlmayer/Dalton): a narrow first hour tends to be followed
by range expansion. The 50% threshold was fixed before any P&L was seen.
Everything is known at the signal bar's close.
"""


def narrow_ib_break(s):
    p = s.prior
    if p is None or p.hi <= p.lo:
        return
    if (s.ib_hi - s.ib_lo) >= 0.5 * (p.hi - p.lo):
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
    dict(id='narrow_ib_break', name='Narrow initial balance breakout', family='initial balance',
         detect=narrow_ib_break,
         rules="When the first-hour (9:30-10:30) range is under half of yesterday's high-low range, the first "
               "5-minute close beyond the first-hour high or low, before 14:00, leans with the break. Tested "
               "with and against; one signal per session."),
]
