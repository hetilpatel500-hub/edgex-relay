"""Initial-balance break confirmed by cumulative close-location delta.
Added 2026-10-06 by volume-vwap-analyst (order-flow proxy from bars: volume x close location value,
the bar-based stand-in for footprint delta that the lab uses until tape/ holds 30+ sessions).
Idea: an IB break is more likely to follow through when buying (selling) pressure inside the
session agrees with the break. Parameters fixed BEFORE any P&L was seen.
"""


def ib_break_delta_confirm(s):
    """From 10:35 to 14:30, the first bar that closes beyond the IB extreme (high or low of the first
    12 bars) while the session's cumulative sum of volume x CLV (CLV = ((c-l)-(h-c))/(h-l)) and the
    sum over the last 6 bars both point the same way leans with the break. One signal per side."""
    b = s.bars
    cum = 0.0
    dl = []
    fired = set()
    for i, x in enumerate(b):
        rng = x.h - x.l
        d = x.v * (((x.c - x.l) - (x.h - x.c)) / rng) if rng > 0 else 0.0
        dl.append(d)
        cum += d
        if i < 12 or not (635 <= x.m <= 870) or not s.atr[i]:
            continue
        last6 = sum(dl[-6:])
        if 1 not in fired and x.c > s.ib_hi and cum > 0 and last6 > 0:
            fired.add(1)
            yield i, 1
        elif -1 not in fired and x.c < s.ib_lo and cum < 0 and last6 < 0:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='ib_break_delta_confirm', name='IB break confirmed by cumulative close-location delta', family='volume',
         detect=ib_break_delta_confirm,
         rules="Between 10:35 and 14:30, the first bar that closes beyond the initial-balance high (low) while "
               "the session's cumulative volume-weighted close-location delta and the last 6 bars' delta are both "
               "positive (negative) leans long (short) with the break. One signal per side per session."),
]
