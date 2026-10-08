"""Retest of the day's opening price after a clear move away from it.
Added 2026-10-02 by support-resistance-mapper: the research queue held only tape items, so this run took
the documented "opening price as support/resistance" idea (day-trading level primers: the open is the
session's first agreed price, and a trend that leaves it often retests it once). Rules were fixed BEFORE
any P&L was seen: 0.75 ATR excursion, touch within 0.1 ATR, close back on the trend side, one per session.
Distinct from range_midpoint_hold, orb_retest and ib_retest (those use OR/IB edges, not the open print).
"""


def day_open_retest(s):
    """After price has closed at least 0.75 ATR away from the day's open, the first bar between 10:00 and 14:30
    whose range touches the open (within 0.1 ATR) and which closes back on the side it came from leans with
    that side (above the open = long, below = short). One signal per session."""
    b = s.bars
    o = s.open
    side = 0
    for i in range(3, len(b)):
        if b[i].m >= 870:
            break
        atr = s.atr[i]
        if not atr:
            continue
        if side == 0:
            if b[i].c >= o + 0.75 * atr:
                side = 1
            elif b[i].c <= o - 0.75 * atr:
                side = -1
            continue
        if b[i].m < 600:
            continue
        if side == 1 and b[i].l <= o + 0.1 * atr and b[i].c > o:
            yield i, 1
            return
        if side == -1 and b[i].h >= o - 0.1 * atr and b[i].c < o:
            yield i, -1
            return
        if side == 1 and b[i].c < o - 0.1 * atr:
            return
        if side == -1 and b[i].c > o + 0.1 * atr:
            return


SETUPS = [
    dict(id='day_open_retest', name="Retest of the day's open after a move away", family='support/resistance',
         detect=day_open_retest,
         rules="Once price has closed at least 0.75 ATR above (below) the day's opening price, the first 5-minute "
               "bar between 10:00 and 14:30 that touches the open (within 0.1 ATR) and closes back on the same "
               "side leans with that side. Abandoned if price closes through the open instead. One signal per session."),
]
