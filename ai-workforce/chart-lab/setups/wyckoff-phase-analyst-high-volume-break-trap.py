"""High-volume range-break trap: a break on heavy volume that closes back inside within 3 bars.
Added 2026-10-15 by wyckoff-phase-analyst via WebSearch (LuxAlgo volume-at-breakout / volume-dry-up pages: heavy volume shows
participation, not direction, and a quick re-entry marks the break as failed; no backtest or thresholds published). The lab
tests spring/upthrust at the IB extreme and the opening-range failure, but not a rolling-range break that was confirmed by
volume and then failed. Fixed BEFORE any P&L was seen: range = highest high / lowest low of the previous 12 bars; a break
bar closes beyond that range with relative volume >= 1.5 (same-slot 20-session average); if within the next 3 bars a bar
closes back inside the range, that bar signals the opposite way (break above fails -> short, break below fails -> long).
Breaks from 10:30 to 14:30 ET, one signal per side per session. The lab tests it with and against.
"""


def hv_break_trap(s):
    b = s.bars
    done = {1: False, -1: False}
    for k in range(12, len(b) - 1):
        if b[k].m < 630 or b[k].m > 870:
            continue
        hi = max(x.h for x in b[k - 12:k]); lo = min(x.l for x in b[k - 12:k])
        rv = s.rvol[k] or 0
        if rv < 1.5:
            continue
        if b[k].c > hi:
            br, lvl = 1, hi
        elif b[k].c < lo:
            br, lvl = -1, lo
        else:
            continue
        for j in range(k + 1, min(k + 4, len(b))):
            if (br == 1 and b[j].c <= lvl) or (br == -1 and b[j].c >= lvl):
                if not done[-br]:
                    done[-br] = True
                    yield j, -br
                break


SETUPS = [
    dict(id='hv_break_trap', name='High-volume range-break trap', family='wyckoff',
         detect=hv_break_trap,
         rules="Price closes outside the previous 12 bars' range on at least 1.5x normal volume (10:30-14:30 ET). If within "
               "the next 3 bars a bar closes back inside that range, the break is read as failed: lean against it at that "
               "close (a failed break up is a short, a failed break down is a long). One per side per session. Tested "
               "with and against."),
]
