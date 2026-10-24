"""First half-hour return leads the last half-hour (market intraday momentum).
Added 2026-09-29 by session-gap-specialist: the research queue's non-tape lines
are coded, so this run used WebSearch for Gao, Han, Li and Zhou, "Market
Intraday Momentum" (Journal of Financial Economics, 2018): on SPY and ten other
ETFs, the return from the previous close to 10:00 predicts the return of the
last half-hour. Distinct from power_hour, which reads VWAP and IB position.
"""


def first_half_hour_last(s):
    """At the close of the 15:25 bar, lean with the sign of the return from the
    prior session's close to the 10:00 close; the trade is the last half-hour
    (entry at the 15:30 open, flat at the close). One signal per session."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    first = last = None
    for i in range(len(b)):
        if b[i].m == 595:
            first = b[i].c
        if b[i].m == 925:
            last = i
    if first is None or last is None:
        return
    r = first - p.bars[-1].c
    if r > 0:
        yield last, 1
    elif r < 0:
        yield last, -1


SETUPS = [
    dict(id='first_half_hour_last', name='First half-hour leads the last half-hour', family='time of day',
         detect=first_half_hour_last,
         rules="If the return from yesterday's close to today's 10:00 close is positive, lean long into the "
               "last half-hour (entry 15:30, flat at the close); if negative, lean short."),
]
