"""First close across VWAP after a long one-sided stretch.
Added 2026-10-06 by volume-vwap-analyst: the queue held only tape items, so this run took the
"trend day ends when VWAP finally breaks" idea (Market Profile / VWAP trend-day literature, found by
WebSearch). Rules were fixed BEFORE any P&L was seen: at least 30 consecutive 5-minute closes on one
side of VWAP, then the first close on the other side between 12:05 and 14:30 ET. One per session.
"""


def vwap_long_side_cross(s):
    """After 30+ consecutive closes on one side of VWAP, the first close on the other side (12:05-14:30 ET)
    signals in the direction of the cross. One signal per session."""
    b = s.bars
    run, side = 0, 0
    for i in range(len(b)):
        sd = 1 if b[i].c > s.vwap[i] else (-1 if b[i].c < s.vwap[i] else 0)
        if sd == 0:
            continue
        if sd == side:
            run += 1
            continue
        if side and run >= 30 and 725 <= b[i].m < 870:
            yield i, sd
            return
        side, run = sd, 1


SETUPS = [
    dict(id='vwap_long_side_cross', name='First VWAP cross after a long one-sided stretch', family='volume/VWAP',
         detect=vwap_long_side_cross,
         rules="When price has closed on one side of VWAP for at least 30 straight 5-minute bars (2.5 hours), the "
               "first close on the other side of VWAP between 12:05 and 14:30 ET signals in the direction of the "
               "cross (a trend day losing its anchor). One signal per session."),
]
