"""VWAP retest in the morning while price holds beyond the prior day's extreme.
Added 2026-10-06 by volume-vwap-analyst: the research queue's non-tape lines
are all coded, so this run used WebSearch (tradezella.com VWAP setups; a
TradingView "VWAP Retest + EMA9 Cross + Candle Pattern" script that trades only
the US morning and only above yesterday's high). Distinct from vwap_bounce
(no prior-day condition, trend-drift rule) and orb_prior_day_clear (an opening
range break, not a VWAP retest).
"""


def vwap_retest_prior_extreme(s):
    """Price has traded beyond yesterday's high (long) or low (short) by 9:45
    and VWAP sits beyond that level too. After 10:00 a bar whose wick tags VWAP
    (within 0.1 ATR) and closes back on the right side in its own direction
    leans with the break. One signal per side per session, before 12:30."""
    p = s.prior
    if not p:
        return
    b = s.bars
    fired = set()
    for i in range(3, len(b)):
        if b[i].m >= 750:
            break
        if b[i].m < 600:
            continue
        atr, v, x = s.atr[i], s.vwap[i], b[i]
        if not atr:
            continue
        up = max(y.h for y in b[:i]) > p.hi and v > p.hi
        dn = min(y.l for y in b[:i]) < p.lo and v < p.lo
        if up and 1 not in fired and x.l <= v + 0.1 * atr and x.c > v and x.c > x.o:
            fired.add(1)
            yield i, 1
        elif dn and -1 not in fired and x.h >= v - 0.1 * atr and x.c < v and x.c < x.o:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='vwap_retest_prior_extreme', name='VWAP retest beyond the prior day extreme', family='vwap',
         detect=vwap_retest_prior_extreme,
         rules="Once price has traded above yesterday's high and VWAP is above it too (mirror for lows), a "
               "bar after 10:00 that wicks to VWAP and closes back above it on an up bar leans long (down "
               "bar below VWAP leans short). One signal per side per session, before 12:30."),
]
