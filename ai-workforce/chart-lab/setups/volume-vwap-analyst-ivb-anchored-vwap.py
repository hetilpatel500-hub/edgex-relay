"""VWAP anchored at the initial volume bar, first retest, 5-minute bars.
Added 2026-10-03 by volume-vwap-analyst: the queue's non-tape lines are coded, so this
run used WebSearch (luxalgo.com anchored-VWAP-as-level, daytradingtoolkit.com anchored
VWAP trend strategy) for an untested idea: anchor VWAP at the highest-volume bar of the
session's first 30 minutes (the initial volume bar) instead of the open or a swing.
Distinct from anchored_vwap (anchored at the session extreme) and session VWAP setups.
"""


def ivb_anchored_vwap(s):
    """AVWAP accumulates typical price x volume from the initial volume bar. From 10:00
    to 14:30, if the 3 prior bars closed on one side of it by at least 0.1 ATR, a bar
    that wicks to it (within 0.1 ATR) and closes back on that side leans away from it.
    One signal per side per session."""
    b = s.bars
    a = s.ivb_i
    fired = set()
    pv = vv = 0.0
    av = []
    for i, x in enumerate(b):
        if i >= a:
            pv += (x.h + x.l + x.c) / 3 * x.v
            vv += x.v
        av.append(pv / vv if i >= a and vv else None)
    for i in range(max(a + 4, 6), len(b)):
        if b[i].m >= 870:
            break
        if b[i].m < 600 or not s.atr[i] or av[i] is None:
            continue
        atr, w, x = s.atr[i], av[i], b[i]
        for d in (1, -1):
            if d in fired:
                continue
            side = all(d * (b[i - k].c - av[i - k]) > 0.1 * atr for k in (1, 2, 3) if av[i - k] is not None)
            touch = x.l <= w + 0.1 * atr if d == 1 else x.h >= w - 0.1 * atr
            hold = d * (x.c - w) > 0
            if side and touch and hold:
                fired.add(d)
                yield i, d


SETUPS = [
    dict(id='ivb_anchored_vwap', name='Initial-volume-bar anchored VWAP retest', family='volume/vwap',
         detect=ivb_anchored_vwap,
         rules="VWAP anchored at the heaviest 5-minute bar of the first 30 minutes. From 10:00 to 14:30, after "
               "3 closes at least 0.1 ATR on one side of it, a bar that wicks to it (within 0.1 ATR) and closes "
               "back on that side leans away from it; one per side per session."),
]
