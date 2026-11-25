"""Amihud price-impact spike, 5-minute bars.
Added 2026-10-15 by volume-vwap-analyst via WebSearch-free idea from the market-microstructure literature (Amihud 2002
illiquidity: absolute return per unit of volume; a bar that moves far on little volume has high price impact). The lab
has volume-spike and effort-vs-result setups, but none that ranks bars by move per share. Numbers fixed BEFORE any P&L
was seen: impact = |close - open| / volume of the bar. Signal on the close of the first bar between 10:00 and 15:00 ET
where impact is at least 3x the mean impact of the previous 20 bars (bars with zero volume skipped) AND the bar's body is
at least 0.8 ATR. Direction is the body's direction (long on an up body, short on a down body). One signal per side per
session. Everything is known at the signal bar's close. The lab tests it with and against the signal.
"""


def amihud_impact_spike(s):
    b = s.bars
    done = {1: False, -1: False}
    for i, x in enumerate(b):
        if i < 21 or x.m < 600 or x.m + 5 > 900 or x.v <= 0:
            continue
        prev = [abs(y.c - y.o) / y.v for y in b[i - 20:i] if y.v > 0]
        if len(prev) < 15:
            continue
        base = sum(prev) / len(prev)
        body = x.c - x.o
        d = 1 if body > 0 else -1
        if base <= 0 or done[d] or body == 0:
            continue
        if abs(body) / x.v >= 3 * base and abs(body) >= 0.8 * s.atr[i]:
            done[d] = True
            yield i, d


SETUPS = [
    dict(id='amihud_impact_spike', name='Amihud price-impact spike bar', family='volume',
         detect=amihud_impact_spike,
         rules="A bar between 10:00 and 15:00 ET whose body moved at least 3x as far per share traded as the "
               "average of the previous 20 bars, and whose body is at least 0.8 ATR. Signal on its close in the "
               "body's direction; one per side per session; tested with and against."),
]
