"""Wilder RSI(14) failure swing, 5-minute session bars.
Added 2026-10-14 by macd-divergence-analyst via WebSearch (LuxAlgo RSI Failure Swing library, therighttrader RSI guide):
Wilder's failure swing is read on the RSI line itself, not on price. Bullish: RSI falls below 30, rebounds above 30 to
a fail point (interim peak), pulls back without making a new low or going back under 30, then breaks the fail point.
Mirror above 70 for shorts. The lab has RSI(2) extremes, RSI-of-VWAP re-entries and RSI divergence, but not this
four-step swing. Parameters fixed BEFORE any P&L was seen: RSI(14) with Wilder smoothing, restarted each session
(first value at bar 14); signals 10:45 to 14:30 ET; one per side per session.
"""


def rsi_failure_swing(s):
    b = s.bars
    n = len(b)
    if n < 16:
        return
    rsi = [None] * n
    ag = al = 0.0
    for i in range(1, n):
        ch = b[i].c - b[i - 1].c
        g, l = max(ch, 0.0), max(-ch, 0.0)
        if i <= 14:
            ag += g / 14; al += l / 14
        else:
            ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14
        if i >= 14:
            rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    # state per side: 0 idle, 1 saw extreme, 2 rebounded (tracking fail point), armed once pullback holds
    st = {1: 0, -1: 0}
    low = {1: 0.0, -1: 0.0}     # extreme RSI reached
    fail = {1: 0.0, -1: 0.0}    # fail point (interim peak for longs, interim trough for shorts)
    done = {1: False, -1: False}
    for i in range(14, n):
        r = rsi[i]
        # long side
        if st[1] == 0:
            if r < 30:
                st[1], low[1] = 1, r
        elif st[1] == 1:
            low[1] = min(low[1], r)
            if r >= 30:
                st[1], fail[1] = 2, r
        elif st[1] == 2:
            if r < low[1] or r < 30:
                st[1] = 1 if r < 30 else 0
                low[1] = min(low[1], r) if st[1] == 1 else 0.0
            elif r > fail[1]:
                if b[i].m >= 645 and b[i].m + 5 <= 870 and not done[1] and r > fail[1] and fail[1] > 0 and _pulled(rsi, i, fail[1]):
                    done[1] = True; yield i, 1
                    st[1] = 0
                else:
                    fail[1] = r
        # short side
        if st[-1] == 0:
            if r > 70:
                st[-1], low[-1] = 1, r
        elif st[-1] == 1:
            low[-1] = max(low[-1], r)
            if r <= 70:
                st[-1], fail[-1] = 2, r
        elif st[-1] == 2:
            if r > low[-1] or r > 70:
                st[-1] = 1 if r > 70 else 0
                low[-1] = max(low[-1], r) if st[-1] == 1 else 0.0
            elif r < fail[-1]:
                if b[i].m >= 645 and b[i].m + 5 <= 870 and not done[-1] and fail[-1] > 0 and _pulled(rsi, i, fail[-1], short=True):
                    done[-1] = True; yield i, -1
                    st[-1] = 0
                else:
                    fail[-1] = r


def _pulled(rsi, i, fail, short=False):
    """True when RSI actually pulled back from the fail point before this break (previous bar below it for longs)."""
    p = rsi[i - 1]
    return p is not None and (p > fail if short else p < fail)


SETUPS = [
    dict(id='rsi_failure_swing', name='Wilder RSI(14) failure swing', family='momentum',
         detect=rsi_failure_swing,
         rules="RSI(14) drops under 30, rebounds above 30 to a peak, pulls back without a new low or a re-entry under 30, "
               "then closes above that peak (mirror: over 70, trough, higher high not made, breaks the trough). RSI is "
               "restarted each session; signals 10:45 to 14:30; one per side per session; tested with and against."),
]
