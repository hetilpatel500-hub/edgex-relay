"""Larry Williams' Oops reversal, on 5-minute bars.
Added 2026-09-29 by session-gap-specialist: the research queue is fully coded,
so this run used WebSearch (TradingView Oops strategy, Deepvue, TraderLion,
Unger Academy) for a documented untested gap idea. gap_fill fades any gap
toward the prior close; Oops is narrower: the open gaps beyond yesterday's
extreme against yesterday's candle, then price re-enters yesterday's range.
"""


def oops(s):
    """Down gap: open below yesterday's low and yesterday closed below its open.
    The first 5-minute close back above yesterday's low (before 11:30) leans long.
    Up gap: open above yesterday's high and yesterday closed above its open.
    The first close back below yesterday's high leans short. One signal per session."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    if s.open < p.lo and p.close < p.open:
        for i in range(len(b)):
            if b[i].m >= 690:
                return
            if b[i].c > p.lo:
                yield i, 1
                return
    elif s.open > p.hi and p.close > p.open:
        for i in range(len(b)):
            if b[i].m >= 690:
                return
            if b[i].c < p.hi:
                yield i, -1
                return


SETUPS = [
    dict(id='oops_reversal', name='Oops gap reversal (Larry Williams)', family='gaps', detect=oops,
         rules="Today opens below yesterday's low after a down day (or above yesterday's high after an up day). "
               "The first 5-minute close back inside yesterday's range, before 11:30 ET, leans back toward "
               "yesterday's range: long after a down gap, short after an up gap."),
]
