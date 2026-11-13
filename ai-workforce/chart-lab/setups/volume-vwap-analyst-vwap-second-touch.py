"""VWAP second touch in a one-sided session.
Added 2026-10-04 by volume-vwap-analyst: VWAP family, a new idea (not on the written queue):
the first pullback to VWAP is already tested (vwap_bounce / first_pullback); this asks whether the
SECOND touch of VWAP, after the side of the session is established, is the better entry.
Parameters fixed BEFORE any P&L was seen: 10:30 to 14:30; since bar 6 every close is on one side of
VWAP except touch bars; touch = bar range reaches within 0.05 ATR of VWAP; exactly the second touch,
at least 4 bars after the first; touch bar closes on the trend side and in the direction of the trend;
at most 1 signal per session. The lab tests it with and against.
"""


def vwap_second_touch(s):
    """Count touches of VWAP from the trend side. On the second touch (bar closes back on the trend
    side, in the trend direction) lean with the trend."""
    b = s.bars
    for side in (1, -1):
        touches = []
        ok = True
        for i in range(6, len(b) - 1):
            a = s.atr[i]
            if not a:
                continue
            w = s.vwap[i]
            x = b[i]
            if side == 1:
                touch = x.l <= w + 0.05 * a
                broke = x.c < w - 0.05 * a
                fire = touch and x.c > w and x.c > x.o
            else:
                touch = x.h >= w - 0.05 * a
                broke = x.c > w + 0.05 * a
                fire = touch and x.c < w and x.c < x.o
            if broke:
                break
            if not touch:
                continue
            if touches and i - touches[-1] <= 1:
                touches[-1] = i
                continue
            if touches and i - touches[-1] < 4:
                continue
            touches.append(i)
            if len(touches) == 2:
                if fire and 630 <= x.m <= 870:
                    yield i, side
                break
            if len(touches) > 2:
                break


SETUPS = [
    dict(id='vwap_second_touch', name='VWAP second touch in a one-sided session', family='VWAP',
         detect=vwap_second_touch,
         rules="When the session has stayed on one side of VWAP since the first half hour and price "
               "touches VWAP for the second time (at least 4 bars after the first), closing back on the "
               "trend side in the trend's direction, lean with the trend. 10:30 to 14:30, one signal a session."),
]
