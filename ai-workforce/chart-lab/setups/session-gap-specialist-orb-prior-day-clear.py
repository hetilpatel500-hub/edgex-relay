"""Opening-range break that also clears the prior day's high or low (room-to-run filter).
Added 2026-10-04 by session-gap-specialist: found via WebSearch on ORB scripts that require the break to
clear prior-day levels with session VWAP on the same side. Rules fixed BEFORE any P&L was seen:
15-minute range (bars 0-2), first close beyond it before 11:00 that is also beyond yesterday's high (long)
or low (short) and on the VWAP side; first signal only. The lab tests it with and against.
"""


def orb_pd_clear(s):
    """First close beyond the 15-minute opening range, before 11:00, that is also beyond the prior day's
    high (long) or low (short) and on the same side of session VWAP. One signal per session."""
    if not s.prior:
        return
    b = s.bars
    ph, pl = s.prior.hi, s.prior.lo
    for i in range(3, len(b) - 1):
        if b[i].m >= 660:
            return
        c = b[i].c
        if c > s.or_hi and c > ph and c > s.vwap[i]:
            yield i, 1
            return
        if c < s.or_lo and c < pl and c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='orb_pd_clear', name='Opening-range break clearing prior-day high/low', family='opening range',
         detect=orb_pd_clear,
         rules="The first close beyond the 15-minute opening range before 11:00 that is also above yesterday's "
               "high (long) or below yesterday's low (short), with price on the same side of session VWAP; one "
               "signal per session. Tested with and against, like every setup."),
]
