"""VWAP tail rejection (5-minute).
Added 2026-10-05 by volume-vwap-analyst: the research queue was fully ticked, so this run took the documented VWAP
rejection candle (tradezella.com/blog/vwap-trading-strategy, forextester.com/blog/vwap: a candle whose body sits fully
on one side of VWAP while its wick touches VWAP). Unlike vwap_bounce / vwap_second_touch it needs no prior trend, no
VWAP slope and no count of earlier touches. Rules fixed BEFORE any P&L was seen.
"""


def vwap_tail_rejection(s):
    b = s.bars
    fired = 0
    for i in range(3, len(b)):
        if b[i].m >= 870 or fired >= 2:
            break
        x, w, atr = b[i], s.vwap[i], s.atr[i]
        if not atr:
            continue
        lo_body, hi_body = min(x.o, x.c), max(x.o, x.c)
        body = hi_body - lo_body
        if lo_body > w and x.l <= w + 0.05 * atr and (lo_body - x.l) >= max(body, 0.3 * atr) and x.c > x.o:
            fired += 1
            yield i, 1                 # tail down to VWAP, body above, closed up
        elif hi_body < w and x.h >= w - 0.05 * atr and (x.h - hi_body) >= max(body, 0.3 * atr) and x.c < x.o:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='vwap_tail_rejection', name='VWAP tail rejection', family='VWAP', detect=vwap_tail_rejection,
         rules="A 5-minute candle whose whole body sits above VWAP, closes up, and whose lower wick reaches VWAP "
               "(within 0.05 ATR) and is at least as long as the body and 0.3 ATR leans long; the mirror below "
               "VWAP leans short. Up to two signals a session, 9:45 to 14:30."),
]
