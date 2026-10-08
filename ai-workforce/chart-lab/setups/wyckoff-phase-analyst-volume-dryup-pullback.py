"""Volume dry-up pullback in a one-sided session (Wyckoff effort vs result).
Added 2026-09-30 by wyckoff-phase-analyst: after a push away from VWAP, a
pullback on shrinking volume shows sellers (buyers) with little effort; the
first bar that closes back through the pullback's extreme is the entry.
All numbers were fixed before any P&L was seen; everything is known at the
signal bar's close.
"""


def volume_dryup_pullback(s):
    b = s.bars
    done = {1: False, -1: False}
    for i in range(12, len(b)):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        for d in (1, -1):
            if done[d] or d * (b[i].c - s.vwap[i]) <= 0:
                continue
            # pullback: exactly the last 3 bars before i moved against d, each lower volume
            pb = b[i - 3:i]
            if not all(d * (pb[k].c - pb[k - 1].c) < 0 for k in (1, 2)):
                continue
            if not (pb[0].v > pb[1].v > pb[2].v):
                continue
            # session has been one-sided: prior 6 bars before the pullback all closed on side d of VWAP
            if not all(d * (b[k].c - s.vwap[k]) > 0 for k in range(i - 9, i - 3)):
                continue
            # pullback stays above VWAP (still one-sided) and bar i closes through the pullback's extreme
            if any(d * (x.l - s.vwap[i - 3 + k]) <= 0 if d == 1 else d * (x.h - s.vwap[i - 3 + k]) <= 0 for k, x in enumerate(pb)):
                continue
            if d == 1 and b[i].c > max(x.h for x in pb) and b[i].c > b[i].o:
                done[d] = True; yield i, 1
            elif d == -1 and b[i].c < min(x.l for x in pb) and b[i].c < b[i].o:
                done[d] = True; yield i, -1


SETUPS = [
    dict(id='volume_dryup_pullback', name='Volume dry-up pullback above/below VWAP', family='wyckoff',
         detect=volume_dryup_pullback,
         rules="After six closes on one side of VWAP, a three-bar pullback against that side on steadily "
               "shrinking volume that never touches VWAP, then a bar that closes beyond the pullback's "
               "extreme in the trend direction, between 10:00 and 14:30. Tested with and against; one "
               "signal per side per session."),
]
