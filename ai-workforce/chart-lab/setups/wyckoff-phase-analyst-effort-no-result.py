"""Wyckoff effort vs result: absorption bar at a session extreme, 5-minute bars.
Added 2026-10-01 by wyckoff-phase-analyst: the research queue is fully coded,
so this run used WebSearch for a documented intraday technique and took the
Wyckoff "effort without result" idea (heavy volume, little price progress
at the low or high means the other side is absorbing). Uses only the bar's
own rvol, range and the running session extreme, so no look-ahead.
"""


def effort_no_result(s):
    """A bar with relative volume >= 2 and a range <= 0.6 ATR that sits at the
    running session low (within 0.25 ATR) is absorption of selling; a later bar
    within 6 bars closing above that bar's high leans long. Mirror at the
    running high leans short. At most two signals a session, before 15:00."""
    b = s.bars
    fired = 0
    pend = []  # (index, dir, trigger_level, expires)
    for i in range(1, len(b)):
        if b[i].m >= 900 or fired >= 2:
            return
        for p in list(pend):
            j, d, lvl, exp = p
            if i > exp:
                pend.remove(p)
            elif (d == 1 and b[i].c > lvl) or (d == -1 and b[i].c < lvl):
                pend.remove(p)
                fired += 1
                yield i, d
                if fired >= 2:
                    return
        atr, rv = s.atr[i], s.rvol[i]
        if not atr or not rv or i < 6:
            continue
        rng = b[i].h - b[i].l
        if rv >= 2 and rng <= 0.6 * atr:
            lo = min(x.l for x in b[:i + 1])
            hi = max(x.h for x in b[:i + 1])
            if b[i].l <= lo + 0.25 * atr:
                pend.append((i, 1, b[i].h, i + 6))
            elif b[i].h >= hi - 0.25 * atr:
                pend.append((i, -1, b[i].l, i + 6))


SETUPS = [
    dict(id='effort_no_result', name='Effort without result: absorption bar at a session extreme', family='wyckoff',
         detect=effort_no_result,
         rules="A 5-minute bar with at least 2x its usual volume but a range under 0.6 ATR, sitting at the "
               "session low, shows selling being absorbed; a close above that bar's high within 6 bars leans "
               "long. The same bar at the session high followed by a close below its low leans short. "
               "Before 15:00."),
]
