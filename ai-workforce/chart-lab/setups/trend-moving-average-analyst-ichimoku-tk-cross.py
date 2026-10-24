"""Ichimoku Tenkan/Kijun cross with VWAP agreement.
Added 2026-10-03 by trend-moving-average-analyst: trend family, found by WebSearch
(daytradingz.com/ichimoku-cloud, daytradingtoolkit.com/strategies/ichimoku-cloud-day-trading-strategy:
TK cross read as momentum). The cloud itself needs 52+26 bars of history, more than one
5-minute session holds, so only the TK cross is tested, with session VWAP as the side filter.
Parameters (9, 26) are the published defaults, fixed before testing.
"""


def ichimoku_tk_cross(s):
    """Tenkan = midpoint of the last 9 bars' high/low, Kijun = midpoint of the last 26, both
    within the session. A cross of Tenkan over Kijun with the bar closing above session VWAP
    leans long; Tenkan under Kijun with a close below VWAP leans short. From bar 27 to 15:00,
    up to 2 per session."""
    b = s.bars

    def mid(i, n):
        return (max(x.h for x in b[i - n + 1:i + 1]) + min(x.l for x in b[i - n + 1:i + 1])) / 2

    fired = 0
    for i in range(26, len(b)):
        if b[i].m >= 900 or fired >= 2:
            return
        t0, k0, t1, k1 = mid(i - 1, 9), mid(i - 1, 26), mid(i, 9), mid(i, 26)
        if t0 <= k0 and t1 > k1 and b[i].c > s.vwap[i]:
            fired += 1
            yield i, 1
        elif t0 >= k0 and t1 < k1 and b[i].c < s.vwap[i]:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='ichimoku_tk_cross', name='Ichimoku TK cross with VWAP agreement', family='trend',
         detect=ichimoku_tk_cross,
         rules="Tenkan (9-bar midpoint) crosses above Kijun (26-bar midpoint) on 5-minute bars and the bar "
               "closes above session VWAP: lean long; crosses below and closes under VWAP: lean short. "
               "Cloud omitted (needs more history than one session). Up to 2 a session, before 15:00."),
]
