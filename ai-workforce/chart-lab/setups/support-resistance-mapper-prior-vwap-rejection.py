"""Rejection at yesterday's closing VWAP.
Added 2026-10-01 by support-resistance-mapper: the research queue is fully
coded, so this run picked a level the lab had not used. Yesterday's session
VWAP (the volume-weighted average price of the whole prior session, final
value) is a reference many participants watch as "yesterday's fair price".
Distinct from prior_close_cross, pd_acceptance and prior_poc_rejection, which
use the prior close, high/low and POC.
"""


def prior_vwap_rejection(s):
    """Price coming from one side of yesterday's final VWAP: a bar whose wick
    reaches it (within 0.1 ATR) but whose close stays on the side the bar
    opened from, in the rejecting direction, leans away from the level. Needs
    the prior bar open on the same side, so it is a first test from below
    (short) or from above (long). One signal per session, 10:00 to 14:30."""
    p = s.prior
    if p is None:
        return
    lvl = p.vwap[-1]
    b = s.bars
    for i in range(6, len(b)):
        if b[i].m >= 870:
            break
        atr = s.atr[i]
        if not atr:
            continue
        x = b[i]
        tol = 0.1 * atr
        if x.o < lvl and x.h >= lvl - tol and x.c < lvl and x.c < x.o and b[i - 1].c < lvl:
            yield i, -1
            return
        if x.o > lvl and x.l <= lvl + tol and x.c > lvl and x.c > x.o and b[i - 1].c > lvl:
            yield i, 1
            return


SETUPS = [
    dict(id='prior_vwap_rejection', name="Rejection at yesterday's closing VWAP", family='levels',
         detect=prior_vwap_rejection,
         rules="A bar that wicks to within 0.1 ATR of yesterday's final session VWAP and closes back on the "
               "side it came from, as a down bar from below or an up bar from above, leans away from the "
               "level. One signal per session, 10:00 to 14:30."),
]
