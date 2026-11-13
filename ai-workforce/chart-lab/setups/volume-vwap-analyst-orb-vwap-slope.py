"""Opening-range breakout that agrees with the VWAP slope.
Added 2026-10-03 by volume-vwap-analyst: the queue's non-tape lines are coded, so this run used WebSearch
(luxalgo.com opening range & ORB, TradingView ORB scripts that gate breaks on VWAP slope) for an untested idea:
only take a 15-minute opening-range break when session VWAP is already moving the same way.
Rules fixed BEFORE any P&L was seen: 15-minute range, 3-bar VWAP slope of at least 0.05 ATR, close on the
VWAP side, before 11:00, first signal only.
"""


def orb_vwap_slope(s):
    """First close beyond the 15-minute opening range (bars 4 to 18, before 11:00). It counts only if VWAP rose
    (long) or fell (short) by at least 0.05 ATR over the last 3 bars and the close is on that side of VWAP.
    The first such break leans that way; one signal per session. A break that fails the VWAP test is skipped
    and a later one can still fire."""
    b = s.bars
    for i in range(3, len(b)):
        if b[i].m >= 660:
            return
        if not s.atr[i]:
            continue
        slope = s.vwap[i] - s.vwap[i - 3]
        if b[i].c > s.or_hi and slope >= 0.05 * s.atr[i] and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if b[i].c < s.or_lo and slope <= -0.05 * s.atr[i] and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='orb_vwap_slope', name='Opening range break with VWAP slope', family='opening range',
         detect=orb_vwap_slope,
         rules="First 5-minute close beyond the 15-minute opening range, before 11:00, counts only if session "
               "VWAP has moved the same way by at least 0.05 ATR over the last 3 bars and the close is on that "
               "side of VWAP; one signal per session. Tested with and against, like every setup."),
]
