"""Two-day composite POC: first-touch rejection when it differs from yesterday's POC.
Added 2026-10-07 by volume-vwap-analyst, from a WebSearch run (composite /
multi-day volume profile practice: a price traded heavily across two sessions
is a stronger acceptance level than one day's POC). Distinct from
prior_poc_rejection (one day) and prior_hvn_secondary (one day's second node).
Parameters fixed BEFORE any P&L was seen: composite POC from the last two
sessions' 5-minute bars (volume spread across each bar's range). Used only
when it sits at least 0.5 x the first bar's ATR
away from yesterday's POC, so it is a different level. Between 09:45 and
13:55 ET, with the previous bar fully on one side, the first bar that wicks
to the level and closes back on the approach side signals in the approach
direction. A close through the level first cancels the day. One per session.
"""
import core


def two_day_composite_poc(s):
    p = s.prior
    if p is None or p.prior is None:
        return
    poc2, _, _ = core.profile(p.prior.bars + p.bars)
    b = s.bars
    if abs(poc2 - p.poc) < 0.5 * s.atr[0]:
        return
    side = 0
    for i in range(3, len(b)):
        if b[i].m >= 835:
            return
        if side == 0:
            if b[i - 1].l > poc2:
                side = 1
            elif b[i - 1].h < poc2:
                side = -1
        if b[i].m < 585:
            continue
        if side == 1 and b[i].l <= poc2 and b[i].c > poc2:
            yield i, 1
            return
        if side == -1 and b[i].h >= poc2 and b[i].c < poc2:
            yield i, -1
            return
        if side == 1 and b[i].c < poc2 or side == -1 and b[i].c > poc2:
            return


SETUPS = [
    dict(id='two_day_composite_poc', name="Two-day composite POC first-touch rejection", family='volume profile',
         detect=two_day_composite_poc,
         rules="Build the volume profile of the last two sessions together and take its POC; skip the day when "
               "it sits within half an ATR of yesterday's own POC. Between 09:45 and 13:55 ET, when price "
               "approaches it from one side, the first bar that wicks to the level and closes back on the "
               "approach side leans in the direction of the approach. Cancelled if a bar closes through it "
               "first. One signal per session; tested with and against."),
]
