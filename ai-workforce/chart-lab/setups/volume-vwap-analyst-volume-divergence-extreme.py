"""Volume divergence at a new session extreme.
Added 2026-09-30 by volume-vwap-analyst: volume/VWAP family, new idea found by
web search (effort vs result: a fresh high on much lighter volume than the
previous high suggests no real participation behind the push). All numbers were
fixed before any P&L was seen; everything is known at the signal bar's close.
"""


def volume_divergence_extreme(s):
    b = s.bars
    done = {1: False, -1: False}
    for i in range(12, len(b)):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        prev = b[:i]
        hj = max(range(len(prev)), key=lambda k: prev[k].h)
        lj = min(range(len(prev)), key=lambda k: prev[k].l)
        rng = b[i].h - b[i].l
        if rng <= 0:
            continue
        # new session high on < 60% of the prior high bar's volume, >= 6 bars later, closing in the lower half
        if (not done[-1] and b[i].h > prev[hj].h and i - hj >= 6 and b[i].v < 0.6 * prev[hj].v
                and b[i].c <= b[i].l + 0.5 * rng):
            done[-1] = True
            yield i, -1
        elif (not done[1] and b[i].l < prev[lj].l and i - lj >= 6 and b[i].v < 0.6 * prev[lj].v
                and b[i].c >= b[i].l + 0.5 * rng):
            done[1] = True
            yield i, 1


SETUPS = [
    dict(id='volume_divergence_extreme', name='Volume divergence at a new session high/low', family='volume',
         detect=volume_divergence_extreme,
         rules="A bar that makes a new session high (low) at least six bars after the previous extreme, on "
               "less than 60% of that earlier extreme bar's volume, and closes in the lower (upper) half of "
               "its range, between 10:30 and 14:30, leans against the push. Tested with and against; one "
               "signal per side per session."),
]
