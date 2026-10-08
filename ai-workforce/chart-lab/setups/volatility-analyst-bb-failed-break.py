"""Bollinger Band failed break (close back inside after a close outside).
Added 2026-09-30 by volatility-analyst via WebSearch (Bollinger band
mean-reversion guides). Parameters (20-bar SMA, 2.0 sd, entry 10:30-15:00, max 2
per day) were fixed before any P&L was seen.
"""
import math


def bb_failed_break(s):
    """A 5-minute bar that closes outside the 20-bar, 2-sd Bollinger Band,
    followed by a bar that closes back inside it, leans back toward the mean
    (short after an upper-band failure, long after a lower-band one). The
    band uses only closes within the session, so it starts at bar 20."""
    b = s.bars
    c = [x.c for x in b]
    fired = 0
    for i in range(21, len(b)):
        m = b[i].m
        if m < 630 or m + 5 > 900 or fired >= 2:
            continue
        def band(k):
            w = c[k - 19:k + 1]
            mu = sum(w) / 20
            sd = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
            return mu - 2 * sd, mu + 2 * sd
        lo0, hi0 = band(i - 1)
        lo1, hi1 = band(i)
        if c[i - 1] > hi0 and c[i] <= hi1:
            fired += 1
            yield i, -1
        elif c[i - 1] < lo0 and c[i] >= lo1:
            fired += 1
            yield i, 1


SETUPS = [
    dict(id='bb_failed_break', name='Bollinger Band failed break', family='volatility',
         detect=bb_failed_break,
         rules="When a 5-minute bar closes outside the 20-bar, 2-standard-deviation Bollinger Band and the next "
               "bar closes back inside it, the move leans back toward the middle band: short after an upper-band "
               "failure, long after a lower-band one. Between 10:30 and 15:00, at most twice a day."),
]
