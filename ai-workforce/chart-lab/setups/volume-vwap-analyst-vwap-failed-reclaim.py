"""Failed VWAP reclaim: price pokes back through VWAP, cannot hold it, and closes back.
Added 2026-09-30 by volume-vwap-analyst via WebSearch (traderprofesional.com, "VWAP Trading
Strategies": "the failed reclaim: price pops above VWAP, cannot hold, and falls back under,
trapping the breakout buyers"). Parameters were fixed before any P&L was seen; the lab tests it
with and against.
"""


def vwap_failed_reclaim(s):
    """After at least 6 consecutive 5-minute closes on one side of VWAP, price closes on the other
    side for exactly 1 or 2 bars, then closes back on the original side. Lean toward the original
    side on that close (short after a failed reclaim from below, long after a failed loss from
    above). Between 10:00 and 14:30, one signal per session."""
    b = s.bars
    n = len(b)
    for i in range(8, n):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        for d in (1, -1):
            side = [d * (b[k].c - s.vwap[k]) for k in range(i + 1)]
            if side[i] <= 0:
                continue
            for w in (1, 2):  # bars spent on the far side
                if all(x < 0 for x in side[i - w:i]) and i - w - 6 >= 0 \
                        and all(x > 0 for x in side[i - w - 6:i - w]):
                    yield i, d
                    return


SETUPS = [
    dict(id='vwap_failed_reclaim', name='Failed VWAP reclaim (trapped breakout traders)',
         family='vwap', detect=vwap_failed_reclaim,
         rules="After six or more closes on one side of VWAP, price closes on the other side for only "
               "one or two bars, then closes back on the original side between 10:00 and 14:30. "
               "Lean toward the original side; tested with and against. One signal per session."),
]
