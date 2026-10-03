"""Tight-box breakout in the direction of VWAP.
Added 2026-09-30 by trend-moving-average-analyst: the research queue is fully
coded, so this run used WebSearch (opening-range / consolidation breakout
write-ups) for an untested idea: a contraction mid-session that resolves with
the side of VWAP the market is already on. Differs from lunch_range_break (fixed
clock window, no VWAP side) and bb_squeeze_expansion (band width). Numbers
(8 bars, 3.0 ATR, 10:30-14:30) were fixed before any P&L was seen; everything
is known at the signal bar's close.
"""


def vwap_box_break(s):
    b = s.bars
    for i in range(20, len(b)):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        box = b[i - 8:i]
        hi, lo = max(x.h for x in box), min(x.l for x in box)
        if hi - lo > 3.0 * s.atr[i - 1]:
            continue
        if b[i].c > hi and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if b[i].c < lo and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='vwap_box_break', name='Tight box breakout with VWAP', family='trend',
         detect=vwap_box_break,
         rules="Between 10:30 and 14:30, when the last eight 5-minute bars fit inside a box no taller than "
               "3 ATR, the first bar that closes beyond the box on the same side of VWAP leans with the "
               "break. Tested with and against; one signal per session."),
]
