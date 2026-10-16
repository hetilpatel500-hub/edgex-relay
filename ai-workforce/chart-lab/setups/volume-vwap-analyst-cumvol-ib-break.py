"""Initial-balance break with a cumulative-volume surge, 5-minute bars.
Added 2026-10-14 by volume-vwap-analyst via WebSearch (time-of-day relative-volume write-ups, e.g. LuxAlgo's
"Relative Volume" note and a TradingView cumulative-volume-at-time script, compare session volume so far with the same
clock time on prior days; the lab's existing rvol filter is per bar, never cumulative). Numbers fixed BEFORE any P&L:
the first bar from 10:30 to 13:00 ET that closes beyond the initial-balance high (long) or low (short), when the
session's cumulative volume through that bar is at least 1.5x the average cumulative volume through the same bar of
the previous 10 sessions (at least 5 must exist; walked back through the session chain). One signal per side per
session. Everything is known at the signal bar's close.
"""


def _cum(s, i):
    return sum(x.v for x in s.bars[:i + 1])


def cumvol_ib_break(s):
    b = s.bars
    hist, p = [], s.prior
    while p is not None and len(hist) < 10:
        hist.append(p)
        p = p.prior
    if len(hist) < 5:
        return
    done = {1: False, -1: False}
    cum = 0.0
    for i, x in enumerate(b):
        cum += x.v
        if i < 12 or x.m < 630 or x.m + 5 > 780:
            continue
        for d in (1, -1):
            if done[d]:
                continue
            if (d == 1 and x.c > s.ib_hi) or (d == -1 and x.c < s.ib_lo):
                done[d] = True
                base = sum(_cum(h, i) for h in hist) / len(hist)
                if base > 0 and cum >= 1.5 * base:
                    yield i, d


SETUPS = [
    dict(id='cumvol_ib_break', name='Initial-balance break with cumulative-volume surge', family='volume',
         detect=cumvol_ib_break,
         rules="The first close beyond the initial-balance high (long) or low (short) between 10:30 and 13:00 ET, "
               "counted only if the session's cumulative volume so far is at least 1.5x the average cumulative "
               "volume at the same bar over the previous 10 sessions. One signal per side per session; tested "
               "with and against."),
]
