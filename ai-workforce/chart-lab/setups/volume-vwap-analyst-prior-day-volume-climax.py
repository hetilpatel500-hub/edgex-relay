"""Yesterday's volume climax closing at its extreme, confirmed by the first hour.
Added 2026-10-07 by volume-vwap-analyst via the lab's own volume work (climactic
volume at a range extreme: continuation or exhaustion). Thresholds (volume at
least 1.5x the mean of the 10 sessions before it, close in the outer 20% of the
day's range, decision at the 10:30 close) were fixed before any P&L was seen.
"""


def _vol(x):
    return sum(b.v for b in x.bars)


def prior_day_volume_climax(s):
    """Yesterday's volume was at least 1.5x the average of the ten sessions
    before it and it closed in the top (bottom) fifth of its range. At the 10:30
    bar close, if price is above (below) VWAP, mark the direction of yesterday's
    close. One signal per session; tested with and against."""
    p = s.prior
    if p is None or p.hi <= p.lo:
        return
    hist, q = [], p.prior
    while q is not None and len(hist) < 10:
        hist.append(_vol(q))
        q = q.prior
    if len(hist) < 10:
        return
    if _vol(p) < 1.5 * sum(hist) / len(hist):
        return
    b = s.bars
    i = 11
    if len(b) <= i or b[i].m != 625:
        return
    loc = (p.close - p.lo) / (p.hi - p.lo)
    c = b[i].c
    if loc >= 0.8 and c > s.vwap[i]:
        yield i, 1
    elif loc <= 0.2 and c < s.vwap[i]:
        yield i, -1


SETUPS = [
    dict(id='prior_day_volume_climax', name="Yesterday's volume climax at its extreme, first hour agrees",
         family='volume', detect=prior_day_volume_climax,
         rules="When yesterday's volume was at least 1.5x the average of the ten sessions before it and it "
               "closed in the top (bottom) fifth of its range, and at the 10:30 close price is above (below) "
               "VWAP, mark that direction. Tested with and against; one signal per session."),
]
