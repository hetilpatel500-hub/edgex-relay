"""Afternoon break of an undisturbed morning range.
Added 2026-10-07 by session-gap-specialist, from a WebSearch run on midday
behavior (midday consolidation then afternoon resolution). Distinct from
lunch_range_break (a fixed 11:30-13:00 box) and ib_break (the first hour).
Parameters fixed BEFORE any P&L was seen: the morning range is the high and
low of 09:30-11:00 (first 18 bars). If no bar between 11:00 and 13:30 closes
outside it, then the first bar from 13:30 to 14:30 ET that closes above the
morning high with the close above VWAP signals long, or below the morning low
with the close below VWAP signals short. One per session.
"""


def morning_range_pm_break(s):
    b = s.bars
    if len(b) < 50:
        return
    hi = max(x.h for x in b[:18])
    lo = min(x.l for x in b[:18])
    for i in range(18, len(b)):
        m = b[i].m
        if m > 870:
            break
        c = b[i].c
        if m < 810:
            if c > hi or c < lo:
                return
            continue
        if c > hi and c > s.vwap[i]:
            yield i, 1
            return
        if c < lo and c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='morning_range_pm_break', name='Afternoon break of an undisturbed morning range', family='session',
         detect=morning_range_pm_break,
         rules="If price closes inside the 09:30-11:00 range for the whole stretch to 13:30, then the first "
               "close between 13:30 and 14:30 ET beyond the morning high (above VWAP) leans long, or beyond "
               "the morning low (below VWAP) leans short."),
]
