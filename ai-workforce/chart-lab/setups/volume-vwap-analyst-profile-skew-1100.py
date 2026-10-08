"""Developing volume-profile shape (p / b) at 11:00.
Added 2026-10-01 by volume-vwap-analyst, from a WebSearch run on market-profile
day-type shapes (p-shape: volume concentrated high after a rally; b-shape:
concentrated low after a selloff). Rules and the one-third cut were fixed before
any P&L was seen; everything is known at the signal bar's close.
"""
import core


def profile_skew(s):
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m < 655:
            continue
        hi = max(x.h for x in b[:i + 1])
        lo = min(x.l for x in b[:i + 1])
        rng = hi - lo
        if rng < 1.5 * s.atr[i] if s.atr[i] else True:
            return
        poc, _, _ = core.profile(b[:i + 1])
        pos = (poc - lo) / rng
        if pos >= 2 / 3:
            yield i, 1
        elif pos <= 1 / 3:
            yield i, -1
        return


SETUPS = [
    dict(id='profile_skew_1100', name='Profile shape (p / b) at 11:00', family='volume profile',
         detect=profile_skew,
         rules="At the first 5-minute close at or after 11:00 ET, build the volume profile of the session so "
               "far. If its POC sits in the top third of the day's range so far (p-shape) the setup leans long; "
               "in the bottom third (b-shape) it leans short. Skipped when the range so far is under 1.5 ATR. "
               "Tested with and against; one signal per session."),
]
