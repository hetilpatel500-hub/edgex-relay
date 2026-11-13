"""Kaufman Adaptive Moving Average (10,2,30) cross, only when the market is efficient (trending).
Added 2026-10-07 by trend-moving-average-analyst via WebSearch of Kaufman's adaptive moving average (KAMA) use as a
trend filter (the average flattens in chop and speeds up in trends, so a cross of price through it only counts
when the efficiency ratio says price is actually trending). Distinct from hull_ma_turn_vwap (slope turn of a
fixed-length average) and ema9_21_crossover.
Parameters fixed from Kaufman's published defaults BEFORE any P&L was seen: efficiency ratio over 10 five-minute
closes, fast constant 2/(2+1), slow constant 2/(30+1), smoothing = (ER*(fast-slow)+slow)^2. Signal: a bar closes
across KAMA with ER(10) >= 0.35 and on the same side of session VWAP; entries from 10:15 to 14:30, at most
2 signals per session (one each way).
"""


def kama_cross(s):
    b = s.bars
    n = 10
    c = [x.c for x in b]
    if len(c) < n + 3:
        return
    fast, slow = 2 / 3, 2 / 31
    k = [None] * len(c)
    k[n - 1] = c[n - 1]
    er = [None] * len(c)
    for i in range(n, len(c)):
        ch = abs(c[i] - c[i - n])
        vol = sum(abs(c[j] - c[j - 1]) for j in range(i - n + 1, i + 1))
        er[i] = ch / vol if vol else 0.0
        sc = (er[i] * (fast - slow) + slow) ** 2
        k[i] = k[i - 1] + sc * (c[i] - k[i - 1])
    seen = set()
    for i in range(n + 1, len(b)):
        if b[i].m < 615:
            continue
        if b[i].m >= 870:
            return
        if k[i - 1] is None or er[i] is None:
            continue
        if er[i] < 0.35:
            continue
        if c[i - 1] <= k[i - 1] and c[i] > k[i] and c[i] > s.vwap[i] and 1 not in seen:
            seen.add(1)
            yield i, 1
        elif c[i - 1] >= k[i - 1] and c[i] < k[i] and c[i] < s.vwap[i] and -1 not in seen:
            seen.add(-1)
            yield i, -1


SETUPS = [
    dict(id='kama_cross_efficiency', name='KAMA(10,2,30) cross in an efficient market with VWAP agreement',
         family='trend', detect=kama_cross,
         rules="A 5-minute bar closes across Kaufman's adaptive moving average (10,2,30) while the efficiency "
               "ratio over the last 10 closes is at least 0.35 and the close is on the same side of session VWAP: "
               "lean long on an up-cross above VWAP, short on a down-cross below it. From 10:15 to 14:30, one "
               "signal each way per session. Parameters are Kaufman's published defaults, fixed before testing. "
               "Tested with and against."),
]
