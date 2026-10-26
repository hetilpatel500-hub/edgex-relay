"""Awesome Oscillator saucer (Bill Williams).
Added 2026-10-03 by momentum-analyst: Bill Williams' Awesome Oscillator
(SMA5 - SMA34 of bar midpoints) and its "saucer" signal, documented by
MetaTrader 5 help, AvaTrade and RoboForex. Not yet in the lab. Rules fixed
before any P&L was seen.
"""


def ao_saucer(s):
    """AO = SMA(5) - SMA(34) of (h+l)/2 built inside the session, so the first
    value is bar 34 (about 12:20 ET). Long saucer: AO above zero on three
    straight bars, the first two falling and the third rising above the second.
    Short mirror below zero. Signals until 14:30 ET, at most 2 per side per
    session."""
    b = s.bars
    mid = [(y.h + y.l) / 2 for y in b]
    ao = [None] * len(b)
    for i in range(33, len(b)):
        ao[i] = sum(mid[i - 4:i + 1]) / 5 - sum(mid[i - 33:i + 1]) / 34
    cnt = {1: 0, -1: 0}
    for i in range(36, len(b)):
        if b[i].m >= 870:
            continue
        a, b1, c = ao[i - 2], ao[i - 1], ao[i]
        if a is None:
            continue
        if a > 0 and b1 > 0 and c > 0 and b1 < a and c > b1 and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif a < 0 and b1 < 0 and c < 0 and b1 > a and c < b1 and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='ao_saucer', name='Awesome Oscillator saucer', family='momentum',
         detect=ao_saucer,
         rules="Awesome Oscillator (5 minus 34 bar average of bar midpoints, five-minute bars, built inside "
               "the session so it starts about 12:20 ET): above zero on three bars with the first two "
               "falling and the third rising leans long; the mirror below zero leans short. Until 14:30 ET, "
               "at most two signals per side per session."),
]
