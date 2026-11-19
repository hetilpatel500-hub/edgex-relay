"""Tillson T3 (14, volume factor 0.7) close-cross after 5+ bars on the other side, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Tim Tillson, Technical Analysis of Stocks & Commodities,
Jan 1998; T3 = GD(GD(GD(price))) with GD(x) = EMA(x)*(1+v) - EMA(EMA(x))*v; community defaults length 14, v = 0.7;
a TradingView T3 strategy script enters when the close crosses the line after 5 or more bars on the other side).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: length 14, v 0.7, the six EMAs seeded at the session's first
close (built inside the session), cross must follow at least 5 closes on the other side, close also on the same side of
VWAP, 10:30 to 14:30 ET, at most 2 signals per side per session. Everything is known at the signal bar's close.
"""


def t3_cross(s):
    b = s.bars
    a = 2 / 15
    v = 0.7
    c1, c2, c3 = -(v ** 3), 3 * v * v + 3 * v ** 3, -6 * v * v - 3 * v - 3 * v ** 3
    c4 = 1 + 3 * v + v ** 3 + 3 * v * v
    e = [b[0].c] * 6
    t3 = [b[0].c]
    for i in range(1, len(b)):
        x = b[i].c
        for k in range(6):
            e[k] += (x - e[k]) * a
            x = e[k]
        t3.append(c1 * e[5] + c2 * e[4] + c3 * e[3] + c4 * e[2])
    cnt = {1: 0, -1: 0}
    for i in range(6, len(b)):
        if b[i].m < 630 or b[i].m >= 870:
            continue
        if b[i].c > t3[i] and all(b[i - j].c <= t3[i - j] for j in range(1, 6)) and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif b[i].c < t3[i] and all(b[i - j].c >= t3[i - j] for j in range(1, 6)) and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='t3_cross_vwap', name='Tillson T3 (14, 0.7) cross with VWAP', family='trend', detect=t3_cross,
         rules="Tillson T3 line (length 14, volume factor 0.7, seeded at the session's first close): a 5-minute close "
               "crossing above it after at least five closes below, with the close above VWAP, leans long; the mirror "
               "leans short. 10:30 to 14:30 ET, at most two signals per side per session; tested with and against."),
]
