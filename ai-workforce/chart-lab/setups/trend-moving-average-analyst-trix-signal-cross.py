"""TRIX signal-line cross against the zero line on 5-minute bars.
Added 2026-10-11 by trend-moving-average-analyst via WebSearch (Hutson's TRIX: 1-bar rate of change of a triple EMA,
with a 9-bar EMA signal line; sources: StockCharts ChartSchool, incrediblecharts, therighttrader, LuxAlgo). Common rule:
buy when TRIX is below zero and crosses up through its signal line, sell when above zero and crossing down; sources
say a cross in a trend marks the end of a retracement, and intraday guides suggest length 7-9 / signal 5-9. No source
gives a tested intraday record. Untested adaptation. Parameters fixed BEFORE any P&L was seen: TRIX length 9, signal
EMA 9, computed inside the session only, cross at a bar close between 10:30 and 14:30 ET (after 12 warm-up bars).
One signal per session. The lab tests it with and against.
"""


def _ema(x, n):
    k = 2.0 / (n + 1)
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def trix_cross(s):
    b = s.bars
    n = len(b)
    if n < 20:
        return
    e3 = _ema(_ema(_ema([x.c for x in b], 9), 9), 9)
    trix = [0.0] + [(e3[i] / e3[i - 1] - 1) * 100 for i in range(1, n)]
    sig = _ema(trix, 9)
    for i in range(12, n - 1):
        m = b[i].m
        if m < 630 or m > 870:
            continue
        if trix[i] < 0 and trix[i] > sig[i] and trix[i - 1] <= sig[i - 1]:
            yield i, 1
            return
        if trix[i] > 0 and trix[i] < sig[i] and trix[i - 1] >= sig[i - 1]:
            yield i, -1
            return


SETUPS = [
    dict(id='trix_signal_cross', name='TRIX signal-line cross against zero', family='trend',
         detect=trix_cross,
         rules="TRIX is the one-bar change of a triple-smoothed average of price (length 9), compared with its own "
               "9-bar average. Between 10:30 and 14:30, the first time TRIX is below zero and crosses up through its "
               "average leans long (a pullback ending); the first time it is above zero and crosses down leans short. "
               "One signal per session; tested with and against."),
]
