"""Heavy-volume morning, trade the direction at 10:30.
Added 2026-10-06 by volume-vwap-analyst: WebSearch run (documented idea: intraday
momentum follows demand/supply imbalance, so a session whose first hour trades
on much more volume than usual should keep its direction). Distinct from
orb5_volume_spike (one bar) and ib_break (price only).
Parameters fixed BEFORE any P&L was seen: average rvol of the first 12 bars
(9:30-10:30) at least 1.5, the signal is the 10:25 bar close (bar 11) when it
sits beyond the session open by 0.5 ATR(5-min) and on the same side of VWAP,
one signal per session.
"""


def heavy_volume_morning_trend(s):
    b = s.bars
    if len(b) < 14:
        return
    r = [x for x in s.rvol[:12] if x]
    if len(r) < 12 or sum(r) / 12 < 1.5:
        return
    i = 11
    atr = s.atr[i]
    if not atr:
        return
    c = b[i].c
    if c - s.open >= 0.5 * atr and c > s.vwap[i]:
        yield i, 1
    elif s.open - c >= 0.5 * atr and c < s.vwap[i]:
        yield i, -1


SETUPS = [
    dict(id='heavy_volume_morning_trend', name='Heavy-volume first hour, direction held at 10:30', family='volume',
         detect=heavy_volume_morning_trend,
         rules="When the first hour (9:30-10:30) trades at 1.5x or more of its usual volume, and price at 10:30 "
               "is at least 0.5 ATR beyond the open and on the same side of VWAP, lean with that direction. "
               "One trade per session."),
]
