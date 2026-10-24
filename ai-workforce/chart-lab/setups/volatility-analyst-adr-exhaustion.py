"""Average-daily-range exhaustion on 5-minute bars.
Added 2026-10-01 by volatility-analyst: the research queue was fully coded, so
this run used WebSearch (luxalgo.com Average Daily Range, scalperintel.com
daily range projections, themarketstructuretrader.com ADR reversals: once the
day's range has used about 100% of the average daily range, odds of a slowdown
or reversal at the extreme rise; sources also warn trends can run 2-3 ADRs).
Thresholds fixed before any P&L was seen. Distinct from range_midpoint_hold
(range centre) and wide_range_bar (single bar size).
"""


def adr_exhaustion(s):
    """Average daily range (ADR) = mean high-low of the previous 10 consecutive
    full sessions (at least 5 needed). When the developing session range
    (high - low) is at least 100% of ADR and a bar makes a new session high
    (low) but closes below (above) its open and in the lower (upper) half of its
    own range, signal against the extreme. One signal per side per session,
    10:30 to 15:00."""
    ranges, p = [], s.prior
    while p is not None and len(ranges) < 10:
        ranges.append(p.hi - p.lo)
        p = p.prior
    if len(ranges) < 5:
        return
    adr = sum(ranges) / len(ranges)
    b = s.bars
    hi, lo = b[0].h, b[0].l
    fired = set()
    for i in range(1, len(b)):
        x = b[i]
        if 630 <= x.m < 900 and hi - lo >= adr and x.h - x.l > 0:
            mid = (x.h + x.l) / 2
            if x.h > hi and x.c < x.o and x.c < mid and -1 not in fired:
                fired.add(-1)
                yield i, -1
            elif x.l < lo and x.c > x.o and x.c > mid and 1 not in fired:
                fired.add(1)
                yield i, 1
        hi, lo = max(hi, x.h), min(lo, x.l)


SETUPS = [
    dict(id='adr_exhaustion', name='Average daily range exhaustion', family='volatility', detect=adr_exhaustion,
         rules="When the day's range has reached the average of the last 10 days' ranges, a bar that makes a new "
               "day high but closes down in its lower half (or a new low closing up in its upper half) marks a "
               "possible exhaustion; tested against the extreme (fade) and with it. One per side per session, "
               "10:30 to 15:00."),
]
