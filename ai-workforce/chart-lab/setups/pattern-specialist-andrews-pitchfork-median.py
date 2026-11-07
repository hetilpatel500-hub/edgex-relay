"""Andrews pitchfork median-line pullback, 5-minute session bars.
Added 2026-10-14 by pattern-specialist via WebSearch (LuxAlgo and LightningChart pitchfork guides: three alternating
pivots define a median line, price tends to return to it and the parallels act as support/resistance; sources give no
5-minute rules and say pivot choice is subjective, so this fixes one mechanical choice). No backtest is published.
Parameters fixed BEFORE any P&L was seen: pivots need 3 bars each side (confirmed 3 bars late, no look-ahead); the fork uses
the last three confirmed alternating pivots (low, high, low for an up-fork; high, low, high for a down-fork), each at least
4 bars apart and the later same-type pivot beyond the earlier one (higher low / lower high). Median line runs from the first
pivot through the midpoint of the last two. Signal 10:00-15:00 ET: a bar whose low (high) reaches within 0.15 x ATR of the
median line and closes above (below) it and in the direction of the bar body. One signal per side per session. No tuning.
"""


def _pivots(b, i, L=3):
    out = []
    for k in range(L, i - L + 1):
        if all(b[k].h > b[k - j].h for j in range(1, L + 1)) and all(b[k].h >= b[k + j].h for j in range(1, L + 1)):
            out.append((k, 'h', b[k].h))
        elif all(b[k].l < b[k - j].l for j in range(1, L + 1)) and all(b[k].l <= b[k + j].l for j in range(1, L + 1)):
            out.append((k, 'l', b[k].l))
    return out


def pitchfork_median(s):
    b = s.bars
    n = len(b)
    done = {1: False, -1: False}
    for i in range(10, n):
        if b[i].m < 600 or b[i].m + 5 > 900 or all(done.values()):
            continue
        a = s.atr[i]
        if not a:
            continue
        piv = _pivots(b, i)
        if len(piv) < 3:
            continue
        (i1, t1, p1), (i2, t2, p2), (i3, t3, p3) = piv[-3:]
        if i2 - i1 < 4 or i3 - i2 < 4 or i <= i3:
            continue
        for side, ts in ((1, ('l', 'h', 'l')), (-1, ('h', 'l', 'h'))):
            if done[side] or (t1, t2, t3) != ts:
                continue
            if side == 1 and not p3 > p1:
                continue
            if side == -1 and not p3 < p1:
                continue
            mid_i, mid_p = (i2 + i3) / 2.0, (p2 + p3) / 2.0
            sl = (mid_p - p1) / (mid_i - i1)
            v = p1 + sl * (i - i1)
            o, c = b[i].o, b[i].c
            if side == 1 and b[i].l <= v + 0.15 * a and c > v and c > o and b[i].l >= v - 0.5 * a:
                done[side] = True; yield i, 1
            elif side == -1 and b[i].h >= v - 0.15 * a and c < v and c < o and b[i].h <= v + 0.5 * a:
                done[side] = True; yield i, -1


SETUPS = [
    dict(id='andrews_pitchfork_median', name='Andrews pitchfork median-line pullback', family='pattern',
         detect=pitchfork_median,
         rules="From the last three alternating swing points (3 bars each side, 4+ bars apart; low-high-low with a higher "
               "second low, or high-low-high with a lower second high) draw the median line from the first point through the "
               "midpoint of the other two. A bar that dips to within 0.15 ATR of it and closes back above it as an up bar "
               "(mirror for a down fork) is the signal. 10:00-15:00, one per side per session; tested with and against."),
]
