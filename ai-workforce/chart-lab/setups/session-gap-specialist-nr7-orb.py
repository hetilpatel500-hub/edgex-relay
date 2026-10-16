"""Crabel NR7 opening-range breakout on 5-minute bars.
Added 2026-09-29 by session-gap-specialist: the research queue's non-tape lines
are coded, so this run used WebSearch (Crabel's NR7 + ORB, summarised by
tradersmastermind.com and Concretum Research). Distinct from orb15 (every day,
15-minute range) and d_nr7_break (daily bars): the breakout is the first
5-minute candle's range, taken only the morning after a narrowest-range-of-7 day.
"""


def _nr7(s):
    """True when yesterday's high-low range is the smallest of the last 7 completed sessions."""
    rngs, p = [], s.prior
    while p is not None and len(rngs) < 7:
        rngs.append(p.hi - p.lo)
        p = p.prior
    return len(rngs) == 7 and rngs[0] == min(rngs)


def nr7_orb(s):
    """After an NR7 day: a 5-minute close beyond the first 5-minute bar's high
    (long) or low (short) between 09:40 and 11:00, only in the direction the
    first candle closed (up candle -> long only, down candle -> short only).
    One signal per session."""
    if not _nr7(s):
        return
    b = s.bars
    f = b[0]
    if f.c == f.o:
        return
    d = 1 if f.c > f.o else -1
    for i in range(1, len(b)):
        if b[i].m >= 660:
            return
        if d == 1 and b[i].c > f.h:
            yield i, 1
            return
        if d == -1 and b[i].c < f.l:
            yield i, -1
            return


SETUPS = [
    dict(id='nr7_orb', name='NR7 day then first-candle opening-range breakout (Crabel)', family='opening range',
         detect=nr7_orb,
         rules="Yesterday's range was the narrowest of the last 7 sessions. If today's first 5-minute candle closes up, "
               "the first 5-minute close above its high before 11:00 ET leans long; if it closes down, the first close "
               "below its low leans short. One trade per session."),
]
