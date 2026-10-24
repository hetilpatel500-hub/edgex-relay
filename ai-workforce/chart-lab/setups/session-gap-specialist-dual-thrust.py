"""Dual Thrust opening breakout (Michael Chalek).
Added 2026-10-05 by session-gap-specialist via WebSearch (https://www.quantconnect.com/research/15258/dual-thrust-trading-algorithm/,
https://www.prorealcode.com/prorealtime-indicators/dual-thrust-strategy-indicator/). Distinct from williams_vol_break
(one prior day's range): Dual Thrust takes Range = max(HH - LC, HC - LL) over the last 4 sessions, so a gap or a
trending stretch widens the trigger. Rules fixed BEFORE any P&L was seen: N = 4 sessions, K1 = K2 = 0.5,
first 5-minute close beyond open +/- 0.5 x Range between 09:45 and 14:30, one signal per session.
"""


def dual_thrust(s):
    hist, p = [], s.prior
    while p is not None and len(hist) < 4:
        hist.append(p)
        p = p.prior
    if len(hist) < 4:
        return
    hh = max(x.hi for x in hist)
    ll = min(x.lo for x in hist)
    hc = max(x.close for x in hist)
    lc = min(x.close for x in hist)
    rng = max(hh - lc, hc - ll)
    if rng <= 0:
        return
    up, dn = s.open + 0.5 * rng, s.open - 0.5 * rng
    for i, x in enumerate(s.bars):
        if x.m >= 870:
            return
        if x.m < 585:
            continue
        if x.c > up:
            yield i, 1
            return
        if x.c < dn:
            yield i, -1
            return


SETUPS = [
    dict(id='dual_thrust', name='Dual Thrust breakout', family='opening range', detect=dual_thrust,
         rules="Range = the larger of (highest high - lowest close) and (highest close - lowest low) over the last 4 "
               "sessions. Buy line = today's open + 0.5 x Range, sell line = open - 0.5 x Range. The first 5-minute "
               "close beyond a line between 09:45 and 14:30 leans that way, once per session. Tested with and against."),
]
