"""Trend that never touched VWAP from 10:30 to noon, read at noon.
Added 2026-10-06 by volume-vwap-analyst via VWAP-trend write-ups (one side of VWAP with no retest shows
one-sided inventory; the test is whether it carries into the afternoon). Distinct from vwap_band_walk (band
distance), afternoon_vwap_trend_pullback (needs a pullback) and trend_day_vote.
Parameters fixed BEFORE any P&L was seen: every 5-minute bar from 10:30 through 11:55 has its low above VWAP
(or its high below it) and the 11:55 close is at least 6 five-minute ATRs from the day's open on that side.
Signal at the 11:55 close (entry 12:00 open); one per session.
"""




def vwap_no_touch_noon(s):
    b = s.bars
    idx = [i for i, x in enumerate(b) if 630 <= x.m <= 715]
    if len(idx) < 14:
        return
    last = idx[-1]
    if b[last].m != 715 or not s.atr[last]:
        return
    if all(b[i].l > s.vwap[i] for i in idx) and b[last].c - b[0].o >= 6 * s.atr[last]:
        yield last, 1
    elif all(b[i].h < s.vwap[i] for i in idx) and b[0].o - b[last].c >= 6 * s.atr[last]:
        yield last, -1


SETUPS = [
    dict(id='vwap_no_touch_noon', name='Morning trend with no VWAP touch, read at noon', family='vwap',
         detect=vwap_no_touch_noon,
         rules="From 10:30 to 11:55 no 5-minute bar touches VWAP (all lows above it, or all highs below it) and "
               "the 11:55 close is at least 6 five-minute ATRs from the day's open on that side. Signal at the "
               "11:55 close, one per session; tested with and against."),
]
