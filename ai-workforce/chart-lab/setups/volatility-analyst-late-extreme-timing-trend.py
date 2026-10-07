"""Extreme timing: the day's low was set early and the high was set late (or the mirror).
Added 2026-10-07 by volatility-analyst via the lab queue (when in the session the extremes print, read at noon;
distinct from failed_hod_break and vwap_held_higher_lows, which read levels, not the timing of the extremes).
Parameters fixed BEFORE any P&L was seen: at the bar starting 12:00 ET (minute 720), look at bars from the open
through that bar. Long if the session low printed in the first 30 minutes (start before 10:00) AND the session
high printed at or after 11:00 AND the close is above VWAP and within 0.5 ATR(5-min) of the session high.
Short is the mirror (high in the first 30 minutes, low at or after 11:00, close below VWAP, within 0.5 ATR of
the low). One per session.
"""


def late_extreme_timing_trend(s):
    b = s.bars
    pos = {x.m: i for i, x in enumerate(b)}
    if 720 not in pos:
        return
    i = pos[720]
    atr = s.atr[i]
    if not atr or i + 1 >= len(b):
        return
    seg = b[:i + 1]
    hi_i = max(range(len(seg)), key=lambda k: seg[k].h)
    lo_i = min(range(len(seg)), key=lambda k: seg[k].l)
    hi, lo, c = seg[hi_i].h, seg[lo_i].l, b[i].c
    if seg[lo_i].m < 600 and seg[hi_i].m >= 660 and c > s.vwap[i] and hi - c <= 0.5 * atr:
        yield i, 1
    elif seg[hi_i].m < 600 and seg[lo_i].m >= 660 and c < s.vwap[i] and c - lo <= 0.5 * atr:
        yield i, -1


SETUPS = [
    dict(id='late_extreme_timing_trend', name='Early low, late high (extreme timing) at noon', family='volatility',
         detect=late_extreme_timing_trend,
         rules="At 12:00 ET, if the session low printed in the first 30 minutes and the session high printed at "
               "or after 11:00, price is above VWAP and within 0.5 ATR of the high, it leans long; the mirror "
               "(early high, late low, below VWAP, near the low) leans short. One signal per session; tested "
               "with and against."),
]
