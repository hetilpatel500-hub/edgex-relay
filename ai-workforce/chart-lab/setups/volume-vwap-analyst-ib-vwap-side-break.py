"""Initial balance break only when VWAP already sits on the break side of the IB midpoint.
Added 2026-10-08 by volume-vwap-analyst (initial balance / VWAP work: volume-weighted price
leaning to one half of the first hour means the auction was already one-sided before the
break; a break against that lean is a probe). Rule fixed before any P&L was seen;
everything is known at the signal bar's close.
"""


def ib_vwap_side_break(s):
    b = s.bars
    if len(b) < 14:
        return
    mid = (s.ib_hi + s.ib_lo) / 2
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if b[i].c > s.ib_hi:
            if s.vwap[i] > mid:
                yield i, 1
            return
        if b[i].c < s.ib_lo:
            if s.vwap[i] < mid:
                yield i, -1
            return


SETUPS = [
    dict(id='ib_vwap_side_break', name='Initial balance break with VWAP on the break side of the IB midpoint',
         family='volume profile', detect=ib_vwap_side_break,
         rules="The first 5-minute close beyond the initial balance (before 14:00) counts only if session VWAP is "
               "above the IB midpoint for an upside break, or below it for a downside break. One signal per "
               "session; a first break against the VWAP lean is skipped. Tested with and against."),
]
