"""Ulf Jensen "123" reversal with a 9-bar stochastic filter, 5-minute bars.
Added 2026-10-14 by pattern-specialist via WebSearch (a Kase DevStop search surfaced a public "123 Reversal" combo script
that cites Ulf Jensen's "How I Tripled My Money In The Futures Market" with a 9-period stochastic filter; the lab had
no test of it. The source gives the name and the 9-period stochastic, not exact rules, so the thresholds below are this
lab's own transfer, fixed BEFORE any P&L was seen). Rules: two consecutive lower closes (bars i-2 and i-1) followed by a
bar i that closes above bar i-1's close, while the 3-bar average of the 9-bar raw stochastic (session bars only) at i-1
was below 30 and is rising at i: long. Mirror (two higher closes, then a lower close, stochastic above 70 and falling):
short. 10:00 to 14:30 ET, one signal per side per session.
"""


def jensen_123(s):
    b = s.bars
    n = len(b)
    raw = []
    for i in range(n):
        if i < 8:
            raw.append(None)
            continue
        hi = max(x.h for x in b[i - 8:i + 1])
        lo = min(x.l for x in b[i - 8:i + 1])
        raw.append(100 * (b[i].c - lo) / (hi - lo) if hi > lo else 50.0)
    k = [None] * n
    for i in range(10, n):
        k[i] = sum(raw[i - 2:i + 1]) / 3
    seen = {1: False, -1: False}
    for i in range(13, n - 1):
        x = b[i]
        if x.m < 600 or x.m + 5 > 870:
            continue
        if (not seen[1] and b[i - 2].c < b[i - 3].c and b[i - 1].c < b[i - 2].c and x.c > b[i - 1].c
                and k[i - 1] < 30 and k[i] > k[i - 1]):
            seen[1] = True
            yield i, 1
        elif (not seen[-1] and b[i - 2].c > b[i - 3].c and b[i - 1].c > b[i - 2].c and x.c < b[i - 1].c
                and k[i - 1] > 70 and k[i] < k[i - 1]):
            seen[-1] = True
            yield i, -1


SETUPS = [
    dict(id='jensen_123_reversal', name='Jensen 123 reversal with 9-bar stochastic filter', family='pattern',
         detect=jensen_123,
         rules="Two consecutive lower closes then a bar that closes above the previous close, with the 9-bar stochastic "
               "(3-bar average, session bars) below 30 one bar earlier and rising: long. Mirror: two higher closes, "
               "then a lower close, stochastic above 70 and falling: short. 10:00 to 14:30 ET, one signal per side per "
               "session; tested with and against."),
]
