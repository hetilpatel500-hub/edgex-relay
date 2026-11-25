"""VWAP decisive break, then first retest, on 5-minute bars.
Added 2026-10-03 by volume-vwap-analyst: the research queue's non-tape lines are
coded, so this run used WebSearch (tradingview / daytradingtoolkit VWAP
reversal write-ups) for a documented, untested idea: price breaks VWAP, then
retests it within a few bars before continuing. Distinct from vwap_reclaim
(needs 6 bars on one side first) and vwap_bounce (needs an established trend).
"""


def vwap_break_retest(s):
    """A bar closes at least 0.4 ATR beyond VWAP after the prior bar closed on
    the other side (the break). Within the next 2 to 8 bars, the first bar whose
    range touches VWAP (within 0.1 ATR) yet closes back on the break side leans
    in the break direction. One signal per side per session, 10:00 to 14:30."""
    b = s.bars
    fired = set()
    brk = None  # (direction, bar index)
    for i in range(1, len(b)):
        if b[i].m >= 870:
            break
        atr, v = s.atr[i], s.vwap[i]
        if not atr:
            continue
        pv = s.vwap[i - 1]
        if brk is not None:
            d, j = brk
            k = i - j
            if k > 8 or (d == 1 and b[i].c < v - 0.1 * atr) or (d == -1 and b[i].c > v + 0.1 * atr):
                brk = None  # window expired or break failed
            elif k >= 2 and b[i].m >= 600 and d not in fired:
                touch = b[i].l <= v + 0.1 * atr if d == 1 else b[i].h >= v - 0.1 * atr
                hold = b[i].c > v if d == 1 else b[i].c < v
                if touch and hold:
                    fired.add(d)
                    brk = None
                    yield i, d
                    continue
        if b[i].c > v + 0.4 * atr and b[i - 1].c < pv:
            brk = (1, i)
        elif b[i].c < v - 0.4 * atr and b[i - 1].c > pv:
            brk = (-1, i)


SETUPS = [
    dict(id='vwap_break_retest', name='VWAP break then first retest', family='volume/vwap',
         detect=vwap_break_retest,
         rules="A 5-minute bar closing 0.4 ATR beyond VWAP right after a close on the other side is a break. "
               "The first bar 2 to 8 bars later that touches VWAP (within 0.1 ATR) and closes back on the break "
               "side leans in the break direction; one per side per session, 10:00 to 14:30."),
]
