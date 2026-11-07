"""High-volume bar midpoint retest.
Added 2026-10-02 by volume-vwap-analyst: volume family, the heaviest-bar-of-
the-session idea (a bar that trades far more than the session's average is
treated as a level where size changed hands; its 50% line is retested).
Rules fixed before any P&L was seen.
"""


def hvb_midpoint_retest(s):
    """A directional bar (close in its top/bottom 30%) with volume >= 3x the
    session's average bar volume so far and range >= 1 ATR, formed 10:00 or
    later. The first later bar (before 14:30) that trades back to the bar's
    midpoint (within 0.1 ATR) and closes on the bar's side of it leans with
    the bar. Abandoned if price closes through the far end of the bar."""
    b = s.bars
    hv = None  # (direction, midpoint, lo, hi)
    cum = 0.0
    for i in range(len(b)):
        x = b[i]
        atr = s.atr[i]
        if hv is not None and b[i].m < 870:
            d, mid, lo, hi = hv
            if (d == 1 and x.c < lo) or (d == -1 and x.c > hi):
                return
            if d == 1 and x.l <= mid + 0.1 * atr and x.c > mid:
                yield i, 1
                return
            if d == -1 and x.h >= mid - 0.1 * atr and x.c < mid:
                yield i, -1
                return
        elif hv is not None:
            return
        if hv is None and i >= 6 and x.m >= 600 and atr and cum:
            avg = cum / i
            rng = x.h - x.l
            if x.v >= 3 * avg and rng >= atr:
                if x.c >= x.h - 0.3 * rng:
                    hv = (1, (x.h + x.l) / 2, x.l, x.h)
                elif x.c <= x.l + 0.3 * rng:
                    hv = (-1, (x.h + x.l) / 2, x.l, x.h)
        cum += x.v


SETUPS = [
    dict(id='hvb_midpoint_retest', name='High-volume bar midpoint retest', family='volume',
         detect=hvb_midpoint_retest,
         rules="After 10:00, a bar with at least 3x the session's average bar volume, a range of at least 1 ATR "
               "and a close in its top (bottom) 30% marks a level. The first later bar before 14:30 that trades "
               "back to the bar's midpoint (within 0.1 ATR) and closes on the bar's side leans long (short). "
               "Abandoned if price closes beyond the far end of the bar. One signal per session."),
]
