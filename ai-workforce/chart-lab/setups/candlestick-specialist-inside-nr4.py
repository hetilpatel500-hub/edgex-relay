"""Inside bar / NR4 on 5-minute bars at a session level.
Added 2026-09-27 by candlestick-specialist: candlestick family, next open
line of the research queue in ai-workforce/chart-lab/README.md.
"""


def _near_level(s, i, lo, hi, atr):
    """True if the bar's own range sits within 0.25 ATR of session VWAP or
    yesterday's high/low -- levels known at the time, no look-ahead."""
    if not atr:
        return False
    levels = [s.vwap[i]]
    if s.prior:
        levels += [s.prior.hi, s.prior.lo]
    return any(lo - 0.25 * atr <= lvl <= hi + 0.25 * atr for lvl in levels)


def inside_nr4_at_level(s):
    """An inside bar (high/low inside the prior bar's range) or an NR4 bar
    (narrowest range of itself and the prior 3) that forms within 0.25 ATR of
    VWAP or yesterday's high/low marks compression at a level worth watching.
    The first of the next 3 bars whose close breaks that compression bar's
    own high or low leans with the breakout."""
    b = s.bars
    fired = 0
    for i in range(3, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        rng = b[i].h - b[i].l
        is_inside = b[i].h <= b[i - 1].h and b[i].l >= b[i - 1].l
        is_nr4 = rng == min(b[j].h - b[j].l for j in range(i - 3, i + 1))
        if not (is_inside or is_nr4):
            continue
        if not _near_level(s, i, b[i].l, b[i].h, s.atr[i]):
            continue
        hi, lo = b[i].h, b[i].l
        for j in range(i + 1, min(i + 4, len(b))):
            if b[j].c > hi:
                fired += 1; yield j, 1; break
            if b[j].c < lo:
                fired += 1; yield j, -1; break


SETUPS = [
    dict(id='inside_nr4_at_level', name='Inside bar / NR4 at a session level', family='candlestick',
         detect=inside_nr4_at_level,
         rules="An inside bar or an NR4 bar (narrowest of itself and the prior 3) within 0.25 ATR of VWAP or "
               "yesterday's high/low marks compression at a level. The first of the next 3 bars whose close "
               "breaks that bar's own high/low leans with the breakout, before 15:00."),
]
