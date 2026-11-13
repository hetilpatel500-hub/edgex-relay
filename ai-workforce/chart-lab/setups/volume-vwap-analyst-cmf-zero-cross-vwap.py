"""Chaikin Money Flow(20) zero-line cross with VWAP agreement.
Added 2026-10-05 by volume-vwap-analyst via WebSearch: Chaikin Money Flow
(https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf,
https://howtotrade.com/indicators/chaikin-money-flow/). Distinct from clv_delta_divergence and mfi_extreme_cross.
Rules fixed BEFORE any P&L was seen: CMF = sum(money-flow volume over 20 bars) / sum(volume over 20 bars), money-flow
multiplier = ((C-L)-(H-C))/(H-L); window uses this session's bars only (first signal bar 20). The cross must clear
+/-0.05 (the weak-cross filter the sources suggest) and close must agree with session VWAP.
"""


def cmf_zero_cross_vwap(s):
    b = s.bars
    w = 20
    mfv = []
    for x in b:
        r = x.h - x.l
        mfv.append(((x.c - x.l) - (x.h - x.c)) / r * x.v if r > 0 else 0.0)
    cm = [None] * len(b)
    for i in range(w - 1, len(b)):
        v = sum(x.v for x in b[i - w + 1:i + 1])
        cm[i] = sum(mfv[i - w + 1:i + 1]) / v if v else 0.0
    fired = 0
    for i in range(w, len(b)):
        if b[i].m >= 900 or fired >= 2:
            break
        p, c = cm[i - 1], cm[i]
        if p <= 0 and c >= 0.05 and b[i].c > s.vwap[i]:
            fired += 1
            yield i, 1
        elif p >= 0 and c <= -0.05 and b[i].c < s.vwap[i]:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='cmf_zero_cross_vwap', name='Chaikin Money Flow zero cross + VWAP', family='volume', detect=cmf_zero_cross_vwap,
         rules="Chaikin Money Flow over the last 20 five-minute bars of the session crosses from at or below zero to "
               "+0.05 or more while price closes above VWAP leans long; from at or above zero to -0.05 or less while "
               "price closes below VWAP leans short, before 15:00. Tested with and against."),
]
