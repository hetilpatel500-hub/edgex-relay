"""Detrended Price Oscillator (20) zero cross with VWAP agreement, 5-minute bars.
Added 2026-10-14 by trend-moving-average-analyst (WebSearch 2026-10-14 for untested ideas; DPO is the classic
cycle-isolating oscillator, StockCharts ChartSchool "Detrended Price Oscillator"). Not in the lab yet.
Rules fixed BEFORE any P&L was seen: causal DPO(20) = close 10 bars ago minus today's SMA(20) of closes (no centred
average, so nothing looks ahead). Signal on the bar where DPO crosses zero from the other side, only if that bar's
close is on the same side of session VWAP as the cross, 10:00 to 15:00 ET, at most two a session. Direction = the cross.
"""


def dpo_vwap_cross(s):
    b = s.bars
    n = len(b)
    w, shift = 20, 10
    if n < w + 2:
        return
    closes = [x.c for x in b]
    fired = 0
    prev = None
    for i in range(w - 1, n):
        sma = sum(closes[i - w + 1:i + 1]) / w
        dpo = closes[i - shift] - sma
        p, prev = prev, dpo
        if p is None or b[i].m < 600 or b[i].m >= 900 or fired >= 2:
            continue
        if p <= 0 < dpo and b[i].c > s.vwap[i]:
            fired += 1; yield i, 1
        elif p >= 0 > dpo and b[i].c < s.vwap[i]:
            fired += 1; yield i, -1


SETUPS = [
    dict(id='dpo_vwap_cross', name='Detrended Price Oscillator (20) zero cross with VWAP', family='trend',
         detect=dpo_vwap_cross,
         rules="Causal DPO(20): the close ten bars ago minus today's 20-bar average close. When it crosses zero and "
               "the bar closes on the same side of session VWAP, lean that way, 10:00 to 15:00 ET, at most two a "
               "session. Tested with and against."),
]
