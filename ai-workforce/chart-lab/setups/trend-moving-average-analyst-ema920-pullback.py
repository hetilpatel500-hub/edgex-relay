"""EMA 9/20 pullback in a trending session, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst (next open line of the research queue).
Parameters fixed BEFORE any P&L was seen: EMAs seeded at the session's first close, trend = EMA9 above EMA20 above
VWAP (below for shorts) with EMA20 rising over the last 6 bars, pullback = a bar whose low reaches the EMA20 (high for
shorts) while the close stays on the trend side of EMA20, signal on that bar's close, 10:15 to 14:30 ET, one signal
per side per session. Everything is known at the signal bar's close.
"""


def ema920_pullback(s):
    b = s.bars
    e9, e20 = [], []
    for i, x in enumerate(b):
        if i == 0:
            e9.append(x.c); e20.append(x.c)
        else:
            e9.append(e9[-1] + (x.c - e9[-1]) * 2 / 10)
            e20.append(e20[-1] + (x.c - e20[-1]) * 2 / 21)
    done = {1: False, -1: False}
    for i in range(24, len(b)):
        if b[i].m < 615 or b[i].m >= 870:
            continue
        for d in (1, -1):
            if done[d]:
                continue
            if not (d * (e9[i] - e20[i]) > 0 and d * (e20[i] - s.vwap[i]) > 0 and d * (e20[i] - e20[i - 6]) > 0):
                continue
            touch = b[i].l <= e20[i] if d == 1 else b[i].h >= e20[i]
            if touch and d * (b[i].c - e20[i]) > 0 and d * (b[i].c - b[i].o) > 0:
                done[d] = True; yield i, d


SETUPS = [
    dict(id='ema920_pullback', name='EMA 9/20 pullback in a trending session', family='trend',
         detect=ema920_pullback,
         rules="EMA 9 above EMA 20 above VWAP with EMA 20 rising over six bars (reverse for shorts). A bar that "
               "dips into the EMA 20 but closes back above it as an up candle (mirror for shorts) is the signal, "
               "10:15 to 14:30 ET, one per side per session. Tested with and against."),
]
