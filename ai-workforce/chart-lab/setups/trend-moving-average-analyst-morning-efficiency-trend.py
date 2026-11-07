"""Morning efficiency-ratio trend continuation.
Added 2026-10-02 by trend-moving-average-analyst after a WebSearch (Kaufman's Efficiency Ratio, "Smarter Trading",
1995; used as a trend-vs-chop regime filter, e.g. strategyquant.com/codebase/kaufmans-efficiency-ratio-ker):
the lab had not tested a regime filter built on the morning's directional efficiency. Rules and the 0.30
threshold were fixed BEFORE any P&L was seen.
"""


def morning_efficiency_trend(s):
    """Efficiency ratio of the 5-minute closes from the open to 11:30 ET = |net change| / sum of |bar-to-bar
    changes|. If it is at least 0.30, the first bar from 11:35 to 14:30 that makes a new session high (up
    morning) or new session low (down morning) leans with the morning; one signal per session."""
    b = s.bars
    n = 0
    while n < len(b) and b[n].m < 690:
        n += 1
    if n < 20 or n >= len(b):
        return
    path = abs(b[0].c - b[0].o) + sum(abs(b[k].c - b[k - 1].c) for k in range(1, n))
    if path <= 0:
        return
    net = b[n - 1].c - b[0].o
    if abs(net) / path < 0.30:
        return
    d = 1 if net > 0 else -1
    ext = max(x.h for x in b[:n]) if d > 0 else min(x.l for x in b[:n])
    for i in range(n, len(b)):
        if b[i].m >= 870:
            return
        if d > 0 and b[i].h > ext and b[i].c > ext:
            yield i, 1
            return
        if d < 0 and b[i].l < ext and b[i].c < ext:
            yield i, -1
            return


SETUPS = [
    dict(id='morning_efficiency_trend', name='Morning efficiency-ratio trend continuation', family='trend',
         detect=morning_efficiency_trend,
         rules="Efficiency ratio of the 5-minute closes from the open to 11:30 ET (net change divided by the sum of "
               "bar-to-bar moves). If it is 0.30 or more, the first bar before 14:30 that breaks and closes beyond "
               "the morning's high (up morning) or low (down morning) leans with the morning. One signal per session."),
]
