"""Narrowest-range-of-4-days (NR4) yesterday, then a break of today's initial balance.
Added 2026-10-07 by volatility-analyst via Toby Crabel's NR4 contraction-to-expansion work (queue: NR bars).
Parameters fixed BEFORE any P&L was seen: yesterday's high-low range is the smallest of the last 4 sessions
(yesterday and the 3 before it); signal is the first 5-minute close beyond the initial balance high (low),
from 10:30 to 12:55; one per session.
"""


def nr4_ib_break(s):
    p = s.prior
    if p is None:
        return
    rngs, q = [], p
    for _ in range(4):
        if q is None:
            return
        rngs.append(q.hi - q.lo)
        q = q.prior
    if rngs[0] > min(rngs):
        return
    for i, x in enumerate(s.bars):
        if i < 12 or x.m > 775:
            continue
        if x.c > s.ib_hi:
            yield i, 1
            return
        if x.c < s.ib_lo:
            yield i, -1
            return


SETUPS = [
    dict(id='nr4_ib_break', name='NR4 yesterday, then initial balance break', family='volatility',
         detect=nr4_ib_break,
         rules="Yesterday's range was the narrowest of the last four sessions. The first 5-minute close from "
               "10:30 to 12:55 beyond today's initial balance high (low) is the signal; one per session; "
               "tested with and against."),
]
