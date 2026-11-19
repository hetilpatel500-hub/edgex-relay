"""Yesterday's outside day closing on its extreme, followed by an initial balance break.
Added 2026-10-06 by session-gap-specialist via Toby Crabel / Linda Raschke outside-day follow-through
write-ups (an outside day that closes at its extreme shows one side won the wider auction).
Parameters fixed BEFORE any P&L was seen: yesterday's high is above and low below the day before's, and it
closed in the top (bottom) 25% of its range; signal is the first 5-minute close beyond the initial balance
high (low) in that direction from 10:30 to 12:55; one per session.
"""


def outside_day_ib_follow(s):
    p = s.prior
    if p is None or p.prior is None or p.hi <= p.lo:
        return
    q = p.prior
    if not (p.hi > q.hi and p.lo < q.lo):
        return
    loc = (p.close - p.lo) / (p.hi - p.lo)
    if loc >= 0.75:
        d = 1
    elif loc <= 0.25:
        d = -1
    else:
        return
    for i, x in enumerate(s.bars):
        if i < 12 or x.m > 775:
            continue
        if d == 1 and x.c > s.ib_hi:
            yield i, 1
            return
        if d == -1 and x.c < s.ib_lo:
            yield i, -1
            return


SETUPS = [
    dict(id='outside_day_ib_follow', name='Outside day closing on its extreme, then IB break with it', family='session',
         detect=outside_day_ib_follow,
         rules="Yesterday's range engulfed the day before's and it closed in the top (bottom) quarter of its range. "
               "The first 5-minute close from 10:30 to 12:55 beyond today's initial balance high (low) in that "
               "direction is the signal; one per session; tested with and against."),
]
