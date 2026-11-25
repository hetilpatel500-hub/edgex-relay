"""Relative Vigor Index (Ehlers) crossing its signal line on the "wrong" side of zero, with VWAP agreement, 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (fbs.eu and capital.com RVI guides: crossover of RVI over its signal
line is the basic rule; zero-line filtering and 'works better in trends' are common conventions). Parameters fixed
BEFORE any P&L was seen: num = (CO + 2*CO[-1] + 2*CO[-2] + CO[-3]) / 6 where CO = close-open, den the same on high-low;
RVI = SMA10(num) / SMA10(den); signal = (RVI + 2*RVI[-1] + 2*RVI[-2] + RVI[-3]) / 6. Long at the close of the first bar
between 10:30 and 14:30 ET where RVI crosses above its signal while RVI < 0 and the close is above session VWAP
(mirror for short with RVI > 0, close below VWAP). One signal per session.
"""


def rvi_signal_cross(s):
    b = s.bars
    n = len(b)
    co = [x.c - x.o for x in b]
    hl = [x.h - x.l for x in b]
    sw = lambda a, i: (a[i] + 2 * a[i - 1] + 2 * a[i - 2] + a[i - 3]) / 6
    num = [None] * 3 + [sw(co, i) for i in range(3, n)]
    den = [None] * 3 + [sw(hl, i) for i in range(3, n)]
    rvi = [None] * n
    for i in range(12, n):
        d = sum(den[i - 9:i + 1])
        rvi[i] = sum(num[i - 9:i + 1]) / d if d else 0.0
    sig = [None] * n
    for i in range(15, n):
        sig[i] = sw(rvi, i)
    for i in range(16, n - 1):
        if sig[i] is None or sig[i - 1] is None or b[i].m < 630 or b[i].m > 870:
            continue
        up = rvi[i] > sig[i] and rvi[i - 1] <= sig[i - 1]
        dn = rvi[i] < sig[i] and rvi[i - 1] >= sig[i - 1]
        if up and rvi[i] < 0 and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if dn and rvi[i] > 0 and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='rvi_signal_cross', name='Relative Vigor Index signal cross with VWAP', family='momentum',
         detect=rvi_signal_cross,
         rules="The Relative Vigor Index measures whether bars tend to close near their highs (vigor up) or lows. "
               "Between 10:30 and 14:30, when it crosses above its signal line while still below zero (a turn "
               "up from weakness) and price closes above VWAP, it leans long; the mirror (cross down while above zero, "
               "price under VWAP) leans short. One signal per session; tested with and against."),
]
