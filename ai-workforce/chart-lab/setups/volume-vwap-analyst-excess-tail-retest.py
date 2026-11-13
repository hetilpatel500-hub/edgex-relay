"""Retest of yesterday's excess (clean) high or low.
Added 2026-10-01 by volume-vwap-analyst, from the Market Profile idea that a
session extreme with a tail (excess) marks a rejected price: the auction left it
fast and the market tends to defend it on the next visit. This is the untested
complement of poor_high_low_break (poor extremes). Rules and the two-bin tail
were fixed before any P&L was seen; everything is known at the signal bar's close.
"""
import statistics as st


def _tails(bars, bps=5.0):
    px = st.median(x.c for x in bars)
    step = px * bps / 1e4
    touches = {}
    for x in bars:
        for k in range(int(x.l // step), int(x.h // step) + 1):
            touches[k] = touches.get(k, 0) + 1
    hb = int(max(x.h for x in bars) // step)
    lb = int(min(x.l for x in bars) // step)
    up = 0
    while touches.get(hb - up) == 1:
        up += 1
    dn = 0
    while touches.get(lb + dn) == 1:
        dn += 1
    return up >= 2, dn >= 2


def excess_tail_retest(s):
    p = s.prior
    if p is None:
        return
    hi_tail, lo_tail = _tails(p.bars)
    b = s.bars
    done_hi = done_lo = False
    for i in range(len(b)):
        if b[i].m >= 840:
            return
        a = s.atr[i]
        if not a:
            continue
        if hi_tail and not done_hi:
            if b[i].c > p.hi:
                done_hi = True
            elif b[i].h >= p.hi - 0.05 * a and b[i].c < p.hi:
                done_hi = True
                yield i, -1
        if lo_tail and not done_lo:
            if b[i].c < p.lo:
                done_lo = True
            elif b[i].l <= p.lo + 0.05 * a and b[i].c > p.lo:
                done_lo = True
                yield i, 1


SETUPS = [
    dict(id='excess_tail_retest', name="Retest of yesterday's excess high/low", family='volume profile',
         detect=excess_tail_retest,
         rules="Yesterday's profile (5 bps bins): if the session high (low) has a tail, meaning at least two "
               "consecutive bins from the extreme down (up) that only one 5-minute bar touched, it is an excess "
               "extreme. Today, the first bar before 14:00 that trades within 0.05 ATR of that extreme or "
               "beyond it but closes back on the inside leans away from it (short at an excess high, long at "
               "an excess low). Cancelled for that side if a bar closes beyond the extreme first. Tested with "
               "and against; up to one signal per side per session."),
]
