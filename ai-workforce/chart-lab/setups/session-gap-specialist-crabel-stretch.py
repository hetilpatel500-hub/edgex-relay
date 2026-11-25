"""Crabel opening-range "stretch" breakout.
Added 2026-09-28 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch (ungeracademy.com, tradersmastermind.com)
for Toby Crabel's stretch entry from "Day Trading with Short Term Price Patterns
and Opening Range Breakout" (1990). Distinct from orb15, which breaks the first
15-minute range: the stretch is a distance from the open, sized by how far the
prior sessions pushed against their own open.
"""


def _stretch(s, n=10):
    """Mean of min(open - low, high - open) over up to the last n chained prior
    sessions (needs at least 5). Only completed sessions, no look-ahead."""
    vals, p = [], s.prior
    while p is not None and len(vals) < n:
        vals.append(min(p.open - p.lo, p.hi - p.open))
        p = p.prior
    return sum(vals) / len(vals) if len(vals) >= 5 else None


def crabel_stretch(s):
    """A 5-minute close beyond the open plus (or minus) the stretch, between
    09:45 and 11:00, leans with the break. One signal per session, the first side."""
    st = _stretch(s)
    if not st or st <= 0:
        return
    b = s.bars
    for i in range(3, len(b)):
        if b[i].m >= 660:
            return
        if b[i].c > s.open + st:
            yield i, 1
            return
        if b[i].c < s.open - st:
            yield i, -1
            return


SETUPS = [
    dict(id='crabel_stretch', name='Crabel opening-range stretch breakout', family='opening range',
         detect=crabel_stretch,
         rules="Stretch = average over the last 10 sessions of the smaller of (open minus low) and (high "
               "minus open). A 5-minute close above the open plus the stretch, or below the open minus "
               "it, between 9:45 and 11:00 leans with the break. One signal per session."),
]
