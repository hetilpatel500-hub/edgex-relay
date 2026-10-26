"""Schaff Trend Cycle (STC) crossing out of its 25 / 75 trigger zones.
Added 2026-10-10 by momentum-analyst via WebSearch (queue was fully coded; sources: LuxAlgo Schaff Trend Cycle
library entry -- trigger lines at 25 and 75, a cross up through 25 flags an emerging uptrend, a cross down
through 75 an emerging downtrend, warns it whipsaws in chop; StockSharp Color Schaff TRIX example).
The lab had no Schaff Trend Cycle setup. Rules fixed BEFORE any P&L was seen: MACD line = EMA12 - EMA26 of closes
(EMAs seeded from the session's first close, session only); stochastic of the MACD over 10 bars, smoothed 0.5,
stochastic of that over 10 bars, smoothed 0.5 = STC (0-100). Signals only after 30 bars (warm-up), 10:00-14:30 ET,
at most one per side per session.
"""


def _ema(x, n):
    k = 2.0 / (n + 1)
    out = [x[0]]
    for v in x[1:]:
        out.append(out[-1] + k * (v - out[-1]))
    return out


def _stoch_smooth(x, n):
    out = []
    for i in range(len(x)):
        w = x[max(0, i - n + 1):i + 1]
        lo, hi = min(w), max(w)
        raw = 100.0 * (x[i] - lo) / (hi - lo) if hi > lo else (out[-1] if out else 50.0)
        out.append(raw if not out else out[-1] + 0.5 * (raw - out[-1]))
    return out


def schaff_trend_cycle(s):
    b = s.bars
    if len(b) < 40:
        return
    c = [x.c for x in b]
    e1, e2 = _ema(c, 12), _ema(c, 26)
    macd = [a - z for a, z in zip(e1, e2)]
    stc = _stoch_smooth(_stoch_smooth(macd, 10), 10)
    up_done = dn_done = False
    for i in range(30, len(b)):
        if b[i].m >= 870:
            return
        if b[i].m < 600:
            continue
        if not up_done and stc[i - 1] < 25 <= stc[i]:
            up_done = True; yield i, 1
        elif not dn_done and stc[i - 1] > 75 >= stc[i]:
            dn_done = True; yield i, -1


SETUPS = [
    dict(id='schaff_trend_cycle', name='Schaff Trend Cycle leaving its trigger zones', family='momentum',
         detect=schaff_trend_cycle,
         rules="The Schaff Trend Cycle (MACD 12/26 run through two 10-bar stochastic passes, smoothed 0.5) "
               "closes back up through 25 (leans long) or back down through 75 (leans short). Only after 30 "
               "bars of the session, 10:00-14:30 ET, one signal per side per session; tested with and against."),
]
