"""Williams %R(10) recovering from an extreme through its midline, with VWAP agreement.
Added 2026-10-10 by momentum-analyst via WebSearch (queue was fully coded; sources: daytradingz.com Williams %R day
trading guide, StoneX Williams %R learning center, TradingView community Williams %R momentum-burst script: 9-10 bar
period for 5-minute charts, act on the move back out of the extreme, cross of -50 as the trigger, pair with trend).
The lab had no Williams %R setup. Rules fixed BEFORE any P&L was seen: %R over 10 bars inside the session only;
%R was at or below -80 (at or above -20) within the last 12 bars, then crosses up through -50 (down through -50)
with the close on the same side of session VWAP; 10:00-14:30 ET; one signal per side per session.
"""


def williams_r_midline_vwap(s):
    b = s.bars
    n = 10
    r = [None] * len(b)
    for i in range(n - 1, len(b)):
        hh = max(x.h for x in b[i - n + 1:i + 1])
        ll = min(x.l for x in b[i - n + 1:i + 1])
        r[i] = -100.0 * (hh - b[i].c) / (hh - ll) if hh > ll else -50.0
    up_done = dn_done = False
    for i in range(n, len(b)):
        if b[i].m >= 870:
            return
        if b[i].m < 600 or r[i - 1] is None:
            continue
        recent = [x for x in r[max(n - 1, i - 12):i] if x is not None]
        if not recent:
            continue
        if not up_done and r[i - 1] < -50 <= r[i] and min(recent) <= -80 and b[i].c > s.vwap[i]:
            up_done = True; yield i, 1
        elif not dn_done and r[i - 1] > -50 >= r[i] and max(recent) >= -20 and b[i].c < s.vwap[i]:
            dn_done = True; yield i, -1


SETUPS = [
    dict(id='williams_r_midline_vwap', name='Williams %R recovering through its midline, with VWAP', family='momentum',
         detect=williams_r_midline_vwap,
         rules="The 10-bar Williams %R was at or below -80 within the last 12 bars and now closes back up through -50 "
               "with price above session VWAP (leans long); mirror: it was at or above -20 and closes down through "
               "-50 with price below VWAP (leans short). 10:00-14:30 ET, one signal per side per session; tested "
               "with and against."),
]
