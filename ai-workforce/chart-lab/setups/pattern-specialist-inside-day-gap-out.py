"""Inside day followed by an opening gap out of its range.
Added 2026-10-06 by pattern-specialist: classic inside-day (compression) pattern from price-action
write-ups, combined with the opening gap. Parameters fixed BEFORE any P&L was seen: yesterday's high
and low both inside the day before's range, today opens beyond yesterday's high (or below its low),
and the 10:00 close is still beyond that level; signal at the 10:00 close, once per session.
The lab tests it with and against.
"""


def inside_day_gap_out(s):
    p = s.prior
    b = s.bars
    if p is None or getattr(p, 'prior', None) is None or len(b) < 7:
        return
    pp = p.prior
    if not (p.hi < pp.hi and p.lo > pp.lo):
        return
    if s.open > p.hi and b[5].c > p.hi:
        yield 5, 1
    elif s.open < p.lo and b[5].c < p.lo:
        yield 5, -1


SETUPS = [
    dict(id='inside_day_gap_out', name='Inside day, then opening gap out of its range', family='pattern',
         detect=inside_day_gap_out,
         rules="Yesterday's whole range sat inside the day before's range. Today opens above yesterday's high "
               "(or below its low) and the 10:00 close is still beyond it: lean with the break at the 10:00 "
               "close, once per session."),
]
