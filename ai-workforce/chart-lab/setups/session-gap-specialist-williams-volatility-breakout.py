"""Larry Williams volatility breakout on 5-minute bars.
Added 2026-09-29 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch (open-breakout rule attributed to
Larry Williams and Toby Crabel in tradersmastermind.com / ungeracademy.com
summaries): enter when price travels half of yesterday's range from today's
open. Distinct from crabel_stretch (stretch is a 10-session average of
open-to-extreme pullbacks) and orb15 (first 15-minute range). Parameters
(0.5 x range, 09:45-14:30, new session extreme) were fixed before testing.
"""


def williams_break(s):
    p = s.prior
    if p is None:
        return
    rng = p.hi - p.lo
    if rng <= 0:
        return
    k = 0.5 * rng
    b = s.bars
    hi, lo = b[0].h, b[0].l
    for i in range(1, len(b)):
        x = b[i]
        if x.m >= 870:
            return
        new_hi, new_lo = x.h > hi, x.l < lo
        if x.m >= 585:
            if x.c > s.open + k and new_hi:
                yield i, 1
                return
            if x.c < s.open - k and new_lo:
                yield i, -1
                return
        hi, lo = max(hi, x.h), min(lo, x.l)


SETUPS = [
    dict(id='williams_vol_break', name='Williams volatility breakout', family='opening range',
         detect=williams_break,
         rules="A 5-minute bar that closes more than half of yesterday's high-low range above today's open "
               "while making a new session high leans long; the mirror below the open and a new low leans "
               "short. Between 9:45 and 14:30, one signal per session."),
]
