"""Kalman-filtered price crossing session VWAP, 5-minute session bars.
Added 2026-10-14 by volume-vwap-analyst via WebSearch (TradingView "Kalman VWAP Filter" / "Rolling VWAP with Optional
Kalman Filter" descriptions: the gap between a Kalman-smoothed price and VWAP is read as short-term imbalance; the
scripts publish no backtest and their process-noise suggestion for intraday is 0.1-0.2). The lab has no Kalman filter.
Parameters fixed BEFORE any P&L was seen: local-level Kalman filter on the typical price (h+l+c)/3, restarted each
session at the first bar, process/measurement noise ratio q = 0.15 (steady-state gain from P = P + q, K = P/(P+1),
P = (1-K)*P), no tuning of q.
Long at the close of the first bar between 10:00 and 14:30 ET where the Kalman line crosses from at-or-below VWAP to above
it and the close is above the Kalman line (mirror short). One per side per session.
"""


def kalman_vwap_cross(s):
    b = s.bars
    q = 0.15
    x = (b[0].h + b[0].l + b[0].c) / 3
    p = 1.0
    ks = [x]
    for i in range(1, len(b)):
        z = (b[i].h + b[i].l + b[i].c) / 3
        p = p + q
        g = p / (p + 1.0)
        x = x + g * (z - x)
        p = (1 - g) * p
        ks.append(x)
    done = {1: False, -1: False}
    for i in range(12, len(b)):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if not done[1] and ks[i - 1] <= s.vwap[i - 1] and ks[i] > s.vwap[i] and b[i].c > ks[i]:
            done[1] = True; yield i, 1
        elif not done[-1] and ks[i - 1] >= s.vwap[i - 1] and ks[i] < s.vwap[i] and b[i].c < ks[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='kalman_vwap_cross', name='Kalman-filtered price crossing VWAP', family='volume',
         detect=kalman_vwap_cross,
         rules="A local-level Kalman filter (noise ratio 0.15, restarted each session) of the 5-minute typical price "
               "crosses session VWAP from below (above) and the bar closes on the same side of the Kalman line, "
               "between 10:00 and 14:30. One signal per side per session; tested with and against."),
]
