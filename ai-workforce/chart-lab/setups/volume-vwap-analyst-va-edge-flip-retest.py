"""Yesterday's value area edge flip: first retest after an open outside value.
Added 2026-10-01 by volume-vwap-analyst: auction-theory idea (a day that opens
and holds outside the prior value area treats the old VAH/VAL as new
support/resistance), distinct from outside_va_acceptance and va_edge_rejection,
which are not retests. Rules fixed before any P&L was seen; everything is known
at the signal bar's close.
"""


def va_edge_flip_retest(s):
    p = s.prior
    if p is None or not p.vah or not p.val:
        return
    b = s.bars
    if s.open > p.vah:
        edge, d = p.vah, 1
    elif s.open < p.val:
        edge, d = p.val, -1
    else:
        return
    for i in range(1, len(b)):
        if b[i].m >= 840:
            return
        atr = s.atr[i]
        if not atr:
            continue
        if d * (b[i].c - edge) <= 0:
            return                      # closed back inside value: flip failed
        if i >= 3 and d == 1 and b[i].l <= edge + 0.1 * atr:
            yield i, 1; return
        if i >= 3 and d == -1 and b[i].h >= edge - 0.1 * atr:
            yield i, -1; return


SETUPS = [
    dict(id='va_edge_flip_retest', name="Yesterday's value area edge: first retest after opening outside", family='volume profile',
         detect=va_edge_flip_retest,
         rules="The session opens above yesterday's VAH (below yesterday's VAL). The first bar from the 4th bar "
               "to 14:00 whose low (high) comes within 0.1 ATR of that edge while it closes still outside value "
               "leans long (short): old value edge flips to support (resistance). Cancelled if any bar closes "
               "back inside value first. Tested with and against; one signal per session."),
]
