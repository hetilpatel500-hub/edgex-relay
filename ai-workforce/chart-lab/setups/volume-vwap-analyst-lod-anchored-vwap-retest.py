"""VWAP anchored at the session's extreme, first retest.
Added 2026-10-06 by volume-vwap-analyst: new idea from outside the queue.
Anchor a VWAP at the running low (or high) of the day once price has moved at
least 1.5 ATR away from it; the first pullback that touches that anchored VWAP
and closes back on the trend side is the signal. Rules fixed before any P&L.
Distinct from anchored_vwap (anchored at the open) and ivb_anchored_vwap.
"""


def lod_anchored_vwap_retest(s):
    """Between 10:00 and 15:00 ET. Long: since the running low (set at or after
    09:35) price has closed 1.5 ATR above it; the anchored VWAP (typical price x
    volume from the low bar) is below price; a later bar's low touches it and
    closes above it. Mirror for the running high. One signal per side per day."""
    b = s.bars
    n = len(b)
    done = set()
    lo_i = hi_i = 0
    for i in range(n):
        if b[i].l < b[lo_i].l:
            lo_i = i
        if b[i].h > b[hi_i].h:
            hi_i = i
        x = b[i]
        if x.m < 600 or x.m >= 900:
            continue
        atr = s.atr[i]
        if not atr:
            continue
        for side, a_i in ((1, lo_i), (-1, hi_i)):
            if side in done or a_i == i:
                continue
            seg = b[a_i:i + 1]
            vv = sum(y.v for y in seg)
            if not vv:
                continue
            av = sum((y.h + y.l + y.c) / 3 * y.v for y in seg) / vv
            if side == 1:
                ext = max(y.c for y in seg) - b[a_i].l
                if ext >= 1.5 * atr and x.l <= av < x.c and x.c > x.o:
                    done.add(side)
                    yield i, 1
            else:
                ext = b[a_i].h - min(y.c for y in seg)
                if ext >= 1.5 * atr and x.h >= av > x.c and x.c < x.o:
                    done.add(side)
                    yield i, -1


SETUPS = [
    dict(id='lod_anchored_vwap_retest', name='Anchored VWAP from the day extreme, first retest', family='volume / VWAP',
         detect=lod_anchored_vwap_retest,
         rules="Anchor a VWAP at the day's running low (high). Once price has closed at least 1.5 ATR away from "
               "it, the first bar between 10:00 and 15:00 ET that dips to the anchored VWAP and closes back on "
               "the trend side (up bar for a long, down bar for a short) is the signal. One per side per day. "
               "Tested with and against."),
]
