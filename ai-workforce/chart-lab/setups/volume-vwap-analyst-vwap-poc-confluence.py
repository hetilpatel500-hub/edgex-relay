"""VWAP and developing POC confluence rejection on 5-minute bars.
Added 2026-10-01 by volume-vwap-analyst: the research queue's non-tape lines
are coded, so this run used WebSearch (tradingsim.com Volume Profile guide:
when VWAP and the POC sit at the same price, bounces from that cluster are
said to work better). Distinct from vwap_bounce (VWAP alone, trend session)
and poc_magnet / prior_poc_rejection (POC alone). Thresholds fixed before
any P&L was seen.
"""
import core


def vwap_poc_confluence(s):
    """From 10:30, when the developing POC (volume profile of the session so far)
    sits within 0.3 ATR of VWAP, that pair is a confluence zone. If the last 3
    bars all closed on one side of the zone and a bar's wick tags it (within 0.1
    ATR of the nearer of the two) but closes back on that side in that
    direction, signal with the bounce. One per side per session, to 14:30."""
    b = s.bars
    fired = set()
    for i in range(12, len(b)):
        if b[i].m >= 870:
            break
        atr = s.atr[i]
        if not atr or 630 > b[i].m:
            continue
        poc, _, _ = core.profile(b[:i + 1])
        v = s.vwap[i]
        if abs(poc - v) > 0.3 * atr:
            continue
        hi_z, lo_z = max(poc, v), min(poc, v)
        x = b[i]
        prior = b[i - 3:i]
        if (1 not in fired and all(p.c > hi_z for p in prior) and x.l <= hi_z + 0.1 * atr
                and x.c > hi_z and x.c > x.o):
            fired.add(1)
            yield i, 1
        elif (-1 not in fired and all(p.c < lo_z for p in prior) and x.h >= lo_z - 0.1 * atr
                and x.c < lo_z and x.c < x.o):
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='vwap_poc_confluence', name='VWAP + developing POC confluence rejection', family='vwap',
         detect=vwap_poc_confluence,
         rules="After 10:30, when VWAP and the session's developing point of control are within 0.3 ATR of "
               "each other, a pullback that wicks into that zone and closes back on the side price came from, "
               "in that direction, leans with the bounce (and its fade is tested). One signal per side per "
               "session, to 14:30."),
]
