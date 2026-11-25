"""Trend Intensity Index (M.H. Pee) cross of 80 / 20 with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (Pee, Technical Analysis of Stocks & Commodities 2002:
TII = SD+ / (SD+ + SD-) * 100, where SD+ and SD- sum the up and down deviations of the last 30 closes from a 60-bar
SMA; above 80 = strong uptrend, below 20 = strong downtrend; sources: LinnSoft, LuxAlgo, OneTradeJournal).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: Pee's 60/30 does not fit a 78-bar session, so the
lab uses half of each, SMA 30 and a 15-bar deviation window, built inside the session (first signal bar 11:00 ET).
Long at the close of the first bar between 11:00 and 14:30 ET where TII crosses from at or below 80 to above it and
the close is above session VWAP (mirror for short at 20). At most one signal per side per session.
"""

MA, WIN = 30, 15


def tii_cross(s):
    b = s.bars
    c = [x.c for x in b]
    t = [None] * len(b)
    for i in range(MA - 1, len(b)):
        ma = sum(c[i - MA + 1:i + 1]) / MA
        up = dn = 0.0
        for k in range(i - WIN + 1, i + 1):
            d = c[k] - ma
            if d > 0:
                up += d
            else:
                dn -= d
        t[i] = 100 * up / (up + dn) if up + dn > 0 else 50.0
    cnt = {1: 0, -1: 0}
    for i in range(MA, len(b) - 1):
        if b[i].m < 660 or b[i].m > 870 or t[i - 1] is None:
            continue
        if t[i - 1] <= 80 < t[i] and c[i] > s.vwap[i] and cnt[1] < 1:
            cnt[1] += 1; yield i, 1
        elif t[i - 1] >= 20 > t[i] and c[i] < s.vwap[i] and cnt[-1] < 1:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='tii_cross_vwap', name='Trend Intensity Index 80/20 cross with VWAP', family='trend',
         detect=tii_cross,
         rules="Trend Intensity Index (Pee): the share of the last 15 closes' distance from the 30-bar average that "
               "lies above it, scaled 0-100 (half of Pee's 60/30 so it fits one session). Between 11:00 and 14:30, "
               "when it crosses up through 80 with the close above VWAP it leans long; crossing down through 20 with "
               "the close below VWAP leans short. One signal per side per session; tested with and against."),
]
