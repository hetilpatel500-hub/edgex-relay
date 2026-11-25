"""Acceptance beyond yesterday's high / low on 5-minute bars.
Added 2026-10-01 by support-resistance-mapper: the "market accepts the new
price area" idea (pd_break_retest waits for a retest, pd_sweep fades a failed
break; this one trades sustained time beyond the level). Rules and parameters
were fixed before testing: 6 consecutive closes beyond the level, each with
the bar's low (high) not back through the level.
"""


def pd_acceptance(s):
    """Six consecutive 5-minute bars that close beyond yesterday's high (low)
    without any of them trading back through it. Signal on the sixth bar's
    close, 09:50-14:30, one per direction per session."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    for level, d in ((p.hi, 1), (p.lo, -1)):
        run = 0
        for i in range(1, len(b)):
            if b[i].m >= 870:
                break
            ok = d * (b[i].c - level) > 0 and d * ((b[i].l if d == 1 else b[i].h) - level) > 0
            run = run + 1 if ok else 0
            if run == 6:
                yield i, d
                break


SETUPS = [
    dict(id='pd_acceptance', name="Acceptance beyond yesterday's high/low", family='levels',
         detect=pd_acceptance,
         rules="Six 5-minute bars in a row that close beyond yesterday's high (low) without any bar "
               "trading back through it, before 14:30, leans in that direction: the market is "
               "accepting the new price area."),
]
