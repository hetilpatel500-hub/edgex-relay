"""Hourly inside-bar breakout, built from the 5-minute bars.
Added 2026-10-01 by pattern-specialist: the research queue is fully coded, so
this run searched the web (no documented source gave a tested rule, so this is
the classic inside-bar idea moved to hourly candles) for an untested pattern
on a coarser timeframe than the 5-minute inside/NR4 already tested.
"""


def hourly_inside_break(s):
    """Clock hours (09:30-10:30, 10:30-11:30 ... in 12-bar blocks). When a
    completed hour's high-low range sits entirely inside the previous hour's
    range, the next 5-minute close beyond the inside hour's high (long) or
    low (short) is the signal. One signal per session, before 15:00."""
    b = s.bars
    n = len(b)
    for k in range(2, n // 12 + 1):
        a0, a1 = (k - 2) * 12, (k - 1) * 12   # previous hour
        c0, c1 = a1, k * 12                   # inside-candidate hour
        if c1 > n:
            return
        ph, pl = max(x.h for x in b[a0:a1]), min(x.l for x in b[a0:a1])
        ch, cl = max(x.h for x in b[c0:c1]), min(x.l for x in b[c0:c1])
        if not (ch < ph and cl > pl):
            continue
        for i in range(c1, n):
            if b[i].m >= 900:
                break
            if b[i].c > ch:
                yield i, 1
                return
            if b[i].c < cl:
                yield i, -1
                return


SETUPS = [
    dict(id='hourly_inside_break', name='Hourly inside-bar breakout', family='pattern',
         detect=hourly_inside_break,
         rules="When one hour's high and low both sit inside the prior hour's range, the first 5-minute close "
               "above that inside hour's high leans long and the first close below its low leans short, "
               "before 15:00."),
]
