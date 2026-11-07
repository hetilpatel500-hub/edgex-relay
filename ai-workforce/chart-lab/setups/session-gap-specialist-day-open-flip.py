"""First-hour commitment, then a flip back through the day's open.
Added 2026-10-04 by session-gap-specialist: the research queue held only tape items, so this run took the
documented "Smart Flip" idea found by WebSearch (prior day and first hour agree, then price flips back through
the daily open). Rules were fixed BEFORE any P&L was seen: prior day body direction, first hour closing
>= 0.75 ATR from the open and never closing through it, flip = a close 0.25 ATR through the open, one per session.
Distinct from day_open_retest (which waits for a touch and leans WITH the move).
"""


def day_open_flip(s):
    """If yesterday's session closed up (down), and the first hour (to 10:30) ended at least 0.75 ATR above
    (below) today's open with no 5-minute close on the wrong side of the open, then the first close between
    10:35 and 14:30 that is 0.25 ATR through the open leans the other way (short after an up first hour,
    long after a down first hour). One signal per session."""
    p = s.prior
    b = s.bars
    if p is None or len(b) < 13:
        return
    o = s.open
    pdir = 1 if p.close > p.open else (-1 if p.close < p.open else 0)
    if pdir == 0:
        return
    atr = s.atr[11]
    if not atr:
        return
    fh = b[11].c - o
    if pdir == 1:
        if fh < 0.75 * atr or any(x.c <= o for x in b[:12]):
            return
    else:
        if fh > -0.75 * atr or any(x.c >= o for x in b[:12]):
            return
    for i in range(12, len(b)):
        if b[i].m >= 870:
            break
        a = s.atr[i]
        if not a:
            continue
        if pdir == 1 and b[i].c <= o - 0.25 * a:
            yield i, -1
            return
        if pdir == -1 and b[i].c >= o + 0.25 * a:
            yield i, 1
            return


SETUPS = [
    dict(id='day_open_flip', name="Flip back through the day's open after a committed first hour", family='session/gap',
         detect=day_open_flip,
         rules="When yesterday closed up (down) and the first hour ends at least 0.75 ATR above (below) today's "
               "open without a 5-minute close through it, the first close between 10:35 and 14:30 that is 0.25 ATR "
               "through the open leans the opposite way (short after an up first hour, long after a down one). "
               "One signal per session."),
]
