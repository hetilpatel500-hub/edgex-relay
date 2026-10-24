"""Same-half-hour return continuation (time-of-day periodicity).
Added 2026-10-05 by session-gap-specialist via WebSearch: Heston, Korajczyk and Sadka, "Intraday Patterns in the
Cross-section of Stock Returns", Journal of Finance 65(4), 2010 (a half-hour's return tends to repeat in the same
half-hour on following days). Rules fixed BEFORE any P&L was seen: two windows only (10:00-10:30 and 15:30-16:00),
a move of at least 1 five-minute ATR yesterday, decision at the close of the bar before the window.
"""


def _same_slot(s, start_m):
    p = s.prior
    if p is None:
        return
    pw = [x for x in p.bars if start_m <= x.m < start_m + 30]
    if len(pw) < 6:
        return
    ret = pw[-1].c - pw[0].o
    b = s.bars
    for i, x in enumerate(b):
        if x.m == start_m - 5:
            if abs(ret) >= s.atr[i] and len(b) > i + 1 and b[i + 1].m == start_m:
                yield i, 1 if ret > 0 else -1
            return


def same_hh_1000(s):
    """Yesterday's 10:00-10:30 return sign, traded from the 10:00 open."""
    yield from _same_slot(s, 600)


def same_hh_1530(s):
    """Yesterday's 15:30-16:00 return sign, traded from the 15:30 open."""
    yield from _same_slot(s, 930)


SETUPS = [
    dict(id='same_hh_1000', name='Same half-hour continuation, 10:00 window', family='session', detect=same_hh_1000,
         rules="If yesterday's 10:00-10:30 move was at least one 5-minute ATR up (down), lean long (short) at the "
               "10:00 open today. Tested with and against; one signal per session."),
    dict(id='same_hh_1530', name='Same half-hour continuation, 15:30 window', family='session', detect=same_hh_1530,
         rules="If yesterday's 15:30-16:00 move was at least one 5-minute ATR up (down), lean long (short) at the "
               "15:30 open today. Tested with and against; one signal per session."),
]
