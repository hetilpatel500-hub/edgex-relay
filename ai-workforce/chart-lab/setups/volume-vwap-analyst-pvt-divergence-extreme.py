"""Price Volume Trend divergence at a new session extreme.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (luxalgo.com Price Volume Trend concept page,
onetradejournal.com PVT worked example: both call price making a high on weaker PVT the most useful PVT signal and
warn that open bursts dominate the intraday percentage term). Distinct from obv_divergence_extreme: PVT scales
volume by the bar's % price change instead of counting whole bars. Rules fixed BEFORE any P&L was seen: PVT starts
at 0 each session and adds volume x (close/prev close - 1) per bar. Signal at the close of a bar that sets a new
session closing high (low) at least 6 bars after the previous closing high (low), after bar 18 and before 14:30 ET,
while PVT sits below (above) its value at that previous extreme. One signal per session.
"""


def pvt_divergence_extreme(s):
    b = s.bars
    pvt = 0.0
    hi_c = lo_c = None
    hi_i = lo_i = 0
    hi_p = lo_p = 0.0
    for i, x in enumerate(b):
        if i > 0 and b[i - 1].c:
            pvt += x.v * (x.c / b[i - 1].c - 1)
        if hi_c is None:
            hi_c = lo_c = x.c
            hi_i = lo_i = i
            hi_p = lo_p = pvt
            continue
        late = i >= 18 and x.m <= 870 and i + 1 < len(b)
        if x.c > hi_c:
            if late and i - hi_i >= 6 and pvt < hi_p:
                yield i, -1
                return
            hi_c, hi_i, hi_p = x.c, i, pvt
        if x.c < lo_c:
            if late and i - lo_i >= 6 and pvt > lo_p:
                yield i, 1
                return
            lo_c, lo_i, lo_p = x.c, i, pvt


SETUPS = [
    dict(id='pvt_divergence_extreme', name='Price Volume Trend divergence at a new session extreme', family='volume',
         detect=pvt_divergence_extreme,
         rules="The session's Price Volume Trend (running sum of volume times each 5-minute bar's % price change) "
               "fails to confirm a new session closing high (it sits below its value at the previous high, which was "
               "at least 6 bars earlier) leans short; a new closing low on a PVT above its value at the previous low "
               "leans long. After 18 bars, before 14:30 ET, one signal a session; tested with and against."),
]
