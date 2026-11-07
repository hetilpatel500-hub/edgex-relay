"""Intraday 80% rule: re-entry into the developing value area after a close outside it.
Added 2026-10-04 by volume-vwap-analyst: volume profile family, an intraday cousin of the
prior-day value-area re-entry (va_reentry) that uses the session's own profile so far.
Parameters fixed BEFORE any P&L was seen: 70% value area of bars up to the previous bar,
11:00 to 14:30, previous close outside the area by at least 0.1 ATR, current close back
inside, at most 2 signals per session. The lab tests it with and against.
"""
import core


def developing_va_reentry(s):
    """Build the volume profile (POC/VAH/VAL) of the session up to the bar before last. If the
    previous bar closed beyond VAH (VAL) by 0.1 ATR or more and this bar closes back inside,
    lean toward the developing POC (short from above, long from below)."""
    b = s.bars
    n = 0
    for i in range(24, len(b) - 1):
        if not (660 <= b[i].m <= 870) or n >= 2:
            continue
        a = s.atr[i]
        if not a:
            continue
        poc, vah, val = core.profile(b[:i - 1])
        pc, c = b[i - 1].c, b[i].c
        if pc > vah + 0.1 * a and val <= c <= vah:
            n += 1
            yield i, -1
        elif pc < val - 0.1 * a and val <= c <= vah:
            n += 1
            yield i, 1


SETUPS = [
    dict(id='developing_va_reentry', name='Developing value-area re-entry', family='volume profile',
         detect=developing_va_reentry,
         rules="After 11:00, when a close beyond the session's developing value-area high (low) by 0.1 ATR "
               "is followed by a close back inside it, lean toward the developing POC (short from above, long "
               "from below), before 14:30."),
]
