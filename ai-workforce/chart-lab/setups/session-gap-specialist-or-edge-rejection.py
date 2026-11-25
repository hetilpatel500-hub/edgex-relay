"""Opening range edge rejection while the range holds.
Added 2026-10-06 by session-gap-specialist: the queue is fully coded, so this
run used WebSearch (TradingView ORB "Range mode" scripts: range BUY near the
opening-range low on a bullish rejection candle, range SELL near the high on a
bearish one, with the range as the battlefield). Distinct from orb_failure
(needs a close beyond the range first) and orb_retest (trades breakouts).
"""


def or_edge_rejection(s):
    """Between 9:45 and 11:30, while no 5-minute bar has closed outside the
    9:30-9:45 range, a bar whose wick reaches within 0.1 ATR of an edge (or
    beyond it) but that closes back inside the range, in the opposite third of
    its own range, leans away from that edge. The range must be at least 1 ATR
    wide. One signal per session."""
    b = s.bars
    rng_w = s.or_hi - s.or_lo
    for i in range(3, len(b)):
        if b[i].m >= 690:
            return
        x, atr = b[i], s.atr[i]
        if x.c > s.or_hi or x.c < s.or_lo:
            return
        if not atr or rng_w < atr or x.h <= x.l:
            continue
        pos = (x.c - x.l) / (x.h - x.l)
        if x.l <= s.or_lo + 0.1 * atr and pos >= 2 / 3:
            yield i, 1
            return
        if x.h >= s.or_hi - 0.1 * atr and pos <= 1 / 3:
            yield i, -1
            return


SETUPS = [
    dict(id='or_edge_rejection', name='Opening range edge rejection', family='opening range', detect=or_edge_rejection,
         rules="Until 11:30, while price has not closed outside the 9:30-9:45 range (range at least 1 ATR wide), a "
               "5-minute bar that wicks to within 0.1 ATR of the range low and closes in its top third leans long; "
               "one that wicks to the range high and closes in its bottom third leans short. One trade per session."),
]
