"""Yesterday's POC first-touch rejection.
Added 2026-09-30 by volume-vwap-analyst: volume profile / POC family. Market
profile teaching: yesterday's point of control is a price the market accepted;
the first test of it from one side often either rejects (fade) or is accepted
(cross). Rules fixed before any P&L was seen; everything is known at the
signal bar's close.
"""


def prior_poc_rejection(s):
    p = s.prior
    if p is None:
        return
    poc = p.poc
    b = s.bars
    side = 0
    for i in range(3, len(b)):
        if b[i].m >= 840:
            return
        if side == 0:
            if b[i - 1].c > poc and b[i - 1].l > poc:
                side = 1
            elif b[i - 1].c < poc and b[i - 1].h < poc:
                side = -1
        if side == 1 and b[i].l <= poc and b[i].c > poc:
            yield i, 1; return
        if side == -1 and b[i].h >= poc and b[i].c < poc:
            yield i, -1; return
        if side == 1 and b[i].c < poc or side == -1 and b[i].c > poc:
            return


SETUPS = [
    dict(id='prior_poc_rejection', name="Yesterday's POC first-touch rejection", family='volume profile',
         detect=prior_poc_rejection,
         rules="Price trades on one side of yesterday's POC; the first bar that wicks to the POC but closes back "
               "on the approach side, before 14:00, leans in the direction of the approach. Tested with and "
               "against; one signal per session, cancelled if a bar closes through the POC first."),
]
