"""Opening-bar trap: an oversized first 5-minute bar whose direction is reversed through its midpoint.
Added 2026-10-07 by session-gap-specialist via WebSearch on opening-range failure (a break that quickly returns
inside leaves the breakout traders trapped: see the TradingView failed-breakout / ORB scripts surfaced by the search).
This is the single-bar version of that idea. Distinct from orb_failure (30-minute range), or5_break (trades the
break) and open_rejection_reverse (open-type classification).
Parameters fixed BEFORE any P&L was seen: the first bar's range is at least 2.0 five-minute ATRs and it closes in the
outer 30% of its range in its own direction. The first later bar before 10:15 that closes beyond the first bar's
midpoint the other way is the signal, against the first bar's direction. One per session.
"""


def opening_bar_trap(s):
    b = s.bars
    f = b[0]
    a = s.atr[0]
    rng = f.h - f.l
    if not a or rng < 2.0 * a or rng <= 0:
        return
    mid = (f.h + f.l) / 2
    if f.c >= f.l + 0.7 * rng:
        for i in range(1, len(b)):
            if b[i].m >= 615:
                break
            if b[i].c < mid:
                yield i, -1
                return
    elif f.c <= f.l + 0.3 * rng:
        for i in range(1, len(b)):
            if b[i].m >= 615:
                break
            if b[i].c > mid:
                yield i, 1
                return


SETUPS = [
    dict(id='opening_bar_trap', name='Oversized opening bar reversed through its midpoint', family='opening range',
         detect=opening_bar_trap,
         rules="The first 5-minute bar has a range of at least 2 ATR and closes in the outer 30% of its range in "
               "its own direction. The first later bar before 10:15 that closes beyond that bar's midpoint the "
               "other way is the signal, against the opening bar's direction. One per session; tested with and "
               "against."),
]
