"""Opening 5-minute bar breakout, only when price is not stretched from VWAP.
Added 2026-10-07 by session-gap-specialist, from a WebSearch run (ORB guides:
"make sure price is not too extended from VWAP" before taking the 5-minute
opening-range break). or5_break takes every first break; this keeps only the
ones that start close to VWAP and on the breakout side of it.
Rules fixed BEFORE any P&L was seen: first 5-minute bar sets the range; the
first bar before 10:30 that closes beyond it counts only if its close is on the
same side of the session VWAP and within 1.0 ATR of it. That first break is the
only candidate; if it fails the filter the session is skipped.
"""


def or5_vwap_near_break(s):
    b = s.bars
    hi, lo = b[0].h, b[0].l
    for i in range(1, len(b)):
        if b[i].m >= 630:
            return
        d = 1 if b[i].c > hi else -1 if b[i].c < lo else 0
        if not d:
            continue
        if (b[i].c - s.vwap[i]) * d > 0 and abs(b[i].c - s.vwap[i]) <= 1.0 * s.atr[i]:
            yield i, d
        return


SETUPS = [
    dict(id='or5_vwap_near_break', name='Opening 5-minute break near VWAP', family='opening range',
         detect=or5_vwap_near_break,
         rules="The first 5-minute bar (09:30-09:35) sets the range. The first later bar before 10:30 that closes "
               "beyond it leans that way only if it closes on the same side of the session VWAP and within 1 ATR "
               "of it; a break that starts stretched from VWAP is skipped, and so is the rest of the session. "
               "One signal per session; tested with and against."),
]
