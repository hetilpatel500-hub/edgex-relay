"""True Strength Index signal cross with VWAP agreement, 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (TradingView community TSI script: crossover of the TSI line over its
signal line is the buy/sell trigger, double EMA smoothing of momentum; that author uses 60/30/9 lengths, which are one
trader's choice with no intraday evidence). Parameters fixed BEFORE any P&L was seen: Blau's classic 25/13 smoothing
(TSI = 100 * EMA13(EMA25(dClose)) / EMA13(EMA25(|dClose|))), signal = EMA9 of TSI (the source's signal length). Long at the
close of the first bar between 10:30 and 14:30 ET where TSI crosses above its signal while TSI < 0 and the close is above
session VWAP (mirror for short with TSI > 0 and close below VWAP). One signal per session.
"""


def _ema(x, n):
    k = 2 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def tsi_signal_cross(s):
    b = s.bars
    d = [0.0] + [b[i].c - b[i - 1].c for i in range(1, len(b))]
    num = _ema(_ema(d, 25), 13)
    den = _ema(_ema([abs(v) for v in d], 25), 13)
    tsi = [100 * a / c if c else 0.0 for a, c in zip(num, den)]
    sig = _ema(tsi, 9)
    for i in range(40, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        up = tsi[i] > sig[i] and tsi[i - 1] <= sig[i - 1]
        dn = tsi[i] < sig[i] and tsi[i - 1] >= sig[i - 1]
        if up and tsi[i] < 0 and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if dn and tsi[i] > 0 and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='tsi_signal_cross', name='True Strength Index signal cross with VWAP', family='momentum',
         detect=tsi_signal_cross,
         rules="The True Strength Index is a double-smoothed measure of price momentum. Between 10:30 and 14:30, when "
               "it crosses above its 9-bar signal line while still below zero (a turn up from weakness) and price "
               "closes above VWAP, it leans long; the mirror (cross down while above zero, price under VWAP) leans "
               "short. One signal per session; tested with and against."),
]
