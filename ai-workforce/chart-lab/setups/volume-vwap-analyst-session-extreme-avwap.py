"""Anchored VWAP from the session extreme, first reclaim.
Added 2026-10-15 by volume-vwap-analyst (idea from anchored-VWAP practice: anchor
at a fresh high/low, trade the first close back through that anchored VWAP).
Everything is known at the signal bar's close; numbers fixed before any P&L was seen.
"""


def extreme_avwap(s):
    b = s.bars
    done = {1: False, -1: False}
    for i in range(14, len(b)):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        for d in (1, -1):
            if done[d]:
                continue
            # anchor: the session low (d=+1) or high (d=-1) so far, at least 8 bars old and not yet broken
            seg = b[:i + 1]
            a = min(range(i + 1), key=lambda k: seg[k].l) if d == 1 else max(range(i + 1), key=lambda k: seg[k].h)
            if i - a < 8:
                continue
            pv = vv = 0.0
            for k in range(a, i + 1):
                x = b[k]
                tp = (x.h + x.l + x.c) / 3
                pv += tp * x.v; vv += x.v
            if not vv:
                continue
            av = pv / vv
            # previous bar closed on the wrong side of the anchored VWAP, this bar closes through it
            pv2 = vv2 = 0.0
            for k in range(a, i):
                x = b[k]
                tp = (x.h + x.l + x.c) / 3
                pv2 += tp * x.v; vv2 += x.v
            if not vv2:
                continue
            av_prev = pv2 / vv2
            if d * (b[i - 1].c - av_prev) < 0 and d * (b[i].c - av) > 0 and d * (b[i].c - b[i].o) > 0:
                done[d] = True
                yield i, d


SETUPS = [
    dict(id='extreme_avwap_reclaim', name='Anchored VWAP from the session extreme, first reclaim', family='volume',
         detect=extreme_avwap,
         rules="Anchor a VWAP at the session's low (high), at least 8 bars old and still the extreme. "
               "When a bar closes up (down) through that anchored VWAP after the previous close was on "
               "the other side, that bar is the signal, between 10:00 and 14:30. Tested with and "
               "against; one signal per side per session."),
]
