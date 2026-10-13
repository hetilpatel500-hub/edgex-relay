"""Chande Intraday Momentum Index (14) re-entry from 30/70, 5-minute bars.
Added 2026-10-13 by momentum-analyst via WebSearch (Chande's IMI = SU / (SU + SD) * 100, where SU sums close-open on
bars that closed up and SD sums open-close on bars that closed down over n bars; sources name n = 14 and the 30/70
overbought/oversold levels). Not yet in the lab. Parameters fixed BEFORE any P&L was seen: n = 14 (built inside the
session, so the first value is the 14th bar), long when IMI crosses back above 30, short when it crosses back below 70,
10:30 to 14:30 ET, at most 2 signals per side per session.
"""


def imi_reentry(s):
    b = s.bars
    n = 14
    imi = [None] * len(b)
    for i in range(n - 1, len(b)):
        w = b[i - n + 1:i + 1]
        su = sum(x.c - x.o for x in w if x.c > x.o)
        sd = sum(x.o - x.c for x in w if x.c < x.o)
        imi[i] = 100.0 * su / (su + sd) if su + sd > 0 else 50.0
    cnt = {1: 0, -1: 0}
    for i in range(n, len(b)):
        if b[i].m < 630 or b[i].m >= 870 or imi[i] is None or imi[i - 1] is None:
            continue
        if imi[i - 1] < 30 <= imi[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif imi[i - 1] > 70 >= imi[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='imi14_reentry', name='Intraday Momentum Index (14) re-entry from 30/70', family='momentum',
         detect=imi_reentry,
         rules="Chande's Intraday Momentum Index over 14 five-minute bars (sum of up-bar bodies over up plus down bodies). "
               "IMI crossing back above 30 leans long; crossing back below 70 leans short. 10:30 to 14:30 ET, at most "
               "two signals per side per session; tested with and against."),
]
