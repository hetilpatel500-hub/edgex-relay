"""Volume Zone Oscillator (VZO) re-entry from an extreme, 5-minute bars.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (LuxAlgo and TradingView VZO descriptions: each bar's volume is
credited to buyers on an up close and to sellers on a down close, VZO = 100 * EMA(signed volume) / EMA(volume), bounded
-100..+100; +/-40 are the quoted overbought/oversold levels. The sources are indicator descriptions with daily-style
defaults and no intraday evidence). Untested intraday adaptation. Parameters fixed BEFORE any P&L was seen: n = 14,
long at the close of the first bar between 10:30 and 14:30 ET where VZO crosses back up through -40 (mirror: down
through +40 for short). No VWAP or candle filter. One signal per session.
"""


def _ema(x, n):
    k = 2 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def vzo_extreme_reentry(s):
    b = s.bars
    sv = [(x.v if x.c > b[i - 1].c else -x.v if x.c < b[i - 1].c else 0) if i else 0 for i, x in enumerate(b)]
    num, den = _ema(sv, 14), _ema([x.v for x in b], 14)
    vzo = [100 * a / d if d else 0 for a, d in zip(num, den)]
    for i in range(15, len(b) - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if vzo[i] > -40 and vzo[i - 1] <= -40:
            yield i, 1
            return
        if vzo[i] < 40 and vzo[i - 1] >= 40:
            yield i, -1
            return


SETUPS = [
    dict(id='vzo_extreme_reentry', name='Volume Zone Oscillator re-entry from +/-40', family='volume',
         detect=vzo_extreme_reentry,
         rules="Each 5-minute bar's volume counts as buying on an up close and selling on a down close; the Volume "
               "Zone Oscillator is the 14-bar smoothed signed volume as a percent of smoothed volume. Between 10:30 "
               "and 14:30 the first cross back up through -40 leans long and the first cross back down through +40 "
               "leans short. One signal per session; tested with and against."),
]
