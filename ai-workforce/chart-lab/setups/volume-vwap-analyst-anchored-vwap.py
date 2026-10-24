"""Anchored VWAP retest from the session's extreme, 5-minute bars.
Added 2026-09-28 by volume-vwap-analyst: queue's non-tape lines are all coded,
so this run used WebSearch (trendspider.com, tradingsim.com) for a documented,
untested technique: VWAP anchored at the day's swing low/high rather than the
open. Buyers who bought the low are read as defending their average cost.
Distinct from session VWAP setups (vwap_reclaim, vwap_bounce).
"""


def anchored_vwap(s):
    """From 10:30 to 14:30, anchor a VWAP at the session's lowest low (long) or
    highest high (short) so far, if that anchor is at least 8 bars old. A bar that
    wicks to the anchored VWAP (within 0.1 ATR) and closes back on the anchor's
    side, in that direction, after the 3 prior bars closed on that side, leans
    away from the anchor. One signal per side per session."""
    b = s.bars
    fired = set()
    for i in range(24, len(b)):
        if b[i].m >= 870:
            break
        if b[i].m < 630 or not s.atr[i]:
            continue
        atr = s.atr[i]
        x = b[i]
        for side in (1, -1):
            if side in fired:
                continue
            past = b[:i]
            a = min(range(len(past)), key=lambda k: past[k].l) if side == 1 else max(range(len(past)), key=lambda k: past[k].h)
            if i - a < 8:
                continue
            pv = sum(((q.h + q.l + q.c) / 3) * q.v for q in b[a:i + 1])
            vv = sum(q.v for q in b[a:i + 1])
            if vv <= 0:
                continue
            av = pv / vv
            # prior 3 bars on the anchor side, using a running anchored VWAP
            ok = True
            for k in (i - 3, i - 2, i - 1):
                pk = sum(((q.h + q.l + q.c) / 3) * q.v for q in b[a:k + 1])
                vk = sum(q.v for q in b[a:k + 1])
                if vk <= 0 or (b[k].c <= pk / vk if side == 1 else b[k].c >= pk / vk):
                    ok = False
                    break
            if not ok:
                continue
            if side == 1 and x.l <= av + 0.1 * atr and x.c > av and x.c > x.o:
                fired.add(1)
                yield i, 1
            elif side == -1 and x.h >= av - 0.1 * atr and x.c < av and x.c < x.o:
                fired.add(-1)
                yield i, -1


SETUPS = [
    dict(id='anchored_vwap', name='Anchored VWAP retest from the day extreme', family='vwap',
         detect=anchored_vwap,
         rules="From 10:30 to 14:30, VWAP anchored at the session's low (or high) so far, at least 8 bars old. "
               "After 3 bars closing on the anchor's side of it, a bar that wicks to the anchored VWAP and "
               "closes back on that side in that direction leans away from the anchor. One signal per side "
               "per session."),
]
