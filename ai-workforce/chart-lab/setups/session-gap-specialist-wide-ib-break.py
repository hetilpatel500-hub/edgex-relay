"""Wide initial balance, then the first break of it.
Added 2026-10-04 by session-gap-specialist: the research queue held only tape items and untested ideas had been
coded, so this run took the Dalton / Market Profile idea that a wide first hour (range already large versus a normal
day) marks a day that is expanding, so the first extension beyond the initial balance is more often a trend-day
continuation than a trap (narrow_ib_break tests the opposite, compressed, case). Rules fixed BEFORE any P&L was
seen: IB range >= 0.5 of the average of the last 10 sessions' ranges (5 needed), first close beyond the IB between
10:30 and 14:00, one signal per session.
"""


def wide_ib_break(s):
    """When the 9:30-10:30 range is at least half the average daily range of the previous 10 full sessions, the first
    5-minute close beyond the IB high/low between 10:30 and 14:00 leans with the break. One per session."""
    ranges, p = [], s.prior
    while p is not None and len(ranges) < 10:
        ranges.append(p.hi - p.lo)
        p = p.prior
    if len(ranges) < 5:
        return
    adr = sum(ranges) / len(ranges)
    if (s.ib_hi - s.ib_lo) < 0.5 * adr:
        return
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m >= 840:
            break
        if b[i].c > s.ib_hi:
            yield i, 1
            return
        if b[i].c < s.ib_lo:
            yield i, -1
            return


SETUPS = [
    dict(id='wide_ib_break', name='Wide initial balance breakout', family='session/initial balance',
         detect=wide_ib_break,
         rules="When the 9:30-10:30 range is at least half the average daily range of the last 10 sessions, the "
               "first 5-minute close beyond the initial balance high or low between 10:30 and 14:00 leans with the "
               "break. Tested with and against; one signal per session."),
]
