"""Opening outside the prior day's range, then closing back inside it (daily-range 80% rule analogue).
Added 2026-10-02 by session-gap-specialist: the research queue held only tape items, so this run took the
documented "open outside the prior day's range / gap re-entry" idea (Dalton-style open-outside-range, the
80% rule applied to the prior day's high-low instead of the value area). Rules fixed BEFORE any P&L was seen:
open beyond the prior high or low, first 5-minute close back inside the range, one signal per session.
Distinct from gap_fade_rvol, unfilled_gap_ib_break and va_reentry (those use prior close or value area).
"""


def outside_range_reentry(s):
    """If the session opens above yesterday's high (or below yesterday's low) and a 5-minute bar between 9:35
    and 11:30 closes back inside yesterday's range, lean back toward the range (short after an open above,
    long after an open below). One signal per session."""
    p = s.prior
    if not p:
        return
    b = s.bars
    ph, pl = p.hi, p.lo
    if s.open > ph:
        side = -1
    elif s.open < pl:
        side = 1
    else:
        return
    for i in range(len(b)):
        if b[i].m >= 690:
            break
        if pl <= b[i].c <= ph:
            yield i, side
            return


SETUPS = [
    dict(id='outside_range_reentry', name='Open outside prior range, re-entry', family='session',
         detect=outside_range_reentry,
         rules="When the session opens above yesterday's high or below yesterday's low, the first 5-minute close "
               "back inside yesterday's range (before 11:30) leans back toward the range: short after an open above, "
               "long after an open below. One signal per session."),
]
