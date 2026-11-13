"""VWAP side persistence into 11:00: a one-sided morning relative to VWAP.
Added 2026-10-07 by volume-vwap-analyst via the lab queue (VWAP family; distinct from vwap_held_structure,
vwap_first_hour_hold and vwap_band_walk, which key on swing structure, one-hour hold or band touches, not on the
share of bars spent on one side).
Parameters fixed BEFORE any P&L was seen: from the second bar of the day (09:35) to the first bar starting at or
after 11:00 ET, at least 90% of closes sit on one side of session VWAP and the VWAP itself has moved in that
direction over the last 6 bars. One signal per session, at that bar's close; direction is the persistent side.
"""


def vwap_side_persistence(s):
    b = s.bars
    for i in range(len(b)):
        if b[i].m < 660:
            continue
        if b[i].m >= 700 or i < 12:
            return
        seg = range(1, i + 1)
        up = sum(1 for k in seg if b[k].c > s.vwap[k]) / len(seg)
        dn = sum(1 for k in seg if b[k].c < s.vwap[k]) / len(seg)
        slope = s.vwap[i] - s.vwap[i - 6]
        if up >= 0.9 and slope > 0:
            yield i, 1
        elif dn >= 0.9 and slope < 0:
            yield i, -1
        return


SETUPS = [
    dict(id='vwap_side_persistence', name='VWAP side persistence into 11:00', family='vwap',
         detect=vwap_side_persistence,
         rules="From 09:35 to the first bar at or after 11:00 ET, at least 90% of closes sit on one side of "
               "session VWAP and VWAP has moved the same way over the last 6 bars: lean with that side at the "
               "11:00 close (long above, short below). One signal per session; tested with and against."),
]
