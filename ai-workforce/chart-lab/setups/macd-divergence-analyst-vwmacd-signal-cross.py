"""Volume-weighted MACD (VWMACD) signal-line cross, 5-minute bars.
Added 2026-10-11 by macd-divergence-analyst via WebSearch (Optuma and LuxAlgo VWMACD pages: VWMACD = VWMA(12) - VWMA(26)
of close, signal = EMA9 of that line, a cross of the signal is the entry read; the sources are indicator descriptions with
daily-style 12/26/9 defaults and give no intraday evidence). Untested intraday adaptation. Parameters fixed BEFORE any
P&L was seen: Long at the close of the first bar between 10:30 and 14:30 ET where the VWMACD line crosses above its
signal line (mirror for short). No VWAP or candle filter. One signal per session.
"""


def _ema(x, n):
    k = 2 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def _vwma(b, n):
    out = []
    for i in range(len(b)):
        w = b[max(0, i - n + 1):i + 1]
        tv = sum(x.v for x in w)
        out.append(sum(x.c * x.v for x in w) / tv if tv else b[i].c)
    return out


def vwmacd_signal_cross(s):
    b = s.bars
    line = [f - sl for f, sl in zip(_vwma(b, 12), _vwma(b, 26))]
    sig = _ema(line, 9)
    for i in range(27, len(b) - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if line[i] > sig[i] and line[i - 1] <= sig[i - 1]:
            yield i, 1
            return
        if line[i] < sig[i] and line[i - 1] >= sig[i - 1]:
            yield i, -1
            return


SETUPS = [
    dict(id='vwmacd_signal_cross', name='Volume-weighted MACD signal-line cross', family='macd',
         detect=vwmacd_signal_cross,
         rules="The volume-weighted MACD is the 12-bar volume-weighted average price minus the 26-bar one, on "
               "5-minute closes, with a 9-bar signal line. Between 10:30 and 14:30 the first cross of the signal "
               "line upward leans long and the first cross downward leans short. One signal per session; tested "
               "with and against."),
]
