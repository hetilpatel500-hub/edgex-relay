"""Key reversal bar at the session extreme.
Added 2026-09-29 by pattern-specialist: the queue's non-tape lines are all coded,
so this run used WebSearch (luxalgo.com key reversal concept, traderlion.com key
reversal bar guide) for a documented, untested idea. Distinct from climax_reversal
(needs 3x volume and a 2-ATR bar) and turtle_soup (prior-day extremes): this is a
plain outside bar that takes the day's running extreme and closes back through the
previous bar's far end.
"""


def key_reversal(s):
    """After 12 bars (the initial balance), a bar that makes a new session low, then
    closes above the previous bar's high, leans long; a bar that makes a new session
    high and closes below the previous bar's low leans short. Before 15:00, at most
    2 signals per session."""
    b = s.bars
    fired = 0
    lo, hi = min(x.l for x in b[:12]), max(x.h for x in b[:12])
    for i in range(12, len(b)):
        if b[i].m >= 900 or fired >= 2:
            return
        new_lo, new_hi = b[i].l < lo, b[i].h > hi
        d = None
        if new_lo and b[i].c > b[i - 1].h:
            d = 1
        elif new_hi and b[i].c < b[i - 1].l:
            d = -1
        lo, hi = min(lo, b[i].l), max(hi, b[i].h)
        if d:
            fired += 1
            yield i, d


SETUPS = [
    dict(id='key_reversal', name='Key reversal bar at the session extreme', family='candlestick', detect=key_reversal,
         rules="After the first hour, a bar that makes a new session low and closes above the previous bar's high "
               "leans long; a bar that makes a new session high and closes below the previous bar's low leans "
               "short. Before 15:00, at most two per session."),
]
