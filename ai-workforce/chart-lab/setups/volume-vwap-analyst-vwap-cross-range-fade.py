"""Chop day (many VWAP crossings) then a failed poke of the IB extreme.
Added 2026-10-04 by volume-vwap-analyst: the research queue held only tape items, so this run took the
Market Profile "balanced day" idea found by WebSearch (rotation around value means extremes get rejected).
Rules were fixed BEFORE any P&L was seen: >= 4 VWAP side flips by 11:30, then after 11:35 a bar that
trades through the IB high/low but closes back inside it. One per session.
"""


def vwap_cross_range_fade(s):
    """If price has flipped sides of VWAP (by close) at least 4 times through 11:30, the first bar between 11:35
    and 14:30 that pokes through the IB high and closes back inside leans short; through the IB low and closes
    back inside leans long. One signal per session."""
    b = s.bars
    if len(b) < 26:
        return
    flips, side = 0, 0
    for i in range(24):
        sd = 1 if b[i].c > s.vwap[i] else (-1 if b[i].c < s.vwap[i] else 0)
        if sd and side and sd != side:
            flips += 1
        if sd:
            side = sd
    if flips < 4:
        return
    for i in range(24, len(b)):
        if b[i].m >= 870:
            break
        if b[i].h > s.ib_hi and b[i].c < s.ib_hi:
            yield i, -1
            return
        if b[i].l < s.ib_lo and b[i].c > s.ib_lo:
            yield i, 1
            return


SETUPS = [
    dict(id='vwap_cross_range_fade', name='Chop day: failed poke of the IB extreme', family='volume/VWAP',
         detect=vwap_cross_range_fade,
         rules="When price has crossed VWAP at least 4 times by 11:30 (a balanced, rotating day), the first bar "
               "between 11:35 and 14:30 that trades through the initial-balance high but closes back inside leans "
               "short; through the IB low but closes back inside leans long. One signal per session."),
]
