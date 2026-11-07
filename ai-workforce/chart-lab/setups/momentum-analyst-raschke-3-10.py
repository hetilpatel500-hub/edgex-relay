"""Raschke 3-10 oscillator: signal-line cross in the direction of the zero line.
Added 2026-09-29 by momentum-analyst: the research queue's non-tape lines are
all coded, so this run used WebSearch (investingpaths.com, tradersmastermind.com)
for a documented, untested oscillator technique from Linda Raschke. Distinct
from stochastic_crossover and macd_vwap_flip: it uses the 3/10 simple average
of the median price and its 16-bar signal line, with no VWAP or level filter.
"""


def _sma(xs, n):
    return [None if i + 1 < n else sum(xs[i + 1 - n:i + 1]) / n for i in range(len(xs))]


def raschke_310(s):
    """osc = SMA3 - SMA10 of the median price; signal = SMA16 of osc. The bar where
    osc crosses above its signal while osc is above zero leans long; osc crossing
    below its signal while under zero leans short. One signal per side per
    session, 10:30 to 14:30."""
    b = s.bars
    med = [(x.h + x.l) / 2 for x in b]
    a, c = _sma(med, 3), _sma(med, 10)
    osc = [None if a[i] is None or c[i] is None else a[i] - c[i] for i in range(len(b))]
    sig = [None] * len(b)
    for i in range(len(b)):
        w = osc[max(0, i - 15):i + 1]
        if i >= 25 and None not in w and len(w) == 16:
            sig[i] = sum(w) / 16
    fired = set()
    for i in range(26, len(b)):
        if b[i].m >= 870:
            break
        if b[i].m < 630 or sig[i] is None or sig[i - 1] is None:
            continue
        if 1 not in fired and osc[i - 1] <= sig[i - 1] and osc[i] > sig[i] and osc[i] > 0:
            fired.add(1)
            yield i, 1
        elif -1 not in fired and osc[i - 1] >= sig[i - 1] and osc[i] < sig[i] and osc[i] < 0:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='raschke_310', name='Raschke 3-10 oscillator signal-line cross with the zero line', family='momentum',
         detect=raschke_310,
         rules="Oscillator = 3-bar average minus 10-bar average of the 5-minute median price; signal line = its "
               "16-bar average. Osc crossing above the signal line while above zero leans long; crossing below "
               "while under zero leans short. One signal per side per session, 10:30 to 14:30."),
]
