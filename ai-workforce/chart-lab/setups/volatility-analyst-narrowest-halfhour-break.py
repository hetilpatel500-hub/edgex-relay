"""Narrowest half-hour of the day so far, then a break in the VWAP's direction.
Added 2026-10-07 by volatility-analyst, from a WebSearch run (intraday
volatility-contraction literature: the narrowest range bar of a window,
the "NR" idea of Toby Crabel, applied to half-hour blocks instead of days).
Distinct from nr7_orb and inside_nr4_at_level (daily NR days) and from
lunch_range_break (fixed 11:30-13:00 window).
Parameters fixed BEFORE any P&L was seen: split the session into 30-minute
blocks of 6 bars from 09:30. After a block closes, if it is block 3 or later,
its high-low range is the smallest of all blocks so far and under 0.8 of the
mean of the earlier blocks' ranges, then for the next 6 bars the first bar
that closes above the block high with the close above VWAP signals long, or
below the block low with the close below VWAP signals short. Signals only
before 14:30 ET. One per session.
"""


def narrowest_halfhour_break(s):
    b = s.bars
    n = len(b)
    rng = []
    for k in range(0, n // 6):
        blk = b[k * 6:k * 6 + 6]
        rng.append(max(x.h for x in blk) - min(x.l for x in blk))
        if k < 3:
            continue
        prev = rng[:-1]
        if rng[-1] > min(prev) or rng[-1] >= 0.8 * sum(prev) / len(prev):
            continue
        hi = max(x.h for x in blk)
        lo = min(x.l for x in blk)
        for i in range(k * 6 + 6, min(k * 6 + 12, n)):
            if b[i].m >= 870:
                return
            if b[i].c > hi and b[i].c > s.vwap[i]:
                yield i, 1
                return
            if b[i].c < lo and b[i].c < s.vwap[i]:
                yield i, -1
                return


SETUPS = [
    dict(id='narrowest_halfhour_break', name='Narrowest half-hour so far: break with VWAP', family='volatility',
         detect=narrowest_halfhour_break,
         rules="Cut the day into 30-minute blocks. When a block (the 4th or later) has the smallest range of the day "
               "so far and under 80% of the earlier blocks' average, watch the next half hour: the first close above "
               "that block's high while above VWAP leans long, the first close below its low while under VWAP leans "
               "short. Nothing after 14:30 ET. One signal per session; tested with and against."),
]
