"""Pretty Good Oscillator (PGO) +/-3 breakout, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (Mark Johnson's PGO; backtrader and pandas-ta document it as
(close - SMA(n)) / ATR(n), with the original rule long when PGO rises above +3 and short when it falls below -3; other
sources read the same levels as overbought/oversold. The sources are indicator write-ups with no intraday evidence and
Johnson's original article was not found). Untested intraday adaptation. Parameters fixed BEFORE any P&L was seen:
n = 14, ATR as the simple mean of the true range over the same 14 bars, thresholds +/-3. Long at the close of the first
bar between 10:30 and 14:30 ET where PGO crosses up through +3 (mirror: down through -3 for short). No VWAP filter.
One signal per session.
"""


def pgo_breakout(s):
    b = s.bars
    n = 14
    tr = [b[0].h - b[0].l] + [max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c))
                              for i in range(1, len(b))]
    pgo = [None] * len(b)
    for i in range(n, len(b)):
        sma = sum(x.c for x in b[i - n + 1:i + 1]) / n
        atr = sum(tr[i - n + 1:i + 1]) / n
        pgo[i] = (b[i].c - sma) / atr if atr else 0
    for i in range(n + 1, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        if pgo[i] > 3 and pgo[i - 1] <= 3:
            yield i, 1
            return
        if pgo[i] < -3 and pgo[i - 1] >= -3:
            yield i, -1
            return


SETUPS = [
    dict(id='pgo_breakout', name='Pretty Good Oscillator +/-3 breakout', family='momentum',
         detect=pgo_breakout,
         rules="PGO is how far the close sits from its 14-bar average, measured in average true ranges. Between "
               "10:30 and 14:30 the first cross above +3 leans long and the first cross below -3 leans short "
               "(Mark Johnson's breakout rule). One signal per session; tested with and against."),
]
