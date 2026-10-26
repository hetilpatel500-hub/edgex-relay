"""Hoffman Inventory Retracement Bar (IRB) with the 8/20 EMA trend, 5-minute session bars.
Added 2026-10-14 by candlestick-specialist via the research queue (Rob Hoffman's inventory retracement bar: a bar that
probes against the trend and closes back with the probe retraced by at least 45% of its range). The lab has pin-bar and
wick-rejection tests but not the trend-gated 45% retracement rule. Parameters fixed BEFORE any P&L was seen:
EMA 8 and 20 of the close, restarted each session at the first bar; trend up when EMA8 > EMA20 and close > EMA20.
Bullish IRB: bar range at least 0.5 ATR (s.atr), low below the prior bar's low, and the lower wick (min(o,c) - l) is at
least 45% of the range, close above the open. Mirror for bears. Window 10:00-14:30 ET, one per side per session.
"""


def hoffman_irb(s):
    b = s.bars
    k8, k20 = 2 / 9, 2 / 21
    e8 = e20 = b[0].c
    ema8, ema20 = [e8], [e20]
    for i in range(1, len(b)):
        e8 += k8 * (b[i].c - e8)
        e20 += k20 * (b[i].c - e20)
        ema8.append(e8); ema20.append(e20)
    done = {1: False, -1: False}
    for i in range(12, len(b)):
        x = b[i]
        if x.m < 600 or x.m + 5 > 870:
            continue
        rng = x.h - x.l
        if rng <= 0 or rng < 0.5 * s.atr[i]:
            continue
        if (not done[1] and ema8[i] > ema20[i] and x.c > ema20[i] and x.l < b[i - 1].l
                and x.c > x.o and (min(x.o, x.c) - x.l) >= 0.45 * rng):
            done[1] = True; yield i, 1
        elif (not done[-1] and ema8[i] < ema20[i] and x.c < ema20[i] and x.h > b[i - 1].h
                and x.c < x.o and (x.h - max(x.o, x.c)) >= 0.45 * rng):
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='hoffman_irb', name='Hoffman inventory retracement bar in an 8/20 EMA trend', family='candlestick',
         detect=hoffman_irb,
         rules="With EMA8 above EMA20 and the close above EMA20, a bar at least half an ATR tall that undercuts the prior "
               "bar's low, closes green, and has a lower wick of 45% or more of its range leans long (mirror for "
               "shorts in a downtrend), between 10:00 and 14:30. One signal per side per session; tested with and against."),
]
