"""Wide first hour that closes at one end, first pullback to its midpoint.
Added 2026-10-04 by session-gap-specialist via the Crabel range-expansion idea (a wide opening
range that closes near its extreme marks a trend day). Parameters fixed BEFORE any P&L was seen:
first-hour (IB) range at least 1.5x yesterday's IB range, the 11:00 close in the top or bottom
25% of that range, then the first 5-minute bar before 14:00 that trades to the IB midpoint and
closes back on the drive's side of it. One per session. The lab tests it with and against.
"""


def wide_ib_midpoint_pullback(s):
    p = s.prior
    b = s.bars
    if p is None or len(b) < 14 or b[11].m != 625:
        return
    rng = s.ib_hi - s.ib_lo
    prng = p.ib_hi - p.ib_lo
    if rng <= 0 or prng <= 0 or rng < 1.5 * prng:
        return
    pos = (b[11].c - s.ib_lo) / rng
    if pos >= 0.75:
        d = 1
    elif pos <= 0.25:
        d = -1
    else:
        return
    mid = (s.ib_hi + s.ib_lo) / 2
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if d == 1 and b[i].l <= mid < b[i].c:
            yield i, d
            return
        if d == -1 and b[i].h >= mid > b[i].c:
            yield i, d
            return


SETUPS = [
    dict(id='wide_ib_midpoint_pullback', name='Wide first hour: pullback to its midpoint', family='session',
         detect=wide_ib_midpoint_pullback,
         rules="The first hour's range is at least 1.5x yesterday's and the 11:00 close sits in its top (or "
               "bottom) 25%: lean with the drive on the first bar before 14:00 that trades to the first-hour "
               "midpoint and closes back on the drive's side, once per session."),
]
