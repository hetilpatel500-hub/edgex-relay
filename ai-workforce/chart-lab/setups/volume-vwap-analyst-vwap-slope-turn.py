"""Midday VWAP slope turn: session VWAP drifted one way through the morning, then turned the other way.
Added 2026-10-07 by volume-vwap-analyst via the lab queue (VWAP slope as a trend-of-value read; distinct from
vwap_cross_range_fade, vwap_break_retest and vwap_band_walk, none of which read VWAP's own direction change).
Parameters fixed BEFORE any P&L was seen: early slope = VWAP at the 11:30 bar minus VWAP at the 10:30 bar
(bars with start 10:30 and 11:30 ET); late slope = VWAP at the 13:00 bar minus VWAP at the 11:30 bar. The two
slopes have opposite signs, early slope magnitude at least 0.5 ATR(5-min) and late slope magnitude at least
0.25 ATR; signal at the close of the 13:00 bar only if that close is on the side of VWAP the late slope points
to (above if rising); direction is the late slope; one per session.
"""


def vwap_slope_turn(s):
    b = s.bars
    pos = {x.m: i for i, x in enumerate(b)}
    if not all(m in pos for m in (630, 690, 780)):
        return
    i0, i1, i2 = pos[630], pos[690], pos[780]
    atr = s.atr[i2]
    if not atr or i2 + 1 >= len(b):
        return
    early = s.vwap[i1] - s.vwap[i0]
    late = s.vwap[i2] - s.vwap[i1]
    if early * late >= 0 or abs(early) < 0.5 * atr or abs(late) < 0.25 * atr:
        return
    d = 1 if late > 0 else -1
    if (b[i2].c - s.vwap[i2]) * d > 0:
        yield i2, d


SETUPS = [
    dict(id='vwap_slope_turn', name='Midday VWAP slope turn', family='vwap',
         detect=vwap_slope_turn,
         rules="VWAP drifted one way from 10:30 to 11:30 (at least 0.5 ATR), then reversed from 11:30 to 13:00 "
               "(at least 0.25 ATR), and at 13:00 price is on the new side of VWAP. One signal per session, "
               "in the direction of the new VWAP slope; tested with and against."),
]
