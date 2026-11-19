"""Gap pulls back to its halfway level and holds.
Added 2026-10-04 by session-gap-specialist: the research queue held only tape items, so this run took the
"half gap" idea found by WebSearch (the 50% level of an opening gap is a common intraday turning point and is
reached more often than a full fill). Rules were fixed BEFORE any P&L was seen: gap >= 0.25% of the prior close,
one signal per session, 9:45-14:30 ET. Distinct from gap_fade_rvol / gap_go_rvol (those act at the open).
"""


def gap_half_fill_hold(s):
    """Gap of at least 0.25% between yesterday's close and today's open. After the first three bars, the first
    bar whose range reaches the halfway level of the gap but closes back on the gap's side of it leans WITH the
    gap (long after a gap up, short after a gap down), provided the gap has not already been fully filled.
    One signal per session, between 9:45 and 14:30."""
    p = s.prior
    b = s.bars
    if p is None or len(b) < 4:
        return
    pc, o = p.close, s.open
    gap = o - pc
    if pc <= 0 or abs(gap) < 0.0025 * pc:
        return
    mid = pc + gap / 2
    up = gap > 0
    for i in range(3, len(b)):
        if b[i].m >= 870:
            break
        if up:
            if min(x.l for x in b[:i]) <= pc:
                return
            if b[i].l <= mid and b[i].c > mid:
                yield i, 1
                return
        else:
            if max(x.h for x in b[:i]) >= pc:
                return
            if b[i].h >= mid and b[i].c < mid:
                yield i, -1
                return


SETUPS = [
    dict(id='gap_half_fill_hold', name='Opening gap pulls back to its halfway level and holds', family='session/gap',
         detect=gap_half_fill_hold,
         rules="When the open is at least 0.25% away from yesterday's close and the gap is still unfilled, the first "
               "bar after 9:45 (until 14:30) that trades down to (after a gap up) or up to (after a gap down) the "
               "halfway level of the gap but closes back on the gap's side of it leans with the gap. One signal "
               "per session."),
]
