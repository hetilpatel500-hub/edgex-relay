"""Swing trendline break and first retest, 5-minute session bars.
Added 2026-10-14 by pattern-specialist via WebSearch (Tradezella break-and-retest playbook: enter on the retest after a
confirmation candle, not on the break; KedArc Quant TradingView trendline-breakout script: pivot-based trendline, close
beyond the line, retest valid within an ATR-scaled buffer; Babypips: a close beyond the line counts, not a wick). None of
these publish a backtest, and the lab has no pivot-trendline detector.
Parameters fixed BEFORE any P&L was seen: pivots need 3 bars each side (confirmed 3 bars late, so no look-ahead); the line
runs through the two most recent confirmed pivot highs (lows) that are at least 6 bars apart and lower (higher) than the
earlier one; retest buffer 0.5 x ATR; no tuning.
Break: a close beyond the line value at that bar by more than 0.25 x ATR. Retest: within the next 8 bars, a bar whose low
(high) reaches back within the buffer of the line and closes back on the breakout side; signal at that close. 10:00-15:00 ET.
One signal per side per session. Long = break up through a falling line.
"""


def _line(piv, i, kind):
    # two latest confirmed pivots with the right slope, >= 6 bars apart
    if len(piv) < 2:
        return None
    (i1, p1), (i2, p2) = piv[-2], piv[-1]
    if i2 - i1 < 6:
        return None
    if kind == 'hi' and p2 >= p1:
        return None
    if kind == 'lo' and p2 <= p1:
        return None
    sl = (p2 - p1) / (i2 - i1)
    return lambda j: p2 + sl * (j - i2)


def trendline_break_retest(s):
    b = s.bars
    n = len(b)
    L = 3
    done = {1: False, -1: False}
    for side in (1, -1):
        kind = 'hi' if side == 1 else 'lo'
        piv = []
        broke = None   # (bar index, line fn)
        for i in range(L, n):
            # confirm pivot at i-L using bars up to i
            k = i - L
            if k >= L:
                if kind == 'hi':
                    if all(b[k].h > b[k - j].h for j in range(1, L + 1)) and all(b[k].h >= b[k + j].h for j in range(1, L + 1)):
                        piv.append((k, b[k].h))
                else:
                    if all(b[k].l < b[k - j].l for j in range(1, L + 1)) and all(b[k].l <= b[k + j].l for j in range(1, L + 1)):
                        piv.append((k, b[k].l))
            if done[side] or b[i].m < 600 or b[i].m + 5 > 900:
                continue
            a = s.atr[i]
            if broke is None:
                f = _line(piv, i, kind)
                if f and i - piv[-1][0] <= 30:
                    v = f(i)
                    if (side == 1 and b[i].c > v + 0.25 * a) or (side == -1 and b[i].c < v - 0.25 * a):
                        broke = (i, f)
            else:
                bi, f = broke
                v = f(i)
                if i - bi > 8:
                    broke = None
                    continue
                if i == bi:
                    continue
                if side == 1:
                    if b[i].c < v - 0.25 * a:
                        broke = None
                    elif b[i].l <= v + 0.5 * a and b[i].c > v:
                        done[side] = True; yield i, 1
                else:
                    if b[i].c > v + 0.25 * a:
                        broke = None
                    elif b[i].h >= v - 0.5 * a and b[i].c < v:
                        done[side] = True; yield i, -1


SETUPS = [
    dict(id='trendline_break_retest', name='Swing trendline break and first retest', family='pattern',
         detect=trendline_break_retest,
         rules="Draw a line through the last two swing highs (3 bars each side, at least 6 bars apart, the later one lower). "
               "When a bar closes more than a quarter ATR above it, wait up to 8 bars for a bar that dips back to within half an "
               "ATR of the line and closes back above it; that close is the signal (mirror for a rising line under swing lows). "
               "10:00-15:00, one per side per session; tested with and against."),
]
