"""Vortex Indicator (14) crossover with VWAP agreement.
Added 2026-10-02 by trend-moving-average-analyst: Botes and Siepman's Vortex
Indicator (VI+ / VI- cross), documented by TradingView, Capital.com and
StockSharp. Not yet in the lab. Rules fixed before any P&L was seen.
"""


def vortex_cross(s):
    """VI+ = sum over 14 bars of |high - prior low| / sum of true range;
    VI- = sum of |low - prior high| / sum of true range, built inside the
    session. VI+ crossing above VI- while the close is above VWAP leans long;
    VI- crossing above VI+ below VWAP leans short. 10:30 to 14:30 ET, at most
    2 signals per side per session."""
    b = s.bars
    n = 14
    vp, vm, tr = [0.0], [0.0], [b[0].h - b[0].l]
    for i in range(1, len(b)):
        vp.append(abs(b[i].h - b[i - 1].l))
        vm.append(abs(b[i].l - b[i - 1].h))
        tr.append(max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c)))
    vi = [None] * len(b)
    for i in range(n, len(b)):
        t = sum(tr[i - n + 1:i + 1])
        if t > 0:
            vi[i] = (sum(vp[i - n + 1:i + 1]) / t, sum(vm[i - n + 1:i + 1]) / t)
    cnt = {1: 0, -1: 0}
    for i in range(n + 1, len(b)):
        if b[i].m < 630 or b[i].m >= 870 or vi[i] is None or vi[i - 1] is None:
            continue
        up = vi[i][0] > vi[i][1] and vi[i - 1][0] <= vi[i - 1][1]
        dn = vi[i][1] > vi[i][0] and vi[i - 1][1] <= vi[i - 1][0]
        if up and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='vortex_cross_vwap', name='Vortex (14) cross with VWAP', family='trend',
         detect=vortex_cross,
         rules="Vortex Indicator on 14 five-minute bars: VI+ crossing above VI- with the close above VWAP "
               "leans long; VI- crossing above VI+ with the close below VWAP leans short. 10:30 to 14:30 ET, "
               "at most two signals per side per session."),
]
