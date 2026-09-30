"""Wide-range bar follow-through (ATR expansion bar closing at its extreme).
Added 2026-09-30 by volatility-analyst via WebSearch (wide range bar / ATR
expansion momentum guides). Parameters (2.0x ATR, close in outer 20%, 10:00-14:30,
one per day) were fixed before any P&L was seen.
"""


def wide_range_bar(s):
    """The first 5-minute bar between 10:00 and 14:30 whose range is at least
    2.0x the ATR carried into it and whose close sits in the outer 20% of that
    range leans with the bar's direction. One per day."""
    b = s.bars
    for i in range(1, len(b)):
        m = b[i].m
        if m < 600 or m + 5 > 870:
            continue
        rng = b[i].h - b[i].l
        if rng <= 0 or rng < 2.0 * s.atr[i - 1]:
            continue
        loc = (b[i].c - b[i].l) / rng
        if loc >= 0.8:
            yield i, 1
            return
        if loc <= 0.2:
            yield i, -1
            return


SETUPS = [
    dict(id='wide_range_bar', name='Wide-range bar follow-through', family='volatility',
         detect=wide_range_bar,
         rules="Between 10:00 and 14:30, the first 5-minute bar whose high-to-low range is at least 2x the usual "
               "5-minute ATR and that closes in the top (or bottom) fifth of its range leans with that direction. "
               "One per day."),
]
