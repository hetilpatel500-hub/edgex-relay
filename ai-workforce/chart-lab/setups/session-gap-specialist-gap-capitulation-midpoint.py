"""Gap capitulation: after a large gap, the first-half-hour range midpoint reclaimed.
Added 2026-10-07 by session-gap-specialist, from a WebSearch run (generic
gap-reversal write-ups: a large gap that fails to extend in its first 30
minutes and then takes back the midpoint of that range is treated as
exhausted). Distinct from gap_first_bar_fail (first bar only) and
gap_vwap_hold (VWAP), which do not use the 30-minute range midpoint.
Parameters fixed BEFORE any P&L was seen: gap = open vs prior close >= 0.8 ATR
(daily-style ATR of the bar series at 10:00). Range R = bars 09:30-09:55
(first 6 bars). After 10:00 and before 12:00, the first close back through
R's midpoint against the gap (gap down -> close above midpoint) signals
a fade of the gap, provided the gap extreme (R's low for a gap down) was not
exceeded after the first 6 bars before the signal. One per session.
"""


def gap_capitulation_midpoint(s):
    p = s.prior
    b = s.bars
    if p is None or len(b) < 8:
        return
    gap = s.open - p.close
    if abs(gap) < 0.8 * s.atr[6]:
        return
    d = 1 if gap < 0 else -1
    R_hi, R_lo = max(x.h for x in b[:6]), min(x.l for x in b[:6])
    mid = (R_hi + R_lo) / 2
    for i in range(6, len(b)):
        if b[i].m >= 720:
            return
        if d == 1:
            if b[i].l < R_lo:
                return
            if b[i].c > mid:
                yield i, 1
                return
        else:
            if b[i].h > R_hi:
                return
            if b[i].c < mid:
                yield i, -1
                return


SETUPS = [
    dict(id='gap_capitulation_midpoint', name='Gap capitulation: first-30-minute midpoint reclaimed', family='gap',
         detect=gap_capitulation_midpoint,
         rules="When the open gaps at least 0.8 ATR from yesterday's close, take the range of the first six "
               "5-minute bars (09:30-09:55). Between 10:00 and 12:00, if price has not made a new extreme "
               "past that range in the gap's direction and a bar closes back through the range midpoint "
               "against the gap, it leans toward filling the gap (gap down: long). One signal per session; "
               "tested with and against."),
]
