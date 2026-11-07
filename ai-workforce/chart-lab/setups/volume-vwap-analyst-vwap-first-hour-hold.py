"""Price holds one side of VWAP for the whole first hour, lean with it.
Added 2026-09-29 by volume-vwap-analyst: WebSearch found the documented rule of thumb that a
stock that opens above VWAP and holds above it through the first hour has set its directional
character (sahi.com, "ORB trading strategy explained"). Parameters were fixed before any P&L
was seen; the lab tests it with and against.
"""


def vwap_first_hour_hold(s):
    """At the 10:30 bar close (12 bars in): every one of the 12 closes has been on the same side
    of session VWAP, the open is on that side too, and the last close is at least 0.25 ATR from
    VWAP. Long if above, short if below. One signal per session."""
    b = s.bars
    if len(b) < 14 or b[11].m != 625:
        return
    atr = s.atr[11]
    if not atr:
        return
    for d in (1, -1):
        if all(d * (b[k].c - s.vwap[k]) > 0 for k in range(12)) and d * (s.open - s.vwap[0]) >= 0 \
                and d * (b[11].c - s.vwap[11]) >= 0.25 * atr:
            yield 11, d
            return


SETUPS = [
    dict(id='vwap_first_hour_hold', name='Held one side of VWAP for the whole first hour',
         family='vwap', detect=vwap_first_hour_hold,
         rules="If all twelve 5-minute closes of the first hour sit on the same side of VWAP, the open "
               "is on that side, and the 10:30 close is at least 0.25 ATR away from VWAP, lean the "
               "same way. Tested with and against; one signal per session."),
]
