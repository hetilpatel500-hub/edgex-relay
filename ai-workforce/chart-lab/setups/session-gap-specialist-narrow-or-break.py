"""Compressed opening range, then the breakout.
Added 2026-10-04 by session-gap-specialist: the research queue held only tape items, so this run took the
Crabel-style "compression precedes expansion" idea applied to the 15-minute opening range, found by WebSearch
(opening range breakout literature: 5-25 minute ranges, breakouts work best after contraction). Rules were fixed
BEFORE any P&L was seen: range <= 2.0 ATR, first close beyond it before 11:00, one per session.
Distinct from nr7_orb (prior-day range) and orb15 (no size condition).
"""


def narrow_or_break(s):
    """If the 9:30-9:45 range is no taller than 2.0 of the session's 5-minute ATR (read at the third bar), the
    first 5-minute close beyond that range between 9:45 and 11:00 leans with the break. One signal per session."""
    b = s.bars
    if len(b) < 4:
        return
    atr = s.atr[2]
    if not atr or (s.or_hi - s.or_lo) > 2.0 * atr:
        return
    for i in range(3, len(b)):
        if b[i].m >= 660:
            break
        if b[i].c > s.or_hi:
            yield i, 1
            return
        if b[i].c < s.or_lo:
            yield i, -1
            return


SETUPS = [
    dict(id='narrow_or_break', name='Compressed 15-minute opening range breakout', family='session/opening range',
         detect=narrow_or_break,
         rules="When the 9:30-9:45 range is no taller than 2.0 of the session's 5-minute ATR, the first 5-minute "
               "close beyond it before 11:00 leans with the break. Tested with and against; one signal per session."),
]
