"""Afternoon first touch of VWAP on a one-sided day, lean with the day.
Added 2026-10-04 by volume-vwap-analyst via WebSearch (VWAP-bounce write-ups: price above VWAP for most of
the session, pulls back to touch it, bullish close = institutions defending their average cost; grade-A
continuation needs ~80% of the session on one side). Parameters fixed BEFORE any P&L was seen: 80% of closes
before 13:00 on one side, first touch and reclaim between 13:00 and 15:30. The lab tests it with and against.
"""


def afternoon_vwap_trend_pullback(s):
    """Before 13:00, at least 80% of the 5-minute closes sit on one side of session VWAP. From 13:00 to 15:30,
    the first bar that trades back to VWAP (low <= VWAP for an up day, high >= VWAP for a down day) but closes
    on the trend side of it gives the signal. One signal per session."""
    b = s.bars
    pre = [k for k in range(len(b)) if b[k].m < 780]
    if len(pre) < 40:
        return
    for d in (1, -1):
        share = sum(1 for k in pre if d * (b[k].c - s.vwap[k]) > 0) / len(pre)
        if share < 0.8:
            continue
        for k in range(len(pre), len(b) - 1):
            if b[k].m >= 930:
                return
            touched = b[k].l <= s.vwap[k] if d == 1 else b[k].h >= s.vwap[k]
            if touched and d * (b[k].c - s.vwap[k]) > 0:
                yield k, d
                return
        return


SETUPS = [
    dict(id='afternoon_vwap_trend_pullback', name='Afternoon first VWAP touch on a one-sided day',
         family='vwap', detect=afternoon_vwap_trend_pullback,
         rules="If at least 80% of the 5-minute closes before 13:00 sit on one side of VWAP, the first bar "
               "between 13:00 and 15:30 that touches VWAP and still closes on the trend side leans with the "
               "day. Tested with and against; one signal per session."),
]
